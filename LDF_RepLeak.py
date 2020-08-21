from PySide2.QtWidgets import (QWidget, QLabel, QScrollArea, QSizePolicy, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, FormTextBox, FormCombo, DateEntry, FormGroupBox, FormEntry, FormCheckBox, SmartHFormLayout, VerticalFiller
from LDF_Client import Client
from enum import Enum

class RepLeak(Enum):
    LEAK_SHOWING = FormCheckBox("Leak Showing at Meter")
    VOL = FormEntry(double_only=True)
    UNIT = FormCombo(default_values=["gpm", "cfm"])
    LOCS = FormTextBox()
    MET_DEV_AGREE = FormCheckBox("Meter and Device Show the Same Leak Amount")
    MET_OR_DEV_HIGHER = FormCombo(default_values=["Meter", "Device"])
    CUS_INFORM = FormCheckBox("Customer Informed of Leak")
    REA_CUS_NOT_INFORM = FormTextBox()
    RESOLUTION = FormTextBox()
    AP_PHASE_ID = Client.AP_PHASE_ID.value

    @property
    def data_type(self):
        return self.value.getType()

class RepLeakTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(RepLeakTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "REP_LEAK"
        self._table = RepLeak
        self._layout = QFormLayout(self)
        self._child_widgets_not_set = True 

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget(self)
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll_contents.setObjectName("rplscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="rplscroll"] {background-color: #FFFFFF;}')
        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)

        self.connectWidgets()
        RepLeak.MET_DEV_AGREE.value.setChecked(True)
        RepLeak.CUS_INFORM.value.setChecked(True)
        self.setRepLeakArea()
        self._scroll_layout.addRow(VerticalFiller(self))

    def setRepLeakArea(self):
        form_box = FormGroupBox("Leak Discovered By SNWA Represenative", self)
        form_box.frame_layout.addRow(RepLeak.LEAK_SHOWING.value)
        vol_unit = QWidget(self)
        vol_unit_row = SmartHFormLayout(vol_unit)
        vol_unit_row.addRow(["Volume at Meter:", "Unit:"], [RepLeak.VOL.value, RepLeak.UNIT.value])
        form_box.frame_layout.addRow(vol_unit)
        form_box.frame_layout.addRow("Leak Location:", RepLeak.LOCS.value)

        metdev_box = FormGroupBox("Meter and Device", self)
        metdev_box.frame_layout.addRow(RepLeak.MET_DEV_AGREE.value)
        metdev_box.frame_layout.addRow("Which has a Higher Volume?", RepLeak.MET_OR_DEV_HIGHER.value)
        metdev_box.frame_layout.addRow(RepLeak.CUS_INFORM.value)
        metdev_box.frame_layout.addRow("If No, Explain:", RepLeak.REA_CUS_NOT_INFORM.value)
        metdev_box.frame_layout.addRow("Expected Resolution (If Known):", RepLeak.RESOLUTION.value)
        
        form_box.frame_layout.addRow(metdev_box)
        form_box.frame_layout.addRow(VerticalFiller(self))
        self._scroll_layout.addRow(form_box)
    
    def connectWidgets(self):
        super().connectWidgets()
        rep_leak_widgets = [RepLeak.VOL, RepLeak.UNIT, RepLeak.LOCS, RepLeak.MET_DEV_AGREE, RepLeak.MET_OR_DEV_HIGHER, RepLeak.CUS_INFORM, RepLeak.REA_CUS_NOT_INFORM, RepLeak.RESOLUTION]
        RepLeak.LEAK_SHOWING.value.stateChanged.connect(self.enableDisableCheck(
        RepLeak.LEAK_SHOWING, 
        rep_leak_widgets))

        RepLeak.MET_DEV_AGREE.value.stateChanged.connect(self.enableDisableCheck(
        RepLeak.MET_DEV_AGREE, 
        [RepLeak.MET_OR_DEV_HIGHER], reverse_check=True))

        RepLeak.CUS_INFORM.value.stateChanged.connect(self.enableDisableCheck(
        RepLeak.CUS_INFORM, 
        [RepLeak.REA_CUS_NOT_INFORM], reverse_check=True))

        for widget in rep_leak_widgets:
            widget.value.setDisabled(True)
    
    def enableDisableCheck(self, check_widget, widgets=[], reverse_check=False):
        def enableDisable():
            if len(widgets) > 0:
                for widget in widgets:
                    if reverse_check:
                        widget.value.setDisabled(check_widget.value.isChecked())
                    else:
                        widget.value.setEnabled(check_widget.value.isChecked())
                        if RepLeak.MET_DEV_AGREE.value.isChecked():
                            RepLeak.MET_OR_DEV_HIGHER.value.setDisabled(True)
                        if RepLeak.CUS_INFORM.value.isChecked():
                            RepLeak.REA_CUS_NOT_INFORM.value.setDisabled(True)
                if check_widget == RepLeak.LEAK_SHOWING:
                    self.MetDevAgreeCheck()
                    self.CusInformCheck()

        return enableDisable

    def MetDevAgreeCheck(self):
        if not RepLeak.MET_DEV_AGREE.value.isEnabled():
            RepLeak.MET_DEV_AGREE.value.setChecked(True)

    def CusInformCheck(self):
        if not RepLeak.CUS_INFORM.value.isEnabled():
            RepLeak.CUS_INFORM.value.setChecked(True)

        