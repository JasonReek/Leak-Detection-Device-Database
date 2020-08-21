from PySide2.QtWidgets import (QWidget, QLabel, QScrollArea, QSizePolicy, QGridLayout, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, FormTextBox, FormSpinBox, DateEntry, FormGroupBox, FormEntry, FormCheckBox, VerticalFiller, HorizontalFiller
from LDF_Client import Client
from enum import Enum

class CustomerKnowledge(Enum):
    INTEREST = FormSpinBox()
    SAT_PRICE = FormSpinBox()
    SAT_INSTALL = FormSpinBox()
    SAT_DEVICE = FormSpinBox()
    SAT_RETAILER = FormSpinBox()
    PROP_COND = FormSpinBox()
    NEIGHBORHOOD = FormSpinBox()
    KNOW_DEVICE = FormSpinBox()
    KNOW_WATER_USE = FormSpinBox()
    KNOW_SNWA = FormSpinBox()
    SAT_SNWA = FormSpinBox()
    NOTES = FormTextBox()
    AP_PHASE_ID = Client.AP_PHASE_ID.value

    @property
    def data_type(self):
        return self.value.getType()

class CustomerKnowledgeTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(CustomerKnowledgeTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "CUSTOMER_KNOWLEDGE"
        self._table = CustomerKnowledge
        self._layout = QFormLayout(self)
        self._child_widgets_not_set = True 

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget(self)
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll_contents.setObjectName("ckwscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="ckwscroll"] {background-color: #FFFFFF;}')
        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)

        self.connectWidgets()
        self.setCustKnowArea()
        self._scroll_layout.addWidget(VerticalFiller(self))

    def setCustKnowArea(self):
        form_box = FormGroupBox("Customer Knowledge / Satisfaction (Select 1 - 5, 1 being the least satisfied)", self)
        fix_and_app = QWidget(self)
        fix_and_app_lay = QGridLayout(fix_and_app)

        # ROW 1
        interest_box = FormGroupBox("Interest / Enthusiasm:", self)
        interest_box.frame_layout.addRow(CustomerKnowledge.INTEREST.value)
        fix_and_app_lay.addWidget(interest_box, 0, 0)
        neigh_box = FormGroupBox("Neighborhood:", self)
        neigh_box.frame_layout.addRow(CustomerKnowledge.NEIGHBORHOOD.value)
        fix_and_app_lay.addWidget(neigh_box, 0, 1) 
        # ROW 2
        sat_price_box = FormGroupBox("Satisfaction with the Device Price:", self)
        sat_price_box.frame_layout.addRow(CustomerKnowledge.SAT_PRICE.value)
        fix_and_app_lay.addWidget(sat_price_box, 1, 0)
        know_dev_box = FormGroupBox("Knowledge About the Device:", self)
        know_dev_box.frame_layout.addRow(CustomerKnowledge.KNOW_DEVICE.value)
        fix_and_app_lay.addWidget(know_dev_box, 1, 1) 
        # ROW 3
        sat_install_box = FormGroupBox("Satisfaction with the Installation:", self)
        sat_install_box.frame_layout.addRow(CustomerKnowledge.SAT_INSTALL.value)
        fix_and_app_lay.addWidget(sat_install_box, 2, 0)
        know_water_box = FormGroupBox("Knowledge About Water Use:", self)
        know_water_box.frame_layout.addRow(CustomerKnowledge.KNOW_WATER_USE.value)
        fix_and_app_lay.addWidget(know_water_box, 2, 1) 
        
        # ROW 4 (BLANK ROW) 
        fix_and_app_lay.addWidget(QLabel(""), 3, 0)
        
        # ROW 5
        sat_dev_box = FormGroupBox("Satisfaction with the Device:", self)
        sat_dev_box.frame_layout.addRow(CustomerKnowledge.SAT_DEVICE.value)
        fix_and_app_lay.addWidget(sat_dev_box, 4, 0)
        know_snwa_box = FormGroupBox("Knowledge About SNWA:", self)
        know_snwa_box.frame_layout.addRow(CustomerKnowledge.KNOW_SNWA.value)
        fix_and_app_lay.addWidget(know_snwa_box, 4, 1) 
        # ROW 6
        sat_retail_box = FormGroupBox("Satisfaction with the Retailer/Mfr:", self)
        sat_retail_box.frame_layout.addRow(CustomerKnowledge.SAT_RETAILER.value)
        fix_and_app_lay.addWidget(sat_retail_box, 5, 0)
        sat_snwa_box = FormGroupBox("Satisfaction with SNWA:", self)
        sat_snwa_box.frame_layout.addRow(CustomerKnowledge.SAT_SNWA.value)
        fix_and_app_lay.addWidget(sat_snwa_box, 5, 1)
        fix_and_app_lay.addWidget(HorizontalFiller(self), 5, 2) 
        # ROW 7
        prop_box = FormGroupBox("Condition of Property:", self)
        prop_box.frame_layout.addRow(CustomerKnowledge.PROP_COND.value)
        fix_and_app_lay.addWidget(prop_box, 6, 0) 

        form_box.frame_layout.addRow(fix_and_app)
      
        form_box.frame_layout.addRow("General Notes:", CustomerKnowledge.NOTES.value)
        self._scroll_layout.addRow(form_box)

        