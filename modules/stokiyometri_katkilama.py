import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QDoubleSpinBox, QLineEdit, QSpinBox
)
from utils.style_manager import notifier

class StokiyometriKatkilamaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        group_input = QGroupBox("Katkılama (Doping) Parametreleri")
        form_input = QFormLayout(group_input)
        
        self.le_host = QLineEdit("Sr2ZnH6")
        self.le_target_atom = QLineEdit("Zn")
        self.le_dopant = QLineEdit("Cu")
        self.sp_percent = QDoubleSpinBox()
        self.sp_percent.setRange(0.01, 100.0)
        self.sp_percent.setValue(5.0)
        
        form_input.addRow("Ana Malzeme Formülü:", self.le_host)
        form_input.addRow("Yer Değişecek Atom (Host):", self.le_target_atom)
        form_input.addRow("Katkı Atomu (Dopant):", self.le_dopant)
        form_input.addRow("İstenen Katkı Oranı (%):", self.sp_percent)
        
        self.btn_calc = QPushButton("Süper Hücre Boyutunu Hesapla")
        self.btn_calc.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.calculate_doping)
        
        group_res = QGroupBox("Analiz Sonuçları")
        res_layout = QVBoxLayout(group_res)
        
        self.lbl_result = QLabel("Bekleniyor...")
        self.lbl_result.setStyleSheet("font-size: 14px;")
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
        
    def calculate_doping(self):
        target = self.le_target_atom.text().strip()
        dopant = self.le_dopant.text().strip()
        percent = self.sp_percent.value() / 100.0
        
        if percent <= 0 or percent > 1:
            self.lbl_result.setText("Hata: Yüzde 0 ile 100 arasında olmalıdır.")
            return
            
        # Simplistic calculation: we need N total target atoms such that 
        # 1 dopant atom replaces 1 target atom to get roughly the desired percentage.
        # So: 1 / N = percent  => N = 1 / percent
        req_atoms = 1.0 / percent
        
        req_int = int(round(req_atoms))
        
        # Supercell estimation
        # We assume the unit cell has 1 target atom for simplicity in this demo.
        # In a real app, we'd parse POSCAR. 
        sc_size = req_int
        # find nearest perfect cube for isotropic supercell
        import math
        c = round(sc_size**(1/3))
        if c == 0: c = 1
        
        actual_atoms = c**3
        actual_percent = 1.0 / actual_atoms * 100.0
        
        self.lbl_result.setText(
            f"Hedeflenen Katkı Oranı: %{percent*100:.2f}\n"
            f"Gereken {target} Atomu Sayısı (En az): {req_atoms:.1f}\n\n"
            f"Önerilen İzotropik Süper Hücre: {c} x {c} x {c} ({actual_atoms} katı büyüklükte)\n"
            f"Bu süper hücrede 1 adet {target} atomunu {dopant} ile değiştirirseniz,\n"
            f"Gerçekleşecek Katkı Oranı: %{actual_percent:.3f}"
        )
