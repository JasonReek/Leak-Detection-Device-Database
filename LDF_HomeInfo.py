from PySide2.QtWidgets import (QWidget, QLabel, QScrollArea, QSizePolicy, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, FormTextBox, DateEntry, FormGroupBox, FormEntry, FormCheckBox
from LDF_Client import Client
from enum import Enum

class HomeInfo(Enum):
    PARCEL = FormEntry()
    REDFIN_VAL = FormEntry(double_only=True)
    AP_PHASE_ID = Client.AP_PHASE_ID.value

    @property
    def data_type(self):
        return self.value.getType()

class HomeInfoTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(HomeInfoTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "HOME_INFO"
        self._table = HomeInfo
        self._layout = QFormLayout(self)
        self._child_widgets_not_set = True 

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget(self)
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll_contents.setObjectName("hinfoscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="hinfoscroll"] {background-color: #FFFFFF;}')
        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)

        self.connectWidgets()
        self.setHomeInfoArea()

    def setHomeInfoArea(self):
        form_box = FormGroupBox("Home Information", self)
        form_box.frame_layout.addRow("Parcel:", HomeInfo.PARCEL.value)
        form_box.frame_layout.addRow("RedFin Home Value:", HomeInfo.REDFIN_VAL.value)
        self._scroll_layout.addRow(form_box)

        