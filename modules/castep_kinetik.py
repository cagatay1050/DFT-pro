import os
import re
import numpy as np
from scipy.interpolate import PchipInterpolator
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QFormLayout, QGroupBox, QMessageBox, QDoubleSpinBox, 
    QSpinBox, QLineEdit, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QColorDialog
)
from PyQt6.QtCore import Qt
from utils.style_manager import apply_global_style, notifier

def parse_castep(content):
    data = {}
    try:
        barriers = re.findall(r"Barrier from reactant:\s+([\d\.]+)\s+eV", content)
        data['barrier'] = float(barriers[-1]) if barriers else None
        
        locations = re.findall(r"Location of transition state:\s+([\d\.]+)", content)
        data['location'] = float(locations[-1]) if locations else 0.5
        
        reactions = re.findall(r"Energy of reaction:\s+([\-\d\.]+)\s+eV", content)
        data['reaction_e'] = float(reactions[-1]) if reactions else None
        
        volumes = re.findall(r"Current cell volume =\s+([\d\.]+)\s+A\*\*3", content)
        data['volume'] = float(volumes[-1]) if volumes else 990.06
        
        return data
    except Exception:
        return None

class CastepKinetikWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data_files = [] 
        self.results = []
        self.plot_data = []
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(450)
        
        # 1. Termodinamik Parametreler
        group_termo = QGroupBox("1. Termodinamik Parametreler")
        l_termo = QFormLayout()
        
        self.sb_t = QDoubleSpinBox(); self.sb_t.setRange(0, 5000); self.sb_t.setValue(300.0); self.sb_t.setSingleStep(10.0)
        self.sb_n = QSpinBox(); self.sb_n.setRange(1, 100); self.sb_n.setValue(1)
        self.sb_z = QSpinBox(); self.sb_z.setRange(1, 10); self.sb_z.setValue(1)
        self.le_v0 = QLineEdit("1.0e13")
        
        l_termo.addRow("Sıcaklık (K):", self.sb_t)
        l_termo.addRow("Mobil İyon Sayısı (N):", self.sb_n)
        l_termo.addRow("İyon Yükü (Z):", self.sb_z)
        l_termo.addRow("Deneme Frekansı (Hz):", self.le_v0)
        group_termo.setLayout(l_termo)
        
        # 2. CASTEP Veri Dosyaları
        group_files = QGroupBox("2. CASTEP Dosyaları")
        self.l_files = QVBoxLayout()
        
        btn_add = QPushButton("+ Yeni Path Ekle")
        btn_add.clicked.connect(self.add_data_slot)
        self.l_files.addWidget(btn_add)
        
        self.files_container = QVBoxLayout()
        self.l_files.addLayout(self.files_container)
        group_files.setLayout(self.l_files)
        
        # Initial 1 slot
        self.add_data_slot()
        
        # 3. Sonuç Tablosu
        group_results = QGroupBox("3. Analiz Sonuçları")
        l_results = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Yön", "Dosya", "Ea (eV)", "a0 (Å)", "D (cm²/s)", "Sigma (S/cm)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        l_results.addWidget(self.table)
        group_results.setLayout(l_results)
        
        self.btn_plot = QPushButton("Verileri Oku ve Çiz")
        self.btn_plot.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.btn_plot.clicked.connect(self.process_and_plot)
        
        left_layout.addWidget(group_termo)
        left_layout.addWidget(group_files)
        left_layout.addWidget(self.btn_plot)
        left_layout.addWidget(group_results)
        left_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidget(left_panel)
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(480)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
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
        
        self.le_mat_name = QLineEdit("Sr$_2$ZnH$_6$")
        self.ls_y_min = QDoubleSpinBox(); self.ls_y_min.setRange(-10, 10); self.ls_y_min.setValue(-0.1); self.ls_y_min.setSingleStep(0.1)
        self.ls_y_max = QDoubleSpinBox(); self.ls_y_max.setRange(-10, 10); self.ls_y_max.setValue(1.0); self.ls_y_max.setSingleStep(0.1)
        self.ls_x_maj = QDoubleSpinBox(); self.ls_x_maj.setRange(0.01, 10); self.ls_x_maj.setValue(0.2); self.ls_x_maj.setSingleStep(0.1)
        self.ls_y_maj = QDoubleSpinBox(); self.ls_y_maj.setRange(0.01, 10); self.ls_y_maj.setValue(0.2); self.ls_y_maj.setSingleStep(0.1)
        self.ls_font_size = QSpinBox(); self.ls_font_size.setRange(8, 40); self.ls_font_size.setValue(14)
        
        layout.addRow("Malzeme Adı:", self.le_mat_name)
        layout.addRow("Y Min (eV):", self.ls_y_min)
        layout.addRow("Y Max (eV):", self.ls_y_max)
        layout.addRow("X Tick Aralığı:", self.ls_x_maj)
        layout.addRow("Y Tick Aralığı:", self.ls_y_maj)
        layout.addRow("Font Boyutu:", self.ls_font_size)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.plot_data:
            self.plot_graph()

    def add_data_slot(self):
        idx = len(self.data_files)
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0,0,0,0)
        
        le_lbl = QLineEdit(f"Path {idx+1}")
        sb_a0 = QDoubleSpinBox()
        sb_a0.setRange(0.1, 20.0)
        sb_a0.setValue(2.52)
        sb_a0.setSingleStep(0.05)
        sb_a0.setToolTip("a0 (Å)")
        
        btn = QPushButton("Dosya Seç")
        btn_color = QPushButton()
        
        default_colors = ['#E64B35', '#4DBBD5', '#00A087', '#3C5488', '#F39B7F']
        c = default_colors[idx % len(default_colors)]
        btn_color.setStyleSheet(f"background-color: {c}; width: 20px; height: 20px;")
        
        item = {'label_le': le_lbl, 'a0_sb': sb_a0, 'file_path': None, 'btn': btn, 'color': c}
        
        def choose_file():
            fp, _ = QFileDialog.getOpenFileName(self, "CASTEP Seç", "", "CASTEP Files (*.castep);;All Files (*)")
            if fp:
                item['file_path'] = fp
                btn.setText(os.path.basename(fp))
                
        def choose_color():
            color = QColorDialog.getColor()
            if color.isValid():
                item['color'] = color.name()
                btn_color.setStyleSheet(f"background-color: {color.name()}; width: 20px; height: 20px;")
                
        btn.clicked.connect(choose_file)
        btn_color.clicked.connect(choose_color)
        
        l.addWidget(le_lbl)
        l.addWidget(btn)
        l.addWidget(sb_a0)
        l.addWidget(btn_color)
        
        self.files_container.addWidget(w)
        self.data_files.append(item)

    def process_and_plot(self):
        self.results = []
        self.plot_data = []
        
        K_B_EV = 8.617333262e-5  
        K_B_J = 1.380649e-23     
        E_CHARGE = 1.602176634e-19 
        
        T = self.sb_t.value()
        N_ions = self.sb_n.value()
        Z_ion = self.sb_z.value()
        
        try:
            v0 = float(self.le_v0.text())
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçersiz Deneme Frekansı (v0)")
            return

        for item in self.data_files:
            if item['file_path']:
                try:
                    with open(item['file_path'], 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    parsed_data = parse_castep(content)
                    if parsed_data and parsed_data['barrier'] is not None:
                        Ea = parsed_data['barrier']
                        loc = parsed_data['location']
                        E_rxn = parsed_data['reaction_e']
                        V_ang = parsed_data['volume']
                        a0 = item['a0_sb'].value()
                        
                        c_H = N_ions / (V_ang * 1e-24)
                        D = ((a0 * 1e-8)**2) * v0 * np.exp(-Ea / (K_B_EV * T))
                        sigma = (c_H * (Z_ion * E_CHARGE)**2 * D) / (K_B_J * T)
                        
                        self.results.append({
                            "Yön": item['label_le'].text(),
                            "Dosya": os.path.basename(item['file_path']),
                            "Ea (eV)": Ea,
                            "a0 (Å)": a0,
                            "D (cm²/s)": f"{D:.3e}",
                            "Sigma (S/cm)": f"{sigma:.3e}"
                        })
                        
                        self.plot_data.append({
                            "label": item['label_le'].text(), 
                            "color": item['color'],
                            "x": [0.0, loc, 1.0], 
                            "y": [0.0, Ea, E_rxn]
                        })
                except Exception as e:
                    QMessageBox.warning(self, "Uyarı", f"{os.path.basename(item['file_path'])} okunamadı:\n{e}")
                    
        self.update_table()
        self.plot_graph()

    def update_table(self):
        self.table.setRowCount(len(self.results))
        for r_idx, res in enumerate(self.results):
            self.table.setItem(r_idx, 0, QTableWidgetItem(str(res['Yön'])))
            self.table.setItem(r_idx, 1, QTableWidgetItem(str(res['Dosya'])))
            self.table.setItem(r_idx, 2, QTableWidgetItem(str(res['Ea (eV)'])))
            self.table.setItem(r_idx, 3, QTableWidgetItem(str(res['a0 (Å)'])))
            self.table.setItem(r_idx, 4, QTableWidgetItem(str(res['D (cm²/s)'])))
            self.table.setItem(r_idx, 5, QTableWidgetItem(str(res['Sigma (S/cm)'])))

    def plot_graph(self):
        if not self.plot_data: return
        
        self.figure.clear()
        apply_global_style()
        self.ax = self.figure.add_subplot(111)
        
        font_size = self.ls_font_size.value()
        
        for path in self.plot_data:
            x = np.array(path["x"])
            y = np.array(path["y"])
            c = path["color"]
            lbl = path['label']
            
            interpolator = PchipInterpolator(x, y)
            x_smooth = np.linspace(0, 1, 500)
            y_smooth = interpolator(x_smooth)
            
            self.ax.plot(x_smooth, y_smooth, label=lbl, linewidth=2.5, color=c)
            
        self.ax.set_xlim(0, 1.0)
        self.ax.set_ylim(self.ls_y_min.value(), self.ls_y_max.value())
        
        self.ax.xaxis.set_major_locator(MultipleLocator(self.ls_x_maj.value()))
        self.ax.yaxis.set_major_locator(MultipleLocator(self.ls_y_maj.value()))
        
        self.ax.set_xlabel("Pathway", fontsize=font_size, fontweight='bold', labelpad=15)
        self.ax.set_ylabel("Energy (eV)", fontsize=font_size, fontweight='bold', labelpad=15)
        
        mat_name = self.le_mat_name.text()
        if mat_name:
            self.ax.text(0.05, 0.95, mat_name, transform=self.ax.transAxes, 
                         fontsize=font_size+2, fontweight='bold', va='top', ha='left')
                         
        self.ax.axhline(0, color='black', linestyle='--', linewidth=1.5, alpha=0.6, zorder=1)
        self.ax.grid(False)
        leg = self.ax.legend(loc="upper right", frameon=False, fontsize=font_size-2)
        leg.set_draggable(True)
        
        self.figure.tight_layout()
        self.canvas.draw()
