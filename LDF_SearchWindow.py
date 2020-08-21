from PySide2.QtWidgets import (QMainWindow, QMessageBox, QTextEdit, QTabWidget, QVBoxLayout, QGridLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QTableWidgetItem, QFileDialog)
from PySide2.QtGui import QSyntaxHighlighter, QTextCharFormat, QBrush, QFont, QColor
from PySide2.QtCore import Qt, QRegExp
from LDF_Widgets import (FormGroupBox, FormCombo, ExtendedComboBox, FormEntry, DataTable, BreakLine, HorizontalFiller, FormTextBox)
from LDF_Types import Types
from LDF_DatabaseTables import Tables, getFieldNames, getAllFieldNames, ExclusiveDbTables
import csv
import sqlite3
import re

DB_LOC = "LeakDetectionDatabase.db"

class SQLCommandBox(QTextEdit):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAcceptRichText(False)
        self.setStyleSheet("""
            QTextEdit 
            {
                font: 12pt;
                color: #EFEFEF;
                background-color: #232323;
                border: 1 solid #777777;
            }
        """)

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(Highlighter, self).__init__(parent)

        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("#00CCFF"))
        keywordFormat.setFontCapitalization(QFont.AllUppercase)

        keywordPatterns = ["\\bSELECT\\b", "\\bFROM\\b", "\\bWHERE\\b",
                "\\bselect\\b", "\\bfrom\\b", "\\bwhere\\b", 
                "\\bTABLE\\b", "\\btable\\b", "\\bON\\b", "\\bon\\b",
                "\\bORDER\\b", "\\border\\b", "\\bBY\\b", "\\bby\\b",
                "\\bLIMIT\\b", "\\blimit\\b", "\\bBETWEEN\\b",
                "\\bbetween\\b", "\\bLIKE\\b", "\\blike\\b", "\\bTO\\b", "\\bto\\b",
                "\\bINNER\\b", "\\inner\\b", "\\bJOIN\\b", "\\bjoin\\b", 
                "\\bAND\\b", "\\and\\b", "\\bOR\\b", "\\bor\\b", 
                ]

        self.highlightingRules = [(QRegExp(pattern), keywordFormat)
                for pattern in keywordPatterns]
        
        keyword2Format = QTextCharFormat()
        keyword2Format.setForeground(QColor("#DE0000"))
        keyword2Format.setFontCapitalization(QFont.AllUppercase)

        keyword2Patterns = ["\\bCREATE\\b", "\\bcreate\\b",
                 "\\bINSERT\\b", "\\binsert\\b", "\\bUPDATE\\b", "\\bupdate\\b",
                "\\bDELETE\\b","\\bdelete\\b", "\\bREPLACE\\b", "\\breplace\\b",
                "\\bDROP\\b", "\\bdrop\\b", "\\bRENAME\\b", "\\rename\\b",
                "\\bALTER\\b", "\\alter\\b",
                "\\bSET\\b", "\\bset\\b"
                ]


        self.highlightingRules.extend([(QRegExp(pattern), keyword2Format)
                for pattern in keyword2Patterns])
        
        table_name_format = QTextCharFormat()
        table_name_format.setForeground(QColor("#00FF7F"))
        table_name_format.setFontWeight(QFont.Bold)
        table_name_patterns = ["\\b{tn}\\b".format(tn=table.name) for table in Tables]
        ex_tables = ["\\b{tn}\\b".format(tn=table.name) for table in ExclusiveDbTables]
        table_name_patterns.extend(ex_tables)
        self.highlightingRules.extend([(QRegExp(pattern), table_name_format) for pattern in table_name_patterns])

        field_name_format = QTextCharFormat()
        field_name_format.setForeground(QColor("#00FF7F"))
        field_names = []
        for table in Tables:
            field_names.extend(getFieldNames(table.name))
        for table in ExclusiveDbTables:
            field_names.extend(getAllFieldNames(table.name, False))
        field_name_patterns = ["\\b{fn}\\b".format(fn=field_name) for field_name in field_names]
        self.highlightingRules.extend([(QRegExp(pattern), field_name_format) for pattern in field_name_patterns])


    def highlightBlock(self, text):
        for pattern, format_v in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format_v)
                index = expression.indexIn(text, index + length)

