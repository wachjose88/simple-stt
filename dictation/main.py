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

"""The main module defines the main window and starts the app.

This is the main module of the dictation app. It defines the main window and
starts the app. On starting the app the translation files are also loaded.

CLI arguments:
    -md, --models-directory: Directory containing vosk models.
"""

import locale
import logging.config
import sys
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

from PySide6.QtCore import QTranslator, QLibraryInfo
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox, QFileDialog

from dictation.editor import Editor
from dictation.signals import DictationSignals
from dictation.stt import SpeechToText
from dictation.settings import LOGGING_CONFIG


logger = logging.getLogger('dictation.app')
"""Logger instance for the app."""


class DictationApp(QMainWindow):
    """The main window for the dictation app.

    This class represents the main window for the dictation app.
    It lists the models for the speech recognition with vosk from the
    given directory. It also handles the custom signals of the app and
    the thread for the speech recognition. Finally it shows the editor
    widget.

    Args:
        models_directory (str): Directory containing vosk models.

    Attributes:
        models_directory (str): Directory containing vosk models.
        models (dict): All vosk models. key: name, value: its path
        signals: The signals of the app.
        stt_thread: SpeechToText thread.
        editor: Editor widget.
    """

    def __init__(self, models_directory):
        super().__init__()
        if not models_directory:
            logger.debug('select models directory')
            models_directory = QFileDialog.getExistingDirectory(
                self,
                self.tr('Select directory for vosk models')
            )
            try:
                models_directory = Path(models_directory).resolve(strict=True)
            except OSError:
                QMessageBox.warning(
                    self,
                    self.tr('No valid directory selected.'),
                    self.tr('Please select an existing directory.')
                )
                return

        logger.debug('Initializing Dictionation App')
        self.setWindowTitle(self.tr('Dictionation'))
        self.statusBar().showMessage(self.tr('Dictionation App Started'))

        self.models_directory = models_directory
        self.models = {str(x.name): x for x in self.models_directory.iterdir() if x.is_dir()}
        logger.debug(self.models)

        self.signals = DictationSignals()

        self.stt_thread = SpeechToText(self.signals, self)

        self.editor = Editor(self, self.models, self.stt_thread)
        self.signals.set_text_to_view.connect(self.editor.set_text_to_view)
        self.signals.model_ready.connect(self.editor.model_ready)
        self.signals.correction_finished.connect(self.editor.correction_finished)
        self.setCentralWidget(self.editor)
        self.show()

    def set_status(self, text):
        """Shows a message in the status bar.

        Args:
            text (str): The text to show in the status bar.
        """
        self.statusBar().showMessage(text)

    def stop_stt(self):
        """Stops the speech recognition thread.

        It is only stopped if it is running. The UI thread waits until
        the stt thread is stopped.
        """
        if self.stt_thread.isRunning():
            self.stt_thread.stop = True
            self.stt_thread.wait()

    def closeEvent(self, event):
        """Close event of the main window.

        It asks if the window should really be closed. If yes the stt thread
        is stopped.

        Args:
            event: The event object.
        """
        result = QMessageBox.question(
            self,
            self.tr("Confirm Exit..."),
            self.tr("Are you sure you want to exit ?"),
            QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            self.stop_stt()
            event.accept()


def path_type(arg):
    """Validates a path in an argument.

    This helper function validates a string to a path.

    Args:
        arg (str): The string of a path to validate.
    """
    logger.debug(arg)
    try:
        path = Path(arg).resolve(strict=True)
        logger.debug(path)
        return path
    except OSError:
        raise ArgumentTypeError()


if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_CONFIG)

    parser = ArgumentParser(
        prog='main.py',
        description='A very simple speech to text application.'
    )
    parser.add_argument('-md', '--models-directory',
                        type=path_type,
                        help='Directory containing vosk models',
                        required=False)
    args = parser.parse_args()

    app = QApplication(sys.argv)
    qtbase_translator = QTranslator()
    qtbase_translator.load(
        'qtbase_' + locale.getlocale()[0][0:2],
        QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
    app.installTranslator(qtbase_translator)
    qt_translator = QTranslator()
    qt_translator.load(
        'qt_' + locale.getlocale()[0][0:2],
        QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
    app.installTranslator(qt_translator)
    translator = QTranslator()
    translator.load('dictation_' + locale.getlocale()[0][0:2],
                    str(Path(__file__).parent / 'locales'))
    app.installTranslator(translator)

    dapp = DictationApp(args.models_directory)
    sys.exit(app.exec())
