import pandas as pd
import itertools
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFormLayout, QGroupBox, QMessageBox, QSpinBox,
    QScrollArea, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt

try:
    from pymatgen.core import Element, Composition
    PYMATGEN_AVAILABLE = True
except ImportError:
    PYMATGEN_AVAILABLE = False

from utils.style_manager import apply_global_style, notifier

class HidrurAdayJeneratoruWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # Sol Panel (Kontrol Paneli)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(400)
        
        input_group = QGroupBox("Girdi Parametreleri")
        i_layout = QFormLayout()
        
        self.le_elements = QLineEdit("Mg, Ti, H")
        self.le_elements.setToolTip("Aralarına virgül koyarak elementleri yazın (Örn: Mg, Ti, H). 'H' zorunludur.")
        i_layout.addRow("Element Sistemi:", self.le_elements)
        
        self.sb_max_cat = QSpinBox()
        self.sb_max_cat.setRange(1, 20)
        self.sb_max_cat.setValue(10)
        i_layout.addRow("Maks. Katyon Katsayısı:", self.sb_max_cat)
        
        self.sb_max_h = QSpinBox()
        self.sb_max_h.setRange(1, 100)
        self.sb_max_h.setValue(25)
        i_layout.addRow("Maks. Hidrojen Katsayısı:", self.sb_max_h)
        
        input_group.setLayout(i_layout)
        
        self.btn_calc = QPushButton("Teorik Adayları Hesapla")
        self.btn_calc.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; padding: 10px;")
        self.btn_calc.clicked.connect(self.hesapla)
        
        self.btn_export = QPushButton("Sonuçları Excel/CSV İndir")
        self.btn_export.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.btn_export.clicked.connect(self.export_csv)
        self.btn_export.setEnabled(False)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setPlaceholderText("Hesaplama ve veritabanı günlüğü burada görünecek...")
        
        left_layout.addWidget(input_group)
        left_layout.addWidget(self.btn_calc)
        left_layout.addWidget(self.btn_export)
        left_layout.addWidget(QLabel("<b>İşlem Günlüğü:</b>"))
        left_layout.addWidget(self.log_text)
        left_layout.addStretch()
        
        # Sağ Panel (Sonuç Tablosu)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.lbl_status = QLabel("Henüz hesaplama yapılmadı.")
        self.lbl_status.setStyleSheet("font-size: 14px; color: #555;")
        right_layout.addWidget(self.lbl_status)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Bileşik Formülü", "Gravimetrik Kapasite (wt. % H)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.table)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.df_results = None
        self.create_local_settings_widget()
        notifier.style_changed.connect(self.on_style_changed)
        
    def create_local_settings_widget(self):
        self.local_widget = QWidget()
        layout = QVBoxLayout(self.local_widget)
        
        lbl = QLabel("Bu modül tablo çıktısı verir. Grafiksel estetik ayarı bulunmamaktadır.")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)
        layout.addStretch()

    def get_local_settings_widget(self):
        return self.local_widget
        
    def on_style_changed(self):
        pass
        
    def hesapla(self):
        if not PYMATGEN_AVAILABLE:
            QMessageBox.critical(self, "Kütüphane Eksik", "Bu modül 'pymatgen' kütüphanesini gerektirir.\nLütfen terminalden 'pip install pymatgen' komutunu çalıştırın.")
            return
            
        input_str = self.le_elements.text()
        all_elements = sorted(list(set([e.strip().capitalize() for e in input_str.split(',') if e.strip()])))
        
        if 'H' not in all_elements:
            QMessageBox.warning(self, "Hata", "Sisteme mutlaka 'H' (Hidrojen) elementini dahil etmelisiniz.")
            return
        if not (2 <= len(all_elements) <= 5):
            QMessageBox.warning(self, "Hata", f"'H' dahil 2 ile 5 arası element girilmelidir. Siz {len(all_elements)} adet girdiniz.")
            return
            
        self.log_text.clear()
        self.log_text.append(f"Tarama başlıyor: {'-'.join(all_elements)} sistemi...")
        
        found_set, log_messages = self.find_candidate_hydrides_dynamic(
            all_elements, 
            max_cation_stoch=self.sb_max_cat.value(), 
            max_H_stoch=self.sb_max_h.value()
        )
        
        for msg in log_messages:
            self.log_text.append(msg)
            
        if found_set:
            self.lbl_status.setText(f"Tarama Tamamlandı! Yük denkliği sağlanan toplam {len(found_set)} benzersiz formül bulundu.")
            self.lbl_status.setStyleSheet("font-size: 14px; color: #27ae60; font-weight: bold;")
            
            df = pd.DataFrame(list(found_set), columns=["Bileşik Formülü", "Gravimetrik Kapasite (wt. % H)"])
            df = df.sort_values(by="Gravimetrik Kapasite (wt. % H)", ascending=False).reset_index(drop=True)
            self.df_results = df
            
            self.table.setRowCount(len(df))
            for i, row in df.iterrows():
                item_formula = QTableWidgetItem(row["Bileşik Formülü"])
                item_formula.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                item_cap = QTableWidgetItem(f"{row['Gravimetrik Kapasite (wt. % H)']:.3f} %")
                item_cap.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                self.table.setItem(i, 0, item_formula)
                self.table.setItem(i, 1, item_cap)
                
            self.btn_export.setEnabled(True)
        else:
            self.lbl_status.setText("Bu parametrelerde uygun bir hidrür formülü bulunamadı.")
            self.lbl_status.setStyleSheet("font-size: 14px; color: #c0392b; font-weight: bold;")
            self.table.setRowCount(0)
            self.btn_export.setEnabled(False)

    def find_candidate_hydrides_dynamic(self, element_symbols, max_cation_stoch=10, max_H_stoch=25):
        log_messages = []
        cation_symbols = [sym for sym in element_symbols if sym != 'H']
        h_charge = -1
        
        MANUAL_OXIDATION_STATES = {
            'Mg': [2], 'Na': [1], 'K': [1], 'Li': [1]
        }
        
        cation_data = []
        for sym in cation_symbols:
            if sym in MANUAL_OXIDATION_STATES:
                states = MANUAL_OXIDATION_STATES[sym]
                log_messages.append(f"(Manuel ayar kullanılıyor: {sym} -> {states})")
            else:
                try:
                    element = Element(sym)
                    states = [s for s in element.oxidation_states if s > 0]
                    log_messages.append(f"(Pymatgen varsayılanı kullanılıyor: {sym} -> {states})")
                except ValueError:
                    states = []
                    
            if not states:
                log_messages.append(f"Uyarı: {sym} için pozitif oksidasyon durumu bulunamadı, atlanıyor.")
                continue
            cation_data.append({'symbol': sym, 'states': states})
        
        if len(cation_data) != len(cation_symbols):
            log_messages.append("Bazı katyonlar için veri bulunamadı. Bu sistem atlanıyor.")
            return set(), log_messages

        stoch_range = range(1, max_cation_stoch + 1)
        stoch_combinations = list(itertools.product(stoch_range, repeat=len(cation_data)))
        
        state_lists = [c['states'] for c in cation_data]
        state_comb_list = list(itertools.product(*state_lists))
        
        found_candidates = set() 
        
        for stochs in stoch_combinations: 
            for states in state_comb_list:
                total_positive_charge = sum(stochs[i] * states[i] for i in range(len(stochs)))
                
                if total_positive_charge % abs(h_charge) != 0: continue 
                z = total_positive_charge // abs(h_charge)
                
                if 0 < z <= max_H_stoch:
                    all_stochs = list(stochs) + [z]
                    common_divisor = all_stochs[0]
                    for s in all_stochs[1:]:
                        common_divisor = math.gcd(common_divisor, s)
                    
                    formula_parts = []
                    for i in range(len(cation_data)):
                        symbol = cation_data[i]['symbol']
                        simplified_stoch = stochs[i] // common_divisor
                        formula_parts.append(f"{symbol}{simplified_stoch if simplified_stoch > 1 else ''}")
                    
                    simplified_z = z // common_divisor
                    formula_parts.append(f"H{simplified_z if simplified_z > 1 else ''}")
                    
                    final_formula = "".join(formula_parts)
                    
                    try:
                        comp = Composition(final_formula)
                        grav_capacity = comp.get_wt_fraction('H') * 100
                    except Exception:
                        grav_capacity = 0.0
                    
                    found_candidates.add((final_formula, grav_capacity))

        if not found_candidates:
            log_messages.append("Bu sistemde aday bulunamadı.")
        
        return found_candidates, log_messages
        
    def export_csv(self):
        if self.df_results is not None:
            save_path, _ = QFileDialog.getSaveFileName(self, "Sonuçları Kaydet", "candidates.csv", "CSV Files (*.csv)")
            if save_path:
                try:
                    self.df_results.to_csv(save_path, index=False)
                    QMessageBox.information(self, "Başarılı", f"Dosya başarıyla kaydedildi:\n{save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Kaydetme hatası:\n{e}")
