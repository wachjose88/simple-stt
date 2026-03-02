import logging

import language_tool_python
import requests
from PySide6.QtCore import QSize
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QGridLayout, QComboBox, QLabel, \
    QSizePolicy

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
        self.action_grid.setRowStretch(i, 5)
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

    def __init__(self, parent, models, stt_thread):
        super().__init__(parent)
        self.models = models
        self.stt_thread = stt_thread
        self.tool = language_tool_python.LanguageTool('de-AT')
        self.languages = requests.get(self.tool._url + 'languages').json()
        self.active_language = 'de-AT'
        self.start_text = self.tr('Start')
        self.stop_text = self.tr('Stop')
        self.vbox = QVBoxLayout()

        self.select_box = QGridLayout()

        self.select_model = QComboBox()
        self.language_label = QLabel(self.tr('Language'))
        self.model_label = QLabel(self.tr('Model'))
        self.select_box.addWidget(self.language_label, 0, 0)
        self.select_box.addWidget(self.model_label, 1, 0)
        for model in self.models:
            self.select_model.addItem(model)
        self.select_model.currentTextChanged.connect(self.select_model_changed)
        self.select_language = QComboBox()
        for language in self.languages:
            self.select_language.addItem(language['name'])
        self.select_language.setCurrentText(self.code_to_language(self.active_language))
        self.select_language.currentTextChanged.connect(self.select_language_changed)
        self.select_box.addWidget(self.select_language, 0, 1)
        self.select_box.addWidget(self.select_model, 1, 1)
        self.start_stop_button = QPushButton(self.start_text)
        self.start_stop_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.start_stop_button.clicked.connect(self.start_stop_button_clicked)
        self.select_box.addWidget(self.start_stop_button, 0, 2, 2, 1)
        self.copy_button = QPushButton(self.tr('Copy'))
        self.copy_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.copy_button.clicked.connect(self.copy_button_clicked)
        self.select_box.addWidget(self.copy_button, 0, 3, 2, 1)
        self.clear_button = QPushButton(self.tr('Clear'))
        self.clear_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.clear_button.clicked.connect(self.clear_button_clicked)
        self.select_box.addWidget(self.clear_button, 0, 4, 2, 1)
        self.vbox.addLayout(self.select_box)

        self.text_hbox = QHBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumSize(QSize(400, 400))
        self.text_hbox.addWidget(self.text_edit)
        self.action_panel = ActionPanel(self, self.text_edit)
        self.text_hbox.addWidget(self.action_panel)
        self.vbox.addLayout(self.text_hbox)
        self.setLayout(self.vbox)

    def clear_button_clicked(self):
        self.text_edit.clear()

    def set_text_to_view(self, text):
        logger.debug(self.text_edit.textCursor().position())
        add_space = True
        position = self.text_edit.textCursor().position()
        if position < 1:
            add_space = False
        else:
            last_char = self.text_edit.toPlainText()[position - 1]
            if last_char != ' ':
                add_space = True
        self.text_edit.insertPlainText(f' {text}' if add_space else text)

    def select_model_changed(self, text):
        logger.debug(f'Selected model {text}')

    def select_language_changed(self, text):
        logger.debug(f'Selected language {text}')
        lang = None
        for language in self.languages:
            if language['name'] == text:
                lang = language
                break
        if lang:
            self.active_language = lang['longCode']
            self.tool.close()
            self.tool = language_tool_python.LanguageTool(lang['longCode'])

    def start_stop_button_clicked(self):
        logger.debug('Start stop button')
        label = self.start_stop_button.text()
        if label == self.start_text:
            self.stt_thread.model_name = self.models[self.select_model.currentText()]
            self.stt_thread.stop = False
            self.stt_thread.start()
            self.start_stop_button.setText(self.stop_text)
            self.select_model.setDisabled(True)
            self.parent().set_status(self.tr('Recording started. Please dictate in ')
                                     + self.code_to_language(self.active_language))
        else:
            if self.stt_thread.isRunning():
                self.stt_thread.stop = True
                self.stt_thread.wait()
            self.start_stop_button.setText(self.start_text)
            self.select_model.setDisabled(False)
            self.parent().set_status(self.tr('Correcting text. Please wait.'))
            self.text_edit.setPlainText(
                self.tool.correct(self.text_edit.toPlainText())
            )
            self.parent().set_status(self.tr('Recording stopped.'))

    def copy_button_clicked(self):
        logger.debug('Copy button')
        clipboard = QGuiApplication.clipboard()
        text = self.text_edit.toPlainText()
        clipboard.setText(text)
        self.parent().set_status(self.tr('Text copied to clipboard.'))

    def code_to_language(self, code):
        for language in self.languages:
            if language['longCode'] == code:
                return language['name']
