# MIT License
#
# Copyright (c) 2026 Josef Wachtler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""The editor module provides the UI widgets for the editor.

This module provides two widgets. The first one (ActionPanel) defines buttons
to add specific characters to the editor. The second one (Editor) defines
the editor, loads the ActionPanel and offers controls for the dictation.
"""

import logging

import language_tool_python
import requests
from PySide6.QtCore import QSize
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QGridLayout, QComboBox, QLabel, \
    QSizePolicy

from dictation.stt import CorrectText

logger = logging.getLogger('dictation.app')
"""Logger instance for the app."""


class ActionPanel(QWidget):
    """This class provides buttons to add specific characters to the editor.

    This UI widget defines a grid and adds buttons to it. Each button adds
    a specific character to the provided editor widget. The button names and
    their character to add are defined in the actions attribute which is a dict.

    Attributes:
        text_edit (QTextEdit): the editor to add the characters
        actions (dict): a dictionary that maps characters to button names

    Arguments:
        parent (QWidget): the parent widget
        text_edit (QTextEdit): the editor to add the characters
    """

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
        """This method adds characters to the editor widget.

        This slot is connected to each action button. It adds the character
        identified by the button to the editor widget.
        """
        text = self.sender().text()
        text = self.actions[text]
        logger.debug(f'Add text {text}')
        self.text_edit.insertPlainText(text)
        self.text_edit.setFocus()

    def add_nl_to_text(self):
        """This method adds a new line to the editor widget.

        This slot is connected to new line button. It adds a LF
        to the editor widget.
        """
        logger.debug('Add New Line')
        self.text_edit.insertPlainText('\n')
        self.text_edit.setFocus()


class Editor(QWidget):
    """This class represents the editor widget.

    This widget shows a line edit as the editor and places the ActionPanel
    on the right hand side of the editor. On top it shows some controls to
    select the language and the dictation model together with buttons to
    start or stop the dictation, to clear the editor and to copy the
    text from the editor to the clipboard.

    Attributes:
        models (dict): All vosk models. key: name, value: its path.
        stt_thread: SpeechToText thread.
        tool (LanguageTool): Language Tool object.
        languages (list): languages provided by Language Tool.
        active_language (str): Active language.
        correction (CorrectText): Thread to correct the text.

    Arguments:
        parent (QWidget): Parent widget.
        models (dict): All vosk models. key: name, value: its path.
        stt_thread (QThread): SpeechToText thread.
    """

    def __init__(self, parent, models, stt_thread):
        super().__init__(parent)
        self.models = models
        self.stt_thread = stt_thread
        self.tool = language_tool_python.LanguageTool('de-AT')
        self.languages = requests.get(self.tool._url + 'languages').json()
        self.active_language = 'de-AT'
        self.correction = CorrectText(self.parent().signals, self.tool)
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
        """Slot to clear the editor."""
        self.text_edit.clear()

    def set_text_to_view(self, text):
        """Adds text to the editor.

        This method adds text to the editor at the current cursor position.
        If the character before the position is not a space, it adds one.

        Arguments:
            text (str): The text to be added to the editor.
        """
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

    def select_language_changed(self, text):
        """Slot to change the language of Language Tool.

        This method changes the language of the Language Tool. It stops
        the current language tool and inits a new one with the new language.

        Arguments:
            text (str): The language name of the new language.
        """
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
        """Slot of the start/stop button.

        This method toggles between recording or not recording for the
        dictation. It uses the stt_thread to record the dictation.
        """
        logger.debug('Start stop button')
        label = self.start_stop_button.text()
        if label == self.start_text:
            self.parent().set_status(self.tr('Loading model. Please wait.'))
            self.stt_thread.model_name = self.models[self.select_model.currentText()]
            self.stt_thread.stop = False
            self.stt_thread.start()

        else:
            self.parent().set_status(self.tr('Correcting text. Please wait.'))
            if self.stt_thread.isRunning():
                self.stt_thread.stop = True
                self.stt_thread.wait()
            self.text_edit.setDisabled(True)
            self.correction.text = self.text_edit.toPlainText()
            self.correction.start()

    def correction_finished(self, text):
        """Slot of the finished  correction."""
        self.text_edit.setDisabled(True)
        self.start_stop_button.setText(self.start_text)
        self.select_model.setDisabled(False)
        self.text_edit.setPlainText(text)
        self.text_edit.setDisabled(False)
        self.parent().set_status(self.tr('Recording stopped.'))

    def model_ready(self):
        """Slot for starting dictation after the model is ready."""
        self.parent().set_status(self.tr('Recording started. Please dictate in ')
                                 + self.code_to_language(self.active_language))
        self.start_stop_button.setText(self.stop_text)
        self.select_model.setDisabled(True)

    def copy_button_clicked(self):
        """Slot to copy the text from the editor to the clipboard."""
        logger.debug('Copy button')
        clipboard = QGuiApplication.clipboard()
        text = self.text_edit.toPlainText()
        clipboard.setText(text)
        self.parent().set_status(self.tr('Text copied to clipboard.'))

    def code_to_language(self, code):
        """Returns the language name of the given language code.

        Arguments:
            code (str): The language code (e.g. de-AT).
        """
        for language in self.languages:
            if language['longCode'] == code:
                return language['name']
