"""Entry point for the Confy application."""

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
    """Main window of the Confy application."""

    def __init__(self):
        """Initialize the MainWindow."""
        super().__init__()
        self.setWindowTitle(W_CONNECT_SERVER_TITLE)
        self.resize(500, 300)
        self.setStyleSheet(f'background-color: {Colors.BACKGROUND};')

        # A stack of widgets where only one widget is visible at a time.
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
        """Change the current window to the specified new window.

        Args:
            new_window (QWidget): The window to switch to.

        """
        if isinstance(new_window, ChatWindow):
            # Create a new ChatWindow instance with the data
            chat_window = ChatWindow(
                username=getattr(self, 'username', None),
                recipient=getattr(self, 'recipient', None),
                server_address=getattr(self, 'server_address', None),
            )
            self.stack.addWidget(chat_window)
            self.stack.setCurrentWidget(chat_window)
            self.setWindowTitle(chat_window.windowTitle())
            self.resize(600, 500)  # Increases window size here
        else:
            self.stack.setCurrentWidget(new_window)
            self.setWindowTitle(new_window.windowTitle())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
