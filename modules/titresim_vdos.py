import pandas as pd
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QFormLayout, QGroupBox, QMessageBox, QDoubleSpinBox,
    QScrollArea, QLineEdit, QComboBox, QSpinBox, QCheckBox, QSlider
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
from utils.style_manager import apply_global_style, notifier

class PartialFileWidget(QWidget):
    def __init__(self, idx, parent):
        super().__init__()
        self.idx = idx
        self.parent_mod = parent
        self.file_path = ""
        self.df = None
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        default_labels = ["H", "Ti", "K", "O", "C", "N"]
        self.le_label = QLineEdit(default_labels[idx] if idx < 6 else f"Atom-{idx+1}")
        
        self.btn_load = QPushButton(f"Dosya ({self.le_label.text()})")
        self.btn_load.clicked.connect(self.load_file)
        self.lbl_status = QLabel("❌")
        
        layout.addWidget(self.le_label)
        layout.addWidget(self.btn_load)
        layout.addWidget(self.lbl_status)
        
    def load_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, f'{self.le_label.text()} Dosyası', '', 'Data (*.dat *.txt);;All (*)')
        if fname:
            self.file_path = fname
            self.btn_load.setText(self.file_path.split("/")[-1].split("\\")[-1][:10] + "...")
            self.lbl_status.setText("✅")

class TitresimVDOSWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)
        
        data_group = QGroupBox("Veri Yükleme")
        d_layout = QFormLayout()
        
        self.inp_formula = QLineEdit(r"\mathbf{K_2TiH_5}")
        
        self.btn_total = QPushButton("Total VDoS Yükle")
        self.btn_total.clicked.connect(self.load_total)
        self.lbl_total = QLabel("❌")
        
        d_layout.addRow("Formül (LaTeX):", self.inp_formula)
        d_layout.addRow(self.btn_total, self.lbl_total)
        data_group.setLayout(d_layout)
        
        partial_group = QGroupBox("Partial VDoS")
        p_layout = QVBoxLayout()
        self.spin_partials = QSpinBox()
        self.spin_partials.setRange(0, 6)
        self.spin_partials.setValue(3)
        self.spin_partials.valueChanged.connect(self.update_partials)
        
        form_p = QFormLayout()
        form_p.addRow("Kaç Adet Partial:", self.spin_partials)
        p_layout.addLayout(form_p)
        
        self.partial_widgets = []
        for i in range(6):
            pw = PartialFileWidget(i, self)
            self.partial_widgets.append(pw)
            p_layout.addWidget(pw)
            
        partial_group.setLayout(p_layout)
        
        self.btn_calc = QPushButton("Verileri Oku ve Grafiği Hazırla")
        self.btn_calc.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.process_data)
        
        left_layout.addWidget(data_group)
        left_layout.addWidget(partial_group)
        left_layout.addWidget(self.btn_calc)
        left_layout.addStretch()
        
        # Right Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.figure = Figure(figsize=(10, 7))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.total_path = ""
        self.total_df = None
        self.valid_partials = []
        self.peak_freq = 0
        self.peak_int = 0
        
        self.update_partials(3)
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)
        
    def load_total(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Total VDoS Aç', '', 'Data (*.dat *.txt);;All (*)')
        if fname:
            self.total_path = fname
            self.btn_total.setText(fname.split("/")[-1].split("\\")[-1][:12] + "...")
            self.lbl_total.setText("✅")
            
    def update_partials(self, count):
        for i, pw in enumerate(self.partial_widgets):
            pw.setVisible(i < count)
            
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        c_layout = QFormLayout(content)
        
        self.ls_x_min = QDoubleSpinBox(); self.ls_x_min.setRange(0, 1000); self.ls_x_min.setValue(0); self.ls_x_min.setSingleStep(5)
        self.ls_x_max = QDoubleSpinBox(); self.ls_x_max.setRange(0, 1000); self.ls_x_max.setValue(100); self.ls_x_max.setSingleStep(5)
        self.ls_x_step = QDoubleSpinBox(); self.ls_x_step.setRange(1, 100); self.ls_x_step.setValue(10); self.ls_x_step.setSingleStep(5)
        
        self.ls_y_min = QDoubleSpinBox(); self.ls_y_min.setRange(0, 1000); self.ls_y_min.setValue(0); self.ls_y_min.setSingleStep(10)
        self.ls_y_max = QDoubleSpinBox(); self.ls_y_max.setRange(0, 1000); self.ls_y_max.setValue(50); self.ls_y_max.setSingleStep(10)
        self.ls_y_step = QDoubleSpinBox(); self.ls_y_step.setRange(1, 100); self.ls_y_step.setValue(10); self.ls_y_step.setSingleStep(5)
        
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
        
        self.ls_minor = QCheckBox("Minör Çentikleri Göster")
        self.ls_minor.setChecked(True)
        c_layout.addRow(self.ls_minor)
        
        # Inset settings
        inset_grp = QGroupBox("Büyüteç (Inset)")
        i_layout = QFormLayout(inset_grp)
        self.ls_inset_act = QCheckBox("Aktif")
        self.ls_in_xmin = QDoubleSpinBox(); self.ls_in_xmin.setRange(0, 500); self.ls_in_xmin.setValue(60); self.ls_in_xmin.setSingleStep(5)
        self.ls_in_xmax = QDoubleSpinBox(); self.ls_in_xmax.setRange(0, 500); self.ls_in_xmax.setValue(90); self.ls_in_xmax.setSingleStep(5)
        self.ls_in_ymin = QDoubleSpinBox(); self.ls_in_ymin.setRange(0, 500); self.ls_in_ymin.setValue(0); self.ls_in_ymin.setSingleStep(0.01)
        self.ls_in_ymax = QDoubleSpinBox(); self.ls_in_ymax.setRange(0, 500); self.ls_in_ymax.setValue(0.05); self.ls_in_ymax.setSingleStep(0.01)
        
        self.ls_in_locx = QDoubleSpinBox(); self.ls_in_locx.setRange(0, 1); self.ls_in_locx.setValue(0.65); self.ls_in_locx.setSingleStep(0.05)
        self.ls_in_locy = QDoubleSpinBox(); self.ls_in_locy.setRange(0, 1); self.ls_in_locy.setValue(0.55); self.ls_in_locy.setSingleStep(0.05)
        self.ls_in_w = QDoubleSpinBox(); self.ls_in_w.setRange(0.1, 1); self.ls_in_w.setValue(0.3); self.ls_in_w.setSingleStep(0.05)
        self.ls_in_h = QDoubleSpinBox(); self.ls_in_h.setRange(0.1, 1); self.ls_in_h.setValue(0.3); self.ls_in_h.setSingleStep(0.05)
        
        i_layout.addRow(self.ls_inset_act)
        i_layout.addRow("Inset X Min/Max:", self.ls_in_xmin)
        i_layout.addRow("", self.ls_in_xmax)
        i_layout.addRow("Inset Y Min/Max:", self.ls_in_ymin)
        i_layout.addRow("", self.ls_in_ymax)
        i_layout.addRow("Konum X/Y:", self.ls_in_locx)
        i_layout.addRow("", self.ls_in_locy)
        i_layout.addRow("Genişlik/Yükseklik:", self.ls_in_w)
        i_layout.addRow("", self.ls_in_h)
        c_layout.addRow(inset_grp)
        
        btn_apply = QPushButton("Yerel Ayarları Uygula")
        btn_apply.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 10px;")
        btn_apply.clicked.connect(self.plot_graph)
        c_layout.addRow(btn_apply)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.total_df is not None:
            apply_global_style()
            self.plot_graph()
            
    def process_data(self):
        if not self.total_path:
            QMessageBox.warning(self, "Hata", "Lütfen Total VDoS dosyasını yükleyin!")
            return
            
        try:
            apply_global_style()
            
            self.total_df = pd.read_csv(self.total_path, sep=r'\s+', comment='#', names=['Freq', 'Int'])
            self.total_df = self.total_df.dropna().query('Freq >= 0').reset_index(drop=True)
            
            self.valid_partials = []
            for i in range(self.spin_partials.value()):
                pw = self.partial_widgets[i]
                if pw.file_path:
                    pdf = pd.read_csv(pw.file_path, sep=r'\s+', comment='#', names=['Freq', 'Int'])
                    pdf = pdf.dropna().query('Freq >= 0').reset_index(drop=True)
                    self.valid_partials.append({"label": pw.le_label.text(), "df": pdf})
                    
            auto_x_max = float(np.ceil(self.total_df['Freq'].max() / 5) * 5)
            auto_y_max = float(np.ceil(self.total_df['Int'].max() / 10) * 10)
            
            self.ls_x_max.setValue(auto_x_max)
            self.ls_y_max.setValue(auto_y_max)
            self.ls_y_step.setValue(float(np.ceil(auto_y_max/6)))
            
            max_idx = self.total_df['Int'].idxmax()
            self.peak_freq = self.total_df['Freq'].iloc[max_idx]
            self.peak_int = self.total_df['Int'].iloc[max_idx]
            
            self.plot_graph()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya okunurken hata oluştu:\n{e}")
            
    def plot_graph(self):
        if self.total_df is None: return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        t_color = "#2c3e50"
        colors = ['#2980b9', '#e67e22', '#27ae60', '#8e44ad', '#c0392b', '#f39c12']
        
        # Total Plot
        ax.plot(self.total_df['Freq'], self.total_df['Int'], color=t_color, lw=2.5, ls='-', label='Total VDoS', zorder=2)
        ax.fill_between(self.total_df['Freq'], self.total_df['Int'], color=t_color, alpha=0.1, zorder=1)
        
        # Partial Plot
        for i, p in enumerate(self.valid_partials):
            c = colors[i % len(colors)]
            ax.plot(p["df"]['Freq'], p["df"]['Int'], color=c, lw=2.0, ls='--', label=f'{p["label"]} (Partial)', zorder=3)
            
        # Peak
        arr_x = self.peak_freq + 1.0
        arr_y = self.peak_int + (self.ls_y_max.value() * 0.05)
        ax.annotate(f'$\\mathbf{{{self.peak_freq:.2f}\\ THz}}$', 
                    xy=(self.peak_freq, self.peak_int), 
                    xytext=(arr_x, arr_y), 
                    fontsize=14, fontweight='bold', color='red',
                    arrowprops=dict(facecolor='red', edgecolor='red', shrink=0.05, width=1.5, headwidth=8))
                    
        ax.set_xlim(self.ls_x_min.value(), self.ls_x_max.value())
        ax.set_ylim(self.ls_y_min.value(), self.ls_y_max.value())
        
        ax.xaxis.set_major_locator(ticker.MultipleLocator(self.ls_x_step.value()))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(self.ls_y_step.value()))
        
        if self.ls_minor.isChecked():
            ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
            ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
            
        ax.set_xlabel(r'$\mathbf{Frequency\ (\nu,\ THz)}$', fontsize=16, labelpad=15)
        ax.set_ylabel(r'$\mathbf{Vibrational\ Density\ of\ States\ (a.u.)}$', fontsize=16, labelpad=15)
        ax.set_title(f'Vibrational Spectra of ${self.inp_formula.text()}$', fontsize=18, pad=20, fontweight='bold')
        
        leg = ax.legend(loc=self.ls_leg_loc.currentText(), frameon=False, ncol=2 if len(self.valid_partials)>2 else 1)
        leg.set_draggable(True)
        
        # Inset
        if self.ls_inset_act.isChecked():
            axins = ax.inset_axes([self.ls_in_locx.value(), self.ls_in_locy.value(), self.ls_in_w.value(), self.ls_in_h.value()])
            axins.plot(self.total_df['Freq'], self.total_df['Int'], color=t_color, lw=2.5, ls='-')
            axins.fill_between(self.total_df['Freq'], self.total_df['Int'], color=t_color, alpha=0.1)
            for i, p in enumerate(self.valid_partials):
                c = colors[i % len(colors)]
                axins.plot(p["df"]['Freq'], p["df"]['Int'], color=c, lw=2.0, ls='--')
                
            axins.set_xlim(self.ls_in_xmin.value(), self.ls_in_xmax.value())
            axins.set_ylim(self.ls_in_ymin.value(), self.ls_in_ymax.value())
            axins.set_title("Kubas $\eta^2-H_2$", fontsize=12, fontweight='bold', pad=5)
            
        self.figure.tight_layout()
        self.canvas.draw()
