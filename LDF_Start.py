import sys
import os  
from PySide2.QtWidgets import (QApplication, QSplashScreen)
from PySide2.QtGui import QPixmap
from PySide2.QtCore import (Qt, QTimer) 
from LDF_AppSettings import app

if __name__ == '__main__':
    spscr_pixmap = QPixmap("splash-screen.png")
    splash = QSplashScreen(spscr_pixmap)
    splash.show()
    splash.showMessage("Loading dependencies...", alignment=Qt.AlignBottom)

    def start():
        from LDF_GUI import Window
        window = Window()
        splash.close()
        window.start()

    start()


