import sys
from PySide2.QtCore import Qt, QSortFilterProxyModel, Signal, QEvent
from PySide2.QtWidgets import (QApplication, QMainWindow, QLabel, QSpinBox, QCompleter, QMenu, QHeaderView, QAbstractScrollArea, QAbstractItemView, QListWidget, QTableWidget, 
                              QTableWidgetItem, QFileDialog, QListWidgetItem, QComboBox, QHBoxLayout, QSizePolicy, QFrame, QMessageBox, QLineEdit, QGridLayout, QDialog, 
                              QCalendarWidget, QToolBar, QDockWidget, QVBoxLayout, QWidget, QPushButton, QFormLayout, QGroupBox, QCheckBox, QTextEdit, QScrollArea, QScroller)
from PySide2.QtGui import QMouseEvent, QFont, QIntValidator, QDoubleValidator, QIcon, QPixmap, QKeySequence
from LDF_UtilityScripts import tabNameFormat, excelColumnFromNumber
from LDF_Types import Types
from itertools import permutations
import re
import csv
import io

class DataTable(QTableWidget):
    def __init__(self, rows=0, columns=0, use_max_height=True, stretch=True, parent=None):
        super().__init__(rows, columns, parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        if use_max_height:
            self.setMaximumHeight(100)
    
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
        if stretch:
            self.verticalHeader().setStretchLastSection(True)

    def showContextMenu(self, pos):
        if self.rowCount() > 0:
            table = self.sender()
            pos = table.viewport().mapToGlobal(pos)
            menu = QMenu()
            copyAction = menu.addAction("Copy")
            if menu.exec_(pos) is copyAction:
                self.copySelection()
    
    def copySelection(self):
        selection = self.selectedIndexes()
        if selection:
            rows = sorted(index.row() for index in selection)
            columns = sorted(index.column() for index in selection)
            rowcount = rows[-1] - rows[0] + 1
            colcount = columns[-1] - columns[0] + 1
            table = [[''] * colcount for _ in range(rowcount)]
            for index in selection:
                row = index.row() - rows[0]
                column = index.column() - columns[0]
                table[row][column] = index.data()
            stream = io.StringIO()
            csv.writer(stream).writerows(table)
            QApplication.clipboard().setText(str(stream.getvalue()).strip())

    def event(self, event):
        if (event.type() == QEvent.KeyPress and
            event.matches(QKeySequence.Copy)):
            self.copySelection()
            return True
        return super().event(event)

class BreakLine(QFrame):
    def __init__(self, parent=None):
        super(BreakLine, self).__init__(parent)
        self.setFrameShape(self.HLine)
        self.setFrameShadow(self.Sunken)

class VerticalFiller(QWidget):
    def __init__(self, parent=None):
        super(VerticalFiller, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

class HorizontalFiller(QWidget):
    def __init__(self, parent=None):
        super(HorizontalFiller, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

class NewRecordDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QFormLayout(self)
        self.setWindowTitle("Enter New Record")
        only_int = QIntValidator(self)
        only_int.setTop(999999)
        self._ap_phase_id_entry = QLineEdit(self)
        self._ap_phase_id_entry.setPlaceholderText("e.g. 212421")
        self._ap_phase_id_entry.setValidator(only_int)
        self._address_entry = QLineEdit(self)
        self._address_entry.setPlaceholderText("1234 Sample Ave")
        button_row = QWidget(self)
        button_layout = QHBoxLayout(button_row)
        self._enter_button = QPushButton("Enter")
        self._enter_button.clicked.connect(self.enter)
        self._cancel_button = QPushButton("Cancel")
        self._canceled = True 
        self._cancel_button.clicked.connect(self.close) 

        button_layout.addWidget(self._enter_button)
        button_layout.addWidget(self._cancel_button) 
        layout.addRow(QLabel("Enter the ApPhase ID and Address:\n(the ApPhase ID must 6 numbers, neither field can be blank.)\n", self))
        layout.addRow("ApPhase ID:", self._ap_phase_id_entry)
        layout.addRow("Address:", self._address_entry)
        layout.addRow(button_row)
     
    def isCanceled(self):
        return self._canceled
    
    def enter(self):
        if len(self.getApPhaseID()) < 6 or len(self.getAddress()) < 1:
            self.enterCheckMsg()
        else:
            self._canceled = False
            self.close()
    
    def getApPhaseID(self):
        return self._ap_phase_id_entry.text()

    def getAddress(self):
        return self._address_entry.text()

    def enterCheckMsg(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Incorrect Inputs")
        msg.setText("ApPhase ID is not a 6 integers long or an Address is not entered.")
        msg.setIcon(msg.Warning)
        msg.setStandardButtons(msg.Ok)
        msg.exec_()

class Form:
    def __init__(self, parent):
        self._parent = parent
        self._new = False 
        self._ap_phase_change = False 
        self._address_change = False      

    def setFormParent(self, parent):
        self._parent = parent

    def setTab(self, parent, database):
        self.setParent(parent)
        self._database = database
    
    def getTableName(self):
        return self._table_name

    def getTabName(self):
        return tabNameFormat(self._table_name)

    def getSelf(self):
        return self
    
    def getFormData(self):
        data = {}
        for widget in self._table:
            data[widget.name] = widget.value.getValue()
        return data

    def getFields(self):
        fields = []
        for field in self._table:
            fields.append(field.name)
        return fields 
    
    def getValues(self):
        values = []
        for widget in self._table:
            values.append(widget.value.getValue())
        return values
        
    def readDataIntoForm(self, ap_phase_id):
        try:
            self._database.openDatabase()
            data = self._database.readRowFromApPhaseID(self._table_name, ap_phase_id)
            if data != None:
                i = 1
                for widget in self._table:
                    if self._table_name != "CLIENT" and widget.name == "AP_PHASE_ID":
                        continue 
                    widget.value.setValue(data[i])
                    i += 1
            self._database.closeDatabase()
        except Exception as e:
            print("Failed to write data into the from:", e) 

    def searchChange(self):
        return(self._ap_phase_change or self._address_change)

    def clearValues(self):
        for widget in self._table:
            widget.value.clearValue()

    def enableDisableCheck(self, check_widget, widgets=[], reverse_check=False):
        def enableDisable():
            if len(widgets) > 0:
                for widget in widgets:
                    if reverse_check:
                        widget.value.setDisabled(check_widget.value.isChecked())
                    else:
                        widget.value.setEnabled(check_widget.value.isChecked())
        return enableDisable
    
    def _formWidgetUpdate(self, table_name, widget):
        def formWidgetUpdate():
            if not self._new and not self._ap_phase_change and not self._address_change and self._database != None:        
                self._database.openDatabase()
                self._database.updateValue(table_name, widget.name, widget.value.getValue(), self._table.AP_PHASE_ID.value.getValue())
                self._database.closeDatabase()
                self._parent.updateDataTable()
            #print(Tables.CLIENT.name, widget.name, widget.value.getValue(), Client.AP_PHASE_ID.value.getValue())
        return formWidgetUpdate
    
    def formWidgetUpdate(self, table_name, widget):
            try:
                if not self._new and not self._ap_phase_change and not self._address_change and self._database != None:        
                    self._database.openDatabase()
                    self._database.updateValue(table_name, widget.name, widget.value.getValue(), self._table.AP_PHASE_ID.value.getValue())
                    self._database.closeDatabase()
                    self._parent.updateDataTable()
            except Exception as e:
                print("Failed to update form widget: ", e)
    
    def connectWidgets(self):
        if self._child_widgets_not_set:
            for widget in self._table:
                if self._table_name != "CLIENT" and widget.name == "AP_PHASE_ID":
                    continue
                widget.value.setParent(self)
                widget.value.connectFunction(self._formWidgetUpdate(self._table_name, widget))
      
            self._child_widgets_not_set = False
    
    def layoutWidgets(self):
        return (self._layout.itemAt(i) for i in range(self._layout.count()))

# A bold label
class FormLabel(QLabel):
    def __init__(self, text, margin_top=0):
        super(FormLabel, self).__init__(text)
        if bool(margin_top):
            self.setStyleSheet("QLabel {font-weight: bold; margin-top:"+str(margin_top)+";}")
        else:
            self.setStyleSheet("QLabel { font-weight: bold; }")
    def getValue(self):
        return self.text()

class FormGroupBox(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        font = QFont()
        font.setBold(True)
        old_font = QFont()
        old_font.setBold(False)
        frame = QWidget(self)
        frame.setFont(old_font)
        self.frame_layout = QFormLayout(frame)
        self.setFont(font)
        self._layout = QFormLayout(self)
        self._layout.addRow(frame)
        self.setLayout(self._layout)

class DateDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super(DateDialog, self).__init__(parent)
        layout = QGridLayout(self)
        self.setStyleSheet("")
        self.calendar = QCalendarWidget(self)
        self.calendar.setStyleSheet("")
        self.setWindowTitle(title)
        buttons = QWidget(self)
        buttons_layout = QGridLayout(buttons)
        self.enter_button = QPushButton("Enter", self)
        self.enter_button.clicked.connect(self.enter)
        self._not_canceled = False 
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.enter_button, 0, 0)
        buttons_layout.addWidget(self.cancel_button, 0, 1)
        layout.addWidget(self.calendar)
        layout.addWidget(buttons)
        self._date = ""
        
    def enter(self):
        self._not_canceled = True 
        self._date = self.calendar.selectedDate().toString("MM/dd/yyyy")
        self.close()
    
    def getDate(self):
        return self._date 
    
    def notCanceled(self):
        return self._not_canceled

class DateEntry(QLineEdit):
    def __init__(self, parent=None, fixed=False):
        super().__init__(parent)
        self.__type = Types.TEXT
        self.setReadOnly(True)
        if fixed:
            self.setFixedWidth(250)
        self.setMaximumWidth(250)
    
    def getType(self):
        return self.__type
    
    def getValue(self):
        return self.text()
    
    def setValue(self, value):
        self.setText(str(value))
    
    def clearValue(self):
        self.clear()

    def mousePressEvent(self, QMouseEvent):
        super(DateEntry, self).mousePressEvent(QMouseEvent)
        
        dd = DateDialog(self, "Select Date")
        dd.exec_()
        if dd.notCanceled():
            self.setText(dd.getDate())
    
    def connectFunction(self, function):
        self.editingFinished.connect(function)

class ExtendedComboBox(QComboBox):
    def __init__(self, table_name="", update_field="", database=None, parent=None):
        super(ExtendedComboBox, self).__init__(parent)
        self.__type = Types.TEXT
        self.setMinimumHeight(30)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)
        self._table_name = table_name
        self._update_field = update_field
        
        self._database = database

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        # connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    def setDatabase(self, database):
        self._database = database

    def getType(self):
        return self.__type

    # on selection of an item from the completer, select the corresponding item from combobox 
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))

    # on model change, update the models of the filter and completer as well 
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)    

    def updateListValues(self):
        if self._update_field and self._database != None:
            self.clear()
            self._database.openDatabase()
            items = list(set(self._database.getValuesFromField(self._table_name, self._update_field)))
            self._database.closeDatabase()
            self.addItems(items) 

    def setValue(self, value):
        if self._update_field and self._table_name and self._database != None:
            self.updateListValues()
        index = self.findText(value)
        if index == -1:
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(index)

    def getValue(self):
        return self.currentText()
    
    def clearValue(self):
        self.setCurrentIndex(0)
    
    def connectFunction(self, function):
        self.activated.connect(function)

