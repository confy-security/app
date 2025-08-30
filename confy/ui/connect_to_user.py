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
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from confy.labels import (
    B_TO_TALK,
    I_PLACEHOLDER_RECIPIENT_ADDRESS,
    W_CONNECT_RECIPIENT_TITLE,
    W_WARNING_REQUIRED_FIELDS_TEXT,
    W_WARNING_REQUIRED_FIELDS_TITLE,
)
from confy.qss import BUTTON_STYLE, INPUT_LABEL_STYLE, WARNING_WIDGET_STYLE
from confy.utils import get_protocol


class ConnectToUserWindow(QWidget):
    """Janela para conectar a um usuário específico."""

    def __init__(self, change_window_callback, new_window_callback: QWidget = None):
        super().__init__()

        self.change_window_callback = change_window_callback
        self.new_window_callback = new_window_callback

        self.setWindowTitle(W_CONNECT_RECIPIENT_TITLE)

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

        # Campo de Username do Destinatário
        self.recipient_username_input = QLineEdit()
        self.recipient_username_input.setPlaceholderText(I_PLACEHOLDER_RECIPIENT_ADDRESS)
        self.recipient_username_input.setFixedSize(250, 40)
        self.recipient_username_input.setStyleSheet(INPUT_LABEL_STYLE)
        layout.addWidget(self.recipient_username_input)

        # Botão Conversar
        self.start_chat_button = QPushButton(B_TO_TALK)
        self.start_chat_button.clicked.connect(self.handle_start_chat)
        self.start_chat_button.setFixedSize(100, 40)
        self.start_chat_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.start_chat_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def handle_start_chat(self):
        recipient = self.recipient_username_input.text()

        # Verifica se o campo de destinatário está vazio
        # Se estiver, exibe uma mensagem de aviso
        if not recipient:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(W_WARNING_REQUIRED_FIELDS_TITLE)
            msg.setText(W_WARNING_REQUIRED_FIELDS_TEXT)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet(WARNING_WIDGET_STYLE)
            msg.exec()
        else:
            main_window = self.parentWidget().parentWidget()

            if recipient == main_window.username:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('Conflito')
                msg.setText('Remetente e destinatário não podem ser o mesmo usuário.')
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setStyleSheet(WARNING_WIDGET_STYLE)
                msg.exec()
            else:
                # === VERIFICA SE DESTINATÁRIO NÃO ESTÁ CONVERSANDO COM ALGUÉM ===
                # Desabilitar botão de conversa
                self.start_chat_button.setEnabled(False)
                self.start_chat_button.setText('Verificando...')

                # === CONSTRUÇÃO DA URL DO ENDPOINT ===
                # Garante que o servidor tenha protocolo HTTP(S)
                protocol, host = get_protocol(main_window.server_address, check_username=True)
                base_url = f'{protocol}://{host}'

                endpoint = f'/ws/check-availability/{recipient}'
                url = urljoin(base_url, endpoint)

                response = httpx.get(url, timeout=10)

                if response.status_code == HTTPStatus.OK:
                    main_window.recipient = recipient
                    if self.new_window_callback:
                        # Se os campos estiverem preenchidos, chama a função de mudança de janela
                        self.change_window_callback(self.new_window_callback)
                elif response.status_code == HTTPStatus.LOCKED:
                    # Status 423 (Locked): Destinatário já está em uma conversa ativa
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle('Destinatário Indisponível')
                    msg.setText('O destinatário já está em uma conversa.')
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setStyleSheet(WARNING_WIDGET_STYLE)
                    msg.exec()
                else:
                    # Outros códigos de status: erro inesperado
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle('Erro de Conexão')
                    msg.setText('Não foi possível verificar a disponibilidade do destinatário.')
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.setStyleSheet(WARNING_WIDGET_STYLE)
                    msg.exec()
                self.start_chat_button.setEnabled(True)
                self.start_chat_button.setText(B_TO_TALK)
