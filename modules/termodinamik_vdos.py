import sys
import numpy as np
import pandas as pd
from scipy.integrate import trapezoid
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QLineEdit, QFormLayout, QGroupBox, QDoubleSpinBox, 
    QSpinBox, QMessageBox, QComboBox, QScrollArea, QTextEdit
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from utils.style_manager import apply_global_style

class TermodinamikVDOSWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel (Inputs)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)
        
        # Data Input Group
        data_group = QGroupBox("Veri Yükleme")
        data_layout = QFormLayout()
        
        self.btn_load = QPushButton("VDOS.dat Yükle")
        self.btn_load.clicked.connect(self.load_data)
        self.lbl_file = QLabel("Dosya: Seçilmedi")
        
        self.inp_formula = QLineEdit("K_2TiH_5")
        self.inp_atoms = QSpinBox()
        self.inp_atoms.setValue(8)
        self.inp_atoms.setMinimum(1)
        
        self.inp_temp_max = QSpinBox()
        self.inp_temp_max.setRange(500, 4000)
        self.inp_temp_max.setValue(1500)
        self.inp_temp_max.setSingleStep(100)
        
        data_layout.addRow(self.btn_load, self.lbl_file)
        data_layout.addRow("Malzeme Formülü:", self.inp_formula)
        data_layout.addRow("Atom Sayısı:", self.inp_atoms)
        data_layout.addRow("Maksimum Sıcaklık (K):", self.inp_temp_max)
        data_group.setLayout(data_layout)
        
        # Calculate Button
        self.btn_calc = QPushButton("Hesapla ve Grafiği Hazırla")
        self.btn_calc.setEnabled(False)
        self.btn_calc.clicked.connect(self.calculate_and_plot)
        self.btn_calc.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        
        # Result Label
        self.lbl_result = QLabel("")
        self.lbl_result.setStyleSheet("color: blue; font-weight: bold;")
        
        # Add to left layout
        left_layout.addWidget(data_group)
        left_layout.addWidget(self.btn_calc)
        left_layout.addWidget(self.lbl_result)
        left_layout.addStretch()
        
        # Right Panel (Plot)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        # Add to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.df = None
        self.T_range = None
        self.Cv = None
        self.U_vib = None
        self.dp_limit = 0
        self.material_name = ""
        
        self.create_local_settings_widget()
        
        # Grafik ayarları değiştiğinde tetiklenir
        from utils.style_manager import notifier
        notifier.style_changed.connect(self.on_style_changed)

    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        c_layout = QFormLayout(content)
        
        self.ls_x_min = QDoubleSpinBox(); self.ls_x_min.setRange(0, 10000); self.ls_x_min.setValue(0)
        self.ls_x_max = QDoubleSpinBox(); self.ls_x_max.setRange(0, 10000); self.ls_x_max.setValue(1500)
        self.ls_x_step = QDoubleSpinBox(); self.ls_x_step.setRange(10, 2000); self.ls_x_step.setValue(300)
        c_layout.addRow("X Başlangıç (K):", self.ls_x_min)
        c_layout.addRow("X Bitiş (K):", self.ls_x_max)
        c_layout.addRow("X Aralık (Tick):", self.ls_x_step)
        
        self.ls_y1_min = QDoubleSpinBox(); self.ls_y1_min.setRange(-1000, 1000); self.ls_y1_min.setValue(0)
        self.ls_y1_max = QDoubleSpinBox(); self.ls_y1_max.setRange(-1000, 1000); self.ls_y1_max.setValue(300)
        self.ls_y2_min = QDoubleSpinBox(); self.ls_y2_min.setRange(-10, 10); self.ls_y2_min.setValue(0)
        self.ls_y2_max = QDoubleSpinBox(); self.ls_y2_max.setRange(-10, 10); self.ls_y2_max.setValue(2.0)
        c_layout.addRow("Y1 (Cv) Min:", self.ls_y1_min)
        c_layout.addRow("Y1 (Cv) Max:", self.ls_y1_max)
        c_layout.addRow("Y2 (U) Min:", self.ls_y2_min)
        c_layout.addRow("Y2 (U) Max:", self.ls_y2_max)
        
        self.ls_leg1 = QLineEdit("Heat Capacity ($C_v$)")
        self.ls_leg2 = QLineEdit("Vibrational Energy")
        self.ls_leg_loc = QComboBox()
        self.ls_leg_loc.addItems(["best", "upper left", "upper right", "lower left", "lower right", "center right"])
        self.ls_leg_loc.setCurrentText("center right")
        c_layout.addRow("Cv Çizgisi İsmi:", self.ls_leg1)
        c_layout.addRow("U_vib Çizgisi İsmi:", self.ls_leg2)
        c_layout.addRow("Lejant Konumu:", self.ls_leg_loc)
        
        self.ls_box_text = QLineEdit("D-P Limit: {:.2f}")
        self.ls_box_x = QDoubleSpinBox(); self.ls_box_x.setRange(0, 10000); self.ls_box_x.setValue(75)
        self.ls_box_y = QDoubleSpinBox(); self.ls_box_y.setRange(-1000, 1000); self.ls_box_y.setValue(105)
        c_layout.addRow("Kutu Metni:", self.ls_box_text)
        c_layout.addRow("Metin X Konumu:", self.ls_box_x)
        c_layout.addRow("Metin Y Konumu:", self.ls_box_y)
        
        btn_apply = QPushButton("Yerel Ayarları Uygula")
        btn_apply.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 10px;")
        btn_apply.clicked.connect(self.plot_graph)
        c_layout.addRow(btn_apply)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.df is not None and self.Cv is not None:
            apply_global_style()
            self.plot_graph(self.material_name)
            
    def load_data(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'VDOS Dosyası Aç', '', 'Data Files (*.dat *.txt);;All Files (*)')
        if fname:
            try:
                self.df = pd.read_csv(fname, sep=r'\s+', comment='#', names=['Freq', 'Int']).dropna()
                self.df = self.df[self.df['Freq'] > 0]
                self.lbl_file.setText(fname.split('/')[-1])
                self.btn_calc.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya okunurken hata oluştu:\n{str(e)}")
                
    def calculate_and_plot(self):
        if self.df is None:
            return
            
        try:
            apply_global_style()
            
            n_atoms = self.inp_atoms.value()
            temp_end = self.inp_temp_max.value()
            material_name = self.inp_formula.text()
            
            R = 8.31446
            h_eV = 4.13567e-15
            kB_eV = 8.61733e-5
            THz_to_Hz = 1e12
            
            freq = self.df['Freq'].values * THz_to_Hz
            dos = self.df['Int'].values
            scale = (3 * n_atoms) / trapezoid(dos, self.df['Freq'].values)
            self.T_range = np.linspace(0.1, temp_end, 500)
            
            cv_list, uvib_list = [], []
            
            for T in self.T_range:
                x = np.clip((h_eV * freq) / (kB_eV * T), None, 500)
                cv_val = (x**2 * np.exp(x)) / (np.exp(x) - 1)**2
                u_val = (h_eV * freq) / (np.exp(x) - 1)
                cv_list.append(scale * trapezoid(cv_val * dos, self.df['Freq'].values))
                uvib_list.append(scale * trapezoid(u_val * dos, self.df['Freq'].values))
                
            self.Cv = np.array(cv_list) * R
            self.U_vib = np.array(uvib_list)
            self.dp_limit = 3 * n_atoms * R
            self.material_name = material_name
            
            self.lbl_result.setText(f"Dulong-Petit Limiti: {self.dp_limit:.2f} J/mol·K")
            
            self.plot_graph(material_name)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Hesaplama sırasında hata:\n{str(e)}")
            
    def plot_graph(self, material_name=None):
        if self.Cv is None: return
        self.figure.clear()
        ax1 = self.figure.add_subplot(111)
        
        ax1.plot(self.T_range, self.Cv, color='red', lw=2.5, label=self.ls_leg1.text())
        
        # Limit çizgisi
        ax1.axhline(y=self.dp_limit, color='black', linestyle='--', lw=2.0)
        
        # İkinci Y ekseni
        ax2 = ax1.twinx()
        ax2.plot(self.T_range, self.U_vib, color='blue', lw=2.5, label=self.ls_leg2.text())

        # X ve Y Eksen Ayarları
        ax1.set_xlim(self.ls_x_min.value(), self.ls_x_max.value())
        ax1.set_ylim(self.ls_y1_min.value(), self.ls_y1_max.value())
        ax2.set_ylim(self.ls_y2_min.value(), self.ls_y2_max.value())

        # Major & Minor Ticks
        ax1.xaxis.set_major_locator(MultipleLocator(self.ls_x_step.value()))
        
        ax1.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax1.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax2.yaxis.set_minor_locator(AutoMinorLocator(2))

        # Etiketler ve Başlık
        ax1.set_xlabel('Temperature (K)', fontweight='bold', labelpad=10)
        ax1.set_ylabel(r'Heat Capacity $C_v$ (J mol$^{-1}$ K$^{-1}$)', fontweight='bold', labelpad=10)
        ax2.set_ylabel(r'Vibrational Energy (kJ mol$^{-1}$)', fontweight='bold', labelpad=10)
        
        # Lejant
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        leg = ax1.legend(lines1 + lines2, labels1 + labels2, loc=self.ls_leg_loc.currentText(), frameon=True, edgecolor='black')
        leg.get_frame().set_linewidth(1.2)
        leg.set_draggable(True)
        
        # Özel Metin
        box_text = self.ls_box_text.text()
        if "{:.2f}" in box_text:
            box_text = box_text.format(self.dp_limit)
            
        ax1.text(self.ls_box_x.value(), self.ls_box_y.value(), box_text, fontsize=12, fontweight='bold',
                 bbox=dict(facecolor='white', alpha=0.9, edgecolor='black', boxstyle='square,pad=0.5'))

        self.figure.suptitle(f'Thermodynamic Properties of ${self.material_name}$', fontweight='bold', y=0.98)
        
        self.figure.tight_layout()
        try:
            from utils.style_manager import apply_custom_axes_settings
            if hasattr(self, 'figure'):
                apply_custom_axes_settings(self.figure)
        except Exception as e:
            print(f'Error applying custom axes settings: {e}')
        self.canvas.draw()