class SearchWindow(QMainWindow):
    def __init__(self, tables, database, parent=None):
        super().__init__(parent)
        try:
            self._tables = tables
            self._database = database
            self.setWindowTitle("Search for Records")
            self._main_widget = QWidget(self)
            self._bas_search_tab = QWidget(self)
            self._bas_search_lay = QVBoxLayout(self._bas_search_tab)
            self._adv_search_tab = QWidget(self)
            self._adv_search_lay = QVBoxLayout(self._adv_search_tab)
            self._search_tabs = QTabWidget(self)
            self._search_tabs.addTab(self._bas_search_tab, "Search")
            self._search_tabs.addTab(self._adv_search_tab, "Advance Search")

            layout = QVBoxLayout(self._main_widget)
            layout.setContentsMargins(0,0,0,0)
            layout.addWidget(self._search_tabs)

            # ----------------------------------------------------------------------------------------
            # ADVANCE  SEARCH
            
            sql_form_box = FormGroupBox("Enter SQL Command:")
            self._sql_cmd_box = SQLCommandBox()
            self._highlighter = Highlighter(self._sql_cmd_box.document())
            self._field_names = {}
            self._field_names = {table.name:getFieldNames(table.name) for table in Tables}
            for table in ExclusiveDbTables:
                self._field_names[table.name] = table.fields
            self._adv_search_button = QPushButton("Run SQL")
            self._adv_search_button.clicked.connect(self.sqlSearch)
            search_button_row = QWidget(self)
            search_button_lay = QHBoxLayout(search_button_row)
            search_button_lay.setContentsMargins(0,0,0,0)
            search_button_lay.addWidget(HorizontalFiller())
            search_button_lay.addWidget(self._adv_search_button)

            sql_results_box = FormGroupBox("Results:")
            self._adv_table_label = QLabel("Number of Results:")
            self._adv_results_table = DataTable(use_max_height=False, stretch=False)
            self._export_results_button = QPushButton("Export Table (CSV)")
            self._export_results_button.clicked.connect(self.exportTable)
            self._export_results_button.setDisabled(True)
            res_row = QWidget(self)
            res_lay = QHBoxLayout(res_row)
            res_lay.setContentsMargins(0,0,0,0)
            res_lay.addWidget(HorizontalFiller())
            res_lay.addWidget(self._export_results_button)

            sql_form_box.frame_layout.addRow(self._sql_cmd_box)
            sql_form_box.frame_layout.addRow(search_button_row)
            self._adv_search_lay.addWidget(sql_form_box)
            sql_results_box.frame_layout.addRow(self._adv_table_label)
            sql_results_box.frame_layout.addRow(self._adv_results_table)
            sql_results_box.frame_layout.addRow(res_row)
            self._adv_search_lay.addWidget(sql_results_box)
  
            # ----------------------------------------------------------------------------------------
            # BASIC  SEARCH

            form_box = FormGroupBox("Search for Record by Value", self)
            results_box = FormGroupBox("Results", self)

            self._table_combo = FormCombo(self)
            table_names = [table.name for table in self._tables]
            table_names.extend([table.name for table in ExclusiveDbTables])
            self._table_combo.addItems(table_names)
            self._field_combo = FormCombo(self)
            self._condition_combo = FormCombo(self)
            self._condition_combo.setMinimumWidth(150)
            self._value_entry = ExtendedComboBox(self)
            self._value_entry.setMinimumWidth(250)
            self._range_entry = FormEntry(self)
            self._range_entry.setMinimumWidth(250)
            self._table_label = QLabel("Number of Results:")
            self._result_table = DataTable(use_max_height=False, stretch=False, parent=self)
            self._search_button = QPushButton(" Search ")
            self._search_button.clicked.connect(self.searchForData)
            self._export_button = QPushButton("Export CSV")
            self._export_button.clicked.connect(self.exportCSV)
            self._export_button.setEnabled(False)
            self._value_type = None 

            form_box.frame_layout.addRow("Table:", self._table_combo)
            condition_row = QWidget(self)
            condition_lay = QGridLayout(condition_row)
            condition_lay.addWidget(QLabel("Field:"), 0,0)
            condition_lay.addWidget(QLabel("Condition:"), 0,1)
            condition_lay.addWidget(QLabel("Value:"), 0,2)
            condition_lay.addWidget(QLabel("Value 2 (Range Between Value 1 and Value 2):"), 0, 3)
            condition_lay.addWidget(self._field_combo, 1,0)
            condition_lay.addWidget(self._condition_combo, 1,1)
            condition_lay.addWidget(self._value_entry, 1,2)
            condition_lay.addWidget(self._range_entry, 1,3)
            form_box.frame_layout.addRow(condition_row)
            search_row = QWidget(self)
            search_lay = QHBoxLayout(search_row)
            search_lay.addWidget(HorizontalFiller(self))
            search_lay.addWidget(self._search_button)
            form_box.frame_layout.addRow(search_row)
            search_lay.setContentsMargins(0,0,0,0)
            form_box.frame_layout.setContentsMargins(0,0,0,0)
            results_box.frame_layout.setContentsMargins(0,0,0,0)
            results_box.frame_layout.addRow(self._table_label)
            results_box.frame_layout.addRow(self._result_table)
            export_row = QWidget(self)
            export_lay = QHBoxLayout(export_row)
            export_lay.addWidget(HorizontalFiller(self))
            export_lay.addWidget(self._export_button)
            results_box.frame_layout.addRow(export_row)
            export_lay.setContentsMargins(0,0,0,0)

            self._current_table = None 
            self._setTableFieldsCombo()
            self._table_combo.currentTextChanged.connect(self._setTableFieldsCombo)
            self._setConditionsCombo()
            self._field_combo.currentTextChanged.connect(self._setConditionsCombo)
            self._conditionChange()
            self._condition_combo.currentTextChanged.connect(self._conditionChange)
            
            self._bas_search_lay.addWidget(form_box)
            self._bas_search_lay.addWidget(results_box)
            self.setCentralWidget(self._main_widget)
        except Exception as e:
            print("Window failed", e)
     
    def _setTableFieldsCombo(self):
        self._field_combo.clear()
        table_name = self._table_combo.getValue()
        if table_name in [table.name for table in Tables]:
            for table in self._tables:
                if table.name == table_name:
                    fields = table.fields 
                    if table_name != "CLIENT":
                        fields.pop(fields.index("AP_PHASE_ID"))
                    self._field_combo.addItems(fields)
                    self._current_table = table
                    self._setConditionsCombo()
                    return
        else: 
            for table in ExclusiveDbTables:
                if table_name == table.name:
                    fields = table.fields 
                    fields.pop(fields.index("AP_PHASE_ID"))
                    self._field_combo.addItems(fields)
                    self._current_table = table
                    self._setConditionsCombo()
                    return 

    
    def _setConditionsCombo(self):
        table_name = self._table_combo.getValue()
        field_name = self._field_combo.getValue()
        number_conds = ["=", ">", "<", ">=", "<=", "Range"]
        bool_conds = ["True", "False"]
        str_conds = ["="]
        self._value_entry.clear()
        self._range_entry.clear()
        self._condition_combo.clear()
        field_name = self._field_combo.getValue()
        for field in self._current_table.table_fields:
            if field.name == field_name:
                if field.data_type == Types.TEXT:
                    self._condition_combo.addItems(str_conds)
                    self._value_entry.clear()
                    self._database.openDatabase()
                    items = list(set(self._database.getValuesFromField(table_name, field_name)))
                    self._database.closeDatabase() 
                    self._value_entry.addItems(items)
                    self._value_entry.setCurrentText("")
                    self._value_entry.setEnabled(True)
                    self._value_type = Types.TEXT
                    
                elif field.data_type == Types.BOOLEAN:
                    self._condition_combo.addItems(bool_conds)
                    self._value_entry.clear()
                    self._value_entry.setEnabled(False)
                    self._value_type = Types.BOOLEAN
                else:
                    self._condition_combo.addItems(number_conds)
                    self._value_entry.clear()
                    self._value_entry.setEnabled(True)
                    self._value_type = Types.NUMBER
                return
    
    def _conditionChange(self):
        if self._condition_combo.getValue() == "Range":
            self._range_entry.setEnabled(True)
        else:
            self._range_entry.setEnabled(False)
        self._range_entry.clear()
    
    def getBoolValue(self, bool_string):
        if bool_string == "False": 
            return 0
        return 1 
    
    def getBoolString(self, bool_value):
        return str(bool(bool_value))

    def updateTable(self, data, field_name, is_bool):
        headers = ["AP_PHASE_ID", "ADDRESS"]
        if field_name != "ADDRESS" and field_name != "AP_PHASE_ID":
            headers.append(field_name)
        data_count = len(data)
        self._table_label.setText("Number of Results: "+str(data_count))
        self._result_table.setRowCount(0)
        self._result_table.setColumnCount(len(headers))
        self._result_table.setRowCount(data_count)
        self._export_button.setEnabled((self._result_table.rowCount() >= 1))

        for col, header_text in enumerate(headers):
            header = QTableWidgetItem(header_text)
            self._result_table.setHorizontalHeaderItem(col, header)
        
        for row, (ap_phase_id, field_row) in enumerate(data.items()):
            item = QTableWidgetItem(ap_phase_id)
            self._result_table.setItem(row, 0, item)
            for col, field in enumerate(field_row):
                if is_bool and field != "ADDRESS":
                    item = QTableWidgetItem(self.getBoolString(field_row[field]))
                else:
                    item = QTableWidgetItem(str(field_row[field]))
                self._result_table.setItem(row, col+1, item)
        self._result_table.horizontalHeader().setStretchLastSection(True)

    def searchForData(self):
        table_name = self._table_combo.getValue()
        field_name = self._field_combo.getValue()
        condition = self._condition_combo.getValue()
        value_1 = self._value_entry.getValue()
        value_2 = self._range_entry.getValue()
        is_bool = False 
        if condition == "True" or condition == "False":
            value_1 = self.getBoolValue(condition)
            is_bool = True
            condition = '=' 

        self._database.openDatabase()
        
        if condition == "Range":
            data = {ap_phase_id[0]:{"ADDRESS": "", field_name: ""} for ap_phase_id in self._database.getApPhaseIDFromRange(table_name, field_name, float(value_1), float(value_2))} 
        else:
            if self._value_type == Types.TEXT:
                data = {ap_phase_id[0]:{"ADDRESS": "", field_name: ""} for ap_phase_id in self._database.getApPhaseIDFromValue(table_name, field_name, value_1, condition)}
            elif self._value_type == Types.INTEGER:
                data = {ap_phase_id[0]:{"ADDRESS": "", field_name: ""} for ap_phase_id in self._database.getApPhaseIDFromValue(table_name, field_name, int(value_1), condition)}
            else:
                data = {ap_phase_id[0]:{"ADDRESS": "", field_name: ""} for ap_phase_id in self._database.getApPhaseIDFromValue(table_name, field_name, float(value_1), condition)}

        for ap_phase_id in data:
            data[ap_phase_id]["ADDRESS"] = self._database.readValueFromApPhaseID("CLIENT", ap_phase_id, "ADDRESS")
            if field_name != "ADDRESS" and field_name != "AP_PHASE_ID":
                data[ap_phase_id][field_name] = self._database.readValueFromApPhaseID(table_name, ap_phase_id, field_name)
        
        self._database.closeDatabase()
        self.updateTable(data, field_name, is_bool)

    def exportCSV(self):
        file_name = self.exportCSVDialog()
        temp_row = []
        headers = []
        for col in range(self._result_table.columnCount()):
            headers.append(self._result_table.horizontalHeaderItem(col).text())
        
        if file_name:
            with open(file_name, 'w', newline='') as n_f:
                writer = csv.writer(n_f)
                writer.writerow(headers)

                for row in range(self._result_table.rowCount()):
                    for col in range(self._result_table.columnCount()):
                        temp_row.append(self._result_table.item(row, col).text())

                    writer.writerow(temp_row)
                    temp_row.clear()
                
    def exportCSVDialog(self):
        file_dialog = QFileDialog()
        file_name, ext = file_dialog.getSaveFileName(self, 'Export CSV File', "", "CSV (*.csv)")
        return file_name 
    
    # ADVANCE METHODS 
    # ----------------------------------------------------------------------------------------
    def sqlSearch(self):
        values = []
        try:
            connection = sqlite3.connect(DB_LOC)
            cursor = connection.cursor()
            sql = self._sql_cmd_box.toPlainText()
            cursor.execute(sql)
 
            values = cursor.fetchall()
            if values:
                self.updateAdvTable(values, sql)
            else:
                connection.commit()
        except Exception as error:
            error_text = "\n(!) Search Error - {e}\n\n".format(e=error)
            self.searchErrorMsgBox(error_text)
        finally:
            connection.close()
    
    def clearFeedBack(self):
        self._feedback_box.clear()
    
    def updateAdvTable(self, data, sql):
        data_count = len(data)
        field_names_ordered = []

        self._adv_table_label.setText("Number of Results: "+str(data_count))
        self._adv_results_table.setRowCount(0)
        if data_count:
            table_names = list(self._field_names.keys())
            table_names = [table_name for table_name in table_names if re.search(r'\b{tn}\b'.format(tn = table_name), sql)]
            all_field_names = {}
            for table_name in table_names:
                for field_name in self._field_names[table_name]:
                    all_field_names[field_name] = ''
            if len(all_field_names):
                field_names_unordered = list(all_field_names.keys())
                field_names_unordered = [field_name for field_name in all_field_names if re.search(r'\b{fn}\b'.format(fn = field_name), sql)]
                field_names_ordered = sorted(field_names_unordered, key=sql.find) 
            if not len(field_names_ordered):
                for table_name in table_names:
                    field_names_ordered.extend(getAllFieldNames(table_name))

            self._adv_results_table.setColumnCount(len(field_names_ordered))
            self._adv_results_table.setRowCount(data_count)
            for col, field_name in enumerate(field_names_ordered):
                header = QTableWidgetItem(field_name)
                self._adv_results_table.setHorizontalHeaderItem(col, header)
            
            for row, data_row in enumerate(data):
                for col, data_value in enumerate(data_row):
                    item = QTableWidgetItem(str(data_value))
                    self._adv_results_table.setItem(row, col, item)
            self._export_results_button.setDisabled(False)
        else:
            self._export_results_button.setDisabled(True)

    def exportTable(self):
        file_name = self.exportCSVDialog()
        temp_row = []
        headers = []
        
        for col in range(self._adv_results_table.columnCount()):
            headers.append(self._adv_results_table.horizontalHeaderItem(col).text())        
        if file_name:
            with open(file_name, 'w', newline='') as n_f:
                writer = csv.writer(n_f)
                writer.writerow(headers)

                for row in range(self._adv_results_table.rowCount()):
                    for col in range(self._adv_results_table.columnCount()):
                        temp_row.append(self._adv_results_table.item(row, col).text())

                    writer.writerow(temp_row)
                    temp_row.clear()
    
    def searchErrorMsgBox(self, error_text):
        msg = QMessageBox(self)
        msg.setWindowTitle("SQL Entry Error")
        msg.setText(error_text)
        msg.setIcon(msg.Warning)
        msg.setStandardButtons(msg.Ok)
        msg.exec_()