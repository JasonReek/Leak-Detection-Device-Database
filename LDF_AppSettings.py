import sys
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon 

app = QApplication(sys.argv)
app.setStyle("Fusion")
app.setWindowIcon(QIcon("snwa_logo_icon.ico"))