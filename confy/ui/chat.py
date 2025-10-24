import asyncio
import base64

import websockets
from confy_addons import (
    AESEncryption,
    RSAEncryption,
    RSAPublicEncryption,
    deserialize_public_key,
)
from confy_addons.prefixes import AES_KEY_PREFIX, AES_PREFIX, KEY_EXCHANGE_PREFIX, SYSTEM_PREFIX
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from confy.core.constants import RAW_PAYLOAD_LENGTH
from confy.utils import get_protocol, is_prefix


class WebSocketThread(QThread):
    """Thread separada para gerenciar a comunicação WebSocket com criptografia end-to-end.

    Esta classe implementa um sistema de chat seguro usando:
    1. Troca de chaves públicas RSA entre usuários
    2. Geração e compartilhamento seguro de chave AES simétrica
    3. Criptografia de todas as mensagens usando AES-256

    O protocolo de handshake funciona da seguinte forma:
    - Ambos os usuários geram pares RSA e trocam chaves públicas
    - O usuário com ID "maior" gera uma chave AES e a envia criptografada com RSA
    - Todas as mensagens subsequentes são criptografadas com AES
    """

    # === SINAIS QT PARA COMUNICAÇÃO THREAD-SAFE ===
    message_received = Signal(str, str)  # (sender, message) - Mensagem descriptografada recebida
    connection_status = Signal(str)  # Status da conexão WebSocket (Conectado/Desconectado)
    system_message = Signal(str)  # Mensagens do sistema/servidor
    error_occurred = Signal(str)  # Notificação de erros para exibir na UI

    def __init__(self, server_address, user_id, recipient_id):
        """Inicializa a thread WebSocket com parâmetros de conexão e criptografia.

        Args:
            server_address (str): Endereço do servidor WebSocket (ex: "ws://localhost:8000")
            user_id (str): ID único do usuário atual
            recipient_id (str): ID único do destinatário do chat
        """
        super().__init__()

        # === CONFIGURAÇÕES DE CONEXÃO ===
        self.server_address = server_address
        self.user_id = user_id
        self.recipient_id = recipient_id
        self.running = True  # Flag para controlar o loop principal da thread
        self.websocket = None  # Instância ativa da conexão WebSocket

        # === SISTEMA DE CRIPTOGRAFIA END-TO-END ===
        # <--- MODIFICADO: Instancia a classe RSA que gera e armazena o par de chaves
        self.rsa = RSAEncryption()

        # Chaves relacionadas ao peer (outro usuário no chat)
        self.peer_public_key = None  # Chave pública RSA recebida do destinatário
        self.peer_aes_key = None  # Chave AES-256 compartilhada para criptografia rápida

        # Controle do handshake de chaves
        self.public_sent = False  # Flag para evitar envio duplicado da chave pública

        # === FILA DE MENSAGENS ASSÍNCRONAS ===
        # Queue asyncio para processar mensagens de saída de forma thread-safe
        self.message_queue = asyncio.Queue()

    def run(self):
        """Ponto de entrada da thread - executa o loop asyncio.

        Este método é chamado automaticamente quando start() é invocado.
        Cria um novo loop de eventos asyncio para esta thread.
        """
        asyncio.run(self.websocket_client())

    async def websocket_client(self):
        """Cliente WebSocket principal que gerencia a conexão.

        Estabelece conexão WebSocket, inicia tarefas assíncronas para:
        - Receber mensagens do servidor
        - Processar fila de mensagens para envio

        Raises:
            Exception: Erros de conexão ou comunicação WebSocket
        """
        # Constrói URI do WebSocket baseado no protocolo detectado
        protocol, host = get_protocol(self.server_address)
        uri = f'{protocol}://{host}/ws/{self.user_id}@{self.recipient_id}'

        try:
            # Estabelece conexão WebSocket com o servidor
            async with websockets.connect(uri) as websocket:
                self.websocket = websocket
                self.connection_status.emit('Conectado')

                # === TAREFAS ASSÍNCRONAS CONCORRENTES ===
                # Task 1: Escutar mensagens do servidor continuamente
                receive_task = asyncio.create_task(self.receive_messages())
                # Task 2: Processar fila de mensagens para envio
                send_task = asyncio.create_task(self.process_send_queue())

                # Aguarda até que uma das tarefas termine (conexão perdida ou erro)
                done, pending = await asyncio.wait(
                    [receive_task, send_task], return_when=asyncio.FIRST_COMPLETED
                )

                # Cancela tarefas que ainda estão executando
                for task in pending:
                    task.cancel()

        except Exception as e:
            # Notifica a UI sobre erro de conexão
            self.error_occurred.emit(f'Erro de conexão: {str(e)}')
        finally:
            # Sempre notifica desconexão ao finalizar
            self.connection_status.emit('Desconectado')

    async def receive_messages(self):
        """Loop principal para receber e processar mensagens do WebSocket.

        Escuta continuamente por mensagens do servidor e as processa
        baseado em seus prefixos (sistema, chave pública, chave AES, mensagem).

        Raises:
            Exception: Erros durante recepção ou processamento de mensagens
        """
        try:
            while self.running:
                try:
                    # Recebe próxima mensagem do WebSocket (bloqueante)
                    message = await self.websocket.recv()
                except websockets.ConnectionClosed:
                    # Conexão foi fechada pelo servidor ou rede
                    self.running = False
                    self.connection_status.emit('Conexão fechada')
                    break

                # Processa a mensagem baseado em seu tipo/prefixo
                await self.process_received_message(message)

        except Exception as e:
            self.error_occurred.emit(f'Erro ao receber mensagem: {str(e)}')

    async def process_received_message(self, message):
        """Processa mensagens recebidas baseado em seus prefixos.

        O sistema usa prefixos para identificar tipos de mensagem:
        - SYSTEM_PREFIX: Mensagens do servidor (não criptografadas)
        - KEY_EXCHANGE_PREFIX: Chaves públicas RSA
        - AES_KEY_PREFIX: Chave AES criptografada com RSA
        - AES_PREFIX: Mensagens de chat criptografadas

        Args:
            message (str): Mensagem bruta recebida do WebSocket
        """

        # === MENSAGENS DO SERVIDOR (NÃO CRIPTOGRAFADAS) ===
        if is_prefix(message, SYSTEM_PREFIX):
            # Verifica se destinatário se conectou para iniciar handshake
            if message == f'{SYSTEM_PREFIX} O usuário destinatário agora está conectado.':
                # Envia chave pública automaticamente (apenas uma vez)
                if not self.public_sent:
                    # <--- MODIFICADO: Usa a propriedade da instância 'rsa'
                    await self.websocket.send(f'{KEY_EXCHANGE_PREFIX}{self.rsa.base64_public_key}')
                    self.public_sent = True
            # Repassa mensagem do sistema para a UI
            self.system_message.emit(message)
            return

        # === RECEBE CHAVE PÚBLICA RSA DO PEER ===
        elif is_prefix(message, KEY_EXCHANGE_PREFIX):
            # Extrai chave pública da mensagem (remove prefixo)
            b64_key = message[len(KEY_EXCHANGE_PREFIX) :]
            try:
                # Deserializa chave pública do base64
                self.peer_public_key = deserialize_public_key(b64_key)
            except Exception as e:
                self.error_occurred.emit(f'Chave pública do peer inválida: {e}')
                return

            # Responde com nossa chave pública se ainda não enviamos
            if not self.public_sent:
                try:
                    # <--- MODIFICADO: Usa a propriedade da instância 'rsa'
                    await self.websocket.send(f'{KEY_EXCHANGE_PREFIX}{self.rsa.base64_public_key}')
                    self.public_sent = True
                except Exception as e:
                    self.error_occurred.emit(f'Falha ao enviar chave pública: {e}')
                    return

            # === LÓGICA DE GERAÇÃO DA CHAVE AES ===
            # Apenas um usuário deve gerar a chave AES para evitar conflitos
            # Critério: usuário com ID "maior" lexicograficamente gera a chave
            if self.peer_aes_key is None and self.public_sent:
                should_generate = str(self.user_id) > str(self.recipient_id)
                if should_generate:
                    # <--- MODIFICADO: Instancia AESEncryption para gerar a chave
                    aes = AESEncryption()
                    # <--- MODIFICADO: Instancia RSAPublicEncryption para criptografar
                    encrypted_key = RSAPublicEncryption(self.peer_public_key).encrypt(aes.key)
                    # Codifica em base64 para transmissão
                    b64_encrypted_key = base64.b64encode(encrypted_key).decode()
                    await self.websocket.send(f'{AES_KEY_PREFIX}{b64_encrypted_key}')
                    # Armazena a chave gerada para uso local
                    self.peer_aes_key = aes.key

        # === RECEBE CHAVE AES CRIPTOGRAFADA ===
        elif is_prefix(message, AES_KEY_PREFIX):
            # Extrai chave AES criptografada da mensagem
            b64_enc = message[len(AES_KEY_PREFIX) :]
            try:
                # Decodifica de base64
                encrypted_key = base64.b64decode(b64_enc)
                # <--- MODIFICADO: Usa o método da instância 'rsa'
                received_aes_key = self.rsa.decrypt(encrypted_key)
                # Armazena chave AES para criptografia de mensagens
                self.peer_aes_key = AESEncryption(key=received_aes_key).key
                self.system_message.emit('Chave AES estabelecida - comunicação segura ativa')
            except Exception as e:
                self.error_occurred.emit(f'Falha ao descriptografar a chave AES: {e}')
            return

        # === MENSAGEM CRIPTOGRAFADA COM AES ===
        elif is_prefix(message, AES_PREFIX):
            # Verifica se handshake foi completado
            if self.peer_aes_key is None:
                self.system_message.emit(
                    'Mensagem criptografada recebida, mas chave AES não definida'
                )
                return

            # <--- INÍCIO DA LÓGICA DE VERIFICAÇÃO DE ASSINATURA --->
            raw_payload_with_sig = message[len(AES_PREFIX) :]
            try:
                # 1. Separa payload e assinatura
                parts = raw_payload_with_sig.split('::')
                if len(parts) != RAW_PAYLOAD_LENGTH:
                    self.error_occurred.emit('Payload de mensagem malformado recebido.')
                    return
                b64_payload, b64_signature = parts

                # 2. Descriptografa a mensagem
                decrypted_message = AESEncryption(self.peer_aes_key).decrypt(b64_payload)

                # 3. Prepara dados para verificação
                decrypted_bytes = decrypted_message.encode('utf-8')
                signature_bytes = base64.b64decode(b64_signature)

                # 4. VERIFICA a assinatura
                RSAPublicEncryption(self.peer_public_key).verify(decrypted_bytes, signature_bytes)

                # 5. SUCESSO: Emite a mensagem descriptografada e verificada
                self.message_received.emit(self.recipient_id, decrypted_message)

            except Exception as e:
                # 6. FALHA NA VERIFICAÇÃO: Emite um erro e descarta a mensagem
                self.error_occurred.emit(f'ASSINATURA INVÁLIDA: Mensagem descartada. ({e})')
            except Exception as e:
                # 7. FALHA GERAL: Erro de descriptografia, base64, etc.
                self.error_occurred.emit(f'Falha ao descriptografar/verificar mensagem: {e}')
            # <--- FIM DA LÓGICA DE VERIFICAÇÃO --->
        else:
            # === MENSAGEM EM TEXTO PURO (FALLBACK) ===
            # Para compatibilidade ou debugging - não recomendado em produção
            self.message_received.emit(self.recipient_id, message)

    async def process_send_queue(self):
        """Processa continuamente a fila de mensagens para envio.

        Loop infinito que pega mensagens da fila e as envia criptografadas.
        Usa timeout para permitir verificação periódica da flag self.running.

        Raises:
            Exception: Erros durante envio de mensagens
        """
        while self.running:
            try:
                # Espera por mensagem na fila (timeout de 1 segundo)
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                # Criptografa e envia a mensagem
                await self.send_encrypted_and_signed_message(message)
            except asyncio.TimeoutError:
                # Timeout normal - continua o loop
                continue
            except Exception as e:
                self.error_occurred.emit(f'Erro ao enviar mensagem: {str(e)}')

    async def send_encrypted_and_signed_message(self, message):
        """Criptografa E ASSINA uma mensagem antes de enviar via WebSocket."""
        if self.peer_aes_key:
            try:
                # <--- INÍCIO DA LÓGICA DE ASSINATURA --->

                # 1. Criptografa a mensagem com AES
                encrypted_payload = AESEncryption(self.peer_aes_key).encrypt(message)

                # 2. Assina a mensagem ORIGINAL (em bytes) com nossa chave privada
                message_bytes = message.encode('utf-8')
                signature = self.rsa.sign(message_bytes)  # Usa a instância 'rsa'

                # 3. Codifica a assinatura em base64
                b64_signature = base64.b64encode(signature).decode('utf-8')

                # 4. Combina e envia
                final_payload = f'{AES_PREFIX}{encrypted_payload}::{b64_signature}'
                await self.websocket.send(final_payload)

                # <--- FIM DA LÓGICA DE ASSINATURA --->
            except Exception as e:
                self.error_occurred.emit(f'Falha ao criptografar/assinar/enviar: {e}')
        else:
            self.system_message.emit('Chave AES ainda não estabelecida. Aguarde o handshake.')

    def send_message(self, message):
        """Adiciona mensagem à fila de envio de forma thread-safe.

        Este método é chamado dalla UI thread e precisa ser thread-safe
        para comunicar com a thread asyncio.

        Args:
            message (str): Mensagem a ser enviada

        Note:
            Usa estratégias diferentes para compatibilidade entre versões do asyncio.
        """
        if self.running:
            # === ESTRATÉGIA 1: Criar novo loop temporário ===
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.message_queue.put(message))
                loop.close()
            except Exception:
                # === ESTRATÉGIA 2: Usar loop existente (fallback) ===
                try:
                    asyncio.run_coroutine_threadsafe(
                        self.message_queue.put(message), asyncio.get_event_loop()
                    )
                except Exception as e:
                    # Se todas as estratégias falharem, notifica erro
                    self.error_occurred.emit(f'Erro ao enfileirar mensagem: {str(e)}')

    def stop(self):
        """Para a thread WebSocket de forma segura.

        Define flag de parada e aguarda conclusão da thread.
        Deve ser chamado antes de fechar a aplicação.
        """
        self.running = False  # Sinaliza para loops pararem
        self.quit()  # Finaliza a thread Qt
        self.wait()  # Aguarda thread terminar completamente


