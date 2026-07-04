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
    QDoubleSpinBox, QComboBox, QScrollArea, QLineEdit, QCheckBox, QSlider
)
from PyQt6.QtCore import Qt
from utils.style_manager import apply_global_style, notifier

class FononBandWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.branches = []
        self.raw_end_points = []
        self.k_label_inputs = []
        self.band_data = None
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Sol Panel (Kontrol Paneli)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(450)
        
        # 1. Dosya Yükleme
        group_file = QGroupBox("1. Dosya Yükleme (BAND.dat vb.)")
        l_file = QVBoxLayout()
        self.btn_load = QPushButton("Fonon Veri Dosyasını Yükle")
        self.btn_load.clicked.connect(self.load_file)
        self.lbl_file = QLabel("Seçilen Dosya: Yok")
        l_file.addWidget(self.btn_load)
        l_file.addWidget(self.lbl_file)
        group_file.setLayout(l_file)
        
        # 2. K-Path Koordinatları
        group_kpath = QGroupBox("2. K-Path Koordinatları")
        l_kpath = QVBoxLayout()
        lbl_info = QLabel("Dikey çizgilerin X koordinatlarını aralarında boşluk bırakarak girin:")
        lbl_info.setWordWrap(True)
        self.le_endpoints = QLineEdit()
        self.le_endpoints.textChanged.connect(self.update_k_labels_ui)
        l_kpath.addWidget(lbl_info)
        l_kpath.addWidget(self.le_endpoints)
        
        self.k_labels_layout = QHBoxLayout()
        l_kpath.addLayout(self.k_labels_layout)
        group_kpath.setLayout(l_kpath)
        
        # 3. İnce Ayarlar
        group_settings = QGroupBox("3. Grafik İnce Ayarları")
        l_settings = QFormLayout()
        
        self.ls_y_min = QDoubleSpinBox(); self.ls_y_min.setRange(-100, 100); self.ls_y_min.setValue(-2.0)
        self.ls_y_max = QDoubleSpinBox(); self.ls_y_max.setRange(-100, 100); self.ls_y_max.setValue(20.0)
        self.ls_y_step = QDoubleSpinBox(); self.ls_y_step.setRange(0.1, 50); self.ls_y_step.setValue(5.0)
        
        self.cb_hline = QCheckBox("y=0 Çizgisini Göster")
        self.cb_hline.setChecked(True)
        
        self.cb_text_box = QCheckBox("Metin Kutusu Ekle (Legend)")
        self.le_text_box = QLineEdit("TiO_2 \\text{ Anatase}")
        self.cmb_text_loc = QComboBox()
        self.cmb_text_loc.addItems(["upper right", "upper left", "lower left", "lower right", "right", "center left", "center right", "lower center", "upper center", "center"])
        
        l_settings.addRow("Y Min (THz):", self.ls_y_min)
        l_settings.addRow("Y Maks (THz):", self.ls_y_max)
        l_settings.addRow("Y Adım:", self.ls_y_step)
        l_settings.addRow("", self.cb_hline)
        l_settings.addRow("", self.cb_text_box)
        l_settings.addRow("Kutu İçeriği:", self.le_text_box)
        l_settings.addRow("Kutu Konumu:", self.cmb_text_loc)
        
        group_settings.setLayout(l_settings)
        
        self.btn_plot = QPushButton("Grafiği Çiz")
        self.btn_plot.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 10px;")
        self.btn_plot.clicked.connect(self.plot_graph)
        
        left_layout.addWidget(group_file)
        left_layout.addWidget(group_kpath)
        left_layout.addWidget(group_settings)
        left_layout.addWidget(self.btn_plot)
        left_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidget(left_panel)
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(480)
        
        # Sağ Panel (Çizim)
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
        self.cb_line_style = QComboBox()
        self.cb_line_style.addItems(["-", "--", "-.", ":"])
        
        layout.addRow("Başlık Punto:", self.ls_font_title)
        layout.addRow("Rakam Punto:", self.ls_font_tick)
        layout.addRow("Çizgi Kalınlığı:", self.ls_line_width)
        layout.addRow("0 Çizgisi Stili:", self.cb_line_style)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.branches:
            self.plot_graph()

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Fonon Dosyasını Seç", "", "Data Files (*.dat *.txt);;All Files (*)")
        if not file_path: return
        
        self.lbl_file.setText(f"Seçilen: {os.path.basename(file_path)}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.readlines()
                
            self.raw_end_points = []
            self.branches = []
            current_x, current_y = [], []
            
            for i, line in enumerate(content):
                line = line.strip()
                if line.startswith("# End points"):
                    parts = line.split(":")
                    if len(parts) > 1 and parts[1].strip() != "":
                        self.raw_end_points = [float(x) for x in parts[1].split()]
                    elif i + 1 < len(content):
                        next_line = content[i+1].strip()
                        if next_line.startswith("#"):
                            nums = next_line.replace("#", "").strip()
                            self.raw_end_points = [float(x) for x in nums.split()]
                            
                elif line == "":
                    if current_x:
                        self.branches.append((current_x, current_y))
                        current_x, current_y = [], []
                elif not line.startswith("#"):
                    try:
                        parts = line.split()
                        if len(parts) >= 2:
                            current_x.append(float(parts[0]))
                            current_y.append(float(parts[1]))
                    except ValueError:
                        pass
                        
            if current_x:
                self.branches.append((current_x, current_y))
                
            self.le_endpoints.setText(" ".join([f"{x:.6f}" for x in self.raw_end_points]))
            
            # Auto set max y
            if self.branches:
                max_y = max([max(y) for x, y in self.branches])
                self.ls_y_max.setValue(float(np.ceil(max_y)) + 2.0)
                
            QMessageBox.information(self, "Başarılı", f"{len(self.branches)} adet fonon bandı okundu.")
            self.plot_graph()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya okuma hatası:\n{e}")

    def update_k_labels_ui(self):
        # Clear layout
        while self.k_labels_layout.count():
            child = self.k_labels_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        self.k_label_inputs = []
        try:
            endpoints = [float(x) for x in self.le_endpoints.text().split()]
        except ValueError:
            endpoints = []
            
        for i, val in enumerate(endpoints):
            le = QLineEdit(f"P{i+1}")
            le.setPlaceholderText(f"{val:.3f}")
            self.k_labels_layout.addWidget(le)
            self.k_label_inputs.append(le)

    def plot_graph(self):
        if not self.branches: return
        
        try:
            end_points = [float(x) for x in self.le_endpoints.text().split()]
        except ValueError:
            QMessageBox.warning(self, "Hata", "K-Path koordinatları geçerli değil.")
            return
            
        if not end_points: return
        
        self.figure.clear()
        apply_global_style()
        ax = self.figure.add_subplot(111)
        line_color = '#3498DB'
        
        lw = self.ls_line_width.value()
        for x_vals, y_vals in self.branches:
            ax.plot(x_vals, y_vals, color=line_color, linewidth=lw, alpha=0.9)
            
        if self.cb_hline.isChecked():
            ax.axhline(0, color='black', linestyle=self.cb_line_style.currentText(), linewidth=1.2, zorder=0)
            
        for ep in end_points:
            ax.axvline(x=ep, color='black', linestyle='-', linewidth=1.0, zorder=0)
            
        ax.set_xlim(end_points[0], end_points[-1])
        ax.set_ylim(self.ls_y_min.value(), self.ls_y_max.value())
        
        k_labels = []
        for i, le in enumerate(self.k_label_inputs):
            val = le.text().strip()
            if val.upper() in ["G", "GAMMA"]:
                k_labels.append(r"$\mathbf{\Gamma}$")
            else:
                k_labels.append(val)
                
        if len(k_labels) == len(end_points):
            ax.set_xticks(end_points)
            ax.set_xticklabels(k_labels, fontsize=self.ls_font_tick.value(), fontweight='bold')
            
        ax.set_ylabel('Frequency (THz)', fontsize=self.ls_font_title.value(), fontweight='bold', labelpad=15)
        ax.yaxis.set_major_locator(MultipleLocator(self.ls_y_step.value()))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        
        ax.tick_params(axis='y', which='major', direction='in', length=10, width=2.0, labelsize=self.ls_font_tick.value(), right=False)
        ax.tick_params(axis='y', which='minor', direction='in', length=5, width=1.5, right=False)
        ax.tick_params(axis='x', which='major', direction='in', length=0)
        
        for label in ax.get_yticklabels():
            label.set_fontweight('bold')
        for spine in ax.spines.values():
            spine.set_linewidth(2.0)
            
        if self.cb_text_box.isChecked() and self.le_text_box.text().strip() != "":
            formatted_text = f"${self.le_text_box.text()}$"
            leg = ax.legend([formatted_text], loc=self.cmb_text_loc.currentText(), fontsize=14, handlelength=0, handletextpad=0, fancybox=False, edgecolor='black')
            leg.get_frame().set_linewidth(1.0)
            leg.set_draggable(True)
            
        self.figure.tight_layout()
        self.canvas.draw()
        self.canvas.draw()
