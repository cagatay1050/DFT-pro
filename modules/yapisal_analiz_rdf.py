import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QFormLayout, QGroupBox, QMessageBox, QDoubleSpinBox,
    QScrollArea, QLineEdit, QComboBox, QSpinBox, QTabWidget
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from utils.style_manager import apply_global_style, notifier

class PanelData:
    def __init__(self, idx, parent):
        self.idx = idx
        self.parent = parent
        self.rdf_path = ""
        self.coord_path = ""
        self.rdf_df = None
        self.coord_df = None
        
        self.group = QGroupBox(f"Panel {idx+1}")
        layout = QFormLayout()
        
        self.le_label = QLineEdit(f"Pair-{idx+1}")
        self.btn_rdf = QPushButton("RDF Dosyası ($g(r)$)")
        self.lbl_rdf = QLabel("Yüklenmedi")
        self.btn_rdf.clicked.connect(self.load_rdf)
        
        self.btn_coord = QPushButton("Coord Dosyası ($N(r)$)")
        self.lbl_coord = QLabel("Yüklenmedi")
        self.btn_coord.clicked.connect(self.load_coord)
        
        layout.addRow("Etiket:", self.le_label)
        layout.addRow(self.btn_rdf, self.lbl_rdf)
        layout.addRow(self.btn_coord, self.lbl_coord)
        self.group.setLayout(layout)
        
        # Local Settings UI for this panel
        self.settings_widget = QWidget()
        s_layout = QFormLayout(self.settings_widget)
        self.ls_x_max = QDoubleSpinBox(); self.ls_x_max.setRange(0.1, 100); self.ls_x_max.setValue(5.0); self.ls_x_max.setSingleStep(0.5)
        self.ls_y_max = QDoubleSpinBox(); self.ls_y_max.setRange(0.1, 1000); self.ls_y_max.setValue(10.0); self.ls_y_max.setSingleStep(1.0)
        self.ls_y_step = QDoubleSpinBox(); self.ls_y_step.setRange(0.1, 100); self.ls_y_step.setValue(2.0); self.ls_y_step.setSingleStep(1.0)
        self.ls_yc_max = QDoubleSpinBox(); self.ls_yc_max.setRange(0.1, 1000); self.ls_yc_max.setValue(10.0); self.ls_yc_max.setSingleStep(1.0)
        self.ls_yc_step = QDoubleSpinBox(); self.ls_yc_step.setRange(0.1, 100); self.ls_yc_step.setValue(2.0); self.ls_yc_step.setSingleStep(1.0)
        
        s_layout.addRow("Maks X ($r$, Å):", self.ls_x_max)
        s_layout.addRow("Maks g(r):", self.ls_y_max)
        s_layout.addRow("g(r) Aralık:", self.ls_y_step)
        s_layout.addRow("Maks N(r):", self.ls_yc_max)
        s_layout.addRow("N(r) Aralık:", self.ls_yc_step)
        
    def load_rdf(self):
        fname, _ = QFileDialog.getOpenFileName(self.parent, 'RDF Dosyası Aç', '', 'Data Files (*.dat *.txt);;All Files (*)')
        if fname:
            self.rdf_path = fname
            self.lbl_rdf.setText("Yüklendi")
            
    def load_coord(self):
        fname, _ = QFileDialog.getOpenFileName(self.parent, 'Coordination Dosyası Aç', '', 'Data Files (*.dat *.txt);;All Files (*)')
        if fname:
            self.coord_path = fname
            self.lbl_coord.setText("Yüklendi")

class YapisalAnalizRDFWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.panels = []
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel (Inputs)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)
        
        control_group = QGroupBox("Panel Ayarları")
        c_layout = QFormLayout()
        self.spin_panels = QSpinBox()
        self.spin_panels.setRange(1, 6)
        self.spin_panels.setValue(3)
        self.spin_panels.valueChanged.connect(self.update_panel_count)
        c_layout.addRow("Panel Sayısı:", self.spin_panels)
        control_group.setLayout(c_layout)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.panels_container = QWidget()
        self.panels_layout = QVBoxLayout(self.panels_container)
        self.scroll_area.setWidget(self.panels_container)
        
        # Create all 6 panels but hide unused
        for i in range(6):
            p = PanelData(i, self)
            self.panels.append(p)
            self.panels_layout.addWidget(p.group)
            
        self.panels_layout.addStretch()
        
        self.btn_calc = QPushButton("Verileri Oku ve Grafiği Hazırla")
        self.btn_calc.clicked.connect(self.process_data)
        self.btn_calc.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        
        left_layout.addWidget(control_group)
        left_layout.addWidget(self.scroll_area)
        left_layout.addWidget(self.btn_calc)
        
        # Right Panel (Plot)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.figure = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.update_panel_count(3)
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)
        
    def update_panel_count(self, count):
        for i in range(6):
            if i < count:
                self.panels[i].group.setVisible(True)
            else:
                self.panels[i].group.setVisible(False)
        self.update_settings_tabs(count)
                
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        
        self.settings_tabs = QTabWidget()
        for p in self.panels:
            self.settings_tabs.addTab(p.settings_widget, f"P {p.idx+1}")
            
        layout.addWidget(self.settings_tabs)
        
        btn_apply = QPushButton("Yerel Ayarları Uygula")
        btn_apply.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 10px;")
        btn_apply.clicked.connect(self.plot_graph)
        layout.addWidget(btn_apply)
        
        self.update_settings_tabs(3)
        
    def update_settings_tabs(self, count):
        if hasattr(self, 'settings_tabs'):
            for i in range(6):
                self.settings_tabs.setTabVisible(i, i < count)
        
    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        self.plot_graph()

    def process_data(self):
        count = self.spin_panels.value()
        valid = False
        
        for i in range(count):
            p = self.panels[i]
            if p.rdf_path and p.coord_path:
                try:
                    p.rdf_df = pd.read_csv(p.rdf_path, sep=r'\s+', header=None, comment='#', engine='python')
                    p.rdf_df = pd.DataFrame({'X': pd.to_numeric(p.rdf_df.iloc[:, 0], errors='coerce'), 'Y': pd.to_numeric(p.rdf_df.iloc[:, -1], errors='coerce')}).dropna().reset_index(drop=True)
                    
                    p.coord_df = pd.read_csv(p.coord_path, sep=r'\s+', header=None, comment='#', engine='python')
                    p.coord_df = pd.DataFrame({'X': pd.to_numeric(p.coord_df.iloc[:, 0], errors='coerce'), 'Y': pd.to_numeric(p.coord_df.iloc[:, -1], errors='coerce')}).dropna().reset_index(drop=True)
                    
                    # Auto bounds
                    y_max = float(np.ceil(p.rdf_df['Y'].max() * 1.2))
                    yc_max = float(np.ceil(p.coord_df['Y'].max() * 1.2))
                    if y_max <= 0: y_max = 10.0
                    if yc_max <= 0: yc_max = 10.0
                    
                    p.ls_y_max.setValue(y_max)
                    p.ls_y_step.setValue(max(1.0, float(np.ceil(y_max/5))))
                    p.ls_yc_max.setValue(yc_max)
                    p.ls_yc_step.setValue(max(1.0, float(np.ceil(yc_max/5))))
                    valid = True
                except Exception as e:
                    QMessageBox.warning(self, "Hata", f"Panel {i+1} okunurken hata oluştu: {e}")
                    
        if not valid:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir panel için hem RDF hem Coord dosyalarını yükleyin.")
            return
            
        apply_global_style()
        self.plot_graph()
        
    def plot_graph(self):
        count = self.spin_panels.value()
        active_panels = [p for p in self.panels[:count] if p.rdf_df is not None and p.coord_df is not None]
        
        if not active_panels: return
        
        self.figure.clear()
        
        n_valid = len(active_panels)
        cols = min(n_valid, 3)
        rows = int(np.ceil(n_valid / cols))
        
        axes = self.figure.subplots(rows, cols, squeeze=False)
        
        # Hide unused
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                if idx >= n_valid:
                    axes[r, c].set_visible(False)
                    
        ln1, ln2 = None, None
        
        for idx, p in enumerate(active_panels):
            r, c = divmod(idx, cols)
            ax1 = axes[r, c]
            
            # Left Axis (g(r))
            line1, = ax1.plot(p.rdf_df['X'], p.rdf_df['Y'], color='black', linewidth=3.5, label='$g(r)$')
            if idx == 0: ln1 = line1
            
            ax1.set_xlabel(r'Distance ($r$, $\mathbf{\AA}$)', fontweight='bold', labelpad=10)
            if c == 0: 
                ax1.set_ylabel(r'$g(r)$', fontweight='bold', color='black', labelpad=10)
                
            ax1.set_xlim(0, p.ls_x_max.value())
            ax1.set_ylim(0, p.ls_y_max.value())
            
            ax1.xaxis.set_major_locator(MultipleLocator(1.0))
            ax1.xaxis.set_minor_locator(AutoMinorLocator(2))
            ax1.yaxis.set_major_locator(MultipleLocator(p.ls_y_step.value()))
            ax1.yaxis.set_minor_locator(AutoMinorLocator(2))
            ax1.tick_params(axis='both', which='major', labelsize=14, direction='in', length=8, width=2, pad=8, top=True, right=False)
            
            # Right Axis (N(r))
            ax2 = ax1.twinx()
            line2, = ax2.plot(p.coord_df['X'], p.coord_df['Y'], color='#d62728', linewidth=3.5, linestyle='--', label='$N(r)$')
            if idx == 0: ln2 = line2
            
            if c == cols - 1 or idx == n_valid - 1:
                ax2.set_ylabel(r'Coordination ($N$)', fontweight='bold', color='#d62728', labelpad=20, rotation=-90)
                
            ax2.set_ylim(0, p.ls_yc_max.value())
            ax2.yaxis.set_major_locator(MultipleLocator(p.ls_yc_step.value()))
            ax2.yaxis.set_minor_locator(AutoMinorLocator(2))
            ax2.tick_params(axis='y', which='major', right=True, labelsize=14, direction='in', length=8, width=2, pad=8, colors='#d62728')
            
            # Peak Text
            try:
                peak_idx = p.rdf_df['Y'].idxmax()
                bond_len = p.rdf_df.loc[peak_idx, 'X']
                max_rdf = p.rdf_df['Y'].max()
                ax1.annotate(f'{bond_len:.2f} Å', xy=(bond_len, max_rdf), 
                            xytext=(bond_len + 0.3, max_rdf + (p.ls_y_max.value()*0.05)),
                            arrowprops=dict(arrowstyle='->', color='blue', lw=2.0), 
                            fontsize=14, color='blue', fontweight='bold')
            except:
                pass
                
            ax1.text(0.04, 0.94, f"({chr(97+idx)}) {p.le_label.text()}", transform=ax1.transAxes, fontsize=16, fontweight='bold', va='top')
            
        if ln1 and ln2:
            leg = axes[0, 0].legend([ln1, ln2], ['$g(r)$', '$N(r)$'], loc='upper right', frameon=False, bbox_to_anchor=(0.98, 0.98))
            leg.set_draggable(True)
            
        self.figure.tight_layout(pad=2.0)
        try:
            from utils.style_manager import apply_custom_axes_settings
            if hasattr(self, 'figure'):
                apply_custom_axes_settings(self.figure)
        except Exception as e:
            print(f'Error applying custom axes settings: {e}')
        self.canvas.draw()
