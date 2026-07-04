import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QDoubleSpinBox, QSpinBox, 
    QScrollArea, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from utils.style_manager import apply_global_style, notifier

class FormasyonEnerjisiWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Sol Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        group_comp = QGroupBox("Bileşik Bilgileri")
        comp_layout = QFormLayout(group_comp)
        
        self.le_formula = QLineEdit("Sr2ZnH6")
        self.le_e_total = QDoubleSpinBox()
        self.le_e_total.setRange(-99999, 99999)
        self.le_e_total.setValue(-35.2415)
        self.le_e_total.setDecimals(4)
        
        comp_layout.addRow("Bileşik Formülü:", self.le_formula)
        comp_layout.addRow("Toplam Enerji (eV):", self.le_e_total)
        
        group_refs = QGroupBox("Referans Elementler")
        refs_layout = QVBoxLayout(group_refs)
        
        self.table_refs = QTableWidget(3, 3)
        self.table_refs.setHorizontalHeaderLabels(["Element", "Bileşikteki Sayı (n)", "Saf Enerjisi (eV/atom)"])
        self.table_refs.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.table_refs.setItem(0, 0, QTableWidgetItem("Sr"))
        self.table_refs.setItem(0, 1, QTableWidgetItem("2"))
        self.table_refs.setItem(0, 2, QTableWidgetItem("-1.52"))
        
        self.table_refs.setItem(1, 0, QTableWidgetItem("Zn"))
        self.table_refs.setItem(1, 1, QTableWidgetItem("1"))
        self.table_refs.setItem(1, 2, QTableWidgetItem("-1.26"))
        
        self.table_refs.setItem(2, 0, QTableWidgetItem("H"))
        self.table_refs.setItem(2, 1, QTableWidgetItem("6"))
        self.table_refs.setItem(2, 2, QTableWidgetItem("-3.38"))
        
        refs_layout.addWidget(self.table_refs)
        
        btn_add_row = QPushButton("+ Element Ekle")
        btn_add_row.clicked.connect(self.add_ref_row)
        btn_del_row = QPushButton("- Son Elementi Sil")
        btn_del_row.clicked.connect(self.del_ref_row)
        
        h_btn = QHBoxLayout()
        h_btn.addWidget(btn_add_row)
        h_btn.addWidget(btn_del_row)
        refs_layout.addLayout(h_btn)
        
        self.lbl_result = QLabel("Oluşum Enerjisi: Bekleniyor...")
        self.lbl_result.setStyleSheet("font-size: 16px; font-weight: bold; color: #8e44ad;")
        
        self.btn_calc = QPushButton("Hesapla ve Çiz")
        self.btn_calc.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.calculate_and_plot)
        
        left_layout.addWidget(group_comp)
        left_layout.addWidget(group_refs)
        left_layout.addWidget(self.lbl_result)
        left_layout.addWidget(self.btn_calc)
        left_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidget(left_panel)
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(450)
        
        # Sağ Panel
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
        
        self.last_ef_total = None
        self.last_ef_atom = None

    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QFormLayout(self.local_widget)
        self.le_bar_color = QLineEdit("#8e44ad")
        layout.addRow("Bar Rengi:", self.le_bar_color)
        
    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.last_ef_total is not None:
            self.plot_graph()
            
    def add_ref_row(self):
        rc = self.table_refs.rowCount()
        self.table_refs.insertRow(rc)
        self.table_refs.setItem(rc, 0, QTableWidgetItem("X"))
        self.table_refs.setItem(rc, 1, QTableWidgetItem("1"))
        self.table_refs.setItem(rc, 2, QTableWidgetItem("0.0"))
        
    def del_ref_row(self):
        rc = self.table_refs.rowCount()
        if rc > 0:
            self.table_refs.removeRow(rc - 1)
            
    def calculate_and_plot(self):
        e_total = self.le_e_total.value()
        
        ref_sum = 0.0
        total_atoms = 0
        try:
            for r in range(self.table_refs.rowCount()):
                elem = self.table_refs.item(r, 0).text() if self.table_refs.item(r, 0) else ""
                n_str = self.table_refs.item(r, 1).text() if self.table_refs.item(r, 1) else "0"
                e_str = self.table_refs.item(r, 2).text() if self.table_refs.item(r, 2) else "0"
                
                n = float(n_str)
                e = float(e_str)
                
                ref_sum += (n * e)
                total_atoms += n
                
            ef_total = e_total - ref_sum
            ef_atom = ef_total / total_atoms if total_atoms > 0 else 0
            
            self.last_ef_total = ef_total
            self.last_ef_atom = ef_atom
            
            self.lbl_result.setText(
                f"Birim Hücre Formasyon Enerjisi: {ef_total:.4f} eV\n"
                f"Atom Başına Formasyon Enerjisi: {ef_atom:.4f} eV/atom"
            )
            
            self.plot_graph()
        except Exception as e:
            self.lbl_result.setText("Lütfen tablodaki sayıları kontrol edin.")
            
    def plot_graph(self):
        if self.last_ef_total is None: return
        
        self.figure.clear()
        apply_global_style()
        ax = self.figure.add_subplot(111)
        
        bars = ['Birim Hücre\n(eV)', 'Atom Başına\n(eV/atom)']
        vals = [self.last_ef_total, self.last_ef_atom]
        
        c = self.le_bar_color.text()
        if not c: c = "#8e44ad"
        
        ax.bar(bars, vals, color=c, width=0.4)
        ax.axhline(0, color='black', linewidth=1.5)
        
        for i, v in enumerate(vals):
            ax.text(i, v + (0.05 if v > 0 else -0.05), f"{v:.4f}", ha='center', va='bottom' if v > 0 else 'top')
            
        ax.set_ylabel("Formasyon Enerjisi (eV)")
        ax.set_title(rf"{self.le_formula.text()} - Formasyon Enerjisi")
        
        self.figure.tight_layout()
        try:
            from utils.style_manager import apply_custom_axes_settings
            if hasattr(self, 'figure'):
                apply_custom_axes_settings(self.figure)
        except Exception as e:
            print(f'Error applying custom axes settings: {e}')
        self.canvas.draw()
