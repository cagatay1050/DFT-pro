import numpy as np
import io
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QFormLayout, QGroupBox, QMessageBox, QDoubleSpinBox,
    QScrollArea, QLineEdit, QComboBox, QSpinBox, QCheckBox, QSlider
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from utils.style_manager import apply_global_style, notifier

# Helper widget for color picker
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

class ElektronikBandWidget(QWidget):
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
        d_layout = QFormLayout()
        
        self.cb_spin = QCheckBox("Manyetik / Spin-Polarize (ISPIN=2)?")
        d_layout.addRow(self.cb_spin)
        
        self.btn_band = QPushButton("1. BAND.dat Yükle")
        self.btn_band.clicked.connect(lambda: self.load_file("band"))
        self.lbl_band = QLabel("❌")
        
        self.btn_klabels = QPushButton("2. KLABELS Yükle")
        self.btn_klabels.clicked.connect(lambda: self.load_file("klabels"))
        self.lbl_klabels = QLabel("❌")
        
        self.btn_gap = QPushButton("3. BAND_GAP Yükle")
        self.btn_gap.clicked.connect(lambda: self.load_file("gap"))
        self.lbl_gap = QLabel("❌")
        
        d_layout.addRow(self.btn_band, self.lbl_band)
        d_layout.addRow(self.btn_klabels, self.lbl_klabels)
        d_layout.addRow(self.btn_gap, self.lbl_gap)
        
        data_group.setLayout(d_layout)
        
        self.btn_calc = QPushButton("Verileri Oku ve Grafiği Hazırla")
        self.btn_calc.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.process_data)
        
        left_layout.addWidget(data_group)
        left_layout.addWidget(self.btn_calc)
        left_layout.addStretch()
        
        # Right Panel (Plot)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.files = {"band": "", "klabels": "", "gap": ""}
        self.band_data_up = {}
        self.band_data_dn = {}
        self.k_coords = []
        self.k_labels = []
        self.band_gap = 0.0
        self.vbm_x = []
        self.vbm_y = []
        self.cbm_x = []
        self.cbm_y = []
        
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)
        
    def load_file(self, key):
        fname, _ = QFileDialog.getOpenFileName(self, 'Dosya Seç', '', 'Tüm Dosyalar (*)')
        if fname:
            self.files[key] = fname
            if key == "band": self.lbl_band.setText("✅")
            elif key == "klabels": self.lbl_klabels.setText("✅")
            elif key == "gap": self.lbl_gap.setText("✅")
            
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        c_layout = QFormLayout(content)
        
        self.ls_y_min = QDoubleSpinBox(); self.ls_y_min.setRange(-50, 50); self.ls_y_min.setValue(-5.0); self.ls_y_min.setSingleStep(1)
        self.ls_y_max = QDoubleSpinBox(); self.ls_y_max.setRange(-50, 50); self.ls_y_max.setValue(5.0); self.ls_y_max.setSingleStep(1)
        self.ls_y_step = QDoubleSpinBox(); self.ls_y_step.setRange(0.1, 50); self.ls_y_step.setValue(2.0); self.ls_y_step.setSingleStep(0.5)
        
        c_layout.addRow("Y Min (eV):", self.ls_y_min)
        c_layout.addRow("Y Maks (eV):", self.ls_y_max)
        c_layout.addRow("Y Adımı:", self.ls_y_step)
        
        self.cp_band = ColorPickerWidget("#000000")
        self.cp_up = ColorPickerWidget("#E74C3C")
        self.cp_dn = ColorPickerWidget("#2980B9")
        self.cp_fill = ColorPickerWidget("#2ecc71")
        self.cp_fermi = ColorPickerWidget("#FF0000")
        
        c_layout.addRow("Bant Çizgisi:", self.cp_band)
        c_layout.addRow("Spin UP Rengi:", self.cp_up)
        c_layout.addRow("Spin DOWN Rengi:", self.cp_dn)
        c_layout.addRow("Band Gap Boyası:", self.cp_fill)
        c_layout.addRow("Fermi Çizgisi:", self.cp_fermi)
        
        self.ls_k_alpha = QDoubleSpinBox(); self.ls_k_alpha.setRange(0, 1); self.ls_k_alpha.setValue(0.4); self.ls_k_alpha.setSingleStep(0.1)
        c_layout.addRow("K-Çizgi Görünürlüğü:", self.ls_k_alpha)
        
        self.ls_show_fill = QCheckBox("Band Arası Boyamayı Göster")
        self.ls_show_fill.setChecked(True)
        self.ls_show_text = QCheckBox("Band Gap Metnini Göster")
        self.ls_show_text.setChecked(True)
        
        c_layout.addRow(self.ls_show_fill)
        c_layout.addRow(self.ls_show_text)
        
        self.ls_pad = QSpinBox(); self.ls_pad.setRange(0, 50); self.ls_pad.setValue(15)
        c_layout.addRow("X Yazı Mesafesi:", self.ls_pad)
        
        self.ls_panel = QLineEdit("(a)")
        c_layout.addRow("Panel Etiketi:", self.ls_panel)
        
        self.ls_text_x = QDoubleSpinBox(); self.ls_text_x.setRange(0, 100); self.ls_text_x.setValue(0); self.ls_text_x.setSingleStep(0.5)
        self.ls_text_y = QDoubleSpinBox(); self.ls_text_y.setRange(-20, 20); self.ls_text_y.setValue(0); self.ls_text_y.setSingleStep(0.5)
        c_layout.addRow("Gap Metni X:", self.ls_text_x)
        c_layout.addRow("Gap Metni Y:", self.ls_text_y)
        
        self.ls_custom = QLineEdit("")
        self.ls_custom_x = QDoubleSpinBox(); self.ls_custom_x.setRange(0, 100); self.ls_custom_x.setValue(0); self.ls_custom_x.setSingleStep(0.5)
        self.ls_custom_y = QDoubleSpinBox(); self.ls_custom_y.setRange(-20, 20); self.ls_custom_y.setValue(0); self.ls_custom_y.setSingleStep(0.5)
        
        c_layout.addRow("Özel Metin:", self.ls_custom)
        c_layout.addRow("Özel Metin X:", self.ls_custom_x)
        c_layout.addRow("Özel Metin Y:", self.ls_custom_y)
        
        btn_apply = QPushButton("Yerel Ayarları Uygula")
        btn_apply.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 10px;")
        btn_apply.clicked.connect(self.plot_graph)
        c_layout.addRow(btn_apply)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.k_coords:
            apply_global_style()
            self.plot_graph()
            
    def process_data(self):
        if not all(self.files.values()):
            QMessageBox.warning(self, "Hata", "Tüm dosyaları yüklemelisiniz!")
            return
            
        try:
            apply_global_style()
            is_spin = self.cb_spin.isChecked()
            
            with open(self.files["klabels"], 'r', encoding='utf-8') as f:
                klabels_text = f.read().splitlines()
            with open(self.files["gap"], 'r', encoding='utf-8') as f:
                gap_text = f.read()
            with open(self.files["band"], 'r', encoding='utf-8') as f:
                band_text = f.read().splitlines()
                
            k_labels, k_coords = [], []
            for line in klabels_text[1:]: 
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        k_coords.append(float(parts[1]))
                        label = parts[0].upper()
                        k_labels.append(r"$\mathbf{\Gamma}$" if label == "GAMMA" else rf"$\mathbf{{{label}}}$")
                    except ValueError: 
                        continue
                        
            gap_lines = gap_text.splitlines()
            band_gap = 0.0
            vbm_up, vbm_dn = 1, 1
            cbm_up, cbm_dn = 1, 1
            
            for line in gap_lines:
                if "Band Gap (eV):" in line:
                    band_gap = float(line.split(":")[1].split()[-1])
                elif "Band Indexes of VBM & CBM:" in line:
                    vals = line.split(":")[1].split()
                    vbm_up, cbm_up = int(vals[0]), int(vals[1])
                    vbm_dn, cbm_dn = vbm_up, cbm_up
                elif "Band Index of VBM:" in line:
                    vals = line.split(":")[1].split()
                    vbm_up = int(vals[0])
                    vbm_dn = int(vals[1]) if len(vals) >= 3 else int(vals[0])
                elif "Band Index of CBM:" in line:
                    vals = line.split(":")[1].split()
                    cbm_up = int(vals[0])
                    cbm_dn = int(vals[1]) if len(vals) >= 3 else int(vals[0])
                    
            bands_up = {}
            bands_dn = {}
            curr = None
            global_y_min, global_y_max = 999, -999
            
            for line in band_text:
                if line.startswith("# Band-Index:"):
                    curr = int(line.split(":")[1].strip())
                    bands_up[curr] = []
                    bands_dn[curr] = []
                elif line.strip() and not line.startswith("#") and curr is not None:
                    parts = line.split()
                    if not is_spin and len(parts) >= 2:
                        x, y = float(parts[0]), float(parts[1])
                        bands_up[curr].append([x, y])
                        global_y_min, global_y_max = min(global_y_min, y), max(global_y_max, y)
                    elif is_spin and len(parts) >= 3:
                        x, y_up, y_dn = float(parts[0]), float(parts[1]), float(parts[2])
                        bands_up[curr].append([x, y_up])
                        bands_dn[curr].append([x, y_dn])
                        global_y_min = min(global_y_min, y_up, y_dn)
                        global_y_max = max(global_y_max, y_up, y_dn)
                        
            vbm_data_up = np.array(bands_up[vbm_up])
            cbm_data_up = np.array(bands_up[cbm_up])
            
            if is_spin:
                vbm_data_dn = np.array(bands_dn[vbm_dn])
                cbm_data_dn = np.array(bands_dn[cbm_dn])
                vbm_data = vbm_data_up if np.max(vbm_data_up[:, 1]) > np.max(vbm_data_dn[:, 1]) else vbm_data_dn
                cbm_data = cbm_data_up if np.min(cbm_data_up[:, 1]) < np.min(cbm_data_dn[:, 1]) else cbm_data_dn
            else:
                vbm_data = vbm_data_up
                cbm_data = cbm_data_up
                
            sort_idx_vbm = np.argsort(vbm_data[:, 0])
            sort_idx_cbm = np.argsort(cbm_data[:, 0])
            self.vbm_x = vbm_data[sort_idx_vbm, 0]
            self.vbm_y = vbm_data[sort_idx_vbm, 1]
            self.cbm_x = cbm_data[sort_idx_cbm, 0]
            self.cbm_y = cbm_data[sort_idx_cbm, 1]
            
            self.band_data_up = bands_up
            self.band_data_dn = bands_dn
            self.k_coords = k_coords
            self.k_labels = k_labels
            self.band_gap = band_gap
            
            self.ls_y_min.setValue(max(-15.0, float(np.floor(global_y_min))))
            self.ls_y_max.setValue(min(15.0, float(np.ceil(global_y_max))))
            
            if k_coords:
                self.ls_text_x.setValue(max(k_coords) / 2)
                self.ls_text_y.setValue((np.max(self.vbm_y) + np.min(self.cbm_y)) / 2)
            
            self.plot_graph()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veri işleme hatası:\n{e}")
            
    def plot_graph(self):
        if not self.k_coords: return
        
        self.figure.clear()
        import matplotlib as mpl
        mpl.rcParams['font.family'] = 'serif'
        mpl.rcParams['font.serif'] = ['Times New Roman']
        mpl.rcParams['mathtext.fontset'] = 'custom'
        mpl.rcParams['mathtext.rm'] = 'Times New Roman'
        mpl.rcParams['mathtext.it'] = 'Times New Roman:italic'
        mpl.rcParams['mathtext.bf'] = 'Times New Roman:bold'
        
        ax = self.figure.add_subplot(111)
        is_spin = self.cb_spin.isChecked()
        
        if is_spin:
            for idx in self.band_data_up.keys():
                data_up = np.array(self.band_data_up[idx])
                data_dn = np.array(self.band_data_dn[idx])
                
                lbl_up = r"Spin $\uparrow$" if idx == 1 else ""
                lbl_dn = r"Spin $\downarrow$" if idx == 1 else ""
                
                ax.plot(data_up[:, 0], data_up[:, 1], color=self.cp_up.color, lw=1.5, zorder=2, label=lbl_up)
                ax.plot(data_dn[:, 0], data_dn[:, 1], color=self.cp_dn.color, lw=1.5, ls='--', zorder=2, label=lbl_dn)
                
            leg = ax.legend(loc='upper right', frameon=True, fontsize=14, prop={'weight': 'bold', 'family': 'Times New Roman'})
            leg.get_frame().set_linewidth(1.5)
            leg.set_draggable(True)
        else:
            for idx, data_list in self.band_data_up.items():
                data = np.array(data_list)
                ax.plot(data[:, 0], data[:, 1], color=self.cp_band.color, lw=2.0, zorder=2)
                
        if self.band_gap > 0.01 and self.ls_show_fill.isChecked():
            ax.fill_between(self.vbm_x, self.vbm_y, self.cbm_y, 
                            color=self.cp_fill.color, alpha=0.3, zorder=1)
                            
        ax.axhline(0, color=self.cp_fermi.color, ls='--', lw=2.0, zorder=3) 
        for c in self.k_coords: 
            ax.axvline(c, color='blue', lw=1.5, zorder=0, alpha=self.ls_k_alpha.value()) 
            
        if self.band_gap > 0.01 and self.ls_show_text.isChecked():
            ax.text(self.ls_text_x.value(), self.ls_text_y.value(), f"Band gap = {self.band_gap:.2f} eV", 
                    fontsize=16, fontweight='bold', ha='center', va='center', zorder=10,
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))
                    
        custom_txt = self.ls_custom.text()
        if custom_txt.strip():
            ax.text(self.ls_custom_x.value(), self.ls_custom_y.value(), custom_txt, 
                    fontsize=16, fontweight='bold', ha='center', va='center', zorder=10)
                    
        ax.set_xticks(self.k_coords)
        ax.set_xticklabels(self.k_labels, fontsize=16, fontweight='bold')
        ax.set_ylabel(r'$\mathbf{Energy\ (E - E_{F})\ (eV)}$', fontsize=18, labelpad=15)
        
        ax.set_ylim(self.ls_y_min.value(), self.ls_y_max.value())
        if self.k_coords:
            ax.set_xlim(min(self.k_coords), max(self.k_coords))
            
        ax.yaxis.set_major_locator(MultipleLocator(self.ls_y_step.value()))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.tick_params(axis='y', labelsize=14, direction='in', length=10, width=2.0, right=False)
        ax.tick_params(axis='y', which='minor', direction='in', length=5, width=1.5, right=False)
        ax.tick_params(axis='x', pad=self.ls_pad.value(), length=0)
        
        for label in ax.get_yticklabels():
            label.set_fontweight('bold')
            
        panel_lbl = self.ls_panel.text()
        if panel_lbl.strip():
            ax.text(-0.05, 0.97, panel_lbl, transform=ax.transAxes, 
                    fontsize=18, fontweight='bold', ha='right', va='bottom')
                    
        for spine in ax.spines.values():
            spine.set_linewidth(2.5)
            
        self.figure.tight_layout()
        try:
            from utils.style_manager import apply_custom_axes_settings
            if hasattr(self, 'figure'):
                apply_custom_axes_settings(self.figure)
        except Exception as e:
            print(f'Error applying custom axes settings: {e}')
        self.canvas.draw()
