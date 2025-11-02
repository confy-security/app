"""Stylesheet definitions for Confy GUI components."""

from confy.utils import Colors

INPUT_LABEL_STYLE = f"""
    background-color: {Colors.INPUT_BACKGROUND};
    border: 1.3px solid {Colors.BORDER};
    border-radius: 10px;
    padding: 8px;
    color: white;
"""

BUTTON_STYLE = """
    QPushButton {
        background-color: white;
        color: black;
        border-radius: 20px;
    }

    QPushButton:hover {
        background-color: #C0C0C0;
    }
"""
