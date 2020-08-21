from PySide2.QtWidgets import (QLayout, QWidget, QScrollArea, QSizePolicy, QLabel, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, DateEntry, FormGroupBox, FormEntry, FormCheckBox, HorizontalFiller, SmartHFormLayout
from enum import Enum

class Client(Enum):
    ADDRESS = FormEntry()
    DATE = DateEntry()
    FIRST_NAME = FormEntry()
    LAST_NAME = FormEntry()
    OTHER_NAME = FormCheckBox("Different person than above met onsite?")
    OTHER_FIRST_NAME = FormEntry()
    OTHER_LAST_NAME = FormEntry()
    SNWA_REP_FIRST_NAME = FormEntry()
    SNWA_REP_LAST_NAME	= FormEntry()
    AP_PHASE_ID = FormEntry()

    @property
    def data_type(self):
        return self.value.getType()

class ClientTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(ClientTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "CLIENT"
        self._table = Client
        self._layout = QFormLayout(self)
        self._child_widgets_not_set = True  

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget()
        
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll_contents.setObjectName("cscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="cscroll"] {background-color: #FFFFFF;}')
        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)
        
        
        self.connectWidgets()
        self.setEvaluationArea()
        self.setRepArea()
        self.setClientArea()

    def setEvaluationArea(self):
        form_box = FormGroupBox("Evaluation", self)
        #form_box = FormBox("Evaluation", self)
        only_int = QIntValidator(self)
        only_int.setTop(999999)
        Client.AP_PHASE_ID.value.setValidator(only_int)
        form_box.frame_layout.addRow("ApPhase ID:", Client.AP_PHASE_ID.value)
        form_box.frame_layout.addRow("Date:", Client.DATE.value)
        form_box.frame_layout.addRow("Address:", Client.ADDRESS.value)
        self._scroll_layout.addRow(form_box)
    
    def setClientArea(self):
        form_box = FormGroupBox("Client", self)
        #form_box = FormBox("Client", self)
        client_name_row = QWidget(self)
        other_name_row = QWidget(self)
        client_name_layout = SmartHFormLayout(client_name_row)
        other_name_layout = SmartHFormLayout(other_name_row)
        client_name_layout.addRow(["First Name:", "Last Name:"], [Client.FIRST_NAME.value, Client.LAST_NAME.value])
        other_name_layout.addRow(["First Name:", "Last Name:"], [Client.OTHER_FIRST_NAME.value, Client.OTHER_LAST_NAME.value])
        form_box.frame_layout.addRow(client_name_row)
        form_box.frame_layout.addRow(Client.OTHER_NAME.value)
        form_box.frame_layout.addRow(other_name_row)
        self._scroll_layout.addRow(form_box)

    def setRepArea(self):
        form_box = FormGroupBox("SNWA Represenative", self)
        #form_box = FormBox("SNWA Represenative", self)
        name_row = QWidget(self)
        name_layout = SmartHFormLayout(name_row)
        name_layout.addRow(["First Name:", "Last Name:"], [Client.SNWA_REP_FIRST_NAME.value, Client.SNWA_REP_LAST_NAME.value])
        form_box.frame_layout.addRow(name_row)
        self._scroll_layout.addRow(form_box)

    def connectWidgets(self):
        super().connectWidgets()
        # Disable widgets if not checked.
   
        Client.OTHER_NAME.value.stateChanged.connect(self.enableDisableCheck(
        Client.OTHER_NAME, 
        [Client.OTHER_FIRST_NAME, Client.OTHER_LAST_NAME]))

        Client.OTHER_FIRST_NAME.value.setDisabled(True)
        Client.OTHER_LAST_NAME.value.setDisabled(True)
    


