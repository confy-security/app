import sys

from PySide6.QtWidgets import QApplication

from confy.ui.connect_to_user import ConnectToUserWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConnectToUserWindow()
    window.show()
    app.exec()
