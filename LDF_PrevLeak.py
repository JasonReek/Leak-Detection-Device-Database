from PySide2.QtWidgets import (QWidget, QLabel, QScrollArea, QSizePolicy, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, FormTextBox, DateEntry, FormGroupBox, FormEntry, FormCheckBox, FormTextBox, SmartHFormLayout, VerticalFiller, HorizontalFiller
from LDF_Client import Client
from enum import Enum

class PrevLeak(Enum):
    INFLUENCE = FormCheckBox("Previous Leak Influenced in purchasing Device")
    COST_TO_REPAIR = FormEntry(double_only=True)
    LOC = FormTextBox() 
    VOL = FormEntry(double_only=True)
    UNIT = FormEntry()
    CLAIM_FILED = FormCheckBox("Claim Filed") 
    CLAIM_AMT = FormEntry(double_only=True)
    DEDUCT = FormEntry(double_only=True)
    AP_PHASE_ID = Client.AP_PHASE_ID.value

    @property
    def data_type(self):
        return self.value.getType()

class PrevLeakTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(PrevLeakTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "PREV_LEAK"
        self._table = PrevLeak
        self._layout = QFormLayout(self)
        self._child_widgets_not_set = True 

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget(self)
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll_contents.setObjectName("prevleakscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="prevleakscroll"] {background-color: #FFFFFF;}')
        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)
        
        self.connectWidgets()
        self.setPrevLeakArea()
        self._scroll_layout.addRow(QWidget(self))
        self._scroll_layout.addRow(VerticalFiller(self))
    
    def getTabName(self):
        return "Previous Leak"

    def setPrevLeakArea(self):
        form_box = FormGroupBox("Previous Leak Information", self)
        form_box.frame_layout.addRow(PrevLeak.INFLUENCE.value)
        form_box.frame_layout.addRow("Location:", PrevLeak.LOC.value)
        form_box.frame_layout.addRow("Cost to Repair ($):", PrevLeak.COST_TO_REPAIR.value)
        vol_unit = QWidget()
        vol_unit_lay = QHBoxLayout(vol_unit)
        vol_unit_lay.setContentsMargins(0,0,0,0)
        vol_unit_lay.addWidget(QLabel("Volume (if known):", self))
        vol_unit_lay.addWidget(PrevLeak.VOL.value)
        vol_unit_lay.addWidget(QLabel("Unit:",self))
        vol_unit_lay.addWidget(PrevLeak.UNIT.value)
        vol_unit_lay.addWidget(HorizontalFiller(self))
        form_box.frame_layout.addRow(vol_unit)
        claim_box = FormGroupBox("Claim Information:", self)
        claim_box.frame_layout.addRow(PrevLeak.CLAIM_FILED.value)
        claim_box.frame_layout.addRow("Total Claim Amount ($):", PrevLeak.CLAIM_AMT.value)
        claim_box.frame_layout.addRow("Deductible ($):", PrevLeak.DEDUCT.value)
        form_box.frame_layout.addRow(claim_box)
        self._scroll_layout.addRow(form_box)
        
    def connectWidgets(self):
        super().connectWidgets()
        prev_leak_widgets = [PrevLeak.LOC, PrevLeak.COST_TO_REPAIR, PrevLeak.VOL, PrevLeak.UNIT, PrevLeak.CLAIM_FILED, PrevLeak.CLAIM_AMT, PrevLeak.DEDUCT]
        PrevLeak.INFLUENCE.value.stateChanged.connect(self.enableDisableCheck(
        PrevLeak.INFLUENCE, 
        prev_leak_widgets))

        PrevLeak.CLAIM_FILED.value.stateChanged.connect(self.enableDisableCheck(
        PrevLeak.CLAIM_FILED, 
        [PrevLeak.CLAIM_AMT, PrevLeak.DEDUCT]))

        for widget in prev_leak_widgets:
            widget.value.setDisabled(True)
    
    def enableDisableCheck(self, check_widget, widgets=[], reverse_check=False):
        def enableDisable():
            if len(widgets) > 0:
                for widget in widgets:
                    if reverse_check:
                        widget.value.setDisabled(check_widget.value.isChecked())
                    else:
                        widget.value.setEnabled(check_widget.value.isChecked())
                        if not PrevLeak.CLAIM_FILED.value.isChecked():
                            PrevLeak.CLAIM_AMT.value.setDisabled(True)
                            PrevLeak.DEDUCT.value.setDisabled(True)
                if check_widget == PrevLeak.INFLUENCE:
                    self.claimFileCheck()
        return enableDisable

    def claimFileCheck(self):
        if not PrevLeak.CLAIM_FILED.value.isEnabled():
            PrevLeak.CLAIM_FILED.value.setChecked(False)
    



        