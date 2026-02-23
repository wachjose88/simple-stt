import logging
import re

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QGridLayout, QComboBox

logger = logging.getLogger('dictation.app')


class ActionPanel(QWidget):

    def __init__(self: QWidget, parent: QWidget, text_edit: QTextEdit):
        super().__init__(parent)
        self.text_edit = text_edit

        self.actions = {
            self.tr('Period .'): '. ',
            self.tr('Comma ,'): ', ',
            self.tr('Colon :'): ': ',
            self.tr('Semicolon ;'): '; ',
            self.tr('Question Mark ?'): '? ',
            self.tr('Exclamation Mark !'): '! ',
            self.tr('Open Bracket ('): '(',
            self.tr('Closed Bracket )'): ') ',
            self.tr('Open Square Bracket ['): '[',
            self.tr('Closed Square Bracket ]'): '] ',
            self.tr('Open Curly Bracket {'): '{',
            self.tr('Closed Curly Bracket }'): '} ',
        }

        self.action_grid = QGridLayout()
        self.new_line_button = QPushButton(self.tr('New Line'))
        self.new_line_button.clicked.connect(self.add_nl_to_text)
        self.action_grid.addWidget(self.new_line_button, 0, 0, 1, 2)
        i = 0
        for name, action in self.actions.items():
            action_button = QPushButton(name)
            action_button.clicked.connect(self.add_to_text)
            #self.actions[i].append(action_button)
            row = int(i / 2) + 1
            col = int(i % 2)
            self.action_grid.addWidget(action_button, row, col)
            i = i + 1
        self.setLayout(self.action_grid)

    def add_to_text(self):
        text = self.sender().text()
        text = self.actions[text]
        logger.debug(f'Add text {text}')
        self.text_edit.insertPlainText(text)
        self.text_edit.setFocus()

    def add_nl_to_text(self):
        logger.debug('Add New Line')
        self.text_edit.insertPlainText('\n')
        self.text_edit.setFocus()


class Editor(QWidget):

    def __init__(self, parent, models):
        super().__init__(parent)
        self.models = models
        self.start_text = self.tr('Start')
        self.stop_text = self.tr('Stop')
        self.vbox = QVBoxLayout()

        self.hbox = QHBoxLayout()
        self.select_model = QComboBox()
        for model in self.models:
            self.select_model.addItem(model)
        self.select_model.currentTextChanged.connect(self.select_model_changed)
        self.hbox.addWidget(self.select_model)
        self.start_stop_button = QPushButton(self.start_text)
        self.start_stop_button.clicked.connect(self.start_stop_button_clicked)
        self.hbox.addWidget(self.start_stop_button)
        self.copy_button = QPushButton(self.tr('Copy'))
        self.copy_button.clicked.connect(self.copy_button_clicked)
        self.hbox.addWidget(self.copy_button)
        self.vbox.addLayout(self.hbox)

        self.text_hbox = QHBoxLayout()
        self.text_edit = QTextEdit()
        self.text_hbox.addWidget(self.text_edit)
        self.action_panel = ActionPanel(self, self.text_edit)
        self.text_hbox.addWidget(self.action_panel)
        self.vbox.addLayout(self.text_hbox)
        self.setLayout(self.vbox)

    def select_model_changed(self, text):
        logger.debug(f'Selected model {text}')

    def start_stop_button_clicked(self):
        logger.debug('Start stop button')
        label = self.start_stop_button.text()
        if label == self.start_text:
            self.start_stop_button.setText(self.stop_text)
            self.select_model.setDisabled(True)
        else:
            self.start_stop_button.setText(self.start_text)
            self.select_model.setDisabled(False)

    def copy_button_clicked(self):
        logger.debug('Copy button')
        clipboard = QGuiApplication.clipboard()
        text = self.text_edit.toPlainText()
        clipboard.setText(text)
