import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QLineEdit, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt
from utils.style_manager import notifier

class KristalYapiBulucuWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        # API Ayarları
        group_api = QGroupBox("Materials Project (API) Ayarları")
        api_layout = QHBoxLayout(group_api)
        
        self.le_api_key = QLineEdit()
        self.le_api_key.setPlaceholderText("Materials Project API Anahtarınızı Girin (Örn: J8x...)")
        self.le_api_key.setEchoMode(QLineEdit.EchoMode.PasswordEchoOnEdit)
        
        api_layout.addWidget(QLabel("API Key:"))
        api_layout.addWidget(self.le_api_key)
        
        # Üst Arama Çubuğu
        top_layout = QHBoxLayout()
        self.le_search = QLineEdit()
        self.le_search.setPlaceholderText("Kimyasal Formül Girin (Örn: Sr2ZnH6 veya BaTiO3)")
        self.le_search.setStyleSheet("font-size: 14px; padding: 5px;")
        
        self.btn_search = QPushButton("Veritabanında Ara")
        self.btn_search.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 8px;")
        self.btn_search.clicked.connect(self.search_db)
        
        top_layout.addWidget(self.le_search)
        top_layout.addWidget(self.btn_search)
        
        # Sonuç Tablosu
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Formül", "Uzay Grubu", "Kristal Sistemi", "a, b, c (Å)", "Birim Hücre Hacmi", "MP ID"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        main_layout.addWidget(group_api)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table)
        
        self.create_local_settings_widget()
        
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        layout.addWidget(QLabel("Bu modül grafik içermemektedir.\nGerçek veriler için geçerli bir\nMaterials Project API Key girmelisiniz."))
        
    def get_local_settings_widget(self):
        return self.local_widget
        
    def search_db(self):
        query = self.le_search.text().strip()
        api_key = self.le_api_key.text().strip()
        
        if not query:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir formül girin.")
            return
            
        self.table.setRowCount(0)
        
        if not api_key:
            # Fallback to dummy DB if no API key is provided
            QMessageBox.information(self, "Bilgi", "API Anahtarı girilmediği için yerel demo veritabanı kullanılıyor.")
            self.search_dummy(query)
            return
            
        # Actual API Call
        self.btn_search.setText("Aranıyor...")
        self.btn_search.setEnabled(False)
        QApplication.processEvents()
        
        try:
            from mp_api.client import MPRester
            
            with MPRester(api_key) as mpr:
                # Search materials by formula
                docs = mpr.materials.summary.search(formula=query, fields=["material_id", "formula_pretty", "symmetry", "structure", "volume"])
                
                if not docs:
                    QMessageBox.information(self, "Bilgi", f"Materials Project'te '{query}' için sonuç bulunamadı.")
                else:
                    self.table.setRowCount(len(docs))
                    for r_idx, doc in enumerate(docs):
                        formula = doc.formula_pretty
                        sg_symbol = doc.symmetry.symbol
                        sg_num = doc.symmetry.number
                        c_sys = doc.symmetry.crystal_system.name if doc.symmetry.crystal_system else "Bilinmiyor"
                        
                        a = doc.structure.lattice.a
                        b = doc.structure.lattice.b
                        c = doc.structure.lattice.c
                        abc_str = f"a={a:.2f}, b={b:.2f}, c={c:.2f}"
                        
                        vol = f"{doc.volume:.2f}"
                        mp_id = str(doc.material_id)
                        
                        row_data = [formula, f"{sg_symbol} ({sg_num})", c_sys, abc_str, vol, mp_id]
                        
                        for c_idx, cell_data in enumerate(row_data):
                            item = QTableWidgetItem(str(cell_data))
                            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                            self.table.setItem(r_idx, c_idx, item)
                            
        except ImportError:
            QMessageBox.critical(self, "Hata", "mp-api kütüphanesi bulunamadı. Lütfen 'pip install mp-api' komutu ile yükleyin.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"API sorgusu sırasında bir hata oluştu:\n{str(e)}\n\nAPI anahtarınızın doğru olduğundan emin olun.")
        finally:
            self.btn_search.setText("Veritabanında Ara")
            self.btn_search.setEnabled(True)

    def search_dummy(self, query):
        dummy_db = [
            ["Sr2ZnH6", "Fm-3m (225)", "Kübik", "a=b=c=6.54", "279.7", "Teorik (DFT)"],
            ["BaTiO3", "Pm-3m (221)", "Kübik", "a=b=c=4.00", "64.0", "mp-2998"],
            ["BaTiO3", "P4mm (99)", "Tetragonal", "a=b=3.99, c=4.03", "64.1", "mp-5986"],
            ["TiO2", "P4_2/mnm (136)", "Tetragonal", "a=b=4.59, c=2.96", "62.4", "mp-2657"],
            ["TiO2", "I4_1/amd (141)", "Tetragonal", "a=b=3.78, c=9.51", "136.2", "mp-390"],
            ["NaCl", "Fm-3m (225)", "Kübik", "a=b=c=5.64", "179.4", "mp-22862"]
        ]
        
        results = []
        for row in dummy_db:
            if query.lower() in row[0].lower():
                results.append(row)
                
        if not results:
            QMessageBox.information(self, "Bilgi", "Aranan formüle ait yerel sonuç bulunamadı.\nGerçek veriler için Materials Project API anahtarınızı girin.")
            return
            
        self.table.setRowCount(len(results))
        for r_idx, row_data in enumerate(results):
            for c_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r_idx, c_idx, item)
