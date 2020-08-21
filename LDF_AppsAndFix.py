from PySide2.QtWidgets import (QWidget, QLabel, QScrollArea, QSizePolicy, QGridLayout, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QGroupBox, QTabWidget, QCheckBox, QHBoxLayout)
from PySide2.QtGui import (QIcon, QIntValidator, QKeySequence, QFont)
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_Widgets import Form, FormTextBox, FormSpinBox, DateEntry, FormGroupBox, FormEntry, FormCheckBox, VerticalFiller, HorizontalFiller
from LDF_Client import Client
from enum import Enum

class FixAndApp(Enum):
    TOILETS = FormSpinBox(default_value=1, min_value=0, max_value=99)
    SINKS = FormSpinBox(default_value=1, min_value=1, max_value=99)
    SHOWERS = FormSpinBox(default_value=1, min_value=0, max_value=99)
    TUBS = FormSpinBox(default_value=1, min_value=0, max_value=99)
    DISHWASHERS = FormSpinBox(default_value=1, min_value=0, max_value=99)
    CLOTHES_WASHERS = FormSpinBox(default_value=1, min_value=0, max_value=99)
    WATER_HEATERS = FormSpinBox(default_value=1, min_value=0, max_value=99)
    TANKLESS_HEATERS = FormSpinBox(default_value=1, min_value=0, max_value=99)
    SOFTENERS = FormSpinBox(default_value=1, min_value=0, max_value=99)
    RO = FormSpinBox(default_value=1, min_value=0, max_value=99)
    POOL = FormSpinBox(default_value=1, min_value=0, max_value=99)
    SPA = FormSpinBox(default_value=1, min_value=0, max_value=99)
    AUTO_REFILL = FormCheckBox("Auto Refill")
    SPRAY_STATIONS = FormSpinBox(default_value=1, min_value=0, max_value=999)
    DRIP_STATIONS = FormSpinBox(default_value=1, min_value=0, max_value=999)
    SMART_CONTROLLER = FormCheckBox("Smart Controller")
    SMART_MODE_ACT = FormCheckBox("Smart Mode Activated")
    OTHER = FormTextBox()
    FIRE_SPRINKLER = FormCheckBox("Fire Sprinkler Installed")
    AP_PHASE_ID = Client.AP_PHASE_ID.value

    @property
    def data_type(self):
        return self.value.getType()
    
    @property
    def table_fields(self):
        return self.value._table

