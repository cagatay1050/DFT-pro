import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFormLayout, 
    QGroupBox, QMessageBox, QDoubleSpinBox, QSpinBox, QLineEdit, 
    QScrollArea, QFileDialog, QColorDialog, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)
from PyQt6.QtCore import Qt
from utils.style_manager import apply_global_style, notifier

class VaspTermodinamikKiyasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data_files = [] 
        self.datasets = []
        self.summary_data = []
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(450)
        
        # 1. Veri Yükleme
        group_files = QGroupBox("1. Malzeme Verileri")
        self.l_files = QVBoxLayout()
        
        btn_add = QPushButton("+ Yeni Malzeme Ekle")
        btn_add.clicked.connect(self.add_data_slot)
        self.l_files.addWidget(btn_add)
        
        self.files_container = QVBoxLayout()
        self.l_files.addLayout(self.files_container)
        group_files.setLayout(self.l_files)
        
        # Initial 2 materials
        for _ in range(2):
            self.add_data_slot()
            
        # 2. Analiz Tablosu
        group_results = QGroupBox("2. Fiziksel Özellikler")
        l_results = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Malzeme", "N", "DP Limiti", "ZPE", "ZPVE"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        l_results.addWidget(self.table)
        group_results.setLayout(l_results)
        
        # 3. Grafik Çizme
        self.btn_plot = QPushButton("Verileri Oku ve Çiz")
        self.btn_plot.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 10px;")
        self.btn_plot.clicked.connect(self.process_and_plot)
        
        left_layout.addWidget(group_files)
        left_layout.addWidget(group_results)
        left_layout.addWidget(self.btn_plot)
        left_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidget(left_panel)
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(480)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.figure = plt.figure(figsize=(12, 10))
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
        
        self.sb_wspace = QDoubleSpinBox(); self.sb_wspace.setRange(0, 1.0); self.sb_wspace.setValue(0.25); self.sb_wspace.setSingleStep(0.05)
        self.sb_hspace = QDoubleSpinBox(); self.sb_hspace.setRange(0, 1.0); self.sb_hspace.setValue(0.25); self.sb_hspace.setSingleStep(0.05)
        
        # X Eksen (Ortak)
        self.sb_t_min = QDoubleSpinBox(); self.sb_t_min.setRange(0, 5000); self.sb_t_min.setValue(0.0); self.sb_t_min.setSingleStep(50.0)
        self.sb_t_max = QDoubleSpinBox(); self.sb_t_max.setRange(0, 5000); self.sb_t_max.setValue(1000.0); self.sb_t_max.setSingleStep(50.0)
        self.sb_t_step = QDoubleSpinBox(); self.sb_t_step.setRange(10, 1000); self.sb_t_step.setValue(200.0); self.sb_t_step.setSingleStep(50.0)
        
        # F Eksen
        self.sb_f_min = QDoubleSpinBox(); self.sb_f_min.setRange(-10000, 10000); self.sb_f_min.setValue(-500.0); self.sb_f_min.setSingleStep(50.0)
        self.sb_f_max = QDoubleSpinBox(); self.sb_f_max.setRange(-10000, 10000); self.sb_f_max.setValue(100.0); self.sb_f_max.setSingleStep(50.0)
        
        # S Eksen
        self.sb_s_min = QDoubleSpinBox(); self.sb_s_min.setRange(-1000, 10000); self.sb_s_min.setValue(0.0); self.sb_s_min.setSingleStep(50.0)
        self.sb_s_max = QDoubleSpinBox(); self.sb_s_max.setRange(-1000, 10000); self.sb_s_max.setValue(500.0); self.sb_s_max.setSingleStep(50.0)
        
        # Cv Eksen
        self.sb_cv_min = QDoubleSpinBox(); self.sb_cv_min.setRange(-1000, 10000); self.sb_cv_min.setValue(0.0); self.sb_cv_min.setSingleStep(50.0)
        self.sb_cv_max = QDoubleSpinBox(); self.sb_cv_max.setRange(-1000, 10000); self.sb_cv_max.setValue(300.0); self.sb_cv_max.setSingleStep(50.0)
        
        # E Eksen
        self.sb_e_min = QDoubleSpinBox(); self.sb_e_min.setRange(-10000, 10000); self.sb_e_min.setValue(0.0); self.sb_e_min.setSingleStep(50.0)
        self.sb_e_max = QDoubleSpinBox(); self.sb_e_max.setRange(-10000, 10000); self.sb_e_max.setValue(500.0); self.sb_e_max.setSingleStep(50.0)
        
        layout.addRow("WSpace (Yatay Boşluk):", self.sb_wspace)
        layout.addRow("HSpace (Dikey Boşluk):", self.sb_hspace)
        
        layout.addRow("X Min (K):", self.sb_t_min)
        layout.addRow("X Max (K):", self.sb_t_max)
        layout.addRow("X Adım:", self.sb_t_step)
        
        layout.addRow("F Min:", self.sb_f_min)
        layout.addRow("F Max:", self.sb_f_max)
        
        layout.addRow("S Min:", self.sb_s_min)
        layout.addRow("S Max:", self.sb_s_max)
        
        layout.addRow("Cv Min:", self.sb_cv_min)
        layout.addRow("Cv Max:", self.sb_cv_max)
        
        layout.addRow("E Min:", self.sb_e_min)
        layout.addRow("E Max:", self.sb_e_max)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.datasets:
            self.plot_graph()

    def add_data_slot(self):
        idx = len(self.data_files)
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 5)
        
        h1 = QHBoxLayout()
        le_lbl = QLineEdit(f"Material_{idx+1}")
        btn = QPushButton("Dosya Seç")
        btn_color = QPushButton()
        
        default_colors = ['#E74C3C', '#2980B9', '#27AE60', '#8E44AD', '#F39C12', '#34495E', '#D35400', '#16A085']
        c = default_colors[idx % len(default_colors)]
        btn_color.setStyleSheet(f"background-color: {c}; width: 20px; height: 20px;")
        
        item = {'label_le': le_lbl, 'file_path': None, 'btn': btn, 'color': c}
        
        def choose_file():
            fp, _ = QFileDialog.getOpenFileName(self, "Veri Seç", "", "Data Files (*.dat *.txt *.out);;All Files (*)")
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
        
        h1.addWidget(le_lbl)
        h1.addWidget(btn)
        h1.addWidget(btn_color)
        
        h2 = QHBoxLayout()
        sb_natom = QSpinBox()
        sb_natom.setRange(1, 1000)
        sb_natom.setValue(1)
        sb_natom.setToolTip("Hücredeki Toplam Atom Sayısı")
        
        sb_zpe = QDoubleSpinBox()
        sb_zpe.setRange(-10000.0, 10000.0)
        sb_zpe.setValue(0.0)
        sb_zpe.setDecimals(4)
        sb_zpe.setToolTip("ZPE (kJ/mol)")
        
        item['natom_sb'] = sb_natom
        item['zpe_sb'] = sb_zpe
        
        h2.addWidget(QLabel("Atom Sayısı:"))
        h2.addWidget(sb_natom)
        h2.addWidget(QLabel("ZPE (kJ/mol):"))
        h2.addWidget(sb_zpe)
        
        l.addLayout(h1)
        l.addLayout(h2)
        
        self.files_container.addWidget(w)
        self.data_files.append(item)

    def process_and_plot(self):
        self.datasets = []
        self.summary_data = []
        
        for item in self.data_files:
            if item['file_path']:
                try:
                    df = pd.read_csv(item['file_path'], sep=r'\s+', comment='#', names=['T', 'F', 'S', 'Cv', 'E'])
                    df = df.dropna().apply(pd.to_numeric, errors='coerce').dropna()
                    
                    if not df.empty:
                        n_atoms = item['natom_sb'].value()
                        zpe_input = item['zpe_sb'].value()
                        
                        dp_limit = 3 * n_atoms * 8.31446
                        zpve_ev_atom = (zpe_input / 96.485) / n_atoms if n_atoms > 0 else 0.0
                        
                        lbl = item['label_le'].text()
                        
                        self.summary_data.append({
                            "Malzeme": lbl,
                            "N": n_atoms,
                            "DP Limiti": f"{dp_limit:.2f}",
                            "ZPE": f"{zpe_input:.4f}",
                            "ZPVE": f"{zpve_ev_atom:.6f}"
                        })
                        
                        self.datasets.append({
                            "df": df,
                            "color": item['color'],
                            "label": rf"$\mathbf{{{lbl}}}$",
                            "dp_limit": dp_limit
                        })
                except Exception as e:
                    QMessageBox.warning(self, "Uyarı", f"{os.path.basename(item['file_path'])} okunamadı:\n{e}")
                    
        self.update_table()
        self.plot_graph()

    def update_table(self):
        self.table.setRowCount(len(self.summary_data))
        for r_idx, res in enumerate(self.summary_data):
            self.table.setItem(r_idx, 0, QTableWidgetItem(res['Malzeme']))
            self.table.setItem(r_idx, 1, QTableWidgetItem(str(res['N'])))
            self.table.setItem(r_idx, 2, QTableWidgetItem(res['DP Limiti']))
            self.table.setItem(r_idx, 3, QTableWidgetItem(res['ZPE']))
            self.table.setItem(r_idx, 4, QTableWidgetItem(res['ZPVE']))

    def plot_graph(self):
        if not self.datasets: return
        
        self.figure.clear()
        apply_global_style()
        self.axes = self.figure.subplots(2, 2)
            
        ax_F, ax_S = self.axes[0, 0], self.axes[0, 1]
        ax_Cv, ax_E = self.axes[1, 0], self.axes[1, 1]
        
        t_min, t_max, t_step = self.sb_t_min.value(), self.sb_t_max.value(), self.sb_t_step.value()
        
        for d in self.datasets:
            ax_F.plot(d["df"]['T'], d["df"]['F'], color=d["color"], linewidth=2.5, label=d["label"])
            ax_S.plot(d["df"]['T'], d["df"]['S'], color=d["color"], linewidth=2.5, label=d["label"])
            
            ax_Cv.plot(d["df"]['T'], d["df"]['Cv'], color=d["color"], linewidth=2.5, label=d["label"])
            if d["dp_limit"] > 0 and self.sb_cv_min.value() <= d["dp_limit"] <= self.sb_cv_max.value():
                ax_Cv.axhline(d["dp_limit"], color=d["color"], linestyle='--', linewidth=1.5, alpha=0.7)
                
            ax_E.plot(d["df"]['T'], d["df"]['E'], color=d["color"], linewidth=2.5, label=d["label"])
            
        # F
        ax_F.set_ylabel(r'$\mathbf{F}$ (kJ/mol)', fontweight='bold', labelpad=10)
        ax_F.set_ylim(self.sb_f_min.value(), self.sb_f_max.value())
        ax_F.text(0.05, 0.95, "(a)", transform=ax_F.transAxes, fontsize=18, fontweight='bold', va='top')
        
        # S
        ax_S.set_ylabel(r'$\mathbf{S}$ (J/K$\cdot$mol)', fontweight='bold', labelpad=10)
        ax_S.set_ylim(self.sb_s_min.value(), self.sb_s_max.value())
        ax_S.text(0.05, 0.95, "(b)", transform=ax_S.transAxes, fontsize=18, fontweight='bold', va='top')
        
        # Cv
        ax_Cv.set_ylabel(r'$\mathbf{C_v}$ (J/K$\cdot$mol)', fontweight='bold', labelpad=10)
        ax_Cv.set_ylim(self.sb_cv_min.value(), self.sb_cv_max.value())
        ax_Cv.text(0.05, 0.95, "(c)", transform=ax_Cv.transAxes, fontsize=18, fontweight='bold', va='top')
        
        # E
        ax_E.set_ylabel(r'$\mathbf{E}$ (kJ/mol)', fontweight='bold', labelpad=10)
        ax_E.set_ylim(self.sb_e_min.value(), self.sb_e_max.value())
        ax_E.text(0.05, 0.95, "(d)", transform=ax_E.transAxes, fontsize=18, fontweight='bold', va='top')
        
        for ax in self.axes.flat:
            ax.set_xlabel(r'$\mathbf{Temperature}$ (K)', fontweight='bold', labelpad=10)
            ax.set_xlim(t_min, t_max)
            ax.xaxis.set_major_locator(MultipleLocator(t_step))
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))
            ax.yaxis.set_minor_locator(AutoMinorLocator(2))
            
            ax.tick_params(axis='both', which='major', direction='in', length=8, width=2.0, top=False, right=False)
            ax.tick_params(axis='both', which='minor', direction='in', length=4, width=1.3, top=False, right=False)
            
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight('bold')
            for spine in ax.spines.values():
                spine.set_linewidth(2.0)
                
        leg = ax_F.legend(loc='best', frameon=False)
        leg.set_draggable(True)
        
        self.figure.tight_layout(pad=2.0)
        self.figure.subplots_adjust(wspace=self.sb_wspace.value(), hspace=self.sb_hspace.value())
        self.canvas.draw()
