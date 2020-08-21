import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QMainWindow, QMenu, QWidget, QVBoxLayout, QToolBar, QPushButton, QFileDialog, QLabel)
from PySide2.QtGui import  (QIcon, QPixmap)
from LDF_UtilityScripts import excelColumnFromNumber, ageFilter, createAgeBins, unknownBlankLabel
from LDF_Widgets import HorizontalFiller, FormEntry, FormMenu
from LDF_DatabaseTables import Tables
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
import pandas as pd 
import pylab as pl 
from collections import Counter

class PlotBarWindow(QMainWindow):
    def __init__(self, title, labels=[], data=[], table_name="", field_name="", x_label=None, y_label=None, parent=None, already_sorted=False):
        super().__init__(parent)
        self._title = title 
        self._labels = labels 
        self._data = data
        self._last_column = excelColumnFromNumber(len(self._data))
        self._plot_location = excelColumnFromNumber(len(self._data)+2)
        self._x_label = x_label
        self._y_label = y_label
        self._already_sorted = already_sorted

        self.setWindowTitle(self._title)
        self._figure = plt.figure(figsize=(5, 4), dpi=100, facecolor=(1,1,1), edgecolor=(0,0,0))
        self.ax = self._figure.add_subplot()
        self.ax.set_title(self._title)
        self._canvas = FigureCanvas(self._figure)
        self._navigation_toolbar = NavigationToolbar(self._canvas, None)
        self.addToolBar(self._navigation_toolbar)
        self._bottom_toolbar = QToolBar(self)
        self._bottom_toolbar.setMovable(False)
        self._bottom_toolbar.setFloatable(False)
        self._bottom_toolbar.setStyleSheet("QToolBar {border-bottom: None; border-top: 1px solid #BBBBBB;}")
        self._table_name_label = QLabel(" Table:")
        self._field_name_label = QLabel(" Field:")
        self._table_name = FormEntry(self)
        self._table_name.setMaximumHeight(20)
        self._field_name = FormEntry(self)
        self._field_name.setMaximumHeight(20)
        self._table_name.setReadOnly(True)
        self._field_name.setReadOnly(True)
        self._table_name.setText(table_name)
        self._field_name.setText(field_name)
        self._bottom_toolbar.addWidget(self._table_name_label)
        self._bottom_toolbar.addWidget(self._table_name)
        self._bottom_toolbar.addWidget(self._field_name_label)
        self._bottom_toolbar.addWidget(self._field_name)
        self._export_chart_button = QPushButton("Export")
        self._export_chart_button.setIcon(QIcon(QPixmap("export.png")))
        self._export_chart_button.clicked.connect(self.exportChart)
        self._bottom_toolbar.addWidget(HorizontalFiller(self))

        self._bottom_toolbar.addWidget(self._export_chart_button)
        self.addToolBar(Qt.BottomToolBarArea, self._bottom_toolbar)

        self.ax.bar(self._labels, self._data)
        if self._x_label != None:
            self.ax.set_xlabel(self._x_label)
        if self._y_label != None:
            self.ax.set_ylabel(self._y_label)
        self.setCentralWidget(self._canvas)

    def exportChartFileDialog(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilters(["*. xlsx"])
        file_name, ext = file_dialog.getSaveFileName(self, 'Export File', "", "Excel (*.xlsx)")
            
        if file_name and ext == "Excel (*.xlsx)":
            return file_name 
        return ""

    def exportChart(self):
        file_name = self.exportChartFileDialog()
        field_name = self._field_name.text()
        if file_name != "":
            title = self.ax.title.get_text()
            last_row = len(self._data)+2
            labels = sorted(self._labels)
            if self._already_sorted:
                sorted_data = {label:[self._data[i]] for i, label in enumerate(self._labels)}
            else:
                data = {label:[self._data[i]] for i, label in enumerate(self._labels)}
                sorted_data = {label:data[label] for label in labels}
            df = pd.DataFrame(data=sorted_data)
            
            writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
            df.to_excel(writer, sheet_name=field_name, index=False)
            workbook = writer.book
            worksheet = writer.sheets[field_name]
            chart = workbook.add_chart({"type": 'column'})
            chart.set_title({"name": title})
            if self._x_label != None:
                chart.set_x_axis({'name': self._x_label})
            if self._y_label != None:
                chart.set_y_axis({'name': self._y_label})
            chart.add_series({"categories": "={fn}!$A$1:${lc}$1".format(lc=self._last_column, fn=field_name), 
                              "values": "={fn}!$A$2:${lc}$2".format(lc=self._last_column, fn=field_name), 
                              "fill": {'color': '#0000CC'}})
            worksheet.insert_chart(self._plot_location+"2", chart)
            writer.save()
            writer.close()

class PlotHBarWindow(QMainWindow):
    def __init__(self, title, labels=[], data=[], table_name="", field_name="", parent=None):
        super().__init__(parent)
        self._title = title 
        self._labels = labels 
        self._data = data
        self._last_column = excelColumnFromNumber(len(self._data))
        self._plot_location = excelColumnFromNumber(len(self._data)+2)

        self.setWindowTitle(self._title)
        self._figure = plt.figure(figsize=(5, 4), dpi=100, facecolor=(1,1,1), edgecolor=(0,0,0))
        self.ax = self._figure.add_subplot()
        self.ax.set_title(self._title)
        self._canvas = FigureCanvas(self._figure)
        self._navigation_toolbar = NavigationToolbar(self._canvas, None)
        self.addToolBar(self._navigation_toolbar)
        self._bottom_toolbar = QToolBar(self)
        self._bottom_toolbar.setMovable(False)
        self._bottom_toolbar.setFloatable(False)
        self._bottom_toolbar.setStyleSheet("QToolBar {border-bottom: None; border-top: 1px solid #BBBBBB;}")
        self._table_name_label = QLabel(" Table:")
        self._field_name_label = QLabel(" Field:")
        self._table_name = FormEntry(self)
        self._table_name.setMaximumHeight(20)
        self._field_name = FormEntry(self)
        self._field_name.setMaximumHeight(20)
        self._table_name.setReadOnly(True)
        self._field_name.setReadOnly(True)
        self._table_name.setText(table_name)
        self._field_name.setText(field_name)
        self._bottom_toolbar.addWidget(self._table_name_label)
        self._bottom_toolbar.addWidget(self._table_name)
        self._bottom_toolbar.addWidget(self._field_name_label)
        self._bottom_toolbar.addWidget(self._field_name)
        self._export_chart_button = QPushButton("Export")
        self._export_chart_button.setIcon(QIcon(QPixmap("export.png")))
        self._export_chart_button.clicked.connect(self.exportChart)
        self._bottom_toolbar.addWidget(HorizontalFiller(self))

        self._bottom_toolbar.addWidget(self._export_chart_button)
        self.addToolBar(Qt.BottomToolBarArea, self._bottom_toolbar)

        y_pos = np.arange(len(data))
        self.ax.barh(y_pos, data, align="center", color='lightskyblue', alpha=0.5)
        self.ax.set_xlabel(labels[len(labels)-1])
        #self.ax.set_ylabel(labels[1])
        
        rects = self.ax.patches
        low_rect = rects[0]
        high_rect = rects[len(rects)-1]
        width = low_rect.get_width()
        self.ax.text(low_rect.get_x()+width, low_rect.get_y()+1, "Lowest: $"+str(data[0]))
        width = high_rect.get_width()
        self.ax.text(high_rect.get_x(), high_rect.get_y()+1, "Highest: $"+str(data[len(data)-1]))
        self.setCentralWidget(self._canvas)
    
    def exportChartFileDialog(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilters(["*. xlsx"])
        file_name, ext = file_dialog.getSaveFileName(self, 'Export File', "", "Excel (*.xlsx)")
            
        if file_name and ext == "Excel (*.xlsx)":
            return file_name 
        return ""

    def exportChart(self):
        file_name = self.exportChartFileDialog()
        field_name = self._field_name.text()
        if file_name != "":
            title = self.ax.title.get_text()
            last_row = len(self._data)+2
            col_1 = ["" for data in self._data]
            col_2 = col_1.copy()
            col_1[0] = self._data[0]
            col_2[0] = self._data[len(self._data)-1]
            data = {
                self._labels[0]: self._data,
                self._labels[1]: col_1,
                self._labels[2]: col_2
            }
            df = pd.DataFrame(data=data)
            
            writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
            df.to_excel(writer, sheet_name=field_name, index=False)
            workbook = writer.book
            worksheet = writer.sheets[field_name]
            chart = workbook.add_chart({"type": 'bar'})
            chart.set_title({"name": title})
            chart.set_x_axis({'name': self._labels[0]})
            chart.add_series({"values": "={fn}!$A$2:$A${lr}".format(lr=last_row, fn=field_name), 'fill': {'color': '#0000CC'}, 'border': {'color': '#0000CC'}})
            worksheet.insert_chart(self._plot_location+"2", chart)
            writer.save()
            writer.close()
        
class PlotPieWindow(QMainWindow):
    def __init__(self, title, labels=[], data=[], table_name="", field_name="", random_colors=False, has_explode=True, parent=None):
        super().__init__(parent)
        self._main_widget = QWidget(self)
        self._layout = QVBoxLayout(self._main_widget)
        self._title = title 
        self._data = data
        self._df_data = {k:v for (k,v) in zip(labels, data)} 
        
        self.setWindowTitle(title)
        # Pie chart, where the slices will be ordered and plotted counter-clockwise:
        self._labels = labels 
        self._sizes = data 
        self._legend_labels = [label+" - "+"{:.1f}".format(value)+"%" for label, value in zip(self._labels, self._sizes)]
        self._last_column = excelColumnFromNumber(len(self._labels))
        self._plot_location = excelColumnFromNumber(len(self._data)+2)
        explode = [0 for value in data]
        explode[1] = 0.1
        explode = tuple(explode)

        self._figure = plt.figure(figsize=(5, 4), dpi=100, facecolor=(1,1,1), edgecolor=(0,0,0))
        self.ax = self._figure.add_subplot()
        self._canvas = FigureCanvas(self._figure)
        colors = ['yellowgreen', 'lightskyblue']
        self._navigation_toolbar = NavigationToolbar(self._canvas, None)
        self.addToolBar(self._navigation_toolbar)
        if random_colors:
            if has_explode:
                self.ax.pie(self._sizes, explode=explode, autopct = "%1.1f%%", shadow=True, startangle=int(90))
            else:
                self.ax.pie(self._sizes, autopct = "%1.1f%%", shadow=True, startangle=int(90))
        else:
            if has_explode:
                self.ax.pie(self._sizes, explode=explode, colors=colors, autopct = "%1.1f%%", shadow=True, startangle=int(90))
            else:
                self.ax.pie(self._sizes, colors=colors, autopct = "%1.1f%%", shadow=True, startangle=int(90))
        self.ax.legend(labels=self._legend_labels, loc="best")
        # Equal aspect ratio ensures that pie is drawn as a circle.
        self.ax.axis("equal")
        self.ax.set_title(title)

        self._bottom_toolbar = QToolBar(self)
        self._bottom_toolbar.setMovable(False)
        self._bottom_toolbar.setFloatable(False)
        self._bottom_toolbar.setStyleSheet("QToolBar {border-bottom: None; border-top: 1px solid #BBBBBB;}")
        self._table_name_label = QLabel(" Table:")
        self._field_name_label = QLabel(" Field:")
        self._table_name = FormEntry(self)
        self._table_name.setMaximumHeight(20)
        self._field_name = FormEntry(self)
        self._field_name.setMaximumHeight(20)
        self._table_name.setReadOnly(True)
        self._field_name.setReadOnly(True)
        self._table_name.setText(table_name)
        self._field_name.setText(field_name)
        self._bottom_toolbar.addWidget(self._table_name_label)
        self._bottom_toolbar.addWidget(self._table_name)
        self._bottom_toolbar.addWidget(self._field_name_label)
        self._bottom_toolbar.addWidget(self._field_name)
        
        self._export_chart_button = QPushButton("Export")
        self._export_chart_button.setIcon(QIcon(QPixmap("export.png")))
        self._export_chart_button.clicked.connect(self.exportChart)
        
        self._bottom_toolbar.addWidget(HorizontalFiller(self))
        self._bottom_toolbar.addWidget(self._export_chart_button)
        self.addToolBar(Qt.BottomToolBarArea, self._bottom_toolbar)
        self.setCentralWidget(self._canvas)
 
    def exportChartFileDialog(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilters(["*. xlsx"])
        file_name, ext = file_dialog.getSaveFileName(self, 'Export File', "", "Excel (*.xlsx)")
            
        if file_name and ext == "Excel (*.xlsx)":
            return file_name 
        return ""

    def exportChart(self):
        file_name = self.exportChartFileDialog()
        if file_name != "":
            title = self.ax.title.get_text()
            df = pd.DataFrame(data=[self._df_data])
            writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Pie_Chart', index=False)
            workbook = writer.book
            worksheet = writer.sheets["Pie_Chart"]
            chart = workbook.add_chart({"type": 'pie'})
            chart.set_title({"name": title})
            chart.add_series({"categories": "=Pie_Chart!$A$1:${lc}$1".format(lc = self._last_column), "values": "=Pie_Chart!$A$2:${lc}$2".format(lc = self._last_column)})
            worksheet.insert_chart(self._plot_location+"2", chart)
            writer.save()
            writer.close()

class Plots:
    def __init__(self):
        self._plots = {}
        self._plot_updates = {
            "Top Reasons for Device": self.deviceMotivation1,
            "2nd Top Reasons for Device": self.deviceMotivation2,
            "3rd Top Reasons for Device": self.deviceMotivation3,
            "Device Influence": self.deviceInfluence,
            "Device Installation": self.deviceInstallation,
            "Installation Cost": self.installationCost,
            "Family Size": self.familySize,
            "Leak Discovered": self.leakDiscovered,
            "Device Owner Age": self.deviceOwnerAge,
            "Device Owner Work Status": self.workStatus,
            "Income of Device Owner": self.incomesOfDeviceOwners,
            "Home Value": self.homeValues,
            "Home Value (RedFin)": self.homeValuesRedFin,
            "Device Owner's Education": self.deviceOwnerEducation
            
        }
        plot_names = list(self._plot_updates.keys())
        self._plot_menu = FormMenu(plot_names, icon_loc="plot.png")
        self._plot_menu.itemDoubleClicked.connect(self.showPlot)
 
    def deviceMotivation1(self):
        # DEVICE MOTIVATION 1 - PIE PLOT
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        data = self._database.getValuesFromField(Tables.MOTIVATIONS.name, "REASON_1")
        clean_data = [value for value in data if not unknownBlankLabel(value)]
        total_data = len(clean_data) 
        data_counts = Counter(clean_data).most_common()
        labels = [label for label, count in data_counts]
        data = [float(data_count/total_data*100) for label, data_count in data_counts]
    
        self._plots["Top Reasons for Device"] = PlotPieWindow(title="Top Reasons for Purchasing Device",
                                                labels=labels,
                                                data=data,
                                                table_name=Tables.MOTIVATIONS.name,
                                                field_name="REASON_1",
                                                random_colors=True,
                                                has_explode=False)
        self._database.closeDatabase()
    
    def deviceMotivation2(self):
        # DEVICE MOTIVATION 2 - PIE PLOT
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        data = self._database.getValuesFromField(Tables.MOTIVATIONS.name, "REASON_2")
        clean_data = [value for value in data if not unknownBlankLabel(value)]
        total_data = len(clean_data) 
        data_counts = Counter(clean_data).most_common()
        labels = [label for label, count in data_counts]
        data = [float(data_count/total_data*100) for label, data_count in data_counts]
    
        self._plots["2nd Top Reasons for Device"] = PlotPieWindow(title="2nd Top Reasons for Purchasing Device",
                                                labels=labels,
                                                data=data,
                                                table_name=Tables.MOTIVATIONS.name,
                                                field_name="REASON_2",
                                                random_colors=True,
                                                has_explode=False)
        self._database.closeDatabase()
    
    def deviceMotivation3(self):
        # DEVICE MOTIVATION 3 - PIE PLOT
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        data = self._database.getValuesFromField(Tables.MOTIVATIONS.name, "REASON_3")
        clean_data = [value for value in data if not unknownBlankLabel(value)]
        total_data = len(clean_data) 
        data_counts = Counter(clean_data).most_common()
        labels = [label for label, count in data_counts]
        data = [float(data_count/total_data*100) for label, data_count in data_counts]
    
        self._plots["3rd Top Reasons for Device"] = PlotPieWindow(title="3rd Top Reasons for Purchasing Device",
                                                labels=labels,
                                                data=data,
                                                table_name=Tables.MOTIVATIONS.name,
                                                field_name="REASON_3",
                                                random_colors=True,
                                                has_explode=False)
        self._database.closeDatabase()
        
    def deviceInfluence(self):
        # DEVICE INFLUENCE - PIE PLOT
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        data = self._database.getValuesFromField(Tables.PREV_LEAK.name, "INFLUENCE")
        total_data = len(data)
        influ_count = data.count(1)
        influ_per = int(influ_count/total_data*100)
        other_per = 100 - influ_per
        data = [influ_per, other_per]
        self._plots["Device Influence"] = PlotPieWindow(title="Device Purchases Due to Previous Leak",
                                            labels=["Previous Leak", "other"],
                                            data=data,
                                            table_name=Tables.PREV_LEAK.name,
                                            field_name="INFLUENCE")
        self._database.closeDatabase()
    
    def deviceInstallation(self):
        # DEVICE INSTALLATION - PIE PLOT
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        data = self._database.getValuesFromField(Tables.INSTALLATION.name, "SELF_INSTALLED")
        total_data = len(data)
        self_installed_count = data.count(1)
        self_installed_per = int(self_installed_count/total_data*100)
        pro_per = 100 - self_installed_per
        data = [self_installed_per, pro_per]
        self._plots["Device Installation"] = PlotPieWindow(title="Device Installation",
                                                labels=["Self Installed", "Installed by Professional/Other"],
                                                data=data,
                                                table_name=Tables.INSTALLATION.name,
                                                field_name="SELF_INSTALLED")
        self._database.closeDatabase()

    def deviceOwnerEducation(self):
        # DEVICE OWNER EDUCATION - PIE PLOT
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        data = self._database.getValuesFromField(Tables.PEOPLE.name, "HIGHEST_EDU")
        clean_data = [value for value in data if not unknownBlankLabel(value)]
        total_data = len(clean_data) 
        data_counts = Counter(clean_data).most_common()
        labels = [label for label, count in data_counts]
        data = [float(data_count/total_data*100) for label, data_count in data_counts]
    
        self._plots["Device Owner's Education"] = PlotPieWindow(title="Device Owner's Education",
                                                labels=labels,
                                                data=data,
                                                table_name=Tables.PEOPLE.name,
                                                field_name="HIGHEST_EDU",
                                                random_colors=True,
                                                has_explode=False)
        self._database.closeDatabase()

    def installationCost(self):
        # INSTALLATION COST - HBar PLOT
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        install_costs = self._database.getValuesFromField(Tables.INSTALLATION.name, "INSTALL_COST")
        total_installs = len(install_costs)
        install_costs = list(filter(lambda a: a != '' and a > 0, install_costs))
        install_costs = sorted(install_costs)
        lowest_cost = min(install_costs)
        highest_cost = max(install_costs)
        self._plots["Installation Cost"] = PlotHBarWindow(title="Installation Cost - Low vs High",
                                                labels=["Installation Cost", "Lowest", "Highest"],
                                                data=install_costs, 
                                                table_name=Tables.INSTALLATION.name,
                                                field_name="INSTALL_COST")
        self._database.closeDatabase()

    def deviceOwnerAge(self):
        # DEVICE OWNER AGE - BAR GRAPH
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        data = self._database.getValuesFromField(Tables.PEOPLE.name, "AGES")
        filter_ages = [ageFilter(age_string.split()) for age_string in data if len(age_string.split())]
        data.clear()
        for ages in filter_ages:
            data.extend(ages)
        bins = [(90, 70), (69, 60), (59, 50), (49, 40), (39, 30), (29, 18)]
        labels = []
        age_bins = [] 
        for age_bin in bins:
            labels.append(str(age_bin))
            age_bins.append(len(createAgeBins(data, age_bin)))
        self._plots["Device Owner Age"] = PlotBarWindow(title="Age of Device Owners",
                                                   labels=labels,
                                                   data=age_bins,
                                                   table_name=Tables.PEOPLE.name, 
                                                   field_name="AGES",
                                                   x_label="Age Ranges",
                                                   y_label="Number of People",
                                                   already_sorted=True)    
        self._database.closeDatabase()
        
    def familySize(self):
        # FAMILY SIZE - BAR GRAPH
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        data = self._database.getValuesFromField(Tables.PEOPLE.name, "PEOPLE_COUNT")
        total_data = len(data)
        data_counts = Counter(data).most_common()
        labels = [label for label, count in data_counts]
        data = [data_count for label, data_count in data_counts]
        #data = [float(data_count/total_data*100) for label, data_count in data_counts]
        self._plots["Family Size"] = PlotBarWindow(title="Family Size",
                                                   labels=labels,
                                                   data=data,
                                                   table_name=Tables.PEOPLE.name, 
                                                   field_name="PEOPLE_COUNT",
                                                   x_label="Number of Family Members",
                                                   y_label="Family Size Counts")
        self._database.closeDatabase()

    def workStatus(self):
        # WORK STATUS - PIE PLOT 
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        data = self._database.getValuesFromField(Tables.ECONOMIC.name, "POC")
        total_data = len(data)
        data_counts = Counter(data).most_common()
        labels = [label for label, count in data_counts]
        data = [float(data_count/total_data*100) for label, data_count in data_counts]
        self._plots["Device Owner Work Status"] = PlotPieWindow(title="Device Owner Work Status",
                                                labels=labels,
                                                data=data,
                                                table_name=Tables.ECONOMIC.name,
                                                field_name="POC")                            
        self._database.closeDatabase()
    
    def incomesOfDeviceOwners(self):
        # INCOMES OF DEVICE OWNERS - HBar PLOT
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        incomes = self._database.getValuesFromField(Tables.ECONOMIC.name, "INCOME")
        incomes = list(filter(lambda a: a != '' and a > 0, incomes))
        incomes = sorted(incomes)
        #lowest_income = min(incomes)
        #highest_income = max(incomes)
        self._plots["Income of Device Owner"] = PlotHBarWindow(title="Income of Device Owner - Low vs High",
                                                labels=["Income", "Lowest", "Highest"],
                                                data=incomes, 
                                                table_name=Tables.ECONOMIC.name,
                                                field_name="INCOME")
        self._database.closeDatabase()
    
    def homeValues(self):
        # Home Values - HBar PLOT
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        home_vals = self._database.getValuesFromField(Tables.ECONOMIC.name, "HOME_VAL")
        home_vals = list(filter(lambda a: a != '' and a > 0, home_vals))
        home_vals = sorted(home_vals)
        #lowest_home_val = min(home_vals)
        #highest_home_val = max(home_vals)
        self._plots["Home Value"] = PlotHBarWindow(title="Home Value - Low vs High",
                                                labels=["Home Value", "Lowest", "Highest"],
                                                data=home_vals, 
                                                table_name=Tables.ECONOMIC.name,
                                                field_name="HOME_VAL")
        self._database.closeDatabase()
    
    def homeValuesRedFin(self):
        # Home Values RedFin- HBar PLOT
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        home_vals = self._database.getValuesFromField(Tables.HOME_INFO.name, "REDFIN_VAL")
        home_vals = list(filter(lambda a: a != '' and a > 0, home_vals))
        home_vals = sorted(home_vals)
        #lowest_home_val = min(home_vals)
        #highest_home_val = max(home_vals)
        self._plots["Home Value (RedFin)"] = PlotHBarWindow(title="Home Value (RedFin) - Low vs High",
                                                labels=["Home Value", "Lowest", "Highest"],
                                                data=home_vals, 
                                                table_name=Tables.HOME_INFO.name,
                                                field_name="REDFIN_VAL")
        self._database.closeDatabase()

    def leakDiscovered(self):                                                   
        # LEAK DISCOVERY - PIE PLOT
        # ----------------------------------------------------------------------------------------------------------
        self._database.openDatabase()
        data = self._database.getValuesFromField(Tables.DEVICE_DETECTION.name, "LEAK_DISCOVERED")
        total_data = len(data)
        leak_discover_count = data.count(1)
        leak_discover_per = int(leak_discover_count/total_data*100)
        no_leak_per = 100 - leak_discover_per
        data = [leak_discover_per, no_leak_per]
        self._plots["Leak Discovered"] = PlotPieWindow(title="Leaks Discovered After Device Install",
                                                labels=["Leaks Discovered", ""],
                                                data=data,
                                                table_name=Tables.DEVICE_DETECTION.name,
                                                field_name="LEAK_DISCOVERED")                            
        self._database.closeDatabase()
        
    def showPlot(self, item):
        plot_name = item.text()
        self._plot_updates[plot_name]()
        self._plots[plot_name].show()