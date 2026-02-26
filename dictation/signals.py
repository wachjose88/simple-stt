import logging

from PySide6.QtCore import Signal, QObject

logger = logging.getLogger('dictation.app')


class DictationSignals(QObject):

    def __init__(self):
        super().__init__()

    set_text_to_view = Signal(str)
