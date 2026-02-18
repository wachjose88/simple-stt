import locale
import sys

from PySide6.QtCore import QTranslator, QLibraryInfo
from PySide6.QtWidgets import QMainWindow, QApplication


class DictationApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr('Dictionation'))
        self.show()


if __name__ == '__main__':
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
