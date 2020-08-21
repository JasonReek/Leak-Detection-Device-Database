from PySide2.QtWidgets import (QWidget, QLabel, QScrollArea, QSizePolicy, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, FormTextBox, DateEntry, FormGroupBox, FormEntry, FormCheckBox, FormCombo, VerticalFiller
from LDF_Client import Client
from enum import Enum

REASONS = ["-- None Selected --", "Previous Leak", "Protecting Property", "Monitoring Use", "Money Savings", "Water Conservation", "Electronics Hobbiest"]

class Motivations(Enum):
    CUST_MOTIVE = FormTextBox()
    REASON_1 = FormCombo(default_values=REASONS, reason_combo=True)
    REASON_2 = FormCombo(default_values=REASONS, reason_combo=True)
    REASON_3 = FormCombo(default_values=REASONS, reason_combo=True)
    DEVICE_CHOICE = FormTextBox()
    OTHER_PROG = FormTextBox()
    GEN_INTEREST = FormTextBox()
    FEEDBACK = FormTextBox()
    AP_PHASE_ID = Client.AP_PHASE_ID.value

    @property
    def data_type(self):
        return self.value.getType()

class MotivationsTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(MotivationsTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "MOTIVATIONS"
        self._table = Motivations
        self._layout = QFormLayout(self)
        self._child_widgets_not_set = True 

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget(self)
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll_contents.setObjectName("mscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="mscroll"] {background-color: #FFFFFF;}')
        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)
        
        reason_combos = [Motivations.REASON_1.value, Motivations.REASON_2.value, Motivations.REASON_3.value]
        for combo in reason_combos:
            combo.setReasonCombos(reason_combos)
            combo.activated.connect(combo.reasonCombos)

        self.connectWidgets()
        self.setReasonsArea()
        self.setGeneralMotivationsArea()
        self._scroll_layout.addRow(VerticalFiller(self))

    def setReasonsArea(self):
        form_box = FormGroupBox("Client Reasoning", self)
        form_box.frame_layout.addRow("Reason for Detection System:", Motivations.CUST_MOTIVE.value)
        rank_box = FormGroupBox("Client's Reasons by Ranking:", self)
        rank_box.frame_layout.addRow("1st:", Motivations.REASON_1.value)
        rank_box.frame_layout.addRow("2nd:", Motivations.REASON_2.value)
        rank_box.frame_layout.addRow("3rd:", Motivations.REASON_3.value)
        form_box.frame_layout.addRow(rank_box)
        self._scroll_layout.addRow(form_box)
                    
    def setGeneralMotivationsArea(self):
        form_box = FormGroupBox("General Motivations Questionaire", self)
        form_box.frame_layout.addRow("Other Water Conservation Programs:", Motivations.OTHER_PROG.value)
        form_box.frame_layout.addRow("Reason for this Device Brand:", Motivations.DEVICE_CHOICE.value)
        form_box.frame_layout.addRow("Client's General Interests:", Motivations.GEN_INTEREST.value)
        form_box.frame_layout.addRow("Feedback From Client:", Motivations.FEEDBACK.value)
        self._scroll_layout.addRow(form_box)
