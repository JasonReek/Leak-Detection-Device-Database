from PySide2.QtWidgets import (QWidget, QLabel, QSizePolicy, QComboBox, QLineEdit, QGridLayout, QScroller, QScrollArea, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from PySide2.QtCore import (Qt, QRect)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, FormTextBox, DateEntry, FormGroupBox, FormEntry, FormCheckBox, VerticalFiller, HorizontalFiller
from LDF_Client import Client
from enum import Enum

class DeviceDetection(Enum):
    SHOWS_LEAK = FormCheckBox("Device is currently displaying a leak.")
    ALERT_PRESENT = FormCheckBox("Device is showing an alert.")
    AUDIO_AT_DEVICE = FormCheckBox("Audio at Device")
    VISUAL_AT_DEVICE = FormCheckBox("Visual at Device")
    PUSH_NOTIFY = FormCheckBox("Push Notification")
    IN_APP_ALERT = FormCheckBox("In-App-Alert")
    TEXT_MSG = FormCheckBox("Text Message")
    EMAIL = FormCheckBox("Email")
    AUTO_CALL = FormCheckBox("Auto Call")
    CALL_BY_RETAILER = FormCheckBox("Called by Retailer/Mfr")
    OTHER = FormEntry()
    LEAK_VOL = FormEntry(double_only=True)
    UNIT = FormEntry()
    LEAK_LOC = FormTextBox()
    LEAK_DISCOVERED = FormCheckBox("Leak discovered when device was installed?")
    LEAK_DIS_VOL = FormEntry(double_only=True)
    LEAK_DIS_UNIT = FormEntry()
    LEAK_DIS_LOC = FormTextBox()
    AP_PHASE_ID = Client.AP_PHASE_ID.value

    @property
    def data_type(self):
        return self.value.getType()

class DeviceDetectionTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(DeviceDetectionTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "DEVICE_DETECTION"
        self._table = DeviceDetection
        self._layout = QFormLayout(self)

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget(self)
        self._scroll_contents.setObjectName("ddscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="ddscroll"] {background-color: #FFFFFF;}')
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)

        self._child_widgets_not_set = True 

        self.connectWidgets()
        self.setDeviceStatusArea()
        self.setDetectedLeakArea()
        self.setLeakDiscoveredArea()
        self._scroll_layout.addRow(VerticalFiller(self))

    def setDeviceStatusArea(self):
        form_box = FormGroupBox("Device Status", self)
        form_box.frame_layout.addRow(DeviceDetection.ALERT_PRESENT.value)
        # Alert type inner group box
        alert_form_box = FormGroupBox("Check all that apply:", self)
        
        alert_grid = QWidget(self)
        alert_lay = QGridLayout(alert_grid)
        alert_lay.setContentsMargins(0,0,0,0)

        alert_lay.addWidget(DeviceDetection.AUDIO_AT_DEVICE.value, 0, 0)
        alert_lay.addWidget(DeviceDetection.IN_APP_ALERT.value, 0, 1)
        alert_lay.addWidget(DeviceDetection.AUTO_CALL.value, 0, 2)

        alert_lay.addWidget(DeviceDetection.VISUAL_AT_DEVICE.value, 1, 0)
        alert_lay.addWidget(DeviceDetection.TEXT_MSG.value, 1, 1)
        alert_lay.addWidget(DeviceDetection.CALL_BY_RETAILER.value, 1, 2)

        alert_lay.addWidget(DeviceDetection.PUSH_NOTIFY.value, 2, 0)
        alert_lay.addWidget(DeviceDetection.EMAIL.value, 2, 1)
        other_row = QWidget(self)
        other_lay = QFormLayout(other_row)
        other_lay.setContentsMargins(0,0,0,0)
        other_lay.addRow("Other?", DeviceDetection.OTHER.value)
        alert_lay.addWidget(other_row, 2, 2)
        alert_form_box.frame_layout.addRow(alert_grid)
        
        form_box.frame_layout.addRow(alert_form_box)
        self._scroll_layout.addRow(form_box)
    
    def setDetectedLeakArea(self):
        form_box = FormGroupBox("Detected Leak from Device", self)
        form_box.frame_layout.addRow(DeviceDetection.SHOWS_LEAK.value)
        vol_unit_row = QWidget(self)
        vol_unit_lay = QHBoxLayout(vol_unit_row)
        vol_unit_lay.setContentsMargins(0,0,0,0)
        vol_unit_lay.addWidget(QLabel("Volume:", self))
        vol_unit_lay.addWidget(DeviceDetection.LEAK_VOL.value)
        vol_unit_lay.addWidget(QLabel("Unit:", self))
        vol_unit_lay.addWidget(DeviceDetection.UNIT.value)
        vol_unit_lay.addWidget(HorizontalFiller(self))
        form_box.frame_layout.addRow(vol_unit_row)
        form_box.frame_layout.addRow("Leak Location:", DeviceDetection.LEAK_LOC.value)
        self._scroll_layout.addRow(form_box)
    
    def setLeakDiscoveredArea(self):
        form_box = FormGroupBox("Leak Discovered when Device was Installed", self)
        form_box.frame_layout.addRow(DeviceDetection.LEAK_DISCOVERED.value)
        vol_unit_row = QWidget(self)
        vol_unit_lay = QHBoxLayout(vol_unit_row)
        vol_unit_lay.setContentsMargins(0,0,0,0)
        vol_unit_lay.addWidget(QLabel("Volume:", self))
        vol_unit_lay.addWidget(DeviceDetection.LEAK_DIS_VOL.value)
        vol_unit_lay.addWidget(QLabel("Unit:", self))
        vol_unit_lay.addWidget(DeviceDetection.LEAK_DIS_UNIT.value)
        vol_unit_lay.addWidget(HorizontalFiller(self))
        form_box.frame_layout.addRow(vol_unit_row)
        form_box.frame_layout.addRow("Discovered Leak Location:", DeviceDetection.LEAK_DIS_LOC.value)
        self._scroll_layout.addRow(form_box)
    
    def connectWidgets(self):
        super().connectWidgets()
        # LEAK IS DETECTED
        leak_det_widgets = [DeviceDetection.LEAK_VOL, DeviceDetection.UNIT, DeviceDetection.LEAK_LOC]
        DeviceDetection.SHOWS_LEAK.value.stateChanged.connect(self.enableDisableCheck(
            DeviceDetection.SHOWS_LEAK,
            leak_det_widgets
        ))

        # LEAK DISCOVERED
        leak_dis_widgets = [DeviceDetection.LEAK_DIS_VOL, DeviceDetection.LEAK_DIS_UNIT, DeviceDetection.LEAK_DIS_LOC]
        DeviceDetection.LEAK_DISCOVERED.value.stateChanged.connect(self.enableDisableCheck(
            DeviceDetection.LEAK_DISCOVERED,
            leak_dis_widgets
        ))

        # ALERT IS PRESENT.
        disable_widgets = [DeviceDetection.AUDIO_AT_DEVICE, DeviceDetection.IN_APP_ALERT, DeviceDetection.AUTO_CALL,
         DeviceDetection.VISUAL_AT_DEVICE, DeviceDetection.TEXT_MSG, DeviceDetection.CALL_BY_RETAILER,
         DeviceDetection.PUSH_NOTIFY, DeviceDetection.EMAIL, DeviceDetection.OTHER]

        DeviceDetection.ALERT_PRESENT.value.stateChanged.connect(self.enableDisableCheck(
        DeviceDetection.ALERT_PRESENT, 
        disable_widgets))

        # DEFAULT DISABLE WIDGETS
        for widget in leak_det_widgets:
            widget.value.setDisabled(True)
        for widget in leak_dis_widgets:
            widget.value.setDisabled(True)
        for widget in disable_widgets:
            widget.value.setDisabled(True)

