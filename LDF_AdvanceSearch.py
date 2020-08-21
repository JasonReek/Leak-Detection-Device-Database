import sys

from PySide2.QtWidgets import (QApplication, QTableWidgetItem, QFileDialog, QLabel, QMainWindow, QTextEdit, QPushButton, QWidget, QHBoxLayout, QVBoxLayout)
from PySide2.QtGui import QSyntaxHighlighter, QTextCharFormat, QBrush, QFont, QColor
from PySide2.QtCore import Qt, QRegExp
from LDF_Widgets import DataTable, HorizontalFiller, BreakLine
import csv 
import sqlite3 
import re


DB_LOC = "LeakDetectionDatabase.db"
app = QApplication(sys.argv)
from LDF_DatabaseTables import Tables, getFieldNames
app.setStyle("Fusion")


class SQLCommandBox(QTextEdit):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(200)
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
        keyword2Format.setForeground(QColor("#BB0000"))
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
        self.highlightingRules.extend([(QRegExp(pattern), table_name_format) for pattern in table_name_patterns])

        field_name_format = QTextCharFormat()
        field_name_format.setForeground(QColor("#00FF7F"))
        field_names = []
        for table in Tables:
            field_names.extend(getFieldNames(table.name))
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

class AdvSearchWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._main_widget = QWidget(self)
        self._main_layout = QVBoxLayout(self._main_widget)
        self._sql_cmd_box = SQLCommandBox()
        self._highlighter = Highlighter(self._sql_cmd_box.document())
        self._field_names = {}
        self._field_names = {table.name:getFieldNames(table.name) for table in Tables}

        
        self._search_label = QLabel("Enter SQL Command:")
        self._search_button = QPushButton("Run SQL")
        self._search_button.clicked.connect(self.sqlSearch)
        search_button_row = QWidget(self)
        search_button_lay = QHBoxLayout(search_button_row)
        search_button_lay.addWidget(HorizontalFiller())
        search_button_lay.addWidget(self._search_button)

        self._results_table = DataTable(use_max_height=False)
        self._export_results_button = QPushButton("Export Table (CSV)")
        self._export_results_button.clicked.connect(self.exportTable)
        self._export_results_button.setDisabled(True)
        res_row = QWidget(self)
        res_lay = QHBoxLayout(res_row)
        res_lay.addWidget(HorizontalFiller())
        res_lay.addWidget(self._export_results_button)

        self._feedback_label = QLabel("Feedback:")
        self._feedback_box = QTextEdit()
        self._feedback_box.setReadOnly(True)
        self._clear_fb_button = QPushButton("Clear")
        self._clear_fb_button.clicked.connect(self.clearFeedBack)
        fb_row = QWidget(self)
        fb_lay = QHBoxLayout(fb_row)
        fb_lay.addWidget(HorizontalFiller())
        fb_lay.addWidget(self._clear_fb_button)


        # Layout
        self._main_layout.addWidget(self._search_label) 
        self._main_layout.addWidget(self._sql_cmd_box)
        self._main_layout.addWidget(search_button_row)
        self._main_layout.addWidget(self._results_table)
        self._main_layout.addWidget(res_row)
        self._main_layout.addWidget(BreakLine())
        self._main_layout.addWidget(self._feedback_label)
        self._main_layout.addWidget(self._feedback_box)
        self._main_layout.addWidget(fb_row)

        self.setCentralWidget(self._main_widget)

    def sqlSearch(self):
        values = []
        try:
            connection = sqlite3.connect(DB_LOC)
            cursor = connection.cursor()
            sql = self._sql_cmd_box.toPlainText()
            cursor.execute(sql)
 
            values = cursor.fetchall()
            if values:
                self.updateTable(values, sql)
            else:
                connection.commit()
        except Exception as error:
            error_text = "\n(!) Search Error - {e}\n\n".format(e=error)
            self._feedback_box.insertPlainText(error_text)
        finally:
            connection.close()
    
    def clearFeedBack(self):
        self._feedback_box.clear()
    
    def updateTable(self, data, sql):
        data_count = len(data)
        self._results_table.setRowCount(0)
        if data_count:
            table_names = list(self._field_names.keys())
            table_names = [table_name for table_name in table_names if re.search(r'\b{tn}\b'.format(tn = table_name), sql)]
            all_field_names = {}
            for table_name in table_names:
                for field_name in self._field_names[table_name]:
                    all_field_names[field_name] = ''
            field_names_unordered = list(all_field_names.keys())
            field_names_unordered = [field_name for field_name in all_field_names if re.search(r'\b{fn}\b'.format(fn = field_name), sql)]
            field_names_ordered = sorted(field_names_unordered, key=sql.find) 

            self._results_table.setColumnCount(len(field_names_ordered))
            self._results_table.setRowCount(data_count)
            for col, field_name in enumerate(field_names_ordered):
                header = QTableWidgetItem(field_name)
                self._results_table.setHorizontalHeaderItem(col, header)
            
            for row, data_row in enumerate(data):
                for col, data_value in enumerate(data_row):
                    item = QTableWidgetItem(str(data_value))
                    self._results_table.setItem(row, col, item)
            self._export_results_button.setDisabled(False)
        else:
            self._export_results_button.setDisabled(True)

    def exportTable(self):
        file_name = self.exportCSVDialog()
        temp_row = []
        headers = []
        
        for col in range(self._results_table.columnCount()):
            headers.append(self._results_table.horizontalHeaderItem(col).text())        
        if file_name:
            with open(file_name, 'w', newline='') as n_f:
                writer = csv.writer(n_f)
                writer.writerow(headers)

                for row in range(self._results_table.rowCount()):
                    for col in range(self._results_table.columnCount()):
                        temp_row.append(self._results_table.item(row, col).text())

                    writer.writerow(temp_row)
                    temp_row.clear()
                
    def exportCSVDialog(self):
        file_dialog = QFileDialog()
        file_name, ext = file_dialog.getSaveFileName(self, 'Export CSV File', "", "CSV (*.csv)")
        return file_name 
        
        


if __name__ == "__main__":
    window = AdvSearchWindow()
    window.show()
    sys.exit(app.exec_())