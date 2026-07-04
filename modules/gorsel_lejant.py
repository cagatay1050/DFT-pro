import os
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QSlider, QGroupBox, QFormLayout, QScrollArea, QLineEdit, QMessageBox, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QFont, QPen

class GorselLejantWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.img_path = None
        self.original_img = None
        self.detected_groups = []
        self.legend_inputs = []
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # LEFT PANEL
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(350)
        
        # 1. File Upload
        grp_file = QGroupBox("1. Görsel Yükle (Ekran Görüntüsü)")
        v_file = QVBoxLayout()
        self.btn_load = QPushButton("📂 Resim Seç (PNG/JPG)")
        self.btn_load.setStyleSheet("background-color: #3498db; color: white; padding: 10px; font-weight: bold;")
        self.btn_load.clicked.connect(self.load_image)
        self.lbl_file = QLabel("Yüklü: Yok")
        self.lbl_file.setWordWrap(True)
        v_file.addWidget(self.btn_load)
        v_file.addWidget(self.lbl_file)
        grp_file.setLayout(v_file)
        left_layout.addWidget(grp_file)
        
        # 2. Controls
        grp_controls = QGroupBox("2. Atom Tespiti (Yapay Görme)")
        v_controls = QVBoxLayout()
        
        lbl_k = QLabel("Farklı Atom Sayısı (Lejant Sayısı):")
        self.spn_k = QSpinBox()
        self.spn_k.setRange(1, 10)
        self.spn_k.setValue(3)
        self.spn_k.valueChanged.connect(self.detect_atoms)
        
        lbl_sens = QLabel("Çember Bulma Hassasiyeti:")
        self.sld_sens = QSlider(Qt.Orientation.Horizontal)
        self.sld_sens.setRange(10, 100)
        self.sld_sens.setValue(35)
        self.sld_sens.valueChanged.connect(self.detect_atoms)
        
        self.btn_detect = QPushButton("🔍 Atomları Bul ve Grupla")
        self.btn_detect.setStyleSheet("background-color: #f39c12; color: white; padding: 8px; font-weight: bold;")
        self.btn_detect.clicked.connect(self.detect_atoms)
        
        v_controls.addWidget(lbl_k)
        v_controls.addWidget(self.spn_k)
        v_controls.addWidget(lbl_sens)
        v_controls.addWidget(self.sld_sens)
        v_controls.addWidget(self.btn_detect)
        grp_controls.setLayout(v_controls)
        left_layout.addWidget(grp_controls)
        
        # 3. Dynamic Legend Panel
        grp_legend = QGroupBox("3. Tespit Edilen Atomlar (Büyükten Küçüğe)")
        v_legend = QVBoxLayout()
        
        self.scroll_legend = QScrollArea()
        self.scroll_legend.setWidgetResizable(True)
        self.legend_content = QWidget()
        self.legend_layout = QVBoxLayout(self.legend_content)
        self.legend_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_legend.setWidget(self.legend_content)
        
        v_legend.addWidget(self.scroll_legend)
        grp_legend.setLayout(v_legend)
        left_layout.addWidget(grp_legend)
        
        # 4. Save
        self.btn_save = QPushButton("💾 Lejantlı Görseli Kaydet")
        self.btn_save.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; font-weight: bold; font-size: 14px;")
        self.btn_save.clicked.connect(self.save_final_image)
        left_layout.addWidget(self.btn_save)
        
        # RIGHT PANEL: Display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.lbl_image = QLabel("Görsel burada görüntülenecek...")
        self.lbl_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_image.setStyleSheet("background-color: #f0f0f0; border: 2px dashed #cccccc;")
        
        scroll_img = QScrollArea()
        scroll_img.setWidget(self.lbl_image)
        scroll_img.setWidgetResizable(True)
        
        right_layout.addWidget(scroll_img)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, stretch=1)
        
    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Resim Seç", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.img_path = file_path
            self.lbl_file.setText(f"Yüklü: {os.path.basename(file_path)}")
            # Fix OpenCV unicode path issue on Windows
            with open(file_path, "rb") as f:
                img_array = np.asarray(bytearray(f.read()), dtype=np.uint8)
                self.original_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            self.show_image_cv(self.original_img)
            self.detect_atoms()
            
    def show_image_cv(self, cv_img):
        if cv_img is None: return
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
        self.lbl_image.setPixmap(QPixmap.fromImage(q_img))
        
    def detect_atoms(self):
        if self.original_img is None: return
        
        # Clear old layout
        for i in reversed(range(self.legend_layout.count())): 
            widget = self.legend_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        self.detected_groups = []
        self.legend_inputs = []
        
        img = self.original_img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 5)
        
        sens = self.sld_sens.value()
        k_clusters = self.spn_k.value()
        
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                                   param1=50, param2=sens, minRadius=5, maxRadius=300)
                                   
        display_img = img.copy()
        
        if circles is not None:
            circles = np.uint16(np.around(circles))[0, :]
            
            circle_data = [] # Store (x, y, r, color_b, color_g, color_r)
            
            for c in circles:
                x, y, r = c[0], c[1], c[2]
                
                # Draw on display image (just to show detection)
                cv2.circle(display_img, (x, y), r, (0, 255, 0), 2)
                
                try:
                    # Get center color (average of 5x5)
                    roi = img[max(0, y-2):y+3, max(0, x-2):x+3]
                    color = np.median(roi, axis=(0,1))
                    circle_data.append((x, y, r, color[0], color[1], color[2]))
                except Exception:
                    pass
                    
            if len(circle_data) >= k_clusters:
                # Use K-Means on COLORS to group them
                data_colors = np.array([[d[3], d[4], d[5]] for d in circle_data], dtype=np.float32)
                
                # K-Means criteria
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
                ret, labels, centers = cv2.kmeans(data_colors, k_clusters, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
                
                groups = {}
                for i, label in enumerate(labels.flatten()):
                    if label not in groups:
                        groups[label] = {'b': 0, 'g': 0, 'r_col': 0, 'r_total': 0, 'count': 0}
                    groups[label]['b'] += circle_data[i][3]
                    groups[label]['g'] += circle_data[i][4]
                    groups[label]['r_col'] += circle_data[i][5]
                    groups[label]['r_total'] += circle_data[i][2]
                    groups[label]['count'] += 1
                    
                for label, g in groups.items():
                    c = g['count']
                    self.detected_groups.append({
                        'b': int(g['b']/c),
                        'g': int(g['g']/c),
                        'r_col': int(g['r_col']/c),
                        'r': int(g['r_total']/c),
                        'count': c
                    })
            else:
                QMessageBox.warning(self, "Hata", f"Bulunan çember sayısı ({len(circle_data)}) istenen lejant sayısından ({k_clusters}) az. Hassasiyeti düşürün.")
                return
                    
        self.show_image_cv(display_img)
        
        if not self.detected_groups:
            QMessageBox.information(self, "Bulunamadı", "Bu görselde belirgin atom küreleri bulunamadı. Lütfen 'Hassasiyet' ayarını düşürüp tekrar deneyin.")
            return
            
        # Sort by radius descending
        self.detected_groups.sort(key=lambda x: x['r'], reverse=True)
        
        # Build UI
        for i, g in enumerate(self.detected_groups):
            row_w = QWidget()
            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(0,0,0,0)
            
            hex_color = f"#{g['r_col']:02x}{g['g']:02x}{g['b']:02x}"
            
            lbl_color = QLabel()
            lbl_color.setFixedSize(30, 30)
            lbl_color.setStyleSheet(f"background-color: {hex_color}; border-radius: 15px; border: 1px solid black;")
            
            lbl_info = QLabel(f"r: {g['r']}px ({g['count']} adet)")
            lbl_info.setFixedWidth(100)
            
            txt_desc = QLineEdit()
            txt_desc.setPlaceholderText("Atom adı (Örn: Ca)")
            
            row_l.addWidget(lbl_color)
            row_l.addWidget(lbl_info)
            row_l.addWidget(txt_desc)
            
            self.legend_layout.addWidget(row_w)
            self.legend_inputs.append((g, txt_desc))
            
    def save_final_image(self):
        if self.original_img is None or not self.detected_groups:
            QMessageBox.warning(self, "Hata", "Önce görsel yükleyin ve atomları tespit edin.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Görseli Kaydet", "kristal_lejantli.png", "PNG Images (*.png)")
        if not file_path: return
        
        img_h, img_w, _ = self.original_img.shape
        
        # Dynamic Scaling based on image height
        scale = max(1.0, img_h / 800.0)
        
        legend_w = int(max(300, img_w * 0.3)) # Legend width at least 30% of image width
        font_size = int(max(16, 24 * scale))
        circle_radius = int(max(20, 30 * scale))
        padding_y = int(60 * scale)
        padding_x = int(40 * scale)
        
        final_w = img_w + legend_w
        final_h = max(img_h, padding_y * 2 + len(self.detected_groups) * (circle_radius * 2 + padding_y))
        
        # Create white background
        final_img = np.ones((final_h, final_w, 3), dtype=np.uint8) * 255
        
        # Paste original image on the left, centered vertically if smaller
        y_offset_img = (final_h - img_h) // 2
        final_img[y_offset_img:y_offset_img+img_h, 0:img_w] = self.original_img
        
        rgb_img = cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB)
        q_img = QImage(rgb_img.data, final_w, final_h, final_w*3, QImage.Format.Format_RGB888).copy()
        
        painter = QPainter(q_img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        font = QFont("Arial", font_size)
        painter.setFont(font)
        
        # Center legend vertically
        total_legend_h = len(self.detected_groups) * (circle_radius * 2 + padding_y) - padding_y
        y_offset = (final_h - total_legend_h) // 2
        
        for g, txt_input in self.legend_inputs:
            desc = txt_input.text().strip()
            if not desc: continue
            
            color = QColor(g['r_col'], g['g'], g['b'])
            painter.setBrush(color)
            painter.setPen(QPen(Qt.GlobalColor.black, max(2, int(3*scale))))
            
            # Draw circle
            painter.drawEllipse(img_w + padding_x, y_offset, circle_radius*2, circle_radius*2)
            
            # Draw text aligned with circle center
            painter.setPen(QPen(Qt.GlobalColor.black, max(2, int(2*scale))))
            # Estimate text vertical center
            painter.drawText(img_w + padding_x + circle_radius*2 + padding_x, y_offset + circle_radius + (font_size//3), desc)
            
            y_offset += circle_radius*2 + padding_y
            
        painter.end()
        
        q_img.save(file_path)
        QMessageBox.information(self, "Başarılı", f"Lejantlı görsel başarıyla kaydedildi:\n{file_path}")
