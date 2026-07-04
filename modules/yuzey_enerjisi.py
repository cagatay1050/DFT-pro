import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QDoubleSpinBox, QSpinBox, 
    QScrollArea, QLineEdit
)
from utils.style_manager import apply_global_style, notifier

class YuzeyEnerjisiWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Sol Panel (Ayarlar)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        group_inputs = QGroupBox("Hesaplama Parametreleri")
        form_inputs = QFormLayout(group_inputs)
        
        self.le_e_slab = QDoubleSpinBox(); self.le_e_slab.setRange(-99999, 99999); self.le_e_slab.setValue(-120.5); self.le_e_slab.setDecimals(4)
        self.le_e_bulk = QDoubleSpinBox(); self.le_e_bulk.setRange(-99999, 99999); self.le_e_bulk.setValue(-25.2); self.le_e_bulk.setDecimals(4)
        self.le_n_slab = QSpinBox(); self.le_n_slab.setRange(1, 1000); self.le_n_slab.setValue(24)
        self.le_n_bulk = QSpinBox(); self.le_n_bulk.setRange(1, 1000); self.le_n_bulk.setValue(5)
        self.le_area = QDoubleSpinBox(); self.le_area.setRange(0.01, 99999); self.le_area.setValue(15.2); self.le_area.setDecimals(4)
        
        form_inputs.addRow("Slab Enerjisi (eV):", self.le_e_slab)
        form_inputs.addRow("Bulk Enerjisi (eV):", self.le_e_bulk)
        form_inputs.addRow("Slab Atom Sayısı:", self.le_n_slab)
        form_inputs.addRow("Bulk Atom Sayısı:", self.le_n_bulk)
        form_inputs.addRow("Yüzey Alanı (Å²):", self.le_area)
        
        group_results = QGroupBox("Sonuçlar")
        res_layout = QVBoxLayout(group_results)
        self.lbl_result = QLabel("Yüzey Enerjisi: Bekleniyor...")
        self.lbl_result.setStyleSheet("font-size: 16px; font-weight: bold; color: #2980b9;")
        res_layout.addWidget(self.lbl_result)
        
        self.btn_calc = QPushButton("Hesapla ve Çiz")
        self.btn_calc.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.calculate_and_plot)
        
        left_layout.addWidget(group_inputs)
        left_layout.addWidget(self.btn_calc)
        left_layout.addWidget(group_results)
        left_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidget(left_panel)
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(400)
        
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
        
        self.last_gamma_ev = None
        self.last_gamma_jm2 = None

    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QFormLayout(self.local_widget)
        self.le_mat_name = QLineEdit("Malzeme Yüzeyi")
        layout.addRow("Malzeme Adı:", self.le_mat_name)
        
    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.last_gamma_ev is not None:
            self.plot_graph()
            
    def calculate_and_plot(self):
        e_slab = self.le_e_slab.value()
        e_bulk = self.le_e_bulk.value()
        n_slab = self.le_n_slab.value()
        n_bulk = self.le_n_bulk.value()
        area = self.le_area.value()
        
        try:
            energy_diff = e_slab - (n_slab / n_bulk) * e_bulk
            gamma_ev_A2 = energy_diff / (2.0 * area)
            
            gamma_jm2 = gamma_ev_A2 * 16.0217662
            
            self.last_gamma_ev = gamma_ev_A2
            self.last_gamma_jm2 = gamma_jm2
            
            self.lbl_result.setText(
                f"Yüzey Enerjisi:\n"
                f"{gamma_ev_A2:.4f} eV/Å²\n"
                f"{gamma_jm2:.4f} J/m²"
            )
            
            self.plot_graph()
            
        except Exception as e:
            self.lbl_result.setText("Hesaplama Hatası!")
            
    def plot_graph(self):
        if self.last_gamma_ev is None: return
        
        self.figure.clear()
        apply_global_style()
        ax = self.figure.add_subplot(111)
        
        bars = ['Yüzey Enerjisi\n(eV/Å²)', 'Yüzey Enerjisi\n(J/m²)']
        vals = [self.last_gamma_ev, self.last_gamma_jm2]
        
        ax.bar(bars, vals, color=['#e74c3c', '#2980b9'], width=0.4)
        ax.axhline(0, color='black', linewidth=1)
        
        for i, v in enumerate(vals):
            ax.text(i, v + (0.05 if v > 0 else -0.05), f"{v:.4f}", ha='center', va='bottom' if v > 0 else 'top')
            
        ax.set_ylabel("Enerji Değeri")
        ax.set_title(rf"{self.le_mat_name.text()} - Yüzey Enerjisi Analizi")
        
        self.figure.tight_layout()
        try:
            from utils.style_manager import apply_custom_axes_settings
            if hasattr(self, 'figure'):
                apply_custom_axes_settings(self.figure)
        except Exception as e:
            print(f'Error applying custom axes settings: {e}')
        self.canvas.draw()
