import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QSlider, QGroupBox, QFormLayout, QScrollArea, QComboBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage

class GorselIyilestiriciWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.img_path = None
        self.original_img = None
        self.enhanced_img = None
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # LEFT PANEL
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(300)
        
        # 1. File Upload
        grp_file = QGroupBox("1. Görsel Yükle (Düşük Kalite)")
        v_file = QVBoxLayout()
        self.btn_load = QPushButton("📂 Resim Seç (PNG/JPG)")
        self.btn_load.setStyleSheet("background-color: #3498db; color: white; padding: 10px; font-weight: bold;")
        self.btn_load.clicked.connect(self.load_image)
        self.lbl_file = QLabel("Yüklü: Yok\nBoyut: -")
        self.lbl_file.setWordWrap(True)
        v_file.addWidget(self.btn_load)
        v_file.addWidget(self.lbl_file)
        grp_file.setLayout(v_file)
        left_layout.addWidget(grp_file)
        
        # 2. Enhancement Settings
        grp_settings = QGroupBox("2. İyileştirme Ayarları")
        f_settings = QFormLayout()
        
        self.cmb_scale = QComboBox()
        self.cmb_scale.addItems(["2x Büyüt", "3x Büyüt", "4x Büyüt", "6x Büyüt", "8x Büyüt"])
        self.cmb_scale.setCurrentIndex(0)
        
        self.chk_denoise = QCheckBox("Gürültü Temizle (Denoise)")
        self.chk_denoise.setChecked(True)
        self.chk_denoise.setToolTip("Özellikle JPEG veya ekran görüntüsü bozulmalarını temizler. Biraz yavaşlatabilir.")
        
        self.sld_sharp = QSlider(Qt.Orientation.Horizontal)
        self.sld_sharp.setRange(0, 30) # 0 to 3.0 scale
        self.sld_sharp.setValue(15) # Default 1.5
        
        f_settings.addRow("Büyütme Katsayısı:", self.cmb_scale)
        f_settings.addRow("", self.chk_denoise)
        f_settings.addRow("Keskinlik Artırımı:", self.sld_sharp)
        grp_settings.setLayout(f_settings)
        left_layout.addWidget(grp_settings)
        
        # Process Button
        self.btn_process = QPushButton("✨ Görüntüyü İyileştir")
        self.btn_process.setStyleSheet("background-color: #9b59b6; color: white; padding: 12px; font-weight: bold; font-size: 14px;")
        self.btn_process.clicked.connect(self.process_image)
        left_layout.addWidget(self.btn_process)
        
        # Save Button
        self.btn_save = QPushButton("💾 Yüksek Kaliteyi Kaydet")
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; font-weight: bold; font-size: 14px;")
        self.btn_save.clicked.connect(self.save_image)
        left_layout.addWidget(self.btn_save)
        
        left_layout.addStretch()
        
        # RIGHT PANEL: Display (Side-by-side)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        lbl_title = QLabel("Önizleme (Orijinal vs İyileştirilmiş)")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(lbl_title)
        
        display_layout = QHBoxLayout()
        
        # Left side: Original
        v_orig = QVBoxLayout()
        self.lbl_orig_title = QLabel("Orijinal Görüntü")
        self.lbl_orig_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_orig_img = QLabel()
        self.lbl_orig_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_orig_img.setStyleSheet("background-color: #eeeeee; border: 1px solid #cccccc;")
        
        scroll_orig = QScrollArea()
        scroll_orig.setWidget(self.lbl_orig_img)
        scroll_orig.setWidgetResizable(True)
        v_orig.addWidget(self.lbl_orig_title)
        v_orig.addWidget(scroll_orig)
        
        # Right side: Enhanced
        v_enh = QVBoxLayout()
        self.lbl_enh_title = QLabel("İyileştirilmiş (Yüksek Kalite)")
        self.lbl_enh_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_enh_title.setStyleSheet("color: green; font-weight: bold;")
        self.lbl_enh_img = QLabel()
        self.lbl_enh_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_enh_img.setStyleSheet("background-color: #eeeeee; border: 1px solid #27ae60;")
        
        scroll_enh = QScrollArea()
        scroll_enh.setWidget(self.lbl_enh_img)
        scroll_enh.setWidgetResizable(True)
        v_enh.addWidget(self.lbl_enh_title)
        v_enh.addWidget(scroll_enh)
        
        display_layout.addLayout(v_orig)
        display_layout.addLayout(v_enh)
        right_layout.addLayout(display_layout)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, stretch=1)
        
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Resim Seç", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.img_path = file_path
            
            with open(file_path, "rb") as f:
                img_array = np.asarray(bytearray(f.read()), dtype=np.uint8)
                self.original_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
            if self.original_img is None:
                QMessageBox.warning(self, "Hata", "Dosya okunamadı veya geçerli bir resim değil.")
                return
                
            h, w, _ = self.original_img.shape
            self.lbl_file.setText(f"Yüklü: {os.path.basename(file_path)}\nBoyut: {w} x {h}")
            self.show_image(self.original_img, self.lbl_orig_img)
            
            # Clear enhanced
            self.enhanced_img = None
            self.lbl_enh_img.clear()
            self.lbl_enh_title.setText("İyileştirilmiş (Bekliyor...)")
            
    def show_image(self, cv_img, label):
        if cv_img is None: return
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
        label.setPixmap(QPixmap.fromImage(q_img))
        
    def process_image(self):
        if self.original_img is None:
            QMessageBox.warning(self, "Hata", "Önce iyileştirilecek görseli yükleyin.")
            return
            
        img = self.original_img.copy()
        
        self.btn_process.setText("⏳ İşleniyor...")
        self.btn_process.setEnabled(False)
        self.repaint() # Force UI update to show processing state
        
        # 1. Denoising
        if self.chk_denoise.isChecked():
            # Apply fastNlMeansDenoisingColored to remove compression artifacts
            img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
            
        # 2. Upscaling (Lanczos4 is excellent for sharp edges and complex structures)
        scale_txt = self.cmb_scale.currentText()
        scale = int(scale_txt[0]) # extracts '2', '3', '4', '6', '8'
        
        h, w = img.shape[:2]
        new_w, new_h = w * scale, h * scale
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # 3. Unsharp Masking
        sharp_val = self.sld_sharp.value() / 10.0 # 0.0 to 3.0
        if sharp_val > 0:
            # Gaussian blur radius depends on scale
            blur_k = scale * 2 + 1 if (scale * 2 + 1) % 2 != 0 else scale * 2 + 3
            blurred = cv2.GaussianBlur(img, (blur_k, blur_k), 0)
            
            # Unsharp mask formula: Original + (Original - Blurred) * Amount
            # cv2.addWeighted(src1, alpha, src2, beta, gamma) -> src1*alpha + src2*beta + gamma
            # We want: img + (img - blurred) * sharp_val = img * (1 + sharp_val) - blurred * sharp_val
            img = cv2.addWeighted(img, 1.0 + sharp_val, blurred, -sharp_val, 0)
            
        self.enhanced_img = img
        self.show_image(self.enhanced_img, self.lbl_enh_img)
        self.lbl_enh_title.setText(f"İyileştirilmiş ({new_w} x {new_h})")
        
        self.btn_process.setText("✨ Görüntüyü İyileştir")
        self.btn_process.setEnabled(True)
        
    def save_image(self):
        if self.enhanced_img is None:
            QMessageBox.warning(self, "Hata", "Önce görseli iyileştirin.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Yüksek Kaliteli Görseli Kaydet", "yuksek_kalite.png", "PNG Images (*.png);;JPEG Images (*.jpg)")
        if file_path:
            # Use OpenCV to save, but handle unicode paths
            # To handle unicode on Windows during write:
            ext = os.path.splitext(file_path)[1]
            success, encoded_img = cv2.imencode(ext, self.enhanced_img)
            if success:
                with open(file_path, "wb") as f:
                    encoded_img.tofile(f)
                QMessageBox.information(self, "Başarılı", f"İyileştirilmiş görsel başarıyla kaydedildi:\n{file_path}")
            else:
                QMessageBox.warning(self, "Hata", "Görsel kaydedilirken bir hata oluştu.")
