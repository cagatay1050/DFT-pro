import numpy as np
from scipy import stats
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QFormLayout, QGroupBox, QMessageBox, QDoubleSpinBox,
    QScrollArea, QComboBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from utils.style_manager import apply_global_style, notifier

class DifuzyonArrheniusWidget(QWidget):
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
        data_group = QGroupBox("Veri Girişi")
        data_layout = QFormLayout()
        
        self.inp_formula = QLineEdit("K_2TiH_5")
        self.inp_temp = QLineEdit("300, 450, 600, 750")
        self.inp_diff = QLineEdit("2.69e-06, 5.59e-06, 7.53e-06, 1.80e-05")
        
        data_layout.addRow("Malzeme Formülü:", self.inp_formula)
        data_layout.addRow("Sıcaklıklar T (K)\n(Virgülle Ayırın):", self.inp_temp)
        data_layout.addRow("Difüzyon D (cm²/s)\n(Virgülle Ayırın):", self.inp_diff)
        data_group.setLayout(data_layout)
        
        # Calculate Button
        self.btn_calc = QPushButton("Hesapla ve Grafiği Hazırla")
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
        
        # Data state
        self.inv_T = None
        self.ln_D = None
        self.slope = 0
        self.intercept = 0
        self.Ea_eV = 0
        self.Ea_kJ = 0
        self.R2 = 0
        self.material_name = ""
        
        self.create_local_settings_widget()
        
        # Listen for style changes
        notifier.style_changed.connect(self.on_style_changed)
        
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        c_layout = QFormLayout(content)
        
        self.ls_x_min = QDoubleSpinBox(); self.ls_x_min.setRange(0, 100); self.ls_x_min.setValue(1.0); self.ls_x_min.setSingleStep(0.5)
        self.ls_x_max = QDoubleSpinBox(); self.ls_x_max.setRange(0, 100); self.ls_x_max.setValue(4.0); self.ls_x_max.setSingleStep(0.5)
        self.ls_x_step = QDoubleSpinBox(); self.ls_x_step.setRange(0.1, 10); self.ls_x_step.setValue(0.5); self.ls_x_step.setSingleStep(0.1)
        c_layout.addRow("X Başlangıç (1000/T):", self.ls_x_min)
        c_layout.addRow("X Bitiş (1000/T):", self.ls_x_max)
        c_layout.addRow("X Aralık (Tick):", self.ls_x_step)
        
        self.ls_y_min = QDoubleSpinBox(); self.ls_y_min.setRange(-100, 100); self.ls_y_min.setValue(-14.0); self.ls_y_min.setSingleStep(1.0)
        self.ls_y_max = QDoubleSpinBox(); self.ls_y_max.setRange(-100, 100); self.ls_y_max.setValue(-10.0); self.ls_y_max.setSingleStep(1.0)
        self.ls_y_step = QDoubleSpinBox(); self.ls_y_step.setRange(0.1, 10); self.ls_y_step.setValue(1.0); self.ls_y_step.setSingleStep(0.5)
        c_layout.addRow("Y Min (lnD):", self.ls_y_min)
        c_layout.addRow("Y Max (lnD):", self.ls_y_max)
        c_layout.addRow("Y Aralık (Tick):", self.ls_y_step)
        
        self.ls_leg1 = QLineEdit("Data")
        self.ls_leg2 = QLineEdit("Linear Fit")
        self.ls_leg_loc = QComboBox()
        self.ls_leg_loc.addItems(["best", "upper left", "upper right", "lower left", "lower right", "center right"])
        self.ls_leg_loc.setCurrentText("upper right")
        c_layout.addRow("Veri İsmi:", self.ls_leg1)
        c_layout.addRow("Fit Çizgisi İsmi:", self.ls_leg2)
        c_layout.addRow("Lejant Konumu:", self.ls_leg_loc)
        
        self.ls_box_x = QDoubleSpinBox(); self.ls_box_x.setRange(0, 1.0); self.ls_box_x.setValue(0.05); self.ls_box_x.setSingleStep(0.05)
        self.ls_box_y = QDoubleSpinBox(); self.ls_box_y.setRange(0, 1.0); self.ls_box_y.setValue(0.05); self.ls_box_y.setSingleStep(0.05)
        c_layout.addRow("Kutu X Konumu:", self.ls_box_x)
        c_layout.addRow("Kutu Y Konumu:", self.ls_box_y)
        
        btn_apply = QPushButton("Yerel Ayarları Uygula")
        btn_apply.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 10px;")
        btn_apply.clicked.connect(self.plot_graph)
        c_layout.addRow(btn_apply)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.inv_T is not None:
            apply_global_style()
            self.plot_graph()
            
    def calculate_and_plot(self):
        try:
            apply_global_style()
            self.material_name = self.inp_formula.text()
            
            # Parse inputs
            temperatures = np.array([float(x.strip()) for x in self.inp_temp.text().split(',')])
            diffusion_coeffs = np.array([float(x.strip()) for x in self.inp_diff.text().split(',')])
            
            if len(temperatures) != len(diffusion_coeffs):
                QMessageBox.critical(self, "Hata", "Sıcaklık ve difüzyon katsayısı sayıları birbirine eşit olmalıdır!")
                return
                
            kB = 8.617333262e-5  
            self.inv_T = 1000 / temperatures
            self.ln_D = np.log(diffusion_coeffs)

            slope, intercept, r_value, p_value, std_err = stats.linregress(1/temperatures, self.ln_D)
            self.slope = slope
            self.intercept = intercept
            self.Ea_eV = -slope * kB            
            self.Ea_kJ = self.Ea_eV * 96.485        
            self.R2 = r_value**2
            
            self.lbl_result.setText(f"✅ Hesaplama Başarılı!\nAktivasyon Enerjisi: {self.Ea_eV:.3f} eV")
            
            self.plot_graph()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bir hata oluştu. Veri formatınızı kontrol edin:\n{str(e)}")
            
    def plot_graph(self):
        if self.inv_T is None: return
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Veri Noktaları ve Fit Çizgisi
        ax.scatter(self.inv_T, self.ln_D, color='red', s=120, edgecolor='black', zorder=5, label=self.ls_leg1.text())
        
        x_fit_plot = np.linspace(self.ls_x_min.value(), self.ls_x_max.value(), 100)
        y_fit_plot = self.intercept + self.slope * (x_fit_plot / 1000)
        ax.plot(x_fit_plot, y_fit_plot, color='blue', lw=2.5, ls='--', label=self.ls_leg2.text())

        # X ve Y Eksen Ayarları
        ax.set_xlim(self.ls_x_min.value(), self.ls_x_max.value())
        ax.set_ylim(self.ls_y_min.value(), self.ls_y_max.value())
        ax.xaxis.set_major_locator(MultipleLocator(self.ls_x_step.value()))
        ax.yaxis.set_major_locator(MultipleLocator(self.ls_y_step.value()))
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

        # Etiketler ve Başlık
        ax.set_xlabel(r'1000 / T (K$^{-1}$)', fontweight='bold', labelpad=10)
        ax.set_ylabel(r'ln(D / cm$^{2}$s$^{-1}$)', fontweight='bold', labelpad=10)
        ax.set_title(rf'Arrhenius Plot for Hydrogen Diffusion in ${self.material_name}$', fontweight='bold', pad=15)

        # Özel Metin Kutusu (Ea ve R2)
        box_text = f"$E_a = {self.Ea_eV:.3f}$ eV\n$E_a = {self.Ea_kJ:.2f}$ kJ/mol\n$R^2 = {self.R2:.4f}$"
        ax.text(self.ls_box_x.value(), self.ls_box_y.value(), box_text, transform=ax.transAxes, fontsize=12, fontweight='bold',
                bbox=dict(facecolor='white', alpha=0.9, edgecolor='black', boxstyle='round,pad=0.6'))

        # Lejant
        leg = ax.legend(frameon=True, edgecolor='black', loc=self.ls_leg_loc.currentText())
        leg.get_frame().set_linewidth(1.2)
        leg.set_draggable(True)
        
        self.figure.tight_layout()
        try:
            from utils.style_manager import apply_custom_axes_settings
            if hasattr(self, 'figure'):
                apply_custom_axes_settings(self.figure)
        except Exception as e:
            print(f'Error applying custom axes settings: {e}')
        self.canvas.draw()
