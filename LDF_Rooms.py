from PySide2.QtWidgets import (QWidget, QLabel, QScrollArea, QSizePolicy, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, FormTextBox, DateEntry, FormGroupBox, FormEntry, FormSpinBox, VerticalFiller
from LDF_Client import Client
from enum import Enum

class Rooms(Enum):
    NUM_OF_FULL_BATHS = FormSpinBox(default_value=1, min_value=0, max_value=99)
    NUM_OF_HALF_BATHS = FormSpinBox(default_value=0, min_value=0, max_value=99)
    NUM_OF_BEDROOMS = FormSpinBox(default_value=1, min_value=0, max_value=99)
    AP_PHASE_ID = Client.AP_PHASE_ID.value

    @property
    def data_type(self):
        return self.value.getType()

class RoomsTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(RoomsTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "ROOMS"
        self._table = Rooms
        self._layout = QFormLayout(self)
        self._child_widgets_not_set = True 

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget(self)
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll_contents.setObjectName("roomscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="roomscroll"] {background-color: #FFFFFF;}')
        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)

        self.connectWidgets()
        self.setRoomsArea()
        self._scroll_layout.addRow(VerticalFiller(self))

    def setRoomsArea(self):
        form_box = FormGroupBox("Client Room Information", self)
        form_box.frame_layout.addRow("Number of Full Bathrooms:", Rooms.NUM_OF_FULL_BATHS.value)
        form_box.frame_layout.addRow("Number of Half Bathrooms:", Rooms.NUM_OF_HALF_BATHS.value)
        form_box.frame_layout.addRow("Number of Bedrooms:", Rooms.NUM_OF_BEDROOMS.value)

        self._scroll_layout.addRow(form_box)

        