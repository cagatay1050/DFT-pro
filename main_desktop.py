import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, 
    QStackedWidget, QLabel, QVBoxLayout,
    QDockWidget, QMenuBar, QMenu, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont, QIcon

# Existing modules
from modules.termodinamik_vdos import TermodinamikVDOSWidget
from modules.global_settings import GlobalSettingsWidget
from modules.difuzyon_arrhenius import DifuzyonArrheniusWidget
from modules.neb_master import NEBMasterWidget
from modules.incar_arsivi import INCARArsiviWidget
from modules.kinetik_msd import KinetikMSDWidget
from modules.yapisal_analiz_rdf import YapisalAnalizRDFWidget
from modules.titresim_vdos import TitresimVDOSWidget
from modules.parcalanma_termodinamigi import ParcalanmaTermodinamigiWidget
from modules.aimd_kararlilik import AIMDKararlilikWidget
from modules.elektronik_band import ElektronikBandWidget
from modules.neb_enerji_bariyeri import NEBEnerjiBariyeriWidget
from modules.makale_paneli import MakalePaneliWidget
from modules.hidrur_aday_jeneratoru import HidrurAdayJeneratoruWidget
from modules.fonon_phonopy import FononPhonopyWidget
from modules.fonon_band import FononBandWidget
from modules.aimd_otomasyon import AIMDOtomasyonWidget
from modules.yogunluk_dos import YogunlukDOSWidget
from modules.aimd_farkli_format import AIMDFarkliFormatWidget
from modules.castep_kinetik import CastepKinetikWidget
from modules.vasp_termodinamik_kiyas import VaspTermodinamikKiyasWidget
from modules.yuzey_enerjisi import YuzeyEnerjisiWidget
from modules.grafik_birlestirici import GrafikBirlestiriciWidget
from modules.formasyon_enerjisi import FormasyonEnerjisiWidget
from modules.kristal_yapi_bulucu import KristalYapiBulucuWidget
from modules.rp_hidrit_2d import RPHidritBulucuWidget
from modules.stokiyometri_katkilama import StokiyometriKatkilamaWidget
from modules.spin_polarize_bant import SpinPolarizeBantWidget
from modules.harici_araclar import HariciAraclarWidget
from modules.mekanik_ozellikler import MekanikOzelliklerWidget

# New 8 INCAR Generator modules
from modules.elastik_sabitler import ElastikSabitlerWidget
from modules.hse06_bant import HSE06BantWidget
from modules.geometri_optimizasyonu import GeometriOptimizasyonuWidget
from modules.statik_enerji import StatikEnerjiWidget
from modules.yuzey_slab import YuzeySlabWidget
from modules.neb_is_fs import NebIsFsWidget
from modules.ci_neb import CiNebWidget
from modules.hse06_optik import Hse06OptikWidget

