from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QSpinBox, QDoubleSpinBox, QLineEdit, QTextEdit
)
from utils.style_manager import notifier

class AIMDOtomasyonWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Sol Panel (Kontrol Paneli)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(400)
        
        # Bilgi Notları
        lbl_info = QLabel("<b>Kritik Uyarılar:</b><br>- AIMD süper hücre (min 10 Å) ile yapılmalıdır.<br>- Hidrojen içeren sistemlerde kütleyi (POMASS) 2.0 yapıp POTIM'i 1.0 seçebilirsiniz.")
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("color: #d35400; font-size: 13px;")
        left_layout.addWidget(lbl_info)
        
        # 1. Fiziksel Parametreler
        group_phys = QGroupBox("1. Fiziksel Parametreler")
        l_phys = QFormLayout()
        
        self.le_temps = QLineEdit("300 450 600 750")
        self.le_pomass = QLineEdit("39.098 47.867 2.00")
        self.sb_nsw = QSpinBox(); self.sb_nsw.setRange(1000, 1000000); self.sb_nsw.setValue(20000); self.sb_nsw.setSingleStep(1000)
        self.sb_potim = QDoubleSpinBox(); self.sb_potim.setRange(0.1, 5.0); self.sb_potim.setValue(1.0); self.sb_potim.setSingleStep(0.5)
        
        l_phys.addRow("Sıcaklıklar (K):", self.le_temps)
        l_phys.addRow("POMASS:", self.le_pomass)
        l_phys.addRow("NSW (Adım):", self.sb_nsw)
        l_phys.addRow("POTIM (fs):", self.sb_potim)
        group_phys.setLayout(l_phys)
        
        # 2. TRUBA / SLURM Ayarları
        group_slurm = QGroupBox("2. TRUBA (SLURM) Ayarları")
        l_slurm = QFormLayout()
        
        self.le_email = QLineEdit("s.yamcicier@gmail.com")
        self.le_queue = QLineEdit("hamsi")
        self.sb_cores = QSpinBox(); self.sb_cores.setRange(1, 256); self.sb_cores.setValue(56)
        self.le_vasp_path = QLineEdit("/arf/home/syamcicier/derleme/vasp.6.3.0/bin/vasp_std")
        
        l_slurm.addRow("E-Posta:", self.le_email)
        l_slurm.addRow("Kuyruk:", self.le_queue)
        l_slurm.addRow("Çekirdek:", self.sb_cores)
        l_slurm.addRow("VASP Yolu:", self.le_vasp_path)
        group_slurm.setLayout(l_slurm)
        
        self.btn_generate = QPushButton("Bash Betiğini Üret")
        self.btn_generate.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        self.btn_generate.clicked.connect(self.generate_script)
        
        left_layout.addWidget(group_phys)
        left_layout.addWidget(group_slurm)
        left_layout.addWidget(self.btn_generate)
        left_layout.addStretch()
        
        # Sağ Panel (Önizleme)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        lbl_preview = QLabel("<b>Üretilen Çalıştırma Betiği (run_aimd.sh)</b>")
        right_layout.addWidget(lbl_preview)
        
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace; font-size: 14px;")
        right_layout.addWidget(self.text_preview)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)
        
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
        temps = self.le_temps.text()
        pomass = self.le_pomass.text()
        nsw = self.sb_nsw.value()
        potim = self.sb_potim.value()
        
        email = self.le_email.text()
        queue = self.le_queue.text()
        cores = self.sb_cores.value()
        vasp_path = self.le_vasp_path.text()
        
        bash_script = f"""#!/bin/bash

# ==============================================================================
# AIMD COKLU SICAKLIK OTOMASYONU (VASP Kontrol Merkezi)
# ==============================================================================

# --- 1. SICAKLIK LISTESI ---
TEMPS="{temps}"

# --- 2. GUVENLIK KONTROLLERİ ---
if [ ! -f "POSCAR" ] || [ ! -f "POTCAR" ]; then
    echo "HATA: Ana dizinde POSCAR veya POTCAR bulunamadi!"
    echo "Lutfen super hucre POSCAR'inizi ve ona uygun POTCAR'inizi bu dizine koyun."
    exit 1
fi

echo "DIKKAT: POSCAR'in bir super hucre oldugundan (min 10x10x10 A) emin olun."
echo "DIKKAT: POMASS siralamasinin POTCAR ile ayni oldugunu dogrulayin."
sleep 3

# --- 3. OTOMASYON DONGUSU ---
for T in $TEMPS; do
    echo ">>> $T K icin klasor ve dosyalar hazirlaniyor..."
    DIR="T_$T"
    mkdir -p $DIR

    # A. KPOINTS DOSYASINI OLUSTUR
    cat <<EOF > $DIR/KPOINTS
K-Points for AIMD
 0
Gamma
 1  1  1
 0  0  0
EOF

    # B. INCAR DOSYASINI OLUSTUR (Sicakliga Gore)
    cat <<EOF > $DIR/INCAR
SYSTEM = AIMD_$T
# --- MD AYARLARI ---
IBRION = 0
NSW    = {nsw}
POTIM  = {potim}
TEBEG  = $T
TEEND  = $T
SMASS  = 0
MDALGO = 2

# --- Elektronik Çözücü ---
ISMEAR = 0
SIGMA  = 0.05
ALGO   = VeryFast
EDIFF  = 1E-4
NELMIN = 4
MAXMIX = 40
LREAL  = Auto

# --- Kütle ve Çıktı Ayarları ---
POMASS = {pomass}
NBLOCK = 1
KBLOCK = 100
NWRITE = 1
LWAVE  = .FALSE.
LCHARG = .FALSE.
EOF

    # C. SLURM DOSYASINI OLUSTUR
    cat <<EOF > $DIR/vasp.slurm
#!/bin/bash
#SBATCH -p {queue}
#SBATCH -A syamcicier
#SBATCH -J AIMD_$T
#SBATCH -N 1
#SBATCH -n {cores}
#SBATCH --time=15-00:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user={email}

export OMP_NUM_THREADS=1
mpirun -n {cores} {vasp_path} > vasp.out
EOF

    # D. POSCAR ve POTCAR KOPYALA
    cp POSCAR $DIR/
    cp POTCAR $DIR/

    # E. IŞI TRUBA'YA GÖNDER
    cd $DIR
    sbatch vasp.slurm
    echo "$DIR dizinindeki is kuyruga eklendi."
    cd ..
done

echo "=============================================================================="
echo "Tüm sıcaklıklar icin klasorler acildi, INCAR/KPOINTS uretildi ve isler gonderildi!"
"""
        self.text_preview.setText(bash_script)
