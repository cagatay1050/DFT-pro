import math
import io
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QMessageBox, QSpinBox,
    QScrollArea, QCheckBox, QSlider, QListWidget, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from utils.style_manager import apply_global_style, notifier

class MakalePaneliWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)
        
        # Upload
        upload_group = QGroupBox("Görselleri Yükle")
        u_layout = QVBoxLayout()
        
        self.btn_upload = QPushButton("Görselleri Seç (Çoklu Seçim)")
        self.btn_upload.clicked.connect(self.load_images)
        u_layout.addWidget(self.btn_upload)
        
        self.list_images = QListWidget()
        self.list_images.setMaximumHeight(150)
        u_layout.addWidget(self.list_images)
        
        upload_group.setLayout(u_layout)
        
        # Settings
        settings_group = QGroupBox("Panel Ayarları")
        s_layout = QFormLayout()
        
        self.sb_cols = QSpinBox(); self.sb_cols.setRange(1, 10); self.sb_cols.setValue(2)
        self.sb_space = QSpinBox(); self.sb_space.setRange(0, 500); self.sb_space.setValue(100); self.sb_space.setSingleStep(20)
        
        s_layout.addRow("Sütun Sayısı:", self.sb_cols)
        s_layout.addRow("Görseller Arası Boşluk (px):", self.sb_space)
        
        self.cb_labels = QCheckBox("Sol Üste (a), (b) Etiketleri Ekle")
        self.cb_labels.setChecked(True)
        s_layout.addRow(self.cb_labels)
        
        self.sl_font = QSlider(Qt.Orientation.Horizontal)
        self.sl_font.setRange(1, 15)
        self.sl_font.setValue(6)
        s_layout.addRow("Etiket Boyutu (%):", self.sl_font)
        
        settings_group.setLayout(s_layout)
        
        self.btn_calc = QPushButton("Görselleri Birleştir ve Paneli Oluştur")
        self.btn_calc.setStyleSheet("background-color: #2e8b57; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.process_data)
        
        self.btn_download = QPushButton("Birleşik Paneli İndir (600 DPI)")
        self.btn_download.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold; padding: 10px;")
        self.btn_download.clicked.connect(self.download_image)
        self.btn_download.setEnabled(False)
        
        left_layout.addWidget(upload_group)
        left_layout.addWidget(settings_group)
        left_layout.addWidget(self.btn_calc)
        left_layout.addWidget(self.btn_download)
        left_layout.addStretch()
        
        # Right Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.lbl_preview = QLabel("Görsel Önizlemesi Burada Görüntülenecek")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setStyleSheet("background-color: #ffffff; border: 2px dashed #ccc;")
        
        scroll_area.setWidget(self.lbl_preview)
        right_layout.addWidget(scroll_area)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.image_paths = []
        self.final_canvas = None
        
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)
        
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        c_layout = QFormLayout(content)
        
        lbl = QLabel("Bu modül grafik üretmediği için yerel estetik ayarı yoktur. Ayarlar sol menüdedir.")
        lbl.setWordWrap(True)
        c_layout.addRow(lbl)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        pass
        
    def load_images(self):
        fnames, _ = QFileDialog.getOpenFileNames(self, 'Görselleri Seç', '', 'Images (*.png *.jpg *.jpeg)')
        if fnames:
            self.image_paths = fnames
            self.list_images.clear()
            for f in fnames:
                self.list_images.addItem(f.split('/')[-1])
                
    def process_data(self):
        if not self.image_paths:
            QMessageBox.warning(self, "Hata", "Lütfen birleştirmek için en az 1 görsel yükleyin!")
            return
            
        try:
            images = [Image.open(img).convert("RGB") for img in self.image_paths]
            col_sayisi = self.sb_cols.value()
            bosluk = self.sb_space.value()
            etiket_ekle = self.cb_labels.isChecked()
            etiket_boyutu = self.sl_font.value()
            
            satir_sayisi = math.ceil(len(images) / col_sayisi)
            
            max_w = max(img.width for img in images)
            max_h = max(img.height for img in images)
            
            canvas_w = (col_sayisi * max_w) + ((col_sayisi - 1) * bosluk)
            canvas_h = (satir_sayisi * max_h) + ((satir_sayisi - 1) * bosluk)
            
            canvas = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
            draw = ImageDraw.Draw(canvas)
            
            font_size = int(max_h * (etiket_boyutu / 100))
            try:
                font = ImageFont.truetype("timesbd.ttf", font_size)
            except IOError:
                try:
                    font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
                except IOError:
                    font = ImageFont.load_default()
                    
            for idx, img in enumerate(images):
                satir = idx // col_sayisi
                sutun = idx % col_sayisi
                
                x = sutun * (max_w + bosluk)
                y = satir * (max_h + bosluk)
                
                offset_x = x + (max_w - img.width) // 2
                offset_y = y + (max_h - img.height) // 2
                
                canvas.paste(img, (offset_x, offset_y))
                
                if etiket_ekle:
                    harf = chr(97 + idx)
                    etiket_metni = f"({harf})"
                    
                    text_x = x + int(max_w * 0.01)
                    text_y = y + int(max_h * 0.01)
                    
                    draw.text((text_x, text_y), etiket_metni, fill=(0, 0, 0), font=font)
                    
            self.final_canvas = canvas
            
            # Preview in UI
            buf = io.BytesIO()
            canvas.save(buf, format="PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(buf.getvalue())
            
            # Scale for preview if it's too big
            preview_w = min(pixmap.width(), 800)
            self.lbl_preview.setPixmap(pixmap.scaledToWidth(preview_w, Qt.TransformationMode.SmoothTransformation))
            self.lbl_preview.setStyleSheet("")
            
            self.btn_download.setEnabled(True)
            QMessageBox.information(self, "Başarılı", "Makale Paneli başarıyla oluşturuldu!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Görseller birleştirilirken bir hata oluştu:\n{e}")
            
    def download_image(self):
        if self.final_canvas:
            save_path, _ = QFileDialog.getSaveFileName(self, "Paneli Kaydet", "Article_Panel_600DPI.jpg", "JPEG Files (*.jpg *.jpeg)")
            if save_path:
                try:
                    self.final_canvas.save(save_path, format="JPEG", dpi=(600, 600), quality=95, subsampling=0)
                    QMessageBox.information(self, "Başarılı", f"Panel başarıyla kaydedildi:\n{save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Kaydetme hatası:\n{e}")
