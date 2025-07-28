import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from confy.ui import ConnectToServerWindow, ConnectToUserWindow
from confy.utils import Colors


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Confy - Conectar ao servidor')
        self.resize(500, 300)
        self.setStyleSheet(f'background-color: {Colors.BACKGROUND};')

        # Uma pilha de widgets onde apenas um widget fica visível por vez.
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.connect_to_user_window = ConnectToUserWindow()
        self.connect_to_server_window = ConnectToServerWindow(
            self.change_window, self.connect_to_user_window
        )

        self.stack.addWidget(self.connect_to_server_window)
        self.stack.addWidget(self.connect_to_user_window)

    def change_window(self, new_window: QWidget):
        """Altera a janela atual exibida na pilha.

        Args:
            new_window (QWidget): A nova janela a ser exibida.
        """
        self.stack.setCurrentWidget(new_window)
        self.setWindowTitle(new_window.windowTitle())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