class ChatWindow(QWidget):
    """Janela principal do chat com interface gráfica usando PySide6.

    Fornece uma interface de usuário completa para:
    - Visualizar mensagens de chat em tempo real
    - Enviar mensagens criptografadas
    - Monitorar status de conexão e sistema
    - Exibir erros e notificações

    A comunicação com o servidor é gerenciada pela WebSocketThread.
    """

    def __init__(self, username=None, recipient=None, server_address=None):
        """Inicializa a janela de chat com parâmetros opcionais.

        Args:
            username (str, optional): Nome do usuário atual
            recipient (str, optional): Nome do destinatário
            server_address (str, optional): Endereço do servidor WebSocket
        """
        super().__init__()

        # === PARÂMETROS DE CONFIGURAÇÃO ===
        self.username = username
        self.recipient = recipient
        self.server_address = server_address

        # Define título da janela com nome do destinatário
        self.setWindowTitle(f'Confy - Chat com {self.recipient}')

        # Constrói a interface gráfica
        self.setup_ui()

        # === GERENCIAMENTO DE CONEXÃO ===
        self.websocket_thread = None  # Thread de comunicação WebSocket
        self.connection_status = 'Desconectado'  # Status atual da conexão

        # Conecta automaticamente se todos os parâmetros foram fornecidos
        if all([username, recipient, server_address]):
            self.connect_to_server()

    def setup_ui(self):
        """Configura todos os elementos da interface do usuário.

        Cria layout com:
        - Área de exibição de mensagens (somente leitura)
        - Campo de input para novas mensagens
        - Botão de envio

        Aplica estilos CSS customizados para tema escuro.
        """
        # === LAYOUT PRINCIPAL VERTICAL ===
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)  # Espaçamento entre elementos

        # === ÁREA DE MENSAGENS ===
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)  # Apenas visualização, não editável
        # Estilo CSS para tema escuro com bordas arredondadas
        self.messages_area.setStyleSheet(
            """
            QTextEdit {
                border: 1.3px solid #393939;
                border-radius: 10px;
                color: white;
                padding: 8px;
                background-color: #202020;
            }
            """
        )
        layout.addWidget(self.messages_area)

        # === ÁREA DE ENVIO DE MENSAGENS ===
        send_layout = QHBoxLayout()

        # Campo de input para digitação
        self.message_input = QLineEdit(placeholderText='Mensagem')
        self.message_input.setFixedHeight(40)
        self.message_input.setStyleSheet(
            """
            QLineEdit {
                border: 1.3px solid #393939;
                border-radius: 10px;
                color: white;
                padding: 8px;
                background-color: #303030;
            }
            """
        )
        # Conecta Enter/Return para enviar mensagem
        self.message_input.returnPressed.connect(self.send_message)

        # Botão de envio
        self.send_button = QPushButton('Enviar')
        self.send_button.setFixedSize(60, 40)
        self.send_button.setStyleSheet(
            """
            QPushButton {
                background-color: white;
                color: black;
                border-radius: 10px;
            }
            
            QPushButton:hover {
                background-color: #C0C0C0;
            }
            
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
            }
            """
        )
        # Conecta clique do botão para enviar mensagem
        self.send_button.clicked.connect(self.send_message)

        # Adiciona input e botão ao layout horizontal
        send_layout.addWidget(self.message_input)
        send_layout.addWidget(self.send_button)

        # Adiciona área de envio ao layout principal
        layout.addLayout(send_layout)
        self.setLayout(layout)

        # === CONFIGURAÇÃO INICIAL ===
        # Desabilita controles até conectar
        self.update_connection_status('Desconectado')

    def connect_to_server(self):
        """Estabelece conexão com o servidor WebSocket.

        Cria e inicia WebSocketThread se não houver uma já rodando.
        Conecta todos os sinais para comunicação thread-safe com a UI.
        """
        # Evita múltiplas conexões simultâneas
        if self.websocket_thread and self.websocket_thread.isRunning():
            return

        # === CRIAÇÃO DA THREAD DE COMUNICAÇÃO ===
        self.websocket_thread = WebSocketThread(self.server_address, self.username, self.recipient)

        # === CONEXÃO DE SINAIS THREAD-SAFE ===
        # Sinal: Mensagem recebida -> Callback para exibir na UI
        self.websocket_thread.message_received.connect(self.on_message_received)
        # Sinal: Status de conexão -> Atualizar UI e controles
        self.websocket_thread.connection_status.connect(self.on_connection_status)
        # Sinal: Mensagem do sistema -> Exibir notificação
        self.websocket_thread.system_message.connect(self.on_system_message)
        # Sinal: Erro ocorrido -> Mostrar erro na UI
        self.websocket_thread.error_occurred.connect(self.on_error_occurred)

        # Inicia a thread (chama run() automaticamente)
        self.websocket_thread.start()

    def send_message(self):
        """Envia mensagem digitada pelo usuário.

        Realiza validações básicas, exibe a mensagem na UI imediatamente,
        e a envia via WebSocketThread para criptografia e transmissão.

        Returns:
            None: Retorna cedo se mensagem vazia ou não conectado
        """
        # Obtém texto e remove espaços em branco
        message = self.message_input.text().strip()
        if not message:
            return  # Não envia mensagens vazias

        # Verifica se conexão está ativa
        if not self.websocket_thread or not self.websocket_thread.isRunning():
            self.show_error('Não conectado ao servidor')
            return

        # === EXIBE MENSAGEM IMEDIATAMENTE NA UI ===
        # Mostra mensagem como "própria" (cor verde)
        self.add_message_to_chat('Você', message, is_own=True)

        # === ENVIA VIA WEBSOCKET ===
        # Adiciona à fila de envio da thread (thread-safe)
        self.websocket_thread.send_message(message)

        # Limpa campo de input para próxima mensagem
        self.message_input.clear()

    def on_message_received(self, sender, message):
        """Callback executado quando mensagem é recebida da thread.

        Args:
            sender (str): ID do remetente da mensagem
            message (str): Conteúdo da mensagem já descriptografado
        """
        # Adiciona mensagem recebida na área de chat (cor azul)
        self.add_message_to_chat(sender, message, is_own=False)

    def on_connection_status(self, status):
        """Callback para mudanças no status de conexão WebSocket.

        Args:
            status (str): Novo status ('Conectado', 'Desconectado', etc.)
        """
        self.update_connection_status(status)

    def on_system_message(self, message):
        """Callback para mensagens do sistema/servidor.

        Args:
            message (str): Mensagem do sistema a ser exibida
        """
        self.add_system_message(message)

    def on_error_occurred(self, error):
        """Callback para notificação de erros da thread.

        Args:
            error (str): Descrição do erro ocorrido
        """
        self.show_error(error)

    def add_message_to_chat(self, sender, message, is_own=False):
        """Adiciona mensagem formatada à área de chat.

        Args:
            sender (str): Nome do remetente
            message (str): Conteúdo da mensagem
            is_own (bool): True se é mensagem própria, False se recebida

        Note:
            Usa HTML para formatação com cores diferentes:
            - Verde (#4CAF50): Mensagens próprias
            - Azul (#2196F3): Mensagens recebidas
        """
        if is_own:
            # Mensagem própria - nome em verde
            formatted_message = (
                f'<div style="color: #4CAF50; font-weight: bold;">'
                f'{sender}: '
                f'<span style="color: white; font-weight: normal;">{message}</span>'
                f'</div>'
            )
        else:
            # Mensagem recebida - nome em azul
            formatted_message = (
                f'<div style="color: #2196F3; font-weight: bold;">'
                f'{sender}: '
                f'<span style="color: white; font-weight: normal;">{message}</span>'
                f'</div>'
            )

        # Adiciona HTML formatado à área de mensagens
        self.messages_area.append(formatted_message)

    def add_system_message(self, message):
        """Adiciona mensagem do sistema com formatação especial.

        Args:
            message (str): Mensagem do sistema/servidor

        Note:
            Mensagens do sistema aparecem em amarelo e itálico.
        """
        formatted_message = (
            f'<div style="color: #FFC107; font-style: italic;">Sistema: {message}</div>'
        )
        self.messages_area.append(formatted_message)

    def update_connection_status(self, status):
        """Atualiza status de conexão e controla habilitação de controles.

        Args:
            status (str): Novo status da conexão

        Note:
            - 'Conectado': Habilita controles de envio
            - Outros: Desabilita controles e mostra status
        """
        self.connection_status = status

        if status == 'Conectado':
            # Habilita controles para envio de mensagens
            self.send_button.setEnabled(True)
            self.message_input.setEnabled(True)
            self.add_system_message('Conectado ao servidor')
        else:
            # Desabilita controles quando desconectado
            self.send_button.setEnabled(False)
            # Só mostra status se não for desconexão normal
            if status != 'Desconectado':
                self.add_system_message(f'Status: {status}')

    def show_error(self, error):
        """Exibe mensagem de erro na área de chat.

        Args:
            error (str): Descrição do erro a ser exibido
        """
        self.add_system_message(f'Erro: {error}')

    def closeEvent(self, event):
        """Cleanup executado quando janela está sendo fechada.

        Garante que a thread WebSocket seja finalizada adequadamente
        para evitar vazamentos de recursos ou threads órfãs.

        Args:
            event (QCloseEvent): Evento de fechamento da janela
        """
        # Para thread WebSocket se estiver rodando
        if self.websocket_thread and self.websocket_thread.isRunning():
            self.websocket_thread.stop()

        # Aceita o evento de fechamento
        event.accept()
