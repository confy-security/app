import os
import sys
from enum import Enum


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
