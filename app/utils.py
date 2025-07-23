from enum import Enum


class Colors(Enum):
    BACKGROUND = '#212121'
    INPUT_BACKGROUND = '#303030'
    BORDER = '#393939'

    def __str__(self):
        return self.value
