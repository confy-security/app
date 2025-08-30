import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from confy.labels import W_CONNECT_SERVER_TITLE
from confy.ui import ChatWindow, ConnectToServerWindow, ConnectToUserWindow
from confy.utils import Colors


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(W_CONNECT_SERVER_TITLE)
        self.resize(500, 300)
        self.setStyleSheet(f'background-color: {Colors.BACKGROUND};')

        # Uma pilha de widgets onde apenas um widget fica visível por vez.
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.chat_window = ChatWindow()
        self.connect_to_user_window = ConnectToUserWindow(self.change_window, self.chat_window)
        self.connect_to_server_window = ConnectToServerWindow(
            self.change_window, self.connect_to_user_window
        )

        self.stack.addWidget(self.connect_to_server_window)
        self.stack.addWidget(self.connect_to_user_window)
        self.stack.addWidget(self.chat_window)

    def change_window(self, new_window: QWidget):
        if isinstance(new_window, ChatWindow):
            # Crie uma nova instância do ChatWindow com os dados
            chat_window = ChatWindow(
                username=getattr(self, 'username', None),
                recipient=getattr(self, 'recipient', None),
                server_address=getattr(self, 'server_address', None),
            )
            self.stack.addWidget(chat_window)
            self.stack.setCurrentWidget(chat_window)
            self.setWindowTitle(chat_window.windowTitle())
            self.resize(600, 500)  # <-- aumenta o tamanho da janela aqui
        else:
            self.stack.setCurrentWidget(new_window)
            self.setWindowTitle(new_window.windowTitle())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
