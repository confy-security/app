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

from confy.utils import Colors


class ConnectToUserWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Confy - Conectar ao usuário')
        self.resize(500, 300)

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
        self.recipient_address_input.setStyleSheet(f"""
            background-color: {Colors.INPUT_BACKGROUND};
            border: 1.3px solid {Colors.BORDER};
            border-radius: 10px;
            padding: 8px;
            color: white;
        """)
        layout.addWidget(self.recipient_address_input)

        # Botão Conversar
        self.start_chat_button = QPushButton('Conversar')
        self.start_chat_button.clicked.connect(self.handle_start_chat)
        self.start_chat_button.setFixedSize(100, 40)
        self.start_chat_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border-radius: 20px;
            }

            QPushButton:hover {
                background-color: #C0C0C0;
            }
        """)
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
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #212121;
                    color: white;
                }
                QLabel {
                    color: white;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: white;
                    color: black;
                    padding: 5px 15px;
                    border-radius: 14px;
                }
                
                QPushButton:hover {
                    background-color: #C0C0C0;
                }
            """)
            msg.exec()
