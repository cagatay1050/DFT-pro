import sys
import os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt

class MekanikOzelliklerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        # Title
        lbl_title = QLabel("⚙️ Elastik Sabitlerden Mekanik Özellikler (VELAS Klonu)")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(lbl_title)
        
        # Splitter for Input and Output
        content_layout = QHBoxLayout()
        
        # --- LEFT PANEL: INPUTS ---
        left_panel = QVBoxLayout()
        
        grp_input = QGroupBox("Cij Elastik Matris Girdisi (GPa)")
        grp_layout = QVBoxLayout()
        
        btn_load_outcar = QPushButton("📂 OUTCAR'dan Oku (Pymatgen)")
        btn_load_outcar.setStyleSheet("background-color: #2980b9; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        btn_load_outcar.clicked.connect(self.load_from_outcar)
        grp_layout.addWidget(btn_load_outcar)
        
        btn_load_castep = QPushButton("📂 CASTEP'ten Oku (.castep)")
        btn_load_castep.setStyleSheet("background-color: #8e44ad; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        btn_load_castep.clicked.connect(self.load_from_castep)
        grp_layout.addWidget(btn_load_castep)
        
        btn_paste = QPushButton("📋 Panodan Matris Yapıştır (6x6)")
        btn_paste.setStyleSheet("background-color: #e67e22; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        btn_paste.clicked.connect(self.paste_from_clipboard)
        grp_layout.addWidget(btn_paste)
        
        # 6x6 Table
        self.table_cij = QTableWidget(6, 6)
        self.table_cij.setHorizontalHeaderLabels(['C1', 'C2', 'C3', 'C4', 'C5', 'C6'])
        self.table_cij.setVerticalHeaderLabels(['C1', 'C2', 'C3', 'C4', 'C5', 'C6'])
        for i in range(6):
            for j in range(6):
                item = QTableWidgetItem("0.0")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table_cij.setItem(i, j, item)
                
        self.table_cij.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_cij.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_cij.setMinimumHeight(250)
        grp_layout.addWidget(self.table_cij)
        
        btn_calc = QPushButton("🚀 Mekanik Özellikleri Hesapla (VRH)")
        btn_calc.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; font-weight: bold; font-size: 14px; border-radius: 5px;")
        btn_calc.clicked.connect(self.calculate_properties)
        grp_layout.addWidget(btn_calc)
        
        grp_input.setLayout(grp_layout)
        left_panel.addWidget(grp_input)
        left_panel.addStretch()
        
        # --- RIGHT PANEL: OUTPUTS ---
        right_panel = QVBoxLayout()
        grp_output = QGroupBox("Hesaplanan Özellikler (Voigt-Reuss-Hill)")
        out_layout = QVBoxLayout()
        
        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        self.txt_output.setStyleSheet("font-family: Consolas, monospace; font-size: 13px; background-color: #f8f9fa;")
        out_layout.addWidget(self.txt_output)
        
        grp_output.setLayout(out_layout)
        right_panel.addWidget(grp_output)
        
        content_layout.addLayout(left_panel, 40)
        content_layout.addLayout(right_panel, 60)
        
        main_layout.addLayout(content_layout)
        self.create_local_settings_widget()

    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        layout.addWidget(QLabel("Bu modül, VELAS yazılımının\nPython/Pymatgen uyarlamasıdır."))
        
    def get_local_settings_widget(self):
        return self.local_widget

    def load_from_outcar(self):
        try:
            from pymatgen.analysis.elasticity import ElasticTensor
            from pymatgen.io.vasp import Outcar
        except ImportError:
            QMessageBox.critical(self, "Hata", "Pymatgen yüklü değil!")
            return
            
        file_path, _ = QFileDialog.getOpenFileName(self, "OUTCAR Seç", "", "All Files (*)")
        if not file_path:
            return
            
        try:
            outcar = Outcar(file_path)
            if not outcar.has_elastic_tensor:
                QMessageBox.warning(self, "Hata", "Bu OUTCAR dosyasında IBRION=6 elastik tensor verisi bulunamadı!")
                return
                
            tensor = outcar.read_elastic_tensor()
            # tensor is 6x6 numpy array in GPa
            for i in range(6):
                for j in range(6):
                    val = float(tensor[i][j])
                    self.table_cij.item(i, j).setText(f"{val:.3f}")
            QMessageBox.information(self, "Başarılı", "Elastik matris OUTCAR'dan başarıyla okundu!")
        except Exception as e:
            QMessageBox.critical(self, "Okuma Hatası", f"Dosya okunurken hata oluştu:\n{e}")

    def load_from_castep(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "CASTEP Seç", "", "CASTEP Output (*.castep);;All Files (*)")
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            tensor = []
            parsing = False
            start_idx = 0
            for i, line in enumerate(lines):
                if "Elastic Stiffness Tensor" in line or "Elastic stiffness tensor" in line:
                    parsing = True
                    start_idx = i
                    break
                    
            if not parsing:
                QMessageBox.warning(self, "Hata", "Bu CASTEP dosyasında 'Elastic Stiffness Tensor' bulunamadı!")
                return
                
            row_count = 0
            for line in lines[start_idx:]:
                parts = line.strip().split()
                if len(parts) >= 7 and parts[0] in ['1','2','3','4','5','6']:
                    try:
                        row_vals = [float(x) for x in parts[1:7]]
                        tensor.append(row_vals)
                        row_count += 1
                        if row_count == 6:
                            break
                    except ValueError:
                        pass
                        
            if len(tensor) == 6:
                for i in range(6):
                    for j in range(6):
                        val = tensor[i][j]
                        self.table_cij.item(i, j).setText(f"{val:.3f}")
                QMessageBox.information(self, "Başarılı", "Elastik matris CASTEP'ten başarıyla okundu!")
            else:
                QMessageBox.warning(self, "Hata", "CASTEP dosyasından 6x6 matris tam olarak çekilemedi!")
                
        except Exception as e:
            QMessageBox.critical(self, "Okuma Hatası", f"Dosya okunurken hata oluştu:\n{e}")

    def paste_from_clipboard(self):
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        if not text.strip():
            QMessageBox.warning(self, "Hata", "Pano boş!")
            return
            
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) != 6:
            QMessageBox.warning(self, "Hata", f"Panodaki veri tam olarak 6 satır olmalıdır! Kopyalanan satır: {len(lines)}")
            return
            
        for i, line in enumerate(lines):
            parts = line.split()
            if len(parts) != 6:
                QMessageBox.warning(self, "Hata", f"{i+1}. satırda 6 sütun sayı olmalıdır!\nKopyalanan sütun: {len(parts)}\n(Lütfen sayıların arasında boşluk veya tab olduğundan emin olun)")
                return
                
            for j, part in enumerate(parts):
                try:
                    val = float(part)
                    self.table_cij.item(i, j).setText(f"{val:.3f}")
                except ValueError:
                    QMessageBox.warning(self, "Hata", f"Sayıya çevrilemeyen karakter bulundu: '{part}'")
                    return
                    
        QMessageBox.information(self, "Başarılı", "6x6 Matris panodan başarıyla tabloya aktarıldı!")

    def calculate_properties(self):
        try:
            C = np.zeros((6, 6))
            for i in range(6):
                for j in range(6):
                    C[i, j] = float(self.table_cij.item(i, j).text())
                    
            # Make symmetric if slight numerical errors exist
            C = (C + C.T) / 2.0
            
            # Compliance Matrix
            try:
                S = np.linalg.inv(C)
            except np.linalg.LinAlgError:
                QMessageBox.critical(self, "Matematiksel Hata", "Matrisin tersi alınamıyor (Singular Matrix). Cij değerlerini kontrol edin.")
                return

            # Formulas matching VELAS mechanics.m
            av = (C[0,0] + C[1,1] + C[2,2]) / 3.0
            bv = (C[0,1] + C[1,2] + C[0,2]) / 3.0
            cv = (C[3,3] + C[4,4] + C[5,5]) / 3.0
            
            ar = (S[0,0] + S[1,1] + S[2,2]) / 3.0
            br = (S[0,1] + S[1,2] + S[0,2]) / 3.0
            cr = (S[3,3] + S[4,4] + S[5,5]) / 3.0
            
            # Bulk Modulus
            Bv = (av + 2*bv) / 3.0
            Br = 1.0 / (3*ar + 6*br) if (3*ar + 6*br) != 0 else 0
            Bh = (Bv + Br) / 2.0
            
            # Shear Modulus
            Gv = (av - bv + 3*cv) / 5.0
            Gr = 5.0 / (4*ar - 4*br + 3*cr) if (4*ar - 4*br + 3*cr) != 0 else 0
            Gh = (Gv + Gr) / 2.0
            
            # Young's Modulus
            Ev = 1.0 / (1/(3*Gv) + 1/(9*Bv)) if (Bv!=0 and Gv!=0) else 0
            Er = 1.0 / (1/(3*Gr) + 1/(9*Br)) if (Br!=0 and Gr!=0) else 0
            Eh = (Ev + Er) / 2.0
            
            # Poisson's ratio
            nuv = (1 - (3*Gv)/(3*Bv+Gv))/2 if (3*Bv+Gv)!=0 else 0
            nur = (1 - (3*Gr)/(3*Br+Gr))/2 if (3*Br+Gr)!=0 else 0
            nuh = (nuv + nur) / 2.0
            
            # Pugh Ratio
            Prv = Bv / Gv if Gv != 0 else 0
            Prr = Br / Gr if Gr != 0 else 0
            Prh = Bh / Gh if Gh != 0 else 0
            ductility = "Sünek (Ductile)" if Prh > 1.75 else "Gevrek (Brittle)"
            
            # Cauchy Pressures (Cubic approx)
            Cp = C[0,1] - C[3,3]
            
            # Anisotropy
            AU = 5*(Gv/Gr) + (Bv/Br) - 6 if (Gr!=0 and Br!=0) else 0
            AZ = 2*C[3,3]/(C[0,0]-C[0,1]) if (C[0,0]-C[0,1])!=0 else 0
            
            # Hardness (Chen Model: Hv = 2*(G^3/B^2)^0.585 - 3)
            try:
                HvChen_h = 2 * ((Gh**3) / (Bh**2))**0.585 - 3 if Bh > 0 else 0
                HvChen_h = max(0, HvChen_h)
            except:
                HvChen_h = 0
            
            # Formatting Output
            report = f"""======================================================================
      Mekanik ve Elastik Özellikler (Voigt-Reuss-Hill Ortalama)
======================================================================
Modül (GPa)         Voigt (V)      Reuss (R)      Hill (H)
----------------------------------------------------------------------
Bulk Modülü (B)   : {Bv:>10.2f}     {Br:>10.2f}     {Bh:>10.2f}
Shear Modülü (G)  : {Gv:>10.2f}     {Gr:>10.2f}     {Gh:>10.2f}
Young Modülü (E)  : {Ev:>10.2f}     {Er:>10.2f}     {Eh:>10.2f}
Poisson Oranı (v) : {nuv:>10.4f}     {nur:>10.4f}     {nuh:>10.4f}
Pugh Oranı (B/G)  : {Prv:>10.2f}     {Prr:>10.2f}     {Prh:>10.2f}
----------------------------------------------------------------------
Kırılganlık       : {ductility} (B/G > 1.75 eşik)
Cauchy Basıncı    : {Cp:.2f} (Pozitif: Metalik, Negatif: Kovalent)
Vickers Sertliği  : {HvChen_h:.2f} GPa (Chen Empirik Modeli)
Evrensel Anizot.  : {AU:.4f} (Au = 0 ise izotropik)
Zener Anizotropi  : {AZ:.4f} (Az = 1 ise izotropik)
======================================================================"""
            
            self.txt_output.setText(report)
            
        except Exception as e:
            QMessageBox.critical(self, "Hesaplama Hatası", f"Değerler hesaplanırken beklenmeyen bir hata oluştu:\n{e}")
