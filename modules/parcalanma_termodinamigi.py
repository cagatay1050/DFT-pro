import pandas as pd
import numpy as np
from scipy.integrate import trapezoid
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QFormLayout, QGroupBox, QMessageBox, QDoubleSpinBox,
    QScrollArea, QLineEdit, QComboBox, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from utils.style_manager import apply_global_style, notifier

class ParcalanmaTermodinamigiWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel (Inputs)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        c_layout = QVBoxLayout(content)
        
        # 1. Girdi Verileri
        group1 = QGroupBox("1. Girdi Verileri (DFT & VDOS)")
        g1_layout = QFormLayout()
        self.le_mat = QLineEdit(r"\mathbf{K_2TiH_5}")
        self.btn_vdos = QPushButton("Ana Malzeme VDOS Yükle")
        self.lbl_vdos = QLabel("❌")
        self.btn_vdos.clicked.connect(self.load_vdos)
        
        g1_layout.addRow("Formül:", self.le_mat)
        g1_layout.addRow(self.btn_vdos, self.lbl_vdos)
        
        self.e_k2tih5 = QDoubleSpinBox(); self.e_k2tih5.setRange(-1000, 1000); self.e_k2tih5.setValue(-28.549848); self.e_k2tih5.setDecimals(6)
        self.e_h2 = QDoubleSpinBox(); self.e_h2.setRange(-100, 100); self.e_h2.setValue(-6.7719); self.e_h2.setDecimals(6)
        self.e_k = QDoubleSpinBox(); self.e_k.setRange(-100, 100); self.e_k.setValue(-1.0497); self.e_k.setDecimals(6)
        self.e_ti = QDoubleSpinBox(); self.e_ti.setRange(-100, 100); self.e_ti.setValue(-7.8405); self.e_ti.setDecimals(6)
        self.e_kh = QDoubleSpinBox(); self.e_kh.setRange(-100, 100); self.e_kh.setValue(-4.830159); self.e_kh.setDecimals(6)
        self.e_tih2 = QDoubleSpinBox(); self.e_tih2.setRange(-100, 100); self.e_tih2.setValue(-16.773732); self.e_tih2.setDecimals(6)
        
        g1_layout.addRow("E(Ana Malzeme):", self.e_k2tih5)
        g1_layout.addRow("E(H2):", self.e_h2)
        g1_layout.addRow("E(K):", self.e_k)
        g1_layout.addRow("E(Ti):", self.e_ti)
        g1_layout.addRow("E(KH) per formula:", self.e_kh)
        g1_layout.addRow("E(TiH2) per formula:", self.e_tih2)
        
        self.s_k = QDoubleSpinBox(); self.s_k.setRange(0, 1000); self.s_k.setValue(64.7)
        self.s_ti = QDoubleSpinBox(); self.s_ti.setRange(0, 1000); self.s_ti.setValue(30.7)
        self.s_kh = QDoubleSpinBox(); self.s_kh.setRange(0, 1000); self.s_kh.setValue(50.2)
        self.s_tih2 = QDoubleSpinBox(); self.s_tih2.setRange(0, 1000); self.s_tih2.setValue(30.0)
        
        g1_layout.addRow("S(K):", self.s_k)
        g1_layout.addRow("S(Ti):", self.s_ti)
        g1_layout.addRow("S(KH):", self.s_kh)
        g1_layout.addRow("S(TiH2):", self.s_tih2)
        group1.setLayout(g1_layout)
        
        # 2. Reaksiyon Yolu
        group2 = QGroupBox("2. Reaksiyon Yolu Seçimi")
        g2_layout = QVBoxLayout()
        self.cb_elem = QCheckBox(r"Elemental: 2K + Ti + 2.5H2")
        self.cb_tih2 = QCheckBox(r"Only TiH2: 2K + TiH2 + 1.5H2")
        self.cb_kh = QCheckBox(r"Only KH: 2KH + Ti + 1.5H2")
        self.cb_bin = QCheckBox(r"Binary Hydrides: 2KH + TiH2 + 0.5H2")
        self.cb_elem.setChecked(True)
        self.cb_tih2.setChecked(True)
        self.cb_kh.setChecked(True)
        self.cb_bin.setChecked(True)
        
        self.sp_tmax = QSpinBox()
        self.sp_tmax.setRange(500, 3000)
        self.sp_tmax.setValue(1500)
        self.sp_tmax.setSingleStep(100)
        
        g2_layout.addWidget(self.cb_elem)
        g2_layout.addWidget(self.cb_tih2)
        g2_layout.addWidget(self.cb_kh)
        g2_layout.addWidget(self.cb_bin)
        
        hl = QHBoxLayout()
        hl.addWidget(QLabel("Maks Sıcaklık (K):"))
        hl.addWidget(self.sp_tmax)
        g2_layout.addLayout(hl)
        group2.setLayout(g2_layout)
        
        c_layout.addWidget(group1)
        c_layout.addWidget(group2)
        scroll.setWidget(content)
        
        self.btn_calc = QPushButton("Termodinamik Verileri Hesapla")
        self.btn_calc.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.process_data)
        
        left_layout.addWidget(scroll)
        left_layout.addWidget(self.btn_calc)
        
        # Right Panel (Plot)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.figure = Figure(figsize=(10, 7))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.vdos_path = ""
        self.results = {}
        self.T_range = None
        self.y_min_g = 0
        self.y_max_g = 0
        
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)
        
    def load_vdos(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'VDOS Aç', '', 'Data (*.dat *.txt);;All (*)')
        if fname:
            self.vdos_path = fname
            self.lbl_vdos.setText("✅")
            
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        c_layout = QFormLayout(content)
        
        self.ls_x_min = QDoubleSpinBox(); self.ls_x_min.setRange(0, 3000); self.ls_x_min.setValue(0); self.ls_x_min.setSingleStep(100)
        self.ls_x_max = QDoubleSpinBox(); self.ls_x_max.setRange(0, 3000); self.ls_x_max.setValue(1500); self.ls_x_max.setSingleStep(100)
        self.ls_x_step = QDoubleSpinBox(); self.ls_x_step.setRange(10, 1000); self.ls_x_step.setValue(200); self.ls_x_step.setSingleStep(100)
        
        self.ls_y_min = QDoubleSpinBox(); self.ls_y_min.setRange(-100, 100); self.ls_y_min.setValue(-2); self.ls_y_min.setSingleStep(0.5)
        self.ls_y_max = QDoubleSpinBox(); self.ls_y_max.setRange(-100, 100); self.ls_y_max.setValue(2); self.ls_y_max.setSingleStep(0.5)
        self.ls_y_step = QDoubleSpinBox(); self.ls_y_step.setRange(0.1, 10); self.ls_y_step.setValue(0.5); self.ls_y_step.setSingleStep(0.1)
        
        c_layout.addRow("X Başlangıç:", self.ls_x_min)
        c_layout.addRow("X Bitiş:", self.ls_x_max)
        c_layout.addRow("X Aralık:", self.ls_x_step)
        c_layout.addRow("Y Başlangıç:", self.ls_y_min)
        c_layout.addRow("Y Bitiş:", self.ls_y_max)
        c_layout.addRow("Y Aralık:", self.ls_y_step)
        
        self.ls_leg_loc = QComboBox()
        self.ls_leg_loc.addItems(["best", "upper right", "upper left", "center right", "lower right", "lower left"])
        self.ls_leg_loc.setCurrentText("upper right")
        c_layout.addRow("Lejant Konumu:", self.ls_leg_loc)
        
        self.ls_arrow_sp = QDoubleSpinBox()
        self.ls_arrow_sp.setRange(0, 2)
        self.ls_arrow_sp.setValue(0.25)
        self.ls_arrow_sp.setSingleStep(0.05)
        c_layout.addRow("Ok Dikey Aralık:", self.ls_arrow_sp)
        
        btn_apply = QPushButton("Yerel Ayarları Uygula")
        btn_apply.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 10px;")
        btn_apply.clicked.connect(self.plot_graph)
        c_layout.addRow(btn_apply)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.results:
            apply_global_style()
            self.plot_graph()
            
    def process_data(self):
        if not self.vdos_path:
            QMessageBox.warning(self, "Hata", "Lütfen ana malzeme VDOS dosyasını yükleyin!")
            return
            
        try:
            apply_global_style()
            
            df = pd.read_csv(self.vdos_path, sep=r'\s+', comment='#', names=['Freq', 'Int']).dropna()
            df = df[df['Freq'] > 0]
            
            freq = df['Freq'].values * 1e12  
            dos = df['Int'].values
            scale = (3 * 8) / trapezoid(dos, df['Freq'].values)
            
            zpe_k2tih5 = scale * trapezoid(0.5 * 4.13567e-15 * freq * dos, df['Freq'].values)
            
            calc_t_max = self.sp_tmax.value()
            self.T_range = np.linspace(1, calc_t_max, 300)
            kB = 8.61733e-5
            
            s_K2TiH5_T = []
            for T in self.T_range:
                x = (4.13567e-15 * freq) / (kB * T)
                s_val = kB * (x / (np.exp(x) - 1) - np.log(1 - np.exp(-x)))
                s_K2TiH5_T.append(scale * trapezoid(s_val * dos, df['Freq'].values))
            s_K2TiH5_T = np.array(s_K2TiH5_T)
            
            s_h2_T = (130.68 / 96485) + (28.8 / 96485) * np.log(self.T_range / 298.15)
            
            all_pathways = {
                "Elemental": {
                    "label": r"2K + Ti + 2.5H$_2$", "h2_coeff": 2.5,
                    "solid_products": [{"coeff": 2, "E": self.e_k.value(), "S": self.s_k.value()}, {"coeff": 1, "E": self.e_ti.value(), "S": self.s_ti.value()}],
                    "color": "#d62728", "linestyle": "-"
                },
                "Only_TiH2": {
                    "label": r"2K + TiH$_2$ + 1.5H$_2$", "h2_coeff": 1.5,
                    "solid_products": [{"coeff": 2, "E": self.e_k.value(), "S": self.s_k.value()}, {"coeff": 1, "E": self.e_tih2.value(), "S": self.s_tih2.value()}],
                    "color": "#ff7f0e", "linestyle": "--"
                },
                "Only_KH": {
                    "label": r"2KH + Ti + 1.5H$_2$", "h2_coeff": 1.5,
                    "solid_products": [{"coeff": 2, "E": self.e_kh.value(), "S": self.s_kh.value()}, {"coeff": 1, "E": self.e_ti.value(), "S": self.s_ti.value()}],
                    "color": "#2ca02c", "linestyle": "-."
                },
                "Binary_Hydrides": {
                    "label": r"2KH + TiH$_2$ + 0.5H$_2$", "h2_coeff": 0.5,
                    "solid_products": [{"coeff": 2, "E": self.e_kh.value(), "S": self.s_kh.value()}, {"coeff": 1, "E": self.e_tih2.value(), "S": self.s_tih2.value()}],
                    "color": "#1f77b4", "linestyle": ":"
                }
            }
            
            active_pathways = {}
            if self.cb_elem.isChecked(): active_pathways["Elemental"] = all_pathways["Elemental"]
            if self.cb_tih2.isChecked(): active_pathways["Only_TiH2"] = all_pathways["Only_TiH2"]
            if self.cb_kh.isChecked(): active_pathways["Only_KH"] = all_pathways["Only_KH"]
            if self.cb_bin.isChecked(): active_pathways["Binary_Hydrides"] = all_pathways["Binary_Hydrides"]
            
            if not active_pathways:
                QMessageBox.warning(self, "Uyarı", "En az bir yol seçmelisiniz!")
                return
                
            self.results = {}
            self.y_min_g, self.y_max_g = 999, -999
            
            for key, path in active_pathways.items():
                E_products_solid = sum(p['coeff'] * p['E'] for p in path['solid_products'])
                delta_E_dft = (E_products_solid + path['h2_coeff'] * self.e_h2.value()) - self.e_k2tih5.value()
                
                delta_zpe = (path['h2_coeff'] * 0.273) - zpe_k2tih5
                delta_h_0 = delta_E_dft + delta_zpe
                
                S_products_solid_eV = sum(p['coeff'] * p['S'] for p in path['solid_products']) / 96485
                delta_s_T = (path['h2_coeff'] * s_h2_T) + S_products_solid_eV - s_K2TiH5_T
                
                delta_g_T = delta_h_0 - self.T_range * delta_s_T
                
                self.y_min_g = min(self.y_min_g, min(delta_g_T))
                self.y_max_g = max(self.y_max_g, max(delta_g_T))
                
                T_des = None
                zero_crossings = np.where(np.diff(np.sign(delta_g_T)))[0]
                if len(zero_crossings) > 0 and delta_g_T[0] > 0:
                    idx = zero_crossings[0]
                    T1, T2 = self.T_range[idx], self.T_range[idx+1]
                    G1, G2 = delta_g_T[idx], delta_g_T[idx+1]
                    T_des = T1 - G1 * (T2 - T1) / (G2 - G1)
                    
                self.results[key] = {
                    "label": path["label"], "color": path["color"], "linestyle": path["linestyle"],
                    "delta_g": delta_g_T, "T_des": T_des
                }
                
            y_pad = (self.y_max_g - self.y_min_g) * 0.1
            self.ls_y_min.setValue(float(np.floor((self.y_min_g - y_pad) * 10) / 10))
            self.ls_y_max.setValue(float(np.ceil((self.y_max_g + y_pad) * 10) / 10))
            self.ls_x_max.setValue(float(calc_t_max))
            
            self.plot_graph()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Hesaplama hatası:\n{e}")
            
    def plot_graph(self):
        if not self.results: return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        for idx, (key, path) in enumerate(self.results.items()):
            ax.plot(self.T_range, path["delta_g"], label=path['label'], color=path['color'], 
                    linestyle=path['linestyle'], linewidth=3.0)
            
            T_des = path["T_des"]
            if T_des is not None and self.ls_x_min.value() <= T_des <= self.ls_x_max.value():
                ax.plot(T_des, 0, 'ko', markersize=8, markerfacecolor=path['color'], zorder=5)
                
                y_offset = self.ls_arrow_sp.value() * (idx + 1)
                
                ax.annotate(rf'$\mathbf{{T_{{des}}}}$ = {T_des:.1f} K', 
                             xy=(T_des, 0), xytext=(T_des + (self.ls_x_max.value()*0.02), y_offset),
                             color=path['color'], fontsize=14, fontweight='bold',
                             arrowprops=dict(facecolor=path['color'], edgecolor=path['color'], arrowstyle='->', lw=2.5))
                             
        ax.axhline(0, color='black', linestyle='-', linewidth=1.5, zorder=1)
        
        ax.set_xlim(self.ls_x_min.value(), self.ls_x_max.value())
        ax.set_ylim(self.ls_y_min.value(), self.ls_y_max.value())
        
        ax.xaxis.set_major_locator(MultipleLocator(self.ls_x_step.value()))
        ax.yaxis.set_major_locator(MultipleLocator(self.ls_y_step.value()))
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        
        ax.set_xlabel("Temperature (K)", fontsize=18, fontweight='bold', color='black', labelpad=12)
        ax.set_ylabel(r"$\boldsymbol{\Delta}\mathbf{G}$ (eV)", fontsize=18, fontweight='bold', color='black', labelpad=12)
        
        baslik_yol = "Decomposition" if len(self.results) == 1 else "Decomposition Pathways"
        mat_baslik = self.le_mat.text()
        ax.set_title(rf"Thermodynamic {baslik_yol} of ${mat_baslik}$", fontsize=18, fontweight='bold', color='black', pad=20)
        
        leg = ax.legend(loc=self.ls_leg_loc.currentText(), framealpha=0.9)
        leg.set_draggable(True)
        
        self.figure.tight_layout()
        try:
            from utils.style_manager import apply_custom_axes_settings
            if hasattr(self, 'figure'):
                apply_custom_axes_settings(self.figure)
        except Exception as e:
            print(f'Error applying custom axes settings: {e}')
        self.canvas.draw()
