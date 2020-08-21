from PySide2.QtWidgets import (QWidget, QLabel, QScrollArea, QSizePolicy, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, FormTextBox, DateEntry, FormGroupBox, FormEntry, FormCheckBox, FormSpinBox
from LDF_Client import Client
from enum import Enum


class Installation(Enum):
    SELF_INSTALLED = FormCheckBox("Self Installed?", reverse=True)
    OTHER_INSTALLER = FormEntry()
    INSTALL_COST = FormEntry(double_only=True)
    SUBSCRIPTION = FormCheckBox("Subscription?")
    SUBSCRIPTION_COST = FormEntry(double_only=True)
    FUNCTIONAL = FormCheckBox("Device is Functional?")
    SETUP_ON_PHONE = FormCheckBox("Device is setup on the phone.")
    EASE_OF_PHYS_INSTALL = FormSpinBox()
    EASE_OF_APP_INSTALL = FormSpinBox()
    EASE_OF_APP_USE = FormSpinBox()
    AP_PHASE_ID = Client.AP_PHASE_ID.value

    @property
    def data_type(self):
        return self.value.getType()

class InstallationTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(InstallationTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "INSTALLATION"
        self._table = Installation
        self._layout = QFormLayout(self)
        self._child_widgets_not_set = True 

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget(self)
        self._scroll_contents.setObjectName("iscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="iscroll"] {background-color: #FFFFFF;}')
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)

        self.connectWidgets()
        self.setInstallInfoArea()
        self.setSupscriptionArea()
        self.setDeviceSetupArea()
    
    def setInstallInfoArea(self):
        form_box = FormGroupBox("Install Information", self)
        form_box.frame_layout.addRow(Installation.SELF_INSTALLED.value)
        form_box.frame_layout.addRow("Other Installer:", Installation.OTHER_INSTALLER.value)
        form_box.frame_layout.addRow("Install Cost ($):", Installation.INSTALL_COST.value)
        self._scroll_layout.addRow(form_box)
    
    def setSupscriptionArea(self):
        form_box = FormGroupBox("Subscription", self)
        form_box.frame_layout.addRow(Installation.SUBSCRIPTION.value)
        form_box.frame_layout.addRow("Subscription Cost ($):", Installation.SUBSCRIPTION_COST.value)
        self._scroll_layout.addRow(form_box)
    
    def setDeviceSetupArea(self):
        formbox = FormGroupBox("Device Setup", self)
        formbox.frame_layout.addRow(Installation.FUNCTIONAL.value)
        formbox.frame_layout.addRow(Installation.SETUP_ON_PHONE.value)
        ratebox = FormGroupBox("Rate on a scale 1-5 (1 being the most difficult):", self)
        ratebox.frame_layout.addRow("Ease of Physical Install:", Installation.EASE_OF_PHYS_INSTALL.value)
        ratebox.frame_layout.addRow("Ease of App Install", Installation.EASE_OF_APP_INSTALL.value)
        ratebox.frame_layout.addRow("Ease of App Use:", Installation.EASE_OF_APP_USE.value)
        formbox.frame_layout.addRow(ratebox)
        self._scroll_layout.addRow(formbox)
        
    def connectWidgets(self):
        super().connectWidgets()
        # Disable widgets if not checked.
        Installation.SELF_INSTALLED.value.stateChanged.connect(self.enableDisableCheck(
        Installation.SELF_INSTALLED, 
        [Installation.OTHER_INSTALLER], reverse_check=True))

        Installation.SUBSCRIPTION.value.stateChanged.connect(self.enableDisableCheck(
        Installation.SUBSCRIPTION, 
        [Installation.SUBSCRIPTION_COST]))

        Installation.OTHER_INSTALLER.value.setDisabled(True)
        Installation.SUBSCRIPTION_COST.value.setDisabled(True)

