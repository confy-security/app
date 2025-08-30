import importlib.resources
from http import HTTPStatus
from urllib.parse import urljoin

import httpx
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from confy.labels import (
    B_CONNECT,
    I_PLACEHOLDER_SERVER_ADDRESS,
    I_PLACEHOLDER_USERNAME,
    W_WARNING_REQUIRED_FIELDS_TEXT,
    W_WARNING_REQUIRED_FIELDS_TITLE,
)
from confy.qss import BUTTON_STYLE, INPUT_LABEL_STYLE
from confy.utils import get_protocol, warning_message_box


class ConnectToServerWindow(QWidget):
    """Janela para conectar ao servidor.

    Args:
        change_window_callback (callable): Função para alterar a janela atual.
        new_window_callback (QWidget, optional): Janela a ser exibida após a conexão.
    """

    def __init__(self, change_window_callback, new_window_callback: QWidget = None):
        super().__init__()

        self.change_window_callback = change_window_callback
        self.new_window_callback = new_window_callback

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        # Logotipo
        self.logo = QLabel()
        self.logo.setFixedSize(60, 65)
        self.logo.setAlignment(Qt.AlignCenter)

        # Renderiza o SVG em um QPixmap
        with importlib.resources.path('confy.assets', 'shield.svg') as img_path:
            svg_renderer = QSvgRenderer(str(img_path))
        pixmap = QPixmap(60, 65)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.end()

        self.logo.setPixmap(pixmap)

        layout.addWidget(self.logo, alignment=Qt.AlignCenter)

        # Campo Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(I_PLACEHOLDER_USERNAME)
        self.username_input.setFixedSize(250, 40)
        self.username_input.setStyleSheet(INPUT_LABEL_STYLE)
        layout.addWidget(self.username_input)

        # Campo de Endereço do Servidor
        self.server_address_input = QLineEdit()
        self.server_address_input.setPlaceholderText(I_PLACEHOLDER_SERVER_ADDRESS)
        self.server_address_input.setFixedSize(250, 40)
        self.server_address_input.setStyleSheet(INPUT_LABEL_STYLE)
        layout.addWidget(self.server_address_input)

        # Botão Conectar
        self.connect_button = QPushButton(B_CONNECT)
        self.connect_button.clicked.connect(self.handle_login)
        self.connect_button.setFixedSize(100, 40)
        self.connect_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.connect_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        server_address = self.server_address_input.text()

        # Verifica se os campos de nome e servidor estão preenchidos
        # Se não estiverem, exibe uma mensagem de aviso
        if not username or not server_address:
            warning_message_box(
                self, W_WARNING_REQUIRED_FIELDS_TITLE, W_WARNING_REQUIRED_FIELDS_TEXT
            )
        else:
            # === INICIALIZAÇÃO DA VERIFICAÇÃO DE USERNAME ===
            # Desabilita botão para prevenir múltiplas requisições simultâneas
            self.connect_button.setEnabled(False)
            self.connect_button.setText('Verificando...')

            # === CONSTRUÇÃO DA URL DO ENDPOINT ===
            # Garante que o servidor tenha protocolo HTTP(S)
            protocol, host = get_protocol(server_address, check_username=True)
            base_url = f'{protocol}://{host}'

            # Constrói URL completa para verificação de username
            endpoint = f'/online-users/{username}'
            url = urljoin(base_url, endpoint)

            # === REQUISIÇÃO HTTP COM TIMEOUT ===
            # Timeout de 10 segundos para evitar travamento indefinido
            try:
                response = httpx.get(url, timeout=10)
                if response.status_code == HTTPStatus.OK:
                    # Status 200: Username está disponível
                    main_window = self.parentWidget().parentWidget()
                    main_window.username = username
                    main_window.server_address = server_address
                    if self.new_window_callback:
                        self.change_window_callback(self.new_window_callback)
                elif response.status_code == HTTPStatus.CONFLICT:
                    # Status 409 (Conflict): Username já está em uso
                    warning_message_box(
                        self,
                        'Username Indisponível',
                        'Este nome de usuário já está em uso. Tente outro nome.',
                    )
                else:
                    # Outros códigos de status: erro inesperado
                    warning_message_box(
                        self,
                        'Erro de Conexão',
                        'Não foi possível verificar a disponibilidade do username.',
                    )
            except (httpx.RequestError, httpx.ConnectError) as e:
                warning_message_box(
                    self, title='Erro de Rede', text=f'Falha ao conectar ao servidor: {str(e)}'
                )
            except Exception as e:
                warning_message_box(self, 'Erro', f'Ocorreu um erro inesperado: {str(e)}')
            self.connect_button.setEnabled(True)
            self.connect_button.setText(B_CONNECT)