class FixAndAppTab(QWidget, Form):
    def __init__(self, parent=None, database=None):
        super(FixAndAppTab, self).__init__(parent)
        Form.__init__(self, parent)
        self._database = database
        self._table_name = "FIX_AND_APP"
        self._table = FixAndApp
        self._layout = QFormLayout(self)
        self._child_widgets_not_set = True 

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._layout.addRow(self._scroll)
        self._scroll_contents = QWidget(self)
        self._scroll_contents.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._scroll_contents.setObjectName("apfxscroll")
        self._scroll_contents.setStyleSheet('QWidget[objectName^="apfxscroll"] {background-color: #FFFFFF;}')
        self._scroll.setWidget(self._scroll_contents)
        self._scroll_layout = QFormLayout(self._scroll_contents)

        self.connectWidgets()
        self.setFixAppArea()
        self._scroll_layout.addWidget(VerticalFiller(self))

    def getTabName(self):
        return "Fixtures and Appliances"

    def setFixAppArea(self):
        form_box = FormGroupBox("Fixture and Appliance Counts", self)
        fix_and_app = QWidget(self)
        fix_and_app_lay = QGridLayout(fix_and_app)

        toilet_box = FormGroupBox("Toilets:", self)
        toilet_box.frame_layout.addRow(FixAndApp.TOILETS.value)
        fix_and_app_lay.addWidget(toilet_box, 0, 0)
        
        soft_box = FormGroupBox("Softeners:", self)
        soft_box.frame_layout.addRow(FixAndApp.SOFTENERS.value)
        fix_and_app_lay.addWidget(soft_box, 0, 1) 

        sink_box = FormGroupBox("Sinks:", self)
        sink_box.frame_layout.addRow(FixAndApp.SINKS.value)
        fix_and_app_lay.addWidget(sink_box, 1, 0)
        ro_box = FormGroupBox("RO:", self)
        ro_box.frame_layout.addRow(FixAndApp.RO.value)
        fix_and_app_lay.addWidget(ro_box, 1, 1) 

        shower_box = FormGroupBox("Showers:", self)
        shower_box.frame_layout.addRow(FixAndApp.SHOWERS.value)
        fix_and_app_lay.addWidget(shower_box, 2, 0)
        tub_box = FormGroupBox("Tubs:", self)
        tub_box.frame_layout.addRow(FixAndApp.TUBS.value)
        fix_and_app_lay.addWidget(tub_box, 2, 1)

        fix_and_app_lay.addWidget(QLabel(""), 3, 0)

        spa_box = FormGroupBox("Spa:", self)
        spa_box.frame_layout.addRow(FixAndApp.SPA.value)
        fix_and_app_lay.addWidget(spa_box, 4, 0) 
        pool_box = FormGroupBox("Pools", self)
        pool_box.frame_layout.addRow(FixAndApp.POOL.value)
        fix_and_app_lay.addWidget(pool_box, 4, 1) 
        fix_and_app_lay.addWidget(FixAndApp.AUTO_REFILL.value, 4, 2)
        fix_and_app_lay.addWidget(HorizontalFiller(self), 4, 3)
        
        dish_box = FormGroupBox("Dishwashers:", self)
        dish_box.frame_layout.addRow(FixAndApp.DISHWASHERS.value)
        fix_and_app_lay.addWidget(dish_box, 5, 0)
        clothes_box = FormGroupBox("Clothes Washer", self)
        clothes_box.frame_layout.addRow(FixAndApp.CLOTHES_WASHERS.value)
        fix_and_app_lay.addWidget(clothes_box, 5, 1)
      
        spray_box = FormGroupBox("Spray Stations:", self)
        spray_box.frame_layout.addRow(FixAndApp.SPRAY_STATIONS.value)
        fix_and_app_lay.addWidget(spray_box, 6, 0)
        drip_box = FormGroupBox("Drip Stations", self)
        drip_box.frame_layout.addRow(FixAndApp.DRIP_STATIONS.value)
        fix_and_app_lay.addWidget(drip_box, 6, 1)

        tank_box = FormGroupBox("Tank Water Heater:", self)
        tank_box.frame_layout.addRow(FixAndApp.WATER_HEATERS.value)
        fix_and_app_lay.addWidget(tank_box, 7, 0)
        tankless_box = FormGroupBox("Tankless Water Header", self)
        tankless_box.frame_layout.addRow(FixAndApp.TANKLESS_HEATERS.value)
        fix_and_app_lay.addWidget(tankless_box)
        
        fix_and_app_lay.addWidget(QLabel(""), 15, 0)

        form_box.frame_layout.addRow(fix_and_app)

        last_chk_boxes = QWidget(self)
        last_chk_boxes_lay = QHBoxLayout(last_chk_boxes)
        last_chk_boxes_lay.addWidget(FixAndApp.SMART_CONTROLLER.value)
        last_chk_boxes_lay.addWidget(FixAndApp.SMART_MODE_ACT.value)
        last_chk_boxes_lay.addWidget(FixAndApp.FIRE_SPRINKLER.value)
        last_chk_boxes_lay.addWidget(HorizontalFiller(self))
        form_box.frame_layout.addRow(last_chk_boxes)
      
        form_box.frame_layout.addRow("Other Water Use:", FixAndApp.OTHER.value)
        self._scroll_layout.addRow(form_box)

        