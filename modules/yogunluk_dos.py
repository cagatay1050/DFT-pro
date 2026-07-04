import os
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QFormLayout, QGroupBox, QMessageBox, QSpinBox, 
    QDoubleSpinBox, QComboBox, QScrollArea, QLineEdit, QCheckBox, QColorDialog
)
from PyQt6.QtCore import Qt
from utils.style_manager import apply_global_style, notifier

class YogunlukDOSWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.tdos_df = None
        self.pdos_list = []
        self.pdos_files = [] # [{'label_le': QLineEdit, 'file_path': str, 'btn': QPushButton, 'color': str}]
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Sol Panel (Kontrol Paneli)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(450)
        
        self.cb_is_spin = QCheckBox("Manyetik / Spin-Polarize (ISPIN=2) Hesaplama Mı?")
        left_layout.addWidget(self.cb_is_spin)
        
        # 1. Total DOS
        group_tdos = QGroupBox("1. Total DOS (TDOS.dat)")
        l_tdos = QVBoxLayout()
        self.btn_load_tdos = QPushButton("TDOS Dosyasını Yükle (Zorunlu)")
        self.btn_load_tdos.clicked.connect(self.load_tdos)
        self.lbl_tdos = QLabel("Seçilen TDOS: Yok")
        
        h_tdos_color = QHBoxLayout()
        h_tdos_color.addWidget(QLabel("TDOS Rengi:"))
        self.btn_tdos_color = QPushButton()
        self.btn_tdos_color.setStyleSheet("background-color: #7f8c8d;")
        self.tdos_color = "#7f8c8d"
        self.btn_tdos_color.clicked.connect(self.pick_tdos_color)
        h_tdos_color.addWidget(self.btn_tdos_color)
        
        l_tdos.addWidget(self.btn_load_tdos)
        l_tdos.addWidget(self.lbl_tdos)
        l_tdos.addLayout(h_tdos_color)
        group_tdos.setLayout(l_tdos)
        
        # 2. PDOS
        group_pdos = QGroupBox("2. PDOS (Partial DOS) Dosyaları")
        self.l_pdos = QVBoxLayout()
        
        btn_add_pdos = QPushButton("+ Yeni PDOS Dosyası Ekle")
        btn_add_pdos.clicked.connect(self.add_pdos_slot)
        self.l_pdos.addWidget(btn_add_pdos)
        
        self.pdos_container = QVBoxLayout()
        self.l_pdos.addLayout(self.pdos_container)
        
        group_pdos.setLayout(self.l_pdos)
        
        # 3. Ayarlar
        group_settings = QGroupBox("3. Grafik Ayarları")
        l_settings = QFormLayout()
        
        self.ls_x_min = QDoubleSpinBox(); self.ls_x_min.setRange(-100, 100); self.ls_x_min.setValue(-10.0)
        self.ls_x_max = QDoubleSpinBox(); self.ls_x_max.setRange(-100, 100); self.ls_x_max.setValue(10.0)
        self.ls_x_step = QDoubleSpinBox(); self.ls_x_step.setRange(0.1, 50); self.ls_x_step.setValue(2.0)
        
        self.ls_y_min = QDoubleSpinBox(); self.ls_y_min.setRange(-1000, 1000); self.ls_y_min.setValue(0.0)
        self.ls_y_max = QDoubleSpinBox(); self.ls_y_max.setRange(-1000, 1000); self.ls_y_max.setValue(50.0)
        self.ls_y_step = QDoubleSpinBox(); self.ls_y_step.setRange(0.1, 500); self.ls_y_step.setValue(10.0)
        
        self.cb_fill = QCheckBox("Grafik Alanlarını Boya (Fill)")
        self.cb_fill.setChecked(True)
        
        l_settings.addRow("X Min (eV):", self.ls_x_min)
        l_settings.addRow("X Maks (eV):", self.ls_x_max)
        l_settings.addRow("X Adım:", self.ls_x_step)
        l_settings.addRow("Y Min:", self.ls_y_min)
        l_settings.addRow("Y Maks:", self.ls_y_max)
        l_settings.addRow("Y Adım:", self.ls_y_step)
        l_settings.addRow("", self.cb_fill)
        
        group_settings.setLayout(l_settings)
        
        self.btn_plot = QPushButton("Grafiği Çiz")
        self.btn_plot.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 10px;")
        self.btn_plot.clicked.connect(self.process_and_plot)
        
        left_layout.addWidget(group_tdos)
        left_layout.addWidget(group_pdos)
        left_layout.addWidget(group_settings)
        left_layout.addWidget(self.btn_plot)
        left_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidget(left_panel)
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(480)
        
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

    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QFormLayout(self.local_widget)
        self.ls_font_title = QSpinBox(); self.ls_font_title.setRange(8, 40); self.ls_font_title.setValue(22)
        self.ls_font_tick = QSpinBox(); self.ls_font_tick.setRange(8, 40); self.ls_font_tick.setValue(18)
        self.ls_line_width = QDoubleSpinBox(); self.ls_line_width.setRange(0.5, 10.0); self.ls_line_width.setValue(2.0); self.ls_line_width.setSingleStep(0.5)
        self.cmb_leg_loc = QComboBox()
        self.cmb_leg_loc.addItems(["upper right", "upper left", "lower left", "lower right", "best"])
        
        layout.addRow("Başlık Punto:", self.ls_font_title)
        layout.addRow("Rakam Punto:", self.ls_font_tick)
        layout.addRow("Çizgi Kalınlığı:", self.ls_line_width)
        layout.addRow("Lejant Konumu:", self.cmb_leg_loc)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.tdos_df is not None:
            self.plot_graph()
            
    def pick_tdos_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.tdos_color = color.name()
            self.btn_tdos_color.setStyleSheet(f"background-color: {self.tdos_color};")

    def load_tdos(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "TDOS Dosyasını Seç", "", "Data Files (*.dat *.txt);;All Files (*)")
        if file_path:
            self.tdos_file_path = file_path
            self.lbl_tdos.setText(f"Seçilen: {os.path.basename(file_path)}")

    def add_pdos_slot(self):
        idx = len(self.pdos_files)
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0,0,0,0)
        
        le = QLineEdit(f"Orbital-{idx+1}")
        btn = QPushButton("Dosya Seç")
        btn_color = QPushButton()
        btn_color.setStyleSheet("background-color: #3498db; width: 20px; height: 20px;")
        
        pdos_item = {'label_le': le, 'file_path': None, 'btn': btn, 'color': '#3498db'}
        
        def choose_file():
            fp, _ = QFileDialog.getOpenFileName(self, "PDOS Seç", "", "Data Files (*.dat *.txt);;All Files (*)")
            if fp:
                pdos_item['file_path'] = fp
                btn.setText(os.path.basename(fp))
                
        def choose_color():
            color = QColorDialog.getColor()
            if color.isValid():
                pdos_item['color'] = color.name()
                btn_color.setStyleSheet(f"background-color: {color.name()}; width: 20px; height: 20px;")
                
        btn.clicked.connect(choose_file)
        btn_color.clicked.connect(choose_color)
        
        l.addWidget(le)
        l.addWidget(btn)
        l.addWidget(btn_color)
        
        self.pdos_container.addWidget(w)
        self.pdos_files.append(pdos_item)

    def smart_load(self, file_path, is_spin):
        df = pd.read_csv(file_path, sep=r'\s+', comment='#', header=None, engine='python')
        if is_spin and df.shape[1] >= 3:
            df_clean = pd.DataFrame({
                'E': df[0],
                'Up': df[1],
                'Dn': -abs(df[2])
            })
        else:
            df_clean = pd.DataFrame({'E': df[0], 'Up': df[1]})
        return df_clean.dropna().reset_index(drop=True)

    def process_and_plot(self):
        if not hasattr(self, 'tdos_file_path') or not self.tdos_file_path:
            QMessageBox.warning(self, "Hata", "Lütfen önce TDOS dosyasını yükleyin.")
            return
            
        try:
            is_spin = self.cb_is_spin.isChecked()
            self.tdos_df = self.smart_load(self.tdos_file_path, is_spin)
            
            self.pdos_list = []
            for p in self.pdos_files:
                if p['file_path']:
                    pdf = self.smart_load(p['file_path'], is_spin)
                    self.pdos_list.append({
                        'label': p['label_le'].text(),
                        'df': pdf,
                        'color': p['color']
                    })
                    
            e_min = float(np.floor(self.tdos_df['E'].min() / 2) * 2)
            e_max = float(np.ceil(self.tdos_df['E'].max() / 2) * 2)
            dos_max = float(np.ceil(self.tdos_df['Up'].max() * 1.1))
            dos_min = float(np.floor(self.tdos_df['Dn'].min() * 1.1)) if is_spin else 0.0
            
            self.ls_x_min.setValue(max(e_min, -10.0))
            self.ls_x_max.setValue(min(e_max, 10.0))
            self.ls_y_min.setValue(dos_min)
            self.ls_y_max.setValue(dos_max)
            
            self.plot_graph()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veri işleme hatası:\n{e}")

    def plot_graph(self):
        if self.tdos_df is None: return
        
        self.figure.clear()
        apply_global_style()
        ax = self.figure.add_subplot(111)
        
        is_spin = self.cb_is_spin.isChecked()
        lw = self.ls_line_width.value()
        fill = self.cb_fill.isChecked()
        
        def plot_dos(df, color, label, zorder):
            ax.plot(df['E'], df['Up'], color=color, linewidth=lw, label=label, zorder=zorder)
            if fill:
                ax.fill_between(df['E'], 0, df['Up'], color=color, alpha=0.3, zorder=zorder)
                
            if is_spin and 'Dn' in df.columns:
                ax.plot(df['E'], df['Dn'], color=color, linewidth=lw, zorder=zorder)
                if fill:
                    ax.fill_between(df['E'], 0, df['Dn'], color=color, alpha=0.3, zorder=zorder)

        plot_dos(self.tdos_df, self.tdos_color, "Total DOS", zorder=2)
        
        for i, p in enumerate(self.pdos_list):
            plot_dos(p['df'], p['color'], p['label'], zorder=3+i)
            
        # Fermi Line
        ax.axvline(0, color='black', linestyle='--', linewidth=1.5, zorder=1)
        if is_spin:
            ax.axhline(0, color='black', linestyle='-', linewidth=1.0, zorder=1)
            
        ax.set_xlim(self.ls_x_min.value(), self.ls_x_max.value())
        ax.set_ylim(self.ls_y_min.value(), self.ls_y_max.value())
        
        ax.set_xlabel('Energy (eV)', fontsize=self.ls_font_title.value(), fontweight='bold', labelpad=15)
        ax.set_ylabel('Density of States', fontsize=self.ls_font_title.value(), fontweight='bold', labelpad=15)
        
        ax.xaxis.set_major_locator(MultipleLocator(self.ls_x_step.value()))
        ax.yaxis.set_major_locator(MultipleLocator(self.ls_y_step.value()))
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        
        ftick = self.ls_font_tick.value()
        ax.tick_params(axis='both', which='major', direction='in', length=10, width=2, labelsize=ftick, top=True, right=False)
        ax.tick_params(axis='both', which='minor', direction='in', length=5, width=1.5, top=True, right=False)
        
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')
        for spine in ax.spines.values():
            spine.set_linewidth(2.0)
            
        leg = ax.legend(loc=self.cmb_leg_loc.currentText(), frameon=True)
        leg.set_draggable(True)
            
        self.figure.tight_layout()
        self.canvas.draw()
        self.canvas.draw()
