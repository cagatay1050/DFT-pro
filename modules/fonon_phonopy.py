from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QMessageBox, QSpinBox, QComboBox,
    QScrollArea, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt
from utils.style_manager import apply_global_style, notifier

class FononPhonopyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Sol Panel (Kontrol Paneli)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(400)
        
        # 1. Süper Hücre Boyutları
        group_cell = QGroupBox("1. Süper Hücre Boyutları")
        l_cell = QFormLayout()
        
        self.sb_dim_x = QSpinBox(); self.sb_dim_x.setRange(1, 10); self.sb_dim_x.setValue(2)
        self.sb_dim_y = QSpinBox(); self.sb_dim_y.setRange(1, 10); self.sb_dim_y.setValue(2)
        self.sb_dim_z = QSpinBox(); self.sb_dim_z.setRange(1, 10); self.sb_dim_z.setValue(2)
        
        l_cell.addRow("X Boyutu:", self.sb_dim_x)
        l_cell.addRow("Y Boyutu:", self.sb_dim_y)
        l_cell.addRow("Z Boyutu:", self.sb_dim_z)
        
        self.le_slurm = QLineEdit("vasp.slurm")
        l_cell.addRow("SLURM Dosyası Adı:", self.le_slurm)
        group_cell.setLayout(l_cell)
        
        # 2. INCAR Ayarları
        group_incar = QGroupBox("2. INCAR Hassasiyet Ayarları")
        l_incar = QFormLayout()
        
        self.sb_encut = QSpinBox(); self.sb_encut.setRange(100, 2000); self.sb_encut.setValue(550); self.sb_encut.setSingleStep(10)
        self.le_ediff = QLineEdit("1E-8")
        
        self.cb_ismear = QComboBox()
        self.cb_ismear.addItems(["0 (Yalıtkan/Yarı İletken)", "1 (Metal)", "2", "-5"])
        
        l_incar.addRow("ENCUT (eV):", self.sb_encut)
        l_incar.addRow("EDIFF:", self.le_ediff)
        l_incar.addRow("ISMEAR:", self.cb_ismear)
        group_incar.setLayout(l_incar)
        
        self.btn_generate = QPushButton("Bash Betiğini Üret")
        self.btn_generate.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        self.btn_generate.clicked.connect(self.generate_script)
        
        left_layout.addWidget(group_cell)
        left_layout.addWidget(group_incar)
        left_layout.addWidget(self.btn_generate)
        left_layout.addStretch()
        
        # Sağ Panel (Betik Önizleme)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        lbl = QLabel("<b>3. Üretilen Çalıştırma Betiği (run_phonopy.sh)</b>")
        right_layout.addWidget(lbl)
        
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace; font-size: 14px;")
        right_layout.addWidget(self.text_preview)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)
        
        # İlk açılışta script üret
        self.generate_script()
        
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        lbl = QLabel("Bu modül bash betiği üretir. Grafiksel estetik ayarı bulunmamaktadır.")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        layout.addStretch()

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        pass
        
    def generate_script(self):
        dx = self.sb_dim_x.value()
        dy = self.sb_dim_y.value()
        dz = self.sb_dim_z.value()
        slurm = self.le_slurm.text()
        
        encut = self.sb_encut.value()
        ediff = self.le_ediff.text()
        ismear = self.cb_ismear.currentText().split(" ")[0]
        
        bash_script = f"""#!/bin/bash
# ==========================================
# PHONOPY OTOMASYON BETİĞİ (TRUBA / SLURM İÇİN)
# Otomatik INCAR Üretimi (ISYM=0)
# Hazırlayan: DFT Lab (Desktop)
# ==========================================

echo "Adım 1: Süper Hücreler {dx}x{dy}x{dz} Boyutlarında Oluşturuluyor..."
phonopy -d --dim="{dx} {dy} {dz}" -c POSCAR

# Supercell klasörlerini oluştur
mkdir -p supercells
mv POSCAR-* supercells/
mv SPOSCAR supercells/

echo "Adım 2: INCAR Dosyası Yüksek Hassasiyetle Hazırlanıyor..."
cat << EOF > INCAR
# --- Hassasiyet Ayarları ---
PREC   = Accurate
ENCUT  = {encut}
EDIFF  = {ediff}
IALGO  = 38
LREAL  = .FALSE.
ADDGRID = .TRUE.

# --- Fonon için Zorunlu Parametre ---
ISYM   = 0     ! Simetri kapatılmalı (Fonon hesaplaması için kritiktir!)

# --- Elektronik Çözücü ---
ISMEAR = {ismear}
SIGMA  = 0.05
EOF

echo "Adım 3: {slurm} İş Dosyası Kopyalanıyor..."
cp {slurm} supercells/
cp INCAR supercells/
cp POTCAR supercells/
cp KPOINTS supercells/

echo "Adım 4: Klasörlere Geçilip SLURM İşleri Gönderiliyor..."
cd supercells
for poscar in POSCAR-*; do
    dir_name="disp_${{poscar#POSCAR-}}"
    mkdir -p "$dir_name"
    
    # Dosyaları Taşı
    mv "$poscar" "$dir_name/POSCAR"
    cp INCAR "$dir_name/"
    cp POTCAR "$dir_name/"
    cp KPOINTS "$dir_name/"
    cp {slurm} "$dir_name/"
    
    # Job'ı Gönder
    cd "$dir_name"
    sbatch {slurm}
    echo "$dir_name dizini kuyruğa eklendi."
    cd ..
done

cd ..
echo "=========================================="
echo "İŞLEM TAMAMLANDI!"
echo "Tüm işler bittiğinde bu dizinde 'phonopy -f supercells/disp_*/vasprun.xml' komutunu çalıştırabilirsiniz."
"""
        self.text_preview.setText(bash_script)
