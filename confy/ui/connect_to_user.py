"""Module for the ConnectToUserWindow class."""

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
    B_TO_TALK,
    I_PLACEHOLDER_RECIPIENT_ADDRESS,
    W_CONNECT_RECIPIENT_TITLE,
    W_WARNING_REQUIRED_FIELDS_TEXT,
    W_WARNING_REQUIRED_FIELDS_TITLE,
)
from confy.qss import BUTTON_STYLE, INPUT_LABEL_STYLE
from confy.utils import get_protocol, warning_message_box


class ConnectToUserWindow(QWidget):
    """Window to connect to a specific user."""

    def __init__(self, change_window_callback, new_window_callback: QWidget = None):
        """Initialize the ConnectToUserWindow.

        Args:
            change_window_callback (callable): Function to change the current window.
            new_window_callback (QWidget, optional): Window to be displayed after connection.

        """
        super().__init__()

        self.change_window_callback = change_window_callback
        self.new_window_callback = new_window_callback

        self.setWindowTitle(W_CONNECT_RECIPIENT_TITLE)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        # Logo
        self.logo = QLabel()
        self.logo.setFixedSize(60, 65)
        self.logo.setAlignment(Qt.AlignCenter)

        # Renders SVG into a QPixmap
        with importlib.resources.path('confy.assets', 'shield.svg') as img_path:
            svg_renderer = QSvgRenderer(str(img_path))
        pixmap = QPixmap(60, 65)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.end()

        self.logo.setPixmap(pixmap)

        layout.addWidget(self.logo, alignment=Qt.AlignCenter)

        # Recipient username field
        self.recipient_username_input = QLineEdit()
        self.recipient_username_input.setPlaceholderText(I_PLACEHOLDER_RECIPIENT_ADDRESS)
        self.recipient_username_input.setFixedSize(250, 40)
        self.recipient_username_input.setStyleSheet(INPUT_LABEL_STYLE)
        layout.addWidget(self.recipient_username_input)

        # Start chat button
        self.start_chat_button = QPushButton(B_TO_TALK)
        self.start_chat_button.clicked.connect(self.handle_start_chat)
        self.start_chat_button.setFixedSize(100, 40)
        self.start_chat_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.start_chat_button, alignment=Qt.AlignCenter)

        # Start chat by pressing Enter in recipient ID field
        self.recipient_username_input.returnPressed.connect(self.handle_start_chat)

        self.setLayout(layout)

    def handle_start_chat(self):
        """Handle the start chat button click event."""
        recipient = self.recipient_username_input.text()

        # Checks if recipient field is empty
        # If it is, displays a warning message
        if not recipient:
            warning_message_box(
                self, W_WARNING_REQUIRED_FIELDS_TITLE, W_WARNING_REQUIRED_FIELDS_TEXT
            )
        else:
            main_window = self.parentWidget().parentWidget()

            if recipient == main_window.username:
                warning_message_box(
                    self, 'Conflito', 'Remetente e destinatário não podem ser o mesmo usuário.'
                )
            else:
                # === CHECKS IF RECIPIENT IS NOT ALREADY CHATTING WITH SOMEONE ===
                # Disable chat button
                self.start_chat_button.setEnabled(False)
                self.start_chat_button.setText('Verificando...')

                # === CONSTRUCTION OF ENDPOINT URL ===
                # Ensures server has HTTP(S) protocol
                protocol, host = get_protocol(main_window.server_address, check_username=True)
                base_url = f'{protocol}://{host}'

                endpoint = f'/ws/check-availability/{recipient}'
                url = urljoin(base_url, endpoint)

                response = httpx.get(url, timeout=10)

                if response.status_code == HTTPStatus.OK:
                    main_window.recipient = recipient
                    if self.new_window_callback:
                        # If fields are filled, calls the window change function
                        self.change_window_callback(self.new_window_callback)
                elif response.status_code == HTTPStatus.LOCKED:
                    # Status 423 (Locked): Recipient is already in an active conversation
                    warning_message_box(
                        self,
                        'Destinatário Indisponível',
                        'O destinatário já está em uma conversa.',
                    )
                else:
                    # Other status codes: unexpected error
                    warning_message_box(
                        self,
                        'Erro de Conexão',
                        'Não foi possível verificar a disponibilidade do destinatário.',
                    )
                self.start_chat_button.setEnabled(True)
                self.start_chat_button.setText(B_TO_TALK)
