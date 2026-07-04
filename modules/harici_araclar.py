import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt

class HariciAraclarWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_title = QLabel("🧰 Harici Masaüstü Araçları")
        lbl_title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 20px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_desc = QLabel("Masaüstünüzde bulunan derlenmiş (.exe) programları buradan tek tıklamayla başlatabilirsiniz.")
        lbl_desc.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 30px;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(lbl_title)
        main_layout.addWidget(lbl_desc)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # Uygulama listesi (Masaüstü dizini baz alınarak)
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        
        apps = [
            ("Moleküler Weight", os.path.join(desktop_path, "Moleküler weight.exe"), "#3498db"),
            ("Elastic Analysis", os.path.join(desktop_path, "elastic.exe"), "#9b59b6"),
            ("Oksidasyon", os.path.join(desktop_path, "oksidasyon.exe"), "#e67e22")
        ]
        
        row = 0
        col = 0
        for name, exe_path, color in apps:
            btn = QPushButton(f"🚀 {name} Başlat")
            btn.setFixedSize(250, 80)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    background-color: #2c3e50;
                }}
            """)
            btn.clicked.connect(lambda checked, p=exe_path: self.launch_app(p))
            grid.addWidget(btn, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1
                
        main_layout.addLayout(grid)
        self.create_local_settings_widget()

    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        layout.addWidget(QLabel("Bu modül harici (.exe) programları başlatır.\nAyarlar harici programın içinden yapılır."))
        
    def get_local_settings_widget(self):
        return self.local_widget

    def launch_app(self, exe_path):
        if os.path.exists(exe_path):
            try:
                # Subprocess ile arka planda uygulamayı başlat
                subprocess.Popen([exe_path], shell=True)
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Program başlatılamadı:\n{e}")
        else:
            QMessageBox.warning(self, "Bulunamadı", f"Uygulama bulunamadı:\n{exe_path}\nLütfen silinmediğinden emin olun.")
