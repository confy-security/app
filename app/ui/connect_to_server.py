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

from app.utils import Colors, resource_path


class ConnectToServerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Confy - Conectar ao servidor')
        self.resize(500, 300)
        self.setStyleSheet(f'background-color: {Colors.BACKGROUND};')

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        # Logotipo
        self.logo = QLabel()
        self.logo.setFixedSize(60, 65)
        self.logo.setAlignment(Qt.AlignCenter)

        # Renderiza o SVG em um QPixmap
        svg_renderer = QSvgRenderer(
            resource_path('resources/icons/shield.svg')
        )
        pixmap = QPixmap(60, 65)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        svg_renderer.render(painter)
        painter.end()

        self.logo.setPixmap(pixmap)

        layout.addWidget(self.logo, alignment=Qt.AlignCenter)

        # Campo Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.username_input.setFixedSize(250, 40)
        self.username_input.setStyleSheet(f"""
            background-color: {Colors.INPUT_BACKGROUND};
            border: 1.3px solid {Colors.BORDER};
            border-radius: 10px;
            padding: 8px;
            color: white;
        """)
        layout.addWidget(self.username_input)

        # Campo de Endereço do Servidor
        self.server_address_input = QLineEdit()
        self.server_address_input.setPlaceholderText('Endereço do Servidor')
        self.server_address_input.setFixedSize(250, 40)
        self.server_address_input.setStyleSheet(f"""
            background-color: {Colors.INPUT_BACKGROUND};
            border: 1.3px solid {Colors.BORDER};
            border-radius: 10px;
            padding: 8px;
            color: white;
        """)
        layout.addWidget(self.server_address_input)

        # Botão Conectar
        self.connect_button = QPushButton('Conectar')
        self.connect_button.clicked.connect(self.handle_login)
        self.connect_button.setFixedSize(100, 40)
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                border-radius: 20px;
            }

            QPushButton:hover {
                background-color: #C0C0C0;
            }
        """)
        layout.addWidget(self.connect_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def handle_login(self):
        nome = self.username_input.text()
        servidor = self.server_address_input.text()

        if not nome or not servidor:
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
