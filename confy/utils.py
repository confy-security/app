import os
import sys
from enum import Enum

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QMessageBox


class Colors(Enum):
    BACKGROUND = '#212121'
    INPUT_BACKGROUND = '#303030'
    BORDER = '#393939'

    def __str__(self):
        return self.value


def resource_path(relative_path: str) -> str:
    """
    Retorna o caminho absoluto para um recurso,
    mesmo se empacotado com PyInstaller
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller extrai os arquivos para essa pasta temporária
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


def is_prefix(message, prefix: str) -> bool:
    """Verifica se uma mensagem é uma string que começa com o prefixo fornecido.

    Args:
        message (Any): Mensagem a ser verificada.
        prefix (str): Prefixo esperado.

    Returns:
        bool: True se a mensagem for uma string e começar com o prefixo,
              False caso contrário.

    """
    if isinstance(message, str) and message.startswith(prefix):
        return True
    return False


def get_protocol(url: str, check_username: bool | None = None) -> tuple[str]:
    """Determina o protocolo WebSocket apropriado (ws ou wss) com base no esquema da URL.

    Args:
        url (str): URL completa, incluindo o protocolo (http:// ou https://).

    Returns:
        tuple[str]: Uma tupla contendo:
            - O protocolo WebSocket correspondente ('ws' ou 'wss').
            - O hostname extraído da URL.

    """
    hostname = url.split('://')
    protocol = 'ws'

    if hostname[0] == 'https':
        protocol = 'wss'

    if check_username:
        protocol = 'https' if hostname[0] == 'https' else 'http'

    return protocol, hostname[1]


def icon(svg_string, size=24, color: str | None = None):
    if color:
        svg_string = svg_string.replace('stroke="currentColor"', f'stroke="{color}"')
        svg_string = svg_string.replace('fill="currentColor"', f'fill="{color}"')

    renderer = QSvgRenderer(QByteArray(svg_string.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def warning_message_box(object, title: str, text: str):
    msg = QMessageBox(object)
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle(title)
    msg.setText(text)
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
