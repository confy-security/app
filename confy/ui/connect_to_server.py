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
    B_CONNECT,
    I_PLACEHOLDER_SERVER_ADDRESS,
    I_PLACEHOLDER_USERNAME,
    W_WARNING_REQUIRED_FIELDS_TEXT,
    W_WARNING_REQUIRED_FIELDS_TITLE,
)
from confy.qss import BUTTON_STYLE, INPUT_LABEL_STYLE
from confy.utils import get_protocol, warning_message_box


class ConnectToServerWindow(QWidget):
    """Window to connect to server.

    Args:
        change_window_callback (callable): Function to change the current window.
        new_window_callback (QWidget, optional): Window to be displayed after connection.

    """

    def __init__(self, change_window_callback, new_window_callback: QWidget = None):
        """Initialize the ConnectToServerWindow.

        Args:
            change_window_callback (callable): Function to change the current window.
            new_window_callback (QWidget, optional): Window to be displayed after connection.

        """
        super().__init__()

        self.change_window_callback = change_window_callback
        self.new_window_callback = new_window_callback

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

        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(I_PLACEHOLDER_USERNAME)
        self.username_input.setFixedSize(250, 40)
        self.username_input.setStyleSheet(INPUT_LABEL_STYLE)
        layout.addWidget(self.username_input)

        # Server address field
        self.server_address_input = QLineEdit()
        self.server_address_input.setPlaceholderText(I_PLACEHOLDER_SERVER_ADDRESS)
        self.server_address_input.setFixedSize(250, 40)
        self.server_address_input.setStyleSheet(INPUT_LABEL_STYLE)
        layout.addWidget(self.server_address_input)

        # Connect button
        self.connect_button = QPushButton(B_CONNECT)
        self.connect_button.clicked.connect(self.handle_login)
        self.connect_button.setFixedSize(100, 40)
        self.connect_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.connect_button, alignment=Qt.AlignCenter)

        # Connect by pressing Enter in server address field
        self.server_address_input.returnPressed.connect(self.handle_login)

        self.setLayout(layout)

    def handle_login(self):
        """Handle the login process by verifying the username with the server."""
        username = self.username_input.text()
        server_address = self.server_address_input.text()

        # Checks if name and server fields are filled
        # If not, displays a warning message
        if not username or not server_address:
            warning_message_box(
                self, W_WARNING_REQUIRED_FIELDS_TITLE, W_WARNING_REQUIRED_FIELDS_TEXT
            )
        else:
            # === INITIALIZATION OF USERNAME VERIFICATION ===
            # Disables button to prevent multiple simultaneous requests
            self.connect_button.setEnabled(False)
            self.connect_button.setText('Verificando...')

            # === CONSTRUCTION OF ENDPOINT URL ===
            # Ensures server has HTTP(S) protocol
            protocol, host = get_protocol(server_address, check_username=True)
            base_url = f'{protocol}://{host}'

            # Constructs full URL for username verification
            endpoint = f'/online-users/{username}'
            url = urljoin(base_url, endpoint)

            # === HTTP REQUEST WITH TIMEOUT ===
            # 10 second timeout to prevent indefinite hanging
            try:
                response = httpx.get(url, timeout=10)
                if response.status_code == HTTPStatus.OK:
                    # Status 200: Username is available
                    main_window = self.parentWidget().parentWidget()
                    main_window.username = username
                    main_window.server_address = server_address
                    if self.new_window_callback:
                        self.change_window_callback(self.new_window_callback)
                elif response.status_code == HTTPStatus.CONFLICT:
                    # Status 409 (Conflict): Username is already in use
                    warning_message_box(
                        self,
                        'Username Indisponível',
                        'Este nome de usuário já está em uso. Tente outro nome.',
                    )
                else:
                    # Other status codes: unexpected error
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
