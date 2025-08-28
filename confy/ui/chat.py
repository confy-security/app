from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ChatWindow(QWidget):
    def __init__(self, username=None, recipient=None, server_address=None):
        super().__init__()
        self.username = username
        self.recipient = recipient
        self.server_address = server_address

        self.setWindowTitle(f'Confy - Chat com {self.recipient}')

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        # Área de mensagens
        self.messages_area = QTextEdit()
        self.messages_area.setReadOnly(True)
        self.messages_area.setStyleSheet(
            """
        QTextEdit {
            border: 1.3px solid #393939;
            border-radius: 10px;
            color: white;
            padding: 8px;
        }
        """
        )
        layout.addWidget(self.messages_area)

        # Campo de envio
        send_layout = QHBoxLayout()
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
            """
        )
        self.send_button.clicked.connect(self.send_message)
        send_layout.addWidget(self.message_input)
        send_layout.addWidget(self.send_button)
        layout.addLayout(send_layout)

        self.setLayout(layout)

        # Aqui você pode iniciar a conexão websocket

    def send_message(self):
        message = self.message_input.text()
        if message:
            # Aqui você envia a mensagem via websocket
            self.messages_area.append(f'Você: {message}')
            self.message_input.clear()
