import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QFormLayout, QGroupBox, QMessageBox, QDoubleSpinBox,
    QScrollArea, QLineEdit, QComboBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from utils.style_manager import apply_global_style, notifier

class KinetikMSDWidget(QWidget):
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
        
        self.btn_load_msd = QPushButton("MSD.dat Yükle")
        self.btn_load_msd.clicked.connect(self.load_msd)
        self.lbl_msd = QLabel("Yüklenmedi")
        
        self.btn_load_diff = QPushButton("DIFFUSION_COEFFICIENT.dat Yükle")
        self.btn_load_diff.clicked.connect(self.load_diff)
        self.lbl_diff = QLabel("Yüklenmedi")
        
        data_layout.addRow(self.btn_load_msd, self.lbl_msd)
        data_layout.addRow(self.btn_load_diff, self.lbl_diff)
        data_group.setLayout(data_layout)
        
        # Calculate Button
        self.btn_calc = QPushButton("Verileri Oku ve Grafiği Hazırla")
        self.btn_calc.clicked.connect(self.process_data)
        self.btn_calc.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        
        # Result Labels
        self.lbl_time = QLabel("")
        self.lbl_D = QLabel("")
        self.lbl_time.setStyleSheet("color: blue; font-weight: bold;")
        self.lbl_D.setStyleSheet("color: red; font-weight: bold;")
        
        left_layout.addWidget(data_group)
        left_layout.addWidget(self.btn_calc)
        left_layout.addWidget(self.lbl_time)
        left_layout.addWidget(self.lbl_D)
        left_layout.addStretch()
        
        # Right Panel (Plot)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.figure = Figure(figsize=(12, 5))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        # Data state
        self.msd_path = ""
        self.diff_path = ""
        self.msd_df = None
        self.diff_df = None
        self.time_max = 0
        self.msd_max = 0
        self.diff_max = 0
        self.final_D = 0
        
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)
        
    def load_msd(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'MSD.dat Aç', '', 'Data Files (*.dat *.txt);;All Files (*)')
        if fname:
            self.msd_path = fname
            self.lbl_msd.setText("Yüklendi")
            
    def load_diff(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'DIFFUSION_COEFFICIENT.dat Aç', '', 'Data Files (*.dat *.txt);;All Files (*)')
        if fname:
            self.diff_path = fname
            self.lbl_diff.setText("Yüklendi")
            
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        c_layout = QFormLayout(content)
        
        self.ls_x_min = QDoubleSpinBox(); self.ls_x_min.setRange(0, 1e7); self.ls_x_min.setValue(0); self.ls_x_min.setSingleStep(1000)
        self.ls_x_max = QDoubleSpinBox(); self.ls_x_max.setRange(0, 1e7); self.ls_x_max.setValue(50000); self.ls_x_max.setSingleStep(1000)
        self.ls_x_step = QDoubleSpinBox(); self.ls_x_step.setRange(10, 1e6); self.ls_x_step.setValue(10000); self.ls_x_step.setSingleStep(1000)
        c_layout.addRow("Ortak X Başlangıç (fs):", self.ls_x_min)
        c_layout.addRow("Ortak X Bitiş (fs):", self.ls_x_max)
        c_layout.addRow("Ortak X Aralık (Tick):", self.ls_x_step)
        
        self.ls_y1_max = QDoubleSpinBox(); self.ls_y1_max.setRange(0, 1000); self.ls_y1_max.setValue(10); self.ls_y1_max.setSingleStep(0.5)
        self.ls_y1_step = QDoubleSpinBox(); self.ls_y1_step.setRange(0.1, 100); self.ls_y1_step.setValue(1.0); self.ls_y1_step.setSingleStep(0.5)
        c_layout.addRow("(a) Maks MSD (Å²):", self.ls_y1_max)
        c_layout.addRow("(a) MSD Aralık:", self.ls_y1_step)
        
        self.ls_y2_max = QDoubleSpinBox(); self.ls_y2_max.setRange(0, 100); self.ls_y2_max.setValue(2.0); self.ls_y2_max.setSingleStep(0.1)
        self.ls_y2_step = QDoubleSpinBox(); self.ls_y2_step.setRange(0.01, 10); self.ls_y2_step.setValue(0.2); self.ls_y2_step.setSingleStep(0.1)
        c_layout.addRow("(b) Maks Difüzyon (10⁻⁴):", self.ls_y2_max)
        c_layout.addRow("(b) Difüzyon Aralık:", self.ls_y2_step)
        
        self.ls_l_x = QLineEdit("x-direction")
        self.ls_l_y = QLineEdit("y-direction")
        self.ls_l_z = QLineEdit("z-direction")
        self.ls_l_tot = QLineEdit("Total")
        c_layout.addRow("X Yönü İsmi:", self.ls_l_x)
        c_layout.addRow("Y Yönü İsmi:", self.ls_l_y)
        c_layout.addRow("Z Yönü İsmi:", self.ls_l_z)
        c_layout.addRow("Total İsmi:", self.ls_l_tot)
        
        self.ls_box_x = QDoubleSpinBox(); self.ls_box_x.setRange(0, 1.0); self.ls_box_x.setValue(0.95); self.ls_box_x.setSingleStep(0.05)
        self.ls_box_y = QDoubleSpinBox(); self.ls_box_y.setRange(0, 1.0); self.ls_box_y.setValue(0.15); self.ls_box_y.setSingleStep(0.05)
        c_layout.addRow("D Kutusu X (0-1):", self.ls_box_x)
        c_layout.addRow("D Kutusu Y (0-1):", self.ls_box_y)
        
        btn_apply = QPushButton("Yerel Ayarları Uygula")
        btn_apply.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 10px;")
        btn_apply.clicked.connect(self.plot_graph)
        c_layout.addRow(btn_apply)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.msd_df is not None and self.diff_df is not None:
            apply_global_style()
            self.plot_graph()
            
    def process_data(self):
        if not self.msd_path or not self.diff_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen her iki dosyayı da yükleyin.")
            return
            
        try:
            apply_global_style()
            
            self.msd_df = pd.read_csv(self.msd_path, sep=r'\s+', comment='#', header=None, engine='python').dropna().reset_index(drop=True)
            self.diff_df = pd.read_csv(self.diff_path, sep=r'\s+', comment='#', header=None, engine='python').dropna().reset_index(drop=True)
            
            self.time_max = float(self.msd_df[0].iloc[-1])
            self.msd_max = float(self.msd_df[4].max())
            self.diff_max = float((self.diff_df[4] * 1e4).max())
            self.final_D = self.diff_df[4].iloc[-1]
            
            # Update auto values if first time
            self.ls_x_max.setValue(float(self.time_max))
            self.ls_x_step.setValue(float(np.ceil(self.time_max/6)))
            self.ls_y1_max.setValue(float(np.ceil(self.msd_max)))
            self.ls_y2_max.setValue(float(np.ceil(self.diff_max*10)/10))
            
            self.lbl_time.setText(f"Süre: {self.time_max:.0f} fs")
            self.lbl_D.setText(f"D_tot = {self.final_D:.4e} cm²/s")
            
            self.plot_graph()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya okunurken hata oluştu:\n{e}")
            
    def plot_graph(self):
        if self.msd_df is None or self.diff_df is None: return
        
        self.figure.clear()
        axes = self.figure.subplots(1, 2)
        ax1, ax2 = axes[0], axes[1]
        
        colors = ['#1f77b4', '#2ca02c', '#ff7f0e', 'black']
        labels = [self.ls_l_x.text(), self.ls_l_y.text(), self.ls_l_z.text(), self.ls_l_tot.text()]
        line_styles = ['-.', '-.', '-.', '-']
        line_widths = [2.5, 2.5, 2.5, 4.0]

        # Panel a: MSD
        time_msd = self.msd_df[0]
        for i, col in enumerate([1, 2, 3, 4]):
            ax1.plot(time_msd, self.msd_df[col], color=colors[i], linestyle=line_styles[i], 
                     linewidth=line_widths[i], alpha=0.9 if i<3 else 1.0, label=labels[i])

        ax1.set_xlabel(r'Time ($t$, fs)', fontweight='bold', labelpad=15)
        ax1.set_ylabel(r'Mean Square Displacement ($\mathbf{\AA}^2$)', fontweight='bold', color='black', labelpad=15)
        ax1.set_xlim(self.ls_x_min.value(), self.ls_x_max.value())
        ax1.set_ylim(0, self.ls_y1_max.value())
        
        ax1.text(0.04, 0.94, "(a) Mean Square Displacement", transform=ax1.transAxes, fontsize=14, fontweight='bold', va='top')
        leg = ax1.legend(loc='upper left', bbox_to_anchor=(0.02, 0.85), frameon=False, ncol=2)
        leg.set_draggable(True)

        # Panel b: Diffusion
        time_diff = self.diff_df[0]
        for i, col in enumerate([1, 2, 3, 4]):
            y_data = self.diff_df[col] * 1e4 
            ax2.plot(time_diff, y_data, color=colors[i], linestyle=line_styles[i], 
                     linewidth=line_widths[i], alpha=0.9 if i<3 else 1.0)

        ax2.set_xlabel(r'Time ($t$, fs)', fontweight='bold', labelpad=15)
        ax2.set_ylabel(r'Diffusion Coefficient ($D$, $10^{-4}$ cm$^2$/s)', fontweight='bold', color='black', labelpad=15)
        ax2.set_xlim(self.ls_x_min.value(), self.ls_x_max.value())
        ax2.set_ylim(0, self.ls_y2_max.value())
        
        ax2.text(0.04, 0.94, "(b) Time-Dependent Diffusion", transform=ax2.transAxes, fontsize=14, fontweight='bold', va='top')

        if self.final_D > 0:
            exponent = int(np.floor(np.log10(abs(self.final_D))))
            mantissa = self.final_D / 10**exponent
            d_latex_str = f"{mantissa:.2f} \\times 10^{{{exponent}}}"
        else:
            d_latex_str = "0.00"

        ax2.text(self.ls_box_x.value(), self.ls_box_y.value(), f"Converged $D_{{tot}} = {d_latex_str}$ cm$^2$/s", 
                 transform=ax2.transAxes, fontweight='bold', 
                 color='black', ha='right' if self.ls_box_x.value() > 0.5 else 'left', va='bottom',
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.4'))

        for ax in axes:
            ax.xaxis.set_major_locator(MultipleLocator(self.ls_x_step.value()))
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))
            
        ax1.yaxis.set_major_locator(MultipleLocator(self.ls_y1_step.value()))
        ax2.yaxis.set_major_locator(MultipleLocator(self.ls_y2_step.value()))
        ax1.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax2.yaxis.set_minor_locator(AutoMinorLocator(2))

        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()