class WelcomeDashboard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_title = QLabel("🚀 DFT Lab Dashboard'a Hoş Geldiniz")
        lbl_title.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_subtitle = QLabel("Lütfen yukarıdaki menüden veya aşağıdaki hızlı erişim kartlarından bir modül seçin.")
        lbl_subtitle.setStyleSheet("font-size: 16px; color: #7f8c8d; margin-bottom: 40px;")
        lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_subtitle)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        
        shortcuts = [
            ("🔥 Termodinamik (VDOS)", 1, "#e74c3c"),
            ("🌌 Elektronik Bant", 10, "#9b59b6"),
            ("🎵 Fonon Band Yapısı", 15, "#2980b9"),
            ("🎨 Master Grafik Birleştirici", 22, "#f39c12"),
            ("🔍 Kristal Yapı Bulucu", 24, "#16a085"),
            ("⚡ Spin-Polarize Bant", 27, "#8e44ad"),
            ("🏗️ Geometri Optimizasyonu", 30, "#34495e"),
            ("⛰️ CI-NEB Hesaplaması", 34, "#c0392b")
        ]
        
        row = 0
        col = 0
        for text, index, color in shortcuts:
            btn = QPushButton(text)
            btn.setFixedSize(280, 100)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-size: 15px;
                    font-weight: bold;
                    border-radius: 12px;
                }}
                QPushButton:hover {{
                    background-color: #2c3e50;
                }}
            """)
            btn.clicked.connect(lambda checked, idx=index: self.main_window.display_module(idx))
            grid.addWidget(btn, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
                
        layout.addLayout(grid)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DFT Lab Dashboard (Desktop V4.1 - INCAR Generators)")
        self.resize(1600, 900)
        
        # Menu Bar (Top)
        self.menu_bar = self.menuBar()
        self.menu_bar.setStyleSheet("QMenuBar { font-size: 14px; padding: 5px; } QMenu { font-size: 14px; }")
        
        # Central Layout Area
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Stacked Widget for pages
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        self.setup_modules()
        self.setup_top_menu()
        
        self.stacked_widget.currentChanged.connect(self.update_local_settings)
        
        # Settings Dock Widget
        self.settings_dock = QDockWidget("🎨 Grafik Ayarları (Origin Style)", self)
        self.settings_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.settings_widget = GlobalSettingsWidget()
        self.settings_dock.setWidget(self.settings_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.settings_dock)
        
        # Ayarlar Menu Action
        settings_menu = self.menu_bar.addMenu("⚙️ Ayarlar")
        toggle_settings_action = QAction("Grafik Ayarlarını Göster/Gizle", self)
        toggle_settings_action.triggered.connect(self.toggle_settings_dock)
        settings_menu.addAction(toggle_settings_action)
        
        # Home Menu
        home_action = QAction("🏠 Ana Sayfa", self)
        home_action.triggered.connect(lambda checked: self.display_module(0))
        self.menu_bar.addAction(home_action)
        
        self.update_local_settings(0)

    def setup_modules(self):
        # 0: Dashboard (Welcome)
        self.dashboard_widget = WelcomeDashboard(self)
        self.stacked_widget.addWidget(self.dashboard_widget)
        
        self.widgets = []
        self.widgets.append(TermodinamikVDOSWidget())               # 1
        self.widgets.append(DifuzyonArrheniusWidget())              # 2
        self.widgets.append(NEBMasterWidget())                      # 3
        self.widgets.append(INCARArsiviWidget())                    # 4
        self.widgets.append(KinetikMSDWidget())                     # 5
        self.widgets.append(YapisalAnalizRDFWidget())               # 6
        self.widgets.append(TitresimVDOSWidget())                   # 7
        self.widgets.append(ParcalanmaTermodinamigiWidget())        # 8
        self.widgets.append(AIMDKararlilikWidget())                 # 9
        self.widgets.append(ElektronikBandWidget())                 # 10
        self.widgets.append(NEBEnerjiBariyeriWidget())              # 11
        self.widgets.append(MakalePaneliWidget())                   # 12
        self.widgets.append(HidrurAdayJeneratoruWidget())           # 13
        self.widgets.append(FononPhonopyWidget())                   # 14
        self.widgets.append(FononBandWidget())                      # 15
        self.widgets.append(AIMDOtomasyonWidget())                  # 16
        self.widgets.append(YogunlukDOSWidget())                    # 17
        self.widgets.append(AIMDFarkliFormatWidget())               # 18
        self.widgets.append(CastepKinetikWidget())                  # 19
        self.widgets.append(VaspTermodinamikKiyasWidget())          # 20
        self.widgets.append(YuzeyEnerjisiWidget())                  # 21
        self.widgets.append(GrafikBirlestiriciWidget())             # 22
        self.widgets.append(FormasyonEnerjisiWidget())              # 23
        self.widgets.append(KristalYapiBulucuWidget())              # 24
        self.widgets.append(RPHidritBulucuWidget())                 # 25
        self.widgets.append(StokiyometriKatkilamaWidget())          # 26
        self.widgets.append(SpinPolarizeBantWidget())               # 27
        self.widgets.append(ElastikSabitlerWidget())                # 28
        self.widgets.append(HSE06BantWidget())                      # 29
        self.widgets.append(GeometriOptimizasyonuWidget())          # 30
        self.widgets.append(StatikEnerjiWidget())                   # 31
        self.widgets.append(YuzeySlabWidget())                      # 32
        self.widgets.append(NebIsFsWidget())                        # 33
        self.widgets.append(CiNebWidget())                          # 34
        self.widgets.append(Hse06OptikWidget())                     # 35
        self.widgets.append(HariciAraclarWidget())                  # 36
        self.widgets.append(MekanikOzelliklerWidget())              # 37
        
        for w in self.widgets:
            self.stacked_widget.addWidget(w)
            
    def setup_top_menu(self):
        # 1. Giriş Dosyası Üreticileri (INCAR) - NEW CATEGORY
        menu_incar = self.menu_bar.addMenu("⚙️ Giriş Dosyası Üreticileri (INCAR)")
        self.add_menu_action(menu_incar, "⚙️ INCAR & TRUBA Arşivi", 4)
        self.add_menu_action(menu_incar, "🎶 Fonon ve Phonopy (Otomasyon)", 14)
        self.add_menu_action(menu_incar, "🏃‍♂️ AIMD Çoklu Sıcaklık (Otomasyon)", 16)
        self.add_menu_action(menu_incar, "🧲 Elastik Sabitler (IBRION=6)", 28)
        self.add_menu_action(menu_incar, "💎 HSE06 Bant Yapısı (Otomasyon)", 29)
        self.add_menu_action(menu_incar, "🏗️ Geometri Optimizasyonu (INCAR)", 30)
        self.add_menu_action(menu_incar, "🔋 Statik Enerji / Referans (INCAR)", 31)
        self.add_menu_action(menu_incar, "🧫 Yüzey & Slab Otomasyonu (VASPKIT)", 32)
        self.add_menu_action(menu_incar, "🏗️ NEB IS/FS Optimizasyonu (2-Aşamalı)", 33)
        self.add_menu_action(menu_incar, "⛰️ CI-NEB Hesaplaması (INCAR)", 34)
        self.add_menu_action(menu_incar, "🌈 HSE06 Optik Özellikler (2-Aşamalı)", 35)

        # 2. Termodinamik ve Kinetik (🔥/⚡)
        menu_thermo = self.menu_bar.addMenu("🔥 Termodinamik ve Kinetik")
        self.add_menu_action(menu_thermo, "Termodinamik (VDOS)", 1)
        self.add_menu_action(menu_thermo, "VASP Termodinamik Kıyaslama (F, S, Cv, E)", 20)
        self.add_menu_action(menu_thermo, "Parçalanma Termodinamiği (T_des)", 8)
        self.add_menu_action(menu_thermo, "Kinetik (MSD & Difüzyon)", 5)
        self.add_menu_action(menu_thermo, "Difüzyon (Arrhenius)", 2)
        self.add_menu_action(menu_thermo, "CASTEP Kinetik Analiz", 19)
        self.add_menu_action(menu_thermo, "Formasyon Enerjisi Hesaplama Modülü", 23)
        self.add_menu_action(menu_thermo, "Yüzey Enerjisi Analizörü (Script)", 21)
        
        # 3. Kuantum ve Elektronik Yapı (🌌/⚡)
        menu_quantum = self.menu_bar.addMenu("🌌 Kuantum & Elektronik Yapı")
        self.add_menu_action(menu_quantum, "Elektronik Bant Yapısı (Band)", 10)
        self.add_menu_action(menu_quantum, "Spin-Polarize Bant Yapısı", 27)
        self.add_menu_action(menu_quantum, "Yoğunluk Durumları (DOS/PDOS)", 17)
        
        # 4. Titreşim ve Dinamik (🎵/⏱️)
        menu_vib = self.menu_bar.addMenu("🎵 Titreşim & Dinamik")
        self.add_menu_action(menu_vib, "Titreşim Spektrumu (VDoS)", 7)
        self.add_menu_action(menu_vib, "Fonon Band Yapısı", 15)
        self.add_menu_action(menu_vib, "AIMD Kararlılık (Sıcaklık/Enerji)", 9)
        self.add_menu_action(menu_vib, "AIMD Kararlılık (farklı format)", 18)
        
        # 5. Yapısal Analiz ve Malzeme (⚛️/🔍)
        menu_struct = self.menu_bar.addMenu("⚛️ Yapısal Analiz & Malzeme")
        self.add_menu_action(menu_struct, "Yapısal Analiz (RDF)", 6)
        self.add_menu_action(menu_struct, "Kristal Yapı Bulucu", 24)
        self.add_menu_action(menu_struct, "2D RP Hidrit Bulucu", 25)
        self.add_menu_action(menu_struct, "Stokiyometri ve Katkılama Analizi", 26)
        self.add_menu_action(menu_struct, "Hidrür Aday Jeneratörü", 13)
        self.add_menu_action(menu_struct, "⚙️ Mekanik Özellikler (VELAS Klonu)", 37)
        
        # 6. İş Akışları ve Araçlar (⚙️/🎨)
        menu_tools = self.menu_bar.addMenu("⚙️ İş Akışları & Araçlar")
        self.add_menu_action(menu_tools, "NEB Master İş Akışı", 3)
        self.add_menu_action(menu_tools, "NEB Enerji Bariyeri (Energy Profile)", 11)
        self.add_menu_action(menu_tools, "Master Grafik Birleştirici (Origin Klonu)", 22)
        self.add_menu_action(menu_tools, "Makale Paneli (Görsel Birleştirici)", 12)
        self.add_menu_action(menu_tools, "🧰 Harici Araçlar (.exe Başlatıcı)", 36)

    def add_menu_action(self, menu, name, index):
        action = QAction(name, self)
        action.triggered.connect(lambda checked, idx=index: self.display_module(idx))
        menu.addAction(action)

    def toggle_settings_dock(self):
        if self.settings_dock.isVisible():
            self.settings_dock.hide()
        else:
            self.settings_dock.show()

    def display_module(self, index):
        if index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)
            
    def update_local_settings(self, index):
        current_module = self.stacked_widget.widget(index)
        if hasattr(current_module, "get_local_settings_widget"):
            local_widget = current_module.get_local_settings_widget()
            self.settings_widget.set_local_widget(local_widget)
        else:
            self.settings_widget.set_local_widget(None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
