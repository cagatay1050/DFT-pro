from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit, QApplication
)

class INCARArsiviWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel("⚙️ INCAR ve TRUBA Gönderim Arşivi")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0078d7;")
        layout.addWidget(lbl_title)
        
        lbl_desc = QLabel("Hesaplama türünüze en uygun, test edilmiş ve makale kalitesindeki (Q1) INCAR dosyalarını buradan kopyalayabilirsiniz.")
        lbl_desc.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(lbl_desc)
        
        self.combo = QComboBox()
        self.combo.setStyleSheet("font-size: 14px; padding: 5px;")
        self.combo.addItems([
            "Seçiniz...",
            "🟢 Optimizasyon",
            "🟢 IS ve FS için Kaba Optimizasyon",
            "🟢 IS ve FS için ince Optimizasyon",
            "🟢 NEB INCAR",
            "🟢 KÜTLE İÇİ (BULK) - IS ve FS Optimizasyonu",
            "🟢 KÜTLE İÇİ (BULK) - CI-NEB Geçiş Durumu",
            "🔵 YÜZEY (SLAB) - IS ve FS Optimizasyonu",
            "🔵 YÜZEY (SLAB) - CI-NEB Geçiş Durumu",
            "⚪ STANDART - Hücre ve Geometri Optimizasyonu (ISIF=3)"
        ])
        self.combo.currentTextChanged.connect(self.on_selection_changed)
        layout.addWidget(self.combo)
        
        self.lbl_warning = QLabel("")
        self.lbl_warning.setStyleSheet("color: red; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.lbl_warning)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("font-family: Consolas; font-size: 14px; background-color: #1e1e1e; color: #d4d4d4;")
        layout.addWidget(self.text_edit)
        
    def on_selection_changed(self, text):
        warning = ""
        content = ""
        
        if text == "🟢 Optimizasyon":
            warning = "⚠️ Manyetik malzemeler için düzenlemeyi unutmayın."
            content = """SYSTEM = Bulk Supercell - IS/FS Optimizasyonu

# --- Elektronik Optimizasyon ---
PREC    = Accurate
ENCUT   = 500
EDIFF   = 1E-6
ALGO    = Fast         ! Hücre esneyeceği için Fast daha verimlidir
LREAL   = Auto
ISMEAR  = 0
SIGMA   = 0.05
ISYM    = 2            ! Standart optimizasyonlarda simetri AÇIK kalabilir

# --- İyonik Optimizasyon ---
IBRION  = 2
ISIF    = 3            ! DİKKAT: Hem atomları hem de hücre hacmini serbest bırakır
NSW     = 100
EDIFFG  = -0.02

# --- Çıktı Kontrolü ---
LWAVE   = .FALSE.
LCHARG  = .FALSE.
"""
        elif text == "🟢 IS ve FS için Kaba Optimizasyon":
            warning = "⚠️ Manyetik malzemeler için düzenlemeyi unutmayın."
            content = """SYSTEM = Kaba_Optimizasyon_Dipolsuz

# --- Elektronik Cozucu (Hizlandirilmis) ---
ALGO   = Fast
PREC   = Normal
NELM   = 100
EDIFF  = 1E-5
ISMEAR = 0
SIGMA  = 0.05
LREAL  = Auto

# --- Iyonik Optimizasyon (Kaba - Hizli) ---
IBRION = 2         ! Conjugate-Gradient
ISIF   = 2         ! Sadece atomlar hareket eder
NSW    = 200
EDIFFG = -0.05     ! Hizlica bitmesi icin kaba kuvvet kriteri

# --- Yuzey ve Dipol (KAPALI) ---
ISYM   = 0         ! Simetriyi kapat (Slab icin sart)
LDIPOL = .FALSE.   ! Yuku calkalamamak icin gecici olarak kapali

# --- Fiziksel Parametreler ---
IVDW   = 11        ! DFT-D3 Van der Waals
ISPIN  = 2         ! Spin polarizasyonu acik

# --- Paralellestirme (TRUBA Orfoz) ---
NCORE  = 8         ! Orfoz icin ideal deger

# --- Cikti Kontrolu ---
LWAVE  = .TRUE.    ! Ince asamada okutmak icin WAVECAR uretilmeli
LCHARG = .FALSE.
"""
        elif text == "🟢 IS ve FS için ince Optimizasyon":
            warning = "⚠️ Manyetik malzemeler için düzenlemeyi unutmayın."
            content = """SYSTEM = Ince_Optimizasyon_Makale_Kalitesi

# --- Elektronik Cozucu (Hassas) ---
ALGO   = Normal
PREC   = Accurate
NELM   = 100
EDIFF  = 1E-6
ISMEAR = 0
SIGMA  = 0.05
LREAL  = Auto

# --- Iyonik Optimizasyon (Hassas) ---
IBRION = 2
ISIF   = 2
NSW    = 100       ! Atomlar zaten yerinde oldugu icin cok surmeyecek
EDIFFG = -0.02     ! Makale kalitesinde kuvvet kriteri

# --- Yuzey ve Dipol (ACIK - Kritik!) ---
ISYM   = 0
LDIPOL = .TRUE.    ! NEB icin referans olacak, acik olmali
IDIPOL = 3         ! Z eksenine (vakuma) uygula
DIPOL  = 0.5 0.5 0.5 ! Hucre kitle merkezi referansi

# --- Fiziksel Parametreler ---
IVDW   = 11
ISPIN  = 2

# --- Paralellestirme (TRUBA Orfoz) ---
NCORE  = 8

# --- Cikti Kontrolu ---
LWAVE  = .FALSE.   ! Diski doldurmamak icin kapatilabilir
LCHARG = .FALSE.
"""
        elif text == "🟢 NEB INCAR":
            warning = "⚠️ Manyetik malzemeler için düzenlemeyi unutmayın."
            content = """SYSTEM = NEB_H2_Desorpsiyonu_7_Imaj

# --- Elektronik Cozucu ---
ALGO   = Normal
PREC   = Accurate
NELM   = 100
EDIFF  = 1E-6
ISMEAR = 0
SIGMA  = 0.05
LREAL  = Auto

# --- NEB Ozel Parametreleri (VTST Kodlari) ---
IMAGES = 7         ! Ara imaj sayisi (TRUBA cekirdeklerine tam bolunmeli)
LCLIMB = .TRUE.    ! Climbing Image (Tepe noktasini bulur)
SPRING = -5.0      ! Imajlar arasi yay sabiti
ICHAIN = 0         ! NEB algoritmasini acar

# --- Iyonik Optimizasyon (NEB Icin LBFGS) ---
IBRION = 3         ! VTST araclari icin sart
IOPT   = 1         ! LBFGS algoritmasi
POTIM  = 0.0       ! IOPT acikken POTIM sifirlanmali
MAXMOVE= 0.2       ! Maksimum adim siniri
NSW    = 300       ! NEB uzun surer, adim sayisi bol verilmeli
EDIFFG = -0.02     ! Bariyerin dogrulugu icin hassas kriter

# --- Yuzey ve Dipol (ACIK OLMAK ZORUNDA) ---
ISYM   = 0
LDIPOL = .TRUE.
IDIPOL = 3
DIPOL  = 0.5 0.5 0.5

# --- Fiziksel Parametreler ---
IVDW   = 11
ISPIN  = 2

# --- Paralellestirme (TRUBA Orfoz - 112 Core Icin) ---
NCORE  = 8         ! Her imaja 16 core duser, 8'e tam bolunur

# --- Cikti Kontrolu ---
LWAVE  = .FALSE.   ! Her imaj devasa WAVECAR yazmasin diye
LCHARG = .FALSE.
"""
        elif text == "🟢 KÜTLE İÇİ (BULK) - IS ve FS Optimizasyonu":
            warning = "⚠️ Kütle içi (Supercell) hesaplamalarda LDIPOL KAPALIDIR."
            content = """SYSTEM = Bulk Supercell - IS/FS Optimizasyonu

# --- Elektronik Optimizasyon ---
PREC    = Accurate     ! Makale kalitesi için zorunlu
ADDGRID = .TRUE.       ! Ekstra fourier ağı
ENCUT   = 500
EDIFF   = 1E-6         
ALGO    = Normal
LREAL   = Auto
ISMEAR  = 0
SIGMA   = 0.05
ISYM    = 0            ! NEB'e girecek yapılar için simetri kapalı

# --- İyonik Optimizasyon ---
IBRION  = 2            
ISIF    = 2            
NSW     = 100          
EDIFFG  = -0.02        

# --- Çıktı Kontrolü ---
LWAVE   = .FALSE.       
LCHARG  = .FALSE.      
"""
        elif text == "🟢 KÜTLE İÇİ (BULK) - CI-NEB Geçiş Durumu":
            warning = "💡 'IMAGES =' kısmını ürettiğiniz imaj sayısına göre güncelleyin."
            content = """SYSTEM = Bulk Supercell - CI-NEB Hesabi

# --- Elektronik Optimizasyon ---
PREC    = Accurate     
ADDGRID = .TRUE.       
ENCUT   = 500
EDIFF   = 1E-6         
ALGO    = Normal
LREAL   = Auto
ISMEAR  = 0
SIGMA   = 0.05
ISYM    = 0            

# --- NEB Motoru (VTST Parametreleri) ---
IMAGES  = 5            ! DİKKAT: Ürettiğiniz imaj sayısını yazın
LCLIMB  = .TRUE.       
SPRING  = -5.0         

# --- İyonik Optimizasyon (NEB Özel Algoritması) ---
IBRION  = 3            
IOPT    = 1            
POTIM   = 0.0          
MAXMOVE = 0.2          
NSW     = 200          
EDIFFG  = -0.02        

# --- Çıktı Kontrolü ---
LWAVE   = .FALSE.      
LCHARG  = .FALSE.      
"""
        elif text == "🔵 YÜZEY (SLAB) - IS ve FS Optimizasyonu":
            warning = "🚨 Slab modellerinde LDIPOL = .TRUE. olmak zorundadır!"
            content = """SYSTEM = Slab Surface - IS/FS Optimizasyonu

# --- Elektronik Optimizasyon ---
PREC    = Accurate     
ADDGRID = .TRUE.       
ENCUT   = 500
EDIFF   = 1E-6         
ALGO    = Normal
LREAL   = Auto
ISMEAR  = 0
SIGMA   = 0.05
ISYM    = 0            

# --- İyonik Optimizasyon ---
IBRION  = 2            
ISIF    = 2            ! Vakum mesafesini korumak için ISIF=2
NSW     = 100          
EDIFFG  = -0.02        

# --- Dipol Düzeltmesi (Slab İçin Zorunlu) ---
LDIPOL  = .TRUE.       
IDIPOL  = 3            ! Z ekseninde (vakum yönü)
DIPOL   = 0.5 0.5 0.5  ! Slab kütle merkezi

# --- Çıktı Kontrolü ---
LWAVE   = .FALSE.       
LCHARG  = .FALSE.      
"""
        elif text == "🔵 YÜZEY (SLAB) - CI-NEB Geçiş Durumu":
            warning = ""
            content = """SYSTEM = Slab Surface - CI-NEB Hesabi

# --- Elektronik Optimizasyon ---
PREC    = Accurate     
ADDGRID = .TRUE.       
ENCUT   = 500
EDIFF   = 1E-6         
ALGO    = Normal
LREAL   = Auto
ISMEAR  = 0
SIGMA   = 0.05
ISYM    = 0            

# --- NEB Motoru (VTST) ---
IMAGES  = 5            ! İmaj sayısını güncelleyin
LCLIMB  = .TRUE.       
SPRING  = -5.0         

# --- İyonik Optimizasyon (NEB Motoru) ---
IBRION  = 3            
IOPT    = 1            
POTIM   = 0.0          
MAXMOVE = 0.2          
NSW     = 200          
EDIFFG  = -0.02        

# --- Dipol Düzeltmesi (IS/FS ile Aynı) ---
LDIPOL  = .TRUE.       
IDIPOL  = 3            
DIPOL   = 0.5 0.5 0.5  

# --- Çıktı Kontrolü ---
LWAVE   = .FALSE.      
LCHARG  = .FALSE.      
"""
        elif text == "⚪ STANDART - Hücre ve Geometri Optimizasyonu (ISIF=3)":
            warning = "✅ Kristalin hem hacmini hem koordinatlarını optimize etmek içindir."
            content = """SYSTEM = Full Cell Optimization (ISIF=3)

# --- Elektronik Optimizasyon ---
PREC    = Accurate
ENCUT   = 500
EDIFF   = 1E-6
ALGO    = Fast         
LREAL   = Auto
ISMEAR  = 0
SIGMA   = 0.05
ISYM    = 2            

# --- İyonik Optimizasyon ---
IBRION  = 2
ISIF    = 3            
NSW     = 100
EDIFFG  = -0.02

# --- Çıktı Kontrolü ---
LWAVE   = .FALSE.
LCHARG  = .FALSE.
"""

        self.lbl_warning.setText(warning)
        self.text_edit.setPlainText(content)

    def get_local_settings_widget(self):
        return None
