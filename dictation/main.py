
import locale
import logging.config
import sys
from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

from PySide6.QtCore import QTranslator, QLibraryInfo
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox

from dictation.editor import Editor
from dictation.signals import DictationSignals
from dictation.stt import SpeechToText
from settings import LOGGING_CONFIG


logger = logging.getLogger('dictation.app')


class DictationApp(QMainWindow):

    def __init__(self, models_directory):
        super().__init__()
        logger.debug('Initializing Dictionation App')
        self.setWindowTitle(self.tr('Dictionation'))
        self.statusBar().showMessage(self.tr('Dictionation App Started'))

        self.models_directory = models_directory
        self.models = {str(x.name): x for x in self.models_directory.iterdir() if x.is_dir()}
        logger.debug(self.models)

        self.signals = DictationSignals()

        self.stt_thread = SpeechToText(self.signals)

        self.editor = Editor(self, self.models, self.stt_thread)
        self.signals.set_text_to_view.connect(self.editor.set_text_to_view)
        self.setCentralWidget(self.editor)
        self.show()

    def set_status(self, text):
        self.statusBar().showMessage(text)

    def stop_stt(self):
        if self.stt_thread.isRunning():
            self.stt_thread.stop = True
            self.stt_thread.wait()

    def closeEvent(self, event):
        result = QMessageBox.question(
            self,
            self.tr("Confirm Exit..."),
            self.tr("Are you sure you want to exit ?"),
            QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            event.accept()


def path_type(arg):
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
                        required=True)
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
    translator.load('locales/dictation_' + locale.getlocale()[0][0:2])
    app.installTranslator(translator)

    dapp = DictationApp(args.models_directory)
    sys.exit(app.exec())
