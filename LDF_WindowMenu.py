from PySide2.QtWidgets import (QAction, QMessageBox, QFileDialog)
from LDF_DatabaseTables import Tables
from LDF_UtilityScripts import getAddresses
from LDF_Widgets import NewRecordDialog
from LDF_SearchWindow import SearchWindow
import pandas as pd
import csv 

class WindowMenu:
    def __init__(self):
        # Window Menu
        self._main_menu = self.menuBar()
        self._search_window = None  
        
        # FILE -----------------------------------------
        self._file_menu = self._main_menu.addMenu("File")

        # Export Data 
        self._export_data_command = QAction("Export Data", self)
        self._export_data_command.triggered.connect(self.exportDataFileDialog)
        self._file_menu.addAction(self._export_data_command) 

        # Exit
        self._file_menu.addSeparator()
        self._exit_command = QAction("Exit", self)
        self._exit_command.triggered.connect(self.close)
        self._file_menu.addAction(self._exit_command)

        # EDIT -----------------------------------------
        self._edit_menu = self._main_menu.addMenu("Edit")

        # Remove Current Record
        self._rmv_rec_command = QAction("Remove Current Record")
        self._rmv_rec_command.triggered.connect(self.removeRecordWarning)
        self._edit_menu.addAction(self._rmv_rec_command)

        # VIEW -----------------------------------------
        self._view_menu = self._main_menu.addMenu("View")

        self._view_menu.addAction(self._plot_menu_dock.toggleViewAction())

        # Search -----------------------------------------
        self._search_menu = self._main_menu.addMenu("Search")

        # Search Window  
        self._search_command = QAction("Search Records", self)
        self._search_command.triggered.connect(self.showSearchWindow)
        self._search_menu.addAction(self._search_command)

    def showSearchWindow(self):
        if self._search_window == None: 
            self._search_window = SearchWindow(Tables, self._database)
        if self._search_window != None and not self._search_window.isVisible():
            self._search_window.show()
        elif self._search_window != None and self._search_window.isVisible():
            self._search_window.raise_()
    
    def exportChartFileDialog(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilters(["*. xlsx"])
        file_name, ext = file_dialog.getSaveFileName(self, 'Export File', "", "Excel (*.xlsx)")
        
        if file_name and ext == "Excel (*.xlsx)":
            return file_name 
        return ""
    
    def exportData(self, file_name, csv_file=False):
        try:
            fields = []
            if csv_file:
                file = open(file_name, 'a', newline='')
                writer = csv.writer(file)
            else:
                writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
            for table in Tables:
                fields.clear()
                fields = ["ID"]
                fields.extend(table.value.getFields())
                self._database.openDatabase()
                data = self._database.readTable(table.name)
                self._database.closeDatabase()
                df = pd.DataFrame(data, columns=fields)
                
                if csv_file: 
                    writer.writerow([""])
                    writer.writerow([table.name])
                    df.to_csv(file_name, mode='w')
                else:
                    df.to_excel(writer, sheet_name=table.name)
            
            if csv_file: 
                file.close()
            else:
                writer.save()
                writer.close()
        except Exception as e:
            if csv_file:
                file.close()
            else:
                writer.close()
            print(str(e))
        
    def exportDataFileDialog(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilters(["*. xlsx"])
        file_name, ext = file_dialog.getSaveFileName(self, 'Export File', "", "Excel (*.xlsx);; CSV (*.csv)")
        
        if file_name and ext == "Excel (*.xlsx)":
            self.exportData(file_name)
        # CSV
        elif file_name:
            self.exportData(file_name, csv_file=True)         
    
    def createNewRecord(self):
        new_record_dialog = NewRecordDialog(self)
        self._new = True
        self.clearForm()
        self._ap_phase_widget.setPlaceholderText("Enter new ApPhase ID...")
        self._address_widget.setPlaceholderText("Enter new Address...")
        new_record_dialog.exec_()
        if not new_record_dialog.isCanceled():
            self._ap_phase_widget.setText(new_record_dialog.getApPhaseID())
            self._address_widget.setText(new_record_dialog.getAddress())
            self.checkApPhaseIDsInDatabase()
         
    def removeRecordWarning(self):
        ap_phase_id = self._ap_phase_widget.text()
        msg = QMessageBox(self)
        msg.setWindowTitle("Remove '"+ap_phase_id+"' Record?")
        msg.setText("Are you sure you want to remove this record?")
        msg.setIcon(msg.Warning)
        msg.setStandardButtons(msg.Yes | msg.No)
        msg_val = msg.exec_()
        if msg_val == msg.Yes:
            self.removeRecord(ap_phase_id)

    def removeRecord(self, ap_phase_id):
        try:
            index = self._tabs.currentIndex()
            for table_name in Tables:
                self._database.openDatabase()
                self._database.removeRowWithApPhaseID(table_name.name, ap_phase_id)
                self._database.closeDatabase()
            self.clearForm()
            self.resetForm()
        except Exception as e:
            print(str(e))
     
    def checkApPhaseIDsInDatabase(self):
        if self._new:
            ap_phase_id = self._ap_phase_widget.text()
            address = self._address_widget.text()
            if len(ap_phase_id) == 6 and len(address) > 0:
                self._database.openDatabase()
                ap_phase_ids = self._database.getValuesFromField(Tables.CLIENT.name, "AP_PHASE_ID")
                
                if ap_phase_id not in ap_phase_ids:
                    self._search_apPhase_combo.setCurrentText(ap_phase_id)
                    self._search_address_combo.setCurrentText(address)
                    #self._database.insertRow(Tables.CLIENT.name, Tables.CLIENT.value.getFields(), Tables.CLIENT.value.getValues())
                    self._newTables()
                    self.updateSearchCombos()
                    self._new = False
                    Tables.CLIENT.value._new = False
                self._database.closeDatabase()
    
    def _newTables(self):
        for table in Tables:
            self._database.insertRow(table.name, table.value.getFields(), table.value.getValues())
       
    def clearForm(self):
        for table in Tables:
            table.value.clearValues()

    def resetForm(self):
        self._database.openDatabase()
        search_data = getAddresses(self._database.getValuesFrom2Fields(Tables.CLIENT.name, "ADDRESS", "AP_PHASE_ID"))
        self._database.closeDatabase()
        search_ap_phase_ids = [value[1] for value in search_data]
        search_addresses = [value[0] for value in search_data]
        self._search_apPhase_combo.clear()
        self._search_address_combo.clear()
        self._search_apPhase_combo.addItems(search_ap_phase_ids)
        self._search_address_combo.addItems(search_addresses)