class FormCheckBox(QCheckBox):
    def __init__(self, text, parent=None, reverse=False):
        super().__init__(text, parent)
        self._reverse = reverse
        self.__type = Types.BOOLEAN
    
    def getType(self):
        return self.__type 

    def getValue(self):
        return int(self.isChecked())
    
    def setValue(self, value):
        self.setChecked(bool(value))
    
    def clearValue(self):
        if self._reverse:
            self.setChecked(True)
        else:
            self.setChecked(False)
    
    def connectFunction(self, function):
        self.stateChanged.connect(function)

class FormEntry(QLineEdit):
    def __init__(self, parent=None, double_only=False, int_only=False, fixed=False, comma_sort=False):
        super().__init__(parent)
        self.__type = Types.TEXT
        self._double_only = double_only
        self._int_only = int_only
        if self._double_only:
            self.setValidator(QDoubleValidator())
            self.__type = Types.NUMBER
        elif self._int_only:
            self.setValidator(QIntValidator())
            self.__type = Types.INTEGER
        if fixed:
            self.setFixedWidth(250)
        self._comma_sort = comma_sort
        self.setMaximumWidth(250)
    
    def getType(self):
        return self.__type 

    def getValue(self):
        return self.text()

    def setValue(self, value):
        if value == -1:
            self.setText("")
        else:
            self.setText(str(value))
    
    def clearValue(self):
        self.clear()

    def commaSort(self):
        text = self.text()
        text = text.strip()
        t_list =  re.split(', | |_|-|!|,|\+', text)
        t_list = list(filter(('').__ne__, t_list))
        c_text = ', '.join(t_list)
        self.setText(c_text)
    
    def connectFunction(self, function):
        self.editingFinished.connect(function)
        if self._comma_sort:
            self.editingFinished.connect(self.commaSort)
   
