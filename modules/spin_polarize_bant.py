import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QScrollArea, QLineEdit, QFileDialog,
    QMessageBox, QComboBox
)
from utils.style_manager import apply_global_style, notifier

class SpinPolarizeBantWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.df_up = None
        self.df_dn = None
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Sol Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        group_files = QGroupBox("Bant Verileri (Spin Up / Spin Down)")
        files_layout = QVBoxLayout(group_files)
        
        self.btn_load_up = QPushButton("Spin UP Yükle (.dat)")
        self.btn_load_up.clicked.connect(self.load_spin_up)
        self.lbl_up_status = QLabel("Spin UP: Yüklenmedi")
        
        self.btn_load_dn = QPushButton("Spin DOWN Yükle (.dat)")
        self.btn_load_dn.clicked.connect(self.load_spin_dn)
        self.lbl_dn_status = QLabel("Spin DOWN: Yüklenmedi")
        
        files_layout.addWidget(self.btn_load_up)
        files_layout.addWidget(self.lbl_up_status)
        files_layout.addWidget(self.btn_load_dn)
        files_layout.addWidget(self.lbl_dn_status)
        
        self.btn_plot = QPushButton("Grafiği Çiz")
        self.btn_plot.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.btn_plot.clicked.connect(self.plot_graph)
        
        left_layout.addWidget(group_files)
        left_layout.addWidget(self.btn_plot)
        left_layout.addStretch()
        
        scroll = QScrollArea()
        scroll.setWidget(left_panel)
        scroll.setWidgetResizable(True)
        scroll.setMaximumWidth(400)
        
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
        
        self.le_color_up = QLineEdit("blue")
        self.le_color_dn = QLineEdit("red")
        
        self.cmb_style_up = QComboBox()
        self.cmb_style_up.addItems(["-", "--", "-.", ":"])
        self.cmb_style_dn = QComboBox()
        self.cmb_style_dn.addItems(["--", "-", "-.", ":"])
        
        self.le_ef = QLineEdit("0.0")
        
        layout.addRow("Spin UP Rengi:", self.le_color_up)
        layout.addRow("Spin UP Stili:", self.cmb_style_up)
        layout.addRow("Spin DOWN Rengi:", self.le_color_dn)
        layout.addRow("Spin DOWN Stili:", self.cmb_style_dn)
        layout.addRow("Fermi Enerjisi (eV):", self.le_ef)
        
    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        if self.df_up is not None or self.df_dn is not None:
            self.plot_graph()
            
    def load_spin_up(self):
        path, _ = QFileDialog.getOpenFileName(self, "Spin UP Verisi Seç", "", "Data Files (*.dat *.csv *.txt)")
        if path:
            try:
                self.df_up = pd.read_csv(path, sep=r'\s+', header=None)
                self.lbl_up_status.setText("Spin UP: Yüklendi")
                self.lbl_up_status.setStyleSheet("color: green;")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Dosya okunamadı:\n{e}")
                
    def load_spin_dn(self):
        path, _ = QFileDialog.getOpenFileName(self, "Spin DOWN Verisi Seç", "", "Data Files (*.dat *.csv *.txt)")
        if path:
            try:
                self.df_dn = pd.read_csv(path, sep=r'\s+', header=None)
                self.lbl_dn_status.setText("Spin DOWN: Yüklendi")
                self.lbl_dn_status.setStyleSheet("color: green;")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Dosya okunamadı:\n{e}")

    def plot_graph(self):
        if self.df_up is None and self.df_dn is None:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir bant verisi yükleyin (UP veya DOWN).")
            return
            
        self.figure.clear()
        apply_global_style()
        ax = self.figure.add_subplot(111)
        
        try:
            ef = float(self.le_ef.text())
        except:
            ef = 0.0
            
        c_up = self.le_color_up.text()
        c_dn = self.le_color_dn.text()
        s_up = self.cmb_style_up.currentText()
        s_dn = self.cmb_style_dn.currentText()
        
        # Plot Spin UP
        if self.df_up is not None:
            # Assuming format: X, Y
            # Multiple bands are usually separated by empty lines or multiple columns.
            # Assuming simple X Y columns format for demo
            x = self.df_up.iloc[:, 0].values
            for i in range(1, self.df_up.shape[1]):
                y = self.df_up.iloc[:, i].values - ef
                ax.plot(x, y, color=c_up, linestyle=s_up, label="Spin UP" if i==1 else "")
                
        # Plot Spin DOWN
        if self.df_dn is not None:
            x = self.df_dn.iloc[:, 0].values
            for i in range(1, self.df_dn.shape[1]):
                y = self.df_dn.iloc[:, i].values - ef
                ax.plot(x, y, color=c_dn, linestyle=s_dn, label="Spin DOWN" if i==1 else "")
                
        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        ax.set_ylabel("Enerji - E$_F$ (eV)")
        ax.set_xlabel("K-Path")
        
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(handles, labels, frameon=True)
            
        self.figure.tight_layout()
        self.canvas.draw()
