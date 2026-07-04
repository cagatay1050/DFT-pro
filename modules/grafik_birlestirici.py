import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QDoubleSpinBox, QSpinBox, 
    QScrollArea, QLineEdit, QFileDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QColorDialog, QComboBox
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from utils.style_manager import apply_global_style, notifier

class GrafikBirlestiriciWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.datasets = []
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Sol Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        group_files = QGroupBox("Veri Setleri (.csv, .dat)")
        files_layout = QVBoxLayout(group_files)
        
        self.btn_load = QPushButton("Veri Ekle")
        self.btn_load.clicked.connect(self.load_data)
        files_layout.addWidget(self.btn_load)
        
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Dosya", "Etiket", "Renk", "Stil"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.edit_cell)
        files_layout.addWidget(self.table)
        
        self.btn_plot = QPushButton("Grafiği Çiz")
        self.btn_plot.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.btn_plot.clicked.connect(self.plot_graph)
        files_layout.addWidget(self.btn_plot)
        
        left_layout.addWidget(group_files)
        left_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidget(left_panel)
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(450)
        
        # Sağ Panel (Çizim)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.figure = plt.figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(scroll)
        main_layout.addWidget(right_panel)
        
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)

    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QFormLayout(self.local_widget)
        self.le_x_label = QLineEdit("X Ekseni")
        self.le_y_label = QLineEdit("Y Ekseni")
        self.le_title = QLineEdit("Master Grafik")
        self.cb_legend_loc = QComboBox()
        self.cb_legend_loc.addItems(['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'])
        
        layout.addRow("X Etiketi:", self.le_x_label)
        layout.addRow("Y Etiketi:", self.le_y_label)
        layout.addRow("Başlık:", self.le_title)
        layout.addRow("Lejant Konumu:", self.cb_legend_loc)
        
    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.datasets:
            self.plot_graph()
            
    def load_data(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Veri Dosyası Seç", "", "Data Files (*.csv *.dat *.txt)")
        if not paths: return
        
        for path in paths:
            try:
                if path.endswith('.csv'):
                    df = pd.read_csv(path)
                else:
                    df = pd.read_csv(path, sep=r'\s+')
                    
                if len(df.columns) < 2:
                    continue
                    
                filename = path.split('/')[-1]
                default_color = plt.cm.tab10(len(self.datasets) % 10)
                hex_color = '#%02x%02x%02x' % (int(default_color[0]*255), int(default_color[1]*255), int(default_color[2]*255))
                
                self.datasets.append({
                    "path": path,
                    "df": df,
                    "label": filename,
                    "color": hex_color,
                    "style": "-"
                })
                self.update_table()
            except Exception as e:
                pass

    def update_table(self):
        self.table.setRowCount(len(self.datasets))
        for row, data in enumerate(self.datasets):
            self.table.setItem(row, 0, QTableWidgetItem(data["path"].split('/')[-1]))
            self.table.setItem(row, 1, QTableWidgetItem(data["label"]))
            
            color_item = QTableWidgetItem(data["color"])
            color_item.setBackground(QColor(data["color"]))
            color_item.setForeground(QColor("white" if int(data["color"][1:], 16) < 0x888888 else "black"))
            self.table.setItem(row, 2, color_item)
            
            self.table.setItem(row, 3, QTableWidgetItem(data["style"]))

    def edit_cell(self, row, col):
        if col == 1:
            from PyQt6.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(self, "Etiket Düzenle", "Yeni Etiket:", text=self.datasets[row]["label"])
            if ok and text:
                self.datasets[row]["label"] = text
                self.update_table()
        elif col == 2:
            color = QColorDialog.getColor(QColor(self.datasets[row]["color"]), self)
            if color.isValid():
                self.datasets[row]["color"] = color.name()
                self.update_table()
        elif col == 3:
            from PyQt6.QtWidgets import QInputDialog
            styles = ["-", "--", "-.", ":", "o", "s", "^", "D"]
            item, ok = QInputDialog.getItem(self, "Çizgi Stili Seç", "Stil:", styles, 0, False)
            if ok and item:
                self.datasets[row]["style"] = item
                self.update_table()
                
    def plot_graph(self):
        if not self.datasets: return
        
        self.figure.clear()
        apply_global_style()
        ax = self.figure.add_subplot(111)
        
        for data in self.datasets:
            df = data["df"]
            x = df.iloc[:, 0].values
            y = df.iloc[:, 1].values
            
            style = data["style"]
            if style in ["o", "s", "^", "D"]:
                ax.scatter(x, y, label=data["label"], color=data["color"], marker=style, s=40)
            else:
                ax.plot(x, y, label=data["label"], color=data["color"], linestyle=style)
                
        ax.set_xlabel(self.le_x_label.text())
        ax.set_ylabel(self.le_y_label.text())
        if self.le_title.text():
            ax.set_title(self.le_title.text())
            
        ax.legend(loc=self.cb_legend_loc.currentText(), frameon=True)
        
        self.figure.tight_layout()
        self.canvas.draw()
