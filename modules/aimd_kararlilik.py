import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QFormLayout, QGroupBox, QMessageBox, QDoubleSpinBox,
    QScrollArea, QLineEdit, QComboBox, QSpinBox, QRadioButton, QButtonGroup,
    QColorDialog
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from utils.style_manager import apply_global_style, notifier

class AIMDFileWidget(QWidget):
    def __init__(self, idx, parent):
        super().__init__()
        self.idx = idx
        self.parent_mod = parent
        self.file_path = ""
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.le_label = QLineEdit(f"{300 + (idx*150)} K")
        
        self.btn_color = QPushButton("Renk")
        default_colors = ['#E74C3C', '#3498DB', '#27AE60', '#F39C12', '#9B59B6', '#34495E', '#1ABC9C', '#D35400']
        self.color = default_colors[idx % len(default_colors)]
        self.btn_color.setStyleSheet(f"background-color: {self.color}; color: white; font-weight: bold;")
        self.btn_color.clicked.connect(self.choose_color)
        
        self.btn_load = QPushButton("Dosya")
        self.btn_load.clicked.connect(self.load_file)
        self.lbl_status = QLabel("❌")
        
        layout.addWidget(self.le_label)
        layout.addWidget(self.btn_color)
        layout.addWidget(self.btn_load)
        layout.addWidget(self.lbl_status)
        
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color = color.name()
            self.btn_color.setStyleSheet(f"background-color: {self.color}; color: white; font-weight: bold;")
            
    def load_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, f'{self.le_label.text()} Dosyası', '', 'Data (*.dat *.txt);;All (*)')
        if fname:
            self.file_path = fname
            self.btn_load.setText(self.file_path.split("/")[-1].split("\\")[-1][:8] + "...")
            self.lbl_status.setText("✅")


class AIMDKararlilikWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        c_layout = QVBoxLayout(content)
        
        mode_group = QGroupBox("Grafik Modu")
        m_layout = QVBoxLayout(mode_group)
        self.rb_both = QRadioButton("İkisi Yan Yana (Both)")
        self.rb_temp = QRadioButton("Sadece Sıcaklık")
        self.rb_ener = QRadioButton("Sadece Enerji")
        self.rb_both.setChecked(True)
        self.bg_mode = QButtonGroup()
        self.bg_mode.addButton(self.rb_both)
        self.bg_mode.addButton(self.rb_temp)
        self.bg_mode.addButton(self.rb_ener)
        m_layout.addWidget(self.rb_both)
        m_layout.addWidget(self.rb_temp)
        m_layout.addWidget(self.rb_ener)
        c_layout.addWidget(mode_group)
        
        data_group = QGroupBox("Veri Setleri")
        d_layout = QVBoxLayout(data_group)
        hl = QHBoxLayout()
        hl.addWidget(QLabel("Karşılaştırılacak Veri Sayısı:"))
        self.sp_count = QSpinBox()
        self.sp_count.setRange(1, 8)
        self.sp_count.setValue(4)
        self.sp_count.valueChanged.connect(self.update_count)
        hl.addWidget(self.sp_count)
        d_layout.addLayout(hl)
        
        self.file_widgets = []
        for i in range(8):
            fw = AIMDFileWidget(i, self)
            self.file_widgets.append(fw)
            d_layout.addWidget(fw)
            
        c_layout.addWidget(data_group)
        
        scroll.setWidget(content)
        left_layout.addWidget(scroll)
        
        self.btn_calc = QPushButton("Verileri Oku ve Grafiği Hazırla")
        self.btn_calc.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.process_data)
        left_layout.addWidget(self.btn_calc)
        
        # Right Panel (Plot)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.figure = Figure(figsize=(14, 7))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.update_count(4)
        self.datasets = []
        
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)
        
    def update_count(self, count):
        for i, fw in enumerate(self.file_widgets):
            fw.setVisible(i < count)
            
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        c_layout = QFormLayout(content)
        
        self.ls_x_max = QDoubleSpinBox(); self.ls_x_max.setRange(0, 10000000); self.ls_x_max.setValue(10000); self.ls_x_max.setSingleStep(1000)
        self.ls_x_step = QDoubleSpinBox(); self.ls_x_step.setRange(0, 10000000); self.ls_x_step.setValue(2000); self.ls_x_step.setSingleStep(1000)
        
        c_layout.addRow("Maks Zaman (fs):", self.ls_x_max)
        c_layout.addRow("Zaman Adımı:", self.ls_x_step)
        
        self.ls_t_min = QDoubleSpinBox(); self.ls_t_min.setRange(0, 100000); self.ls_t_min.setValue(0); self.ls_t_min.setSingleStep(50)
        self.ls_t_max = QDoubleSpinBox(); self.ls_t_max.setRange(0, 100000); self.ls_t_max.setValue(1000); self.ls_t_max.setSingleStep(50)
        self.ls_t_step = QDoubleSpinBox(); self.ls_t_step.setRange(0, 100000); self.ls_t_step.setValue(100); self.ls_t_step.setSingleStep(50)
        
        c_layout.addRow("Min Sıcaklık:", self.ls_t_min)
        c_layout.addRow("Maks Sıcaklık:", self.ls_t_max)
        c_layout.addRow("Sıcaklık Adımı:", self.ls_t_step)
        
        self.ls_e_min = QDoubleSpinBox(); self.ls_e_min.setRange(-1000000, 1000000); self.ls_e_min.setValue(-100); self.ls_e_min.setSingleStep(1)
        self.ls_e_max = QDoubleSpinBox(); self.ls_e_max.setRange(-1000000, 1000000); self.ls_e_max.setValue(0); self.ls_e_max.setSingleStep(1)
        self.ls_e_step = QDoubleSpinBox(); self.ls_e_step.setRange(0.1, 100000); self.ls_e_step.setValue(2); self.ls_e_step.setSingleStep(1)
        
        c_layout.addRow("Min Enerji:", self.ls_e_min)
        c_layout.addRow("Maks Enerji:", self.ls_e_max)
        c_layout.addRow("Enerji Adımı:", self.ls_e_step)
        
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
        if self.datasets:
            apply_global_style()
            self.plot_graph()
            
    def process_data(self):
        count = self.sp_count.value()
        self.datasets = []
        
        g_t_max = 0
        g_temp_min, g_temp_max = 99999, -99999
        g_e_min, g_e_max = 99999, -99999
        
        try:
            apply_global_style()
            for i in range(count):
                fw = self.file_widgets[i]
                if fw.file_path:
                    # Daha sağlam okuma (Normalize headers)
                    try:
                        df = pd.read_csv(fw.file_path, sep=r'\s+', on_bad_lines='skip')
                    except Exception:
                        continue
                        
                    # E0_eV varsa her zaman önceliklidir
                    e0_col_name = None
                    for c in df.columns:
                        c_low = str(c).replace('#', '').strip().lower()
                        if c_low == 'e0' or 'e0_ev' in c_low or 'e0(ev)' in c_low:
                            e0_col_name = c
                            break

                    new_cols = []
                    found_energy = False
                    found_time = False
                    found_temp = False
                    for c in df.columns:
                        c_low = str(c).replace('#', '').strip().lower()
                        if not found_time and ('time' in c_low and 'ps' in c_low):
                            new_cols.append('Time(ps)')
                            found_time = True
                        elif not found_time and ('time' in c_low or c_low == 'step'):
                            new_cols.append('Time(fs)')
                            found_time = True
                        elif not found_temp and ('temp' in c_low):
                            new_cols.append('Temperature(K)')
                            found_temp = True
                        elif not found_energy:
                            if e0_col_name is not None:
                                if c == e0_col_name:
                                    new_cols.append('Energy(eV)')
                                    found_energy = True
                                else:
                                    new_cols.append(c)
                            elif 'e_total' in c_low or 'etotal' in c_low or 'energy' in c_low or c_low == 'e' or 'e(ev)' in c_low:
                                new_cols.append('Energy(eV)')
                                found_energy = True
                            else:
                                new_cols.append(c)
                        else:
                            new_cols.append(c)
                            
                    df.columns = new_cols
                    
                    # Eğer hala sıcaklık veya enerji yoksa, büyük ihtimalle dosya başlıksız (header yok)
                    if 'Temperature(K)' not in df.columns and 'Energy(eV)' not in df.columns:
                        try:
                            df = pd.read_csv(fw.file_path, sep=r'\s+', header=None, comment='#', on_bad_lines='skip')
                            if len(df.columns) >= 3:
                                df.columns = ['Time(fs)', 'Temperature(K)', 'Energy(eV)'] + list(df.columns[3:])
                            elif len(df.columns) == 2:
                                df.columns = ['Time(fs)', 'Energy(eV)']
                        except:
                            pass
                    
                    if 'Time(ps)' in df.columns and 'Time(fs)' not in df.columns:
                        df['Time(fs)'] = pd.to_numeric(df['Time(ps)'], errors='coerce') * 1000
                    elif 'Time(fs)' not in df.columns:
                        df['Time(fs)'] = df.index 
                        
                    for col in ['Time(fs)', 'Temperature(K)', 'Energy(eV)']:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                            
                    # Drop rows where both Temperature and Energy are NaN (if they exist)
                    cols_to_check = [c for c in ['Temperature(K)', 'Energy(eV)'] if c in df.columns]
                    if cols_to_check:
                        df = df.dropna(subset=cols_to_check, how='all')
                        
                    if 'Time(fs)' in df.columns: g_t_max = max(g_t_max, df['Time(fs)'].max())
                    if 'Temperature(K)' in df.columns:
                        g_temp_min = min(g_temp_min, df['Temperature(K)'].min())
                        g_temp_max = max(g_temp_max, df['Temperature(K)'].max())
                    if 'Energy(eV)' in df.columns:
                        g_e_min = min(g_e_min, df['Energy(eV)'].min())
                        g_e_max = max(g_e_max, df['Energy(eV)'].max())
                        
                    self.datasets.append({
                        "df": df, 
                        "label": rf"$\mathbf{{{fw.le_label.text()}}}$", 
                        "color": fw.color
                    })
                    
            if not self.datasets:
                QMessageBox.warning(self, "Hata", "Lütfen en az bir veri dosyası yükleyin!")
                return
                
            self.ls_x_max.setValue(float(g_t_max) if g_t_max > 0 else 10000.0)
            self.ls_x_step.setValue(float(np.ceil((float(g_t_max) if g_t_max > 0 else 10000.0) / 5)))
            
            if g_temp_min != 99999: 
                self.ls_t_min.setValue(float(np.floor(g_temp_min/50)*50))
            if g_temp_max != -99999: 
                self.ls_t_max.setValue(float(np.ceil(g_temp_max/50)*50))
                if g_temp_min != 99999:
                    t_range = g_temp_max - g_temp_min
                    self.ls_t_step.setValue(float(np.ceil(t_range / 5)) if t_range > 0 else 50.0)
            
            if g_e_min != 99999: 
                self.ls_e_min.setValue(float(np.floor(g_e_min)))
            if g_e_max != -99999: 
                self.ls_e_max.setValue(float(np.ceil(g_e_max)))
                if g_e_min != 99999:
                    e_range = g_e_max - g_e_min
                    # Minimum step 0.1, yoksa çok fazla tick üretilir
                    calc_step = float(np.ceil(e_range / 6))
                    self.ls_e_step.setValue(calc_step if calc_step >= 0.1 else 0.5)
            
            self.plot_graph()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veri okuma hatası:\n{e}")
            
    def plot_graph(self):
        if not self.datasets: return
        
        self.figure.clear()
        
        mode = "both"
        if self.rb_temp.isChecked(): mode = "temp"
        elif self.rb_ener.isChecked(): mode = "energy"
        
        if mode == "temp":
            selected_metrics = [('Temperature(K)', 'Temperature (K)', (self.ls_t_min.value(), self.ls_t_max.value()), self.ls_t_step.value())]
        elif mode == "energy":
            selected_metrics = [('Energy(eV)', 'Total Energy (eV)', (self.ls_e_min.value(), self.ls_e_max.value()), self.ls_e_step.value())]
        else:
            selected_metrics = [
                ('Temperature(K)', 'Temperature (K)', (self.ls_t_min.value(), self.ls_t_max.value()), self.ls_t_step.value()), 
                ('Energy(eV)', 'Total Energy (eV)', (self.ls_e_min.value(), self.ls_e_max.value()), self.ls_e_step.value())
            ]
            
        num_cols = len(selected_metrics)
        axs = self.figure.subplots(1, num_cols, squeeze=False)
        
        for col in range(num_cols):
            ax = axs[0, col]
            m_col, ylabel, y_limits, y_step = selected_metrics[col]
            
            for i, data in enumerate(self.datasets):
                df = data["df"]
                if m_col in df.columns:
                    valid_df = df.dropna(subset=[m_col, 'Time(fs)'])
                    if not valid_df.empty:
                        ax.plot(valid_df['Time(fs)'], valid_df[m_col], color=data["color"], linewidth=2.5, 
                                label=data["label"], alpha=0.85, zorder=10-i)
                            
            ax.set_ylabel(ylabel, fontsize=16, fontweight='bold', labelpad=15)
            ax.set_xlabel('Time (fs)', fontsize=16, fontweight='bold', labelpad=15)
            ax.set_xlim(0, self.ls_x_max.value())
            ax.set_ylim(y_limits[0], y_limits[1])
            
            ax.xaxis.set_major_locator(MultipleLocator(self.ls_x_step.value()))
            ax.yaxis.set_major_locator(MultipleLocator(y_step))
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))
            ax.yaxis.set_minor_locator(AutoMinorLocator(2))
            
            if col == 0:
                leg = ax.legend(loc=self.ls_leg_loc.currentText(), frameon=True)
                leg.set_draggable(True)
                
        self.figure.tight_layout()
        self.canvas.draw()
