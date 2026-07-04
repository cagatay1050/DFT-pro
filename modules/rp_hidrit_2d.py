import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QSpinBox, QLineEdit
)
from PyQt6.QtCore import Qt
from utils.style_manager import notifier

class RPHidritBulucuWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        group_input = QGroupBox("Ruddlesden-Popper (RP) Faz Ayarları")
        form_input = QFormLayout(group_input)
        
        self.le_a_atom = QLineEdit("Sr")
        self.le_b_atom = QLineEdit("Zn")
        self.le_x_atom = QLineEdit("H")
        
        self.sp_n = QSpinBox()
        self.sp_n.setRange(1, 10)
        self.sp_n.setValue(1)
        
        form_input.addRow("A Atomu (Toprak Alkali vb.):", self.le_a_atom)
        form_input.addRow("B Atomu (Geçiş Metali vb.):", self.le_b_atom)
        form_input.addRow("X Atomu (Hidrojen):", self.le_x_atom)
        form_input.addRow("n İndeksi (Katman Sayısı):", self.sp_n)
        
        self.btn_calc = QPushButton("Stokiyometri Hesapla")
        self.btn_calc.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.calculate_rp)
        
        group_res = QGroupBox("Sonuç: Teorik RP Fazı")
        res_layout = QVBoxLayout(group_res)
        
        self.lbl_formula = QLabel("Genel Formül: A_{n+1} B_n X_{3n+1}")
        self.lbl_formula.setStyleSheet("font-size: 14px; font-style: italic;")
        
        self.lbl_result = QLabel("Sonuç: Bekleniyor...")
        self.lbl_result.setStyleSheet("font-size: 18px; font-weight: bold; color: #c0392b; margin-top: 10px;")
        
        res_layout.addWidget(self.lbl_formula)
        res_layout.addWidget(self.lbl_result)
        
        main_layout.addWidget(group_input)
        main_layout.addWidget(self.btn_calc)
        main_layout.addWidget(group_res)
        main_layout.addStretch()
        
        self.create_local_settings_widget()

    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        layout.addWidget(QLabel("Bu modül grafik içermemektedir."))
        
    def get_local_settings_widget(self):
        return self.local_widget
        
    def calculate_rp(self):
        a = self.le_a_atom.text().strip()
        b = self.le_b_atom.text().strip()
        x = self.le_x_atom.text().strip()
        n = self.sp_n.value()
        
        a_count = n + 1
        b_count = n
        x_count = 3 * n + 1
        
        result_formula = f"{a}{a_count}{b}{b_count if b_count > 1 else ''}{x}{x_count}"
        
        self.lbl_result.setText(
            f"Hesaplanan Formül: {result_formula}\n\n"
            f"Birim Hücredeki Atom Sayıları:\n"
            f"{a}: {a_count}\n"
            f"{b}: {b_count}\n"
            f"{x}: {x_count}\n"
            f"Toplam: {a_count + b_count + x_count} atom"
        )
