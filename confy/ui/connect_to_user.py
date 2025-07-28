import importlib.resources

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

from confy.qss import BUTTON_STYLE, INPUT_LABEL_STYLE, WARNING_WIDGET_STYLE


class ConnectToUserWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Confy - Conectar ao usuário')

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

        # Campo de Endereço do Destinatário
        self.recipient_address_input = QLineEdit()
        self.recipient_address_input.setPlaceholderText('Endereço do Destinatário')
        self.recipient_address_input.setFixedSize(250, 40)
        self.recipient_address_input.setStyleSheet(INPUT_LABEL_STYLE)
        layout.addWidget(self.recipient_address_input)

        # Botão Conversar
        self.start_chat_button = QPushButton('Conversar')
        self.start_chat_button.clicked.connect(self.handle_start_chat)
        self.start_chat_button.setFixedSize(100, 40)
        self.start_chat_button.setStyleSheet(BUTTON_STYLE)
        layout.addWidget(self.start_chat_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def handle_start_chat(self):
        recipient = self.recipient_address_input.text()

        if not recipient:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle('Campos obrigatórios')
            msg.setText('Você precisa preencher todos os campos!')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet(WARNING_WIDGET_STYLE)
            msg.exec()
