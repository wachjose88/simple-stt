import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit

logger = logging.getLogger('dictation.app')


class Editor(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()
        self.start_stop_button = QPushButton(self.tr('Start'))
        self.hbox.addWidget(self.start_stop_button)
        self.copy_button = QPushButton(self.tr('Copy'))
        self.hbox.addWidget(self.copy_button)
        self.vbox.addLayout(self.hbox)
        self.text_edit = QTextEdit()
        self.vbox.addWidget(self.text_edit)
        self.setLayout(self.vbox)