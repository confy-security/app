import sys

from PySide6.QtWidgets import QApplication

from confy.ui.connect_to_server import ConnectToServerWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConnectToServerWindow()
    window.show()
    app.exec()
