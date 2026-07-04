from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser

class NEBMasterWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel("NEB Hesaplaması Adım Adım İş Akışı")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #0078d7;")
        layout.addWidget(lbl_title)
        
        text_browser = QTextBrowser()
        text_browser.setStyleSheet("font-size: 14px; background-color: #f9f9f9; padding: 10px;")
        
        content = """
        <h3>Bu liste, NEB hesaplaması için hollow yöntemidir.</h3>
        <ul>
            <li><b>1. Adım:</b> ilk olarak bulk yapımızı statik bir hesap ile tekrar optimize edelim.</li>
            <li><b>2. Adım:</b> Optimize olmuş yapıyı vaspkit ile "803" uygun yönlerden slab- katman- ve vakum yapacağız, katman için 3 veya 5, vakum için 15-20 A yeterli.</li>
            <li><b>3. Adım:</b> kararlı olan yüzeyi tespit edip ( slab hesabı için otomasyon kullanabilirsiniz ve sonuçlarıda slab_result ile incele.) bu yapıdan ilerleyeceğiz.</li>
            <li><b>4. Adım:</b> bu yapılardan modül 30 yardımı ile initial ve final yapılarını oluşturup bunları önce kaba optimize yapıp sonra tüm etkiler ile birlikte optimize yapılacak.</li>
            <li><b>5. Adım:</b> Sonra 5 veya 7 image ile NEB hesabı kurulacak. (nebmake.pl) veya ase kod yardımı ile (IDPP)</li>
            <li><b>6. Aşama:</b> Cartesian koordinatlı 1x3x1 süper hücre oluştur. Altı kilitle (F F F), üstü serbest bırak (T T T).</li>
            <li><b>7. Aşama:</b> Kaba Optimizasyon (Dipol KAPALI, PREC=Normal, EDIFFG=-0.05).</li>
            <li><b>8. Aşama:</b> Hassas Optimizasyon (Dipol AÇIK, PREC=Accurate, EDIFFG=-0.02, ISTART=1).</li>
            <li><b>9. Aşama:</b> VTST nebmake.pl ile imajları oluştur (00 ve 08 içine OUTCAR'ları koymayı unutma!).</li>
            <li><b>10. Aşama:</b> CI-NEB Koşusu (Çekirdek sayısı imaj sayısına tam bölünmeli).</li>
        </ul>
        """
        text_browser.setHtml(content)
        layout.addWidget(text_browser)
        
    def get_local_settings_widget(self):
        return None
