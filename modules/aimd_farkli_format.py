import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QFormLayout, QGroupBox, QMessageBox, QSpinBox, 
    QDoubleSpinBox, QComboBox, QScrollArea, QLineEdit, QCheckBox, 
    QColorDialog, QRadioButton, QButtonGroup, QSlider
)
from PyQt6.QtCore import Qt
from utils.style_manager import apply_global_style, notifier

class AIMDFarkliFormatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.datasets = []
        self.data_files = [] 
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Sol Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(450)
        
        # 1. Plot Mode and Data Count
        group_mode = QGroupBox("1. Çizim Modu")
        l_mode = QVBoxLayout()
        
        self.bg_mode = QButtonGroup(self)
        self.rb_both = QRadioButton("İkisi Yan Yana (Both)")
        self.rb_temp = QRadioButton("Sadece Sıcaklık")
        self.rb_energy = QRadioButton("Sadece Enerji")
        
        self.rb_both.setChecked(True)
        self.bg_mode.addButton(self.rb_both, 1)
        self.bg_mode.addButton(self.rb_temp, 2)
        self.bg_mode.addButton(self.rb_energy, 3)
        
        h_mode = QHBoxLayout()
        h_mode.addWidget(self.rb_both)
        h_mode.addWidget(self.rb_temp)
        h_mode.addWidget(self.rb_energy)
        
        self.sb_potim = QDoubleSpinBox()
        self.sb_potim.setRange(0.1, 10.0)
        self.sb_potim.setValue(1.0)
        self.sb_potim.setSingleStep(0.5)
        
        l_mode.addLayout(h_mode)
        l_mode.addWidget(QLabel("Adım Süresi (POTIM, fs):"))
        l_mode.addWidget(self.sb_potim)
        group_mode.setLayout(l_mode)
        
        # 2. Files
        group_files = QGroupBox("2. AIMD Veri Dosyaları")
        self.l_files = QVBoxLayout()
        
        btn_add = QPushButton("+ Yeni Veri Ekle")
        btn_add.clicked.connect(self.add_data_slot)
        self.l_files.addWidget(btn_add)
        
        self.files_container = QVBoxLayout()
        self.l_files.addLayout(self.files_container)
        group_files.setLayout(self.l_files)
        
        # Initial 4 files as default in legacy
        for _ in range(4):
            self.add_data_slot()
            
        # 3. Ayarlar
        group_settings = QGroupBox("3. Eksen Sınırları")
        l_settings = QFormLayout()
        
        self.ls_x_max = QDoubleSpinBox(); self.ls_x_max.setRange(0, 100000); self.ls_x_max.setValue(20000)
        self.ls_x_step = QDoubleSpinBox(); self.ls_x_step.setRange(0, 10000); self.ls_x_step.setValue(4000)
        
        self.ls_t_min = QDoubleSpinBox(); self.ls_t_min.setRange(0, 10000); self.ls_t_min.setValue(0)
        self.ls_t_max = QDoubleSpinBox(); self.ls_t_max.setRange(0, 10000); self.ls_t_max.setValue(1000)
        self.ls_t_step = QDoubleSpinBox(); self.ls_t_step.setRange(0, 1000); self.ls_t_step.setValue(100)
        
        self.ls_e_min = QDoubleSpinBox(); self.ls_e_min.setRange(-10000, 10000); self.ls_e_min.setValue(-200)
        self.ls_e_max = QDoubleSpinBox(); self.ls_e_max.setRange(-10000, 10000); self.ls_e_max.setValue(-100)
        self.ls_e_step = QDoubleSpinBox(); self.ls_e_step.setRange(0.1, 1000); self.ls_e_step.setValue(2.0)
        
        l_settings.addRow("Maks Zaman (fs):", self.ls_x_max)
        l_settings.addRow("Zaman Adım:", self.ls_x_step)
        l_settings.addRow("Min Sıcaklık (K):", self.ls_t_min)
        l_settings.addRow("Maks Sıcaklık (K):", self.ls_t_max)
        l_settings.addRow("Sıcaklık Adım:", self.ls_t_step)
        l_settings.addRow("Min Enerji (eV):", self.ls_e_min)
        l_settings.addRow("Maks Enerji (eV):", self.ls_e_max)
        l_settings.addRow("Enerji Adım:", self.ls_e_step)
        group_settings.setLayout(l_settings)
        
        self.btn_plot = QPushButton("Verileri Oku ve Çiz")
        self.btn_plot.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 10px;")
        self.btn_plot.clicked.connect(self.process_and_plot)
        
        left_layout.addWidget(group_mode)
        left_layout.addWidget(group_files)
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
        self.figure = plt.figure(figsize=(10, 5))
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
        self.ls_font_title = QSpinBox(); self.ls_font_title.setRange(8, 40); self.ls_font_title.setValue(24)
        self.ls_font_tick = QSpinBox(); self.ls_font_tick.setRange(8, 40); self.ls_font_tick.setValue(20)
        self.cmb_leg_loc = QComboBox()
        self.cmb_leg_loc.addItems(["upper right", "upper left", "lower left", "lower right", "best"])
        self.cmb_leg_loc.setCurrentText("upper right")
        self.cb_leg_orient = QComboBox()
        self.cb_leg_orient.addItems(["Dikey", "Yatay"])
        
        self.le_mat_name = QLineEdit()
        self.le_mat_name.setPlaceholderText("Örn: MoS_2")
        
        layout.addRow("Başlık Punto:", self.ls_font_title)
        layout.addRow("Rakam Punto:", self.ls_font_tick)
        layout.addRow("Lejant Konumu:", self.cmb_leg_loc)
        layout.addRow("Lejant Dizilimi:", self.cb_leg_orient)
        layout.addRow("Malzeme İsmi:", self.le_mat_name)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.datasets:
            self.plot_graph()

    def add_data_slot(self):
        idx = len(self.data_files)
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0,0,0,0)
        
        le = QLineEdit(f"{300 + (idx*150)} K")
        btn = QPushButton("Dosya Seç")
        btn_color = QPushButton()
        
        default_colors = ['#E74C3C', '#3498DB', '#27AE60', '#F39C12', '#9B59B6', '#34495E', '#1ABC9C', '#D35400']
        c = default_colors[idx % len(default_colors)]
        btn_color.setStyleSheet(f"background-color: {c}; width: 20px; height: 20px;")
        
        item = {'label_le': le, 'file_path': None, 'btn': btn, 'color': c}
        
        def choose_file():
            fp, _ = QFileDialog.getOpenFileName(self, "Veri Seç", "", "Data Files (*.dat *.txt *.csv *.out);;All Files (*)")
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
        
        l.addWidget(le)
        l.addWidget(btn)
        l.addWidget(btn_color)
        
        self.files_container.addWidget(w)
        self.data_files.append(item)

    def process_and_plot(self):
        self.datasets = []
        global_t_max = 0
        global_temp_min, global_temp_max = 99999, -99999
        global_e_min, global_e_max = 99999, -99999
        potim_val = self.sb_potim.value()

        try:
            for item in self.data_files:
                if item['file_path']:
                    df = pd.read_csv(item['file_path'], sep=r'\s+', engine='python')
                    
                    if 'Time(fs)' not in df.columns:
                        if 'Time(ps)' in df.columns:
                            df['Time(fs)'] = df['Time(ps)'] * 1000
                        elif 'tep' in df.columns: 
                            df['Time(fs)'] = df['tep'] * potim_val
                        elif 'step' in df.columns.str.lower():
                            step_col = df.columns[df.columns.str.lower() == 'step'][0]
                            df['Time(fs)'] = df[step_col] * potim_val
                        else:
                            df['Time(fs)'] = (df.index + 1) * potim_val

                    if 'Temperature(K)' not in df.columns:
                        if 'Temperature_K' in df.columns: 
                            df['Temperature(K)'] = df['Temperature_K']
                        elif 'T(K)' in df.columns:
                            df['Temperature(K)'] = df['T(K)']
                        elif len(df.columns) > 1:
                            df['Temperature(K)'] = df.iloc[:, 1]

                    if 'Energy(eV)' not in df.columns:
                        if 'E_Kinetic_eV' in df.columns:
                            df['Energy(eV)'] = df['E_Kinetic_eV']
                        elif 'E_Total_eV' in df.columns: 
                            df['Energy(eV)'] = df['E_Total_eV']
                        elif len(df.columns) > 1:
                            df['Energy(eV)'] = df.iloc[:, -2]

                    if 'Time(fs)' in df.columns:
                        global_t_max = max(global_t_max, df['Time(fs)'].max())
                    if 'Temperature(K)' in df.columns:
                        global_temp_min = min(global_temp_min, df['Temperature(K)'].min())
                        global_temp_max = max(global_temp_max, df['Temperature(K)'].max())
                    if 'Energy(eV)' in df.columns:
                        global_e_min = min(global_e_min, df['Energy(eV)'].min())
                        global_e_max = max(global_e_max, df['Energy(eV)'].max())

                    self.datasets.append({
                        "df": df, 
                        "label": rf"$\mathbf{{{item['label_le'].text()}}}$", 
                        "color": item['color']
                    })

            if not self.datasets:
                QMessageBox.warning(self, "Hata", "Lütfen en az bir adet veri yükleyin.")
                return

            self.ls_x_max.setValue(global_t_max if global_t_max > 0 else 10000.0)
            self.ls_x_step.setValue(float(np.ceil(global_t_max/5)) if global_t_max > 0 else 2000.0)
            
            self.ls_t_min.setValue(np.floor(global_temp_min/50)*50 if global_temp_min != 99999 else 0.0)
            self.ls_t_max.setValue(np.ceil(global_temp_max/50)*50 if global_temp_max != -99999 else 1000.0)
            
            self.ls_e_min.setValue(np.floor(global_e_min) if global_e_min != 99999 else -200.0)
            self.ls_e_max.setValue(np.ceil(global_e_max) if global_e_max != -99999 else -100.0)
            
            self.plot_graph()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Okuma hatası:\n{e}")

    def plot_graph(self):
        if not self.datasets: return
        
        self.figure.clear()
        
        mode_id = self.bg_mode.checkedId()
        mode_str = "both" if mode_id == 1 else "temp" if mode_id == 2 else "energy"
        
        p_t_min, p_t_max, p_t_step = self.ls_t_min.value(), self.ls_t_max.value(), self.ls_t_step.value()
        p_e_min, p_e_max, p_e_step = self.ls_e_min.value(), self.ls_e_max.value(), self.ls_e_step.value()
        p_x_max, p_x_step = self.ls_x_max.value(), self.ls_x_step.value()

        if mode_str == "temp":
            selected_metrics = [('Temperature(K)', 'Temperature (K)', (p_t_min, p_t_max), p_t_step)]
        elif mode_str == "energy":
            selected_metrics = [('Energy(eV)', 'Total Energy (eV)', (p_e_min, p_e_max), p_e_step)]
        else:
            selected_metrics = [
                ('Temperature(K)', 'Temperature (K)', (p_t_min, p_t_max), p_t_step), 
                ('Energy(eV)', 'Total Energy (eV)', (p_e_min, p_e_max), p_e_step)
            ]

        num_cols = len(selected_metrics)
        apply_global_style()
        axs = self.figure.subplots(1, num_cols, squeeze=False)

        leg_ncol = len(self.datasets) if self.cb_leg_orient.currentText() == "Yatay" else 1
        panel_labels = ["(a)", "(b)"]

        for col in range(num_cols):
            ax = axs[0, col]
            m_col, ylabel, y_limits, y_step = selected_metrics[col]
            
            for i, data in enumerate(self.datasets):
                df = data["df"]
                if m_col in df.columns:
                    ax.plot(df['Time(fs)'], df[m_col], color=data["color"], linewidth=2.5, 
                            label=data["label"], alpha=0.85, zorder=10-i)
            
            ax.set_ylabel(ylabel, fontsize=self.ls_font_title.value(), fontweight='bold', labelpad=20)
            ax.set_xlabel('Time (fs)', fontsize=self.ls_font_title.value(), fontweight='bold', labelpad=20)
            ax.set_xlim(0, p_x_max)
            ax.set_ylim(y_limits[0], y_limits[1])

            ax.xaxis.set_major_locator(MultipleLocator(p_x_step))
            ax.yaxis.set_major_locator(MultipleLocator(y_step))
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))
            ax.yaxis.set_minor_locator(AutoMinorLocator(2))

            ax.tick_params(axis='both', which='major', direction='in', length=12, width=2.5, labelsize=self.ls_font_tick.value(), pad=10, top=False, right=False)
            ax.tick_params(axis='both', which='minor', direction='in', length=6, width=1.5, top=False, right=False)

            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight('bold')
            for spine in ax.spines.values():
                spine.set_linewidth(2.5)

            if mode_str == "both" or num_cols > 1:
                ax.text(0.15, 0.15, panel_labels[col], transform=ax.transAxes, 
                        fontsize=self.ls_font_title.value(), fontweight='bold', va='center', ha='center')

            if self.le_mat_name.text().strip() != "":
                ax.text(0.05, 0.92, fr"${self.le_mat_name.text()}$", transform=ax.transAxes, 
                        fontsize=self.ls_font_title.value(), fontweight='bold', va='center', ha='left')

            if col == 0:
                leg = ax.legend(loc=self.cmb_leg_loc.currentText(), ncol=leg_ncol, fontsize=18, frameon=True, edgecolor='black', framealpha=0.9)
                leg.get_frame().set_linewidth(1.5)
                leg.set_draggable(True)

        self.figure.tight_layout(pad=3.0)
        self.figure.subplots_adjust(wspace=0.15)
        self.canvas.draw()
