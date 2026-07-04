import numpy as np
import io
import re
from scipy.interpolate import Akima1DInterpolator
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QMessageBox, QDoubleSpinBox,
    QScrollArea, QLineEdit, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from utils.style_manager import apply_global_style, notifier

class ColorPickerWidget(QWidget):
    def __init__(self, color_hex, parent=None):
        super().__init__(parent)
        self.color = color_hex
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.btn = QPushButton()
        self.btn.setStyleSheet(f"background-color: {self.color}; border: 1px solid black;")
        self.btn.clicked.connect(self.choose_color)
        self.layout.addWidget(self.btn)
        
    def choose_color(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(QColor(self.color), self)
        if color.isValid():
            self.color = color.name()
            self.btn.setStyleSheet(f"background-color: {self.color}; border: 1px solid black;")

class NEBEnerjiBariyeriWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)
        
        # Input Data Group
        data_group = QGroupBox("İmaj Enerjileri (eV)")
        d_layout = QVBoxLayout()
        
        lbl_info = QLabel("Sırasıyla: IS, Img1, Img2... FS\nVirgülle veya alt alta ayırabilirsiniz.")
        lbl_info.setStyleSheet("color: #555; font-size: 12px;")
        d_layout.addWidget(lbl_info)
        
        self.te_energies = QTextEdit()
        self.te_energies.setPlainText("-331.831500\n-331.946800\n-332.021000\n-331.855100\n-331.961700\n-331.995000\n-331.967400")
        d_layout.addWidget(self.te_energies)
        
        data_group.setLayout(d_layout)
        
        self.btn_calc = QPushButton("Enerjileri Hesapla ve Çiz")
        self.btn_calc.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.process_data)
        
        # Metrics Display
        metrics_group = QGroupBox("Hesaplanan Metrikler")
        m_layout = QFormLayout()
        
        self.lbl_eaf = QLabel("-")
        self.lbl_eab = QLabel("-")
        self.lbl_delta = QLabel("-")
        
        m_layout.addRow("Aktivasyon Bariyeri ($E_{a,f}$):", self.lbl_eaf)
        m_layout.addRow("Ters Bariyer ($E_{a,b}$):", self.lbl_eab)
        m_layout.addRow("Reaksiyon Enerjisi (ΔE):", self.lbl_delta)
        metrics_group.setLayout(m_layout)
        
        left_layout.addWidget(data_group)
        left_layout.addWidget(self.btn_calc)
        left_layout.addWidget(metrics_group)
        left_layout.addStretch()
        
        # Right Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.figure = Figure(figsize=(10, 6.5))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.relative_energies = []
        self.x = []
        self.x_smooth = []
        self.y_smooth = []
        self.ts_index = 0
        self.metrics = {}
        
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)
        
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        c_layout = QFormLayout(content)
        
        self.ls_title = QLineEdit("Hydrogen Diffusion Energy Profile")
        c_layout.addRow("Grafik Başlığı:", self.ls_title)
        
        self.cp_curve = ColorPickerWidget("#000000")
        c_layout.addRow("Eğri (Curve) Rengi:", self.cp_curve)
        
        self.ls_y_min = QDoubleSpinBox(); self.ls_y_min.setRange(-50, 50); self.ls_y_min.setValue(-1.0); self.ls_y_min.setSingleStep(0.1)
        self.ls_y_max = QDoubleSpinBox(); self.ls_y_max.setRange(-50, 50); self.ls_y_max.setValue(1.0); self.ls_y_max.setSingleStep(0.1)
        self.ls_y_step = QDoubleSpinBox(); self.ls_y_step.setRange(0.01, 10); self.ls_y_step.setValue(0.1); self.ls_y_step.setSingleStep(0.05)
        
        c_layout.addRow("Y Min (eV):", self.ls_y_min)
        c_layout.addRow("Y Maks (eV):", self.ls_y_max)
        c_layout.addRow("Y Adımı:", self.ls_y_step)
        
        self.ls_box_x = QDoubleSpinBox(); self.ls_box_x.setRange(0, 1); self.ls_box_x.setValue(0.03); self.ls_box_x.setSingleStep(0.05)
        self.ls_box_y = QDoubleSpinBox(); self.ls_box_y.setRange(0, 1); self.ls_box_y.setValue(0.96); self.ls_box_y.setSingleStep(0.05)
        
        c_layout.addRow("Bilgi Kutusu X:", self.ls_box_x)
        c_layout.addRow("Bilgi Kutusu Y:", self.ls_box_y)
        
        self.ls_leg_loc = QComboBox()
        self.ls_leg_loc.addItems(["best", "upper right", "upper left", "lower left", "lower right", "center right"])
        self.ls_leg_loc.setCurrentText("upper right")
        c_layout.addRow("Lejant Konumu:", self.ls_leg_loc)
        
        btn_apply = QPushButton("Yerel Ayarları Uygula")
        btn_apply.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 10px;")
        btn_apply.clicked.connect(self.plot_graph)
        c_layout.addRow(btn_apply)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if len(self.relative_energies) > 0:
            apply_global_style()
            self.plot_graph()
            
    def process_data(self):
        raw_text = self.te_energies.toPlainText()
        raw_energies = re.split(r'[,\n]+', raw_text)
        
        try:
            energies = np.array([float(x.strip()) for x in raw_energies if x.strip()])
            if len(energies) < 3:
                QMessageBox.warning(self, "Eksik Veri", "En az 3 enerji değeri (IS, TS, FS) girmelisiniz!")
                return
                
            self.relative_energies = energies - energies[0]
            self.x = np.arange(len(energies))
            
            # Smart TS Logic
            self.ts_index = np.argmax(self.relative_energies[1:-1]) + 1
            min_before_ts = np.min(self.relative_energies[0:self.ts_index+1])
            min_after_ts = np.min(self.relative_energies[self.ts_index:])
            
            Ea_f = self.relative_energies[self.ts_index] - min_before_ts
            Ea_b = self.relative_energies[self.ts_index] - min_after_ts
            Delta_E = self.relative_energies[-1] - self.relative_energies[0]
            
            self.metrics = {"Ea_f": Ea_f, "Ea_b": Ea_b, "Delta_E": Delta_E}
            
            self.lbl_eaf.setText(f"{Ea_f:.4f} eV")
            self.lbl_eab.setText(f"{Ea_b:.4f} eV")
            self.lbl_delta.setText(f"{Delta_E:.4f} eV")
            
            self.x_smooth = np.linspace(self.x.min(), self.x.max(), 500)
            spl = Akima1DInterpolator(self.x, self.relative_energies) 
            self.y_smooth = spl(self.x_smooth)
            
            auto_y_max = float(np.ceil((max(self.relative_energies) + 0.1) * 10) / 10) 
            auto_y_min = float(np.floor((min(self.relative_energies) - 0.1) * 10) / 10)
            if auto_y_max < 0.2: auto_y_max = 0.2
            
            self.ls_y_min.setValue(auto_y_min)
            self.ls_y_max.setValue(auto_y_max)
            
            apply_global_style()
            self.plot_graph()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Enerji verileri ayrıştırılırken hata oluştu:\n{e}")

    def plot_graph(self):
        if len(self.relative_energies) == 0: return
        
        self.figure.clear()
        
        import matplotlib as mpl
        mpl.rcParams['font.family'] = 'serif'
        mpl.rcParams['font.serif'] = ['Times New Roman']
        mpl.rcParams['mathtext.fontset'] = 'custom'
        mpl.rcParams['mathtext.rm'] = 'Times New Roman'
        mpl.rcParams['mathtext.it'] = 'Times New Roman:italic'
        mpl.rcParams['mathtext.bf'] = 'Times New Roman:bold'
        
        ax = self.figure.add_subplot(111)
        
        ax.axhline(0, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, zorder=0)
        
        ax.plot(self.x_smooth, self.y_smooth, color=self.cp_curve.color, linewidth=3.0, zorder=1)
        ax.scatter(self.x, self.relative_energies, color='white', edgecolor='black', s=80, linewidth=2.0, zorder=2)
        
        ax.scatter(0, self.relative_energies[0], color='#2980b9', s=160, marker='s', label='Initial State (IS)', zorder=3)
        ax.scatter(self.ts_index, self.relative_energies[self.ts_index], color='#e74c3c', s=160, marker='s', label='Transition State (TS)', zorder=3)
        ax.scatter(len(self.relative_energies)-1, self.relative_energies[-1], color='#27ae60', s=160, marker='s', label='Final State (FS)', zorder=3)
        
        ax.set_ylim(self.ls_y_min.value(), self.ls_y_max.value())
        ax.set_xlim(-0.4, len(self.relative_energies) - 0.6)
        
        ax.yaxis.set_major_locator(MultipleLocator(self.ls_y_step.value()))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.tick_params(axis='both', which='major', direction='in', length=8, width=2.0, labelsize=14)
        ax.tick_params(axis='y', which='minor', direction='in', length=4, width=1.5)
        
        for spine in ax.spines.values():
            spine.set_linewidth(2.0)
            spine.set_edgecolor('black')
            
        ax.set_xlabel('Reaction Coordinate', fontsize=16, fontweight='bold', labelpad=12)
        ax.set_ylabel('Relative Energy (eV)', fontsize=16, fontweight='bold', labelpad=12)
        
        labels = ['IS' if i==0 else 'FS' if i==len(self.relative_energies)-1 else 'TS' if i==self.ts_index else f'Img {i}' for i in range(len(self.relative_energies))]
        ax.set_xticks(self.x)
        ax.set_xticklabels(labels, fontsize=14, fontweight='bold')
        
        info_box = (
            f"Kinetic Barrier ($E_a$): {self.metrics['Ea_f']:.4f} eV\n"
            f"Reverse Barrier: {self.metrics['Ea_b']:.4f} eV\n"
            f"Thermodynamic $\\Delta E$: {self.metrics['Delta_E']:.4f} eV"
        )
        ax.text(self.ls_box_x.value(), self.ls_box_y.value(), info_box, transform=ax.transAxes, 
                fontsize=13, fontweight='bold', verticalalignment='top',
                bbox=dict(boxstyle='square,pad=0.5', facecolor='white', edgecolor='black', linewidth=1.5))
                
        leg = ax.legend(loc=self.ls_leg_loc.currentText(), fontsize=13, frameon=True, edgecolor='black', fancybox=False, shadow=False)
        leg.get_frame().set_linewidth(1.5)
        leg.set_draggable(True)
        
        title = self.ls_title.text()
        if title.strip():
            ax.set_title(title, fontsize=18, fontweight='bold', pad=15)
            
        self.figure.tight_layout()
        try:
            from utils.style_manager import apply_custom_axes_settings
            if hasattr(self, 'figure'):
                apply_custom_axes_settings(self.figure)
        except Exception as e:
            print(f'Error applying custom axes settings: {e}')
        self.canvas.draw()