class FormSpinBox(QSpinBox):
    def __init__(self, parent=None, default_value=3, min_value=1, max_value=5):
        super(FormSpinBox, self).__init__(parent)
        self.__type = Types.INTEGER
        self._min = min_value
        self._max = max_value
        self._default_value = default_value
        
        self.setMinimum(self._min)
        self.setMaximum(self._max)
        self.setValue(self._default_value)
        self.setMaximumWidth(200)
        self.setMinimumWidth(200)
    
    def getType(self):
        return self.__type 
        
    def getValue(self):
        return self.value()
    
    def setValue(self, value):
        int_val = int(value)
        super().setValue(value)

    def clearValue(self):
        self.setValue(3)
    
    def connectFunction(self, function):
        self.valueChanged.connect(function)

class SmartHFormLayout(QHBoxLayout):
    def __init__(self, parent):
        super().__init__(parent)
        self.setContentsMargins(0,0,0,0)

    def addRow(self, labels=None, widgets=None):
        try:
            if len(labels) > 0 and len(labels) < len(widgets):
                dif = len(widgets) - len(labels)
                for i in range(dif):
                    labels.append(None)

            if len(labels) == len(widgets):
                for i in range(0, len(labels)):
                    if labels[i] != None:
                        self.addWidget(QLabel(labels[i]))
                    self.addWidget(widgets[i])

            # Handle widget(s) without labels
            elif len(labels) < 1:
                for widget in widgets:
                    self.addWidget(widget) 
            self.addWidget(HorizontalFiller())
        
        except Exception as e:
            print("Could not add row:", str(e))

