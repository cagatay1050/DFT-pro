from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QGroupBox, 
    QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QPushButton, QScrollArea, QLineEdit,
    QTabWidget
)
from PyQt6.QtCore import Qt
from utils.style_manager import current_settings, notifier

class GlobalSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.load_current_settings()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # --- TAB 1: Global Settings ---
        self.global_tab = QWidget()
        self.tabs.addTab(self.global_tab, "Evrensel Ayarlar")
        
        global_scroll = QScrollArea()
        global_scroll.setWidgetResizable(True)
        global_content = QWidget()
        self.layout = QVBoxLayout(global_content)
        
        # --- TAB 2: Local Settings ---
        self.local_tab = QWidget()
        self.tabs.addTab(self.local_tab, "Aktif Grafik Ayarları")
        self.local_layout = QVBoxLayout(self.local_tab)
        
        # Placeholder for local tab
        self.current_local_widget = None
        
        # 1. Çözünürlük ve Boyut (Adding to global tab)
        grp1 = QGroupBox("1. Çözünürlük ve Boyut")
        lyt1 = QFormLayout()
        self.dpi = QSpinBox()
        self.dpi.setRange(72, 600)
        self.dpi.setSingleStep(50)
        self.save_dpi = QSpinBox()
        self.save_dpi.setRange(300, 1200)
        self.save_dpi.setSingleStep(100)
        self.fig_width = QDoubleSpinBox()
        self.fig_width.setRange(1.0, 20.0)
        self.fig_width.setSingleStep(0.5)
        self.fig_height = QDoubleSpinBox()
        self.fig_height.setRange(1.0, 20.0)
        self.fig_height.setSingleStep(0.5)
        lyt1.addRow("Ekran DPI:", self.dpi)
        lyt1.addRow("Kayıt DPI (Makale):", self.save_dpi)
        lyt1.addRow("Genişlik (inch):", self.fig_width)
        lyt1.addRow("Yükseklik (inch):", self.fig_height)
        grp1.setLayout(lyt1)
        self.layout.addWidget(grp1)
        
        # 2. Font ve Yazı Tipleri
        grp2 = QGroupBox("2. Font ve Yazı Tipleri")
        lyt2 = QFormLayout()
        self.font_family = QComboBox()
        self.font_family.addItems(["Arial", "Helvetica", "Times New Roman", "DejaVu Sans"])
        self.font_base = QSpinBox()
        self.font_title = QSpinBox()
        self.font_label = QSpinBox()
        self.font_tick = QSpinBox()
        for sp in [self.font_base, self.font_title, self.font_label, self.font_tick]:
            sp.setRange(6, 40)
        lyt2.addRow("Yazı Tipi (Font):", self.font_family)
        lyt2.addRow("Ana Punto:", self.font_base)
        lyt2.addRow("Başlık Puntosu:", self.font_title)
        lyt2.addRow("Eksen (X/Y) Puntosu:", self.font_label)
        lyt2.addRow("Rakam (Tick) Puntosu:", self.font_tick)
        grp2.setLayout(lyt2)
        self.layout.addWidget(grp2)
        
        # 3. Eksen ve Çizgiler
        grp3 = QGroupBox("3. Eksen (Spines) ve Veri Çizgileri")
        lyt3 = QFormLayout()
        self.axes_width = QDoubleSpinBox()
        self.axes_width.setSingleStep(0.2)
        self.line_width = QDoubleSpinBox()
        self.line_width.setSingleStep(0.2)
        self.cmap = QComboBox()
        self.cmap.addItems(["tab10", "Set1", "viridis", "plasma", "Dark2"])
        lyt3.addRow("Eksen Çerçeve Kalınlığı:", self.axes_width)
        lyt3.addRow("Veri Çizgisi Kalınlığı:", self.line_width)
        lyt3.addRow("Veri Renk Paleti:", self.cmap)
        grp3.setLayout(lyt3)
        self.layout.addWidget(grp3)
        
        # 4. Tick (Çentik) Ayarları
        grp4 = QGroupBox("4. Tick (Çentik) Ayarları")
        lyt4 = QFormLayout()
        self.tick_dir = QComboBox()
        self.tick_dir.addItems(["in", "out", "inout"])
        self.maj_tick_len = QDoubleSpinBox()
        self.maj_tick_wid = QDoubleSpinBox()
        self.minor_ticks = QCheckBox("Minor (Ara) Tickleri Aktifleştir")
        self.min_tick_len = QDoubleSpinBox()
        self.min_tick_wid = QDoubleSpinBox()
        self.top_right_ticks = QCheckBox("Üst ve Sağ Eksenlere de Tick Ekle")
        lyt4.addRow("Tick Yönü:", self.tick_dir)
        lyt4.addRow("Major Uzunluk:", self.maj_tick_len)
        lyt4.addRow("Major Kalınlık:", self.maj_tick_wid)
        lyt4.addRow("", self.minor_ticks)
        lyt4.addRow("Minor Uzunluk:", self.min_tick_len)
        lyt4.addRow("Minor Kalınlık:", self.min_tick_wid)
        lyt4.addRow("", self.top_right_ticks)
        grp4.setLayout(lyt4)
        self.layout.addWidget(grp4)
        
        # 5. Izgara ve Lejant
        grp5 = QGroupBox("5. Izgara (Grid) ve Lejant")
        lyt5 = QFormLayout()
        self.grid = QCheckBox("Arka Plan Izgarası")
        self.legend_frame = QCheckBox("Lejant Çerçevesi Çiz")
        lyt5.addRow("", self.grid)
        lyt5.addRow("", self.legend_frame)
        grp5.setLayout(lyt5)
        self.layout.addWidget(grp5)
        

        # 6. Gelişmiş Grafikler (Koyu Mod ve Metin)
        grp6 = QGroupBox("6. Koyu Mod ve Özel Metin")
        lyt6 = QFormLayout()
        
        self.dark_mode = QCheckBox("Koyu Mod (Dark Mode)")
        self.custom_text = QLineEdit()
        self.custom_text.setPlaceholderText("Örn: Band Gap = 1.2 eV")
        
        self.txt_x = QDoubleSpinBox()
        self.txt_x.setRange(-2.0, 3.0)
        self.txt_x.setSingleStep(0.05)
        
        self.txt_y = QDoubleSpinBox()
        self.txt_y.setRange(-2.0, 3.0)
        self.txt_y.setSingleStep(0.05)
        
        self.txt_size = QSpinBox()
        self.txt_size.setRange(6, 40)
        
        lyt6.addRow("", self.dark_mode)
        lyt6.addRow("Özel Metin:", self.custom_text)
        lyt6.addRow("Metin X Konumu:", self.txt_x)
        lyt6.addRow("Metin Y Konumu:", self.txt_y)
        lyt6.addRow("Metin Büyüklüğü:", self.txt_size)
        grp6.setLayout(lyt6)
        self.layout.addWidget(grp6)
        
        # 7. Sınırlar ve Lejant Konumu
        grp7 = QGroupBox("7. Gelişmiş Lejant ve Eksen Sınırları")
        lyt7 = QFormLayout()
        
        self.show_legend = QCheckBox("Lejantı Göster")
        self.leg_x = QDoubleSpinBox()
        self.leg_x.setRange(-2.0, 3.0)
        self.leg_x.setSingleStep(0.05)
        
        self.leg_y = QDoubleSpinBox()
        self.leg_y.setRange(-2.0, 3.0)
        self.leg_y.setSingleStep(0.05)
        
        self.leg_size = QSpinBox()
        self.leg_size.setRange(6, 40)
        
        self.use_custom_x = QCheckBox("Özel X Sınırı")
        self.x_min = QDoubleSpinBox()
        self.x_min.setRange(-9999, 9999)
        self.x_max = QDoubleSpinBox()
        self.x_max.setRange(-9999, 9999)
        self.x_step = QDoubleSpinBox()
        self.x_step.setRange(0.01, 1000)
        
        self.use_custom_y = QCheckBox("Özel Y Sınırı")
        self.y_min = QDoubleSpinBox()
        self.y_min.setRange(-9999, 9999)
        self.y_max = QDoubleSpinBox()
        self.y_max.setRange(-9999, 9999)
        self.y_step = QDoubleSpinBox()
        self.y_step.setRange(0.01, 1000)
        
        lyt7.addRow("", self.show_legend)
        lyt7.addRow("Lejant X Konumu:", self.leg_x)
        lyt7.addRow("Lejant Y Konumu:", self.leg_y)
        lyt7.addRow("Lejant Büyüklüğü:", self.leg_size)
        
        lyt7.addRow("", self.use_custom_x)
        lyt7.addRow("X Min:", self.x_min)
        lyt7.addRow("X Max:", self.x_max)
        lyt7.addRow("X Adım:", self.x_step)
        
        lyt7.addRow("", self.use_custom_y)
        lyt7.addRow("Y Min:", self.y_min)
        lyt7.addRow("Y Max:", self.y_max)
        lyt7.addRow("Y Adım:", self.y_step)
        
        grp7.setLayout(lyt7)
        self.layout.addWidget(grp7)
        
        # Uygula Butonu
        self.btn_apply = QPushButton("Evrensel Ayarları Uygula")
        self.btn_apply.setStyleSheet("background-color: #0078d7; color: white; font-weight: bold; padding: 10px;")
        self.btn_apply.clicked.connect(self.save_and_apply)
        self.layout.addWidget(self.btn_apply)
        
        self.layout.addStretch()
        global_scroll.setWidget(global_content)
        
        g_layout = QVBoxLayout(self.global_tab)
        g_layout.addWidget(global_scroll)

    def set_local_widget(self, widget):
        """Replaces the content of the local settings tab with the new widget."""
        if self.current_local_widget is not None:
            self.local_layout.removeWidget(self.current_local_widget)
            self.current_local_widget.setParent(None)
            
        if widget is not None:
            self.local_layout.addWidget(widget)
            self.current_local_widget = widget
        else:
            self.current_local_widget = None

    def load_current_settings(self):
        s = current_settings
        self.dpi.setValue(s["dpi"])
        self.save_dpi.setValue(s["save_dpi"])
        self.fig_width.setValue(s["fig_width"])
        self.fig_height.setValue(s["fig_height"])
        
        self.font_family.setCurrentText(s["font_family"])
        self.font_base.setValue(s["font_base"])
        self.font_title.setValue(s["font_title"])
        self.font_label.setValue(s["font_label"])
        self.font_tick.setValue(s["font_tick"])
        
        self.axes_width.setValue(s["axes_width"])
        self.line_width.setValue(s["line_width"])
        self.cmap.setCurrentText(s["cmap"])
        
        self.tick_dir.setCurrentText(s["tick_dir"])
        self.maj_tick_len.setValue(s["maj_tick_len"])
        self.maj_tick_wid.setValue(s["maj_tick_wid"])
        self.minor_ticks.setChecked(s["minor_ticks"])
        self.min_tick_len.setValue(s["min_tick_len"])
        self.min_tick_wid.setValue(s["min_tick_wid"])
        self.top_right_ticks.setChecked(s["top_right_ticks"])
        
        self.grid.setChecked(s["grid"])
        self.legend_frame.setChecked(s["legend_frame"])
        
        self.dark_mode.setChecked(s.get("dark_mode", False))
        self.custom_text.setText(s.get("custom_text", ""))
        self.txt_x.setValue(s.get("txt_x", 0.5))
        self.txt_y.setValue(s.get("txt_y", 0.9))
        self.txt_size.setValue(s.get("txt_size", 16))
        
        self.show_legend.setChecked(s.get("show_legend", True))
        self.leg_x.setValue(s.get("leg_x", 1.0))
        self.leg_y.setValue(s.get("leg_y", 1.0))
        self.leg_size.setValue(s.get("leg_size", 14))
        
        self.use_custom_x.setChecked(s.get("use_custom_x", False))
        self.x_min.setValue(s.get("x_min", 0.0))
        self.x_max.setValue(s.get("x_max", 10.0))
        self.x_step.setValue(s.get("x_step", 1.0))
        
        self.use_custom_y.setChecked(s.get("use_custom_y", False))
        self.y_min.setValue(s.get("y_min", -5.0))
        self.y_max.setValue(s.get("y_max", 5.0))
        self.y_step.setValue(s.get("y_step", 1.0))

    def save_and_apply(self):
        s = current_settings
        s["dpi"] = self.dpi.value()
        s["save_dpi"] = self.save_dpi.value()
        s["fig_width"] = self.fig_width.value()
        s["fig_height"] = self.fig_height.value()
        
        s["font_family"] = self.font_family.currentText()
        s["font_base"] = self.font_base.value()
        s["font_title"] = self.font_title.value()
        s["font_label"] = self.font_label.value()
        s["font_tick"] = self.font_tick.value()
        
        s["axes_width"] = self.axes_width.value()
        s["line_width"] = self.line_width.value()
        s["cmap"] = self.cmap.currentText()
        
        s["tick_dir"] = self.tick_dir.currentText()
        s["maj_tick_len"] = self.maj_tick_len.value()
        s["maj_tick_wid"] = self.maj_tick_wid.value()
        s["minor_ticks"] = self.minor_ticks.isChecked()
        s["min_tick_len"] = self.min_tick_len.value()
        s["min_tick_wid"] = self.min_tick_wid.value()
        s["top_right_ticks"] = self.top_right_ticks.isChecked()
        
        s["grid"] = self.grid.isChecked()
        s["legend_frame"] = self.legend_frame.isChecked()
        
        s["dark_mode"] = self.dark_mode.isChecked()
        s["custom_text"] = self.custom_text.text()
        s["txt_x"] = self.txt_x.value()
        s["txt_y"] = self.txt_y.value()
        s["txt_size"] = self.txt_size.value()
        
        s["show_legend"] = self.show_legend.isChecked()
        s["leg_x"] = self.leg_x.value()
        s["leg_y"] = self.leg_y.value()
        s["leg_size"] = self.leg_size.value()
        
        s["use_custom_x"] = self.use_custom_x.isChecked()
        s["x_min"] = self.x_min.value()
        s["x_max"] = self.x_max.value()
        s["x_step"] = self.x_step.value()
        
        s["use_custom_y"] = self.use_custom_y.isChecked()
        s["y_min"] = self.y_min.value()
        s["y_max"] = self.y_max.value()
        s["y_step"] = self.y_step.value()
        
        # Yayını gönder: Grafiklerin yeniden çizilmesini tetikler
        notifier.style_changed.emit()
