import sys
from PySide2.QtWidgets import (QApplication, QGridLayout, QSizePolicy, QToolBar, QDockWidget, QAbstractScrollArea, QTableWidgetItem, QHeaderView, QHBoxLayout, QStackedWidget, QMainWindow, QVBoxLayout, QWidget, QLabel, QScrollArea, QScroller, QComboBox, QLineEdit, QMessageBox, QTabWidget, QAction, QFileDialog, QPushButton, QFormLayout, QTabWidget)
from PySide2.QtGui import (QIcon, QKeySequence, QPixmap)
from PySide2.QtCore import Qt, QRect
import csv 
from LDF_AppSettings import app


from LDF_Widgets import (ExtendedComboBox, FormMenu, HorizontalFiller, DataTable, BreakLine)
from LDF_Plots import Plots
from LDF_UtilityScripts import getAddresses
from SQLiteLibrary import SQLiteLib, SQLTypes
from LDF_DatabaseTables import Tables, getFieldNames
from LDF_Client import Client
from LDF_WindowMenu import WindowMenu



class Window(QMainWindow, WindowMenu, Plots):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowTitle("Leak Detection Evaluation Form")
        self.main_style_qss = "Eclippy.qss"
        self._main_widget = QWidget(self)
        self._main_layout = QVBoxLayout(self._main_widget)
        self._form_widget = QWidget(self)
        self._form_layout = QVBoxLayout(self._form_widget)
        self._database_widget = QWidget(self)
        self._database_layout = QVBoxLayout(self._database_widget)
        self._database_table_label = QLabel()
        self._database_table_label.setObjectName("dbtablelabel")
        self._database_table_label.setStyleSheet('QLabel[objectName^="dbtablelabel"] {font-size: 12pt; font-weight: bold;}')
        self._database_table_export_button = QPushButton("Export Table (CSV)")
        self._database_table_export_button.clicked.connect(self.exportDatabaseTable)
        database_table_export_row = QWidget()
        database_table_export_lay = QHBoxLayout(database_table_export_row)
        database_table_export_lay.setContentsMargins(0,0,0,0)
        database_table_export_lay.addWidget(HorizontalFiller())
        database_table_export_lay.addWidget(self._database_table_export_button)

        self._database_layout.addWidget(self._database_table_label)
        self._database_table = DataTable(use_max_height=False)
        self._database_layout.addWidget(self._database_table)
        self._database_layout.addWidget(database_table_export_row)
        self._main_tabs = QTabWidget(self)
        self._main_layout.addWidget(self._main_tabs)
        self._main_tabs.addTab(self._form_widget, "Form")
        self._main_tabs.addTab(self._database_widget, "Database")

        snwa_logo = QPixmap("snwa_logo.png")
        self._logo = QLabel(self)
        self._logo.setPixmap(snwa_logo)
        search_row = QWidget(self)
        search_lay = QHBoxLayout(search_row)
        search_lay.addWidget(self._logo)

        self._search_toolbar = QToolBar(self)
        self._new_rec_button = QPushButton("Create New Record")
        self._new_rec_button.clicked.connect(self.createNewRecord)
        self._new_rec_button.setIcon(QIcon(QPixmap("plus.png")))

        self._search_toolbar.addWidget(self._new_rec_button)
        
        # Database 
        DB_LOC = "LeakDetectionDatabase.db"
        self._database = SQLiteLib(DB_LOC)

        self.setTabs()
        Plots.__init__(self)

        self._data_table_label = QLabel("Client Table")
        self._data_table = DataTable(1, 1, self)

        search_bars = self.setSearchBars()
        search_bars.setContentsMargins(0,0,0,0)
        search_lay.setContentsMargins(0,0,0,0)
        search_lay.addWidget(search_bars)
        search_lay.addWidget(HorizontalFiller(self))
        self.readDataFromDatabase()

        self._ap_phase_widget = Client.AP_PHASE_ID.value
        self._address_widget = Client.ADDRESS.value
        self._main_tabs.currentChanged.connect(self.mainTabChange)
        self._ap_phase_widget.returnPressed.connect(self.checkApPhaseIDsInDatabase) 
        
        # Layout -----------------------------------
        
        # Docks 
        self._form_menu_dock = QDockWidget("Form Selections", self)
        self._form_menu_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self._form_menu_dock.setFeatures(self._form_menu_dock.features() & ~QDockWidget.DockWidgetClosable)
        self._form_menu_dock.setWidget(self._form_menu)
        self.addDockWidget(Qt.LeftDockWidgetArea, self._form_menu_dock)

        
        self._plot_menu_dock = QDockWidget("Plotted Data (Double Click to Activate Chart)", self)
        self._plot_menu_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self._plot_menu_dock.setWidget(self._plot_menu)
        self.addDockWidget(Qt.RightDockWidgetArea, self._plot_menu_dock)

        WindowMenu.__init__(self)

        # Tabs
        form_area = QWidget(self)
        form_lay = QVBoxLayout(form_area)
        form_lay.addWidget(search_row)
        form_lay.addWidget(self._search_toolbar)
        form_lay.addWidget(BreakLine(self))
        form_lay.addWidget(self._tab_label)
        form_lay.addWidget(self._tabs)
        form_lay.addWidget(self._data_table_label)
        form_lay.addWidget(self._data_table)
        form_lay.setContentsMargins(0,0,0,0)

        self._form_layout.addWidget(form_area)
        self.updateDataTable()
               
        self.setCentralWidget(self._main_widget)
    
    def closeEvent(self, event):
        for plot_name in self._plots:
            if self._plots[plot_name].isVisible():
                self._plots[plot_name].close()
        if self._search_window != None and self._search_window.isVisible():
            self._search_window.close()

    def setSearchBars(self):
        self._database.openDatabase()

        self._search_apPhase_combo = ExtendedComboBox(self)
        self._search_address_combo = ExtendedComboBox(self)
        search_data = getAddresses(self._database.getValuesFrom2Fields(Tables.CLIENT.name, Client.ADDRESS.name, Client.AP_PHASE_ID.name))
        self._search_ap_phase_ids = [value[1] for value in search_data]
        search_addresses = [value[0] for value in search_data]
        self._search_apPhase_combo.addItems(self._search_ap_phase_ids)
        self._search_address_combo.addItems(search_addresses)
        self._search_apPhase_combo.currentIndexChanged.connect(self.apPhaseComboChange)
        self._search_apPhase_combo.currentTextChanged.connect(self.newSearchApCombo)
        self._search_address_combo.currentIndexChanged.connect(self.addressComboChange)
        self._search_address_combo.currentTextChanged.connect(self.newSearchAdrCombo)
        self._new = False 
        self._ap_phase_change = False 
        self._address_change = False 
        
        self._database.closeDatabase()

        bot_menu = QWidget(self)
        bot_menu_layout = QFormLayout(bot_menu)
        bot_menu.setStyleSheet("QLabel { font-weight: bold; }")
        bot_menu_layout.addRow("Search ApPhase ID:", self._search_apPhase_combo) 
        bot_menu_layout.addRow("Search Address:", self._search_address_combo)
        return bot_menu

    def setTabs(self):
        #self._tabs = QTabWidget(self)
        self._tab_label = QLabel("Client", self)
        self._tab_label.setObjectName("tablabel")
        self._tab_label.setStyleSheet('QLabel[objectName^="tablabel"] {font-size: 12pt; font-weight: bold;}')
        self._tabs = QStackedWidget(self)
        table_names = []
        for table in Tables:
            table_name = table.value.getTabName()
            table_names.append(table_name)
            table.value.setTab(self, self._database)
            table.value.setFormParent(self) 

            #self._tabs.addTab(table.value, table_name)
            self._tabs.addWidget(table.value)
        self._form_menu = FormMenu(item_names=table_names, parent=self)
        self._form_menu.currentRowChanged.connect(self.selectMenuItemChange)
    
    def selectMenuItemChange(self, index):
        self._tabs.setCurrentIndex(index)
        text = self._form_menu.currentItem().text()
        self._tab_label.setText(text)
        self._data_table_label.setText(text+" Table")
        self.updateDataTable()
        self.updateDatabaseTable()
         
    def updateDataTable(self):
        self._data_table.setRowCount(0)
        self._data_table.setRowCount(1)
        data = self._tabs.currentWidget()
        
        fields = data.getFields()
        values = data.getValues()
        col_count = len(values)
        self._data_table.setColumnCount(col_count)
        for col, (field, value) in enumerate(zip(fields, values)):
            header = QTableWidgetItem(field)
            item = QTableWidgetItem(str(value))
            self._data_table.setHorizontalHeaderItem(col, header)
            self._data_table.setItem(0, col, item)

        #self._data_table.resizeColumnsToContents()
        self._data_table.verticalHeader().setStretchLastSection(True)

    def readDataFromDatabase(self):
        for table in Tables:
            table.value.readDataIntoForm(self._search_apPhase_combo.currentText())

    def setApPhaseChangeCheck(self, change):
        self._ap_phase_change = change
        for table in Tables:
            table.value._ap_phase_change = change

    def setAddressChangeCheck(self, change):
        self._address_change = change 
        for table in Tables:
            table.value._address_change = change
    
    def setNewForTables(self, new_val):
        self._new = new_val
        for table in Tables:
            table.value._new = new_val
       
    def apPhaseComboChange(self):
        if not self._address_change:
            self.setApPhaseChangeCheck(True)
            self.clearForm()
            self.readDataFromDatabase()
            self._search_address_combo.setCurrentIndex(self._search_apPhase_combo.currentIndex())
            self.updateDataTable()
            self.setNewForTables(False) 
            self.setApPhaseChangeCheck(False) 
    
    def addressComboChange(self):
        if not self._ap_phase_change:
            self.setAddressChangeCheck(True)
            self.clearForm()
            self._search_apPhase_combo.setCurrentIndex(self._search_address_combo.currentIndex())
            self.readDataFromDatabase()
            self.updateDataTable()
            self.setNewForTables(False)
            self.setAddressChangeCheck(False) 
    
    def newSearchApCombo(self):
        if not self._address_change and self._search_apPhase_combo.currentText() == "":
            self._ap_phase_change = True
            Tables.CLIENT.value._ap_phase_change = True
            self._search_address_combo.setCurrentText("")
            self._ap_phase_widget.setPlaceholderText("Enter new ApPhase ID...")
            self._address_widget.setPlaceholderText("Enter new Address...")
            Tables.CLIENT.value.clearValues()
            self.setNewForTables(True)
            Tables.CLIENT.value._ap_phase_change = False   
            self._ap_phase_change = False 
    
    def newSearchAdrCombo(self):
        if not self._ap_phase_change and self._search_address_combo.currentText() == "":
            self._address_change = True
            self._search_apPhase_combo.setCurrentText("")
            self._ap_phase_widget.setPlaceholderText("Enter new ApPhase ID...")
            self._address_widget.setPlaceholderText("Enter new Address...")
            self.setNewForTables(True)
            Tables.CLIENT.value.clearValues()
            self._address_change = False 

    def updateSearchCombos(self):
        ap_phase_id = self._ap_phase_widget.text()
        search_data = getAddresses(self._database.getValuesFrom2Fields(Tables.CLIENT.name, Client.ADDRESS.name, Client.AP_PHASE_ID.name))
        search_ap_phase_ids = [value[1] for value in search_data]
        search_addresses = [value[0] for value in search_data]
        self._search_apPhase_combo.clear()
        self._search_address_combo.clear()
        self._search_apPhase_combo.addItems(search_ap_phase_ids)
        self._search_address_combo.addItems(search_addresses)
        index = self._search_apPhase_combo.findText(ap_phase_id)
        self._search_apPhase_combo.setCurrentIndex(index)

    def updateDatabaseTable(self):
        if self._main_tabs.currentIndex() == 1:
            table_name = self._tabs.currentWidget().getTableName()
            tab_name = self._tabs.currentWidget().getTabName()
            self._database_table_label.setText("Table: {tn} ({tbn})".format(tn = table_name, tbn = tab_name))
            self._database.openDatabase()
            data = self._database.readTable(table_name)
            self._database.closeDatabase()
            headers = getFieldNames(table_name)
            data_count = len(data)
            self._database_table.setRowCount(0)
            self._database_table.setColumnCount(len(headers))
            self._database_table.setRowCount(data_count)

            for col, header_text in enumerate(headers):
                header = QTableWidgetItem(header_text)
                self._database_table.setHorizontalHeaderItem(col, header)
            
            for row, data_row in enumerate(data):
                data_row = list(data_row)
                data_row.pop(0)
                for col, data_value in enumerate(data_row):
                    item = QTableWidgetItem(str(data_value))
                    self._database_table.setItem(row, col, item)
        
    def exportDatabaseTable(self):
        file_name = self.exportCSVDialog()
        temp_row = []
        headers = []
        for col in range(self._database_table.columnCount()):
            headers.append(self._database_table.horizontalHeaderItem(col).text())
        
        if file_name:
            with open(file_name, 'w', newline='') as n_f:
                writer = csv.writer(n_f)
                writer.writerow(headers)

                for row in range(self._database_table.rowCount()):
                    for col in range(self._database_table.columnCount()):
                        temp_row.append(self._database_table.item(row, col).text())

                    writer.writerow(temp_row)
                    temp_row.clear()
                
    def exportCSVDialog(self):
        file_dialog = QFileDialog()
        file_name, ext = file_dialog.getSaveFileName(self, 'Export CSV File', "", "CSV (*.csv)")
        return file_name 

    def mainTabChange(self, index):
        if index == 1:
            self.updateDatabaseTable()
    

    def start(self):
        with open(self.main_style_qss, 'r') as main_qss:
                main_style = main_qss.read()
                app.setStyleSheet(main_style)
        self.showMaximized()
        sys.exit(app.exec_())

        