class FormTextBox(QTextEdit):
    editingFinished = Signal()
    receivedFocus = Signal()
    def __init__(self, parent=None, text="", fixed=False):
        super(FormTextBox, self).__init__(parent)
        self.__type = Types.TEXT
        self._changed = False
        self.setTabChangesFocus(True)
        self.textChanged.connect(self._handle_text_changed)
        self.setFixedHeight(60)
        if fixed:
            self.setFixedWidth(350)
    
    def getType(self):
        return self.__type

    def focusInEvent(self, event):
        super(FormTextBox, self).focusInEvent( event )
        self.receivedFocus.emit()

    def focusOutEvent(self, event):
        if self._changed:
            self.editingFinished.emit()
        super(FormTextBox, self).focusOutEvent( event )

    def _handle_text_changed(self):
        self._changed = True

    def setTextChanged(self, state=True):
        self._changed = state

    def setHtml(self, html):
        self.setHtml(self, html)
        self._changed = False

    def getValue(self):
        return self.toPlainText()
    
    def setValue(self, value):
        self.setText(str(value))

    def clearValue(self):
        self.clear()
    
    def connectFunction(self, function):
        self.editingFinished.connect(function)

class FormCombo(QComboBox):
    def __init__(self, parent=None, default_values=[], reason_combo=False):
        super().__init__(parent)
        self.__type = Types.TEXT
        self.setMinimumHeight(30)
        self.setMaximumWidth(250)
 
        if len(default_values) >= 1:
            self.addItems(default_values)
            self._reason_combo = reason_combo
            if self._reason_combo:
                self.REASONS = default_values
                self.RC = None
    
    def getType(self):
        return self.__type

    def setValue(self, value):
        index = self.findText(value)
        if index == -1:
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(index)
        if self._reason_combo:
            self.reasonCombos()

    def getValue(self):
        return self.currentText()
    
    def clearValue(self):
        self.setCurrentIndex(0)
    
    def connectFunction(self, function):
        self.activated.connect(function)
    
    def setReasonCombos(self, rc = []):
        if self._reason_combo:
            self.RC = rc 
    
    def reasonCombos(self):
        index = 0
        r_texts = [combo.currentText() for combo in self.RC]
        for i in range(0, len(self.RC)):
            self.RC[i].clear()
            self.RC[i].addItems(self.REASONS)
            self.RC[i].setCurrentText(r_texts[i])

        for combo in permutations(self.RC, len(self.RC)-1):
            if combo[0].currentText() != self.REASONS[0]:
                index = combo[1].findText(combo[0].currentText()) 
                if index > -1:
                    combo[1].removeItem(index)

class FormMenu(QListWidget):
   def __init__(self, item_names=[], icon_loc="table.png", parent=None):
      super().__init__(parent)
      self.setStyleSheet("""
         font-size: 12pt;
      """)
      self.setMinimumWidth(300)

      self.setSelectionMode(QAbstractItemView.SingleSelection)
      if item_names:
         for item_name in item_names:
            item = QListWidgetItem(item_name)
            item.setIcon(QIcon(QPixmap(icon_loc)))
            self.addItem(item)