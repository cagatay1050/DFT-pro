import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QGroupBox
)

class Hse06OptikWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        lbl = QLabel("🌈 HSE06 Optik Özellikler INCAR Üretici")
        lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("font-family: Consolas, monospace; font-size: 14px; background-color: #f8f9fa;")
        
        btn_generate = QPushButton("Standart INCAR Üret")
        btn_generate.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        btn_generate.clicked.connect(self.generate_incar)
        
        main_layout.addWidget(lbl)
        main_layout.addWidget(self.text_edit)
        main_layout.addWidget(btn_generate)
        
        self.create_local_settings_widget()
        self.generate_incar()

    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        layout.addWidget(QLabel("Bu modül sadece metin üretir."))
        
    def get_local_settings_widget(self):
        return self.local_widget
        
    def generate_incar(self):
        incar_content = """System = VASP Calculation
PREC = Accurate
ALGO = Fast
ISPIN = 1

# Specific Tags
LHFCALC = .TRUE.
HFSCREEN = 0.2
ALGO = Exact
NBANDS = 120
LOPTICS = .TRUE.
CSHIFT = 0.1
"""
        self.text_edit.setPlainText(incar_content)
