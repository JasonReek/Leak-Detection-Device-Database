from PySide2.QtWidgets import (QWidget, QLabel, QScrollArea, QSizePolicy, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, FormTextBox, DateEntry, FormGroupBox, FormEntry, FormCheckBox
from LDF_Client import Client
from enum import Enum

class Economic(Enum):
    POC = FormEntry()
    HOME_VAL = FormEntry(double_only=True)
    INCOME = FormEntry(double_only=True)
    AP_PHASE_ID = Client.AP_PHASE_ID.value

    @property
    def data_type(self):
        return self.value.getType()

class EconomicTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(EconomicTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "ECONOMIC"
        self._table = Economic
        self._layout = QFormLayout(self)
        self._child_widgets_not_set = True 

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget(self)
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll_contents.setObjectName("ecoscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="ecoscroll"] {background-color: #FFFFFF;}')
        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)

        self.connectWidgets()
        self.setEconomicArea()

    def setEconomicArea(self):
        form_box = FormGroupBox("Economic Information", self)
        form_box.frame_layout.addRow("Employment Status:", Economic.POC.value)
        form_box.frame_layout.addRow("Home Value:", Economic.HOME_VAL.value)
        form_box.frame_layout.addRow("Income:", Economic.INCOME.value)
        self._scroll_layout.addRow(form_box)

        