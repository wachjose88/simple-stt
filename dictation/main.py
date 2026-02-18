import locale
import logging.config
import sys

from PySide6.QtCore import QTranslator, QLibraryInfo
from PySide6.QtWidgets import QMainWindow, QApplication, QMessageBox

from dictation.editor import Editor
from settings import LOGGING_CONFIG


logger = logging.getLogger('dictation.app')


class DictationApp(QMainWindow):

    def __init__(self):
        super().__init__()
        logger.debug('Initializing Dictionation App')
        self.setWindowTitle(self.tr('Dictionation'))
        self.statusBar().showMessage(self.tr('Dictionation App Started'))

        self.editor = Editor(self)
        self.setCentralWidget(self.editor)
        self.show()

    def closeEvent(self, event):
        result = QMessageBox.question(
            self,
            self.tr("Confirm Exit..."),
            self.tr("Are you sure you want to exit ?"),
            QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            event.accept()


if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_CONFIG)
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
    dapp = DictationApp()
    sys.exit(app.exec())
