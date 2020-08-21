from PySide2.QtWidgets import (QWidget, QLabel, QScrollArea, QSizePolicy, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, FormTextBox, DateEntry, FormGroupBox, FormEntry, FormCheckBox, FormSpinBox, FormCombo
from LDF_Client import Client
from enum import Enum

class People(Enum):
    PEOPLE_COUNT = FormSpinBox(default_value=1, min_value=1, max_value=99)
    AGES = FormEntry(comma_sort=True)
    HIGHEST_EDU = FormCombo(default_values=["-- None Selected --", "High School or (G.E.D)", "Technical Degree", "Bachelor's Degree", "Graduate School"])
    AP_PHASE_ID = Client.AP_PHASE_ID.value

    @property
    def data_type(self):
        return self.value.getType()

class PeopleTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(PeopleTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "PEOPLE"
        self._table = People
        self._layout = QFormLayout(self)
        self._child_widgets_not_set = True 

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget(self)
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll_contents.setObjectName("peoscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="peoscroll"] {background-color: #FFFFFF;}')
        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)

        self.connectWidgets()
        self.setPeopleArea()

    def setPeopleArea(self):
        form_box = FormGroupBox("Occupant Information", self)
        form_box.frame_layout.addRow("Number of Occupants:", People.PEOPLE_COUNT.value)
        form_box.frame_layout.addRow("Occupant Ages:", People.AGES.value)
        form_box.frame_layout.addRow("Highest Education:", People.HIGHEST_EDU.value)
        self._scroll_layout.addRow(form_box)

        