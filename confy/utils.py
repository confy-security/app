"""Utility functions and classes for the Confy application."""

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
    """Return the absolute path to a resource, even if packaged with PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller extracts files to this temporary folder
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


def is_prefix(message, prefix: str) -> bool:
    """Check if a message is a string that starts with the provided prefix.

    Args:
        message (Any): Message to be checked.
        prefix (str): Expected prefix.

    Returns:
        bool: True if the message is a string and starts with the prefix,
              False otherwise.

    """
    if isinstance(message, str) and message.startswith(prefix):
        return True
    return False


def get_protocol(url: str, check_username: bool | None = None) -> tuple[str, str]:
    """Determine the appropriate WebSocket protocol (ws or wss) based on the URL scheme.

    Args:
        url (str): Full URL, including the protocol (http:// or https://).
        check_username (bool | None): If True, returns 'http' or 'https' instead of 'ws' or 'wss'.

    Returns:
        tuple[str]: A tuple containing:
            - The corresponding WebSocket protocol ('ws' or 'wss').
            - The hostname extracted from the URL.

    """
    hostname = url.split('://')
    protocol = 'ws'

    if hostname[0] == 'https':
        protocol = 'wss'

    if check_username:
        protocol = 'https' if hostname[0] == 'https' else 'http'

    return protocol, hostname[1]


def icon(svg_string, size=24, color: str | None = None):
    """Create a QIcon from an SVG string.

    Args:
        svg_string (str): The SVG content as a string.
        size (int): The desired size of the icon (width and height).
        color (str | None): Optional color to apply to the SVG elements.

    Returns:
        QIcon: The generated icon.

    """
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
    """Display a warning message box with the given title and text.

    Args:
        object (QWidget): Parent widget for the message box.
        title (str): Title of the message box.
        text (str): Text content of the message box.

    """
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
