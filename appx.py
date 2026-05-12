# ==========================================
# 1. STANDART PYTHON KÜTÜPHANELERİ
# ==========================================
import os
import io
import re
import json
import math
import tempfile
import zipfile
import itertools
from itertools import combinations

# ==========================================
# 2. TEMEL VERİ BİLİMİ VE WEB ARAYÜZÜ
# ==========================================
import streamlit as st
import numpy as np
import pandas as pd
import requests
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# 3. GRAFİK VE GÖRSELLEŞTİRME (Matplotlib)
# ==========================================
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.ticker as ticker
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

# ==========================================
# 4. MATEMATİK, FİT VE İSTATİSTİK (SciPy)
# ==========================================
from scipy import stats
from scipy.integrate import trapezoid
from scipy.interpolate import Akima1DInterpolator
from scipy.optimize import curve_fit

# ==========================================
# 5. MALZEME BİLİMİ VE KİMYA (ASE & Pymatgen)
# ==========================================
from ase import Atom
from ase.io import read, write
from ase.constraints import FixAtoms
from ase.mep import NEB
from ase.geometry import find_mic

from pymatgen.core.periodic_table import Element
from pymatgen.core.composition import Composition
import plotly.graph_objects as go

# ==========================================
# AKADEMİK GRAFİK FONT AYARLARI (GLOBAL)
# ==========================================
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['mathtext.fontset'] = 'stix'

# ==========================================
# 🎨 UZMAN SEVİYE GLOBAL GRAFİK MOTORU (RC PARAMS)
# ==========================================
with st.sidebar.expander("🎨 Kapsamlı Grafik Ayarları (OriginLab TarzıZ)", expanded=False):
    st.markdown("Bu paneldeki ayarlar, uygulamadaki **tüm** modüllerin grafik çizim stilini anında ve evrensel olarak değiştirir.")
    
    # --- 1. SEKME: Çözünürlük ve Boyut ---
    st.markdown("**1. Çözünürlük ve Boyut**")
    c1, c2 = st.columns(2)
    with c1:
        g_dpi = st.number_input("Ekran DPI", min_value=72, max_value=600, value=150, step=50)
        g_save_dpi = st.number_input("Kayıt DPI (Makale)", min_value=300, max_value=1200, value=600, step=100)
    with c2:
        g_fig_width = st.number_input("Genişlik (inch)", value=8.0, step=0.5)
        g_fig_height = st.number_input("Yükseklik (inch)", value=5.0, step=0.5)

    # --- 2. SEKME: Font ve Yazı Tipleri ---
    st.markdown("**2. Font ve Yazı Tipleri**")
    g_font_family = st.selectbox("Yazı Tipi (Font)", ["Arial", "Helvetica", "Times New Roman", "DejaVu Sans"], index=0)
    c3, c4 = st.columns(2)
    with c3:
        g_font_base = st.number_input("Ana Punto", value=14, step=1)
        g_font_title = st.number_input("Başlık Puntosu", value=16, step=1)
    with c4:
        g_font_label = st.number_input("Eksen (X/Y) Puntosu", value=15, step=1)
        g_font_tick = st.number_input("Rakam (Tick) Puntosu", value=13, step=1)

    # --- 3. SEKME: Eksenler (Spines) ve Çizgiler ---
    st.markdown("**3. Eksen (Spines) ve Veri Çizgileri**")
    c5, c6 = st.columns(2)
    with c5:
        g_axes_width = st.number_input("Eksen Çerçeve Kalınlığı", value=2.0, step=0.2)
    with c6:
        g_line_width = st.number_input("Veri Çizgisi Kalınlığı", value=2.5, step=0.2)
    g_cmap = st.selectbox("Veri Renk Paleti", ["tab10", "Set1", "viridis", "plasma", "Dark2"], index=0)

    # --- 4. SEKME: Tick (Çentik) Ayarları ---
    st.markdown("**4. Tick (Çentik) Ayarları**")
    g_tick_dir = st.selectbox("Tick Yönü", ["in", "out", "inout"], index=0)
    
    st.markdown("*Major (Ana) Tickler*")
    c7, c8 = st.columns(2)
    with c7:
        g_maj_tick_len = st.number_input("Major Uzunluk", value=6.0, step=1.0)
    with c8:
        g_maj_tick_wid = st.number_input("Major Kalınlık", value=2.0, step=0.2)
        
    g_minor_ticks = st.checkbox("Minor (Ara) Tickleri Aktifleştir", value=True)
    c9, c10 = st.columns(2)
    with c9:
        g_min_tick_len = st.number_input("Minor Uzunluk", value=3.0, step=1.0)
    with c10:
        g_min_tick_wid = st.number_input("Minor Kalınlık", value=1.2, step=0.2)
        
    g_top_right_ticks = st.checkbox("Üst ve Sağ Eksenlere de Tick Ekle (Kutu Görünümü)", value=True)

    # --- 5. SEKME: Izgara (Grid) ve Lejant ---
    st.markdown("**5. Izgara (Grid) ve Lejant**")
    g_grid = st.checkbox("Arka Plan Izgarası", value=False)
    g_legend_frame = st.checkbox("Lejant Çerçevesi Çiz", value=False)

    # ==========================================
    # MATPLOTLIB GLOBAL (RCPARAMS) GÜNCELLEMESİ
    # ==========================================
    mpl.rcParams.update({
        "figure.figsize": (g_fig_width, g_fig_height),
        "figure.dpi": g_dpi,
        "savefig.dpi": g_save_dpi,
        "savefig.bbox": "tight",
        "font.family": "sans-serif" if g_font_family != "Times New Roman" else "serif",
        "font.sans-serif": [g_font_family],
        "font.serif": [g_font_family],
        "font.size": g_font_base,
        "axes.titlesize": g_font_title,
        "axes.labelsize": g_font_label,
        "xtick.labelsize": g_font_tick,
        "ytick.labelsize": g_font_tick,
        "legend.fontsize": g_font_base - 2,
        "axes.linewidth": g_axes_width,
        "lines.linewidth": g_line_width,
        "axes.prop_cycle": plt.cycler('color', plt.get_cmap(g_cmap).colors) if g_cmap in ['tab10', 'Set1', 'Dark2'] else plt.rcParams['axes.prop_cycle'],
        "xtick.direction": g_tick_dir,
        "ytick.direction": g_tick_dir,
        "xtick.major.size": g_maj_tick_len,
        "ytick.major.size": g_maj_tick_len,
        "xtick.major.width": g_maj_tick_wid,
        "ytick.major.width": g_maj_tick_wid,
        "xtick.minor.visible": g_minor_ticks,
        "ytick.minor.visible": g_minor_ticks,
        "xtick.minor.size": g_min_tick_len,
        "ytick.minor.size": g_min_tick_len,
        "xtick.minor.width": g_min_tick_wid,
        "ytick.minor.width": g_min_tick_wid,
        "xtick.top": g_top_right_ticks,
        "ytick.right": g_top_right_ticks,
        "axes.grid": g_grid,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
        "legend.frameon": g_legend_frame,
        "legend.edgecolor": "black",
        "legend.fancybox": False
    })

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Çağatay Yamçıçıer Modüller", layout="wide", page_icon="⚛️")

# (Buradan itibaren senin menü ve elif blokların eskisi gibi devam edecek...)
# --- YAN MENÜ (SIDEBAR) ---
st.sidebar.image("https://tr.wikipedia.org/wiki/Dosya:Osmaniye_Korkut_Ata_Üniversitesi.jpg", width=50)
st.sidebar.title(" Analiz Paneli")
st.sidebar.markdown("---")
# ==========================================
# 1. MENÜLERİ KATEGORİLERE AYIRMA (SÖZLÜK YAPISI)
# ==========================================
menuler = {
    "📊 Çizim ve Veri Analizi": [
        "🖼️ Makale Paneli (Görsel Birleştirici)",
        "🌟 Kapsamlı A-Sınıfı (Yelpaze & Arrhenius)",
        "🔥 Termodinamik (VDOS)",
        "🎵 Titreşim Spektrumu (VDoS)",
        "🎵 Titreşim Spektrumu(VDoS) Grafikli",
        "🎶 Fonon Band Yapısı",
        "⚡ Difüzyon (Arrhenius)",
        "📈 Kinetik (MSD & Difüzyon)",
        "⚛️ Yapısal Analiz (RDF)",
        "📍 Çoklu Sıcaklık RDF (Overlay)",
        "📉 Parçalanma Termodinamiği (T_des)",
        "⏱️ AIMD Kararlılık (Sıcaklık/Enerji)",
        "⏱️ AIMD Kararlılık (Sıcaklık/Enerji)- farklı format",
        "🌌 Elektronik Bant Yapısı (Band)",
        "📊 Yoğunluk Durumları (DOS/PDOS)",
        "⛰️ NEB Enerji Bariyeri (Energy Profile)",
        "📍 Çoklu Sıcaklık VDoS (Overlay)",
        "🧱 Elastik Özellikler ve Modüller",
    ],
    "🤖 Otonom NEB ve Difüzyon": [
        "📌 NEB Master İş Akışı",
        "🤖 Otonom NEB Yapı Oluşturucu",
        "🤖 Otonom NEB Yapı Oluşturucu-yüzey",
        "🤖 Otonom NEB Yapı Oluşturucu-hollow",
        "🛣️ NEB IDPP Rota Oluşturucu",
        "🔀 Yüzey Difüzyonu (FS Jeneratörü)",
        "🌌 Otonom Kütle İçi Difüzyon (Vacancy)",
        "🌌 Otonom Kütle İçi Difüzyon (Vacancy) CASTEP",
        "🌟 Otonom Arayer (Interstitial) Difüzyon"
    ],
    "⚙️ Giriş Dosyası Üreticileri (INCAR)": [
        "⚙️ INCAR & TRUBA Arşivi",
        "🎶 Fonon ve Phonopy (Otomasyon)",
        "🏃‍♂️ AIMD Çoklu Sıcaklık (Otomasyon)",
        "🧲 Elastik Sabitler (IBRION=6)",
        "💎 HSE06 Bant Yapısı (Otomasyon)",
        "🏗️ Geometri Optimizasyonu (INCAR)",
        "🔋 Statik Enerji / Referans (INCAR)",
        "🧫 Yüzey & Slab Otomasyonu (VASPKIT)",
        "🏗️ NEB IS/FS Optimizasyonu (2-Aşamalı)",
        "⛰️ CI-NEB Hesaplaması (INCAR)",
        "🌈 HSE06 Optik Özellikler (2-Aşamalı)"
    ],
    "🛠️ Yardımcı Araçlar ve Scriptler": [
        "✍️ Akademik Paraphrase (Yapay Zeka)",
        "🧪 Hidrür Aday Jeneratörü",
        "🔍 Yüzey Enerjisi Analizörü (Script)",
        "🧹 VASP CONTCAR Katlama ve Temizleme Modülü",
        "🎨 Master Grafik Birleştirici (Origin Klonu)",
        "🧪 Formasyon Enerjisi Hesaplama Modülü",
        "📈 Murnaghan EOS Fit (CASTEP)",
        "🔍 Kristal Yapı Bulucu",
        "🥞 2D RP Hidrit Bulucu",
        "⚡ Spin-Polarize Bant Yapısı"
    ]
}

# ==========================================
# 2. DİNAMİK AÇILIR MENÜ (SIDEBAR)
# ==========================================
st.sidebar.title("🧪 DFT Lab Dashboard")
st.sidebar.markdown("---")

# Kullanıcı önce "Ana Kategoriyi" seçer (Dropdown kutusu)
secili_kategori = st.sidebar.selectbox("📂 Ana Kategori Seçin:", list(menuler.keys()))

st.sidebar.markdown("---")

# Kod sadece seçilen kategoriye ait modülleri gösterir (Radio butonu)
secim = st.sidebar.radio(f"👉 Seçili Modül:", menuler[secili_kategori])

st.sidebar.markdown("---")
st.sidebar.info("Geliştirici: Çağatay Yamçıcıer")

st.sidebar.markdown("---")
st.sidebar.info("VASP Çıktı Analizörü v3.1")

# ==========================================
# MODÜL 1: İŞ AKIŞI
# ==========================================
if secim == "📌 NEB Master İş Akışı":
    st.header("NEB Hesaplaması Adım Adım İş Akışı")
    st.markdown("""
    Bu liste, NEB hesaplaması için hollow yöntemidir.
    * **1. Adım:** ilk olarak bulk yapımızı statik bir hesap ile tekrar optimize edelim.
    * **2. Adım:** Optimize olmuş yapıyı vaspkit ile "803" uygun yönlerden slab- katman- ve vakum yapacağız, katman için 3 veya 5, vakum için 15-20 A yeterli.
    * **3. Adım:** kararlı olan yüzeyi tespit edip ( slab hesabı için otomasyon kullanabilirsiniz ve sonuçlarıda slab_result ile incele.) bu yapıdan ilerleyeceğiz. 
    * **4. Adım:** bu yapılardan modül 30 yardımı ile initial ve final yapılarını oluşturup bunları önce kaba optimize yapıp sonra tüm etkiler ile birlikte optimize yapılacak.
    * **5. Adım:** Sonra 5 veya 7 image ile NEB hesabı kurulacak. (nebmake.pl) veya ase kod yardımı ile (IDPP)
    * **. Aşama:** Cartesian koordinatlı $1 \\times 3 \\times 1$ süper hücre oluştur. Altı kilitle (`F F F`), üstü serbest bırak (`T T T`).
    * **. Aşama:** Kaba Optimizasyon (Dipol KAPALI, `PREC=Normal`, `EDIFFG=-0.05`).
    * **. Aşama:** Hassas Optimizasyon (Dipol AÇIK, `PREC=Accurate`, `EDIFFG=-0.02`, `ISTART=1`).
    * **. Aşama:** VTST `nebmake.pl` ile imajları oluştur (00 ve 08 içine OUTCAR'ları koymayı unutma!).
    * **. Aşama:** CI-NEB Koşusu (Çekirdek sayısı imaj sayısına tam bölünmeli).
    """)

# ==========================================
# MODÜL 2: INCAR VE TRUBA ARŞİVİ
# ==========================================
elif secim == "⚙️ INCAR & TRUBA Arşivi":
    st.header("⚙️ INCAR ve TRUBA Gönderim Arşivi")
    st.markdown("Hesaplama türünüze en uygun, test edilmiş ve makale kalitesindeki (Q1) INCAR dosyalarını buradan kopyalayabilirsiniz.")
    st.markdown("---")

    kategori = st.selectbox("📂 Hangi Hesaplama İçin INCAR Arıyorsunuz?", [
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
    
    if kategori == "🟢 Optimizasyon":
        st.subheader("Optimizasyon")
        st.warning("⚠️ **Manyetik malzemeler için düzenleme unutma.")
        
        incar_bulk_opt1 = """SYSTEM = Bulk Supercell - IS/FS Optimizasyonu

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
        st.code(incar_bulk_opt1, language="bash") 
    if kategori == "🟢 IS ve FS için Kaba Optimizasyon":
        st.subheader("Optimizasyon")
        st.warning("⚠️ **Manyetik malzemeler için düzenleme unutma.")
        
        incar_bulk_opt2 = """SYSTEM = Kaba_Optimizasyon_Dipolsuz

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
        st.code(incar_bulk_opt2, language="bash")
        
    if kategori == "🟢 IS ve FS için ince Optimizasyon":
        st.subheader("Optimizasyon")
        st.warning("⚠️ **Manyetik malzemeler için düzenleme unutma.")
        
        incar_bulk_opt3 = """SYSTEM = Ince_Optimizasyon_Makale_Kalitesi

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
        st.code(incar_bulk_opt3, language="bash")
        
    if kategori == "🟢 NEB INCAR":
        st.subheader("Optimizasyon")
        st.warning("⚠️ **Manyetik malzemeler için düzenleme unutma.")
        
        incar_neb = """SYSTEM = NEB_H2_Desorpsiyonu_7_Imaj

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
        st.code(incar_neb, language="bash")
    
    
    
    
    
    
    
    if kategori == "🟢 KÜTLE İÇİ (BULK) - IS ve FS Optimizasyonu":
        st.subheader("Kütle İçi (Bulk) IS ve FS Optimizasyonu")
        st.warning("⚠️ **Fiziksel Kural:** Kütle içi (Supercell) hesaplamalarda vakum boşluğu olmadığı için **LDIPOL düzeltmesi KAPALIDIR**. Hücre hacminin değişip NEB'i bozmaması için **ISIF = 2** olarak ayarlanmıştır.")
        
        incar_bulk_opt = """SYSTEM = Bulk Supercell - IS/FS Optimizasyonu

# --- Elektronik Optimizasyon ---
PREC    = Accurate     ! Makale kalitesi için zorunlu
ADDGRID = .TRUE.       ! Ekstra fourier ağı (Kuvvet hassasiyeti)
ENCUT   = 500
EDIFF   = 1E-6         ! Sıkı yakınsama
ALGO    = Normal
LREAL   = Auto
ISMEAR  = 0
SIGMA   = 0.05
ISYM    = 0            ! NEB'e girecek yapılar için simetri kapalı kalmalı

# --- İyonik Optimizasyon ---
IBRION  = 2            ! Conjugate-Gradient Algoritması
ISIF    = 2            ! Sadece iyonlar hareket eder, hücre sabit kalır
NSW     = 100          
EDIFFG  = -0.02        ! Kuvvet yakınsama kriteri

# --- Çıktı Kontrolü ---
LWAVE   = .FALSE.       ! NEB'e hız katmak için WAVECAR'ı yazdır
LCHARG  = .FALSE.      ! Diski doldurmamak için kapalı
"""
        st.code(incar_bulk_opt, language="bash")
        st.info("💡 **K-Point Uyarısı:** Süper hücre kullandığınız için K-Point ağınızı küçültmeyi unutmayın (Örn: 2x2x2 veya 1x1x1 Gamma).")

    elif kategori == "🟢 KÜTLE İÇİ (BULK) - CI-NEB Geçiş Durumu":
        st.subheader("Kütle İçi (Bulk) CI-NEB Hesaplaması")
        st.info("💡 **Gönderim Kuralı:** 'IMAGES =' kısmını ürettiğiniz imaj sayısına göre güncelleyin. TRUBA'dan isteyeceğiniz çekirdek sayısı, İmaj sayısına tam bölünmek zorundadır!")
        
        incar_bulk_neb = """SYSTEM = Bulk Supercell - CI-NEB Hesabi

# --- Elektronik Optimizasyon (IS/FS ile Birebir Aynı) ---
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
LCLIMB  = .TRUE.       ! CI-NEB (Gerçek tepe noktasını bulur)
SPRING  = -5.0         ! İmajlar arası yay sertliği

# --- İyonik Optimizasyon (NEB Özel Algoritması) ---
IBRION  = 3            ! VTST optimizasyonu için 3 olmalı
IOPT    = 1            ! LBFGS algoritması (En stabil NEB yakınsaması)
POTIM   = 0.0          ! IOPT=1 olduğu için 0.0 olmalı
MAXMOVE = 0.2          ! Atomlar bir adımda çok uzağa fırlamasın
NSW     = 200          
EDIFFG  = -0.02        ! DİKKAT: IS/FS optimizasyonuyla AYNI olmalı

# --- Çıktı Kontrolü ---
LWAVE   = .FALSE.      
LCHARG  = .FALSE.      
"""
        st.code(incar_bulk_neb, language="bash")

    elif kategori == "🔵 YÜZEY (SLAB) - IS ve FS Optimizasyonu":
        st.subheader("Yüzey (Slab) IS ve FS Optimizasyonu")
        st.error("🚨 **Fiziksel Kural:** Slab modellerinde vakum olduğu için **LDIPOL = .TRUE.** olmak zorundadır! Elektronların vakuma taşmasını engeller.")
        
        incar_slab_opt = """SYSTEM = Slab Surface - IS/FS Optimizasyonu

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
        st.code(incar_slab_opt, language="bash")

    elif kategori == "🔵 YÜZEY (SLAB) - CI-NEB Geçiş Durumu":
        st.subheader("Yüzey (Slab) CI-NEB Hesaplaması")
        
        incar_slab_neb = """SYSTEM = Slab Surface - CI-NEB Hesabi

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
        st.code(incar_slab_neb, language="bash")
        
    elif kategori == "⚪ STANDART - Hücre ve Geometri Optimizasyonu (ISIF=3)":
        st.subheader("Sıfırdan Birim Hücre (Unit Cell) Optimizasyonu")
        st.success("✅ Bu INCAR, yeni indirdiğiniz bir kristalin (Bulk) hem hacmini (a, b, c) hem de atom koordinatlarını optimize etmek içindir.")
        
        incar_std = """SYSTEM = Full Cell Optimization (ISIF=3)

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
        st.code(incar_std, language="bash")

# ==========================================
# MODÜL 3: TERMODİNAMİK (VDOS VE CV) - ORIGIN STYLE
# ==========================================
elif secim == "🔥 Termodinamik (VDOS)":
    st.header("Fonon Termodinamiği: Isı Kapasitesi ($C_v$) ve Enerji")
    st.markdown("VASP fonon hesaplamalarından elde ettiğiniz `VDOS.dat` dosyasını yükleyerek malzemenin termodinamik özelliklerini hesaplayın ve OriginLab kalitesinde görselleştirin.")
    
    # Kullanıcı Arayüzü (Veri Yükleme Paneli)
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("VDOS.dat Dosyasını Yükleyin", type=["dat", "txt"], key="vdos_uploader")
        material_name = st.text_input("Malzeme Formülü (Başlık İçin):", "K_2TiH_5")
    with col2:
        n_atoms = st.number_input("Formüldeki Atom Sayısı (Örn: K2TiH5 = 8)", min_value=1, value=8, step=1)
        temp_end_input = st.number_input("Hesaplanacak Maksimum Sıcaklık (K):", min_value=500, max_value=4000, value=1500, step=100)

    st.markdown("---")

    # --- 1. ADIM: AĞIR HESAPLAMA VE HAFIZAYA ALMA (Sadece butona basılınca çalışır) ---
    if uploaded_file is not None:
        if st.button("Veriyi Hesapla ve Grafiği Hazırla", type="primary"):
            try:
                
                # Dosyayı okuma
                df = pd.read_csv(uploaded_file, sep=r'\s+', comment='#', names=['Freq', 'Int']).dropna()
                df = df[df['Freq'] > 0]
                
                # Sabitler
                R = 8.31446
                h_eV = 4.13567e-15
                kB_eV = 8.61733e-5
                THz_to_Hz = 1e12
                
                # Hesaplama Hazırlığı
                freq = df['Freq'].values * THz_to_Hz
                dos = df['Int'].values
                scale = (3 * n_atoms) / trapezoid(dos, df['Freq'].values)
                T_range = np.linspace(0.1, temp_end_input, 500) 
                
                cv_list, uvib_list = [], []
                
                # İntegral Döngüsü
                for T in T_range:
                    x = np.clip((h_eV * freq) / (kB_eV * T), None, 500)
                    cv_val = (x**2 * np.exp(x)) / (np.exp(x) - 1)**2
                    u_val = (h_eV * freq) / (np.exp(x) - 1)
                    cv_list.append(scale * trapezoid(cv_val * dos, df['Freq'].values))
                    uvib_list.append(scale * trapezoid(u_val * dos, df['Freq'].values))
                
                # Verileri hafızaya at!
                st.session_state.vdos_data_ready = True
                st.session_state.vdos_T_range = T_range
                st.session_state.vdos_Cv = np.array(cv_list) * R
                st.session_state.vdos_U_vib = np.array(uvib_list)
                st.session_state.vdos_dp_limit = 3 * n_atoms * R
                st.session_state.vdos_temp_end = temp_end_input
                
            except Exception as e:
                st.error(f"Hesaplama hatası: {e}")

    # --- 2. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM (Veri hazırsa çalışır) ---
    if st.session_state.get("vdos_data_ready", False):
        st.success(f"✅ Analiz Tamamlandı! Dulong-Petit Limiti: **{st.session_state.vdos_dp_limit:.2f} J/mol·K**")
        
        # Otonom başlangıç değerleri atama
        def_dp = st.session_state.vdos_dp_limit
        def_temp = st.session_state.vdos_temp_end
        def_uvib_max = max(st.session_state.vdos_U_vib)

        # 📐 EKSEN VE İNCE AYAR PANELİ (SİZİN İSTEDİĞİNİZ BÖLÜM)
        with st.expander("📐 Eksen, Lejant ve Özel Metin Ayarları (Anlık Tepki)", expanded=True):
            st.markdown("**1. X Ekseni (Sıcaklık)**")
            cx1, cx2, cx3 = st.columns(3)
            with cx1: p_x_min = st.number_input("X Başlangıç (K)", value=0.0, step=100.0)
            with cx2: p_x_max = st.number_input("X Bitiş (K)", value=float(def_temp), step=100.0)
            with cx3: p_x_step = st.number_input("X Aralık (Tick)", value=300.0, step=100.0)

            st.markdown("**2. Y Eksenleri (Sol: Cv, Sağ: U_vib)**")
            cy1, cy2, cy3, cy4 = st.columns(4)
            with cy1: p_y1_min = st.number_input("Y1 (Cv) Min", value=0.0, step=10.0)
            with cy2: p_y1_max = st.number_input("Y1 (Cv) Max", value=float(def_dp * 1.2), step=10.0)
            with cy3: p_y2_min = st.number_input("Y2 (U) Min", value=0.0, step=0.1)
            with cy4: p_y2_max = st.number_input("Y2 (U) Max", value=float(def_uvib_max * 1.1), step=0.1)

            st.markdown("**3. Lejant ve Çizgi İsimleri**")
            cl1, cl2, cl3 = st.columns(3)
            with cl1: p_leg1 = st.text_input("Cv Çizgisi İsmi", value="Heat Capacity ($C_v$)")
            with cl2: p_leg2 = st.text_input("U_vib Çizgisi İsmi", value="Vibrational Energy")
            with cl3: p_leg_loc = st.selectbox("Lejant Konumu", ["best", "upper left", "upper right", "lower left", "lower right", "center right"], index=5)

            st.markdown("**4. Grafik İçi Bilgi Kutucuğu**")
            ct1, ct2, ct3 = st.columns(3)
            with ct1: p_box_text = st.text_input("Kutu Metni (Boş = Çizilmez)", value=f"D-P Limit: {def_dp:.2f}")
            with ct2: p_box_x = st.number_input("Metin X Konumu (Data Coords)", value=def_temp * 0.05, step=50.0)
            with ct3: p_box_y = st.number_input("Metin Y Konumu (Data Coords)", value=def_dp * 1.05, step=10.0)

        # 🎨 ÇİZİM BÖLÜMÜ (Yukarıdaki parametreleri anında grafiğe basar)
        
        fig, ax1 = plt.subplots(figsize=(10, 7))

        # Çizgiler (Hafızadan okunuyor)
        line1, = ax1.plot(st.session_state.vdos_T_range, st.session_state.vdos_Cv, color="#0000FF", lw=2.5, label=p_leg1)
        ax2 = ax1.twinx()
        line2, = ax2.plot(st.session_state.vdos_T_range, st.session_state.vdos_U_vib, color="#FF0000", lw=2.5, ls='--', label=p_leg2)

        # Dulong-Petit Referans Çizgisi
        ax1.axhline(y=def_dp, color='black', ls=':', lw=1.5, alpha=0.6)

        # X Ekseni Dinamik Ayarları
        ax1.set_xlim(p_x_min, p_x_max)
        ax1.xaxis.set_major_locator(MultipleLocator(p_x_step))
        ax1.xaxis.set_minor_locator(AutoMinorLocator(2))

        # Y Eksenleri Dinamik Ayarları
        ax1.set_ylim(p_y1_min, p_y1_max)
        ax2.set_ylim(p_y2_min, p_y2_max)

        # Eksen İsimleri (Mathtext kullanılarak)
        ax1.set_xlabel('Temperature (K)', fontweight='bold', labelpad=10)
        ax1.set_ylabel('$C_v$ (J/mol·K)', color="#0000FF", fontweight='bold', labelpad=10)
        ax2.set_ylabel('$U_{vib}$ (eV/f.u.)', color="#FF0000", fontweight='bold', labelpad=10)

        # Lejant Ayarı
        lines = [line1, line2]
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc=p_leg_loc, frameon=True, edgecolor='black', fancybox=False).get_frame().set_linewidth(1.2)

        # Özel Metin Kutusu Ekleme
        if p_box_text.strip() != "":
            ax1.text(p_box_x, p_box_y, p_box_text, fontsize=12, fontweight='bold',
                     bbox=dict(facecolor='white', alpha=0.9, edgecolor='black', boxstyle='square,pad=0.5'))

        plt.title(f'Thermodynamic Properties of ${material_name}$', fontweight='bold', pad=15)
        
        # Grafiği Ekrana Bas
        st.pyplot(fig)
        
        # İndirme Butonu
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight')
        st.download_button(
            label="📥 Son Ayarlarla Grafiği İndir (PNG)",
            data=buf.getvalue(),
            file_name=f"Cv_Uvib_{material_name}_Origin.png",
            mime="image/png"
        )
# ==========================================
# MODÜL 4: DİFÜZYON (ARRHENIUS) - ORIGIN STYLE
# ==========================================
elif secim == "⚡ Difüzyon (Arrhenius)":
    st.header("AIMD Difüzyon ve Arrhenius Analizi")
    st.markdown("AIMD simülasyonlarından elde ettiğiniz sıcaklığa bağlı difüzyon katsayılarını girerek aktivasyon enerjisini ($E_a$) hesaplayın ve OriginLab kalitesinde görselleştirin.")
    
    # --- 1. KULLANICI ARAYÜZÜ (Veri Girişi) ---
    col0, col1, col2 = st.columns([1, 2, 2])
    with col0:
        mat_name = st.text_input("Malzeme Formülü:", "K_2TiH_5")
    with col1:
        temp_input = st.text_input("Sıcaklıklar T (K) - Virgülle Ayırın:", "300, 450, 600, 750")
    with col2:
        diff_input = st.text_input("Difüzyon D (cm²/s) - Virgülle Ayırın:", "2.69e-06, 5.59e-06, 7.53e-06, 1.80e-05")
    
    st.markdown("---")
    
    # --- 2. ADIM: AĞIR HESAPLAMA VE HAFIZAYA ALMA ---
    if st.button("Veriyi Hesapla ve Grafiği Hazırla", type="primary"):
        try:
           
            # Verileri numpy array'e çevirme
            temperatures = np.array([float(x.strip()) for x in temp_input.split(',')])
            diffusion_coeffs = np.array([float(x.strip()) for x in diff_input.split(',')])
            
            if len(temperatures) != len(diffusion_coeffs):
                st.error("HATA: Girdiğiniz sıcaklık ve difüzyon katsayısı sayıları birbirine eşit olmalıdır!")
            else:
                # Hesaplamalar
                kB = 8.617333262e-5  
                inv_T = 1000 / temperatures
                ln_D = np.log(diffusion_coeffs)

                slope, intercept, r_value, p_value, std_err = stats.linregress(1/temperatures, ln_D)
                Ea_eV = -slope * kB            
                Ea_kJ = Ea_eV * 96.485        
                r_squared = r_value**2

                # Verileri hafızaya at!
                st.session_state.arr_ready = True
                st.session_state.arr_inv_T = inv_T
                st.session_state.arr_ln_D = ln_D
                st.session_state.arr_slope = slope
                st.session_state.arr_intercept = intercept
                st.session_state.arr_Ea_eV = Ea_eV
                st.session_state.arr_Ea_kJ = Ea_kJ
                st.session_state.arr_R2 = r_squared
                
        except Exception as e:
            st.error(f"Bir hata oluştu. Veri formatınızı kontrol edin. Hata: {e}")

    # --- 3. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("arr_ready", False):
        st.success(f"✅ Hesaplama Başarılı! Bulunan Aktivasyon Enerjisi: **{st.session_state.arr_Ea_eV:.3f} eV**")
        
        # Otonom başlangıç değerleri atama
        def_x_min = np.floor(min(st.session_state.arr_inv_T))
        def_x_max = np.ceil(max(st.session_state.arr_inv_T)) + 0.5
        def_y_min = np.floor(min(st.session_state.arr_ln_D)) - 1.0
        def_y_max = np.ceil(max(st.session_state.arr_ln_D)) + 1.0
        
        def_box_text = (f"$E_a = {st.session_state.arr_Ea_eV:.3f}$ eV\n"
                        f"$E_a = {st.session_state.arr_Ea_kJ:.2f}$ kJ/mol\n"
                        f"$R^2 = {st.session_state.arr_R2:.4f}$")

        # 📐 EKSEN VE İNCE AYAR PANELİ
        with st.expander("📐 Eksen, Lejant ve Özel Metin Ayarları (Anlık Tepki)", expanded=True):
            st.markdown("**1. X Ekseni [1000/T (K⁻¹)]**")
            cx1, cx2, cx3 = st.columns(3)
            with cx1: p_x_min = st.number_input("X Başlangıç", value=float(def_x_min), step=0.5)
            with cx2: p_x_max = st.number_input("X Bitiş", value=float(def_x_max), step=0.5)
            with cx3: p_x_step = st.number_input("X Aralık (Tick)", value=0.5, step=0.1)

            st.markdown("**2. Y Ekseni [ln(D)]**")
            cy1, cy2, cy3 = st.columns(3)
            with cy1: p_y_min = st.number_input("Y Başlangıç", value=float(def_y_min), step=1.0)
            with cy2: p_y_max = st.number_input("Y Bitiş", value=float(def_y_max), step=1.0)
            with cy3: p_y_step = st.number_input("Y Aralık (Tick)", value=1.0, step=0.5)

            st.markdown("**3. Lejant ve Çizgi İsimleri**")
            cl1, cl2, cl3 = st.columns(3)
            with cl1: p_leg1 = st.text_input("Veri Noktaları İsmi", value=f"${mat_name}$ Data")
            with cl2: p_leg2 = st.text_input("Fit Çizgisi İsmi", value="Linear Fit")
            with cl3: p_leg_loc = st.selectbox("Lejant Konumu", ["best", "upper right", "upper left", "lower left", "lower right"], index=1)

            st.markdown("**4. Grafik İçi Bilgi Kutucuğu (Ea ve R²)**")
            ct1, ct2, ct3 = st.columns(3)
            with ct1: p_box_text = st.text_area("Kutu Metni (Boş = Çizilmez)", value=def_box_text, height=100)
            with ct2: p_box_x = st.number_input("X Konumu (0 ile 1 arası)", value=0.05, step=0.05, help="0: En Sol, 1: En Sağ")
            with ct3: p_box_y = st.number_input("Y Konumu (0 ile 1 arası)", value=0.05, step=0.05, help="0: En Alt, 1: En Üst")

        # 🎨 ÇİZİM BÖLÜMÜ      
        fig, ax = plt.subplots(figsize=(8, 6))

        # Veri Noktaları ve Fit Çizgisi (Hafızadan)
        ax.scatter(st.session_state.arr_inv_T, st.session_state.arr_ln_D, 
                   color='red', s=120, edgecolor='black', zorder=5, label=p_leg1)
        
        x_fit_plot = np.linspace(p_x_min, p_x_max, 100)
        y_fit_plot = st.session_state.arr_intercept + st.session_state.arr_slope * (x_fit_plot / 1000)
        ax.plot(x_fit_plot, y_fit_plot, color='blue', lw=2.5, ls='--', label=p_leg2)

        # X ve Y Dinamik Eksen Ayarları
        ax.set_xlim(p_x_min, p_x_max)
        ax.set_ylim(p_y_min, p_y_max)
        ax.xaxis.set_major_locator(MultipleLocator(p_x_step))
        ax.yaxis.set_major_locator(MultipleLocator(p_y_step))
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

        # Etiketler ve Başlık
        ax.set_xlabel(r'1000 / T (K$^{-1}$)', fontweight='bold', labelpad=10)
        ax.set_ylabel(r'ln(D / cm$^{2}$s$^{-1}$)', fontweight='bold', labelpad=10)
        ax.set_title(rf'Arrhenius Plot for Hydrogen Diffusion in ${mat_name}$', fontweight='bold', pad=15)

        # Özel Metin Kutusu (Transform=ax.transAxes sayesinde her zaman ekrana göre hizalanır)
        if p_box_text.strip() != "":
            ax.text(p_box_x, p_box_y, p_box_text, transform=ax.transAxes, fontsize=12, fontweight='bold',
                    bbox=dict(facecolor='white', alpha=0.9, edgecolor='black', boxstyle='round,pad=0.6'))

        # Lejant
        ax.legend(frameon=True, edgecolor='black', loc=p_leg_loc).get_frame().set_linewidth(1.2)
        plt.tight_layout()

        # Grafiği Ekrana Bas
        st.pyplot(fig)
        
        # İndirme Butonu
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight')
        st.download_button(
            label="📥 Son Ayarlarla Grafiği İndir (PNG)",
            data=buf.getvalue(),
            file_name=f"Arrhenius_{mat_name}_Origin.png",
            mime="image/png"
        )
# ==========================================
# MODÜL 5: KİNETİK (MSD VE DİFÜZYON) - ORIGIN STYLE
# ==========================================
elif secim == "📈 Kinetik (MSD & Difüzyon)":
    st.header("AIMD Kinetik Analizi: MSD ve Difüzyon")
    st.markdown("Vaspkit'ten elde ettiğiniz `MSD.dat` ve `DIFFUSION_COEFFICIENT.dat` dosyalarını yükleyerek zamana bağlı difüzyon grafiklerini OriginLab kalitesinde çizin.")

    # --- 1. KULLANICI ARAYÜZÜ (Dosya Yükleme) ---
    col1, col2 = st.columns(2)
    with col1:
        msd_file = st.file_uploader("MSD.dat Yükle", type=["dat", "txt"], key="msd_up")
    with col2:
        diff_file = st.file_uploader("DIFFUSION_COEFFICIENT.dat Yükle", type=["dat", "txt"], key="diff_up")

    st.markdown("---")

    # --- 2. ADIM: AĞIR VERİ OKUMA VE HAFIZAYA ALMA ---
    if msd_file and diff_file:
        if st.button("Verileri Oku ve Grafiği Hazırla", type="primary"):
            try:
                # --- AKILLI DOSYA OKUYUCU (İmleci Başa Sarar) ---
                def smart_load(uploaded_file):
                    uploaded_file.seek(0) # HATAYI ÇÖZEN HAYAT KURTARICI SATIR!
                    df = pd.read_csv(uploaded_file, sep=r'\s+', comment='#', header=None, engine='python')
                    return df.dropna().reset_index(drop=True)

                msd_df = smart_load(msd_file)
                diff_df = smart_load(diff_file)
                
                # Hafızaya Atma
                st.session_state.kin_ready = True
                st.session_state.msd_df = msd_df
                st.session_state.diff_df = diff_df
                st.session_state.kin_time_max = float(msd_df[0].iloc[-1])
                st.session_state.kin_msd_max = float(msd_df[4].max())
                st.session_state.kin_diff_max = float((diff_df[4] * 1e4).max())
                
                st.success("✅ Veriler başarıyla okundu ve hafızaya alındı!")
                
            except Exception as e:
                st.error(f"Dosya okuma hatası: {e}. Lütfen dosyalarınızın Vaspkit çıktısı olduğundan emin olun.")

    # --- 3. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("kin_ready", False):
        
        # Otonom Başlangıç Değerlerini Çek
        def_t_max = st.session_state.kin_time_max
        def_msd_max = st.session_state.kin_msd_max
        def_diff_max = st.session_state.kin_diff_max
        
        # 📐 ÇİFT PANELLİ EKSEN VE İNCE AYAR PANELİ
        with st.expander("📐 Eksen, Lejant ve Özel Metin Ayarları (Anlık Tepki)", expanded=True):
            st.markdown("**1. Ortak X Ekseni (Zaman - fs)**")
            cx1, cx2, cx3 = st.columns(3)
            with cx1: p_x_min = st.number_input("X Başlangıç (fs)", value=0.0, step=1000.0)
            with cx2: p_x_max = st.number_input("X Bitiş (fs)", value=float(def_t_max), step=1000.0)
            with cx3: p_x_step = st.number_input("X Aralık (Tick)", value=float(np.ceil(def_t_max/6)), step=1000.0)

            st.markdown("**2. Y Eksenleri (Panel a ve Panel b)**")
            cy1, cy2, cy3, cy4 = st.columns(4)
            with cy1: p_y1_max = st.number_input("(a) Maks MSD (Å²)", value=float(np.ceil(def_msd_max)), step=0.5)
            with cy2: p_y1_step = st.number_input("(a) MSD Aralık", value=1.0, step=0.5)
            with cy3: p_y2_max = st.number_input("(b) Maks Difüzyon (10⁻⁴)", value=float(np.ceil(def_diff_max*10)/10), step=0.1)
            with cy4: p_y2_step = st.number_input("(b) Difüzyon Aralık", value=0.2, step=0.1)

            st.markdown("**3. Lejant ve Çizgi İsimleri (Panel a)**")
            cl1, cl2, cl3, cl4 = st.columns(4)
            with cl1: l_x = st.text_input("X Yönü İsmi", value="x-direction")
            with cl2: l_y = st.text_input("Y Yönü İsmi", value="y-direction")
            with cl3: l_z = st.text_input("Z Yönü İsmi", value="z-direction")
            with cl4: l_tot = st.text_input("Total İsmi", value="Total")

            st.markdown("**4. (b) Paneli İçin 'Converged D' Kutu Konumu (0 ile 1 arası)**")
            ct1, ct2 = st.columns(2)
            with ct1: p_box_x = st.number_input("Kutu X Konumu", value=0.95, step=0.05, help="0: Sol, 1: Sağ")
            with ct2: p_box_y = st.number_input("Kutu Y Konumu", value=0.15, step=0.05, help="0: Alt, 1: Üst")

        # 🎨 ÇİZİM BÖLÜMÜ
        
        # Hafızadan Verileri Çek
        msd_df = st.session_state.msd_df
        diff_df = st.session_state.diff_df

        fig, axes = plt.subplots(1, 2, figsize=(20, 8))
        colors = ['#1f77b4', '#2ca02c', '#ff7f0e', 'black']
        labels = [l_x, l_y, l_z, l_tot]
        line_styles = ['-.', '-.', '-.', '-']
        line_widths = [2.5, 2.5, 2.5, 4.0]

        # ==========================================
        # --- PANEL (a): MSD ÇİZİMİ ---
        # ==========================================
        ax1 = axes[0]
        time_msd = msd_df[0]
        for i, col in enumerate([1, 2, 3, 4]):
            ax1.plot(time_msd, msd_df[col], color=colors[i], linestyle=line_styles[i], 
                     linewidth=line_widths[i], alpha=0.9 if i<3 else 1.0, label=labels[i])

        ax1.set_xlabel(r'Time ($t$, fs)', fontweight='bold', labelpad=15)
        ax1.set_ylabel(r'Mean Square Displacement ($\mathbf{\AA}^2$)', fontweight='bold', color='black', labelpad=15)
        ax1.set_xlim(p_x_min, p_x_max)
        ax1.set_ylim(0, p_y1_max)
        
        ax1.text(0.04, 0.94, "(a) Mean Square Displacement", transform=ax1.transAxes, fontsize=18, fontweight='bold', va='top')
        ax1.legend(loc='upper left', bbox_to_anchor=(0.02, 0.85), frameon=False, ncol=2)

        # ==========================================
        # --- PANEL (b): DIFFUSION COEFFICIENT ÇİZİMİ ---
        # ==========================================
        ax2 = axes[1]
        time_diff = diff_df[0]
        for i, col in enumerate([1, 2, 3, 4]):
            y_data = diff_df[col] * 1e4 
            ax2.plot(time_diff, y_data, color=colors[i], linestyle=line_styles[i], 
                     linewidth=line_widths[i], alpha=0.9 if i<3 else 1.0)

        ax2.set_xlabel(r'Time ($t$, fs)', fontweight='bold', labelpad=15)
        ax2.set_ylabel(r'Diffusion Coefficient ($D$, $10^{-4}$ cm$^2$/s)', fontweight='bold', color='black', labelpad=15)
        ax2.set_xlim(p_x_min, p_x_max)
        ax2.set_ylim(0, p_y2_max)
        
        ax2.text(0.04, 0.94, "(b) Time-Dependent Diffusion", transform=ax2.transAxes, fontsize=18, fontweight='bold', va='top')

        # Nihai D Değerini Çekme ve Kutu Yazdırma 
        final_D = diff_df[4].iloc[-1]
        if final_D > 0:
            exponent = int(np.floor(np.log10(abs(final_D))))
            mantissa = final_D / 10**exponent
            d_latex_str = f"{mantissa:.2f} \\times 10^{{{exponent}}}"
        else:
            d_latex_str = "0.00"

        ax2.text(p_box_x, p_box_y, f"Converged $D_{{tot}} = {d_latex_str}$ cm$^2$/s", 
                 transform=ax2.transAxes, fontweight='bold', 
                 color='black', ha='right' if p_box_x > 0.5 else 'left', va='bottom',
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.4'))

        # --- ORTAK EKSEN DİNAMİK AYARLARI ---
        for ax in axes:
            ax.xaxis.set_major_locator(MultipleLocator(p_x_step))
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))
            ax.tick_params(axis='both', which='major', labelsize=16, direction='in', length=10, width=2.0, pad=8, top=True, right=False)
            ax.tick_params(axis='both', which='minor', direction='in', length=5, width=1.5, top=True, right=False)
            
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight('bold')
            for spine in ax.spines.values():
                spine.set_linewidth(2.0)
        
        ax1.yaxis.set_major_locator(MultipleLocator(p_y1_step))
        ax2.yaxis.set_major_locator(MultipleLocator(p_y2_step))

        plt.tight_layout(pad=3.0, w_pad=4.0)

        # --- EKRANA METRİK VE GRAFİK BASMA ---
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Simülasyon Süresi (Son Adım)", f"{time_diff.iloc[-1]:.0f} fs")
        col_m2.metric("Nihai Toplam Difüzyon Katsayısı (D)", f"{final_D:.4e} cm²/s")
        
        st.pyplot(fig)
        
        # İndirme Butonu
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight')
        st.download_button(
            label="📥 Son Ayarlarla Paneli İndir (PNG)",
            data=buf.getvalue(),
            file_name="MSD_Diffusion_Origin.png",
            mime="image/png"
        )
# ==========================================
# MODÜL 6: YAPISAL ANALİZ (RDF VE KOORDİNASYON) - ORIGIN STYLE
 #==========================================
elif secim == "⚛️ Yapısal Analiz (RDF)":
    st.header("Yapısal Analiz: Radial Distribution Function (RDF)")
    st.markdown("Vaspkit'ten elde edilen RDF ($g(r)$) ve Koordinasyon ($N(r)$) dosyalarını yükleyerek, istediğiniz sayıda paneli (1-6 arası) içeren makale kalitesinde grafikler oluşturun.")

    # --- 1. DİNAMİK PANEL SAYISI ---
    n_panels = st.number_input("Kaç Adet Atom Çifti (Panel) Çizilecek?", min_value=1, max_value=6, value=3, step=1)
    st.markdown("---")

    # --- 2. VERİ GİRİŞ SEKMELERİ (DİNAMİK) ---
    tab_names = [f"Panel {i+1}" for i in range(n_panels)]
    tabs = st.tabs(tab_names)
    
    # Verileri geçici olarak tutacağımız sözlük (Session state'e atmak için)
    temp_target_data = []

    for i in range(n_panels):
        with tabs[i]:
            c1, c2 = st.columns(2)
            with c1:
                label = st.text_input(f"Atom Çifti Etiketi", f"Pair-{i+1}", key=f"label_{i}")
                rdf_file = st.file_uploader(f"RDF Dosyası ($g(r)$)", type=["dat", "txt"], key=f"rdf_{i}")
            with c2:
                x_max = st.number_input(f"Maks X ($r$, Å)", value=5.0, step=0.5, key=f"x_max_{i}")
                coord_file = st.file_uploader(f"Coordination Dosyası ($N(r)$)", type=["dat", "txt"], key=f"coord_{i}")

            temp_target_data.append({
                "label": label, 
                "rdf_file": rdf_file, 
                "coord_file": coord_file,
                "x_max": x_max
            })

    st.markdown("---")

    # --- 3. AĞIR VERİ OKUMA VE HAFIZAYA ALMA ---
    if st.button("Verileri Oku ve Grafiği Hazırla", type="primary"):
        # Yüklenen dosyaları kontrol et (En az 1 panel tamamen dolu olmalı)
        valid_targets = []
        
        # Streamlit için özel okuma fonksiyonu
        def smart_load_st(uploaded_file):
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=r'\s+', header=None, comment='#', engine='python')
            data = pd.DataFrame({'X': pd.to_numeric(df.iloc[:, 0], errors='coerce'),
                                 'Y': pd.to_numeric(df.iloc[:, -1], errors='coerce')})
            return data.dropna().reset_index(drop=True)

        try:
            for t in temp_target_data:
                if t["rdf_file"] is not None and t["coord_file"] is not None:
                    rdf_df = smart_load_st(t["rdf_file"])
                    coord_df = smart_load_st(t["coord_file"])
                    
                    # Başlangıç Y sınırlarını otomatik bul (Dinamik ayarlama için)
                    y_max_auto = float(np.ceil(rdf_df['Y'].max() * 1.2))
                    yc_max_auto = float(np.ceil(coord_df['Y'].max() * 1.2))
                    if y_max_auto == 0: y_max_auto = 10.0
                    if yc_max_auto == 0: yc_max_auto = 10.0
                    
                    valid_targets.append({
                        "label": t["label"],
                        "rdf_df": rdf_df,
                        "coord_df": coord_df,
                        "x_max": float(t["x_max"]),
                        "y_max_auto": y_max_auto,
                        "yc_max_auto": yc_max_auto
                    })
            
            if len(valid_targets) == 0:
                st.error("HATA: Grafiği çizmek için en az bir panele ait hem RDF hem de Koordinasyon dosyalarını yüklemelisiniz!")
            else:
                st.session_state.rdf_ready = True
                st.session_state.rdf_targets = valid_targets
                st.success(f"✅ {len(valid_targets)} adet panel verisi başarıyla hafızaya alındı!")
                
        except Exception as e:
            st.error(f"Dosya okuma hatası: {e}. Vaspkit formatını kontrol edin.")

    # --- 4. ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("rdf_ready", False):
        valid_targets = st.session_state.rdf_targets
        n_valid = len(valid_targets)
        
        # 📐 EKSEN VE İNCE AYAR PANELİ (Dinamik Paneller İçin)
        with st.expander("📐 Origin İnce Ayarları (Y Eksenleri ve Adımlar)", expanded=True):
            st.markdown("Burada yaptığınız değişiklikler grafiğe **anında** yansır.")
            
            # Güncel panel ayarlarını tutacağımız liste
            panel_settings = []
            
            # Dinamik sekme arayüzü
            set_tabs = st.tabs([t["label"] for t in valid_targets])
            
            for i, (t, set_tab) in enumerate(zip(valid_targets, set_tabs)):
                with set_tab:
                    st.markdown(f"**Panel: {t['label']}**")
                    cc1, cc2, cc3, cc4 = st.columns(4)
                    with cc1: y_max = st.number_input(f"Maks g(r)", value=t["y_max_auto"], step=1.0, key=f"ps_y_{i}")
                    with cc2: y_step = st.number_input(f"g(r) Aralık", value=max(1.0, float(np.ceil(t["y_max_auto"]/5))), step=1.0, key=f"ps_ys_{i}")
                    with cc3: yc_max = st.number_input(f"Maks N(r)", value=t["yc_max_auto"], step=1.0, key=f"ps_yc_{i}")
                    with cc4: yc_step = st.number_input(f"N(r) Aralık", value=max(1.0, float(np.ceil(t["yc_max_auto"]/5))), step=1.0, key=f"ps_ycs_{i}")
                    
                    panel_settings.append({
                        "y_max": y_max, "y_step": y_step,
                        "yc_max": yc_max, "yc_step": yc_step
                    })

        # 🎨 ÇİZİM BÖLÜMÜ

        # --- Grid (Izgara) Mantığı (Örn: 4 panel ise 2x2 çizer) ---
        cols = min(n_valid, 3) # Maksimum yan yana 3 panel
        rows = int(np.ceil(n_valid / cols))
        
        # Figür boyutunu panel sayısına göre dinamik ayarla
        fig, axes = plt.subplots(rows, cols, figsize=(7 * cols, 6 * rows), squeeze=False)
        
        # Gereksiz (boş) panelleri görünmez yap
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                if idx >= n_valid:
                    axes[r, c].set_visible(False)

        ln1, ln2 = None, None # Lejant için
        
        for idx, (t, p_set) in enumerate(zip(valid_targets, panel_settings)):
            r, c = divmod(idx, cols)
            ax1 = axes[r, c]
            
            rdf_df = t["rdf_df"]
            coord_df = t["coord_df"]
            
            # --- Sol Eksen (RDF - g(r)) ---
            line1, = ax1.plot(rdf_df['X'], rdf_df['Y'], color='black', linewidth=3.5, label='$g(r)$')
            if idx == 0: ln1 = line1
            
            ax1.set_xlabel(r'Distance ($r$, $\mathbf{\AA}$)', fontsize=20, fontweight='bold', labelpad=10)
            # Sadece en soldaki panellere Y1 etiketi koy
            if c == 0: ax1.set_ylabel(r'$g(r)$', fontsize=24, fontweight='bold', color='black', labelpad=10)
            
            ax1.set_xlim(0, t["x_max"])
            ax1.set_ylim(0, p_set["y_max"])

            ax1.xaxis.set_major_locator(MultipleLocator(1.0))
            ax1.xaxis.set_minor_locator(AutoMinorLocator(2))
            ax1.yaxis.set_major_locator(MultipleLocator(p_set["y_step"]))
            ax1.yaxis.set_minor_locator(AutoMinorLocator(2))
            ax1.tick_params(axis='both', which='major', labelsize=16, direction='in', length=8, width=2, pad=8, top=True, right=False)
            ax1.tick_params(axis='both', which='minor', direction='in', length=4, width=1.5, top=True, right=False)

            # --- Sağ Eksen (Coordination - N(r)) ---
            ax2 = ax1.twinx()
            line2, = ax2.plot(coord_df['X'], coord_df['Y'], color='#d62728', linewidth=3.5, linestyle='--', label='$N(r)$')
            if idx == 0: ln2 = line2
            
            # Sadece en sağdaki panellere Y2 etiketi koy
            if c == cols - 1 or idx == n_valid - 1:
                ax2.set_ylabel(r'Coordination ($N$)', fontsize=20, fontweight='bold', color='#d62728', labelpad=20, rotation=-90)
            
            ax2.set_ylim(0, p_set["yc_max"])
            ax2.yaxis.set_major_locator(MultipleLocator(p_set["yc_step"]))
            ax2.yaxis.set_minor_locator(AutoMinorLocator(2))
            ax2.tick_params(axis='y', which='major', right=True, labelsize=16, direction='in', length=8, width=2, pad=8, colors='#d62728')
            ax2.tick_params(axis='y', which='minor', right=True, direction='in', length=4, width=1.5, colors='#d62728')

            # Tepe Noktası (Peak) Etiketi ve Oku
            peak_idx = rdf_df['Y'].idxmax()
            bond_len = rdf_df.loc[peak_idx, 'X']
            max_rdf = rdf_df['Y'].max()
            
            ax1.text(0.04, 0.94, f"({chr(97+idx)}) {t['label']}", transform=ax1.transAxes, fontsize=20, fontweight='bold', va='top')
            
            ax1.annotate(f'{bond_len:.2f} Å', xy=(bond_len, max_rdf), xytext=(bond_len + 0.3, max_rdf + (p_set["y_max"]*0.05)),
                         arrowprops=dict(arrowstyle='->', color='blue', lw=2.0), fontsize=16, color='blue', fontweight='bold')

        # Efsane (Legend) - Sadece ilk panelin (0,0) üst köşesinde
        if ln1 and ln2:
            axes[0, 0].legend([ln1, ln2], ['$g(r)$', '$N(r)$'], loc='upper right', frameon=False, fontsize=18, bbox_to_anchor=(0.98, 0.98))

        plt.tight_layout(pad=2.0, w_pad=3.0, h_pad=3.0)

        # --- EKRANA BASMA ---
        st.pyplot(fig)
        
        # İndirme Butonu
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=600, bbox_inches='tight')
        st.download_button(
            label=f"📥 {n_valid} Panelli RDF Grafiğini İndir (PNG)",
            data=buf.getvalue(),
            file_name="RDF_Coordination_Dynamic_Origin.png",
            mime="image/png"
        )
# ==========================================
# MODÜL 7: TİTREŞİM SPEKTRUMU (VDOS) - ORIGIN STYLE
# ==========================================
elif secim == "🎵 Titreşim Spektrumu (VDoS)":
    st.header("Titreşim Yoğunluk Durumları (Vibrational DoS)")
    st.markdown("VASP/Vaspkit çıktısı olan `TVDOS.dat` (Total) ve dilediğiniz sayıdaki `VDOS_X.dat` (Partial) dosyalarını yükleyerek makale kalitesinde spektrum grafiklerini oluşturun.")

    st.markdown("---")
    
    # --- 1. KULLANICI ARAYÜZÜ (Veri Girişi) ---
    col1, col2 = st.columns(2)
    with col1:
        malzeme_adi = st.text_input("Malzeme Adı (Grafik Başlığı İçin LaTeX)", r"\mathbf{K_2TiH_5}")
    with col2:
        total_file = st.file_uploader("1. Total VDoS (Örn: TVDOS.dat) *Zorunlu*", type=["dat", "txt"])
        
    st.markdown("---")
    
    # --- DİNAMİK PARTIAL DOSYA SİSTEMİ ---
    n_partials = st.number_input("Kaç Adet Kısmi (Partial) Atom Çizeceksiniz?", min_value=0, max_value=6, value=3, step=1)
    
    temp_partials = []
    if n_partials > 0:
        st.markdown("**Partial VDoS Dosyalarını Yükleyin**")
        p_cols = st.columns(min(n_partials, 3))
        
        for i in range(n_partials):
            col_idx = i % 3
            with p_cols[col_idx]:
                p_label = st.text_input(f"{i+1}. Atom Sembolü", value=["H", "Ti", "K", "O", "C", "N"][i] if i < 6 else f"Atom-{i+1}", key=f"plabel_{i}")
                p_file = st.file_uploader(f"Dosya ({p_label})", type=["dat", "txt"], key=f"pfile_{i}")
                temp_partials.append({"label": p_label, "file": p_file})
                
    st.markdown("---")

    # --- 2. ADIM: AĞIR VERİ OKUMA VE HAFIZAYA ALMA ---
    if st.button("Verileri Oku ve Grafiği Hazırla", type="primary"):
        if total_file is None:
            st.error("HATA: Grafiği çizmek için en azından 'Total VDoS' dosyasını yüklemelisiniz!")
        else:
            try:
                
                def smart_load(uploaded_file):
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, sep=r'\s+', comment='#', names=['Freq', 'Int'])
                    return df.dropna().query('Freq >= 0').reset_index(drop=True)

                total_df = smart_load(total_file)
                
                valid_partials = []
                for p in temp_partials:
                    if p["file"] is not None:
                        pdf = smart_load(p["file"])
                        valid_partials.append({"label": p["label"], "df": pdf})

                auto_x_max = float(np.ceil(total_df['Freq'].max() / 5) * 5)
                auto_y_max = float(np.ceil(total_df['Int'].max() / 10) * 10)

                st.session_state.vdos_ready = True
                st.session_state.vdos_total = total_df
                st.session_state.vdos_partials = valid_partials
                st.session_state.vdos_xmax = auto_x_max
                st.session_state.vdos_ymax = auto_y_max
                
                st.success("✅ Tüm veriler başarıyla hafızaya alındı!")
                
            except Exception as e:
                st.error(f"Dosya okuma hatası: {e}")

    # --- 3. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("vdos_ready", False):

        total_df = st.session_state.vdos_total
        partials = st.session_state.vdos_partials
        def_x = st.session_state.vdos_xmax
        def_y = st.session_state.vdos_ymax

        max_idx = total_df['Int'].idxmax()
        peak_freq = total_df['Freq'].iloc[max_idx]
        peak_int = total_df['Int'].iloc[max_idx]

        # 📐 EKSEN VE İNCE AYAR PANELİ
        with st.expander("📐 Eksen, Lejant ve Özel Metin Ayarları (Anlık Tepki)", expanded=False):
            cx1, cx2, cx3 = st.columns(3)
            with cx1: p_x_min = st.number_input("X Başlangıç", value=0.0, step=5.0)
            with cx2: p_x_max = st.number_input("X Bitiş", value=float(def_x), step=5.0)
            with cx3: p_x_step = st.number_input("X Aralık (Tick)", value=5.0, step=1.0)

            cy1, cy2, cy3 = st.columns(3)
            with cy1: p_y_min = st.number_input("Y Başlangıç", value=0.0, step=10.0)
            with cy2: p_y_max = st.number_input("Y Bitiş", value=float(def_y), step=10.0)
            with cy3: p_y_step = st.number_input("Y Aralık (Tick)", value=float(np.ceil(def_y/6)), step=10.0)

            ct1, ct2 = st.columns(2)
            with ct1: p_peak_x = st.number_input("Etiket X Konumu (Ok Uzunluğunu Etkiler)", value=float(peak_freq + 1.0), step=1.0)
            with ct2: p_peak_y = st.number_input("Etiket Y Konumu (Ok Uzunluğunu Etkiler)", value=float(peak_int + (def_y * 0.05)), step=5.0)
            
            p_leg_loc = st.selectbox("Lejant Konumu", ["best", "upper right", "upper left", "center right"], index=1)
            
            # 🔍 YENİ: KUBAS / İÇ GRAFİK (INSET) PANELİ
        with st.expander("🔍 İç Grafik (Inset / Büyüteç) Ayarları - Kubas Tepesi İçin", expanded=False):
            inset_aktif = st.checkbox("Grafiğe Büyüteç (Inset) Ekle", value=False)
            if inset_aktif:
                st.markdown("**Inset Eksen Sınırları**")
                ic1, ic2, ic3, ic4 = st.columns(4)
                with ic1: in_x_min = st.number_input("Inset X Min", value=60.0, step=5.0)
                with ic2: in_x_max = st.number_input("Inset X Max", value=90.0, step=5.0)
                with ic3: in_y_min = st.number_input("Inset Y Min", value=0.0, step=0.01)
                with ic4: in_y_max = st.number_input("Inset Y Max", value=0.05, step=0.01)

                st.markdown("**Inset'in Ana Grafik Üzerindeki Konumu (0 ile 1 Arası Yüzde)**")
                pc1, pc2, pc3, pc4 = st.columns(4)
                with pc1: in_loc_x = st.slider("X Konumu (Sağ/Sol)", 0.0, 1.0, 0.65)
                with pc2: in_loc_y = st.slider("Y Konumu (Alt/Üst)", 0.0, 1.0, 0.55)
                with pc3: in_width = st.slider("Genişlik", 0.1, 0.8, 0.3)
                with pc4: in_height = st.slider("Yükseklik", 0.1, 0.8, 0.3)
            
            # YENİ: Minör Çentik (Ara Çizgi) Kontrolü
            show_minor_ticks = st.checkbox("Eksenlerde Minör Çentikleri (Ara Ticks) Göster", value=True)

        # 🎨 YENİ: RENK, ÇİZGİ VE OK AYARLARI PANELİ
        with st.expander("🎨 Çizgi, Renk ve Ok İşareti Ayarları", expanded=True):
            ls_map = {"- (Düz)": "-", "-- (Kesik)": "--", "-. (Nokta-Kesik)": "-.", ": (Noktalı)": ":"}
            
            st.markdown("**Total VDoS Çizgisi**")
            tc1, tc2, tc3 = st.columns(3)
            with tc1: t_color = st.color_picker("Total Rengi", "#2c3e50")
            with tc2: t_ls = st.selectbox("Total Stili", list(ls_map.keys()), index=0)
            with tc3: t_lw = st.slider("Total Kalınlık", 1.0, 5.0, 2.5, 0.5)

            partial_styles = []
            if partials:
                st.markdown("**Partial (Kısmi) VDoS Çizgileri**")
                default_colors = ['#2980b9', '#e67e22', '#27ae60', '#8e44ad', '#c0392b', '#f39c12']
                
                for i, p in enumerate(partials):
                    pc1, pc2, pc3 = st.columns(3)
                    with pc1: p_c = st.color_picker(f"{p['label']} Rengi", default_colors[i % len(default_colors)], key=f"c_{i}")
                    with pc2: p_ls = st.selectbox(f"{p['label']} Stili", list(ls_map.keys()), index=1, key=f"ls_{i}")
                    with pc3: p_lw = st.slider(f"{p['label']} Kalınlığı", 1.0, 5.0, 2.0, 0.5, key=f"lw_{i}")
                    partial_styles.append({"color": p_c, "ls": ls_map[p_ls], "lw": p_lw})

            st.markdown("**Tepe Noktası (Peak) Oku Ayarları**")
            oc1, oc2 = st.columns(2)
            with oc1: arrow_color = st.color_picker("Ok ve Yazı Rengi", "#FF0000")
            with oc2: arrow_shrink = st.slider("Ok Kısaltma (Shrink) Payı", 0.0, 0.2, 0.05, 0.01, help="Değer büyüdükçe ok çizgisi etiketten ve tepeden uzaklaşır/kısalır.")

        # 🎨 ÇİZİM BÖLÜMÜ
        fig, ax = plt.subplots(figsize=(11, 7))

        # Total Çizimi
        ax.plot(total_df['Freq'], total_df['Int'], color=t_color, lw=t_lw, ls=ls_map[t_ls], label='Total VDoS', zorder=2)
        ax.fill_between(total_df['Freq'], total_df['Int'], color=t_color, alpha=0.1, zorder=1)

        # Partial Çizimleri
        for i, p in enumerate(partials):
            style = partial_styles[i]
            ax.plot(p["df"]['Freq'], p["df"]['Int'], color=style['color'], lw=style['lw'], ls=style['ls'], label=f'{p["label"]} (Partial)', zorder=3)

        # Tepe Noktası İşaretleme (Dinamik Renk ve Ok Boyu)
        ax.annotate(f'$\mathbf{{{peak_freq:.2f}\ THz}}$', 
                    xy=(peak_freq, peak_int), 
                    xytext=(p_peak_x, p_peak_y), 
                    fontsize=14, fontweight='bold', color=arrow_color,
                    arrowprops=dict(facecolor=arrow_color, edgecolor=arrow_color, shrink=arrow_shrink, width=1.5, headwidth=8))

        # Eksen Ayarları
        ax.set_xlim(p_x_min, p_x_max)
        ax.set_ylim(p_y_min, p_y_max)
        
        ax.xaxis.set_major_locator(ticker.MultipleLocator(p_x_step))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(p_y_step))
        
        # Minör Çentik (Minor Tick) Dinamik Kontrolü
        if show_minor_ticks:
            ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
            ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
        else:
            ax.xaxis.set_minor_locator(ticker.NullLocator())
            ax.yaxis.set_minor_locator(ticker.NullLocator())

        # Etiketler
        ax.set_xlabel(r'$\mathbf{Frequency\ (\nu,\ THz)}$', fontsize=16, labelpad=15)
        ax.set_ylabel(r'$\mathbf{Vibrational\ Density\ of\ States\ (a.u.)}$', fontsize=16, labelpad=15)
        ax.set_title(f'Vibrational Spectra of ${malzeme_adi}$', fontsize=18, pad=20, fontweight='bold')

        # Tick Fontları
        for tick in ax.get_xticklabels() + ax.get_yticklabels():
            tick.set_fontweight('bold')
            tick.set_fontsize(13)

        # Lejant
        ax.legend(loc=p_leg_loc, frameon=False, fontsize=16, ncol=2 if len(partials)>2 else 1, 
                  prop={'weight': 'bold', 'size': 14})
                  
        # 🔍 İÇ GRAFİK (INSET) ÇİZİMİ
        if st.session_state.get("inset_aktif", inset_aktif):
            # Inset eksenini oluştur
            axins = ax.inset_axes([in_loc_x, in_loc_y, in_width, in_height])
            
            # Ana grafikteki her şeyi Inset içine de çiz
            axins.plot(total_df['Freq'], total_df['Int'], color=t_color, lw=t_lw, ls=ls_map[t_ls])
            axins.fill_between(total_df['Freq'], total_df['Int'], color=t_color, alpha=0.1)
            for i, p in enumerate(partials):
                style = partial_styles[i]
                axins.plot(p["df"]['Freq'], p["df"]['Int'], color=style['color'], lw=style['lw'], ls=style['ls'])
            
            # Inset limitlerini ve ayarlarını uygula
            axins.set_xlim(in_x_min, in_x_max)
            axins.set_ylim(in_y_min, in_y_max)
            
            # Inset fontları ve çerçevesi
            for tick in axins.get_xticklabels() + axins.get_yticklabels():
                tick.set_fontweight('bold')
                tick.set_fontsize(10)
            
            axins.set_title("Kubas $\eta^2-H_2$", fontsize=12, fontweight='bold', pad=5)
            # İsteğe bağlı: Ana grafikten inset'e bağlayıcı çizgiler çizer
            # ax.indicate_inset_zoom(axins, edgecolor="black")
        plt.tight_layout()

        # Ekrana Basma
        st.pyplot(fig)
        
        # 💾 İNDİRME BÖLÜMÜ (DPI SEÇİMİ EKLENDİ)
        st.markdown("### 📥 Grafiği İndir")
        dcol1, dcol2 = st.columns([1, 3])
        with dcol1:
            dpi_secim = st.selectbox("Çözünürlük (DPI)", [300, 600, 1200], index=1, help="Makaleler için genellikle 600 DPI istenir.")
        
        with dcol2:
            st.markdown("<br>", unsafe_allow_html=True) # Butonu hizalamak için boşluk
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi_secim)
            
            clean_name = malzeme_adi.replace('\\', '').replace('{', '').replace('}', '').replace('mathbf', '').replace('_', '')
            st.download_button(
                label=f"Son Ayarlarla VDoS Grafiğini İndir (PNG, {dpi_secim} DPI)",
                data=buf.getvalue(),
                file_name=f"{clean_name}_VDoS_Origin.png",
                mime="image/png"
            )
# ==========================================
# MODÜL 8: PARÇALANMA TERMODİNAMİĞİ (T_des) - ORIGIN STYLE
# ==========================================
elif secim == "📉 Parçalanma Termodinamiği (T_des)":
    st.header("Termodinamik Parçalanma Yolları ve Denge Sıcaklığı ($T_{eq}$)")
    st.markdown("VASP VDOS verisi ve DFT enerjilerini kullanarak, malzemenin hidrojen salınım yollarının sıcaklığa bağlı Gibbs serbest enerji ($\Delta G$) değişimlerini OriginLab kalitesinde analiz edin.")

    st.markdown("---")
    
    # --- 1. KULLANICI ARAYÜZÜ (Veri Girişi) ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Girdi Verileri (DFT & VDOS)")
        malzeme_adi = st.text_input("Ana Malzeme Formülü (Grafik İçin)", r"\mathbf{K_2TiH_5}")
        vdos_file = st.file_uploader(f"Ana Malzeme VDOS Dosyası (TVDOS.dat)", type=["dat", "txt"], key="vdos_tdes")
        
        with st.expander("DFT Enerjilerini (eV) Düzenle", expanded=False):
            e_k2tih5 = st.number_input("E(Ana Malzeme)", value=-28.549848, format="%.6f")
            e_h2 = st.number_input("E(H2)", value=-6.7719, format="%.6f")
            e_k = st.number_input("E(K)", value=-1.0497, format="%.6f")
            e_ti = st.number_input("E(Ti)", value=-7.8405, format="%.6f")
            e_kh = st.number_input("E(KH) per formula", value=-19.320636 / 4, format="%.6f")
            e_tih2 = st.number_input("E(TiH2) per formula", value=-33.547465 / 2, format="%.6f")

        with st.expander("Standart Entropiler (J/mol.K)", expanded=False):
            s_k = st.number_input("S(K)", value=64.7)
            s_ti = st.number_input("S(Ti)", value=30.7)
            s_kh = st.number_input("S(KH)", value=50.2)
            s_tih2 = st.number_input("S(TiH2)", value=30.0)

    with col2:
        st.subheader("2. Reaksiyon Yolu Seçimi")
        st.info("Sadece grafikte görünmesini istediğiniz reaksiyonları seçin. Kendi sisteminize uyarlıyorsanız katsayıları kod içinden değiştirebilirsiniz.")
        
        path_elem = st.checkbox(r"Elemental: 2K + Ti + 2.5H$_2$", value=True)
        path_tih2 = st.checkbox(r"Only TiH$_2$: 2K + TiH$_2$ + 1.5H$_2$", value=True)
        path_kh   = st.checkbox(r"Only KH: 2KH + Ti + 1.5H$_2$", value=True)
        path_bin  = st.checkbox(r"Binary Hydrides: 2KH + TiH$_2$ + 0.5H$_2$", value=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        calc_t_max = st.number_input("Hesaplanacak Maksimum Sıcaklık (K)", min_value=500, max_value=2500, value=1500, step=100)

    st.markdown("---")

    # --- 2. ADIM: AĞIR HESAPLAMA VE HAFIZAYA ALMA ---
    if st.button("Termodinamik Verileri Hesapla", type="primary"):
        if vdos_file is None:
            st.error("Lütfen ana malzemeye ait VDOS dosyasını yükleyin!")
        elif not any([path_elem, path_tih2, path_kh, path_bin]):
            st.error("En az bir reaksiyon yolu seçmelisiniz!")
        else:
            try:
                
                # VDOS OKUMA VE ZPE / ENTROPİ HESABI
                vdos_file.seek(0)
                df = pd.read_csv(vdos_file, sep=r'\s+', comment='#', names=['Freq', 'Int']).dropna()
                df = df[df['Freq'] > 0]
                
                freq = df['Freq'].values * 1e12  
                dos = df['Int'].values
                scale = (3 * 8) / trapezoid(dos, df['Freq'].values) # 8 atomlu sistem kabulü

                zpe_k2tih5 = scale * trapezoid(0.5 * 4.13567e-15 * freq * dos, df['Freq'].values)

                T_range = np.linspace(1, calc_t_max, 300)
                kB = 8.61733e-5

                s_K2TiH5_T = []
                for T in T_range:
                    x = (4.13567e-15 * freq) / (kB * T)
                    s_val = kB * (x / (np.exp(x) - 1) - np.log(1 - np.exp(-x)))
                    s_K2TiH5_T.append(scale * trapezoid(s_val * dos, df['Freq'].values))
                s_K2TiH5_T = np.array(s_K2TiH5_T)

                s_h2_T = (130.68 / 96485) + (28.8 / 96485) * np.log(T_range / 298.15)

                # SEÇİLEN REAKSİYON YOLLARINI DERLEME
                all_pathways = {
                    "Elemental": {
                        "label": r"2K + Ti + 2.5H$_2$", "h2_coeff": 2.5,
                        "solid_products": [{"coeff": 2, "E": e_k, "S": s_k}, {"coeff": 1, "E": e_ti, "S": s_ti}],
                        "color": "#d62728", "linestyle": "-"
                    },
                    "Only_TiH2": {
                        "label": r"2K + TiH$_2$ + 1.5H$_2$", "h2_coeff": 1.5,
                        "solid_products": [{"coeff": 2, "E": e_k, "S": s_k}, {"coeff": 1, "E": e_tih2, "S": s_tih2}],
                        "color": "#ff7f0e", "linestyle": "--"
                    },
                    "Only_KH": {
                        "label": r"2KH + Ti + 1.5H$_2$", "h2_coeff": 1.5,
                        "solid_products": [{"coeff": 2, "E": e_kh, "S": s_kh}, {"coeff": 1, "E": e_ti, "S": s_ti}],
                        "color": "#2ca02c", "linestyle": "-."
                    },
                    "Binary_Hydrides": {
                        "label": r"2KH + TiH$_2$ + 0.5H$_2$", "h2_coeff": 0.5,
                        "solid_products": [{"coeff": 2, "E": e_kh, "S": s_kh}, {"coeff": 1, "E": e_tih2, "S": s_tih2}],
                        "color": "#1f77b4", "linestyle": ":"
                    }
                }

                active_pathways = {}
                if path_elem: active_pathways["Elemental"] = all_pathways["Elemental"]
                if path_tih2: active_pathways["Only_TiH2"] = all_pathways["Only_TiH2"]
                if path_kh:   active_pathways["Only_KH"] = all_pathways["Only_KH"]
                if path_bin:  active_pathways["Binary_Hydrides"] = all_pathways["Binary_Hydrides"]

                # ΔG Hesaplamaları
                results = {}
                y_min_global = 999
                y_max_global = -999

                for key, path in active_pathways.items():
                    E_products_solid = sum(p['coeff'] * p['E'] for p in path['solid_products'])
                    delta_E_dft = (E_products_solid + path['h2_coeff'] * e_h2) - e_k2tih5
                    
                    delta_zpe = (path['h2_coeff'] * 0.273) - zpe_k2tih5
                    delta_h_0 = delta_E_dft + delta_zpe
                    
                    S_products_solid_eV = sum(p['coeff'] * p['S'] for p in path['solid_products']) / 96485
                    delta_s_T = (path['h2_coeff'] * s_h2_T) + S_products_solid_eV - s_K2TiH5_T
                    
                    delta_g_T = delta_h_0 - T_range * delta_s_T
                    
                    y_min_global = min(y_min_global, min(delta_g_T))
                    y_max_global = max(y_max_global, max(delta_g_T))

                    # T_des bulma
                    T_des = None
                    zero_crossings = np.where(np.diff(np.sign(delta_g_T)))[0]
                    if len(zero_crossings) > 0 and delta_g_T[0] > 0:
                        idx = zero_crossings[0]
                        T1, T2 = T_range[idx], T_range[idx+1]
                        G1, G2 = delta_g_T[idx], delta_g_T[idx+1]
                        T_des = T1 - G1 * (T2 - T1) / (G2 - G1)

                    results[key] = {
                        "label": path["label"], "color": path["color"], "linestyle": path["linestyle"],
                        "delta_g": delta_g_T, "T_des": T_des
                    }

                # Hafızaya Kaydet
                st.session_state.tdes_ready = True
                st.session_state.tdes_T_range = T_range
                st.session_state.tdes_results = results
                st.session_state.tdes_ymin = y_min_global
                st.session_state.tdes_ymax = y_max_global
                st.session_state.tdes_calc_tmax = calc_t_max
                st.session_state.tdes_material = malzeme_adi
                
                st.success("✅ Termodinamik veriler başarıyla hesaplandı ve hafızaya alındı!")

            except Exception as e:
                st.error(f"Hesaplama sırasında bir hata oluştu: {e}")

    # --- 3. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("tdes_ready", False):
        T_range = st.session_state.tdes_T_range
        results = st.session_state.tdes_results
        
        # Otonom Sınırlar
        y_pad = (st.session_state.tdes_ymax - st.session_state.tdes_ymin) * 0.1
        def_y_min = np.floor((st.session_state.tdes_ymin - y_pad) * 10) / 10
        def_y_max = np.ceil((st.session_state.tdes_ymax + y_pad) * 10) / 10

        # 📐 EKSEN VE İNCE AYAR PANELİ
        with st.expander("📐 Eksen, Lejant ve Özel Metin Ayarları (Anlık Tepki)", expanded=True):
            st.markdown("**1. X Ekseni (Sıcaklık, K)**")
            cx1, cx2, cx3 = st.columns(3)
            with cx1: p_x_min = st.number_input("X Başlangıç", value=0.0, step=100.0)
            with cx2: p_x_max = st.number_input("X Bitiş", value=float(st.session_state.tdes_calc_tmax), step=100.0)
            with cx3: p_x_step = st.number_input("X Aralık (Tick)", value=200.0, step=100.0)

            st.markdown("**2. Y Ekseni ($\Delta G$, eV)**")
            cy1, cy2, cy3 = st.columns(3)
            with cy1: p_y_min = st.number_input("Y Başlangıç", value=float(def_y_min), step=0.5)
            with cy2: p_y_max = st.number_input("Y Bitiş", value=float(def_y_max), step=0.5)
            with cy3: p_y_step = st.number_input("Y Aralık (Tick)", value=0.5, step=0.1)

            st.markdown("**3. T_des Okları ve Lejant**")
            cl1, cl2 = st.columns(2)
            with cl1: p_arrow_spacing = st.number_input("Okların Dikey Aralığı (Çarpışmayı Önler)", value=0.25, step=0.05)
            with cl2: p_leg_loc = st.selectbox("Lejant Konumu", ["best", "upper right", "upper left", "lower left", "lower right"], index=1)

        # 🎨 ÇİZİM BÖLÜMÜ

        fig, ax = plt.subplots(figsize=(10, 7))

        # Yolları Çiz ve T_des İşaretle
        for idx, (key, path) in enumerate(results.items()):
            ax.plot(T_range, path["delta_g"], label=path['label'], color=path['color'], 
                    linestyle=path['linestyle'], linewidth=3.0)
            
            # T_des Oku ve Metni
            T_des = path["T_des"]
            if T_des is not None and p_x_min <= T_des <= p_x_max:
                ax.plot(T_des, 0, 'ko', markersize=8, markerfacecolor=path['color'], zorder=5)
                
                # Okları çarpışmadan üst üste dizmek için dinamik y_offset
                y_offset = p_arrow_spacing * (idx + 1)
                
                ax.annotate(rf'$\mathbf{{T_{{des}}}}$ = {T_des:.1f} K', 
                             xy=(T_des, 0), xytext=(T_des + (p_x_max*0.02), y_offset),
                             color=path['color'], fontsize=14, fontweight='bold',
                             arrowprops=dict(facecolor=path['color'], edgecolor=path['color'], arrowstyle='->', lw=2.5))

        # Y=0 Denge Çizgisi
        ax.axhline(0, color='black', linestyle='-', linewidth=1.5, zorder=1)

        # Eksen Sınırları ve Adımları
        ax.set_xlim(p_x_min, p_x_max)
        ax.set_ylim(p_y_min, p_y_max)
        
        ax.xaxis.set_major_locator(MultipleLocator(p_x_step))
        ax.yaxis.set_major_locator(MultipleLocator(p_y_step))
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

        # Etiketler ve Başlık
        ax.set_xlabel("Temperature (K)", fontsize=18, fontweight='bold', color='black', labelpad=12)
        ax.set_ylabel(r"$\boldsymbol{\Delta}\mathbf{G}$ (eV)", fontsize=18, fontweight='bold', color='black', labelpad=12)
        
        baslik_yol = "Decomposition" if len(results) == 1 else "Decomposition Pathways"
        mat_baslik = st.session_state.tdes_material
        ax.set_title(rf"Thermodynamic {baslik_yol} of ${mat_baslik}$", fontsize=18, fontweight='bold', color='black', pad=20)

        # Tick Stilleri
        ax.tick_params(axis='both', which='major', labelsize=14, direction='in', length=10, width=2)
        ax.tick_params(axis='both', which='minor', direction='in', length=5, width=1.5)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')

        # Çerçeve Kalınlığı
        for spine in ax.spines.values():
            spine.set_linewidth(2.5)  

        # Lejant
        legend = ax.legend(loc=p_leg_loc, prop={'weight':'bold', 'size':14}, framealpha=0.9)
        legend.get_frame().set_edgecolor('black')
        legend.get_frame().set_linewidth(1.5)

        plt.tight_layout()

        # Ekrana Basma
        st.pyplot(fig)
        
        # İndirme Butonu
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight')
        
        clean_name = mat_baslik.replace('\\', '').replace('{', '').replace('}', '').replace('mathbf', '').replace('_', '')
        dl_name = "Single_Pathway" if len(results) == 1 else "All_Pathways"
        
        st.download_button(
            label="📥 Son Ayarlarla T_des Grafiğini İndir (PNG)",
            data=buf.getvalue(),
            file_name=f"{clean_name}_{dl_name}_Origin.png",
            mime="image/png"
        )
# ==========================================
# MODÜL 9: AIMD KARARLILIK (SICAKLIK VE ENERJİ) - ORIGIN STYLE
# ==========================================
elif secim == "⏱️ AIMD Kararlılık (Sıcaklık/Enerji)":
    st.header("AIMD Kararlılık Analizi (Sıcaklık ve Toplam Enerji)")
    st.markdown("Farklı sıcaklıklarda çalıştırılan AIMD simülasyonlarının zamanla enerji ve sıcaklık dalgalanmalarını dilediğiniz sayıda veri setiyle karşılaştırın.")
    st.markdown("---")

    # --- 1. KULLANICI ARAYÜZÜ (Dinamik Veri Yükleme) ---
    c_mode, c_count = st.columns([1, 1])
    with c_mode:
        plot_mode = st.radio("Hangi veriler çizilsin?", ["İkisi Yan Yana (Both)", "Sadece Sıcaklık", "Sadece Enerji"])
        mode_dict = {"İkisi Yan Yana (Both)": "both", "Sadece Sıcaklık": "temp", "Sadece Enerji": "energy"}
        selected_mode = mode_dict[plot_mode]
    with c_count:
        n_datasets = st.number_input("Kaç Adet AIMD Verisi Karşılaştırılacak?", min_value=1, max_value=8, value=4, step=1)

    st.markdown("---")
    st.markdown(f"**AIMD Veri Dosyalarını Yükleyin ({n_datasets} Adet)**")
    
    # Dinamik Dosya Yükleme Arayüzü
    temp_aimd_data = []
    default_colors = ['#E74C3C', '#3498DB', '#27AE60', '#F39C12', '#9B59B6', '#34495E', '#1ABC9C', '#D35400'] 
    
    cols = st.columns(min(n_datasets, 4)) # Ekranda en fazla 4 sütun yan yana dursun
    for i in range(n_datasets):
        col_idx = i % 4
        with cols[col_idx]:
            # Etiket ve Renk Seçiciyi yan yana daha şık göstermek için alt sütunlar oluşturuyoruz
            c_lbl, c_col = st.columns([3, 1])
            with c_lbl:
                label = st.text_input(f"Etiket {i+1}", value=f"{300 + (i*150)} K", key=f"aimd_lbl_{i}")
            with c_col:
                # Renk seçici widget'ı (Varsayılan olarak listedeki rengi alır)
                chosen_color = st.color_picker(f"Renk", value=default_colors[i % len(default_colors)], key=f"aimd_color_{i}")
                
            file = st.file_uploader(f"Dosya {i+1}", type=["dat", "txt"], key=f"aimd_file_{i}")
            
            # Seçilen rengi "color" anahtarına atıyoruz
            temp_aimd_data.append({"file": file, "label": label, "color": chosen_color})

    st.markdown("---")

    # --- 2. ADIM: AĞIR VERİ OKUMA VE HAFIZAYA ALMA ---
    if st.button("Verileri Oku ve Grafiği Hazırla", type="primary"):
        loaded_datasets = []
        
        # Otonom Sınırlar İçin Değişkenler
        global_t_max = 0
        global_temp_min, global_temp_max = 99999, -99999
        global_e_min, global_e_max = 99999, -99999

        try:
            for item in temp_aimd_data:
                if item["file"] is not None:
                    item["file"].seek(0)
                    df = pd.read_csv(item["file"], sep=r'\s+')
                    
                    # Zaman birimi düzeltmesi
                    if 'Time(ps)' in df.columns and 'Time(fs)' not in df.columns:
                        df['Time(fs)'] = df['Time(ps)'] * 1000
                    elif 'Time(fs)' not in df.columns:
                        df['Time(fs)'] = df.index 
                        
                    # Otonom Sınırları Güncelle
                    if 'Time(fs)' in df.columns:
                        global_t_max = max(global_t_max, df['Time(fs)'].max())
                    if 'Temperature(K)' in df.columns:
                        global_temp_min = min(global_temp_min, df['Temperature(K)'].min())
                        global_temp_max = max(global_temp_max, df['Temperature(K)'].max())
                    if 'Energy(eV)' in df.columns:
                        global_e_min = min(global_e_min, df['Energy(eV)'].min())
                        global_e_max = max(global_e_max, df['Energy(eV)'].max())

                    loaded_datasets.append({"df": df, "label": rf"$\mathbf{{{item['label']}}}$", "color": item["color"]})

            if len(loaded_datasets) == 0:
                st.error("HATA: Grafiği çizmek için en az bir adet AIMD veri dosyası yüklemelisiniz!")
            else:
                # Hafızaya Kaydet
                st.session_state.aimd_ready = True
                st.session_state.aimd_datasets = loaded_datasets
                st.session_state.aimd_mode = selected_mode
                
                # Sınırları Güvenli Hale Getir
                st.session_state.aimd_bounds = {
                    "t_max": float(global_t_max) if global_t_max > 0 else 10000.0,
                    "temp_min": float(global_temp_min) if global_temp_min != 99999 else 0.0,
                    "temp_max": float(global_temp_max) if global_temp_max != -99999 else 1000.0,
                    "e_min": float(global_e_min) if global_e_min != 99999 else -200.0,
                    "e_max": float(global_e_max) if global_e_max != -99999 else -100.0
                }
                st.success(f"✅ {len(loaded_datasets)} adet veri seti başarıyla okundu!")

        except Exception as e:
            st.error(f"Veri okuma hatası: Sütun adlarının 'Time(fs)', 'Temperature(K)', 'Energy(eV)' olduğundan emin olun. Detay: {e}")

    # --- 3. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("aimd_ready", False):
        datasets = st.session_state.aimd_datasets
        mode = st.session_state.aimd_mode
        b = st.session_state.aimd_bounds

        # 📐 EKSEN VE İNCE AYAR PANELİ
        with st.expander("📐 Eksen, Lejant ve Özel Metin Ayarları (Anlık Tepki)", expanded=True):
            st.markdown("**1. X Ekseni (Zaman - fs)**")
            cx1, cx2 = st.columns(2)
            with cx1: p_x_max = st.number_input("Maksimum Zaman (fs)", value=b["t_max"], step=1000.0)
            with cx2: p_x_step = st.number_input("X Ekseni Adımı (Tick)", value=float(np.ceil(b["t_max"]/5)), step=1000.0)

            c_t, c_e = st.columns(2)
            with c_t:
                st.markdown("**2. Sıcaklık Ekseni (K)**")
                p_t_min = st.number_input("Min Sıcaklık", value=np.floor(b["temp_min"]/50)*50, step=50.0)
                p_t_max = st.number_input("Maks Sıcaklık", value=np.ceil(b["temp_max"]/50)*50, step=50.0)
                p_t_step = st.number_input("Sıcaklık Adımı (Tick)", value=100.0, step=50.0)
            
            with c_e:
                st.markdown("**3. Enerji Ekseni (eV)**")
                p_e_min = st.number_input("Min Enerji", value=np.floor(b["e_min"]), step=1.0)
                p_e_max = st.number_input("Maks Enerji", value=np.ceil(b["e_max"]), step=1.0)
                p_e_step = st.number_input("Enerji Adımı (Tick)", value=2.0, step=1.0)

            p_leg_loc = st.selectbox("Lejant Konumu", ["best", "upper right", "upper left", "lower left", "lower right", "center right"], index=1)

        # 🎨 ÇİZİM BÖLÜMÜ

        if mode == "temp":
            selected_metrics = [('Temperature(K)', 'Temperature (K)', (p_t_min, p_t_max), p_t_step)]
        elif mode == "energy":
            selected_metrics = [('Energy(eV)', 'Total Energy (eV)', (p_e_min, p_e_max), p_e_step)]
        else:
            selected_metrics = [
                ('Temperature(K)', 'Temperature (K)', (p_t_min, p_t_max), p_t_step), 
                ('Energy(eV)', 'Total Energy (eV)', (p_e_min, p_e_max), p_e_step)
            ]

        num_cols = len(selected_metrics)
        fig, axs = plt.subplots(1, num_cols, figsize=(14*num_cols, 8), squeeze=False)

        for col in range(num_cols):
            ax = axs[0, col]
            m_col, ylabel, y_limits, y_step = selected_metrics[col]
            
            for i, data in enumerate(datasets):
                df = data["df"]
                if m_col in df.columns:
                    ax.plot(df['Time(fs)'], df[m_col], color=data["color"], linewidth=2.5, 
                            label=data["label"], alpha=0.85, zorder=10-i)
            
            # Eksen Etiketleri ve Sınırları
            ax.set_ylabel(ylabel, fontsize=24, fontweight='bold', labelpad=20)
            ax.set_xlabel('Time (fs)', fontsize=24, fontweight='bold', labelpad=20)
            ax.set_xlim(0, p_x_max)
            ax.set_ylim(y_limits[0], y_limits[1])

            # Tick (Adım) Ayarları
            ax.xaxis.set_major_locator(MultipleLocator(p_x_step))
            ax.yaxis.set_major_locator(MultipleLocator(y_step))
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))
            ax.yaxis.set_minor_locator(AutoMinorLocator(2))

            ax.tick_params(axis='both', which='major', direction='in', length=12, width=2.5, labelsize=20, pad=10, top=True, right=False)
            ax.tick_params(axis='both', which='minor', direction='in', length=6, width=1.5, top=True, right=False)

            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight('bold')

            for spine in ax.spines.values():
                spine.set_linewidth(2.5)

            # Sadece tek panelde (veya sol panelde) lejant göster
            if col == 0:
                ax.legend(loc=p_leg_loc, fontsize=20, frameon=True, edgecolor='black', framealpha=0.9).get_frame().set_linewidth(1.5)

        plt.tight_layout(pad=3.0)

        # Ekrana Basma
        st.pyplot(fig)
        
        # İndirme Butonu
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=600, bbox_inches='tight')
        st.download_button(
            label="📥 Son Ayarlarla AIMD Grafiğini İndir (PNG)",
            data=buf.getvalue(),
            file_name=f"AIMD_Multi_{mode}_Origin.png",
            mime="image/png"
        )
# ==========================================
# MODÜL 10: ELEKTRONİK BANT YAPISI (BAND STRUCTURE) - ORIGIN STYLE
# ==========================================
elif secim == "🌌 Elektronik Bant Yapısı (Band)":
    st.header("Elektronik Bant Yapısı ve Band Gap Grafiği")
    st.markdown("Vaspkit çıktıları olan `BAND.dat` (veya `BAND-RE.dat`), `KLABELS` ve `BAND_GAP` dosyalarını yükleyerek yüksek çözünürlüklü bant grafiklerini çizin.")
    st.markdown("---")

    # --- 1. KULLANICI ARAYÜZÜ (Veri Yükleme) ---
    is_spin = st.checkbox("Manyetik / Spin-Polarize (ISPIN=2) Hesaplama Mı?", value=False, help="Eğer hesaplamanızda Spin-Up ve Spin-Down bantları ayrıysa bunu işaretleyin. BAND.dat dosyanız 3 sütunlu okunacaktır.")
    
    c1, c2, c3 = st.columns(3)
    with c1: band_file = st.file_uploader("1. BAND.dat Yükle", type=["dat", "txt"])
    with c2: klabels_file = st.file_uploader("2. KLABELS Yükle")
    with c3: gap_file = st.file_uploader("3. BAND_GAP Yükle")

    st.markdown("---")

    # --- 2. ADIM: AĞIR VERİ OKUMA VE HAFIZAYA ALMA ---
    if st.button("Verileri Oku ve Grafiği Hazırla", type="primary"):
        if not (band_file and klabels_file and gap_file):
            st.error("HATA: Grafiği çizmek için BAND.dat, KLABELS ve BAND_GAP dosyalarının üçünü de yüklemelisiniz!")
        else:
            try:
                
                # Dosyaları okuma
                klabels_text = klabels_file.getvalue().decode("utf-8").splitlines()
                gap_text = gap_file.getvalue().decode("utf-8")
                band_text = band_file.getvalue().decode("utf-8").splitlines()

                # 1. K-NOKTALARI OKUMA
                k_labels, k_coords = [], []
                for line in klabels_text[1:]: 
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            k_coords.append(float(parts[1]))
                            label = parts[0].upper()
                            k_labels.append(r"$\mathbf{\Gamma}$" if label == "GAMMA" else rf"$\mathbf{{{label}}}$")
                        except ValueError: 
                            continue

                # 2. BAND GAP VE İNDEKSLERİ OKUMA (Spin Uyumlu)
                gap_lines = gap_text.splitlines()
                band_gap = 0.0
                vbm_up, vbm_dn = 1, 1
                cbm_up, cbm_dn = 1, 1
                
                for line in gap_lines:
                    if "Band Gap (eV):" in line:
                        vals = line.split(":")[1].split()
                        band_gap = float(vals[-1]) # ISPIN=2'de sonuncu değer TOTAL gap'tir
                    elif "Band Indexes of VBM & CBM:" in line: # Eski/ISPIN=1 formatı
                        vals = line.split(":")[1].split()
                        vbm_up, cbm_up = int(vals[0]), int(vals[1])
                        vbm_dn, cbm_dn = vbm_up, cbm_up
                    elif "Band Index of VBM:" in line: # ISPIN=2 formatı
                        vals = line.split(":")[1].split()
                        vbm_up = int(vals[0])
                        vbm_dn = int(vals[1]) if len(vals) >= 3 else int(vals[0])
                    elif "Band Index of CBM:" in line: # ISPIN=2 formatı
                        vals = line.split(":")[1].split()
                        cbm_up = int(vals[0])
                        cbm_dn = int(vals[1]) if len(vals) >= 3 else int(vals[0])

                # 3. BAND VERİLERİ YÜKLEME
                bands_up = {}
                bands_dn = {}
                curr = None
                global_y_min, global_y_max = 999, -999
                
                for line in band_text:
                    if line.startswith("# Band-Index:"):
                        curr = int(line.split(":")[1].strip())
                        bands_up[curr] = []
                        bands_dn[curr] = []
                    elif line.strip() and not line.startswith("#") and curr is not None:
                        parts = line.split()
                        if not is_spin and len(parts) >= 2:
                            x, y = float(parts[0]), float(parts[1])
                            bands_up[curr].append([x, y])
                            global_y_min, global_y_max = min(global_y_min, y), max(global_y_max, y)
                        elif is_spin and len(parts) >= 3:
                            x, y_up, y_dn = float(parts[0]), float(parts[1]), float(parts[2])
                            bands_up[curr].append([x, y_up])
                            bands_dn[curr].append([x, y_dn])
                            global_y_min = min(global_y_min, y_up, y_dn)
                            global_y_max = max(global_y_max, y_up, y_dn)

                # VBM-CBM Verilerini Hazırlama (Spin Polarize Durumunda Global VBM/CBM Seçimi)
                vbm_data_up = np.array(bands_up[vbm_up])
                cbm_data_up = np.array(bands_up[cbm_up])
                
                if is_spin:
                    vbm_data_dn = np.array(bands_dn[vbm_dn])
                    cbm_data_dn = np.array(bands_dn[cbm_dn])
                    # Toplam Gap boyaması için en yüksek VBM ve en düşük CBM'i bul
                    vbm_data = vbm_data_up if np.max(vbm_data_up[:, 1]) > np.max(vbm_data_dn[:, 1]) else vbm_data_dn
                    cbm_data = cbm_data_up if np.min(cbm_data_up[:, 1]) < np.min(cbm_data_dn[:, 1]) else cbm_data_dn
                else:
                    vbm_data = vbm_data_up
                    cbm_data = cbm_data_up

                sort_idx_vbm = np.argsort(vbm_data[:, 0])
                sort_idx_cbm = np.argsort(cbm_data[:, 0])
                vbm_x_sorted, vbm_y_sorted = vbm_data[sort_idx_vbm, 0], vbm_data[sort_idx_vbm, 1]
                cbm_x_sorted, cbm_y_sorted = cbm_data[sort_idx_cbm, 0], cbm_data[sort_idx_cbm, 1]

                # Hafızaya Kaydet
                st.session_state.band_ready = True
                st.session_state.band_is_spin = is_spin
                st.session_state.band_data_up = bands_up
                st.session_state.band_data_dn = bands_dn
                st.session_state.band_kcoords = k_coords
                st.session_state.band_klabels = k_labels
                st.session_state.band_gap = band_gap
                st.session_state.band_vbm_x = vbm_x_sorted
                st.session_state.band_vbm_y = vbm_y_sorted
                st.session_state.band_cbm_x = cbm_x_sorted
                st.session_state.band_cbm_y = cbm_y_sorted
                
                # Otonom Sınırlar
                st.session_state.band_ymin = max(-10.0, np.floor(global_y_min))
                st.session_state.band_ymax = min(10.0, np.ceil(global_y_max))
                
                st.success("✅ Bant verileri başarıyla okundu ve hafızaya alındı!")

            except Exception as e:
                st.error(f"Grafik okuma hatası: {e}")

    # --- 3. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("band_ready", False):
        
        b_kcoords = st.session_state.band_kcoords
        b_klabels = st.session_state.band_klabels
        b_gap = st.session_state.band_gap
        def_ymin = st.session_state.band_ymin
        def_ymax = st.session_state.band_ymax
        is_spin_plot = st.session_state.band_is_spin
        
        def_mid_y = (np.max(st.session_state.band_vbm_y) + np.min(st.session_state.band_cbm_y)) / 2

        # 📐 EKSEN VE İNCE AYAR PANELİ
        with st.expander("📐 Eksen, Estetik ve Özel Metin Ayarları (Anlık Tepki)", expanded=True):
            st.markdown("**1. Y Ekseni Sınırları (Enerji, eV)**")
            cy1, cy2, cy3 = st.columns(3)
            with cy1: p_y_min = st.number_input("Y Min", value=float(def_ymin if def_ymin > -15 else -5.0), step=1.0)
            with cy2: p_y_max = st.number_input("Y Maks", value=float(def_ymax if def_ymax < 15 else 5.0), step=1.0)
            with cy3: p_y_step = st.number_input("Y Adımı (Tick)", value=2.0, step=0.5)

            st.markdown("**2. Renkler ve K-Noktası Çizgileri**")
            # Spin aktifse 5 sütun, değilse 4 sütun göster
            cc_all = st.columns(5) if is_spin_plot else st.columns(4)
            if is_spin_plot:
                with cc_all[0]: color_up = st.color_picker("Spin UP Rengi", value="#E74C3C")
                with cc_all[1]: color_dn = st.color_picker("Spin DOWN Rengi", value="#2980B9")
                with cc_all[2]: fill_color = st.color_picker("Band Gap Boyası", value="#2ecc71")
                with cc_all[3]: fermi_color = st.color_picker("Fermi Çizgisi", value="#000000")
                with cc_all[4]: k_alpha = st.slider("K-Çizgi Görünürlüğü", 0.0, 1.0, 0.4, 0.1)
            else:
                with cc_all[0]: band_color = st.color_picker("Bant Çizgisi Rengi", value="#000000")
                with cc_all[1]: fill_color = st.color_picker("Band Gap Boyası", value="#2ecc71")
                with cc_all[2]: fermi_color = st.color_picker("Fermi Çizgisi Rengi", value="#FF0000")
                with cc_all[3]: k_alpha = st.slider("K-Çizgi Görünürlüğü", 0.0, 1.0, 0.4, 0.1)

            st.markdown("**3. Metin Konumları**")
            cm1, cm2, cm3 = st.columns(3)
            with cm1: panel_label = st.text_input("Panel Etiketi (a, b)", value="(a)")
            with cm2: p_text_x = st.number_input("Gap Metni X Konumu", value=max(b_kcoords)/2, step=0.5)
            with cm3: p_text_y = st.number_input("Gap Metni Y Konumu", value=def_mid_y, step=0.5)

        # 🎨 ÇİZİM BÖLÜMÜ
        fig, ax = plt.subplots(figsize=(10, 8))

        # Bantları Çizme (Hafızadan)
        if is_spin_plot:
            for idx in st.session_state.band_data_up.keys():
                data_up = np.array(st.session_state.band_data_up[idx])
                data_dn = np.array(st.session_state.band_data_dn[idx])
                
                # Lejant için sadece ilk bandı etiketle
                lbl_up = r"Spin $\uparrow$" if idx == 1 else ""
                lbl_dn = r"Spin $\downarrow$" if idx == 1 else ""
                
                ax.plot(data_up[:, 0], data_up[:, 1], color=color_up, lw=1.5, zorder=2, label=lbl_up)
                ax.plot(data_dn[:, 0], data_dn[:, 1], color=color_dn, lw=1.5, ls='--', zorder=2, label=lbl_dn)
            
            # Spin polarize grafiğinde lejantı göster
            ax.legend(loc='upper right', frameon=True, fontsize=14, prop={'weight': 'bold'}).get_frame().set_linewidth(1.5)
        else:
            for idx, data_list in st.session_state.band_data_up.items():
                data = np.array(data_list)
                ax.plot(data[:, 0], data[:, 1], color=band_color, lw=2.0, zorder=2)

        # VBM-CBM Boyama (Gap varsa)
        if b_gap > 0.01:
            ax.fill_between(st.session_state.band_vbm_x, st.session_state.band_vbm_y, st.session_state.band_cbm_y, 
                            color=fill_color, alpha=0.3, zorder=1)

        # K-Noktası Dikey Çizgileri ve Fermi Seviyesi
        ax.axhline(0, color=fermi_color, ls='--', lw=2.0, zorder=3) 
        for c in b_kcoords: 
            ax.axvline(c, color='blue', lw=1.5, zorder=0, alpha=k_alpha) 

        # Band Gap Metni
        if b_gap > 0.01:
            ax.text(p_text_x, p_text_y, f"Band gap = {b_gap:.2f} eV", 
                    fontsize=16, fontweight='bold', ha='center', va='center', zorder=10,
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))

        # Eksen Formatlama
        ax.set_xticks(b_kcoords)
        ax.set_xticklabels(b_klabels, fontsize=14, fontweight='bold')
        ax.set_ylabel(r'$\mathbf{Energy\ (E - E_{F})\ (eV)}$', fontsize=18, labelpad=15)
        
        ax.set_ylim(p_y_min, p_y_max)
        ax.set_xlim(min(b_kcoords), max(b_kcoords))

        # Tick Ayarları
        ax.yaxis.set_major_locator(MultipleLocator(p_y_step))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.tick_params(axis='y', labelsize=14, direction='in', length=10, width=2.0, right=False)
        ax.tick_params(axis='y', which='minor', direction='in', length=5, width=1.5, right=False)
        ax.tick_params(axis='x', pad=15, length=0) # X ekseninde çentik (tick) olmaz

        for label in ax.get_yticklabels():
            label.set_fontweight('bold')

        # Panel Etiketi
        if panel_label.strip():
            ax.text(-0.05, 0.97, panel_label, transform=ax.transAxes, 
                    fontsize=18, fontweight='bold', ha='right', va='bottom')

        # Çerçeve
        for spine in ax.spines.values():
            spine.set_linewidth(2.5)

        plt.tight_layout()

        # Ekrana Basma
        st.pyplot(fig)
        
        # İndirme Butonu
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight', dpi=600)
        st.download_button(
            label="📥 Son Ayarlarla Bant Grafiğini İndir (PNG - 600 DPI)",
            data=buf.getvalue(),
            file_name="Band_Structure_Origin.png",
            mime="image/png"
        )
# ==========================================
# MODÜL 11: YOĞUNLUK DURUMLARI (DOS VE PDOS) - ORIGIN STYLE
# ==========================================
elif secim == "📊 Yoğunluk Durumları (DOS/PDOS)":
    st.header("Elektronik Yoğunluk Durumları (TDOS & PDOS)")
    st.markdown("Vaspkit'ten elde ettiğiniz `TDOS.dat` ve dilediğiniz sayıdaki PDOS dosyalarınızı yükleyerek makale kalitesinde, Origin tarzı interaktif grafikler oluşturun.")
    st.markdown("---")

    # --- 1. KULLANICI ARAYÜZÜ (Dosya Yükleme) ---
    is_spin = st.checkbox("Manyetik / Spin-Polarize (ISPIN=2) Hesaplama Mı?", value=False, help="Eğer hesaplamanızda Spin-Up ve Spin-Down durumları ayrıysa (3 sütunlu dosya), bunu işaretleyin. Grafikte Spin-Down durumları X ekseninin altına simetrik çizilecektir.")
    
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.subheader("1. Total DOS (Zorunlu)")
        tdos_file = st.file_uploader("TDOS.dat Yükle", type=["dat", "txt"], key="tdos")
        
        st.markdown("<br>", unsafe_allow_html=True)
        n_pdos = st.number_input("Kaç Adet PDOS (Partial DOS) Çizeceksiniz?", min_value=0, max_value=8, value=3, step=1)

    with c2:
        st.subheader("2. Partial DOS Dosyaları")
        temp_pdos_data = []
        
        if n_pdos > 0:
            pdos_defaults = [
                {"label": "K-s", "color": "#FBC02D", "ls": "-"},
                {"label": "Ti-3d", "color": "#1976D2", "ls": "-"},
                {"label": "H-1s", "color": "#D32F2F", "ls": "-"},
                {"label": "Ti-4s", "color": "#388E3C", "ls": "--"},
                {"label": "O-2p", "color": "#8E44AD", "ls": "-"},
                {"label": "C-2p", "color": "#E67E22", "ls": "-"}
            ]
            
            p_cols = st.columns(2)
            for i in range(n_pdos):
                with p_cols[i % 2]:
                    with st.expander(f"PDOS Yuvası {i+1}", expanded=True):
                        def_lbl = pdos_defaults[i]["label"] if i < len(pdos_defaults) else f"Atom-{i+1}"
                        def_col = pdos_defaults[i]["color"] if i < len(pdos_defaults) else "#000000"
                        def_ls = pdos_defaults[i]["ls"] if i < len(pdos_defaults) else "-"
                        
                        p_file = st.file_uploader(f"Dosya {i+1}", type=["dat", "txt"], key=f"pfile_{i}")
                        p_label = st.text_input(f"Etiket", value=def_lbl, key=f"plbl_{i}")
                        cc1, cc2 = st.columns(2)
                        with cc1: p_color = st.color_picker(f"Renk", value=def_col, key=f"pcol_{i}")
                        with cc2: p_ls = st.selectbox(f"Çizgi", ["-", "--", ":", "-."], index=["-", "--", ":", "-."].index(def_ls), key=f"pls_{i}")
                        
                        temp_pdos_data.append({
                            "file": p_file,
                            "label": rf"$\mathbf{{{p_label}}}$",
                            "color": p_color,
                            "ls": p_ls
                        })

    st.markdown("---")

    # --- 2. ADIM: AĞIR VERİ OKUMA VE HAFIZAYA ALMA ---
    if st.button("Verileri Oku ve Grafiği Hazırla", type="primary"):
        if tdos_file is None:
            st.error("HATA: Grafiği çizmek için mutlaka Total DOS (TDOS.dat) dosyasını yüklemelisiniz!")
        else:
            try:
                
                # TDOS Okuma
                tdos_file.seek(0)
                tdos_arr = np.loadtxt(tdos_file)
                
                # PDOS Okuma
                valid_pdos = []
                for p in temp_pdos_data:
                    if p["file"] is not None:
                        p["file"].seek(0)
                        p_arr = np.loadtxt(p["file"])
                        valid_pdos.append({"arr": p_arr, "label": p["label"], "color": p["color"], "ls": p["ls"]})
                
                # Otonom Y-Ekseni Sınırı Bulma (-4 ile 8 eV arasındaki en yüksek/düşük DOS değeri)
                mask = (tdos_arr[:, 0] >= -4.0) & (tdos_arr[:, 0] <= 8.0)
                if len(tdos_arr[mask]) > 0:
                    if is_spin and tdos_arr.shape[1] >= 3:
                        # Spin-down değerleri Vaspkit'te negatif verilir, bu yüzden mutlak değere (abs) bakarız
                        max_val = np.max(np.abs(tdos_arr[mask, 1:3]))
                    else:
                        max_val = np.max(tdos_arr[mask, 1])
                    auto_y_limit = float(np.ceil(max_val / 5) * 5)
                    if auto_y_limit == 0: auto_y_limit = 5.0
                else:
                    auto_y_limit = 20.0

                # Hafızaya Kaydet
                st.session_state.dos_ready = True
                st.session_state.dos_is_spin = is_spin
                st.session_state.dos_tdos = tdos_arr
                st.session_state.dos_pdos = valid_pdos
                st.session_state.dos_ymax = auto_y_limit
                
                st.success(f"✅ TDOS ve {len(valid_pdos)} adet PDOS verisi başarıyla hafızaya alındı!")

            except Exception as e:
                st.error(f"Veri okuma hatası: {e}. Dosya formatınızın doğru olduğundan emin olun.")

    # --- 3. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("dos_ready", False):

        tdos_arr = st.session_state.dos_tdos
        pdos_list = st.session_state.dos_pdos
        def_ymax = st.session_state.dos_ymax
        is_spin_plot = st.session_state.dos_is_spin

        # 📐 EKSEN VE İNCE AYAR PANELİ
        with st.expander("📐 Eksen, Lejant ve Estetik Ayarları (Anlık Tepki)", expanded=True):
            st.markdown("**1. X Ekseni (Enerji, eV)**")
            cx1, cx2, cx3 = st.columns(3)
            with cx1: p_x_min = st.number_input("X Min", value=-4.0, step=1.0)
            with cx2: p_x_max = st.number_input("X Maks", value=8.0, step=1.0)
            with cx3: p_x_step = st.number_input("X Adımı (Tick)", value=2.0, step=1.0)

            st.markdown("**2. Y Ekseni (States/eV)**")
            cy1, cy2, cy3 = st.columns(3)
            
            # Eğer spin polarize ise Y ekseni minimumu varsayılan olarak -Y_Maks olacak
            default_ymin = -def_ymax if is_spin_plot else 0.0
            
            with cy1: p_y_min = st.number_input("Y Min", value=float(default_ymin), step=5.0)
            with cy2: p_y_max = st.number_input("Y Maks", value=def_ymax, step=5.0)
            with cy3: p_y_step = st.number_input("Y Adımı (Tick)", value=float(np.ceil(def_ymax/4)), step=5.0)

            st.markdown("**3. Estetik ve Konumlandırma**")
            cm1, cm2 = st.columns(2)
            with cm1: p_leg_loc = st.selectbox("Lejant Konumu", ["best", "upper right", "upper left", "center right", "center left"], index=1)
            with cm2: p_fermi_color = st.color_picker("Fermi Çizgisi Rengi", value="#000000")

        # 🎨 ÇİZİM BÖLÜMÜ
        fig, ax = plt.subplots(figsize=(10, 7.5))

        # --- TDOS ÇİZİMİ ---
        ax.plot(tdos_arr[:,0], tdos_arr[:,1], color='dimgray', lw=3, alpha=0.4, label=r'$\mathbf{Total\ DOS}$')
        ax.fill_between(tdos_arr[:,0], 0, tdos_arr[:,1], color='gray', alpha=0.1, zorder=1)
        
        # Eğer Spin-Polarize ise 3. sütunu (Spin-DOWN) çiz
        if is_spin_plot and tdos_arr.shape[1] >= 3:
            ax.plot(tdos_arr[:,0], tdos_arr[:,2], color='dimgray', lw=3, alpha=0.4)
            ax.fill_between(tdos_arr[:,0], 0, tdos_arr[:,2], color='gray', alpha=0.1, zorder=1)

        # --- PDOS ÇİZİMİ ---
        for p in pdos_list:
            ax.plot(p["arr"][:,0], p["arr"][:,1], label=p["label"], color=p["color"], lw=3, ls=p["ls"], zorder=3)
            ax.fill_between(p["arr"][:,0], 0, p["arr"][:,1], color=p["color"], alpha=0.15, zorder=2)
            
            if is_spin_plot and p["arr"].shape[1] >= 3:
                ax.plot(p["arr"][:,0], p["arr"][:,2], color=p["color"], lw=3, ls=p["ls"], zorder=3)
                ax.fill_between(p["arr"][:,0], 0, p["arr"][:,2], color=p["color"], alpha=0.15, zorder=2)

        # --- Y=0 ÇİZGİSİ (Sadece Spin grafiğinde alt ve üstü ayırmak için) ---
        if is_spin_plot:
            ax.axhline(0, color='black', lw=1.0, ls='-', zorder=4)
            # Opsiyonel: Yukarı ve Aşağı okları eklemek
            ax.text(p_x_min + 0.5, p_y_max * 0.85, r'$\uparrow$', fontsize=28, color='black', fontweight='bold')
            ax.text(p_x_min + 0.5, p_y_min * 0.85, r'$\downarrow$', fontsize=28, color='black', fontweight='bold')

        # --- FERMİ SEVİYESİ VE ETİKETİ ---
        ax.axvline(x=0, color=p_fermi_color, linestyle=':', lw=3, zorder=5)
        # E_F metninin Y konumu spin aktifse merkeze yakın, değilse tepede olsun
        ef_y_pos = 0.90 if not is_spin_plot else 0.55
        ax.text(0.51, ef_y_pos, r'$\mathbf{E_F}$', transform=ax.transAxes, fontsize=16, fontweight='bold', color=p_fermi_color)

        # --- EKSEN VE TICK AYARLARI ---
        ax.set_xlim(p_x_min, p_x_max)
        ax.set_ylim(p_y_min, p_y_max)

        ax.xaxis.set_major_locator(MultipleLocator(p_x_step))
        ax.yaxis.set_major_locator(MultipleLocator(p_y_step))
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        
        ax.set_xlabel(r'$\mathbf{Energy\ -\ E_F\ (eV)}$', fontsize=18, labelpad=15)
        ax.set_ylabel(r'$\mathbf{Density\ of\ States\ (States\ /\ eV)}$', fontsize=18, labelpad=15)

        ax.tick_params(axis='both', which='major', labelsize=16, length=10, width=2.5, direction='in', pad=10, top=True, right=True)
        ax.tick_params(axis='both', which='minor', length=6, width=1.5, direction='in', top=True, right=True)
        
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight('bold')

        # Çerçeve
        for spine in ax.spines.values():
            spine.set_linewidth(2.5)

        # Lejant
        ax.legend(frameon=False, loc=p_leg_loc, fontsize=16, handletextpad=0.5, borderaxespad=1)

        plt.tight_layout()

        # Ekrana Basma
        st.pyplot(fig)
        
        # İndirme Butonu
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=600, bbox_inches='tight', pad_inches=0.05)
        st.download_button(
            label="📥 Son Ayarlarla DOS/PDOS Grafiğini İndir (PNG - 600 DPI)",
            data=buf.getvalue(),
            file_name="DOS_PDOS_Spin_Origin.png",
            mime="image/png"
        )
                # ==========================================
# MODÜL 12: OTONOM NEB YAPI OLUŞTURUCU
# ==========================================
elif secim == "🤖 Otonom NEB Yapı Oluşturucu":
    st.header("Otonom NEB IS/FS Jeneratörü (ASE Tabanlı)")
    st.markdown("Tek bir birim hücre (Birim `POSCAR`) yükleyin. Program otomatik olarak süper hücre oluşturur, alt katmanları dondurur (`F F F`) ve yüzeyden $H_2$ kopararak Başlangıç (IS) ve Bitiş (FS) POSCAR dosyalarınızı **Cartesian** formatta hazırlar.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("1. Girdi Dosyası")
        poscar_file = st.file_uploader("Birim Hücre POSCAR Yükle")
        
    with c2:
        st.subheader("2. Fiziksel Parametreler")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1: s_x = st.number_input("Süper X", value=1, min_value=1)
        with col_s2: s_y = st.number_input("Süper Y", value=3, min_value=1)
        with col_s3: s_z = st.number_input("Süper Z", value=1, min_value=1)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1: layer_tol = st.number_input("Katman Toleransı (Å)", value=0.8, step=0.1)
        with col_p2: desorp_dist = st.number_input("Desorpsiyon Mesafesi (Å)", value=4.0, step=0.5)

    st.markdown("---")

    if st.button("IS ve FS Yapılarını Oluştur", type="primary"):
        if poscar_file is None:
            st.error("Lütfen bir POSCAR dosyası yükleyin!")
        else:
            try:

                # Streamlit uploaded_file'ı geçici bir dosyaya yazıp ASE ile okumak en güvenlisidir
                with tempfile.NamedTemporaryFile(delete=False, mode="wb") as temp_in:
                    temp_in.write(poscar_file.getvalue())
                    temp_in_path = temp_in.name

                atoms = read(temp_in_path, format='vasp')
                st.write(f"✅ **Başarılı:** POSCAR okundu. Birim hücrede {len(atoms)} atom var.")

                # --- 1. SÜPER HÜCRE VE SIRALAMA ---
                original_symbols = atoms.get_chemical_symbols()
                unique_ordered_elements = []
                for sym in original_symbols:
                    if sym not in unique_ordered_elements:
                        unique_ordered_elements.append(sym)
                
                atoms_super = atoms.repeat((s_x, s_y, s_z))
                
                ordered_indices = []
                for sym in unique_ordered_elements:
                    ordered_indices.extend([atom.index for atom in atoms_super if atom.symbol == sym])
                
                atoms_super = atoms_super[ordered_indices]
                st.write(f"✅ **Süper Hücre Oluşturuldu:** ({s_x}x{s_y}x{s_z}) | Toplam {len(atoms_super)} atom.")

                # --- 2. KATMAN TANIMA VE DONDURMA ---
                z_coords = atoms_super.positions[:, 2]
                sorted_indices = np.argsort(z_coords)
                
                layers = []
                current_layer = [sorted_indices[0]]
                
                for i in range(1, len(sorted_indices)):
                    prev_idx = sorted_indices[i-1]
                    curr_idx = sorted_indices[i]
                    if z_coords[curr_idx] - z_coords[prev_idx] > layer_tol:
                        layers.append(current_layer)
                        current_layer = [curr_idx]
                    else:
                        current_layer.append(curr_idx)
                layers.append(current_layer)
                
                total_layers = len(layers)
                auto_freeze_count = total_layers // 2
                if auto_freeze_count == 0 and total_layers > 1: auto_freeze_count = 1
                    
                frozen_indices = []
                for i in range(auto_freeze_count):
                    frozen_indices.extend(layers[i])
                    
                constraint = FixAtoms(indices=frozen_indices)
                atoms_super.set_constraint(constraint)
                
                st.write(f"🛡️ **Zırhlama Başarılı:** Tespit edilen {total_layers} katmanın alt {auto_freeze_count} katmanı ({len(frozen_indices)} atom) kilitlendi (F F F).")

                # --- 3. IS_POSCAR OLUŞTURMA ---
                is_stream = io.StringIO()
                write(is_stream, atoms_super, format='vasp', direct=False)
                is_text = is_stream.getvalue()

                # --- 4. FS_POSCAR (H2 KOPARMA) OLUŞTURMA ---
                atoms_fs = atoms_super.copy()
                atoms_fs.set_constraint(constraint)

                h_indices = [i for i, atom in enumerate(atoms_fs) if atom.symbol == 'H']
                if len(h_indices) < 2:
                    st.error("HATA: Sistemde reaksiyona girecek en az 2 Hidrojen atomu bulunamadı!")
                    st.stop()
                    
                h_z_coords = atoms_fs.positions[h_indices, 2]
                max_h_z = np.max(h_z_coords)
                surface_h_indices = [i for i in h_indices if abs(atoms_fs.positions[i, 2] - max_h_z) < 1.5]

                min_dist = float('inf')
                closest_pair = None
                for idx1, idx2 in combinations(surface_h_indices, 2):
                    dist = atoms_fs.get_distance(idx1, idx2, mic=True)
                    if dist < min_dist:
                        min_dist = dist
                        closest_pair = (idx1, idx2)

                h1_idx, h2_idx = closest_pair
                st.write(f"🧪 **Reaksiyon Kuruldu:** Yüzeydeki en yakın iki hidrojen (Mesafe: {min_dist:.2f} Å) {desorp_dist} Å yukarı taşındı ve H2 (0.74 Å) bağı oluşturuldu.")

                c_axis_length = atoms_fs.get_cell()[2, 2]
                new_z_pos = max_h_z + desorp_dist
                if (c_axis_length - new_z_pos) < 2.0:
                    st.warning(f"⚠️ DİKKAT: H2 molekülü hücrenin üst vakum sınırına çok yaklaştı! Vakum boşluğunu artırmanız önerilir.")

                atoms_fs.positions[h1_idx, 2] += desorp_dist
                atoms_fs.positions[h2_idx, 2] += desorp_dist
                atoms_fs.set_distance(h1_idx, h2_idx, 0.74, fix=0.5, mic=True)

                fs_stream = io.StringIO()
                write(fs_stream, atoms_fs, format='vasp', direct=False)
                fs_text = fs_stream.getvalue()

                # Temizlik
                os.remove(temp_in_path)

                # --- 5. İNDİRME BUTONLARI ---
                st.success("Tüm işlemler kusursuz tamamlandı! Cartesian yapılarınızı indirebilirsiniz.")
                
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.download_button("📥 IS_POSCAR İndir", data=is_text, file_name="IS_POSCAR", mime="text/plain")
                with dl_col2:
                    st.download_button("📥 FS_POSCAR İndir", data=fs_text, file_name="FS_POSCAR", mime="text/plain")

            except Exception as e:
                st.error(f"Kritik Hata: İşlem sırasında bir sorun oluştu. Detay: {e}")
 # ==========================================
# MODÜL 13: NEB ENERJİ BARİYERİ (ENERGY PROFILE) - ORIGIN STYLE (SMART TS)
# ==========================================
elif secim == "⛰️ NEB Enerji Bariyeri (Energy Profile)":
    st.header("NEB Reaksiyon Yolu ve Enerji Profili")
    st.markdown("VASP NEB hesaplamanızdaki imajların toplam enerjilerini (eV) girerek makale kalitesinde bariyer grafiği oluşturun.")
    st.markdown("---")

    # --- 1. KULLANICI ARAYÜZÜ (Veri Girişi) ---
    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.subheader("1. İmaj Enerjileri (eV)")
        st.info("Virgülle veya alt alta enter ile ayırarak yazabilirsiniz (Sırasıyla: IS, Img1, Img2... FS).")
        default_energies = "-331.831500\n-331.946800\n-332.021000\n-331.855100\n-331.961700\n-331.995000\n-331.967400"
        energies_input = st.text_area("Enerji Değerleri", value=default_energies, height=150)

    with c2:
        st.subheader("2. Genel Ayarlar")
        plot_title = st.text_input("Grafik Başlığı", value="Hydrogen Diffusion Energy Profile")
        curve_color = st.color_picker("Eğri (Curve) Rengi", value="#000000")

    st.markdown("---")

    # --- 2. ADIM: AĞIR HESAPLAMA VE HAFIZAYA ALMA ---
    if st.button("Enerjileri Hesapla ve Grafiği Hazırla", type="primary"):
        try:

            # Girdiyi parse etme
            raw_energies = re.split(r'[,\n]+', energies_input)
            energies = np.array([float(x.strip()) for x in raw_energies if x.strip()])
            
            if len(energies) < 3:
                st.error("HATA: Grafiği çizmek için en az 3 enerji değeri (IS, TS, FS) girmelisiniz!")
            else:
                # Hesaplamalar
                relative_energies = energies - energies[0]
                x = np.arange(len(energies))
                
                # --- YENİ AKILLI TS VE BARİYER MOTORU ---
                # TS'yi sadece ara imajlar (IS ve FS hariç) arasında ara
                ts_index = np.argmax(relative_energies[1:-1]) + 1
                
                # TS'den önceki ve sonraki en düşük noktaları (Local Minima) bul
                min_before_ts = np.min(relative_energies[0:ts_index+1])
                min_after_ts = np.min(relative_energies[ts_index:])
                
                # Bariyerleri bu lokal minimumlara göre hesapla (W-eğrileri için kusursuz sonuç)
                Ea_f = relative_energies[ts_index] - min_before_ts
                Ea_b = relative_energies[ts_index] - min_after_ts
                Delta_E = relative_energies[-1] - relative_energies[0]

                # Yumuşatma (Akima)
                x_smooth = np.linspace(x.min(), x.max(), 500)
                spl = Akima1DInterpolator(x, relative_energies) 
                y_smooth = spl(x_smooth)

                # Otonom Y Sınırları
                auto_y_max = float(np.ceil((max(relative_energies) + 0.1) * 10) / 10) 
                auto_y_min = float(np.floor((min(relative_energies) - 0.1) * 10) / 10)
                if auto_y_max < 0.2: auto_y_max = 0.2
                
                # Hafızaya Kaydet
                st.session_state.neb_ready = True
                st.session_state.neb_energies = relative_energies
                st.session_state.neb_x = x
                st.session_state.neb_x_smooth = x_smooth
                st.session_state.neb_y_smooth = y_smooth
                st.session_state.neb_ts_idx = ts_index
                st.session_state.neb_metrics = {"Ea_f": Ea_f, "Ea_b": Ea_b, "Delta_E": Delta_E}
                
                st.session_state.neb_ymin = auto_y_min
                st.session_state.neb_ymax = auto_y_max
                st.session_state.neb_title = plot_title
                st.session_state.neb_color = curve_color
                
                st.success("✅ Enerjiler başarıyla hesaplandı ve enterpolasyon tamamlandı!")

        except Exception as e:
            st.error(f"Hesaplama hatası. Enerji değerlerinde harf olmadığından emin olun. Detay: {e}")

    # --- 3. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("neb_ready", False):
        
        # Otonom Sınırları Çek
        def_ymin = st.session_state.neb_ymin
        def_ymax = st.session_state.neb_ymax
        metrics = st.session_state.neb_metrics

        # 📐 EKSEN VE İNCE AYAR PANELİ
        with st.expander("📐 Eksen, Lejant ve Özel Metin Ayarları (Anlık Tepki)", expanded=True):
            st.markdown("**1. Y Ekseni Sınırları (Relative Energy, eV)**")
            cy1, cy2, cy3 = st.columns(3)
            with cy1: p_y_min = st.number_input("Y Min", value=float(def_ymin), step=0.1)
            with cy2: p_y_max = st.number_input("Y Maks", value=float(def_ymax), step=0.1)
            with cy3: p_y_step = st.number_input("Y Adımı (Tick)", value=0.1, step=0.05)

            st.markdown("**2. Bilgi Kutusu ve Lejant Konumu (0 ile 1 arası)**")
            ct1, ct2, ct3 = st.columns(3)
            with ct1: p_box_x = st.number_input("Kutu X Konumu", value=0.03, step=0.05)
            with ct2: p_box_y = st.number_input("Kutu Y Konumu", value=0.96, step=0.05)
            with ct3: p_leg_loc = st.selectbox("Lejant Konumu", ["best", "upper right", "upper left", "lower left", "lower right", "center right"], index=1)

        # 🎨 ÇİZİM BÖLÜMÜ

        fig, ax = plt.subplots(figsize=(10, 6.5))
        
        # Verileri Hafızadan Çekme
        x = st.session_state.neb_x
        relative_energies = st.session_state.neb_energies
        x_smooth = st.session_state.neb_x_smooth
        y_smooth = st.session_state.neb_y_smooth
        ts_index = st.session_state.neb_ts_idx

        # Sıfır Noktası Referans Çizgisi 
        ax.axhline(0, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, zorder=0)

        # Ana Eğri ve Veri Noktaları
        ax.plot(x_smooth, y_smooth, color=st.session_state.neb_color, linewidth=3.0, zorder=1)
        ax.scatter(x, relative_energies, color='white', edgecolor='black', s=80, linewidth=2.0, zorder=2)

        # Özel Durum İşaretçileri (IS, TS, FS)
        ax.scatter(0, relative_energies[0], color='#2980b9', s=160, marker='s', label='Initial State (IS)', zorder=3)
        ax.scatter(ts_index, relative_energies[ts_index], color='#e74c3c', s=160, marker='s', label='Transition State (TS)', zorder=3)
        ax.scatter(len(relative_energies)-1, relative_energies[-1], color='#27ae60', s=160, marker='s', label='Final State (FS)', zorder=3)

        # Eksen Sınırları ve Tickleri
        ax.set_ylim(p_y_min, p_y_max)
        ax.set_xlim(-0.4, len(relative_energies) - 0.6)
        
        ax.yaxis.set_major_locator(MultipleLocator(p_y_step))
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.tick_params(axis='both', which='major', direction='in', length=8, width=2.0, labelsize=14)
        ax.tick_params(axis='y', which='minor', direction='in', length=4, width=1.5)

        for spine in ax.spines.values():
            spine.set_linewidth(2.0)
            spine.set_edgecolor('black')

        ax.set_xlabel('Reaction Coordinate', fontsize=16, fontweight='bold', labelpad=12)
        ax.set_ylabel('Relative Energy (eV)', fontsize=16, fontweight='bold', labelpad=12)

        # X Ekseni Etiketleri (IS, Img, TS, FS)
        labels = ['IS' if i==0 else 'FS' if i==len(relative_energies)-1 else 'TS' if i==ts_index else f'Img {i}' for i in range(len(relative_energies))]
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=14, fontweight='bold')

        # Bilgi Kutusu 
        info_box = (
            f"Kinetic Barrier ($E_a$): {metrics['Ea_f']:.4f} eV\n"
            f"Reverse Barrier: {metrics['Ea_b']:.4f} eV\n"
            f"Thermodynamic $\\Delta E$: {metrics['Delta_E']:.4f} eV"
        )
        ax.text(p_box_x, p_box_y, info_box, transform=ax.transAxes, 
                fontsize=13, fontweight='bold', verticalalignment='top',
                bbox=dict(boxstyle='square,pad=0.5', facecolor='white', edgecolor='black', linewidth=1.5))

        # Lejant ve Başlık
        ax.legend(loc=p_leg_loc, fontsize=13, frameon=True, edgecolor='black', fancybox=False, shadow=False).get_frame().set_linewidth(1.5)
        ax.set_title(st.session_state.neb_title, fontsize=18, fontweight='bold', pad=15)

        plt.tight_layout()

        # --- EKRANA METRİK VE GRAFİK BASMA ---
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Aktivasyon Bariyeri (Ea)", f"{metrics['Ea_f']:.4f} eV")
        col_m2.metric("Ters Bariyer", f"{metrics['Ea_b']:.4f} eV")
        col_m3.metric("Reaksiyon Enerjisi (ΔE)", f"{metrics['Delta_E']:.4f} eV")

        st.pyplot(fig)
        
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=600, bbox_inches='tight')
        st.download_button(
            label="📥 Son Ayarlarla NEB Grafiğini İndir (PNG)",
            data=buf.getvalue(),
            file_name="NEB_Energy_Profile_Origin.png",
            mime="image/png"
        )
            # ==========================================
# MODÜL 14: MAKALE PANELİ (GÖRSEL BİRLEŞTİRİCİ)
# ==========================================
elif secim == "🖼️ Makale Paneli (Görsel Birleştirici)":
    st.header("Bilimsel Makale Paneli Oluşturucu (Figure Montage)")
    st.markdown("Farklı modüllerden elde ettiğiniz (veya kendi çizdiğiniz) grafikleri buraya yükleyerek, (a), (b), (c) etiketli tek bir yüksek çözünürlüklü makale paneli haline getirin.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("1. Görselleri Yükle")
        uploaded_images = st.file_uploader("Birleştirilecek Görselleri Seçin (Birden fazla seçebilirsiniz)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        st.info(f"Şu an {len(uploaded_images)} görsel yüklendi.")

    with c2:
        st.subheader("2. Panel Ayarları")
        col_sayisi = st.number_input("Sütun Sayısı (Yan Yana Kaç Görsel Olsun?)", min_value=1, value=2, step=1)
        
        c2_1, c2_2 = st.columns(2)
        with c2_1:
            bosluk = st.number_input("Görseller Arası Boşluk (px)", min_value=0, value=100, step=20)
        with c2_2:
            etiket_ekle = st.checkbox("Sol Üste (a), (b) Etiketleri Ekle", value=True)
            
        etiket_boyutu = st.slider("Etiket Boyutu (Otomatik ölçeğe göre %)", min_value=1, max_value=15, value=6)

    st.markdown("---")

    if st.button("Görselleri Birleştir ve Paneli Oluştur", type="primary"):
        if len(uploaded_images) == 0:
            st.error("HATA: Lütfen birleştirmek için en az 1 görsel yükleyin!")
        else:
            try:

                # Yüklenen görselleri PIL Image objelerine dönüştür
                images = [Image.open(img).convert("RGB") for img in uploaded_images]
                
                # Izgara (Grid) hesaplamaları
                satir_sayisi = math.ceil(len(images) / col_sayisi)
                
                # Tüm görselleri en büyüğünün boyutuna göre merkezlemek için max boyutları bul
                max_w = max(img.width for img in images)
                max_h = max(img.height for img in images)
                
                # Ana Tuvalin (Canvas) Boyutunu Hesapla
                canvas_w = (col_sayisi * max_w) + ((col_sayisi - 1) * bosluk)
                canvas_h = (satir_sayisi * max_h) + ((satir_sayisi - 1) * bosluk)
                
                # Beyaz arka planlı tuvali oluştur
                canvas = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
                draw = ImageDraw.Draw(canvas)

                # Yazı tipi ayarı (Sistemde yoksa varsayılana döner ama boyutu ayarlamaya çalışırız)
                font_size = int(max_h * (etiket_boyutu / 100))
                try:
                    # Windows için
                    font = ImageFont.truetype("timesbd.ttf", font_size) # Times New Roman Bold
                except IOError:
                    try:
                        # Linux/Mac için genel bir font
                        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
                    except IOError:
                        # Font bulunamazsa varsayılan
                        font = ImageFont.load_default()
                        st.warning("Sistemde Times New Roman fontu bulunamadı, varsayılan font kullanılıyor. Çıktıda yazılar küçük görünebilir.")

                # Görselleri Tuvale Yerleştirme Döngüsü
                for idx, img in enumerate(images):
                    satir = idx // col_sayisi
                    sutun = idx % col_sayisi
                    
                    # Hücrenin sol üst koordinatları
                    x = sutun * (max_w + bosluk)
                    y = satir * (max_h + bosluk)
                    
                    # Görseli hücrenin tam ortasına yerleştir
                    offset_x = x + (max_w - img.width) // 2
                    offset_y = y + (max_h - img.height) // 2
                    
                    canvas.paste(img, (offset_x, offset_y))
                    
                    # Etiket ekleme (a, b, c...)
                    if etiket_ekle:
                        harf = chr(97 + idx) # 97 = 'a' ASCII kodu
                        etiket_metni = f"({harf})"
                        
                        # Etiketi biraz içeriye (marjin) yazdır
                        text_x = x + int(max_w * 0.01)
                        text_y = y + int(max_h * 0.01)
                        
                        # Siyah metin
                        draw.text((text_x, text_y), etiket_metni, fill=(0, 0, 0), font=font)

                # --- EKRANA BASMA VE İNDİRME ---
                st.success("Makale Paneli başarıyla oluşturuldu!")
                
                # Streamlit ekranında göstermek için tuvali biraz küçült (Orijinali devasa olabilir)
                st.image(canvas, caption=f"{satir_sayisi}x{col_sayisi} Makale Paneli", use_column_width=True)
                
                # 600 DPI Kaydetme
                buf = io.BytesIO()
                canvas.save(buf, format="JPEG", dpi=(600, 600), quality=95, subsampling=0)
                
                st.download_button(
                    label="📥 Birleşik Paneli İndir (600 DPI - Makale Kalitesi)",
                    data=buf.getvalue(),
                    file_name="Article_Panel_600DPI.jpg",
                    mime="image/jpeg"
                )

            except Exception as e:
                st.error(f"Görseller birleştirilirken bir hata oluştu: {e}")
                # ==========================================
# MODÜL 15: HİDRÜR ADAY JENERATÖRÜ (PYMATGEN)
# ==========================================
elif secim == "🧪 Hidrür Aday Jeneratörü":
    st.header("Kimyasal Hidrür Aday Jeneratörü")
    st.markdown("Pymatgen veritabanını kullanarak, belirlediğiniz element sistemi için yük denkliğine (charge balance) dayalı, teorik olarak sentezlenebilir tüm hidrür formüllerini ve gravimetrik kapasitelerini hesaplayın.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    c1, c2, c3 = st.columns(3)
    with c1:
        input_str = st.text_input("Element Sistemi (H Dahil)", "Mg, Ti, H", help="Aralarına virgül koyarak elementleri yazın.")
    with c2:
        max_cat = st.number_input("Maks. Katyon Katsayısı", min_value=1, max_value=20, value=10)
    with c3:
        max_h = st.number_input("Maks. Hidrojen Katsayısı", min_value=1, max_value=100, value=25)

    st.markdown("---")

    if st.button("Teorik Adayları Hesapla", type="primary"):
        try:

            # Manuel ayar listesi
            MANUAL_OXIDATION_STATES = {
                'Mg': [2], 'Na': [1], 'K': [1], 'Li': [1]
            }

            def find_candidate_hydrides_dynamic(element_symbols, max_cation_stoch=10, max_H_stoch=25):
                log_messages = []
                cation_symbols = [sym for sym in element_symbols if sym != 'H']
                h_charge = -1
                
                log_messages.append(f"--- Sistem Taranıyor: {'-'.join(cation_symbols)}-H ---")
                
                cation_data = []
                for sym in cation_symbols:
                    if sym in MANUAL_OXIDATION_STATES:
                        states = MANUAL_OXIDATION_STATES[sym]
                        log_messages.append(f"   (Manuel ayar kullanılıyor: {sym} -> {states})")
                    else:
                        try:
                            element = Element(sym)
                            states = [s for s in element.oxidation_states if s > 0]
                            log_messages.append(f"   (Pymatgen varsayılanı kullanılıyor: {sym} -> {states})")
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
                stoch_combinations = itertools.product(stoch_range, repeat=len(cation_data))
                
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

            # Girdiyi işle
            all_elements = sorted(list(set([e.strip().capitalize() for e in input_str.split(',') if e.strip()])))
            
            # Hata Kontrolleri
            if 'H' not in all_elements:
                st.error("HATA: Sisteme mutlaka 'H' (Hidrojen) elementini dahil etmelisiniz.")
            elif not 2 <= len(all_elements) <= 5:
                st.error(f"HATA: 'H' dahil 2 ile 5 arası element girilmelidir. Siz {len(all_elements)} adet girdiniz.")
            else:
                with st.spinner(f"{'-'.join(all_elements)} sistemi veritabanında taranıyor..."):
                    found_set, log_messages = find_candidate_hydrides_dynamic(
                        all_elements, max_cation_stoch=max_cat, max_H_stoch=max_h
                    )
                
                if found_set:
                    st.success(f"Tarama Tamamlandı! Yük denkliği sağlanan toplam **{len(found_set)} benzersiz formül** bulundu.")
                    
                    df = pd.DataFrame(list(found_set), columns=["Bileşik Formülü", "Gravimetrik Kapasite (wt. % H)"])
                    df_sorted = df.sort_values(by="Gravimetrik Kapasite (wt. % H)", ascending=False).reset_index(drop=True)
                    
                    # Şık Tablo Görünümü
                    st.dataframe(df_sorted.style.format({"Gravimetrik Kapasite (wt. % H)": "{:.3f} %"}), use_container_width=True)
                    
                    # CSV İndirme Butonu
                    csv = df_sorted.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Sonuçları Excel/CSV Olarak İndir",
                        data=csv,
                        file_name=f"{''.join(all_elements)}_candidates.csv",
                        mime="text/csv",
                    )
                else:
                    st.warning("Bu parametrelerde uygun bir hidrür formülü bulunamadı.")
                
                # Logları göster
                with st.expander("Hesaplama ve Veritabanı Günlüğünü Göster (Log)"):
                    st.code('\n'.join(log_messages))

        except ImportError:
            st.error("Bu modül 'pymatgen' kütüphanesini gerektirir. Lütfen terminalinize gidip şu komutu çalıştırın: `pip install pymatgen`")
        except Exception as e:
            st.error(f"Beklenmeyen bir hata oluştu: {e}")
            # ==========================================
# MODÜL 16: FONON VE PHONOPY OTOMASYONU
# ==========================================
elif secim == "🎶 Fonon ve Phonopy (Otomasyon)":
    st.header("Phonopy ile Fonon Hesaplama Otomasyonu")
    st.markdown("Birim hücreniz için Phonopy süper hücrelerini üreten, yüksek hassasiyetli `INCAR` dosyasını otomatik yazan ve tüm işleri TRUBA kuyruğuna (SLURM) gönderen Bash betiğinizi (Script) hazırlayın.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("1. Süper Hücre Boyutları")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1: dim_x = st.number_input("X Boyutu", value=2, min_value=1)
        with col_s2: dim_y = st.number_input("Y Boyutu", value=2, min_value=1)
        with col_s3: dim_z = st.number_input("Z Boyutu", value=2, min_value=1)
        
        slurm_name = st.text_input("SLURM Dosyası Adı", value="vasp.slurm")

    with c2:
        st.subheader("2. INCAR Hassasiyet Ayarları")
        encut_val = st.number_input("ENCUT (eV)", value=550, step=10)
        ediff_val = st.text_input("EDIFF", value="1E-8")
        ismear_val = st.selectbox("ISMEAR (Yalıtkan: 0, Metal: 1)", [0, 1, 2, -5], index=0)

    st.markdown("---")
    st.subheader("3. Üretilen Çalıştırma Betiği (run_phonopy.sh)")

    # BASH SCRIPT METNİ (ISYM = 0 düzeltmesiyle birlikte)
    bash_script = f"""#!/bin/bash

# ==============================================================================
# PHONOPY OTOMASYON BETIGI (VASP Kontrol Merkezi tarafindan uretilmistir)
# ==============================================================================

SUPERCELL_DIM="{dim_x} {dim_y} {dim_z}"
SLURM_FILE="{slurm_name}"

# 1. Ortam ve Dosya Kontrolleri
if ! command -v phonopy &> /dev/null; then
    echo "HATA: phonopy komutu bulunamadi. Lutfen 'module load' veya conda environment'inizi aktif edin."
    exit 1
fi

if [ ! -f "\$SLURM_FILE" ]; then
    echo "HATA: \$SLURM_FILE dosyasi bu dizinde yok!"
    exit 1
fi

if [ ! -f "POSCAR" ]; then
    echo "HATA: POSCAR dosyasi bu dizinde yok!"
    exit 1
fi

# 2. Fonon ICIN Ozel INCAR Olusturma
echo "Ultra-hassas INCAR dosyasi olusturuluyor..."
cat > INCAR << EOF
SYSTEM = Phonon Single Point Calculation
PREC   = Accurate
ADDGRID= .TRUE.
LREAL  = .FALSE.
ENCUT  = {encut_val}
EDIFF  = {ediff_val}
ISMEAR = {ismear_val}
SIGMA  = 0.05
ISYM   = 0         ! KRITIK: Phonopy icin simetri KESINLIKLE kapali olmali
IBRION = -1        ! Atomlar hareket etmeyecek (Sadece single point)
NSW    = 0
LWAVE  = .FALSE.
LCHARG = .FALSE.
NELM   = 220
EOF

# 3. Süper Hücreleri Üretme
echo "Süper hücreler üretiliyor (\$SUPERCELL_DIM)..."
phonopy -d --dim="\$SUPERCELL_DIM" -c POSCAR

# 4. Klasörleri Acma, Dosyalari Kopyalama ve Is Gönderme
echo "Klasörler hazirlaniyor ve isler gonderiliyor..."

count=0
for f in POSCAR-*[0-9]*; do
    
    id=${{f#POSCAR-}}
    dir="disp-\$id"
    
    if [ -d "\$dir" ]; then rm -rf "\$dir"; fi
    mkdir "\$dir"
    
    cp "\$f" "\$dir/POSCAR"
    cp INCAR POTCAR KPOINTS "\$SLURM_FILE" "\$dir/"
    
    cd "\$dir" || exit
    echo "\$dir klasorunde is gonderiliyor..."
    sbatch "\$SLURM_FILE"
    cd ..
    
    count=\$((count+1))
done

echo "------------------------------------------------"
echo "BASARILI: TOPLAM \$count adet is TRUBA kuyruguna gonderildi."
echo "Islerin durumunu 'squeue' komutu ile takip edebilirsiniz."
"""

    # Kodu Ekranda Göster
    st.code(bash_script, language="bash")

    # İndirme Butonu
    st.download_button(
        label="📥 Çalıştırma Betiğini İndir (run_phonopy.sh)",
        data=bash_script,
        file_name="run_phonopy.sh",
        mime="text/x-shellscript"
    )
    
    st.info("💡 **Nasıl Kullanılır?** Bu dosyayı TRUBA'da `POSCAR`, `POTCAR`, `KPOINTS` ve `vasp.slurm` dosyalarınızın olduğu klasöre atın. Terminalden `chmod +x run_phonopy.sh` yazarak yetki verin ve `./run_phonopy.sh` yazarak çalıştırın.")
    # ==========================================
# MODÜL 17: AIMD ÇOKLU SICAKLIK OTOMASYONU
# ==========================================
elif secim == "🏃‍♂️ AIMD Çoklu Sıcaklık (Otomasyon)":
    st.header("AIMD Çoklu Sıcaklık İş Akışı Otomasyonu")
    st.markdown("Belirlediğiniz sıcaklıklar için otomatik olarak klasör açan, `INCAR`, `KPOINTS` ve `SLURM` dosyalarını oluşturan ve işleri tek tıkla TRUBA'ya gönderen akıllı Bash betiğinizi hazırlayın.")
    st.markdown("---")

    # --- KRİTİK BİLİMSEL UYARILAR ---
    st.warning("**⚠️ KRİTİK SÜPER HÜCRE UYARISI:** AIMD hesaplamaları ASLA birim (ilkel) hücreyle yapılmaz! Birim hücredeki atom, periyodik sınır koşulları yüzünden kendi yansımasıyla (self-interaction) etkileşime girer. Hücrenizin her yönde **en az 10 Å** büyüklüğünde (Süper Hücre) olduğundan emin olun.")
    
    st.info("**💡 KÜTLE (POMASS) UYARISI:** Hidrojen (kütle: 1.0) çok hızlı titreştiği için MD adımını (POTIM) 0.5 fs veya altına düşürmeyi zorunlu kılar. Ancak Hidrojenin kütlesini Döteryum gibi **2.00** veya Trityum gibi **3.00** yaparsanız, `POTIM = 1.0` veya `1.5` kullanarak simülasyonu 2 kat daha hızlı bitirebilirsiniz (Enerji korunduğu sürece termodinamik/yapısal özellikler değişmez).")

    st.markdown("---")

    # --- KONTROL PANELİ ---
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("1. Fiziksel Parametreler")
        temps = st.text_input("Sıcaklıklar (K) - Boşlukla Ayırın", value="300 450 600 750")
        pomass = st.text_input("POMASS (POSCAR'daki Sıraya Göre)", value="39.098 47.867 2.00", help="Örn: K Ti H için. H kütlesini 2.00 yapmak POTIM'i 1.0 kullanmanızı sağlar.")
        nsw = st.number_input("Adım Sayısı (NSW)", value=20000, step=1000)
        potim = st.number_input("Zaman Adımı (POTIM, fs)", value=1.0, step=0.5)

    with c2:
        st.subheader("2. TRUBA (SLURM) Ayarları")
        email = st.text_input("E-Posta Adresi", value="s.yamcicier@gmail.com")
        queue = st.text_input("Kuyruk (Partition)", value="hamsi")
        cores = st.number_input("Çekirdek Sayısı (-n)", value=56, step=8)
        vasp_path = st.text_input("VASP Executable Yolu", value="/arf/home/syamcicier/derleme/vasp.6.3.0/bin/vasp_std")

    st.markdown("---")

    # --- BASH SCRIPT METNİ ---
    bash_script = f"""#!/bin/bash

# ==============================================================================
# AIMD COKLU SICAKLIK OTOMASYONU (VASP Kontrol Merkezi)
# ==============================================================================

# --- 1. SICAKLIK LISTESI ---
TEMPS="{temps}"

# --- 2. GUVENLIK KONTROLLERİ ---
if [ ! -f "POSCAR" ] || [ ! -f "POTCAR" ]; then
    echo "HATA: Ana dizinde POSCAR veya POTCAR bulunamadi!"
    echo "Lutfen super hucre POSCAR'inizi ve ona uygun POTCAR'inizi bu dizine koyun."
    exit 1
fi

echo "DIKKAT: POSCAR'in bir super hucre oldugundan (min 10x10x10 A) emin olun."
echo "DIKKAT: POMASS siralamasinin POTCAR ile ayni oldugunu dogrulayin."
sleep 3

# --- 3. OTOMASYON DONGUSU ---
for T in \$TEMPS; do
    echo ">>> \$T K icin klasor ve dosyalar hazirlaniyor..."
    DIR="T_\$T"
    mkdir -p \$DIR

    # A. KPOINTS DOSYASINI OLUSTUR
    cat <<EOF > \$DIR/KPOINTS
K-Points for AIMD
 0
Gamma
 1  1  1
 0  0  0
EOF

    # B. INCAR DOSYASINI OLUSTUR (Sicakliga Gore)
    cat <<EOF > \$DIR/INCAR
SYSTEM = AIMD_\$T
# --- MD AYARLARI ---
IBRION = 0
NSW    = {nsw}
POTIM  = {potim}
TEBEG  = \$T
TEEND  = \$T
SMASS  = 0
MDALGO = 2

# --- KUTLE (POMASS) ---
POMASS = {pomass}

# --- ELEKTRONIK ---
ISMEAR = 0
SIGMA  = 0.1
ALGO   = Fast
PREC   = Normal
MAXMIX = 40
ISYM   = 0
LREAL  = Auto
ENCUT  = 400
EDIFF  = 1E-4
NELMIN = 4
LWAVE  = .FALSE.
LCHARG = .FALSE.
NCORE  = 4
EOF

    # C. SLURM (vasp.sh) DOSYASINI OLUSTUR
    cat <<EOF > \$DIR/vasp.sh
#!/bin/bash
#SBATCH -p {queue}
#SBATCH -J vasp_\$T
#SBATCH -N 1
#SBATCH -n {cores}
#SBATCH -c 1
#SBATCH -C weka
#SBATCH --time=3-00:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --mail-user={email}
#SBATCH --mail-type=BEGIN

export OMP_NUM_THREADS=1
module purge 
module load comp/oneapi/2022 

mpirun {vasp_path}
exit
EOF

    # D. POSCAR ve POTCAR DOSYALARINI KOPYALA
    cp POSCAR POTCAR \$DIR/

    # E. ISI KUYRUGA GONDER
    cd \$DIR
    sbatch vasp.sh
    echo ">>> \$T K isi basariyla gonderildi."
    cd ..

    echo "------------------------------------------"
done

echo "TUM AIMD IS AKISI KURULDU VE BASLATILDI!"
"""

    st.subheader("3. Üretilen Çalıştırma Betiği (run_aimd.sh)")
    st.code(bash_script, language="bash")

    st.download_button(
        label="📥 AIMD Otomasyon Betiğini İndir (run_aimd.sh)",
        data=bash_script,
        file_name="run_aimd.sh",
        mime="text/x-shellscript"
    )
    
    st.success("💡 **Kullanım:** İndirdiğiniz `run_aimd.sh` dosyasını `POSCAR` ve `POTCAR` ile aynı klasöre koyun. Terminalden `chmod +x run_aimd.sh` ile yetki verip `./run_aimd.sh` yazarak 4 farklı sıcaklık işini aynı anda TRUBA'ya gönderebilirsiniz.")
    # ==========================================
# MODÜL 18: ELASTİK SABİTLER VE MEKANİK (IBRION=6)
# ==========================================
elif secim == "🧲 Elastik Sabitler (IBRION=6)":
    st.header("Elastik Sabitler (Mekanik Özellikler) INCAR Jeneratörü")
    st.markdown("Malzemenizin Bulk (B), Shear (G) ve Young (E) modüllerini hesaplamak için gereken DFPT (IBRION=6) tabanlı, yüksek hassasiyetli INCAR dosyasını oluşturun.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Sistem ve Fiziksel Ayarlar")
        system_name = st.text_input("Sistem Adı (SYSTEM)", value="K2TiH5 Elastic")
        isif_val = st.selectbox("ISIF (Hücre Esnetme Yöntemi)", [3, 5, 2], index=1, help="ISIF=3 tam elastik tensör için standarttır. ISIF=5 hücre şeklini değiştirir ama hacmi sabit tutar.")
        encut = st.number_input("ENCUT (eV)", value=550, step=10)
        ispin = st.selectbox("ISPIN (Manyetizma)", [1, 2], index=1)
        
        if ispin == 2:
            magmom = st.text_input("MAGMOM", value="2*0.0 1*1.0 5*0.0")
        else:
            magmom = None

    with col2:
        st.subheader("2. Hassasiyet ve Yakınsama")
        ediff = st.text_input("EDIFF (Elektronik)", value="1E-8", help="Elastik sabitler için en az 1E-8 olmalıdır.")
        ediffg = st.text_input("EDIFFG (İyonik)", value="-1E-6")
        prec_val = st.selectbox("PREC (Hassasiyet)", ["High", "Accurate", "Normal"], index=0)
        ivdw_val = st.selectbox("IVDW (vdW Düzeltmesi)", [11, 12, 10, 0], index=0, help="11: DFT-D3 (Grimme), 12: DFT-D3(BJ), 10: DFT-D2, 0: Kapalı")

    st.markdown("---")
    st.subheader("3. Üretilen INCAR Dosyası")

    # INCAR Metnini Oluştur
    incar_lines = [
        f"SYSTEM = {system_name}",
        "IBRION = 6        ! Elastik sabitleri hesaplama modu",
        f"ISIF   = {isif_val}        ! Hücre esnetme parametresi",
        "NSW    = 1        ! IBRION=6 icin minimum adım",
        "",
        "# --- HASSASİYET VE YAKINSAMA ---",
        f"PREC   = {prec_val}",
        f"ENCUT  = {encut}",
        f"EDIFF  = {ediff}",
        f"EDIFFG = {ediffg}",
        "ADDGRID= .TRUE.   ! PAW potansiyelleri icin ekstra grid",
        "LREAL  = .FALSE.  ! Projeksiyon reciprocal space'te (En hassas)",
        "",
        "# --- ELEKTRONİK VE MANYETİK ---",
        "ISMEAR = 0        ! Yalıtkan/Yarı İletken için Gaussian",
        "SIGMA  = 0.05",
        f"ISPIN  = {ispin}"
    ]

    if magmom:
        incar_lines.append(f"MAGMOM = {magmom}")

    incar_lines.extend([
        "",
        "# --- VDW DÜZELTMESİ VE ÇIKTI ---",
        f"IVDW   = {ivdw_val}",
        "ICHARG = 1        ! CHGCAR okunsun (Önceki optimizasyondan)",
        "LWAVE  = .FALSE.",
        "LCHARG = .FALSE."
    ])

    incar_text = "\n".join(incar_lines)
    
    # Ekranda Göster
    st.code(incar_text, language="bash")
    
    # İndirme ve Bilgi
    st.download_button(
        label="📥 INCAR Dosyasını İndir",
        data=incar_text,
        file_name="INCAR_Elastic",
        mime="text/plain"
    )

    st.info("💡 **Analiz İpucu:** VASP hesaplaması bittikten sonra sonuçları elde etmek için `OUTCAR` dosyasına bakabilirsiniz. Eğer Vaspkit kuruluysa, terminalde **`vaspkit -task 201`** komutunu çalıştırarak tüm elastik tensörü (C11, C12, C44 vb.), Bulk/Shear modüllerini ve malzemenin sünek/gevrek (ductile/brittle) analizini anında tablo olarak çekebilirsiniz.")
    # ==========================================
# MODÜL 19: HSE06 BANT YAPISI OTOMASYONU
# ==========================================
elif secim == "💎 HSE06 Bant Yapısı (Otomasyon)":
    st.header("HSE06 Hibrit Fonksiyonel Bant Yapısı İş Akışı")
    st.markdown("Geometri optimizasyonundan çıkan yapınızı primitive hücreye çeviren, k-yolunu oluşturan ve HSE06 için ağırlıksız (zero-weight) KPOINTS dosyasını Vaspkit ile otonom olarak hazırlayan araçtır.")
    st.markdown("---")

    # --- KRİTİK UYARI ---
    st.warning("**⚠️ İŞLEME BAŞLAMADAN ÖNCE DİKKAT:** Geometri optimizasyonundan elde ettiğiniz `CONTCAR` dosyasını, bu hesabı yapacağınız klasöre **`POSCAR`** adıyla kopyalamayı kesinlikle unutmayın! Aksi takdirde Vaspkit çalışmayacaktır.")
    
    st.info("💡 **HSE06 Mantığı:** HSE hesaplamalarında `ISTART = 1` ve `ICHARG = 1` kullanıldığı için, bu klasörde standart bir PBE-SCF adımından elde edilmiş `WAVECAR` ve `CHGCAR` dosyalarının da bulunması hesaplamayı inanılmaz derecede hızlandırır.")

    st.markdown("---")

    # --- KONTROL PANELİ ---
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("1. Sistem ve Manyetizma")
        system_name = st.text_input("Sistem Adı", value="Hybrid_Functional_BAND")
        ispin = st.selectbox("ISPIN (Manyetizma)", [1, 2], index=1)
        if ispin == 2:
            magmom = st.text_input("MAGMOM", value="2*0.0 1*1.0 5*0.0")
        else:
            magmom = None

    with c2:
        st.subheader("2. Çözünürlük ve K-Noktası")
        encut = st.number_input("ENCUT (eV)", value=600, step=50)
        k_spacing = st.number_input("K-Spacing (Vaspkit 251 için)", value=0.05, step=0.01, format="%.2f")

    st.markdown("---")

    # --- BASH SCRIPT (VASPKIT OTOMASYONU) ---
    bash_script = f"""#!/bin/bash
# =======================================================
# VASPKIT HSE06 OTOMASYON BETIGI
# =======================================================

echo "1. Primitive Hucre Olusturuluyor (Task 602)..."
vaspkit -task 602

if [ -f "PRIMCELL.vasp" ]; then
    echo "PRIMCELL.vasp -> POSCAR olarak degistiriliyor."
    cp PRIMCELL.vasp POSCAR
else
    echo "HATA: PRIMCELL.vasp olusamadi! (Eski POSCAR hatali olabilir)"
    exit 1
fi

echo "2. K-Yolu (K-Path) Olusturuluyor (Task 303)..."
vaspkit -task 303

echo "3. HSE06 icin KPOINTS Olusturuluyor (Task 251 -> 2 -> {k_spacing} {k_spacing})..."
# Vaspkit alt menulerine otomatik cevap gonderme
echo -e "2\\n{k_spacing}\\n{k_spacing}" | vaspkit -task 251

echo "---------------------------------------------------"
echo "BASARILI: HSE06 KPOINTS dosyasi hazirlandi!"
echo "Islem bittikten sonra bant yapisini cekmek icin 'vaspkit -task 252' kullanin."
"""

    # --- INCAR DOSYASI OLUŞTURMA ---
    incar_lines = [
        f"SYSTEM = {system_name}",
        "ISTART = 1",
        "ICHARG = 1",
        "LWAVE  = .TRUE.",
        "LCHARG = .TRUE.",
        "LVTOT  = .FALSE.",
        "LVHAR  = .FALSE.",
        "LELF   = .FALSE.",
        "LORBIT = 11",
        "NEDOS  = 1000",
        "",
        "##### SCF #####",
        f"ENCUT  = {encut}",
        "ISMEAR = 0",
        "SIGMA  = 0.05",
        "EDIFF  = 1E-6",
        "NELMIN = 5",
        "NELM   = 300",
        "GGA    = PE",
        "LREAL  = .FALSE.",
        "",
        "##### Geo Opt (Kapalı) #####",
        "EDIFFG = -0.01",
        "IBRION = 2",
        "POTIM  = 0.2",
        "NSW    = 0         ! Bant yapisi icin 0 (Statik)",
        "ISIF   = 2",
        "",
        "#### HSE06 AYARLARI ####",
        "LHFCALC = .TRUE.",
        "AEXX    = 0.25",
        "HFSCREEN= 0.2",
        "ALGO    = Damped   ! HSE yakınsamasını iyileştirir",
        "TIME    = 0.4",
        f"ISPIN   = {ispin}"
    ]
    if magmom:
        incar_lines.append(f"MAGMOM  = {magmom}")

    incar_text = "\n".join(incar_lines)

    # --- EKRANDA GÖSTERİM VE İNDİRME ---
    c_out1, c_out2 = st.columns(2)
    
    with c_out1:
        st.subheader("Adım A: Vaspkit Betiği (prep_hse.sh)")
        st.code(bash_script, language="bash")
        st.download_button("📥 prep_hse.sh İndir", data=bash_script, file_name="prep_hse.sh", mime="text/x-shellscript")
        
    with c_out2:
        st.subheader("Adım B: HSE06 INCAR Dosyası")
        st.code(incar_text, language="bash")
        st.download_button("📥 INCAR İndir", data=incar_text, file_name="INCAR", mime="text/plain")

    st.success("🎉 **Kullanım Rehberi:** 1) `CONTCAR`'ı `POSCAR` yapın. 2) İndirdiğiniz `prep_hse.sh` dosyasını çalıştırın. 3) İndirdiğiniz `INCAR` dosyasını klasöre atıp VASP'ı çalıştırın. 4) İş bitince terminale **`vaspkit -task 252`** yazıp sonuçları alın!")
    # ==========================================
# MODÜL 20: GEOMETRİ OPTİMİZASYONU (INCAR)
# ==========================================
elif secim == "🏗️ Geometri Optimizasyonu (INCAR)":
    st.header("Kompleks Metal Hidrür Geometri Optimizasyonu")
    st.markdown("Hacim, şekil ve iyonik pozisyonların (ISIF=3) aynı anda optimize edildiği, hafif elementlere (H, B, N) ve vdW etkileşimlerine özel yüksek hassasiyetli INCAR şablonu.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Sistem ve Ağ (Grid) Ayarları")
        system_name = st.text_input("Sistem Adı (SYSTEM)", value="Metal_Hydride_Opt")
        encut = st.number_input("Kesme Enerjisi - ENCUT (eV)", value=550, step=10, help="H ve B gibi elementler için min 500 eV önerilir.")
        isif_val = st.selectbox("ISIF (Serbestlik Derecesi)", 
                                [3, 2, 4], 
                                index=0, 
                                help="3: Hacim+Şekil+İyonlar (Tam Opt). 2: Sadece İyonlar. 4: Hacim Sabit, Şekil+İyonlar.")
        ivdw_val = st.selectbox("IVDW (van der Waals Düzeltmesi)", 
                                [12, 11, 10, 0], 
                                index=0, 
                                help="12: DFT-D3(BJ) (En moderni). 11: DFT-D3 (Grimme). 0: Kapalı.")

    with col2:
        st.subheader("2. Elektronik ve İyonik Yakınsama")
        ediff = st.text_input("EDIFF (Elektronik Tolerans)", value="1E-8")
        ediffg = st.text_input("EDIFFG (İyonik Kuvvet Toleransı)", value="-0.01", help="Kuvvet kriteri. Makaleler için genelde -0.01 veya -0.02 eV/A yeterlidir.")
        ispin = st.selectbox("ISPIN (Spin Polarizasyonu)", [1, 2], index=0, help="Geçiş metali (Ti, Sc, Ni vb.) varsa 2 yapın.")
        
        if ispin == 2:
            magmom = st.text_input("MAGMOM", value="2*0.0 1*1.0 5*0.0")
        else:
            magmom = None

    st.markdown("---")
    st.subheader("3. Üretilen INCAR Dosyası")

    # INCAR Metnini Oluştur
    incar_lines = [
        f"SYSTEM = {system_name}",
        "",
        "# --- Global Parametreler ---",
        "PREC   = Accurate    ! Hassas hesaplama",
        f"ENCUT  = {encut}         ! Kesme enerjisi",
        "LREAL  = .FALSE.     ! Projeksiyon resiprokal uzayda (Hassasiyet için)",
        "ALGO   = Fast        ! Davison + RMM-DIIS",
        "ISYM   = 2           ! Simetri açık",
        "",
        "# --- Elektronik Yakınsama (SCF) ---",
        f"EDIFF  = {ediff}      ! Elektronik yakınsama kriteri",
        "NELM   = 100         ! Maksimum elektronik adım",
        "NELMIN = 4           ! Minimum elektronik adım",
        "",
        "# --- İyonik Gevşeme (Geometri Optimizasyonu) ---",
        f"ISIF   = {isif_val}            ! 3: Hacim, sekil ve pozisyonlar",
        "IBRION = 2            ! Eşlenik Gradyan (Conjugate Gradient)",
        "NSW    = 200          ! Maksimum iyonik adım sayısı",
        f"EDIFFG = {ediffg}        ! Kuvvet yakınsama kriteri (eV/A)",
        "",
        "# --- Elektronik Smearing ---",
        "ISMEAR = 0            ! Yalıtkanlar/yarı iletkenler için Gaussian",
        "SIGMA  = 0.05",
        "",
        "# --- Van der Waals (vdW) Düzeltmeleri ---",
        f"IVDW   = {ivdw_val}           ! Kompleks anyonlar arasi etkilesimler",
        "",
        "# --- Spin Polarizasyonu ---",
        f"ISPIN  = {ispin}"
    ]

    if magmom:
        incar_lines.append(f"MAGMOM = {magmom}")

    incar_text = "\n".join(incar_lines)
    
    # Ekranda Göster
    st.code(incar_text, language="bash")
    
    # İndirme ve Bilgi
    st.download_button(
        label="📥 Optimizasyon INCAR Dosyasını İndir",
        data=incar_text,
        file_name="INCAR",
        mime="text/plain"
    )

    st.success("💡 **İpucu:** Tam geometri optimizasyonundan (ISIF=3) sonra hacim (volume) değişeceği için, elektronik yapıyı (DOS, Band vb.) hesaplamadan önce elde ettiğiniz `CONTCAR`'ı `POSCAR` yapıp bu sefer **ISIF=2** ile tek bir optimizasyon adımı daha koşturmak (Volume Relaxation Protocol) en güvenli yoldur.")
    # ==========================================
# MODÜL 21: STATİK ENERJİ / REFERANS (INCAR)
# ==========================================
elif secim == "🔋 Statik Enerji / Referans (INCAR)-NEB":
    st.header("Statik Enerji (Single Point / Bulk Reference) INCAR Jeneratörü")
    st.markdown("İyonların sabit tutulup sadece elektronik yapının çok yüksek hassasiyetle yakınsatıldığı (IBRION=-1), referans enerjisi veya DOS/Band öncesi CHGCAR üretimi için kullanılan INCAR şablonu.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Sistem Ayarları")
        system_name = st.text_input("Sistem Adı (SYSTEM)", value="K2TiH5_Bulk_Reference")
        encut = st.number_input("Kesme Enerjisi (ENCUT, eV)", value=550, step=10)
        ediff = st.text_input("Elektronik Tolerans (EDIFF)", value="1E-6")
        
    with col2:
        st.subheader("2. Çıktı Kontrolü (I/O)")
        st.info("DOS veya Bant hesabı yapacaksanız CHGCAR yazdırılmalıdır.")
        lcharg = st.checkbox("Şarj Yoğunluğunu Yazdır (LCHARG = .TRUE.)", value=True)
        lwave = st.checkbox("Dalga Fonksiyonunu Yazdır (LWAVE = .TRUE.)", value=False)
        lreal = st.selectbox("LREAL (Projeksiyon)", [".FALSE.", "Auto"], index=0, help="Küçük/orta boy hücreler için .FALSE., çok büyük hücreler (100+ atom) için Auto önerilir.")

    st.markdown("---")
    st.subheader("3. Üretilen INCAR Dosyası")

    # Boolean değişkenleri VASP formatına çevirme
    str_lcharg = ".TRUE." if lcharg else ".FALSE."
    str_lwave = ".TRUE." if lwave else ".FALSE."

    # INCAR Metnini Oluştur
    incar_lines = [
        f"SYSTEM = {system_name}",
        "ISTART = 0          ! Sifirdan basla",
        "ICHARG = 2          ! Baslangic sarj yogunlugu atomlardan",
        "",
        "# --- Hassasiyet Ayarlari ---",
        "PREC   = Accurate   ! Yuksek hassasiyetli grid",
        f"ENCUT  = {encut}        ! Duzlem dalga kesme enerjisi",
        f"EDIFF  = {ediff}       ! Elektronik yakinsama kriteri",
        "EDIFFG = -0.01      ! (Iyonik yakinsama - Statik hesapta etkisizdir)",
        "",
        "# --- Smearing Ayarlari ---",
        "ISMEAR = 0          ! Yalitan/Yari iletken icin Gaussian",
        "SIGMA  = 0.05",
        "",
        "# --- Iyonik Gevseme (KAPALI) ---",
        "IBRION = -1         ! Iyonlari HAREKET ETTIRME (Statik)",
        "NSW    = 0          ! Iyonik adim sayisi 0",
        f"LREAL  = {lreal}    ! Resiprokal uzay projeksiyonu",
        "",
        "# --- Dosya Yazdirma ---",
        f"LWAVE  = {str_lwave}     ! WAVECAR dosyasi yazilsin mi?",
        f"LCHARG = {str_lcharg}     ! CHGCAR dosyasi yazilsin mi?"
    ]

    incar_text = "\n".join(incar_lines)
    
    # Ekranda Göster
    st.code(incar_text, language="bash")
    
    # İndirme ve Bilgi
    st.download_button(
        label="📥 Statik INCAR Dosyasını İndir",
        data=incar_text,
        file_name="INCAR",
        mime="text/plain"
    )
    
    st.success("💡 **Kullanım Notu:** Bu INCAR ile çalıştırdığınız bir Bulk veya temiz Slab yapısının OUTCAR dosyasından okuyacağınız son `free energy TOTEN` değeri, NEB hesaplamalarınızda veya Formasyon Enerjisi formüllerinizde kullanacağınız referans enerjidir ($E_{ref}$).")
    # ==========================================
# MODÜL 22: YÜZEY VE SLAB OTOMASYONU (VASPKIT)
# ==========================================
elif secim == "🧫 Yüzey & Slab Otomasyonu (VASPKIT)":
    st.header("Yüzey (Slab) Üretimi ve İş Gönderme Otomasyonu")
    st.markdown("VASPKIT 803 kullanarak belirlediğiniz Bulk yapıdan farklı Miller indekslerinde yüzeyler (slab) kesen, her yüzey sonlanması (termination) için dinamik K-noktası hesaplayan ve işleri TRUBA'ya gönderen akıllı Bash betiği.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. Yüzey Geometrisi")
        miller_input = st.text_input("Miller İndeksleri", value="0 0 1, 1 0 0, 1 1 0", help="Aralarına virgül koyarak yazın.")
        layers = st.number_input("Slab Kalınlığı (Katman)", value=3, min_value=1)
        vacuum = st.number_input("Vakum Boşluğu (Å)", value=15.0, step=1.0)
        k_product = st.number_input("K-Points Yoğunluğu (K_PRODUCT)", value=30, help="L * K = 30 mantığıyla dinamik K-ağı örülür.")

    with col2:
        st.subheader("2. INCAR Ayarları")
        encut = st.number_input("ENCUT (eV)", value=550, step=10)
        potim = st.number_input("POTIM (Adım Büyüklüğü)", value=0.05, step=0.01)
        ispin = st.selectbox("ISPIN (Manyetizma)", [1, 2], index=1)
        magmom = st.text_input("MAGMOM", value="6*0.0 3*1.0 15*0.0") if ispin == 2 else ""
        ivdw = st.selectbox("IVDW (vdW Düzeltmesi)", [11, 12, 10, 0], index=0)

    with col3:
        st.subheader("3. TRUBA (SLURM) Ayarları")
        queue = st.text_input("Kuyruk (Partition)", value="hamsi")
        cores = st.number_input("Çekirdek Sayısı", value=56, step=8)
        email = st.text_input("E-Posta", value="s.yamcicier@gmail.com")

    st.markdown("---")

    # Miller input formatını Bash Array formatına çevirme ("0 0 1" "1 1 0" vb.)
    miller_clean = " ".join([f'"{m.strip()}"' for m in miller_input.split(",")])

    # Bash Script Metni (Değişken kaçışlarına (\$hkl vb.) dikkat edilerek hazırlandı)
    bash_script = f"""#!/bin/bash

# ==============================================================================
# YUZEY (SLAB) VE TERMINATION OTOMASYONU
# ==============================================================================
MILLER_INDICES=({miller_clean}) 
LAYERS={layers}       
VACUUM={vacuum}      
K_PRODUCT={k_product}  

POTCAR_FILE="POTCAR"
BULK_POSCAR="POSCAR"

if [ ! -f "\$BULK_POSCAR" ] || [ ! -f "\$POTCAR_FILE" ]; then
    echo "HATA: Ana dizinde POSCAR (Bulk) veya POTCAR bulunamadi!"
    exit 1
fi

# ==============================================================================
# OTOMASYON DONGUSU
# ==============================================================================

for hkl in "\${{MILLER_INDICES[@]}}"; do
    HKL_STR=\$(echo \$hkl | tr -d ' ')
    HKL_DIR=\$(echo \$hkl | tr ' ' '_')
    
    BASE_DIR="Surface_\$HKL_DIR"
    mkdir -p "\$BASE_DIR"
    cp "\$BULK_POSCAR" "\$BASE_DIR/POSCAR"
    
    echo "------------------------------------------------------------"
    echo ">>> Miller Indeksi (\$hkl) Isleniyor..."
    cd "\$BASE_DIR"

    # VASPKIT ile Slab Uretimi
    vaspkit <<EOF
803
\$hkl
\$LAYERS
\$VACUUM
EOF

    shopt -s nullglob
    SLAB_FILES=(SLAB_\${{HKL_STR}}_*.vasp)
    [ \${{#SLAB_FILES[@]}} -eq 0 ] && SLAB_FILES=(SLAB_POSCAR_*)

    for slab_file in "\${{SLAB_FILES[@]}}"; do
        TERM_ID=\$(echo "\$slab_file" | grep -oP '\d{{4}}')
        [ -z "\$TERM_ID" ] && TERM_ID="unique"

        TERM_DIR="Term_\$TERM_ID"
        mkdir -p "\$TERM_DIR"
        mv "\$slab_file" "\$TERM_DIR/POSCAR"
        cp "../\$POTCAR_FILE" "\$TERM_DIR/POTCAR"

        cd "\$TERM_DIR"

        # --- DINAMIK INCAR URETIMI ---
        cat <<EOF > INCAR
SYSTEM = Slab Soft Relaxation (\$HKL_STR - \$TERM_ID)
PREC   = Accurate
ENCUT  = {encut}
EDIFF  = 1E-6
EDIFFG = -0.05
POTIM  = {potim}
ISIF   = 2
IBRION = 2
NSW    = 100
ISMEAR = 0
SIGMA  = 0.05
ALGO   = Fast
ISPIN  = {ispin}
{f"MAGMOM = {magmom}" if ispin == 2 else ""}
IVDW   = {ivdw}
LREAL  = Auto
LWAVE  = .FALSE.
LCHARG = .FALSE.
EOF

        # --- DINAMIK K-POINTS URETIMI ---
        L1=\$(sed -n '3p' POSCAR | awk '{{print sqrt(\$1^2+\$2^2+\$3^2)}}')
        L2=\$(sed -n '4p' POSCAR | awk '{{print sqrt(\$1^2+\$2^2+\$3^2)}}')
        K1=\$(python3 -c "print(max(1, round(\$K_PRODUCT / \$L1)))")
        K2=\$(python3 -c "print(max(1, round(\$K_PRODUCT / \$L2)))")

        cat <<EOF > KPOINTS
Dinamik K-Points (L1= \${{L1:0:4}} A, L2= \${{L2:0:4}} A)
0
Monkhorst-Pack
\$K1 \$K2 1
0 0 0
EOF

        # --- SLURM BETIGI ---
        cat <<EOM > job.sh
#!/bin/bash
#SBATCH -p {queue}
#SBATCH -J v_\${{HKL_STR}}_\${{TERM_ID}}
#SBATCH -N 1
#SBATCH -n {cores}
#SBATCH --time=3-00:00:00
#SBATCH --output=slurm-%j.out
#SBATCH --mail-user={email}
#SBATCH --mail-type=BEGIN,END,FAIL 

module purge 
module load comp/oneapi/2022 

mpirun /arf/home/syamcicier/derleme/vasp.6.3.0/bin/vasp_std
EOM

        sbatch job.sh
        echo "      [+] \$TERM_DIR gonderildi (K=\$K1 \$K2 1)"
        cd ..
    done
    rm -f POSCAR
    cd ..
done
echo ">>> TUM SLAB ISLEMLERI TAMAMLANDI!"
"""

    st.subheader("4. Üretilen Otonom Betik (run_slabs.sh)")
    st.code(bash_script, language="bash")

    st.download_button(
        label="📥 Yüzey/Slab Betiğini İndir (run_slabs.sh)",
        data=bash_script,
        file_name="run_slabs.sh",
        mime="text/x-shellscript"
    )
    
    st.success("💡 **Nasıl Kullanılır:** Bu betiği, optimize edilmiş bir Bulk `POSCAR` ve ona ait `POTCAR` dosyasının bulunduğu ana klasöre atın. `chmod +x run_slabs.sh` ile yetki verin ve çalıştırın. Script tüm Miller indeksleri ve sonlanmalar (terminations) için klasörleri açıp otonom olarak kuyruğa gönderecektir.")
    # ==========================================
# MODÜL 23: YÜZEY ENERJİSİ ANALİZÖRÜ (SCRIPT)
# ==========================================
elif secim == "🔍 Yüzey Enerjisi Analizörü (Script)":
    st.header("Yüzey Enerjisi ($\gamma$) Tarama ve Analiz Betiği")
    st.markdown("TRUBA'da çalışan Slab hesaplamalarınızın durumunu denetleyen, biten işlerin alanını ($Å^2$) ve Yüzey Enerjisini ($J/m^2$) otonom olarak hesaplayıp terminale tablo olarak basan ileri düzey Bash/Python analizörü.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Bulk (Referans) Verileri")
        e_bulk = st.number_input("Birim Hücrenin Toplam Enerjisi (eV)", value=-28.549848, format="%.6f", help="Örn: Statik hesaptan elde ettiğiniz TOTEN değeri.")
        n_bulk = st.number_input("Birim Hücredeki Atom Sayısı", value=8, step=1, min_value=1)

    with col2:
        st.subheader("2. Formül Bilgisi")
        st.latex(r"\gamma = \frac{E_{slab} - N_{units} \times E_{bulk}}{2 \times A} \times 16.02")
        st.info("Bu betik TRUBA'da saniyeler içinde çalışarak tüm klasörlerdeki sonuçları yukarıdaki formüle göre süzer.")

    st.markdown("---")

    # --- BASH SCRIPT METNİ ---
    bash_script = f"""#!/bin/bash

# ==============================================================================
# YUZEY ENERJISI TARAMA VE HESAPLAMA BETIGI (VASP Kontrol Merkezi)
# ==============================================================================
export E_BULK_VAL="{e_bulk}"
export N_BULK_REF="{n_bulk}"

echo "=========================================================================================="
echo " Miller | Term.     |  E_Slab (eV)  |  Alan (A^2) |  Surf. Energy (J/m2) | Durum"
echo "------------------------------------------------------------------------------------------"

for surf_dir in Surface_*; do
    # Eger klasor yoksa atla
    [ -d "\$surf_dir" ] || continue
    
    HKL_STR=\$(echo "\$surf_dir" | cut -d'_' -f2,3,4 | tr -d '_')
    
    for term_dir in "\$surf_dir"/Term_*; do
        [ -d "\$term_dir" ] || continue
        TERM=\$(basename "\$term_dir")
        TERM_ID=\$(echo "\$TERM" | cut -d'_' -f2)
        export JOB_NAME="v_\${{HKL_STR}}_\${{TERM_ID}}"
        export TERM_DIR_VAL="\$term_dir"

        STATUS="YOK"
        E_SLAB_VAL="---"
        GAMMA="---"
        A_ANG="---"

        # --- 1. DURUM TESPITI ---
        if squeue -u \$USER | grep -q "\$JOB_NAME"; then
            STATUS="CALISIYOR"
        elif [ -f "\$term_dir/OUTCAR" ]; then
            if grep -q "General timing and accounting" "\$term_dir/OUTCAR"; then
                STATUS="BITTI (OK)"
            else
                STATUS="DURDU/HATA"
            fi
        else
            STATUS="BEKLIYOR"
        fi

        # --- 2. VERI CEKME VE HESAPLAMA ---
        if [ -f "\$term_dir/OSZICAR" ] && [ -f "\$term_dir/POSCAR" ]; then
            E_SLAB_VAL=\$(grep 'F=' "\$term_dir/OSZICAR" | tail -1 | awk '{{print \$5}}')
            export E_SLAB_INPUT="\$E_SLAB_VAL"
            
            # Gomulu Python Betigi (Hizli Alan ve Enerji Hesabi)
            CALC_RESULTS=\$(python3 -c "
import numpy as np
import os

def run():
    try:
        term_dir = os.environ.get('TERM_DIR_VAL')
        with open(os.path.join(term_dir, 'POSCAR'), 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        scale = float(lines[1].strip())
        v1 = np.array([float(x) for x in lines[2].split()]) * scale
        v2 = np.array([float(x) for x in lines[3].split()]) * scale
        area = np.linalg.norm(np.cross(v1, v2))
        
        line6 = lines[6].split()
        if line6[0].isdigit():
            n_slab = sum([int(x) for x in line6])
        else:
            n_slab = sum([int(x) for x in lines[7].split()])
            
        e_slab = float(os.environ.get('E_SLAB_INPUT'))
        e_bulk = float(os.environ.get('E_BULK_VAL'))
        n_bulk_ref = float(os.environ.get('N_BULK_REF'))
        
        n_units = n_slab / n_bulk_ref
        gamma_j_m2 = ((e_slab - (n_units * e_bulk)) / (2 * area)) * 16.021766
        
        print('{{:.4f}} {{:.4f}}'.format(area, gamma_j_m2))
    except Exception:
        print('HATA HATA')

run()
")
            A_ANG=\$(echo \$CALC_RESULTS | awk '{{print \$1}}')
            GAMMA=\$(echo \$CALC_RESULTS | awk '{{print \$2}}')
        fi

        printf " %-6s | %-9s | %-13s | %-11s | %-19s | %s\\n" "\$HKL_STR" "\$TERM" "\$E_SLAB_VAL" "\$A_ANG" "\$GAMMA" "\$STATUS"
    done
done
echo "=========================================================================================="
"""

    st.subheader("3. Üretilen Analiz Betiği (get_surface_energy.sh)")
    st.code(bash_script, language="bash")

    st.download_button(
        label="📥 Yüzey Enerjisi Betiğini İndir (get_surface_energy.sh)",
        data=bash_script,
        file_name="get_surface_energy.sh",
        mime="text/x-shellscript"
    )
    
    st.success("💡 **Kullanım:** İndirdiğiniz bu dosyayı `Surface_001`, `Surface_110` vb. klasörlerinizin bulunduğu en üst (ana) dizine atın. `chmod +x get_surface_energy.sh` ile yetkilendirip `./get_surface_energy.sh` yazdığınızda tüm simülasyonların sonuçları şık bir tablo olarak terminalinize düşecektir.")
    # ==========================================
# MODÜL 24: NEB IS/FS OPTİMİZASYONU (2-AŞAMALI)
# ==========================================
elif secim == "🏗️ NEB IS/FS Optimizasyonu (2-Aşamalı)":
    st.header("NEB Başlangıç (IS) ve Bitiş (FS) Optimizasyonu")
    st.markdown("Asimetrik yüzeylerde VASP'ın çökmesini engellemek için **2 aşamalı optimizasyon** stratejisi: Önce standart geometri rahatlatması yapılır, ardından dalga fonksiyonları (`WAVECAR`) okunarak Dipol Düzeltmesi (`LDIPOL`) ile hassas optimizasyon tamamlanır.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Sistem ve Hassasiyet")
        system_name = st.text_input("Sistem Adı", value="K2TiH5 Slab Relaxation (IS/FS)")
        encut = st.number_input("ENCUT (eV)", value=500, step=10)
        ediffg = st.text_input("Kuvvet Yakınsaması (EDIFFG)", value="-0.02", help="Makale standardı için -0.02 veya -0.01 eV/A")

    with col2:
        st.subheader("2. Dipol Düzeltmesi (2. Aşama İçin)")
        idipol = st.selectbox("Düzeltme Yönü (IDIPOL)", [3, 1, 2, 4], index=0, help="3: Z-ekseni (Slab/Vakum yönü genelde Z'dir)")
        dipol_center = st.text_input("Kütle Merkezi (DIPOL)", value="0.5 0.5 0.5", help="Sistemin kütle merkezi. VASP'ın vakumda yük biriktirmesini önler.")

    st.markdown("---")

    # --- 1. AŞAMA INCAR (KABA OPTİMİZASYON) ---
    incar_step1 = f"""SYSTEM = {system_name} - 1. Asama

# --- Elektronik Optimizasyon ---
PREC   = Accurate    ! Kuvvet hassasiyeti için zorunlu
ADDGRID= .TRUE.      ! Hassas kuvvet hesabı
ENCUT  = {encut}
EDIFF  = 1E-6        ! Sıkı elektronik yakınsama
ALGO   = Normal
LREAL  = Auto
ISMEAR = 0
SIGMA  = 0.05
ISYM   = 0           ! Simetriyi kapat (Slab/NEB için güvenli)
NELM   = 150

# --- İyonik Optimizasyon (Geometri) ---
IBRION = 2           ! Conjugate-Gradient
ISIF   = 2           ! Sadece iyonlar (Vakumu koru)
NSW    = 400
EDIFFG = {ediffg}      ! Kuvvet yakınsama kriteri (eV/A)

# --- Çıktı Kontrolü ---
LWAVE  = .TRUE.      ! 2. aşamaya temel oluşturması için KAYDET
LCHARG = .FALSE.     ! CHGCAR'a gerek yok
"""

    # --- 2. AŞAMA INCAR (HASSAS DİPOL OPTİMİZASYONU) ---
    incar_step2 = f"""SYSTEM = {system_name} - 2. Asama Hassas Opt

# --- Yeniden Başlatma (Restart) Ayarları ---
ISTART = 1           ! ÖNEMLİ: Klasördeki mevcut WAVECAR dosyasını oku
ICHARG = 0           ! Başlangıç yük yoğunluğunu WAVECAR'dan hesapla

# --- Yüksek Hassasiyet (Makale ve NEB İçin Zorunlu) ---
PREC   = Accurate
ADDGRID= .TRUE.
ENCUT  = {encut}
EDIFF  = 1E-6
ALGO   = Normal      ! WAVECAR okunduğu için Normal algoritma çok stabil çalışır
LREAL  = Auto
ISMEAR = 0
SIGMA  = 0.05
ISYM   = 0           ! Simetriyi kesinlikle kapat

# --- İyonik Optimizasyon (Geometri) ---
IBRION = 2
ISIF   = 2           ! Sadece iyonları hareket ettir, vakumu KORU
NSW    = 100         ! Zaten yerine oturduğu için 10-15 adımda bitecektir
EDIFFG = {ediffg}      ! Kuvvet yakınsama kriteri

# --- Dipol Düzeltmesi (Asimetrik Yüzey İçin Zorunlu) ---
LDIPOL = .TRUE.      ! Dipol düzeltmesini AÇ
IDIPOL = {idipol}           ! Düzeltmeyi belirtilen eksen boyunca yap
DIPOL  = {dipol_center}  ! Slab'in kütle merkezi (VASP'ın çökmesini engeller)

# --- Çıktı Kontrolü ---
LWAVE  = .TRUE.      ! NEB hesabına aktarılmak üzere güncel dalgayı YAZ
LCHARG = .FALSE.
"""

    # --- EKRANDA GÖSTERİM VE İNDİRME ---
    st.subheader("3. Üretilen INCAR Dosyaları")
    
    c_out1, c_out2 = st.columns(2)
    
    with c_out1:
        st.markdown("**Adım 1: Standart Optimizasyon**")
        st.code(incar_step1, language="bash")
        st.download_button("📥 1. Aşama INCAR İndir", data=incar_step1, file_name="INCAR_Step1", mime="text/plain")
        
    with c_out2:
        st.markdown("**Adım 2: Dipol Korumalı Hassas Optimizasyon**")
        st.code(incar_step2, language="bash")
        st.download_button("📥 2. Aşama INCAR İndir", data=incar_step2, file_name="INCAR_Step2", mime="text/plain")

    st.success("💡 **İş Akışı Tavsiyesi:** Önce 1. Aşama INCAR ile hesabınızı bitirin. İşlem bittiğinde `CONTCAR` dosyasını `POSCAR` olarak değiştirin (veya VESTA ile kontrol edin). Ardından 2. Aşama INCAR dosyasını klasöre atıp VASP'ı tekrar çalıştırın. `OUTCAR`'da dipol düzeltmesinin devreye girdiğini göreceksiniz.")
    # ==========================================
# MODÜL 25: CI-NEB HESAPLAMASI (INCAR)
# ==========================================
elif secim == "⛰️ CI-NEB Hesaplaması (INCAR)":
    st.header("CI-NEB (Climbing Image Nudged Elastic Band) INCAR Jeneratörü")
    st.markdown("Reaksiyon bariyerlerini (Aktivasyon Enerjisi) bulmak için VTST kodlarını (FIRE optimizer) kullanan, dipol düzeltmeli makale kalitesinde NEB INCAR şablonu.")
    st.markdown("---")

    # --- KRİTİK UYARI ---
    st.warning("**⚠️ TRUBA (SLURM) KURALI:** NEB hesabını kuyruğa gönderirken talep ettiğiniz toplam çekirdek sayısı (`-n`), İmaj Sayısına (`IMAGES`) **TAM BÖLÜNMELİDİR**. Örneğin `IMAGES = 7` ise, çekirdek sayınız 28, 56 veya 112 gibi 7'nin katları olmalıdır. Aksi halde VASP anında çöker!")

    # --- KONTROL PANELİ ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. NEB ve VTST Ayarları")
        images = st.number_input("İmaj Sayısı (IMAGES)", value=7, min_value=1, step=1, help="Araya eklenecek nokta sayısı. Tek sayı (3, 5, 7) olması tepe noktasının (TS) bulunmasını kolaylaştırır.")
        lclimb = st.checkbox("Climbing Image Açık (LCLIMB = .TRUE.)", value=True, help="En yüksek enerjili imajı zorla tepe noktasına (Transition State) oturtur.")
        iopt = st.selectbox("VTST Optimizer (IOPT)", [3, 1, 2, 7], index=0, help="3: FIRE (En kararlı), 1: LBFGS, 2: CG, 7: FAST")
        ediffg = st.text_input("Kuvvet Yakınsaması (EDIFFG)", value="-0.03", help="Geçiş durumları için -0.03 veya -0.05 genelde yeterlidir.")

    with col2:
        st.subheader("2. Dipol ve Hassasiyet")
        system_name = st.text_input("Sistem Adı", value=f"K2TiH5 CI-NEB ({images} Images)")
        encut = st.number_input("ENCUT (eV)", value=500, step=10)
        idipol = st.selectbox("Dipol Yönü (IDIPOL)", [3, 1, 2, 4], index=0)
        dipol_center = st.text_input("Kütle Merkezi (DIPOL)", value="0.5 0.5 0.5")

    st.markdown("---")

    # --- INCAR OLUŞTURMA ---
    str_lclimb = ".TRUE." if lclimb else ".FALSE."
    
    incar_lines = [
        f"SYSTEM = {system_name}",
        "",
        "# --- Elektronik Optimizasyon (IS/FS ile Birebir Ayni Olmali) ---",
        "PREC   = Accurate    ! NEB kuvvetleri icin cok kritik",
        "ADDGRID= .TRUE.      ! Fourier aginda hassas kuvvet hesabi",
        f"ENCUT  = {encut}",
        "EDIFF  = 1E-6        ! Kuvvet gurultusunu onlemek icin siki tutuldu",
        "ALGO   = Normal      ! NEB icin Fast yerine Normal daha stabil calisir",
        "LREAL  = Auto",
        "ISMEAR = 0",
        "SIGMA  = 0.05",
        "ISYM   = 0           ! Simetri kesinlikle kapali",
        "",
        "# --- Iyonik Optimizasyon ve NEB Parametreleri (VTST) ---",
        "IBRION = 3           ! NEB ve VTST optimizerlari icin 3 olmali",
        "POTIM  = 0           ! VTST optimizer kullanildiginda sifir birakilir",
        f"IOPT   = {iopt}           ! VTST Algoritmasi (3=FIRE, 1=LBFGS)",
        "ISIF   = 2           ! Hucre hacmi ve vakum sabit",
        "NSW    = 500         ! NEB uzun surebilir",
        f"EDIFFG = {ediffg}        ! Kuvvet yakinsamasi (eV/A)",
        "",
        "# --- NEB Spesifik Etiketler ---",
        f"IMAGES = {images}           ! Ara imaj sayisi (01'den baslar)",
        "SPRING = -5.0        ! Imajlar arasi yay sabiti",
        f"LCLIMB = {str_lclimb}       ! CI-NEB modunu acar (Tepe noktasina oturtur)",
        "",
        "# --- Dipol Duzeltmesi (IS/FS ile Birebir Ayni Olmali) ---",
        "LDIPOL = .TRUE.",
        f"IDIPOL = {idipol}",
        f"DIPOL  = {dipol_center}",
        "",
        "# --- Cikti Kontrolu ---",
        "LWAVE  = .FALSE.     ! Tum imajlar icin devasa dosya yazmasin",
        "LCHARG = .FALSE."
    ]

    incar_text = "\n".join(incar_lines)

    # --- EKRANDA GÖSTERİM VE İNDİRME ---
    st.subheader("3. Üretilen CI-NEB INCAR Dosyası")
    st.code(incar_text, language="bash")
    
    st.download_button(
        label="📥 CI-NEB INCAR İndir",
        data=incar_text,
        file_name="INCAR",
        mime="text/plain"
    )
    
    st.success(f"💡 **İş Akışı İpucu:** İşlemi başlatmadan önce klasör yapınızın `00` (IS), `01`...`{images:02d}`, `{images+1:02d}` (FS) şeklinde sıralandığından ve `00` ile `{images+1:02d}` klasörlerinin içinde IS/FS hesaplarından gelen **OUTCAR** dosyalarının bulunduğundan emin olun.")
    # ==========================================
# MODÜL 26: HSE06 OPTİK ÖZELLİKLER (2-AŞAMALI)
# ==========================================
elif secim == "🌈 HSE06 Optik Özellikler (2-Aşamalı)":
    st.header("HSE06 Hibrit Fonksiyonel ile Optik Özellikler (LOPTICS)")
    st.markdown("Optik spektrum (Dielektrik matrisi, Soğurma, Yansıma vb.) için PBE dalga fonksiyonundan başlayan 2 aşamalı, yüksek hassasiyetli HSE06 INCAR jeneratörü.")
    st.markdown("---")

    # --- KRİTİK UYARI ---
    st.warning("**⚠️ KRİTİK BANT UYARISI (NBANDS):** Optik geçişlerin (transition) doğru hesaplanabilmesi için iletkenlik bandında (conduction band) yeterince boş seviye olmalıdır. Geometri optimizasyonundan aldığınız standart `OUTCAR` dosyasındaki `NBANDS` değerini **en az 1.5 veya 2 katına** çıkararak bu hesaba girmelisiniz!")

    # --- KONTROL PANELİ ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Sistem ve Çözünürlük")
        system_name = st.text_input("Sistem Adı", value="Material_Optical_HSE06")
        encut = st.number_input("ENCUT (eV)", value=550, step=10)
        nbands = st.number_input("NBANDS (Boş Bantlı)", value=220, step=10, help="Optik hesaplamalar için standart değerin 2 katı önerilir.")

    with col2:
        st.subheader("2. HSE06 ve Optik Ayarları")
        algo_opt = st.selectbox("HSE Algoritması (ALGO)", ["All", "Damped", "Normal"], index=0, help="'All' veya 'Damped', HSE06 için en kararlı olanlardır.")
        precfock = st.selectbox("PRECFOCK (HSE Hızı)", ["Fast", "Normal", "Accurate"], index=0, help="Süreyi makul tutmak için optik hesaplarda 'Fast' kabul edilebilir bir standarttır.")
        cshift = st.number_input("Lorentziyen Genişletme (CSHIFT)", value=0.10, step=0.01, format="%.2f")

    st.markdown("---")

    # --- 1. AŞAMA INCAR (PBE WAVECAR) ---
    incar_step1 = f"""SYSTEM = {system_name} - Adim 1 PBE Wavefunction
PREC   = Accurate
ENCUT  = {encut}         ! 2. Adim ile ayni olmali
ISMEAR = 0
SIGMA  = 0.05
IBRION = -1          ! Iyonlari hareket ettirme (Sadece elektronik hesap)
NSW    = 0
ALGO   = Normal
LWAVE  = .TRUE.      ! ONEMLI: 2. asama icin WAVECAR dosyasini yaz
LCHARG = .TRUE.      ! CHGCAR da lazim olabilir
"""

    # --- 2. AŞAMA INCAR (HSE06 OPTICS) ---
    incar_step2 = f"""SYSTEM = {system_name} - Adim 2 HSE06 Optics

# --- Baslangic Parametreleri ---
ISTART = 1           ! 1: Adim 1'den uretilen WAVECAR'dan devam et (Hizlandirir)
PREC   = Accurate    ! Yuksek hassasiyet
LREAL  = .FALSE.     ! Projeksiyonlar reel uzayda olmamali (Hassasiyet icin)

# --- Elektronik Cozumleyici (HSE Icin Kritik) ---
ALGO   = {algo_opt}          ! HSE icin karali algoritma
TIME   = 0.4         ! ALGO=All/Damped icin zaman adimi
NELM   = 100         ! Maksimum elektronik iterasyon sayisi
EDIFF  = 1E-5        ! Enerji yakinsama kriteri

# --- Hibrit Fonksiyonel (HSE06) Ayarlari ---
LHFCALC  = .TRUE.    ! Hibrit hesabi acar
HFSCREEN = 0.2       ! HSE06 icin standart tarama parametresi
AEXX     = 0.25      ! %25 Degisim (Exchange) katkisi
PRECFOCK = {precfock}       ! Hesaplama suresini optimize etmek icin

# --- Optik Ozellikler (LOPTICS) ---
LOPTICS = .TRUE.     ! Optik dielektrik matrisini hesaplar
CSHIFT  = {cshift}         ! Lorentziyen genisletme
NEDOS   = 2000       ! Spektrumun puruzsuz gorunmesi icin enerji noktasi sayisi

# --- Bant ve Doluluk Ayarlari ---
ISMEAR = 0           ! Yari iletkenler icin Gaussian Smearing
SIGMA  = 0.05
NBANDS = {nbands}          ! DIKKAT: Bos bantlar (conduction) optik gecisler icin sarttir!
"""

    # --- EKRANDA GÖSTERİM VE İNDİRME ---
    st.subheader("3. Üretilen INCAR Dosyaları")
    
    c_out1, c_out2 = st.columns(2)
    
    with c_out1:
        st.markdown("**Adım 1: PBE Dalga Fonksiyonu (WAVECAR) Üretimi**")
        st.code(incar_step1, language="bash")
        st.download_button("📥 1. Aşama INCAR İndir", data=incar_step1, file_name="INCAR_Step1", mime="text/plain")
        
    with c_out2:
        st.markdown("**Adım 2: HSE06 Optik Hesaplama (LOPTICS)**")
        st.code(incar_step2, language="bash")
        st.download_button("📥 2. Aşama INCAR İndir", data=incar_step2, file_name="INCAR_Step2", mime="text/plain")

    st.success("💡 **İş Akışı ve Analiz İpucu:**\n1. Önce `INCAR_Step1`'i `INCAR` yaparak çalıştırın.\n2. Bittiğinde hiçbir dosyayı silmeden `INCAR_Step2`'yi `INCAR` yapıp tekrar çalıştırın.\n3. HSE06 işlemi bittikten sonra optik spektrumu (Dielektrik sabiti, Soğurma katsayısı, Yansıma vb.) makale formatında çıkartmak için klasörde terminalden **`vaspkit -task 711`** komutunu kullanabilirsiniz.")
# ==========================================
# MODÜL 27: OTONOM YÜZEY DİFÜZYONU (FS JENERATÖRÜ)
# ==========================================
elif secim == "🔀 Yüzey Difüzyonu (FS Jeneratörü)":
    st.header("Otonom Yüzey Difüzyonu (Çarpışma Korumalı)")
    st.markdown("Bu modül yüzeydeki hidrojeni bulur, komşu boşluğa kaydırır ve **Periyodik Çarpışma Sensörü (Minimum Image Convention)** ile atomların üst üste binmesini engeller.")
    st.markdown("---")

    poscar_file = st.file_uploader("Optimize Edilmiş Başlangıç POSCAR (IS) Dosyasını Yükle")

    if poscar_file is not None:
        try:
            lines = poscar_file.getvalue().decode("utf-8").splitlines()
            
            # --- MATRİS VE ATOM OKUMA ---
            scale = float(lines[1].strip())
            cell = np.array([[float(x) for x in line.split()] for line in lines[2:5]]) * scale
            inv_cell = np.linalg.inv(cell)
            
            elem_names = lines[5].split()
            elem_counts = [int(x) for x in lines[6].split()]
            total_atoms = sum(elem_counts)
            
            sel_dyn = False
            coord_start = 7
            if lines[7].strip()[0] in ['S', 's']:
                sel_dyn = True
                coord_start = 8
                
            coord_type = lines[coord_start].strip()[0]
            coord_start += 1
            
            atoms = []
            atom_idx = 1
            for i, count in enumerate(elem_counts):
                elem = elem_names[i]
                for j in range(count):
                    line_idx = coord_start + atom_idx - 1
                    parts = lines[line_idx].split()
                    coords = np.array([float(parts[0]), float(parts[1]), float(parts[2])])
                    tags = parts[3:] if len(parts) > 3 else []
                    
                    if coord_type in ['D', 'd']:
                        cart_coords = np.dot(coords, cell)
                        dir_coords = coords
                    else:
                        cart_coords = coords
                        dir_coords = np.dot(coords, inv_cell)
                        
                    atoms.append({
                        "idx": atom_idx, "line_idx": line_idx, 
                        "elem": elem, "cart": cart_coords, 
                        "dir": dir_coords, "tags": tags
                    })
                    atom_idx += 1

            # --- OTONOM HEDEF BULMA ---
            target_element = st.selectbox("Hangi Element Difüze Olacak?", elem_names, index=elem_names.index('H') if 'H' in elem_names else 0)
            
            target_atoms = [a for a in atoms if a["elem"] == target_element]
            target_atoms.sort(key=lambda x: x["cart"][2], reverse=True)
            highest_atom = target_atoms[0]
            
            st.info(f"🎯 **Hedef:** Z-eksenindeki en yüksek **{highest_atom['elem']} atomu (Sıra: {highest_atom['idx']})**. (Z = {highest_atom['cart'][2]:.3f} Å)")

            # --- KAYDIRMA VE ÇARPIŞMA AYARLARI ---
            c1, c2, c3 = st.columns(3)
            with c1:
                direction = st.selectbox("Kaydırma Yönü", ["+X Yönü", "-X Yönü", "+Y Yönü", "-Y Yönü"])
            with c2:
                shift_dist = st.number_input("Mesafe (Å)", value=1.5, step=0.1)
            with c3:
                safe_radius = st.number_input("Güvenli Yarıçap (Å)", value=0.9, step=0.1, help="İki atom bu değerden daha fazla yaklaşırsa sistem uyarı verir.")

            if st.button("🚀 Otonom FS POSCAR Üret"):
                shift_vec = np.array([0.0, 0.0, 0.0])
                if direction == "+X Yönü": shift_vec[0] = shift_dist
                elif direction == "-X Yönü": shift_vec[0] = -shift_dist
                elif direction == "+Y Yönü": shift_vec[1] = shift_dist
                elif direction == "-Y Yönü": shift_vec[1] = -shift_dist

                new_cart = highest_atom["cart"] + shift_vec
                new_dir = np.dot(new_cart, inv_cell) % 1.0  # Periyodik sınırları koru
                new_cart_pbc = np.dot(new_dir, cell) # Gerçek fiziksel koordinat
                
                # 🚨 ÇARPIŞMA SENSÖRÜ (Minimum Image Convention) 🚨
                collision = False
                for other_atom in atoms:
                    if other_atom["idx"] == highest_atom["idx"]:
                        continue # Kendisiyle çarpışmayı kontrol etme
                    
                    # İki atom arasındaki periyodik mesafeyi hesapla
                    diff_dir = new_dir - other_atom["dir"]
                    diff_dir = diff_dir - np.round(diff_dir) # Hücre dışına taşmaları düzeltir
                    dist = np.linalg.norm(np.dot(diff_dir, cell))
                    
                    if dist < safe_radius:
                        st.error(f"⚠️ **ÇARPIŞMA UYARISI!** Kaydırmak istediğiniz nokta, {other_atom['idx']}. sıradaki **{other_atom['elem']}** atomuna çok yakın! (Mesafe: {dist:.2f} Å). Lütfen kaydırma yönünü veya mesafesini değiştirin.")
                        collision = True
                        break
                
                # 🚨 ÇARPIŞMA SENSÖRÜ (Minimum Image Convention) 🚨
                # ... (Buradaki for döngüsü ve çarpışma kontrolü aynı kalacak) ...
                
                if not collision:
                    # ORİJİNAL DOSYANIN FORMATINA GÖRE YAZDIRMA (Kritik Düzeltme)
                    if coord_type in ['D', 'd']:
                        final_write_coords = new_dir
                    else:
                        final_write_coords = new_cart_pbc # PBC uygulanmış Cartesian koordinat
                        
                    # Seçilen formata göre yeni satırı oluştur
                    new_line = f"  {final_write_coords[0]:.10f}  {final_write_coords[1]:.10f}  {final_write_coords[2]:.10f}"
                    if highest_atom["tags"]:
                        new_line += "  " + "  ".join(highest_atom["tags"])
                        
                    lines[highest_atom["line_idx"]] = new_line
                    output_poscar = "\n".join(lines)
                    
                    st.success(f"✅ Çarpışma Testi Geçildi! Atom {coord_type} formatında güvenli bir bölgeye kaydırıldı.")
                    st.download_button("📥 POSCAR_FS Dosyasını İndir", data=output_poscar, file_name="POSCAR_FS", mime="text/plain")

        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
# ==========================================
# MODÜL 28: OTONOM KÜTLE İÇİ DİFÜZYON (VACANCY) - ORIGIN STYLE & PBC AWARE
# ==========================================
elif secim == "🌌 Otonom Kütle İçi Difüzyon (Vacancy)":
    st.header("Otonom Kütle İçi (Bulk) Difüzyon Jeneratörü")
    st.markdown("Birim hücrenizi yükleyin. Bu modül; otonom olarak süper hücre oluşturur, merkezde bir boşluk (vacancy) yaratır (IS), Periyodik Sınır Koşullarını (PBC) gözeterek en yakın komşu atomu bulup bu boşluğa taşır (FS) ve NEB yolundaki çarpışmaları denetler.")
    st.markdown("---")

    # --- HAFIZA (SESSION STATE) TANIMLAMALARI ---
    if "vac_is_data" not in st.session_state:
        st.session_state.vac_is_data = None
        st.session_state.vac_fs_data = None
        st.session_state.vac_msg = ""
        st.session_state.vac_initial_count = 0  
        st.session_state.vac_final_count = 0    

    poscar_file = st.file_uploader("Birim Hücre (Unit Cell) POSCAR Dosyasını Yükle", key="vac_uploader")

    if poscar_file is not None:
        try:
            lines = poscar_file.getvalue().decode("utf-8").splitlines()
            
            scale = float(lines[1].strip())
            unit_cell = np.array([[float(x) for x in line.split()] for line in lines[2:5]]) * scale
            elem_names = lines[5].split()
            elem_counts = [int(x) for x in lines[6].split()]
            
            coord_start = 8 if lines[7].strip()[0] in ['S', 's'] else 7
            coord_type = lines[coord_start].strip()[0]
            coord_start += 1
            
            unit_atoms = []
            for i, count in enumerate(elem_counts):
                elem = elem_names[i]
                for j in range(count):
                    parts = lines[coord_start].split()
                    coords = np.array([float(parts[0]), float(parts[1]), float(parts[2])])
                    if coord_type in ['C', 'c', 'K', 'k']: 
                        coords = np.dot(coords, np.linalg.inv(unit_cell))
                    unit_atoms.append({"elem": elem, "dir": coords})
                    coord_start += 1

            st.success(f"✅ Birim hücre okundu. Boyutlar: a={np.linalg.norm(unit_cell[0]):.2f}Å, b={np.linalg.norm(unit_cell[1]):.2f}Å, c={np.linalg.norm(unit_cell[2]):.2f}Å")

            c1, c2, c3 = st.columns(3)
            nx = c1.number_input("X Çoğaltma", min_value=1, value=2, key="vac_nx")
            ny = c2.number_input("Y Çoğaltma", min_value=1, value=2, key="vac_ny")
            nz = c3.number_input("Z Çoğaltma", min_value=1, value=2, key="vac_nz")
            
            if st.button("🏗️ Sistemi İnşa Et ve Difüzyonu Analiz Et"):
                super_cell = np.array([unit_cell[0]*nx, unit_cell[1]*ny, unit_cell[2]*nz])
                inv_super = np.linalg.inv(super_cell) # YENİ: PBC için ters matris
                
                super_atoms = []
                for x in range(nx):
                    for y in range(ny):
                        for z in range(nz):
                            for atom in unit_atoms:
                                new_dir = (atom["dir"] + np.array([x, y, z])) / [nx, ny, nz]
                                new_cart = np.dot(new_dir, super_cell)
                                super_atoms.append({
                                    "elem": atom["elem"], 
                                    "dir": new_dir, 
                                    "cart": new_cart,
                                    "id": len(super_atoms)
                                })
                
                st.session_state.vac_initial_count = len(super_atoms)
                st.session_state.vac_final_count = len(super_atoms) - 1

                target_element = 'H' if 'H' in elem_names else elem_names[-1]
                
                # Merkezdeki atomu (Koparılacak atomu) bulma (Burası klasik mesafe ile olabilir, kutunun ortası sonuçta)
                center_cart = np.dot(np.array([0.5, 0.5, 0.5]), super_cell)
                target_atoms = [a for a in super_atoms if a["elem"] == target_element]
                target_atoms.sort(key=lambda a: np.linalg.norm(a["cart"] - center_cart))
                vac_atom = target_atoms[0] 
                
                # YENİ: En yakın komşuyu PBC'ye (Minimum Image Convention) göre bul!
                other_targets = [a for a in target_atoms if a["id"] != vac_atom["id"]]
                
                for a in other_targets:
                    d_dir = np.dot(a["cart"] - vac_atom["cart"], inv_super)
                    d_dir = d_dir - np.round(d_dir) # Sınırları aşanları en kısa yola çek
                    a["pbc_dist"] = np.linalg.norm(np.dot(d_dir, super_cell))
                
                other_targets.sort(key=lambda a: a["pbc_dist"])
                move_atom = other_targets[0] 
                jump_dist = move_atom["pbc_dist"]

                # YENİ: Çarpışma rotasını PBC'ye göre çiz
                collision = False
                steps = 5
                
                # Rotanın gerçek en kısa vektörü
                path_vector_dir = np.dot(vac_atom["cart"] - move_atom["cart"], inv_super)
                path_vector_dir = path_vector_dir - np.round(path_vector_dir)
                path_vector_cart = np.dot(path_vector_dir, super_cell)
                
                for step in range(1, steps):
                    test_point_cart = move_atom["cart"] + path_vector_cart * (step / steps)
                    for stationary_atom in super_atoms:
                        if stationary_atom["id"] not in [vac_atom["id"], move_atom["id"]]:
                            # Çarpışma kontrolünde de PBC şarttır
                            d_dir = np.dot(stationary_atom["cart"] - test_point_cart, inv_super)
                            d_dir = d_dir - np.round(d_dir)
                            dist = np.linalg.norm(np.dot(d_dir, super_cell))
                            
                            if dist < 0.8: 
                                st.error(f"⚠️ Çarpışma Tespit Edildi! {target_element} atomu bir {stationary_atom['elem']} atomuna {dist:.2f} Å kadar yaklaşıyor.")
                                collision = True
                                break
                    if collision: break

                if not collision:
                    st.session_state.vac_msg = f"✅ Yol temiz! Merkezdeki {target_element} atomu silindi (Boşluk Yaratıldı). Komşu atom ({jump_dist:.2f} Å uzaktaki gerçek en yakın komşu) bu boşluğa başarıyla taşındı."
                    
                    # YENİ: Cartesian yerine Direct (Kesirli) koordinat sistemi ve "% 1.0" kuralı
                    def generate_poscar_string(atoms_list, cell, inv_cell, e_names, target_id=None, tag_message=""):
                        lines = ["Otonom_Bulk_Vacancy_Diffusion", "1.0"]
                        for row in cell: lines.append(f"  {row[0]:.6f}  {row[1]:.6f}  {row[2]:.6f}")
                        lines.append("  " + "  ".join(e_names))
                        
                        actual_counts = [str(sum(1 for a in atoms_list if a["elem"] == elem)) for elem in e_names]
                        lines.append("  " + "  ".join(actual_counts))
                        
                        lines.append("Direct")
                        for elem in e_names:
                            for a in atoms_list:
                                if a["elem"] == elem:
                                    # Mod 1.0 alarak atomların kutu sınırından çıkmasını önlüyoruz
                                    frac = np.round(np.dot(a["cart"], inv_cell), 8)
                                    line_str = f"  {frac[0]:.6f}  {frac[1]:.6f}  {frac[2]:.6f}"
                                    if target_id is not None and a["id"] == target_id:
                                        line_str += f"  # <-- {tag_message}"
                                    lines.append(line_str)
                        return "\n".join(lines)

                    # IS DOSYASI (Koparılacak atom listeden çıkarılıyor)
                    is_atoms = [a for a in super_atoms if a["id"] != vac_atom["id"]]
                    st.session_state.vac_is_data = generate_poscar_string(
                        is_atoms, super_cell, inv_super, elem_names,
                        target_id=move_atom["id"],
                        tag_message="BOSLUGA_ATLAYACAK_KOMSU (IS)"
                    )

                    # FS DOSYASI (Hareket edecek komşu atom, yaratılan boşluğa taşınıyor)
                    fs_atoms = []
                    for a in is_atoms:
                        if a["id"] == move_atom["id"]:
                            new_a = a.copy()
                            new_a["cart"] = move_atom["cart"] + path_vector_cart
                            fs_atoms.append(new_a)
                        else:
                            fs_atoms.append(a)
                            
                    st.session_state.vac_fs_data = generate_poscar_string(
                        fs_atoms, super_cell, inv_super, elem_names,
                        target_id=move_atom["id"],
                        tag_message="BOSLUGA_OTURAN_ATOM (FS)"
                    )

            # --- HAFIZADAKİ BUTONLARI EKRANA BAS ---
            if st.session_state.vac_is_data and st.session_state.vac_fs_data:
                st.info(f"🧱 İlk Süper Hücre: **{st.session_state.vac_initial_count}** atom. \n🕳️ Boşluk yaratmak için 1 atom silindi. \n📥 İndireceğiniz POSCAR dosyaları **{st.session_state.vac_final_count}** atom içerir.")
                st.success(st.session_state.vac_msg)
                
                c_dl1, c_dl2 = st.columns(2)
                with c_dl1:
                    st.download_button("📥 POSCAR_IS İndir (Boşluklu)", data=st.session_state.vac_is_data, file_name="POSCAR_IS")
                with c_dl2:
                    st.download_button("📥 POSCAR_FS İndir (Taşınmış)", data=st.session_state.vac_fs_data, file_name="POSCAR_FS")

        except Exception as e:
            st.error(f"Hata oluştu: {e}. Dosya formatını kontrol edin.")

# ==========================================
# MODÜL 29: OTONOM ARAYER (INTERSTITIAL) DİFÜZYON
# ==========================================
elif secim == "🌟 Otonom Arayer (Interstitial) Difüzyon":
    st.header("Otonom Arayer (Interstitial) Difüzyon Jeneratörü")
    st.markdown("Hiçbir atomu silmeden, merkezdeki bir hidrojeni koparıp kristal kafes içindeki en fiziksel 'arayer boşluğuna' taşıyarak kusursuz IS ve FS dosyaları üretir.")
    st.markdown("---")

    # --- HAFIZA (SESSION STATE) TANIMLAMALARI ---
    if "int_is_data" not in st.session_state:
        st.session_state.int_is_data = None
        st.session_state.int_fs_data = None
        st.session_state.int_msg = ""
        st.session_state.int_atom_count = 0  

    poscar_file = st.file_uploader("Birim Hücre (Unit Cell) POSCAR Dosyasını Yükle", key="int_uploader")

    if poscar_file is not None:
        try:
            lines = poscar_file.getvalue().decode("utf-8").splitlines()
            
            scale = float(lines[1].strip())
            unit_cell = np.array([[float(x) for x in line.split()] for line in lines[2:5]]) * scale
            elem_names = lines[5].split()
            elem_counts = [int(x) for x in lines[6].split()]
            
            coord_start = 8 if lines[7].strip()[0] in ['S', 's'] else 7
            coord_type = lines[coord_start].strip()[0]
            coord_start += 1
            
            unit_atoms = []
            for i, count in enumerate(elem_counts):
                elem = elem_names[i]
                for j in range(count):
                    parts = lines[coord_start].split()
                    coords = np.array([float(parts[0]), float(parts[1]), float(parts[2])])
                    if coord_type in ['C', 'c', 'K', 'k']: 
                        coords = np.dot(coords, np.linalg.inv(unit_cell))
                    unit_atoms.append({"elem": elem, "dir": coords})
                    coord_start += 1

            st.success("✅ Birim hücre başarıyla okundu.")

            c1, c2, c3 = st.columns(3)
            nx = c1.number_input("X Çoğaltma", min_value=1, value=2, key="int_nx")
            ny = c2.number_input("Y Çoğaltma", min_value=1, value=2, key="int_ny")
            nz = c3.number_input("Z Çoğaltma", min_value=1, value=2, key="int_nz")
            
            if st.button("🚀 Sistemi İnşa Et ve İdeal Arayer Bul"):
                super_cell = np.array([unit_cell[0]*nx, unit_cell[1]*ny, unit_cell[2]*nz])
                inv_super = np.linalg.inv(super_cell) # YENİ: Ters matris (PBC için gerekli)
                
                super_atoms = []
                for x in range(nx):
                    for y in range(ny):
                        for z in range(nz):
                            for atom in unit_atoms:
                                new_dir = (atom["dir"] + np.array([x, y, z])) / [nx, ny, nz]
                                new_cart = np.dot(new_dir, super_cell)
                                super_atoms.append({
                                    "elem": atom["elem"], 
                                    "dir": new_dir, 
                                    "cart": new_cart,
                                    "id": len(super_atoms)
                                })

                st.session_state.int_atom_count = len(super_atoms)
                target_element = 'H' if 'H' in elem_names else elem_names[-1]
                
                center_cart = np.dot(np.array([0.5, 0.5, 0.5]), super_cell)
                target_atoms = [a for a in super_atoms if a["elem"] == target_element]
                target_atoms.sort(key=lambda a: np.linalg.norm(a["cart"] - center_cart))
                move_atom = target_atoms[0] 
                
                candidates = []
                # Küresel tarama
                for r in np.arange(1.2, 2.6, 0.2):
                    for theta in np.linspace(0, np.pi, 8):
                        for phi in np.linspace(0, 2*np.pi, 12):
                            dx = r * np.sin(theta) * np.cos(phi)
                            dy = r * np.sin(theta) * np.sin(phi)
                            dz = r * np.cos(theta)
                            test_cart = move_atom["cart"] + np.array([dx, dy, dz])
                            
                            min_dist = 999.0
                            for a in super_atoms:
                                if a["id"] != move_atom["id"]:
                                    # YENİ: Periyodik Sınır Koşulları (PBC) Uyumu!
                                    d_dir = np.dot(a["cart"] - test_cart, inv_super)
                                    d_dir = d_dir - np.round(d_dir) # -0.5 ile 0.5 arasına sıkıştır (Wrap)
                                    dist = np.linalg.norm(np.dot(d_dir, super_cell))
                                    
                                    if dist < min_dist:
                                        min_dist = dist
                            
                            # Eğer çok fazla atomun üzerine binmiyorsa (Clearance > 1.3 Å) listeye al
                            if min_dist > 1.3: 
                                candidates.append({"pos": test_cart, "clearance": min_dist, "r": r})

                if not candidates:
                    st.error("⚠️ Sistem çok sıkı! Güvenli bir arayer boşluğu bulunamadı.")
                else:
                    # YENİ: En "Boş" olanı DEĞİL, Hidrojen için en ideal bağ mesafesi olanı (Ort. 1.8 Å) seç.
                    ideal_clearance = 1.8 
                    candidates.sort(key=lambda x: abs(x["clearance"] - ideal_clearance))
                    best_void = candidates[0]
                    
                    st.session_state.int_msg = f"✅ En uygun Arayer Boşluğu bulundu! Koparılan atomdan uzaklığı: {best_void['r']:.2f} Å. Yakınlık (Clearance): {best_void['clearance']:.2f} Å."

                    # YENİ: Cartesian yerine Direct (Kesirli) formatta POSCAR üretir ve sınır dışına çıkmasını engeller.
                    def generate_poscar_string(atoms_list, cell, inv_cell, e_names, target_id=None, tag_message=""):
                        lines = ["Otonom_Interstitial_Diffusion", "1.0"]
                        for row in cell: lines.append(f"  {row[0]:.6f}  {row[1]:.6f}  {row[2]:.6f}")
                        lines.append("  " + "  ".join(e_names))
                        
                        actual_counts = [str(sum(1 for a in atoms_list if a["elem"] == elem)) for elem in e_names]
                        lines.append("  " + "  ".join(actual_counts))
                        
                        lines.append("Direct")
                        for elem in e_names:
                            for a in atoms_list:
                                if a["elem"] == elem:
                                    # Koordinatları mod 1 alarak 0 ile 1 arasına sıkıştır (Kutu dışına çıkmayı önler)
                                    frac = np.dot(a["cart"], inv_cell) % 1.0
                                    line_str = f"  {frac[0]:.6f}  {frac[1]:.6f}  {frac[2]:.6f}"
                                    if target_id is not None and a["id"] == target_id:
                                        line_str += f"  # <-- {tag_message}"
                                    lines.append(line_str)
                        return "\n".join(lines)

                    # IS DOSYASI
                    st.session_state.int_is_data = generate_poscar_string(
                        super_atoms, super_cell, inv_super, elem_names, 
                        target_id=move_atom["id"], 
                        tag_message="BURADAN_KOPARILACAK_ATOM (IS)"
                    )

                    # FS DOSYASI
                    fs_atoms = []
                    for a in super_atoms:
                        if a["id"] == move_atom["id"]:
                            new_a = a.copy()
                            new_a["cart"] = best_void["pos"]
                            fs_atoms.append(new_a)
                        else:
                            fs_atoms.append(a)
                            
                    st.session_state.int_fs_data = generate_poscar_string(
                        fs_atoms, super_cell, inv_super, elem_names, 
                        target_id=move_atom["id"], 
                        tag_message="YENI_ARAYER_BOSLUGU_HEDEF (FS)"
                    )

            # --- HAFIZADAN BUTONLARI VE BİLGİLERİ EKRANA BAS ---
            if st.session_state.int_is_data and st.session_state.int_fs_data:
                st.info(f"🧱 Süper Hücre oluşturuldu! Toplam Atom: {st.session_state.int_atom_count}")
                st.success(st.session_state.int_msg)
                
                c_dl1, c_dl2 = st.columns(2)
                with c_dl1:
                    st.download_button("📥 POSCAR_IS İndir (Kusursuz)", data=st.session_state.int_is_data, file_name="POSCAR_IS")
                with c_dl2:
                    st.download_button("📥 POSCAR_FS İndir (Arayere Taşındı)", data=st.session_state.int_fs_data, file_name="POSCAR_FS")

        except Exception as e:
            st.error(f"Hata oluştu: {e}")
# ==========================================
# MODÜL 30: OTONOM NEB YAPI OLUŞTURUCU (YÜZEYE H EKLEME VERSİYONU)
# ==========================================
elif secim == "🤖 Otonom NEB Yapı Oluşturucu-yüzey":
    st.header("Otonom NEB IS/FS Jeneratörü (ASE Tabanlı)")
    st.markdown("Katmanlı slab `POSCAR` dosyanızı yükleyin. Program otomatik olarak süper hücre oluşturur, atomları VASP'a uygun sıralar, alt katmanları dondurur (`F F F`), yüzeye **2 yeni H atomu** ekler (IS) ve ardından bu atomları vakuma taşıyarak H2 gazı (FS) oluşturur.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("1. Girdi Dosyası")
        poscar_file = st.file_uploader("Slab POSCAR Yükle")
        
    with c2:
        st.subheader("2. Fiziksel Parametreler")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1: s_x = st.number_input("Süper X", value=2, min_value=1)
        with col_s2: s_y = st.number_input("Süper Y", value=2, min_value=1)
        with col_s3: s_z = st.number_input("Süper Z", value=1, min_value=1)
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1: layer_tol = st.number_input("Katman Toleransı (Å)", value=0.8, step=0.1)
        with col_p2: h_ekleme_z = st.number_input("Yüzey-H Mesafesi (Å)", value=1.6, step=0.1)
        with col_p3: desorp_dist = st.number_input("Vakum Uçuşu (Å)", value=4.0, step=0.5)

    st.markdown("---")

    if st.button("IS ve FS Yapılarını Oluştur", type="primary"):
        if poscar_file is None:
            st.error("Lütfen bir POSCAR dosyası yükleyin!")
        else:
            try:

                with tempfile.NamedTemporaryFile(delete=False, mode="wb") as temp_in:
                    temp_in.write(poscar_file.getvalue())
                    temp_in_path = temp_in.name

                atoms = read(temp_in_path, format='vasp')
                st.write(f"✅ **Başarılı:** Slab okundu. Temel hücrede {len(atoms)} atom var.")

                # --- 1. ORİJİNAL ELEMENT SIRASINI BUL (K, Ti, H gibi) ---
                orig_symbols = atoms.get_chemical_symbols()
                element_order = []
                for sym in orig_symbols:
                    if sym not in element_order:
                        element_order.append(sym)
                if 'H' not in element_order:
                    element_order.append('H') # Eğer yapıda hiç H yoksa listeye ekle

                # --- 2. SÜPER HÜCRE ---
                atoms_super = atoms.repeat((s_x, s_y, s_z))
                st.write(f"✅ **Süper Hücre Oluşturuldu:** ({s_x}x{s_y}x{s_z}) | Toplam {len(atoms_super)} atom.")

                # --- 3. YÜZEYİ BUL VE 2 YENİ H EKLE ---
                z_coords_super = atoms_super.positions[:, 2]
                max_z = np.max(z_coords_super)
                surface_indices = [i for i, z in enumerate(z_coords_super) if abs(z - max_z) < 1.0]
                
                min_dist = float('inf')
                best_pair = (surface_indices[0], surface_indices[1]) if len(surface_indices) > 1 else (0, 0)
                for i, j in combinations(surface_indices, 2):
                    dist = atoms_super.get_distance(i, j, mic=True)
                    if 1.0 < dist < min_dist:
                        min_dist = dist
                        best_pair = (i, j)

                pos1 = atoms_super.positions[best_pair[0]].copy()
                pos2 = atoms_super.positions[best_pair[1]].copy()
                pos1[2] = max_z + h_ekleme_z
                pos2[2] = max_z + h_ekleme_z

                atoms_super.append(Atom('H', position=pos1))
                atoms_super.append(Atom('H', position=pos2))
                st.write(f"🧪 **IS Kuruldu:** Yüzeyin {h_ekleme_z} Å üzerine 2 adet yeni H atomu eklendi.")

                # --- 4. ATOMLARI VASP'A UYGUN GRUPLA (Sıralama / Sorting) ---
                sorted_indices = []
                for el in element_order:
                    sorted_indices.extend([atom.index for atom in atoms_super if atom.symbol == el])
                atoms_is = atoms_super[sorted_indices]

                # --- 5. KATMAN TANIMA VE DONDURMA (Sıralanmış yapı üzerinden!) ---
                z_coords_is = atoms_is.positions[:, 2]
                z_sorted_indices = np.argsort(z_coords_is)
                
                layers = []
                current_layer = [z_sorted_indices[0]]
                
                for i in range(1, len(z_sorted_indices)):
                    prev_idx = z_sorted_indices[i-1]
                    curr_idx = z_sorted_indices[i]
                    if z_coords_is[curr_idx] - z_coords_is[prev_idx] > layer_tol:
                        layers.append(current_layer)
                        current_layer = [curr_idx]
                    else:
                        current_layer.append(curr_idx)
                layers.append(current_layer)
                
                total_layers = len(layers)
                auto_freeze_count = total_layers // 2
                if auto_freeze_count == 0 and total_layers > 1: auto_freeze_count = 1
                    
                frozen_indices = []
                for i in range(auto_freeze_count):
                    frozen_indices.extend(layers[i])
                    
                constraint = FixAtoms(indices=frozen_indices)
                atoms_is.set_constraint(constraint)
                
                st.write(f"🛡️ **Zırhlama Başarılı:** {total_layers} katmandan alt {auto_freeze_count} katman ({len(frozen_indices)} atom) kilitlendi (F F F).")

                is_stream = io.StringIO()
                write(is_stream, atoms_is, format='vasp', direct=False)
                is_text = is_stream.getvalue()

                # --- 6. VAKUMA TAŞIMA (FS_POSCAR) ---
                atoms_fs = atoms_is.copy()
                
                # Eklenen H'leri bul (En yüksek Z koordinatına sahip 2 H atomu)
                h_indices = [atom.index for atom in atoms_fs if atom.symbol == 'H']
                h_indices_by_z = sorted(h_indices, key=lambda idx: atoms_fs.positions[idx, 2], reverse=True)
                h1_idx, h2_idx = h_indices_by_z[0], h_indices_by_z[1]

                # H atomlarını havaya kaldır ve H2 bağı (0.74 A) yap
                atoms_fs.positions[h1_idx, 2] += desorp_dist
                atoms_fs.positions[h2_idx, 2] += desorp_dist
                atoms_fs.set_distance(h1_idx, h2_idx, 0.74, fix=0.5, mic=True)
                atoms_fs.set_constraint(constraint)

                c_axis_length = atoms_fs.get_cell()[2, 2]
                new_z_pos = atoms_fs.positions[h1_idx, 2]
                if (c_axis_length - new_z_pos) < 2.0:
                    st.warning(f"⚠️ DİKKAT: H2 molekülü hücrenin üst vakum sınırına çok yaklaştı! Vakum boşluğunu artırmanız gerekebilir.")

                st.write(f"☁️ **FS Kuruldu:** Yüzeydeki H atomları {desorp_dist} Å daha yukarı taşındı ve H2 gazı (0.74 Å) oluşturuldu.")

                fs_stream = io.StringIO()
                write(fs_stream, atoms_fs, format='vasp', direct=False)
                fs_text = fs_stream.getvalue()

                # Temizlik
                os.remove(temp_in_path)

                # --- 7. İNDİRME BUTONLARI ---
                st.success("Tüm işlemler kusursuz tamamlandı! Orijinal element sırasına (K Ti H) sadık kalındı.")
                
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.download_button("📥 IS_POSCAR İndir", data=is_text, file_name="IS_POSCAR", mime="text/plain")
                with dl_col2:
                    st.download_button("📥 FS_POSCAR İndir", data=fs_text, file_name="FS_POSCAR", mime="text/plain")

            except Exception as e:
                st.error(f"Kritik Hata: İşlem sırasında bir sorun oluştu. Detay: {e}")
# ==========================================
# MODÜL 12: OTONOM NEB YAPI OLUŞTURUCU (HOLLOW SITE & MAX UZAKLIK)
# ==========================================
elif secim == "🤖 Otonom NEB Yapı Oluşturucu-hollow":
    st.header("Otonom NEB IS/FS Jeneratörü (Hollow Site Algoritması)")
    st.markdown("Bu modül, H2 gazı oluşumunu önlemek için H atomlarını yüzeyin tepe noktalarına değil, **en derin çukurlarına (hollow sites)** ve birbirlerinden **mümkün olan en uzak mesafeye** otomatik olarak yerleştirir.")
    st.markdown("---")

    # --- KONTROL PANELİ ---
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("1. Girdi Dosyası")
        poscar_file = st.file_uploader("Slab POSCAR Yükle")
        
    with c2:
        st.subheader("2. Fiziksel Parametreler")
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1: s_x = st.number_input("Süper X", value=2, min_value=1)
        with col_s2: s_y = st.number_input("Süper Y", value=2, min_value=1)
        with col_s3: s_z = st.number_input("Süper Z", value=1, min_value=1)
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1: layer_tol = st.number_input("Katman Toleransı (Å)", value=0.8, step=0.1)
        with col_p2: h_ekleme_z = st.number_input("Çukur Derinliği (+Z Å)", value=0.9, step=0.1)
        with col_p3: desorp_dist = st.number_input("Vakum Uçuşu (Å)", value=4.0, step=0.5)

    st.markdown("---")

    if st.button("IS ve FS Yapılarını Oluştur", type="primary"):
        if poscar_file is None:
            st.error("Lütfen bir POSCAR dosyası yükleyin!")
        else:
            try:

                with tempfile.NamedTemporaryFile(delete=False, mode="wb") as temp_in:
                    temp_in.write(poscar_file.getvalue())
                    temp_in_path = temp_in.name

                atoms = read(temp_in_path, format='vasp')
                st.write(f"✅ **Başarılı:** Slab okundu. Temel hücrede {len(atoms)} atom var.")

                # --- 1. ORİJİNAL ELEMENT SIRASINI BUL ---
                orig_symbols = atoms.get_chemical_symbols()
                element_order = []
                for sym in orig_symbols:
                    if sym not in element_order:
                        element_order.append(sym)
                if 'H' not in element_order:
                    element_order.append('H')

                # --- 2. SÜPER HÜCRE ---
                atoms_super = atoms.repeat((s_x, s_y, s_z))
                st.write(f"✅ **Süper Hücre Oluşturuldu:** ({s_x}x{s_y}x{s_z}) | Toplam {len(atoms_super)} atom.")

                # --- 3. HOLLOW SİTELARI BULMA ---
                z_coords_super = atoms_super.positions[:, 2]
                max_z = np.max(z_coords_super)
                surface_indices = [i for i, z in enumerate(z_coords_super) if abs(z - max_z) < 1.5]
                
                hollow_sites = []
                # Yüzeydeki atomların 3'lü gruplarını tarayarak çukurları (merkezleri) bul
                for triplet in combinations(surface_indices, 3):
                    d1 = atoms_super.get_distance(triplet[0], triplet[1], mic=True)
                    d2 = atoms_super.get_distance(triplet[1], triplet[2], mic=True)
                    d3 = atoms_super.get_distance(triplet[0], triplet[2], mic=True)
                    
                    # 3 atom da birbirine yakınsa (arada koca bir delik yoksa) bu bir hollow sitedır
                    if d1 < 4.5 and d2 < 4.5 and d3 < 4.5:
                        pos0 = atoms_super.positions[triplet[0]]
                        pos1 = atoms_super.positions[triplet[1]]
                        pos2 = atoms_super.positions[triplet[2]]
                        
                        center_x = (pos0[0] + pos1[0] + pos2[0]) / 3.0
                        center_y = (pos0[1] + pos1[1] + pos2[1]) / 3.0
                        hollow_sites.append((center_x, center_y))

                if len(hollow_sites) < 2:
                    st.error("Yeterli hollow site bulunamadı! Yüzey çok düzensiz olabilir.")
                    st.stop()

                # --- 4. BİRBİRİNE EN UZAK İKİ ÇUKURU (HOLLOW SITE) SEÇME ---
                max_dist = 0
                best_sites = (hollow_sites[0], hollow_sites[1])
                
                # Periyodik Sınır Koşulları (PBC) ile en uzak mesafeyi bulmak için sanal bir hücre kuruyoruz
                dummy_cell = atoms_super.get_cell()
                for i, j in combinations(range(len(hollow_sites)), 2):
                    dummy_atoms = Atoms('H2', positions=[
                        [hollow_sites[i][0], hollow_sites[i][1], max_z],
                        [hollow_sites[j][0], hollow_sites[j][1], max_z]
                    ], cell=dummy_cell, pbc=True)
                    
                    dist = dummy_atoms.get_distance(0, 1, mic=True)
                    if dist > max_dist:
                        max_dist = dist
                        best_sites = (hollow_sites[i], hollow_sites[j])

                # Bulunan en uzak iki çukura H atomlarını yerleştir
                pos1 = [best_sites[0][0], best_sites[0][1], max_z + h_ekleme_z]
                pos2 = [best_sites[1][0], best_sites[1][1], max_z + h_ekleme_z]

                atoms_super.append(Atom('H', position=pos1))
                atoms_super.append(Atom('H', position=pos2))
                st.write(f"🧪 **IS Kuruldu:** H atomları yüzeydeki boşluklara, aralarında **{max_dist:.2f} Å** (Maksimum Ulaşılabilir Mesafe) olacak şekilde yerleştirildi.")

                # --- 5. ATOMLARI VASP'A UYGUN GRUPLA ---
                sorted_indices = []
                for el in element_order:
                    sorted_indices.extend([atom.index for atom in atoms_super if atom.symbol == el])
                atoms_is = atoms_super[sorted_indices]

                # --- 6. KATMAN TANIMA VE DONDURMA ---
                z_coords_is = atoms_is.positions[:, 2]
                z_sorted_indices = np.argsort(z_coords_is)
                
                layers = []
                current_layer = [z_sorted_indices[0]]
                
                for i in range(1, len(z_sorted_indices)):
                    prev_idx = z_sorted_indices[i-1]
                    curr_idx = z_sorted_indices[i]
                    if z_coords_is[curr_idx] - z_coords_is[prev_idx] > layer_tol:
                        layers.append(current_layer)
                        current_layer = [curr_idx]
                    else:
                        current_layer.append(curr_idx)
                layers.append(current_layer)
                
                total_layers = len(layers)
                auto_freeze_count = total_layers // 2
                if auto_freeze_count == 0 and total_layers > 1: auto_freeze_count = 1
                    
                frozen_indices = []
                for i in range(auto_freeze_count):
                    frozen_indices.extend(layers[i])
                    
                constraint = FixAtoms(indices=frozen_indices)
                atoms_is.set_constraint(constraint)
                
                st.write(f"🛡️ **Zırhlama Başarılı:** {total_layers} katmandan alt {auto_freeze_count} katman ({len(frozen_indices)} atom) kilitlendi (F F F).")

                is_stream = io.StringIO()
                write(is_stream, atoms_is, format='vasp', direct=False)
                is_text = is_stream.getvalue()

                # --- 7. VAKUMA TAŞIMA (FS_POSCAR) ---
                atoms_fs = atoms_is.copy()
                
                h_indices = [atom.index for atom in atoms_fs if atom.symbol == 'H']
                h_indices_by_z = sorted(h_indices, key=lambda idx: atoms_fs.positions[idx, 2], reverse=True)
                h1_idx, h2_idx = h_indices_by_z[0], h_indices_by_z[1]

                # H atomlarını vakumda birleştir (0.74 Å)
                atoms_fs.positions[h1_idx, 2] += desorp_dist
                atoms_fs.positions[h2_idx, 2] += desorp_dist
                atoms_fs.set_distance(h1_idx, h2_idx, 0.74, fix=0.5, mic=True)
                atoms_fs.set_constraint(constraint)

                st.write(f"☁️ **FS Kuruldu:** H atomları yüzeyden koparılarak {desorp_dist} Å yukarıda birleşti (H2 bağı: 0.74 Å).")

                fs_stream = io.StringIO()
                write(fs_stream, atoms_fs, format='vasp', direct=False)
                fs_text = fs_stream.getvalue()

                os.remove(temp_in_path)

                # --- 8. İNDİRME BUTONLARI ---
                st.success("Tüm işlemler kusursuz tamamlandı! H2 birleşme problemi algoritma ile çözüldü.")
                
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.download_button("📥 IS_POSCAR İndir", data=is_text, file_name="IS_POSCAR", mime="text/plain")
                with dl_col2:
                    st.download_button("📥 FS_POSCAR İndir", data=fs_text, file_name="FS_POSCAR", mime="text/plain")

            except Exception as e:
                st.error(f"Kritik Hata: İşlem sırasında bir sorun oluştu. Detay: {e}")
                # ==========================================
# MODÜL 30: ELASTİK SABİTLER VE ÖZELLİKLER (Cij -> Sij, VRH, Hardness)
# ==========================================
elif secim == "🧱 Elastik Özellikler ve Modüller":
    st.header("Kapsamlı Elastik Özellikler Hesaplayıcı")
    st.markdown("6x6 Elastik Sabitler ($C_{ij}$) matrisini girerek; Voigt-Reuss-Hill ortalamalarını, mekanik modülleri, anizotropi indekslerini, ses hızlarını, Debye sıcaklığını ve ampirik sertlik değerlerini hesaplayın.")
    st.markdown("---")

    # Fiziksel Sabitler
    PLANCK_CONSTANT_H = 6.62607015e-34 # J*s
    BOLTZMANN_CONSTANT_KB = 1.380649e-23 # J/K
    AVOGADRO_NUMBER_NA = 6.02214076e23 # 1/mol

    # --- 1. MATEMATİKSEL FONKSİYONLAR ---
    def cij_to_sij(cij_matrix):
        try:
            det = np.linalg.det(cij_matrix)
            if abs(det) < 1e-12:
                 return None, f"HATA: Matris tekil (singular). Determinant çok küçük ({det:.2e})."
            return np.linalg.inv(cij_matrix), None
        except Exception as e:
            return None, f"Hata: {e}"

    def calculate_vrh_averages(cij, sij):
        try:
            Bv = (cij[0,0] + cij[1,1] + cij[2,2] + 2*(cij[0,1] + cij[0,2] + cij[1,2])) / 9.0
            Gv = ((cij[0,0]+cij[1,1]+cij[2,2]) - (cij[0,1]+cij[0,2]+cij[1,2]) + 3*(cij[3,3]+cij[4,4]+cij[5,5])) / 15.0
            
            sum_S_B = sij[0,0] + sij[1,1] + sij[2,2] + 2*(sij[0,1] + sij[0,2] + sij[1,2])
            Br = 1.0 / sum_S_B if abs(sum_S_B) > 1e-12 else float('inf')
            
            sum_S_G_denom = 4*(sij[0,0]+sij[1,1]+sij[2,2]) - 4*(sij[0,1]+sij[0,2]+sij[1,2]) + 3*(sij[3,3]+sij[4,4]+sij[5,5])
            Gr = 15.0 / sum_S_G_denom if abs(sum_S_G_denom) > 1e-12 else float('inf')
            
            Bh = (Bv + Br) / 2.0
            Gh = (Gv + Gr) / 2.0
            
            return {"B_Voigt (BV)": Bv, "B_Reuss (BR)": Br, "B_Hill (BH)": Bh,
                    "G_Voigt (GV)": Gv, "G_Reuss (GR)": Gr, "G_Hill (GH)": Gh}
        except:
            return None

    def calculate_extended_properties(cij, sij, averages, density, molar_mass, num_elements):
        props = {}
        try:
            Bh = averages.get("B_Hill (BH)", float('nan'))
            Gh = averages.get("G_Hill (GH)", float('nan'))
            Bv = averages.get("B_Voigt (BV)", float('nan'))
            Gr = averages.get("G_Reuss (GR)", float('nan'))
            Br = averages.get("B_Reuss (BR)", float('nan'))
            Gv = averages.get("G_Voigt (GV)", float('nan'))

            # Young, Poisson, Pugh vb.
            Eh = (9 * Bh * Gh) / (3*Bh + Gh) if (3*Bh + Gh) != 0 else float('nan')
            nuH = (3*Bh - 2*Gh) / (6*Bh + 2*Gh) if (6*Bh + 2*Gh) != 0 else float('nan')
            pugh = Bh / Gh if Gh != 0 else float('nan')
            
            # AU Anizotropi
            AU = 5 * (Gv/Gr) + (Bv/Br) - 6 if (Gr!=0 and Br!=0) else float('nan')
            
            # Ses Hızları ve Debye
            vt = vl = vm = theta_D = k_min = float('nan')
            if density > 0:
                Gh_pa = Gh * 1e9; Bh_pa = Bh * 1e9
                if Gh_pa >= 0: vt = math.sqrt(Gh_pa / density)
                if (3*Bh_pa + 4*Gh_pa) >= 0: vl = math.sqrt((3*Bh_pa + 4*Gh_pa) / (3*density))
                if vt > 0 and vl > 0:
                    vm = ( (1/3.0) * (2/(vt**3) + 1/(vl**3)) )**(-1.0/3.0)
                
                if not np.isnan(vm) and molar_mass > 0 and num_elements > 0:
                    term = ((3.0 * num_elements) / (4.0 * math.pi) * (AVOGADRO_NUMBER_NA * density) / molar_mass)**(1.0/3.0)
                    theta_D = (PLANCK_CONSTANT_H / BOLTZMANN_CONSTANT_KB) * term * vm
                    
                    base_power = molar_mass / (num_elements * density * AVOGADRO_NUMBER_NA)
                    k_min = BOLTZMANN_CONSTANT_KB * vm * (base_power**(-2.0/3.0))

            # Sertlik Formülleri (Ampirik)
            H_miao = ((1 - 2 * nuH) * Eh) / (6 * (1 + nuH)) if not np.isnan(nuH) else float('nan')
            k_ratio = Gh/Bh if Bh!=0 else 0
            H_chen = 2 * ((k_ratio**2 * Gh)**0.585) - 3 if (k_ratio**2 * Gh) >= 0 else float('nan')
            H_tian = 0.92 * (k_ratio ** 1.137) * (Gh ** 0.708) if (k_ratio>0 and Gh>0) else float('nan')
            H_teter = 0.151 * Gh
            
            props = {
                "--- Temel Mekanik Özellikler ---": "",
                "Young's Modulus (E)": (Eh, "GPa"),
                "Poisson's Ratio (ν)": (nuH, ""),
                "Pugh's Ratio (B/G)": (pugh, ""),
                "Cauchy Pressure (C12-C44)": (cij[0, 1] - cij[3, 3], "GPa"),
                "Machinability Index (B/C44)": (Bh / cij[3, 3] if cij[3,3]!=0 else float('nan'), ""),
                
                "--- Anizotropi İndeksleri ---": "",
                "Universal Anisotropy (AU)": (AU, ""),
                "Zener Anisotropy (A)": ((2 * cij[3, 3]) / (cij[0, 0] - cij[0, 1]) if (cij[0, 0]-cij[0, 1])!=0 else float('nan'), ""),
                "Compressibility Ratio (Kc/Ka)": ((cij[0,0]+cij[0,1]-2*cij[0,2])/(cij[2,2]-cij[0,2]) if (cij[2,2]-cij[0,2])!=0 else float('nan'), ""),
                
                "--- Akustik ve Termal Özellikler ---": "",
                "Transverse Sound Vel. (vt)": (vt, "m/s"),
                "Longitudinal Sound Vel. (vl)": (vl, "m/s"),
                "Mean Sound Vel. (vm)": (vm, "m/s"),
                "Debye Temperature (θD)": (theta_D, "K"),
                "Min Thermal Conductivity (k_min)": (k_min, "W/(m·K)"),
                
                "--- Sertlik Tahminleri (Hardness) ---": "",
                "Hardness (Miao)": (H_miao, "GPa"),
                "Hardness (Chen)": (H_chen, "GPa"),
                "Hardness (Tian)": (H_tian, "GPa"),
                "Hardness (Teter)": (H_teter, "GPa"),
            }
        except Exception as e:
            st.error(f"Ek özellikler hesaplanırken hata oluştu: {e}")
        return props

    # --- 2. STREAMLIT ARAYÜZÜ ---
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.subheader("1. Elastik Sabitler Matrisi (Cij, GPa)")
        default_matrix = "250.0 100.0 100.0 0.0 0.0 0.0\n100.0 250.0 100.0 0.0 0.0 0.0\n100.0 100.0 250.0 0.0 0.0 0.0\n0.0 0.0 0.0 80.0 0.0 0.0\n0.0 0.0 0.0 0.0 80.0 0.0\n0.0 0.0 0.0 0.0 0.0 80.0"
        matrix_input = st.text_area("6x6 Cij Matrisini yapıştırın (Her satırda 6 sayı boşluklu):", value=default_matrix, height=150)

    with c2:
        st.subheader("2. Fiziksel Parametreler")
        st.info("Akustik ve termal özellikler (Ses hızı, Debye vb.) için gereklidir. İstemiyorsanız 0 bırakın.")
        density_in = st.number_input("Yoğunluk (g/cm³):", value=0.0, step=0.1)
        molar_mass_in = st.number_input("Molar Kütle (g/mol):", value=0.0, step=0.1)
        num_atoms_in = st.number_input("Formüldeki Atom Sayısı:", value=0, step=1)

    if st.button("🚀 Elastik Özellikleri Analiz Et", type="primary"):
        try:
            # Matrisi Parse Et
            lines = [line.strip() for line in matrix_input.strip().splitlines() if line.strip()]
            if len(lines) != 6: st.error("HATA: Matris tam olarak 6 satır olmalıdır."); st.stop()
            
            matrix_data = []
            for line in lines:
                row = [float(x) for x in line.split()]
                if len(row) != 6: st.error("HATA: Her satırda tam 6 sayı olmalıdır."); st.stop()
                matrix_data.append(row)
            
            cij = np.array(matrix_data)
            sij, err = cij_to_sij(cij)
            if err: st.error(err); st.stop()

            # Birimleri Çevir
            dens_kgm3 = density_in * 1000.0
            mass_kgmol = molar_mass_in / 1000.0

            # Hesaplamalar
            vrh = calculate_vrh_averages(cij, sij)
            ext_props = calculate_extended_properties(cij, sij, vrh, dens_kgm3, mass_kgmol, num_atoms_in)

            st.success("✅ Hesaplamalar başarıyla tamamlandı!")

            # --- SONUÇLARI PANDAS İLE ŞIK TABLOLARA ÇEVİRME ---
            st.markdown("### 📊 Sonuç Raporu")
            
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.markdown("**1. Uyumluluk Matrisi (Sij) [1/GPa]**")
                sij_df = pd.DataFrame(sij).applymap(lambda x: f"{x:.4e}" if abs(x)<1e-3 and x!=0 else f"{x:.4f}")
                st.dataframe(sij_df, use_container_width=True)

                st.markdown("**2. Voigt-Reuss-Hill Ortalamaları (GPa)**")
                vrh_df = pd.DataFrame(list(vrh.items()), columns=["Modül Tipi", "Değer (GPa)"])
                vrh_df["Değer (GPa)"] = vrh_df["Değer (GPa)"].apply(lambda x: f"{x:.4f}")
                st.table(vrh_df)

            with col_res2:
                # Genişletilmiş özellikleri kategorilere ayırarak tablo yapma
                current_category = ""
                cat_data = []
                
                for key, val_tuple in ext_props.items():
                    if key.startswith("---"):
                        # Önceki kategoriyi tablo olarak bas
                        if cat_data:
                            df = pd.DataFrame(cat_data, columns=["Özellik", "Değer", "Birim"])
                            st.markdown(f"**{current_category.replace('-', '').strip()}**")
                            st.dataframe(df, use_container_width=True, hide_index=True)
                            cat_data = []
                        current_category = key
                    else:
                        val, unit = val_tuple
                        val_str = "Veri Eksik" if np.isnan(val) else f"{val:.4f}"
                        cat_data.append([key, val_str, unit])
                
                # Son kalan kategoriyi bas
                if cat_data:
                    df = pd.DataFrame(cat_data, columns=["Özellik", "Değer", "Birim"])
                    st.markdown(f"**{current_category.replace('-', '').strip()}**")
                    st.dataframe(df, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Beklenmeyen bir hata oluştu: {e}")
# ==========================================
# MODÜL 32: NEB IDPP ROTA OLUŞTURUCU (ASE İLE)
# ==========================================
elif secim == "🛣️ NEB IDPP Rota Oluşturucu":
    st.header("NEB IDPP Kavisli Rota Üreticisi")
    st.markdown("Başlangıç (IS) ve Bitiş (FS) `POSCAR` dosyalarınızı yükleyin. ASE kütüphanesinin **IDPP algoritması**, atomların birbirine çarpmasını engelleyen güvenli ve kavisli ara imajları otomatik oluştursun ve size tek bir ZIP dosyası olarak versin.")
    st.markdown("---")

    # 1. Dosya Yükleme Alanları
    col1, col2 = st.columns(2)
    with col1:
        st.info("İlk durumdaki stabilize POSCAR (Örn: 00 klasörü)")
        is_file = st.file_uploader("Başlangıç Durumu (IS)", key="is_file")
    with col2:
        st.info("Son durumdaki stabilize POSCAR (Örn: Hedef klasör)")
        fs_file = st.file_uploader("Bitiş Durumu (FS)", key="fs_file")

    # 2. Parametre Ayarları
    n_images = st.number_input("Ara İmaj Sayısı (Sadece aradaki imajlar):", min_value=1, max_value=15, value=5, step=1)

    # 3. Çalıştırma Butonu
    if st.button("🚀 IDPP Rotasını Oluştur ve İndir", type="primary", use_container_width=True):
        if is_file is None or fs_file is None:
            st.error("❌ Lütfen hem Başlangıç hem de Bitiş dosyalarını yükleyin!")
        else:
            with st.spinner("IDPP ile kavisli rota hesaplanıyor... (Bu işlem biraz sürebilir)"):
                try:
                    # Streamlit dosya yükleyicileri RAM'de tutar. ASE'nin okuyabilmesi için
                    # geçici bir çalışma klasörüne kaydediyoruz.
                    with tempfile.TemporaryDirectory() as tmpdir:
                        is_path = os.path.join(tmpdir, "POSCAR_IS")
                        fs_path = os.path.join(tmpdir, "POSCAR_FS")

                        with open(is_path, "wb") as f:
                            f.write(is_file.getbuffer())
                        with open(fs_path, "wb") as f:
                            f.write(fs_file.getbuffer())

                        # --- SİZİN ASE KODUNUZUN BİREBİR AYNISI BURADA BAŞLIYOR ---
                        initial = read(is_path, format="vasp")
                        final = read(fs_path, format="vasp")

                        images = [initial]
                        for i in range(n_images):
                            images.append(initial.copy())
                        images.append(final)

                        neb = NEB(images)
                        neb.interpolate(method='idpp', mic=True)
                        # --- ASE KODUNUZ BURADA BİTİYOR ---

                        # 4. Çıktıları Hazırlama (İndirilecek ZIP dosyası için)
                        out_dir = os.path.join(tmpdir, "neb_outputs")
                        os.makedirs(out_dir, exist_ok=True)

                        # Bütün yolu görselleştirme için kaydetme
                        write(os.path.join(out_dir, 'neb_idpp_yolu.traj'), images)
                        write(os.path.join(out_dir, 'neb_yolu.xyz'), images)

                        # Her imajı 00, 01, 02... şeklinde klasörlere kaydetme
                        for i, image in enumerate(images):
                            folder_name = f"{i:02d}"
                            folder_path = os.path.join(out_dir, folder_name)
                            os.makedirs(folder_path, exist_ok=True)
                            write(os.path.join(folder_path, "POSCAR"), image, format='vasp')

                        # 5. Oluşturulan dosyaları ZIP arşivi yapma (Hafızada)
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                            for root, dirs, files in os.walk(out_dir):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    # Klasör yapısını korumak için relpath kullanıyoruz
                                    arcname = os.path.relpath(file_path, out_dir)
                                    zip_file.write(file_path, arcname)

                        # Ekrana başarı mesajı bas
                        st.success(f"✅ IDPP interpolasyonu başarıyla tamamlandı! Toplam {len(images)} adet klasör (00'dan {len(images)-1:02d}'e kadar) oluşturuldu.")

                        # 6. İndirme Butonunu Gösterme
                        st.download_button(
                            label="📥 Tüm Klasörleri ve Dosyaları İndir (.ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name=f"IDPP_NEB_{n_images}_images.zip",
                            mime="application/zip",
                            type="secondary",
                            use_container_width=True
                        )

                except Exception as e:
                    st.error(f"Sistem Hatası: {str(e)}")
                    st.info("Not: Başlangıç ve Bitiş dosyalarınızın geçerli bir VASP POSCAR formatında olduğundan ve sistemde 'ase' kütüphanesinin yüklü olduğundan emin olun.")
# ==========================================
# MODÜL 32: NEB IDPP ROTA OLUŞTURUCU (ASE İLE)
# ==========================================
elif secim == "🧹 VASP CONTCAR Katlama ve Temizleme Modülü":
    st.header("🧹 VASP CONTCAR Temizleme ve Sınır Katlama (Wrap) Aracı")
    st.markdown("""
    Bu araç geometri optimizasyonu (relaxation) sonrasında periyodik hücre sınırından taşan 
    (örn: `-0.002` veya `1.005`) **Direct** koordinatları `0` ile `1` aralığına katlar (wrap). 
    Aynı zamanda dosyanın altındaki **Velocity (hız) bloklarını** temizleyerek NEB (IS/FS) için pürüzsüz hale getirir.
    """)
    st.markdown("---")

    uploaded_files = st.file_uploader("Temizlenecek CONTCAR/POSCAR Dosyalarını Yükleyin", accept_multiple_files=True)

    if uploaded_files:
        for file in uploaded_files:
            try:
                # Dosyayı satır satır oku
                lines = file.getvalue().decode("utf-8").splitlines()
                output_lines = []
                
                is_direct = False
                coord_start_idx = -1
                num_atoms = 0
                
                # 1. Başlığı ve Atom Sayılarını Oku
                for i, line in enumerate(lines):
                    output_lines.append(line)
                    
                    # VASP 5 formatında 6. indeks (7. satır) atom sayılarıdır
                    if i == 6:
                        counts = [int(x) for x in line.split()]
                        num_atoms = sum(counts)
                        
                    # Koordinat sisteminin tipini bul
                    if line.strip().lower().startswith("direct"):
                        coord_start_idx = i + 1
                        is_direct = True
                        break
                    elif line.strip().lower().startswith("cartesian"):
                        coord_start_idx = i + 1
                        break

                if not is_direct:
                    st.warning(f"⚠️ {file.name}: Bu dosya 'Cartesian' formatta. Sınır katlama işlemi şu an sadece 'Direct' koordinatlar için aktiftir.")
                    continue

                # 2. Koordinatları Oku ve Katla (Wrap)
                for i in range(num_atoms):
                    line = lines[coord_start_idx + i]
                    parts = line.split()
                    
                    # x, y, z değerlerini al
                    x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                    
                    # Numpy % operatörü negatif sayıları harika bir şekilde pozitife (1'den geriye) tamamlar.
                    # Örn: -0.001 % 1.0 = 0.999 | 1.002 % 1.0 = 0.002
                    x_wrap = x % 1.0
                    y_wrap = y % 1.0
                    z_wrap = z % 1.0
                    
                    # Yeni satırı oluştur (VASP standartlarında 6-8 küsurat hanesi yeterlidir)
                    new_line = f"  {x_wrap:.8f}  {y_wrap:.8f}  {z_wrap:.8f}"
                    
                    # Eğer satırın sonunda "T T T" (Selective dynamics) veya yorum (#) varsa onları da koru
                    if len(parts) > 3:
                        new_line += "    " + " ".join(parts[3:])
                        
                    output_lines.append(new_line)
                    
                # 3. İndirilebilir Dosyayı Oluştur
                # Dikkat: coord_start_idx + num_atoms sonrasında döngüyü bitirdiğimiz için
                # aşağıda kalan velocity veya predictor-corrector blokları OTOMATİK olarak silinmiş oldu!
                clean_poscar_data = "\n".join(output_lines)
                
                st.success(f"✅ **{file.name}** başarıyla katlandı ve temizlendi!")
                
                # İndirme Butonu
                new_file_name = f"{file.name}_CLEAN"
                st.download_button(
                    label=f"📥 İndir: {new_file_name}",
                    data=clean_poscar_data,
                    file_name=new_file_name,
                    mime="text/plain",
                    key=file.name
                )

            except Exception as e:
                st.error(f"❌ {file.name} işlenirken hata oluştu: {e}")
                # ==========================================
# MODÜL 28: OTONOM KÜTLE İÇİ DİFÜZYON (CASTEP & ASE PBC)
# ==========================================
elif secim == "🌌 Otonom Kütle İçi Difüzyon (Vacancy) CASTEP":
    st.header("Otonom Kütle İçi (Bulk) Difüzyon Jeneratörü")
    st.markdown("Birim hücrenizi (.cell) yükleyin. Bu modül; otonom olarak süper hücre oluşturur, merkezde bir boşluk (vacancy) yaratır, Periyodik Sınır Koşullarını (PBC) gözeterek en yakın komşu atomu bulup bu boşluğa taşır ve NEB yolundaki çarpışmaları denetler.")
    st.markdown("---")

    # --- HAFIZA (SESSION STATE) TANIMLAMALARI ---
    if "vac_is_data" not in st.session_state:
        st.session_state.vac_is_data = None
        st.session_state.vac_fs_data = None
        st.session_state.vac_msg = ""
        st.session_state.vac_initial_count = 0  
        st.session_state.vac_final_count = 0    

    # DEĞİŞİKLİK 1: .cell dosyası yükleniyor
    cell_file = st.file_uploader("Birim Hücre (Unit Cell) .cell Dosyasını Yükle", key="vac_uploader", type=['cell', 'txt'])

    if cell_file is not None:
        try:

            # ASE'nin dosyayı okuyabilmesi için geçici bir dosyaya yazıyoruz
            with tempfile.NamedTemporaryFile(delete=False, mode="wb") as temp_in:
                temp_in.write(cell_file.getvalue())
                temp_in_path = temp_in.name

            # DEĞİŞİKLİK 2: Okuma formatı 'castep-cell'
            unit_atoms = read(temp_in_path, format='castep-cell')
            
            st.success(f"✅ Birim hücre okundu. Toplam Atom: {len(unit_atoms)} | Boyutlar: a={unit_atoms.cell.lengths()[0]:.2f}Å, b={unit_atoms.cell.lengths()[1]:.2f}Å, c={unit_atoms.cell.lengths()[2]:.2f}Å")

            c1, c2, c3 = st.columns(3)
            nx = c1.number_input("X Çoğaltma", min_value=1, value=2, key="vac_nx")
            ny = c2.number_input("Y Çoğaltma", min_value=1, value=2, key="vac_ny")
            nz = c3.number_input("Z Çoğaltma", min_value=1, value=2, key="vac_nz")
            
            if st.button("🏗️ Sistemi İnşa Et ve Difüzyonu Analiz Et", type="primary"):
                # SÜPER HÜCREYİ ASE İLE OLUŞTUR
                super_atoms = unit_atoms.repeat((nx, ny, nz))
                
                st.session_state.vac_initial_count = len(super_atoms)
                st.session_state.vac_final_count = len(super_atoms) - 1

                # Hedef elementi belirle (H varsa H, yoksa son element)
                symbols = super_atoms.get_chemical_symbols()
                target_element = 'H' if 'H' in symbols else list(set(symbols))[-1]
                
                # Hedef elementin tüm indeksleri
                target_indices = [atom.index for atom in super_atoms if atom.symbol == target_element]
                
                # Merkez koordinatını bul
                center_cart = super_atoms.cell.sum(axis=0) / 2.0
                
                # DEĞİŞİKLİK 3: Merkezdeki atomu bul (Vacancy adayı)
                distances_to_center = np.linalg.norm(super_atoms.positions[target_indices] - center_cart, axis=1)
                vac_idx = target_indices[np.argmin(distances_to_center)]
                vac_pos = super_atoms.positions[vac_idx]
                
                # Diğer hedef atomları listele
                other_targets = [idx for idx in target_indices if idx != vac_idx]
                
                # DEĞİŞİKLİK 4: En yakın komşuyu PBC ile bulma (ASE'nin gücü)
                # get_distances fonksiyonundaki mic=True parametresi Periyodik Sınırları otomatik çözer
                pbc_distances = super_atoms.get_distances(vac_idx, other_targets, mic=True)
                min_idx = np.argmin(pbc_distances)
                move_idx = other_targets[min_idx]
                jump_dist = pbc_distances[min_idx]

                # Rota vektörünü (MIC gözetilerek) al. Vektör: vac_atom'dan -> move_atom'a doğru
                # DÜZELTİLMİŞ SATIR:
                path_vector = super_atoms.get_distance(vac_idx, move_idx, mic=True, vector=True)    

                # ÇARPIŞMA KONTROLÜ (PBC'ye Göre)
                collision = False
                steps = 5
                stationary_indices = [atom.index for atom in super_atoms if atom.index not in [vac_idx, move_idx]]
                
                for step in range(1, steps):
                    # Test noktası vac'dan move'a doğru ilerliyor
                    test_point_cart = vac_pos + path_vector * (step / steps)
                    
                    # Test noktası ile geri kalan tüm atomlar arasındaki mesafeyi ölç (MIC ile)
                    diffs = super_atoms.positions[stationary_indices] - test_point_cart
                    mic_diffs, mic_dists = find_mic(diffs, super_atoms.cell)
                    
                    if np.any(mic_dists < 0.8):
                        col_idx = stationary_indices[np.argmin(mic_dists)]
                        col_elem = super_atoms[col_idx].symbol
                        col_dist = np.min(mic_dists)
                        st.error(f"⚠️ Çarpışma Tespit Edildi! {target_element} atomu bir {col_elem} atomuna {col_dist:.2f} Å kadar yaklaşıyor.")
                        collision = True
                        break

                if not collision:
                    st.session_state.vac_msg = f"✅ Yol temiz! Merkezdeki {target_element} atomu silindi (Boşluk Yaratıldı). Komşu atom ({jump_dist:.2f} Å uzaktaki) bu boşluğa taşındı."
                    
                    # BAŞLANGIÇ (IS) YAPISI: Merkezdeki atomu sil
                    is_atoms = super_atoms.copy()
                    del is_atoms[vac_idx]
                    
                    # DEĞİŞİKLİK 5: CASTEP formatında IS_stream'e yazdır
                    is_stream = io.StringIO()
                    write(is_stream, is_atoms, format='castep-cell')
                    st.session_state.vac_is_data = is_stream.getvalue()

                    # BİTİŞ (FS) YAPISI: Komşu atomu boşluğun eski yerine taşı
                    fs_atoms = is_atoms.copy()
                    # vac_idx silindiği için, move_idx'in listesindeki yeni indeksini bulmalıyız
                    new_move_idx = move_idx if move_idx < vac_idx else move_idx - 1
                    
                    # CASTEP'in kafası karışmasın diye pozisyonu periyodik hücrenin içine alıyoruz (wrap)
                    fs_atoms.positions[new_move_idx] = vac_pos
                    fs_atoms.wrap()
                    
                    fs_stream = io.StringIO()
                    write(fs_stream, fs_atoms, format='castep-cell')
                    st.session_state.vac_fs_data = fs_stream.getvalue()

            # Temp dosyayı temizle
            os.remove(temp_in_path)

            # --- HAFIZADAKİ BUTONLARI EKRANA BAS ---
            if st.session_state.vac_is_data and st.session_state.vac_fs_data:
                st.info(f"🧱 İlk Süper Hücre: **{st.session_state.vac_initial_count}** atom. \n🕳️ Boşluk yaratmak için 1 atom silindi. \n📥 İndireceğiniz .cell dosyaları **{st.session_state.vac_final_count}** atom içerir.")
                st.success(st.session_state.vac_msg)
                
                c_dl1, c_dl2 = st.columns(2)
                with c_dl1:
                    st.download_button("📥 IS.cell İndir (Boşluklu)", data=st.session_state.vac_is_data, file_name="IS.cell", mime="text/plain")
                with c_dl2:
                    st.download_button("📥 FS.cell İndir (Taşınmış)", data=st.session_state.vac_fs_data, file_name="FS.cell", mime="text/plain")

        except Exception as e:
            st.error(f"Hata oluştu: {e}. Dosya formatını kontrol edin.")

# ==========================================
# MODÜL 6: KAPSAMLI A-SINIFI (YELPAZE MSD & ARRHENIUS)
# ==========================================
# st.sidebar vs. menü ayarların varsa buraya entegre edersin.
elif secim == "🌟 Kapsamlı A-Sınıfı (Yelpaze & Arrhenius)":
    st.header("A-Sınıfı Dergi Analizi: Yelpaze MSD ve Arrhenius")
    st.markdown("Farklı sıcaklıklara ait verileri yükleyin. Düşük sıcaklıkları (titreşim gürültüsü) Arrhenius fitinden çıkarmak için yanlarındaki tiki kaldırın. Çıkarılan veriler grafikte şeffaf/içi boş olarak gösterilecektir.")

# --- 1. KULLANICI ARAYÜZÜ (Dinamik Veri Girişi) ---
    st.markdown("### 1. Veri Yükleme Alanı")
    mat_name = st.text_input("Malzeme Formülü (Lejant ve Başlık için):", "K_2NiH_6")
    num_temps = st.number_input("Kaç farklı sıcaklık verisi yükleyeceksiniz?", min_value=2, max_value=10, value=5)

    upload_data = []
    for i in range(int(num_temps)):
        st.markdown(f"**{i+1}. Veri Seti**")
        # Dahil etme tik'ini yerleştirmek için kolonları 4'e çıkardık
        c1, c2, c3, c4 = st.columns([1.5, 1, 2, 2])
        with c1:
            t_val = st.number_input(f"Sıcaklık (K)", value=300.0 + i*150.0, key=f"t_{i}", step=50.0)
        with c2:
            # FİT'E DAHİL ETME KONTROLÜ
            include_fit = st.checkbox("Fit'e Dahil Et", value=True, key=f"inc_{i}", help="Arrhenius (Ea) hesabına katılsın mı?")
        with c3:
            msd_file = st.file_uploader(f"MSD.dat ({t_val} K)", type=["dat", "txt", "csv"], key=f"msd_{i}")
        with c4:
            diff_file = st.file_uploader(f"DIFFUSION.dat ({t_val} K)", type=["dat", "txt", "csv"], key=f"diff_{i}")
        
        if msd_file and diff_file:
            upload_data.append((t_val, msd_file, diff_file, include_fit))
            
    st.markdown("---")

    # --- 2. ADIM: AĞIR VERİ OKUMA VE HESAPLAMA ---
    if len(upload_data) == int(num_temps):
        if st.button("Verileri İşle ve Grafiği Hazırla", type="primary"):
            try:
                # Akıllı Dosya Okuyucu
                def smart_load(uploaded_file):
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, sep=r'\s+', comment='#', header=None, engine='python')
                    return df.dropna().reset_index(drop=True)

                processed_data = []
                all_temperatures = []
                all_diffusion_coeffs = []
                all_includes = []
                max_msd_list = []
                
                max_time = 0
                max_msd = 0
                
                for t_val, m_file, d_file, inc_fit in upload_data:
                    m_df = smart_load(m_file)
                    d_df = smart_load(d_file)
                    
                    final_D = d_df[4].iloc[-1]
                    local_max_msd = m_df[4].max()
                    
                    all_temperatures.append(t_val)
                    all_diffusion_coeffs.append(final_D)
                    all_includes.append(inc_fit)
                    max_msd_list.append(local_max_msd)
                    
                    processed_data.append((t_val, m_df, inc_fit))
                    
                    if m_df[0].iloc[-1] > max_time: max_time = float(m_df[0].iloc[-1])
                    if local_max_msd > max_msd: max_msd = float(local_max_msd)

                # --- SADECE TİKLİ OLANLARLA ARRHENIUS HESABI ---
                T_arr = np.array(all_temperatures)
                D_arr = np.array(all_diffusion_coeffs)
                Inc_arr = np.array(all_includes, dtype=bool)
                
                fit_T = T_arr[Inc_arr]
                fit_D = D_arr[Inc_arr]
                
                kB = 8.617333262e-5  
                
                if len(fit_T) >= 2:
                    slope, intercept, r_value, _, _ = stats.linregress(1/fit_T, np.log(fit_D))
                    Ea_eV = -slope * kB            
                    r_squared = r_value**2
                else:
                    st.error("Fit işlemi için en az 2 sıcaklık seçmelisiniz!")
                    st.stop()
                
                # Hafızaya Atma
                st.session_state.master_ready = True
                st.session_state.master_data = processed_data
                
                st.session_state.all_T = T_arr
                st.session_state.all_D = D_arr
                st.session_state.all_Inc = Inc_arr
                
                st.session_state.master_slope = slope
                st.session_state.master_intercept = intercept
                st.session_state.master_Ea_eV = Ea_eV
                st.session_state.master_R2 = r_squared
                st.session_state.master_max_time = max_time
                st.session_state.master_max_msd = max_msd
                
                # Sayfaya Tablo Olarak Değerleri Basma
                st.success(f"✅ Hesaplama Başarılı! Sadece seçili ({len(fit_T)} adet) veri fite dahil edildi.")
                st.markdown("### 📊 Okunan Ham Veriler")
                
                res_df = pd.DataFrame({
                    "Sıcaklık (K)": T_arr,
                    "Difüzyon Katsayısı (D)": D_arr,
                    "Maksimum MSD": max_msd_list,
                    "Fit'e Dahil?": ["Evet" if i else "Hayır" for i in Inc_arr]
                })
                st.table(res_df.style.format({"Difüzyon Katsayısı (D)": "{:.4e}", "Maksimum MSD": "{:.2f}"}))

            except Exception as e:
                st.error(f"Hata oluştu: {e}")
    elif len(upload_data) > 0:
        st.info(f"Yüklenen set sayısı: {len([x for x in upload_data if x[1] and x[2]])} / {int(num_temps)}. Devam etmek için tüm dosyaları yükleyin.")

    # --- 3. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("master_ready", False):
        
        def_t_max = st.session_state.master_max_time
        def_msd_max = st.session_state.master_max_msd
        
        st.markdown("### ⚙️ Grafik İnce Ayarları")
        with st.expander("📐 Eksen ve Tipografi (Punto) Ayarları", expanded=True):
            c_ay1, c_ay2, c_ay3 = st.columns(3)
            with c_ay1:
                font_labels = st.slider("Eksen Başlıkları (Punto)", 10, 24, 18)
                font_ticks = st.slider("Eksen Rakamları (Punto)", 8, 20, 14)
            with c_ay2:
                font_inner = st.slider("İç Yazılar (a, b, Ea) (Punto)", 10, 24, 16)
                font_leg = st.slider("Lejant (Punto)", 8, 20, 14)
            with c_ay3:
                pos_x = st.slider("(a) ve (b) X Konumu", 0.0, 1.0, 0.04, step=0.01)
                pos_y = st.slider("(a) ve (b) Y Konumu", 0.0, 1.0, 0.94, step=0.01)

            st.markdown("---")
            cx1, cx2, cx3 = st.columns(3)
            with cx1: p_x_max = st.number_input("Panel (a): X Bitiş (fs)", value=float(def_t_max), step=1000.0)
            with cx2: p_x_step = st.number_input("Panel (a): X Aralık", value=float(np.ceil(def_t_max/5)), step=1000.0)
            with cx3: p_y1_max = st.number_input("Panel (a): Y Bitiş (MSD)", value=float(np.ceil(def_msd_max)), step=1.0)

            cy1, cy2, cy3, cy4 = st.columns(4)
            with cy1: p_arr_xmin = st.number_input("Panel (b): 1000/T Min", value=float(np.floor(min(1000/st.session_state.all_T))), step=0.5)
            with cy2: p_arr_xmax = st.number_input("Panel (b): 1000/T Maks", value=float(np.ceil(max(1000/st.session_state.all_T)))+0.5, step=0.5)
            with cy3: p_arr_ymin = st.number_input("Panel (b): ln(D) Min", value=float(np.floor(min(np.log(st.session_state.all_D))))-1.0, step=1.0)
            with cy4: p_arr_ymax = st.number_input("Panel (b): ln(D) Maks", value=float(np.ceil(max(np.log(st.session_state.all_D))))+1.0, step=1.0)

        # 🎨 ÇİZİM BÖLÜMÜ
        fig, axes = plt.subplots(1, 2, figsize=(18, 7.5))
        
        # --- PANEL (a): YELPAZE MSD ---
        ax1 = axes[0]
        num_plots = len(st.session_state.master_data)
        colors = cm.jet(np.linspace(0.1, 0.9, num_plots))
        
        for idx, (t_val, m_df, inc_fit) in enumerate(st.session_state.master_data):
            time_data = m_df[0]
            total_msd = m_df[4]
            # Eğer fit'e dahil değilse çizgiyi biraz daha soluk yapabiliriz
            alpha_val = 1.0 if inc_fit else 0.4
            ls_val = '-' if inc_fit else '--'
            ax1.plot(time_data, total_msd, color=colors[idx], linewidth=3.0, alpha=alpha_val, linestyle=ls_val, label=f"{t_val} K")

        ax1.set_xlabel(r'Time ($t$, fs)', fontweight='bold', fontsize=font_labels, labelpad=10)
        ax1.set_ylabel(r'Total Mean Square Displacement ($\mathbf{\AA}^2$)', fontweight='bold', fontsize=font_labels, labelpad=10)
        ax1.set_xlim(0, p_x_max)
        ax1.set_ylim(0, p_y1_max)
        ax1.xaxis.set_major_locator(MultipleLocator(p_x_step))
        
        ax1.text(pos_x, pos_y, "(a) Temperature-Dependent MSD", transform=ax1.transAxes, fontsize=font_inner, fontweight='bold', va='top')
        ax1.legend(loc='upper left', bbox_to_anchor=(0.02, 0.88), frameon=True, edgecolor='black', ncol=2, fontsize=font_leg).get_frame().set_linewidth(1.2)

        # --- PANEL (b): ARRHENIUS ---
        ax2 = axes[1]
        
        T_all = st.session_state.all_T
        D_all = st.session_state.all_D
        Inc_all = st.session_state.all_Inc
        
        # Tikli (Dahil Edilen) ve Tiksiz (Dışlanan) verileri ayırma
        inv_T_inc = 1000 / T_all[Inc_all]
        ln_D_inc = np.log(D_all[Inc_all])
        
        inv_T_exc = 1000 / T_all[~Inc_all]
        ln_D_exc = np.log(D_all[~Inc_all])
        
        # Tikli noktaları İÇİ DOLU KIRMIZI çiz
        if len(inv_T_inc) > 0:
            ax2.scatter(inv_T_inc, ln_D_inc, color='red', s=160, edgecolor='black', zorder=5, label=f'${mat_name}$ Data (Fitted)')
        
        # Tiksiz (Dışlanan) noktaları İÇİ BOŞ GRİ çiz (Bilimsel dürüstlük)
        if len(inv_T_exc) > 0:
            ax2.scatter(inv_T_exc, ln_D_exc, facecolors='none', edgecolors='grey', s=160, linewidth=2.5, zorder=4, label='Excluded Data')
        
        # Fit Çizgisi (Sadece Tikli verilere göre hesaplanan doğru)
        x_fit_plot = np.linspace(p_arr_xmin, p_arr_xmax, 100)
        y_fit_plot = st.session_state.master_intercept + st.session_state.master_slope * (x_fit_plot / 1000)
        ax2.plot(x_fit_plot, y_fit_plot, color='blue', lw=2.5, ls='--', label='Linear Fit')

        ax2.set_xlabel(r'1000 / T (K$^{-1}$)', fontweight='bold', fontsize=font_labels, labelpad=10)
        ax2.set_ylabel(r'ln($D_{tot}$ / cm$^{2}$s$^{-1}$)', fontweight='bold', fontsize=font_labels, labelpad=10)
        ax2.set_xlim(p_arr_xmin, p_arr_xmax)
        ax2.set_ylim(p_arr_ymin, p_arr_ymax)
        
        ax2.text(pos_x, pos_y, "(b) Arrhenius Plot", transform=ax2.transAxes, fontsize=font_inner, fontweight='bold', va='top')
        ax2.legend(loc='upper right', frameon=True, edgecolor='black', fontsize=font_leg).get_frame().set_linewidth(1.2)

        # Aktivasyon Enerjisi Kutusu
        box_text = f"$E_a = {st.session_state.master_Ea_eV:.3f}$ eV\n$R^2 = {st.session_state.master_R2:.4f}$"
        ax2.text(0.05, 0.05, box_text, transform=ax2.transAxes, fontsize=font_inner, fontweight='bold',
                 bbox=dict(facecolor='white', alpha=0.9, edgecolor='black', boxstyle='round,pad=0.6'))

        # --- ORTAK ORIGIN STYLE EKSEN AYARLARI ---
        for ax in axes:
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))
            ax.yaxis.set_minor_locator(AutoMinorLocator(2))
            ax.tick_params(axis='both', which='major', labelsize=font_ticks, direction='in', length=8, width=2.0, pad=8, top=True, right=True)
            ax.tick_params(axis='both', which='minor', direction='in', length=4, width=1.5, top=True, right=True)
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight('bold')
            for spine in ax.spines.values():
                spine.set_linewidth(2.0)

        plt.tight_layout(pad=3.0, w_pad=4.0)
        st.pyplot(fig)
        
        # İndirme Butonu
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight', dpi=300)
        st.download_button(
            label="📥 A-Sınıfı Yayın Grafiğini İndir (PNG, 300 DPI)",
            data=buf.getvalue(),
            file_name=f"Comprehensive_AIMD_{mat_name}.png",
            mime="image/png"
        )
       # ==========================================
# MODÜL: AIMD KARARLILIK (Sıcaklık/Enerji)
# ==========================================
elif secim == "⏱️ AIMD Kararlılık (Sıcaklık/Enerji)- farklı format":
    st.header("AIMD Kararlılık Analizi (Sıcaklık ve Toplam Enerji)")
    st.markdown("Farklı sıcaklıklarda çalıştırılan AIMD simülasyonlarının zamanla enerji ve sıcaklık dalgalanmalarını dilediğiniz sayıda veri setiyle karşılaştırın.")
    st.markdown("---")

    # --- 1. KULLANICI ARAYÜZÜ (Dinamik Veri Yükleme) ---
    c_mode, c_count, c_time = st.columns([1.5, 1, 1])
    with c_mode:
        plot_mode = st.radio("Hangi veriler çizilsin?", ["İkisi Yan Yana (Both)", "Sadece Sıcaklık", "Sadece Enerji"])
        mode_dict = {"İkisi Yan Yana (Both)": "both", "Sadece Sıcaklık": "temp", "Sadece Enerji": "energy"}
        selected_mode = mode_dict[plot_mode]
    with c_count:
        n_datasets = st.number_input("Kaç Adet AIMD Verisi Karşılaştırılacak?", min_value=1, max_value=8, value=4, step=1)
    with c_time:
        potim_val = st.number_input("Adım Süresi (POTIM, fs):", min_value=0.1, max_value=10.0, value=1.0, step=0.5, help="Zaman sütunu yoksa, adım (tep) değerini fs cinsine çevirir.")

    st.markdown("---")
    st.markdown(f"**AIMD Veri Dosyalarını Yükleyin ({n_datasets} Adet)**")
    
    temp_aimd_data = []
    default_colors = ['#E74C3C', '#3498DB', '#27AE60', '#F39C12', '#9B59B6', '#34495E', '#1ABC9C', '#D35400'] 
    
    cols = st.columns(min(n_datasets, 4))
    for i in range(n_datasets):
        col_idx = i % 4
        with cols[col_idx]:
            c_lbl, c_col = st.columns([3, 1])
            with c_lbl:
                label = st.text_input(f"Etiket {i+1}", value=f"{300 + (i*150)} K", key=f"aimd_lbl_{i}")
            with c_col:
                chosen_color = st.color_picker(f"Renk", value=default_colors[i % len(default_colors)], key=f"aimd_color_{i}")
                
            file = st.file_uploader(f"Dosya {i+1}", type=["dat", "txt", "csv", "out"], key=f"aimd_file_{i}")
            temp_aimd_data.append({"file": file, "label": label, "color": chosen_color})

    st.markdown("---")

    # --- 2. ADIM: AKILLI VERİ OKUMA VE HAFIZAYA ALMA ---
    if st.button("Verileri Oku ve Grafiği Hazırla", type="primary"):
        loaded_datasets = []
        
        global_t_max = 0
        global_temp_min, global_temp_max = 99999, -99999
        global_e_min, global_e_max = 99999, -99999

        try:
            for item in temp_aimd_data:
                if item["file"] is not None:
                    item["file"].seek(0)
                    df = pd.read_csv(item["file"], sep=r'\s+', engine='python')
                    
                    # 1. ZAMAN (fs)
                    if 'Time(fs)' not in df.columns:
                        if 'Time(ps)' in df.columns:
                            df['Time(fs)'] = df['Time(ps)'] * 1000
                        elif 'tep' in df.columns: 
                            df['Time(fs)'] = df['tep'] * potim_val
                        elif 'step' in df.columns.str.lower():
                            step_col = df.columns[df.columns.str.lower() == 'step'][0]
                            df['Time(fs)'] = df[step_col] * potim_val
                        else:
                            df['Time(fs)'] = (df.index + 1) * potim_val

                    # 2. SICAKLIK
                    if 'Temperature(K)' not in df.columns:
                        if 'Temperature_K' in df.columns: 
                            df['Temperature(K)'] = df['Temperature_K']
                        elif 'T(K)' in df.columns:
                            df['Temperature(K)'] = df['T(K)']
                        elif len(df.columns) > 1: # Başlık yoksa bile 2. sütunu al
                            df['Temperature(K)'] = df.iloc[:, 1]

                    # 3. ENERJİ İÇİN SON SÜTUNU OKUMA
                    if 'Energy(eV)' not in df.columns:
                        if 'E_Kinetic_eV' in df.columns: # Son sütununuzun başlığı
                            df['Energy(eV)'] = df['E_Kinetic_eV']
                        elif 'E_Total_eV' in df.columns: 
                            df['Energy(eV)'] = df['E_Total_eV']
                        elif len(df.columns) > 0: # Dosyada sütun varsa
                            df['Energy(eV)'] = df.iloc[:, -1] # -1 her zaman EN SON sütunu alır

                    # Otonom Sınırları Güncelle
                    if 'Time(fs)' in df.columns:
                        global_t_max = max(global_t_max, df['Time(fs)'].max())
                    if 'Temperature(K)' in df.columns:
                        global_temp_min = min(global_temp_min, df['Temperature(K)'].min())
                        global_temp_max = max(global_temp_max, df['Temperature(K)'].max())
                    if 'Energy(eV)' in df.columns:
                        global_e_min = min(global_e_min, df['Energy(eV)'].min())
                        global_e_max = max(global_e_max, df['Energy(eV)'].max())

                    loaded_datasets.append({"df": df, "label": rf"$\mathbf{{{item['label']}}}$", "color": item["color"]})

            if len(loaded_datasets) == 0:
                st.error("HATA: Grafiği çizmek için en az bir adet AIMD veri dosyası yüklemelisiniz!")
            else:
                st.session_state.aimd_ready = True
                st.session_state.aimd_datasets = loaded_datasets
                st.session_state.aimd_mode = selected_mode
                
                st.session_state.aimd_bounds = {
                    "t_max": float(global_t_max) if global_t_max > 0 else 10000.0,
                    "temp_min": float(global_temp_min) if global_temp_min != 99999 else 0.0,
                    "temp_max": float(global_temp_max) if global_temp_max != -99999 else 1000.0,
                    "e_min": float(global_e_min) if global_e_min != 99999 else -200.0,
                    "e_max": float(global_e_max) if global_e_max != -99999 else -100.0
                }
                st.success(f"✅ {len(loaded_datasets)} adet veri seti başarıyla okundu!")

        except Exception as e:
            st.error(f"Veri okuma hatası: Sütun formatı tanınamadı. Detay: {e}")

    # --- 3. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("aimd_ready", False):
        datasets = st.session_state.aimd_datasets
        mode = st.session_state.aimd_mode
        b = st.session_state.aimd_bounds

        # 📐 EKSEN VE İNCE AYAR PANELİ
        with st.expander("📐 Eksen, Lejant ve İndirme Ayarları", expanded=True):
            cx1, cx2, cx3 = st.columns(3)
            with cx1: 
                st.markdown("**1. X Ekseni (Zaman - fs)**")
                p_x_max = st.number_input("Maksimum Zaman (fs)", value=b["t_max"], step=1000.0)
                p_x_step = st.number_input("X Ekseni Adımı (Tick)", value=float(np.ceil(b["t_max"]/5)), step=1000.0)
            
            with cx2:
                st.markdown("**2. Sıcaklık Ekseni (K)**")
                p_t_min = st.number_input("Min Sıcaklık", value=np.floor(b["temp_min"]/50)*50, step=50.0)
                p_t_max = st.number_input("Maks Sıcaklık", value=np.ceil(b["temp_max"]/50)*50, step=50.0)
                p_t_step = st.number_input("Sıcaklık Adımı", value=100.0, step=50.0)

            with cx3:
                st.markdown("**3. Enerji Ekseni (eV)**")
                p_e_min = st.number_input("Min Enerji", value=np.floor(b["e_min"]), step=1.0)
                p_e_max = st.number_input("Maks Enerji", value=np.ceil(b["e_max"]), step=1.0)
                p_e_step = st.number_input("Enerji Adımı", value=2.0, step=1.0)

            st.markdown("---")
            cl1, cl2, cl3 = st.columns(3)
            with cl1:
                p_leg_loc = st.selectbox("Lejant (Etiket) Konumu", ["best", "upper right", "upper left", "lower left", "lower right", "center right", "center"], index=1)
            with cl2:
                p_leg_orient = st.radio("Lejant Dizilimi", ["Dikey (Alt Alta)", "Yatay (Yan Yana)"])
            with cl3:
                p_dpi = st.selectbox("İndirme Çözünürlüğü (DPI)", [300, 600, 1000, 1200], index=1)

            st.markdown("---")
            st.markdown("**4. Grafik Boyutu, Panel Etiketleri ve Malzeme İsmi Ayarları**")
            cb1, cb2, cb3 = st.columns(3)
            with cb1:
                st.markdown("**Boyut & Boşluk**")
                p_fig_width = st.slider("Grafik Genişliği", min_value=5, max_value=40, value=24, step=1)
                p_fig_height = st.slider("Grafik Yüksekliği", min_value=5, max_value=30, value=12, step=1)
                p_wspace = st.slider("Grafikler Arası Boşluk", min_value=0.0, max_value=1.0, value=0.15, step=0.05)
            with cb2:
                st.markdown("**Panel (a)/(b) Konumu**")
                p_panel_x = st.slider("(a)/(b) X Konumu", min_value=-0.2, max_value=1.2, value=0.15, step=0.01)
                p_panel_y = st.slider("(a)/(b) Y Konumu", min_value=-0.2, max_value=1.2, value=0.15, step=0.01)
            with cb3:
                st.markdown("**Malzeme İsmi**")
                p_mat_name = st.text_input("Malzeme İsmi (Örn: MoS_2)", value="")
                p_mat_x = st.slider("Malzeme X Konumu", min_value=-0.2, max_value=1.2, value=0.05, step=0.01)
                p_mat_y = st.slider("Malzeme Y Konumu", min_value=-0.2, max_value=1.2, value=0.92, step=0.01)

        # 🎨 ÇİZİM BÖLÜMÜ

        # Global Font Ayarı: Times New Roman
        plt.rcParams['font.family'] = 'Times New Roman'

        if mode == "temp":
            selected_metrics = [('Temperature(K)', 'Temperature (K)', (p_t_min, p_t_max), p_t_step)]
        elif mode == "energy":
            selected_metrics = [('Energy(eV)', 'Total Energy (eV)', (p_e_min, p_e_max), p_e_step)]
        else:
            selected_metrics = [
                ('Temperature(K)', 'Temperature (K)', (p_t_min, p_t_max), p_t_step), 
                ('Energy(eV)', 'Total Energy (eV)', (p_e_min, p_e_max), p_e_step)
            ]

        num_cols = len(selected_metrics)
        # Genişlik ve yükseklik kullanıcıya bağlandı
        fig, axs = plt.subplots(1, num_cols, figsize=(p_fig_width, p_fig_height), squeeze=False)

        # Lejant kolon sayısını belirleme (Yatay ise veri sayısı kadar yan yana)
        leg_ncol = len(datasets) if p_leg_orient == "Yatay (Yan Yana)" else 1

        panel_labels = ["(a)", "(b)"]

        for col in range(num_cols):
            ax = axs[0, col]
            m_col, ylabel, y_limits, y_step = selected_metrics[col]
            
            for i, data in enumerate(datasets):
                df = data["df"]
                if m_col in df.columns:
                    ax.plot(df['Time(fs)'], df[m_col], color=data["color"], linewidth=2.5, 
                            label=data["label"], alpha=0.85, zorder=10-i)
            
            # Eksen Etiketleri ve Sınırları
            ax.set_ylabel(ylabel, fontsize=24, fontweight='bold', labelpad=20)
            ax.set_xlabel('Time (fs)', fontsize=24, fontweight='bold', labelpad=20)
            ax.set_xlim(0, p_x_max)
            ax.set_ylim(y_limits[0], y_limits[1])

            # Tick (Adım) Ayarları
            ax.xaxis.set_major_locator(MultipleLocator(p_x_step))
            ax.yaxis.set_major_locator(MultipleLocator(y_step))
            ax.xaxis.set_minor_locator(AutoMinorLocator(2))
            ax.yaxis.set_minor_locator(AutoMinorLocator(2))

            # Üst eksen tick'leri (top=False) yapıldı (Hem major hem minor için)
            ax.tick_params(axis='both', which='major', direction='in', length=12, width=2.5, labelsize=20, pad=10, top=False, right=False)
            ax.tick_params(axis='both', which='minor', direction='in', length=6, width=1.5, top=False, right=False)

            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontweight('bold')

            for spine in ax.spines.values():
                spine.set_linewidth(2.5)

            # Panel Etiketini Ekleme (a, b)
            if mode == "both" or num_cols > 1:
                ax.text(p_panel_x, p_panel_y, panel_labels[col], transform=ax.transAxes, 
                        fontsize=26, fontweight='bold', va='center', ha='center')

            # Malzeme İsmi Ekleme (Kullanıcı girdiyse)
            if p_mat_name.strip() != "":
                # LaTeX formatı için süslü parantez içine alıp $ sembolleri ile sarmalıyoruz
                ax.text(p_mat_x, p_mat_y, fr"${p_mat_name}$", transform=ax.transAxes, 
                        fontsize=26, fontweight='bold', va='center', ha='left')

            # Sadece tek panelde (ilk grafikte) lejant göster
            if col == 0:
                ax.legend(loc=p_leg_loc, ncol=leg_ncol, fontsize=20, frameon=True, edgecolor='black', framealpha=0.9).get_frame().set_linewidth(1.5)

        plt.tight_layout(pad=3.0)
        # Grafikler arası mesafe kullanıcı ayarına bağlandı
        fig.subplots_adjust(wspace=p_wspace)

        # Ekrana Basma
        st.pyplot(fig)
        
        # İndirme Butonu (Seçilen DPI değerine göre)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=p_dpi, bbox_inches='tight')
        
        st.download_button(
            label=f"📥 AIMD Grafiğini İndir (PNG, {p_dpi} DPI)",
            data=buf.getvalue(),
            file_name=f"AIMD_{mode}_{p_dpi}dpi.png",
            mime="image/png"
        )
# ==========================================
# MODÜL 33: FONON BAND YAPISI ÇİZİMİ
# ==========================================
elif secim == "🎶 Fonon Band Yapısı":
    st.header("Fonon Band Yapısı Çizimi (Origin Stili)")
    st.markdown("Phonopy veya VASP'tan elde ettiğiniz fonon band verisini yükleyin. K-noktalarını belirleyip yüksek çözünürlüklü makale grafiğinizi saniyeler içinde oluşturun.")
    st.markdown("---")

    # --- 1. VERİ YÜKLEME ---
    st.markdown("### 1. Veri Yükleme")
    uploaded_phonon = st.file_uploader("Fonon Veri Dosyasını Yükleyin (.dat, .txt)", type=["dat", "txt"], key="phonon_file")

    if uploaded_phonon is not None:
        # --- DOSYA OKUMA VE PARÇALAMA ---
        content = uploaded_phonon.getvalue().decode("utf-8").splitlines()
        
        raw_end_points = []
        branches = []
        current_x = []
        current_y = []

        for i, line in enumerate(content):
            line = line.strip()
            
            # K-path dikey çizgilerini (End points) akıllı yakalama
            if line.startswith("# End points"):
                parts = line.split(":")
                # Rakamlar aynı satırdaysa
                if len(parts) > 1 and parts[1].strip() != "":
                    raw_end_points = [float(x) for x in parts[1].split()]
                # Rakamlar bir alt satırdaysa (Sizin verinizdeki durum)
                elif i + 1 < len(content):
                    next_line = content[i+1].strip()
                    if next_line.startswith("#"):
                        nums = next_line.replace("#", "").strip()
                        raw_end_points = [float(x) for x in nums.split()]
                        
            elif line == "":
                if current_x:
                    branches.append((current_x, current_y))
                    current_x, current_y = [], []
            elif not line.startswith("#"):
                try:
                    parts = line.split()
                    if len(parts) >= 2:
                        current_x.append(float(parts[0]))
                        current_y.append(float(parts[1]))
                except ValueError:
                    pass
        
        if current_x:
            branches.append((current_x, current_y))

        st.success(f"✅ Dosya okundu: {len(branches)} adet fonon bandı tespit edildi.")

        # --- 2. K-PATH KOORDİNATLARI (Manuel / Otomatik) ---
        st.markdown("### 2. K-Path Koordinatları (Manuel Kontrol)")
        st.info("Program dikey çizgilerin atılacağı yerleri dosyadan okumaya çalıştı. Eğer yanlışsa veya eksikse, aşağıdaki sayıları aralarında boşluk bırakarak elle düzeltebilirsiniz.")
        
        default_ep_str = " ".join([f"{x:.6f}" for x in raw_end_points])
        ep_input = st.text_input("Dikey K-Path Çizgilerinin X Koordinatları:", value=default_ep_str)
        
        try:
            end_points = [float(x) for x in ep_input.split()]
        except ValueError:
            end_points = []

        if len(end_points) == 0:
            st.error("HATA: K-noktası koordinatları bulunamadı. Lütfen yukarıdaki kutuya X değerlerini (Örn: 0.000 0.124 0.232) elle girin.")
        else:
            # --- 3. K-PATH ETİKETLERİ ---
            st.markdown("### 3. K-Noktası Etiketleri")
            st.markdown("Gamma noktası için sadece **G** veya **Gamma** yazmanız yeterlidir. Ekrana $\Gamma$ olarak basılacaktır.")
            
            k_labels = []
            # Kullanıcının girdiği veya dosyadan okunan koordinat sayısı kadar kutu açılır
            cols_k = st.columns(len(end_points))
            for i, val in enumerate(end_points):
                with cols_k[i]:
                    user_label = st.text_input(f"{val:.3f}", value=f"P{i+1}", key=f"k_lbl_{i}")
                    if user_label.upper() == "G" or user_label.upper() == "GAMMA":
                        k_labels.append(r"$\Gamma$")
                    else:
                        k_labels.append(user_label)

            st.markdown("---")

            # --- 4. GRAFİK İNCE AYARLARI ---
            st.markdown("### 4. Grafik İnce Ayarları")
            with st.expander("📐 Eksen, Çizgi ve Tipografi Ayarları", expanded=True):
                c1, c2, c3 = st.columns(3)
                
                with c1:
                    st.markdown("**Y Ekseni ve Boyut Ayarları**")
                    p_y_min = st.number_input("Min Frekans (THz)", value=-2.0, step=1.0)
                    p_y_max = st.number_input("Maks Frekans (THz)", value=float(np.ceil(max([max(y) for x, y in branches])))+2.0, step=1.0)
                    p_y_step = st.number_input("Y Ekseni Adımı", value=10.0, step=5.0)
                    st.markdown("**Grafik Boyutları**") # EKLENDİ
                    p_fig_width = st.slider("Grafik Genişliği", min_value=3, max_value=20, value=6, step=1)
                    p_fig_height = st.slider("Grafik Yüksekliği", min_value=3, max_value=20, value=8, step=1)
                
                with c2:
                    st.markdown("**Çizgi Stili**")
                    p_line_color = st.color_picker("Band Rengi", value="#0000FF") 
                    p_line_width = st.number_input("Çizgi Kalınlığı", value=2.0, step=0.5)
                    st.markdown("**Kararlılık (y=0) Çizgisi**") # EKLENDİ
                    p_hline = st.checkbox("y=0 Çizgisini Göster", value=True)
                    p_hline_color = st.color_picker("0 Çizgisi Rengi", value="#000000")
                    p_hline_style = st.selectbox("0 Çizgisi Türü", options=["-", "--", "-.", ":"], index=0, help="'-' (Düz), '--' (Kesik), '-.' (Noktalı Kesik), ':' (Noktalı)")
                
                with c3:
                    st.markdown("**Tipografi ve Çıktı**")
                    p_font_label = st.slider("Eksen Başlıkları (Punto)", 14, 28, 22)
                    p_font_tick = st.slider("Eksen Rakamları (Punto)", 12, 24, 18)
                    p_dpi = st.selectbox("İndirme Çözünürlüğü (DPI)", [300, 600, 1000, 1200], index=1)

            # --- 5. ÇİZİM İŞLEMİ ---
            if st.button("🚀 Grafiği Çiz ve Hazırla", type="primary", use_container_width=True):
                # TİMES NEW ROMAN AYARI EKLENDİ
                plt.rcParams['font.family'] = 'Times New Roman'
                
                # GRAFİK BOYUTLARI DİNAMİK YAPILDI
                fig, ax = plt.subplots(figsize=(p_fig_width, p_fig_height)) 

                for x_vals, y_vals in branches:
                    ax.plot(x_vals, y_vals, color=p_line_color, linewidth=p_line_width, alpha=0.9)

                # y=0 ÇİZGİSİ DİNAMİK YAPILDI
                if p_hline:
                    ax.axhline(0, color=p_hline_color, linestyle=p_hline_style, linewidth=1.2, zorder=0)

                for ep in end_points:
                    ax.axvline(x=ep, color='black', linestyle='-', linewidth=1.0, zorder=0)

                ax.set_xlim(end_points[0], end_points[-1])
                ax.set_ylim(p_y_min, p_y_max)

                ax.set_xticks(end_points)
                ax.set_xticklabels(k_labels, fontsize=p_font_tick, fontweight='bold')

                ax.set_ylabel('Frequency (THz)', fontsize=p_font_label, fontweight='bold', labelpad=15)
                ax.yaxis.set_major_locator(MultipleLocator(p_y_step))
                ax.yaxis.set_minor_locator(AutoMinorLocator(2))

                ax.tick_params(axis='y', which='major', direction='in', length=10, width=2.0, labelsize=p_font_tick, right=False)
                ax.tick_params(axis='y', which='minor', direction='in', length=5, width=1.5, right=False)
                ax.tick_params(axis='x', which='major', direction='in', length=0) 
                
                for label in ax.get_yticklabels():
                    label.set_fontweight('bold')
                for spine in ax.spines.values():
                    spine.set_linewidth(2.0)

                plt.tight_layout()
                st.pyplot(fig)

                # --- 6. İNDİRME BUTONU ---
                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=p_dpi, bbox_inches='tight')
                
                st.download_button(
                    label=f"📥 Fonon Band Grafiğini İndir (PNG, {p_dpi} DPI)",
                    data=buf.getvalue(),
                    file_name=f"Phonon_Bands_{p_dpi}dpi.png",
                    mime="image/png",
                    type="secondary",
                    use_container_width=True
                )
# ==========================================
# MODÜL 35: VDOS alternatif
# ==========================================                             
elif secim == "🎵 Titreşim Spektrumu(VDoS) Grafikli":
    st.header("Titreşim Yoğunluk Durumları (Vibrational DoS)")
    st.markdown("VASP/Vaspkit çıktısı olan ham (a.u.) dosyalarınızı yükleyin. Program, atom sayılarını (stokiyometri) kullanarak partial eğrilerin Total eğriyi aşmasını matematiksel olarak engelleyecek ve yayın kalitesinde spektrumlar çizecektir.")

    st.markdown("---")
    
    # --- 1. KULLANICI ARAYÜZÜ (Veri Girişi ve Stokiyometri) ---
    col1, col2, col3 = st.columns(3)
    with col1:
        malzeme_adi = st.text_input("Malzeme Adı (Başlık İçin LaTeX)", r"\mathbf{K_2TiH_5}")
    with col2:
        total_file = st.file_uploader("1. Total VDoS (Örn: TVDOS.dat)", type=["dat", "txt"])
    with col3:
        # Toplam atom sayısı stokiyometrik çarpan için hayati önem taşır
        total_atoms = st.number_input("Birim Hücredeki TOPLAM Atom Sayısı", min_value=1, value=8, help="Örn: K2TiH5 için 2+1+5 = 8")
        
    st.markdown("---")
    
    # --- DİNAMİK PARTIAL DOSYA SİSTEMİ ---
    n_partials = st.number_input("Kaç Adet Kısmi (Partial) Atom Çizeceksiniz?", min_value=0, max_value=6, value=3, step=1)
    
    temp_partials = []
    if n_partials > 0:
        st.markdown("**Partial VDoS Dosyaları ve Stokiyometri Ayarları**")
        p_cols = st.columns(min(n_partials, 3)) # Yan yana max 3 sütun
        
        default_atoms = ["H", "Ti", "K", "O", "C", "N"]
        default_counts = [5, 1, 2, 1, 1, 1] # K2TiH5 varsayılanları için
        
        for i in range(n_partials):
            col_idx = i % 3
            with p_cols[col_idx]:
                p_label = st.text_input(f"{i+1}. Atom Sembolü", value=default_atoms[i] if i < 6 else f"Atom-{i+1}", key=f"plabel_{i}")
                # Hangi atomdan kaç tane olduğunu alıyoruz
                p_count = st.number_input(f"{p_label} Atom Sayısı", min_value=1, value=default_counts[i] if i < 6 else 1, key=f"pcount_{i}")
                p_file = st.file_uploader(f"Dosya ({p_label})", type=["dat", "txt"], key=f"pfile_{i}")
                
                temp_partials.append({"label": p_label, "count": p_count, "file": p_file})
                
    st.markdown("---")

    # --- 2. ADIM: AĞIR VERİ OKUMA VE HAFIZAYA ALMA ---
    if st.button("Verileri Oku ve Grafiği Hazırla", type="primary"):
        if total_file is None:
            st.error("HATA: Grafiği çizmek için en azından 'Total VDoS' dosyasını yüklemelisiniz!")
        else:
            try:
                
                # Streamlit bellek okuyucusu
                def smart_load(uploaded_file):
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, sep=r'\s+', comment='#', names=['Freq', 'Int'])
                    return df.dropna().query('Freq >= 0').reset_index(drop=True)

                total_df = smart_load(total_file)
                
                valid_partials = []
                for p in temp_partials:
                    if p["file"] is not None:
                        pdf = smart_load(p["file"])
                        valid_partials.append({"label": p["label"], "count": p["count"], "df": pdf})

                # Otomatik Sınır Bulucu
                auto_x_max = float(np.ceil(total_df['Freq'].max() / 5) * 5)
                auto_y_max = float(np.ceil(total_df['Int'].max() / 10) * 10)

                # Hafızaya Kaydet
                st.session_state.vdos_ready = True
                st.session_state.vdos_total = total_df
                st.session_state.vdos_partials = valid_partials
                st.session_state.vdos_xmax = auto_x_max
                st.session_state.vdos_ymax = auto_y_max
                st.session_state.vdos_tot_atoms = total_atoms
                
                st.success("✅ Veriler okundu ve Stokiyometrik ayarlar sisteme işlendi!")
                
            except Exception as e:
                st.error(f"Dosya okuma hatası: {e}")

    # --- 3. ADIM: ORIGIN KONTROL PANELİ VE DİNAMİK ÇİZİM ---
    if st.session_state.get("vdos_ready", False):
        
        total_df = st.session_state.vdos_total
        partials = st.session_state.vdos_partials
        def_x = st.session_state.vdos_xmax
        auto_y_max = st.session_state.vdos_ymax
        tot_atoms = st.session_state.vdos_tot_atoms

        st.markdown("### ⚙️ Grafik Türü ve Görünüm Ayarları")
        
        # Grafik Türü Seçimi (Ham vs Normalize)
        p_norm = st.radio("Y-Ekseni Veri Modu (Farklı sıcaklıkları kıyaslamak için Normalize kullanın):", 
                          ["Ham Veri (Raw a.u.)", "Normalize Edilmiş (0 - 1 Arası)"], horizontal=True)

        norm_factor = total_df['Int'].max() if p_norm == "Normalize Edilmiş (0 - 1 Arası)" else 1.0

        # Tepe Noktası (Peak) Bilgisi
        max_idx = total_df['Int'].idxmax()
        peak_freq = total_df['Freq'].iloc[max_idx]
        peak_int = total_df['Int'].iloc[max_idx] / norm_factor

        def_y = 1.2 if p_norm == "Normalize Edilmiş (0 - 1 Arası)" else auto_y_max
        def_y_step = 0.2 if p_norm == "Normalize Edilmiş (0 - 1 Arası)" else float(np.ceil(auto_y_max/6))

        # 📐 EKSEN VE İNCE AYAR PANELİ
        with st.expander("📐 Eksen, Lejant ve Özel Metin Ayarları", expanded=False):
            st.markdown("**1. X Ekseni (Frekans)**")
            cx1, cx2, cx3 = st.columns(3)
            with cx1: p_x_min = st.number_input("X Başlangıç", value=0.0, step=5.0)
            with cx2: p_x_max = st.number_input("X Bitiş", value=float(def_x), step=5.0)
            with cx3: p_x_step = st.number_input("X Aralık (Tick)", value=5.0, step=1.0) # EKSİK OLAN SATIR GELDİ

            st.markdown("**2. Y Ekseni (Şiddet)**")
            cy1, cy2, cy3 = st.columns(3)
            with cy1: p_y_min = st.number_input("Y Başlangıç", value=0.0, step=def_y_step)
            with cy2: p_y_max = st.number_input("Y Bitiş", value=float(def_y), step=def_y_step)
            with cy3: p_y_step = st.number_input("Y Aralık (Tick)", value=float(def_y_step), step=def_y_step/2) # EKSİK OLAN SATIR GELDİ

            st.markdown("**3. Peak (Tepe Noktası) Etiketi Konumu**")
            ct1, ct2 = st.columns(2)
            y_offset = 0.05 if p_norm == "Normalize Edilmiş (0 - 1 Arası)" else (def_y * 0.05)
            with ct1: p_peak_x = st.number_input("Etiket X Konumu", value=float(peak_freq + 1.0), step=1.0)
            with ct2: p_peak_y = st.number_input("Etiket Y Konumu", value=float(peak_int + y_offset), step=def_y_step)
            
            p_leg_loc = st.selectbox("Lejant Konumu", ["best", "upper right", "upper left", "center right"], index=1)

        # 🎨 YENİ: RENK VE ÇİZGİ STİLİ PANELİ
        with st.expander("🎨 Çizgi Renkleri, Kalınlığı ve Stil Ayarları", expanded=True):
            st.markdown("**Total VDoS Çizgisi**")
            tc1, tc2, tc3 = st.columns(3)
            with tc1: t_color = st.color_picker("Total Rengi", "#2c3e50")
            with tc2: t_ls = st.selectbox("Total Çizgi Stili", ["- (Düz)", "-- (Kesik)", "-. (Nokta-Kesik)", ": (Noktalı)"], index=0)
            with tc3: t_lw = st.slider("Total Kalınlık", 1.0, 5.0, 2.5, 0.5)

            if partials:
                st.markdown("**Partial (Kısmi) VDoS Çizgileri**")
                default_colors = ['#e67e22', '#27ae60', '#2980b9', '#8e44ad', '#c0392b', '#f39c12']
                ls_map = {"- (Düz)": "-", "-- (Kesik)": "--", "-. (Nokta-Kesik)": "-.", ": (Noktalı)": ":"}
                
                partial_styles = []
                for i, p in enumerate(partials):
                    pc1, pc2, pc3 = st.columns(3)
                    with pc1: p_c = st.color_picker(f"{p['label']} Rengi", default_colors[i % len(default_colors)], key=f"c_{i}")
                    with pc2: p_ls = st.selectbox(f"{p['label']} Stili", ["- (Düz)", "-- (Kesik)", "-. (Nokta-Kesik)", ": (Noktalı)"], index=1, key=f"ls_{i}")
                    with pc3: p_lw = st.slider(f"{p['label']} Kalınlığı", 1.0, 5.0, 2.0, 0.5, key=f"lw_{i}")
                    
                    partial_styles.append({"color": p_c, "ls": ls_map[p_ls], "lw": p_lw})

        # 🎨 ÇİZİM BÖLÜMÜ

        fig, ax = plt.subplots(figsize=(11, 7))
        t_ls_mapped = {"- (Düz)": "-", "-- (Kesik)": "--", "-. (Nokta-Kesik)": "-.", ": (Noktalı)": ":"}[t_ls]

        # Total Çizimi
        plot_total_y = total_df['Int'] / norm_factor
        ax.plot(total_df['Freq'], plot_total_y, color=t_color, lw=t_lw, ls=t_ls_mapped, label='Total VDoS', zorder=2)
        ax.fill_between(total_df['Freq'], plot_total_y, color=t_color, alpha=0.1, zorder=1)

        # Partial Çizimleri (STOKİYOMETRİK ÇARPAN BURADA UYGULANIYOR)
        for i, p in enumerate(partials):
            style = partial_styles[i]
            # MUCİZE FORMÜL: Değer * (O atomdan kaç tane var / Toplam Atom Sayısı)
            weight = p['count'] / tot_atoms 
            plot_partial_y = (p["df"]['Int'] * weight) / norm_factor
            
            ax.plot(p["df"]['Freq'], plot_partial_y, color=style['color'], lw=style['lw'], ls=style['ls'], label=f'{p["label"]} (Partial)', zorder=3)

        # Tepe Noktası İşaretleme
        ax.annotate(f'$\mathbf{{{peak_freq:.2f}\ THz}}$', 
                    xy=(peak_freq, peak_int), 
                    xytext=(p_peak_x, p_peak_y), 
                    fontsize=14, fontweight='bold', color='red',
                    arrowprops=dict(facecolor='red', shrink=0.05, width=1.5, headwidth=8))

        # Eksen Ayarları
        ax.set_xlim(p_x_min, p_x_max)
        ax.set_ylim(p_y_min, p_y_max) # Y min degerini de arayuzden aliyoruz artik
        
        ax.xaxis.set_major_locator(ticker.MultipleLocator(p_x_step))
        ax.yaxis.set_major_locator(ticker.MultipleLocator(p_y_step)) # Hata vermemesi icin guncellendi
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))

        # Etiketler
        y_label_text = r'$\mathbf{Normalized\ VDoS}$' if p_norm == "Normalize Edilmiş (0 - 1 Arası)" else r'$\mathbf{Vibrational\ Density\ of\ States\ (a.u.)}$'
        
        ax.set_xlabel(r'$\mathbf{Frequency\ (\nu,\ THz)}$', fontsize=16, labelpad=15)
        ax.set_ylabel(y_label_text, fontsize=16, labelpad=15)
        ax.set_title(f'Vibrational Spectra of ${malzeme_adi}$', fontsize=18, pad=20, fontweight='bold')

        # Tick Fontları
        for tick in ax.get_xticklabels() + ax.get_yticklabels():
            tick.set_fontweight('bold')
            tick.set_fontsize(13)

        # Lejant
        ax.legend(loc=p_leg_loc, frameon=False, fontsize=16, ncol=2 if len(partials)>2 else 1, 
                  prop={'weight': 'bold', 'size': 14})
        
        plt.tight_layout()

        # Ekrana Basma
        st.pyplot(fig)
        
        # İndirme Butonu
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight', dpi=600)
        
        clean_name = malzeme_adi.replace('\\', '').replace('{', '').replace('}', '').replace('mathbf', '').replace('_', '')
        st.download_button(
            label="📥 Son Ayarlarla VDoS Grafiğini İndir (PNG, 600 DPI)",
            data=buf.getvalue(),
            file_name=f"{clean_name}_VDoS_Origin.png",
            mime="image/png"
        )
# ==========================================
# MODÜL 35: ÇOKLU SICAKLIK RDF OVERLAY (AYRI DOSYALAR)
# ==========================================
elif secim == "📍 Çoklu Sıcaklık RDF (Overlay)":
    st.header("Sıcaklığa Bağlı RDF Kıyaslama (Overlay)")
    st.markdown("Aynı atom çifti (Örn: H-H) için farklı sıcaklıklara ait **ayrı ayrı** $g(r)$ ve $N(r)$ dosyalarını yükleyerek tek bir makale figüründe (üst üste) kıyaslayın.")

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        rdf_title = st.text_input("Grafik Başlığı (Örn: (a) H-H)", "(a) H-H")
    with col2:
        n_temps = st.number_input("Kaç Farklı Sıcaklık Kıyaslanacak?", min_value=1, max_value=5, value=3, step=1)

    st.markdown("---")
    
    # --- DİNAMİK DOSYA YÜKLEYİCİ (AYRI DOSYALAR İÇİN) ---
    tabs = st.tabs([f"Sıcaklık {i+1}" for i in range(n_temps)])
    datasets_raw = []
    default_labels = ["300 K", "600 K", "900 K", "450 K", "750 K"]
    
    for i in range(n_temps):
        with tabs[i]:
            c1, c2, c3 = st.columns(3)
            with c1:
                label = st.text_input("Sıcaklık Etiketi", value=default_labels[i] if i < 5 else f"{i+1}. Veri", key=f"lbl_{i}")
            with c2:
                rdf_file = st.file_uploader(f"RDF Dosyası ($g(r)$)", type=["dat", "txt"], key=f"rdf_{i}")
            with c3:
                coord_file = st.file_uploader(f"Koordinasyon Dosyası ($N(r)$)", type=["dat", "txt"], key=f"coord_{i}")
                
            datasets_raw.append({"label": label, "rdf_file": rdf_file, "coord_file": coord_file})

    if st.button("Verileri Oku ve Grafiği Hazırla", type="primary"):
        
        valid_datasets = []
        
        # Senin o harika iki sütunlu akıllı okuma fonksiyonun
        def smart_load_st(uploaded_file):
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=r'\s+', header=None, comment='#', engine='python')
            data = pd.DataFrame({
                'X': pd.to_numeric(df.iloc[:, 0], errors='coerce'),
                'Y': pd.to_numeric(df.iloc[:, 1], errors='coerce') 
            })
            return data.dropna().query('X >= 0').reset_index(drop=True)

        for i, data in enumerate(datasets_raw):
            if data["rdf_file"] is not None and data["coord_file"] is not None:
                try:
                    rdf_df = smart_load_st(data["rdf_file"])
                    coord_df = smart_load_st(data["coord_file"])
                    
                    # Otomatik Tepe Bulucu (Sadece g(r) için)
                    max_idx = rdf_df['Y'].idxmax()
                    peak_r = rdf_df['X'].iloc[max_idx]
                    peak_g = rdf_df['Y'].iloc[max_idx]
                    
                    valid_datasets.append({
                        "id": i, "label": data["label"], "rdf_df": rdf_df, "coord_df": coord_df, 
                        "peak_r": peak_r, "peak_g": peak_g
                    })
                except Exception as e:
                    st.error(f"{data['label']} verileri okunamadı: {e}")
        
        if valid_datasets:
            st.session_state.multi_rdf_ready = True
            st.session_state.multi_rdf_data = valid_datasets
            st.success("✅ Tüm sıcaklık verileri başarıyla hafızaya alındı!")
        else:
            st.error("Lütfen en az bir sıcaklık için hem g(r) hem de N(r) dosyalarını yükleyin.")

    # --- KONTROL PANELİ VE ÇİZİM ---
    if st.session_state.get("multi_rdf_ready", False):

        datasets = st.session_state.multi_rdf_data

        # 📐 EKSEN AYARLARI (Tamamen RDF'ye Uyarlandı)
        with st.expander("📐 Eksen Sınırları ve Görünüm", expanded=False):
            cx1, cx2, cx3, cx4 = st.columns(4) 
            
            with cx1: r_max = st.number_input("Maks. X (Mesafe, Å)", value=10.0, step=1.0)
            with cx2: r_step = st.number_input("X Ekseni Adımı", value=2.0, step=1.0)
            
            # GÜVENLİ MAKSİMUM BULUCU (rdf_df ve Y sütunu kullanıldı)
            global_max_g = max([d['rdf_df']['Y'].max() for d in datasets])
            
            with cx3: gr_max = st.number_input("Maks. Y (g(r))", value=float(np.ceil(global_max_g + (global_max_g*0.1))), step=0.5)
            with cx4: nr_max = st.number_input("Maks. Y (N(r))", value=15.0, step=5.0) # N(r) için de sınır eklendi
            
            show_minor_ticks = st.checkbox("Eksenlerde Minör Çentikleri Göster", value=True)
            leg_loc = st.selectbox("Lejant Konumu", ["best", "upper right", "upper left", "center right"], index=1)

        # 🎨 RENK VE TİK (AÇ/KAPAT) AYARLARI
        with st.expander("🎨 Sıcaklıkları Aç/Kapat ve Stilleri Belirle", expanded=True):
            st.markdown("Ana makale için $N(r)$ çizgilerini kapatıp sadece $g(r)$'leri kıyaslayabilirsiniz.")
            
            default_colors = ["#2c3e50", "#2980b9", "#e74c3c", "#27ae60", "#8e44ad"]
            ls_map = {"- (Düz)": "-", "-- (Kesik)": "--", "-. (Nokta-Kesik)": "-.", ": (Noktalı)": ":"}
            plot_settings = []
            
            for i, d in enumerate(datasets):
                st.markdown(f"**{d['label']}**")
                sc1, sc2, sc3, sc4 = st.columns([1, 1, 1, 2])
                
                with sc1:
                    show_g = st.checkbox(f"g(r) Çiz", value=True, key=f"show_g_{i}")
                    c_g = st.color_picker("Renk", default_colors[i % len(default_colors)], key=f"cg_{i}")
                with sc2:
                    show_n = st.checkbox(f"N(r) Çiz", value=False, key=f"show_n_{i}") 
                    ls_n = st.selectbox("N(r) Stili", list(ls_map.keys()), index=1, key=f"lsn_{i}") 
                with sc3:
                    lw = st.slider("Çizgi Kalınlığı", 1.0, 4.0, 3.0, 0.5, key=f"lw_{i}")
                with sc4:
                    add_peak = st.checkbox(f"Tepe Oku ({d['peak_r']:.2f} Å)", value=(i == len(datasets)-1), key=f"peak_{i}")
                    if add_peak:
                        off_x = st.number_input("Ok X", value=float(d['peak_r'] + 0.3), step=0.1, key=f"offx_{i}")
                        off_y = st.number_input("Ok Y", value=float(d['peak_g'] + (gr_max*0.05)), step=0.5, key=f"offy_{i}")
                    else:
                        off_x, off_y = 0, 0
                
                plot_settings.append({
                    "show_g": show_g, "c_g": c_g, "show_n": show_n, "ls_n": ls_map[ls_n], "lw": lw,
                    "add_peak": add_peak, "off_x": off_x, "off_y": off_y
                })
                st.markdown("---")

        # 🎨 ÇİZİM MOTORU
        fig, ax1 = plt.subplots(figsize=(14, 12))
        
        any_nr_shown = any([s['show_n'] for s in plot_settings])
        if any_nr_shown:
            ax2 = ax1.twinx()
            ax2.set_ylabel(r'$\mathbf{Coordination\ (N)}$', fontsize=20, fontweight='bold', color='black', labelpad=25, rotation=270, va='bottom')
            ax2.set_ylim(0, nr_max)
            ax2.tick_params(axis='y', labelsize=16, direction='in', length=8, width=2)
            if show_minor_ticks: ax2.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))
            ax2.spines['right'].set_linewidth(2.0)

        for i, d in enumerate(datasets):
            s = plot_settings[i]
            
            if s['show_g']:
                ax1.plot(d['rdf_df']['X'], d['rdf_df']['Y'], color=s['c_g'], lw=s['lw'], label=f"{d['label']} $g(r)$")
            
            if s['show_n'] and any_nr_shown:
                ax2.plot(d['coord_df']['X'], d['coord_df']['Y'], color=s['c_g'], lw=s['lw']-0.5, ls=s['ls_n'], label=f"{d['label']} $N(r)$")

            if s['add_peak']:
                ax1.annotate(f'$\mathbf{{{d["peak_r"]:.2f}\ \AA}}$', 
                            xy=(d['peak_r'], d['peak_g']), xytext=(s['off_x'], s['off_y']),
                            fontsize=18, fontweight='bold', color=s['c_g'],
                            arrowprops=dict(facecolor=s['c_g'], edgecolor=s['c_g'], shrink=0.05, width=1.5, headwidth=8))

        ax1.set_xlabel(r'$\mathbf{Distance\ (r,\ \AA)}$', fontsize=20, fontweight='bold', labelpad=12)
        ax1.set_ylabel(r'$\mathbf{g(r)}$', fontsize=22, fontweight='bold', color='black', labelpad=12)
        
        # Düzeltilmiş Eksen Sınırları ve Adımları
        ax1.set_xlim(0, r_max)
        ax1.set_ylim(0, gr_max)
        ax1.xaxis.set_major_locator(ticker.MultipleLocator(r_step))
        
        ax1.tick_params(axis='both', labelsize=16, direction='in', length=8, width=2)
        
        if show_minor_ticks:
            ax1.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
            ax1.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))

        ax1.text(0.04, 0.94, f'$\mathbf{{{rdf_title}}}$', transform=ax1.transAxes, fontsize=22, fontweight='bold', va='top')

        lines_1, labels_1 = ax1.get_legend_handles_labels()
        if any_nr_shown:
            lines_2, labels_2 = ax2.get_legend_handles_labels()
            ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc=leg_loc, frameon=False, prop={'weight':'bold', 'size':16})
        else:
            ax1.legend(loc=leg_loc, frameon=False, prop={'weight':'bold', 'size':16})

        for axis in ['top','bottom','left','right']:
            ax1.spines[axis].set_linewidth(2.0)
        for tick in ax1.get_xticklabels() + ax1.get_yticklabels():
            tick.set_fontweight('bold')
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # 📥 İNDİRME MOTORU
        st.markdown("### 📥 Makale İçin İndir")
        dcol1, dcol2 = st.columns([1, 3])
        with dcol1: 
            dpi_secim = st.selectbox("Çözünürlük (DPI)", [300, 600, 1200], index=1)
        with dcol2:
            st.markdown("<br>", unsafe_allow_html=True)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi_secim)
            
            safe_title = rdf_title.replace('(', '').replace(')', '').replace(' ', '_')
            st.download_button("Grafiği İndir (PNG)", data=buf.getvalue(), file_name=f"Overlay_RDF_{safe_title}.png", mime="image/png")
# ==========================================
# MODÜL 36: ÇOKLU SICAKLIK VDOS OVERLAY (MAKALE VİTRİNİ - CANAVAR SÜRÜM)
# ==========================================
elif secim == "📍 Çoklu Sıcaklık VDoS (Overlay)":
    st.header("Sıcaklığa Bağlı VDoS Kıyaslama (Overlay)")
    st.markdown("Farklı sıcaklıklara ait Total VDoS dosyalarını yükleyerek fonon yumuşamasını ve yüksek frekans bandını (Kubas) kusursuz eksen ayarlarıyla tek bir grafikte gösterin.")

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        vdos_title = st.text_input("Y Ekseni Başlığı", "Vibrational DoS (a.u.)") # LaTeX iptal edildi, boşluklar artık bozulmaz
    with col2:
        n_temps = st.number_input("Kaç Farklı Sıcaklık Kıyaslanacak?", min_value=1, max_value=5, value=3, step=1)

    st.markdown("---")
    
    # --- DİNAMİK DOSYA YÜKLEYİCİ ---
    tabs = st.tabs([f"Sıcaklık {i+1}" for i in range(n_temps)])
    datasets_raw = []
    default_labels = ["300 K", "600 K", "900 K", "450 K", "750 K"]
    
    for i in range(n_temps):
        with tabs[i]:
            c1, c2 = st.columns(2)
            with c1:
                label = st.text_input("Veri Etiketi (Lejant)", value=default_labels[i] if i < 5 else f"{i+1}. Veri", key=f"v_lbl_{i}")
            with c2:
                v_file = st.file_uploader(f"VDoS Dosyası (Örn: TVDOS.dat)", type=["dat", "txt"], key=f"v_file_{i}")
                
            datasets_raw.append({"label": label, "file": v_file})

    if st.button("Verileri Oku ve Grafiği Hazırla", type="primary"):
        if "multi_vdos_data" in st.session_state:
            del st.session_state["multi_vdos_data"]
        
        valid_datasets = []
        
        def smart_load_vdos(uploaded_file):
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=r'\s+', comment='#', names=['Freq', 'Int'])
            return df.dropna().query('Freq >= 0').reset_index(drop=True)

        for i, data in enumerate(datasets_raw):
            if data["file"] is not None:
                try:
                    df = smart_load_vdos(data["file"])
                    valid_datasets.append({
                        "id": i, "label": data["label"], "df": df
                    })
                except Exception as e:
                    st.error(f"{data['label']} verisi okunamadı: {e}")
        
        if valid_datasets:
            st.session_state.multi_vdos_ready = True
            st.session_state.multi_vdos_data = valid_datasets
            st.success("✅ Tüm VDoS verileri başarıyla hafızaya alındı!")
        else:
            st.error("Lütfen en az bir VDoS dosyası yükleyin.")

    # --- KONTROL PANELİ VE ÇİZİM ---
    if st.session_state.get("multi_vdos_ready", False):

        datasets = st.session_state.multi_vdos_data

        # 📐 EKSEN AYARLARI (KUSURSUZ VE EKSİKSİZ)
        with st.expander("📐 Eksen Sınırları, Adımlar ve Görünüm", expanded=False):
            st.markdown("**X Ekseni (Frekans) Ayarları**")
            cx1, cx2, cx3 = st.columns(3)
            with cx1: f_min = st.number_input("Min. X", value=0.0, step=10.0)
            with cx2: f_max = st.number_input("Maks. X", value=100.0, step=10.0)
            with cx3: f_step = st.number_input("X Adımı", min_value=1.0, value=20.0, step=5.0)
            
            st.markdown("**Y Ekseni (Şiddet) Ayarları**")
            global_max_int = max([d['df']['Int'].max() for d in datasets])
            cy1, cy2, cy3 = st.columns(3)
            with cy1: int_min = st.number_input("Min. Y", value=0.0, step=0.1)
            with cy2: int_max = st.number_input("Maks. Y", value=float(np.ceil(global_max_int + (global_max_int*0.1))), step=0.5)
            with cy3: int_step = st.number_input("Y Adımı", min_value=0.05, value=0.50, step=0.25)
            
            st.markdown("**Ekstra Görünüm Ayarları**")
            cg1, cg2, cg3 = st.columns(3)
            with cg1: show_minor_ticks = st.checkbox("Minör Çentikleri Göster", value=True)
            with cg2: show_grid = st.checkbox("Arka Plan Izgarası (Grid) Aç", value=False)
            with cg3: leg_loc = st.selectbox("Lejant Konumu", ["best", "upper right", "upper left", "center right"], index=1)

        # 🎨 RENK VE STİL AYARLARI
        with st.expander("🎨 Sıcaklıkları Aç/Kapat ve Stilleri Belirle", expanded=True):
            default_colors = ["#2c3e50", "#2980b9", "#e74c3c", "#27ae60", "#8e44ad"]
            ls_map = {"- (Düz)": "-", "-- (Kesik)": "--", "-. (Nokta-Kesik)": "-.", ": (Noktalı)": ":"}
            plot_settings = []
            
            for i, d in enumerate(datasets):
                st.markdown(f"**{d['label']}**")
                sc1, sc2, sc3, sc4 = st.columns(4)
                
                with sc1:
                    show_line = st.checkbox(f"Çizgiyi Göster", value=True, key=f"sh_{i}")
                with sc2:
                    c_line = st.color_picker("Renk", default_colors[i % len(default_colors)], key=f"cl_{i}")
                with sc3:
                    ls_line = st.selectbox("Stil", list(ls_map.keys()), index=0, key=f"lsl_{i}") 
                with sc4:
                    lw_line = st.slider("Kalınlık", 1.0, 4.0, 2.5, 0.5, key=f"lwl_{i}")
                
                plot_settings.append({
                    "show": show_line, "c": c_line, "ls": ls_map[ls_line], "lw": lw_line
                })
                st.markdown("---")

        # 🎨 ÇİZİM MOTORU (A-SINIFI)
        fig, ax = plt.subplots(figsize=(10, 6))

        for i, d in enumerate(datasets):
            s = plot_settings[i]
            if s['show']:
                ax.plot(d['df']['Freq'], d['df']['Int'], color=s['c'], lw=s['lw'], ls=s['ls'], label=d['label'])

        ax.set_xlabel(r'$\mathbf{Frequency\ (\nu,\ THz)}$', fontsize=20, fontweight='bold', labelpad=12)
        ax.set_ylabel(vdos_title, fontsize=22, fontweight='bold', color='black', labelpad=12)
        
        # Sınırlar
        ax.set_xlim(f_min, f_max)
        ax.set_ylim(int_min, int_max)
        
        # GÜVENLİ ADIM (TICK) MOTORU (Sıfıra Bölünme Korumalı)
        if f_step > 0:
            ax.xaxis.set_major_locator(ticker.MultipleLocator(f_step))
        if int_step > 0:
            ax.yaxis.set_major_locator(ticker.MultipleLocator(int_step))

        if show_minor_ticks:
            ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(2))
            ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(2))

        # İsteğe Bağlı Izgara (Grid)
        if show_grid:
            ax.grid(True, which='major', color='gray', linestyle='--', alpha=0.3)

        ax.tick_params(axis='both', labelsize=16, direction='in', length=8, width=2)
        ax.legend(loc=leg_loc, frameon=False, prop={'weight':'bold', 'size':16})

        # Kalın Çerçeve ve Fontlar
        for axis_name in ['top','bottom','left','right']:
            ax.spines[axis_name].set_linewidth(2.0)
        for tick in ax.get_xticklabels() + ax.get_yticklabels():
            tick.set_fontweight('bold')
        
        plt.tight_layout()
        
        # Önce ekrana bas
        st.pyplot(fig)

        # 📥 İNDİRME MOTORU
        st.markdown("### 📥 Makale İçin İndir")
        dcol1, dcol2 = st.columns([1, 3])
        with dcol1: 
            dpi_secim = st.selectbox("Çözünürlük (DPI)", [300, 600, 1200], index=1)
        with dcol2:
            st.markdown("<br>", unsafe_allow_html=True)
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi_secim)
            st.download_button("Grafiği İndir (PNG)", data=buf.getvalue(), file_name=f"Overlay_VDOS.png", mime="image/png")
            
        # Ghosting'i (Hayalet Veriyi) kesin olarak önler
        plt.close(fig)
    # ==========================================
# MODÜL: MASTER GRAFİK BİRLEŞTİRİCİ (ORIGIN KLONU)
# ==========================================
elif secim == "🎨 Master Grafik Birleştirici (Origin Klonu)":
    st.header("Master Grafik Birleştirici")
    st.markdown("Farklı veri dosyalarını yükleyin, sütunları seçin ve grafiğinizin her bir pikselini OriginLab kalitesinde özelleştirin.")
    st.markdown("---")

    # --- KONTROL PANELİ (SEKMELER) ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📂 1. Veri Yükleme ve Çizgi Ayarları", 
        "📐 2. Eksen ve Ölçek Ayarları", 
        "📝 3. Tipografi ve Lejant", 
        "📥 4. Önizleme ve İndirme"
    ])

    # ---------------------------------------------------------
    # TAB 1: VERİ VE ÇİZGİ AYARLARI
    # ---------------------------------------------------------
    with tab1:
        n_lines = st.number_input("Kaç farklı veri (çizgi) birleştirilecek?", min_value=1, max_value=10, value=2, step=1)
        
        plot_data = [] # Çizilecek verileri tutacağımız liste
        
        for i in range(n_lines):
            st.markdown(f"**Veri Seti {i+1}**")
            
            c_file, c_cols = st.columns([1.5, 1])
            with c_file:
                uploaded_file = st.file_uploader(f"{i+1}. Dosya", type=["dat", "txt", "csv", "out"], key=f"file_{i}")
                skip_r = st.number_input("Atlanacak Satır (Eğer # yoksa)", value=0, min_value=0, key=f"skip_{i}")
            
            if uploaded_file is not None:
                try:
                    uploaded_file.seek(0)
                    # YENİ EKLENEN KISIM: sep=r'\s+' (Boşlukları böler) ve comment='#' (# satırlarını otomatik atlar)
                    df = pd.read_csv(uploaded_file, sep=r'\s+', engine='python', skiprows=skip_r, header=None, comment='#')
                    
                    with c_cols:
                        x_col = st.number_input("X Sütunu (İndeks)", value=0, min_value=0, max_value=len(df.columns)-1, key=f"x_{i}")
                        y_col = st.number_input("Y Sütunu (İndeks)", value=1 if len(df.columns)>1 else 0, min_value=0, max_value=len(df.columns)-1, key=f"y_{i}")
                    
                    # Çizgi İnce Ayarları
                    with st.expander(f"🖌️ {i+1}. Çizgi İçin Stil Ayarları"):
                        s1, s2, s3, s4 = st.columns(4)
                        with s1:
                            lbl = st.text_input("Lejant İsmi", value=f"Data {i+1}", key=f"lbl_{i}")
                        with s2:
                            clr = st.color_picker("Renk", value=['#FF0000', '#0000FF', '#008000', '#FFA500', '#800080'][i%5], key=f"clr_{i}")
                        with s3:
                            ls = st.selectbox("Çizgi Stili", ["-", "--", "-.", ":", "None"], key=f"ls_{i}")
                            lw = st.number_input("Kalınlık", value=2.5, min_value=0.0, step=0.5, key=f"lw_{i}")
                        with s4:
                            marker = st.selectbox("İşaretçi (Marker)", ["None", "o", "s", "^", "D", "x"], key=f"marker_{i}")
                            ms = st.number_input("Marker Boyutu", value=8, min_value=1, step=1, key=f"ms_{i}")

                    # --- EKSEN KORUMASI VE VİRGÜL DÜZELTMESİ ---
                    x_raw = df.iloc[:, x_col].astype(str).str.replace(',', '.')
                    y_raw = df.iloc[:, y_col].astype(str).str.replace(',', '.')
                    
                    x_num = pd.to_numeric(x_raw, errors='coerce')
                    y_num = pd.to_numeric(y_raw, errors='coerce')
                    
                    mask = ~x_num.isna() & ~y_num.isna()
                    x_clean = x_num[mask].values
                    y_clean = y_num[mask].values

                    if len(x_clean) == 0:
                        st.error(f"❌ HATA: {i+1}. dosyada çizilecek veri bulunamadı! X/Y sütun numaralarını kontrol edin.")
                    else:
                        st.success(f"✅ {i+1}. Dosyadan {len(x_clean)} satır veri başarıyla okundu.")
                        
                        plot_data.append({
                            "x": x_clean,
                            "y": y_clean,
                            "label": lbl, "color": clr, "ls": ls, "lw": lw, "marker": marker, "ms": ms
                        })
                        
                except Exception as e:
                    st.error(f"{i+1}. dosya okunamadı: {e}")
    # ---------------------------------------------------------
    # TAB 2: EKSEN VE ÖLÇEK AYARLARI
    # ---------------------------------------------------------
    with tab2:
        c_x, c_y = st.columns(2)
        
        with c_x:
            st.markdown("### X Ekseni (Yatay)")
            x_label = st.text_input("X Ekseni Başlığı", "X Axis (Units)")
            x_min = st.number_input("X Min", value=0.0, step=1.0)
            x_max = st.number_input("X Max", value=100.0, step=1.0)
            x_step = st.number_input("X Ana Adım (Tick)", value=20.0, step=1.0)
            x_scale = st.radio("X Ölçeği", ["linear", "log"], horizontal=True)

        with c_y:
            st.markdown("### Y Ekseni (Dikey)")
            y_label = st.text_input("Y Ekseni Başlığı", "Y Axis (Units)")
            y_min = st.number_input("Y Min", value=0.0, step=1.0)
            y_max = st.number_input("Y Max", value=100.0, step=1.0)
            y_step = st.number_input("Y Ana Adım (Tick)", value=20.0, step=1.0)
            y_scale = st.radio("Y Ölçeği", ["linear", "log"], horizontal=True)

        st.markdown("---")
        show_grid = st.checkbox("Arkaplan Izgarasını (Grid) Göster", value=False)

    # ---------------------------------------------------------
    # TAB 3: TİPOGRAFİ VE LEJANT
    # ---------------------------------------------------------
    with tab3:
        ct1, ct2 = st.columns(2)
        with ct1:
            st.markdown("### Tipografi (Punto)")
            font_title = st.slider("Grafik Başlığı Puntosu", 10, 30, 20)
            font_label = st.slider("Eksen Başlıkları Puntosu", 10, 30, 18)
            font_tick = st.slider("Eksen Rakamları Puntosu", 8, 24, 14)
            graph_title = st.text_input("Ana Grafik Başlığı (İsteğe Bağlı)", "")

        with ct2:
            st.markdown("### Lejant Ayarları")
            show_legend = st.checkbox("Lejantı Göster", value=True)
            leg_loc = st.selectbox("Lejant Konumu", ["best", "upper right", "upper left", "lower right", "lower left", "center right", "center"])
            leg_ncol = st.number_input("Lejant Sütun Sayısı", value=1, min_value=1, max_value=5, step=1)
            leg_frame = st.checkbox("Lejant Çerçevesini Göster", value=True)

    # ---------------------------------------------------------
    # TAB 4: ÇİZİM, ÖNİZLEME VE İNDİRME
    # ---------------------------------------------------------
    with tab4:
        if len(plot_data) == 0:
            st.warning("Henüz çizilecek geçerli bir veri yüklemediniz. Lütfen 1. Sekmeden dosyalarınızı yükleyin.")
        else:
            if st.button("🚀 Grafiği Oluştur", type="primary", use_container_width=True):
                
                # --- ÇİZİM MOTORU ---
                fig, ax = plt.subplots(figsize=(10, 7))

                # Verileri Çiz
                for d in plot_data:
                    m = None if d["marker"] == "None" else d["marker"]
                    l = '-' if d["ls"] == "None" and m is None else d["ls"] # İkisi de none ise görünmez, engellemek için
                    
                    if l != "None":
                        ax.plot(d["x"], d["y"], label=d["label"], color=d["color"], 
                                linestyle=l, linewidth=d["lw"], marker=m, markersize=d["ms"])
                    else:
                        ax.scatter(d["x"], d["y"], label=d["label"], color=d["color"], 
                                   marker=m, s=d["ms"]**2) # Scatter mode

                # Eksen Ölçekleri
                ax.set_xscale(x_scale)
                ax.set_yscale(y_scale)

                # Eksen Sınırları (Lineer ölçekteyse manuel limitleri uygula)
                if x_scale == "linear":
                    ax.set_xlim(x_min, x_max)
                    ax.xaxis.set_major_locator(MultipleLocator(x_step))
                    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
                
                if y_scale == "linear":
                    ax.set_ylim(y_min, y_max)
                    ax.yaxis.set_major_locator(MultipleLocator(y_step))
                    ax.yaxis.set_minor_locator(AutoMinorLocator(2))

                # Etiketler ve Başlık
                ax.set_xlabel(x_label, fontsize=font_label, fontweight='bold', labelpad=10)
                ax.set_ylabel(y_label, fontsize=font_label, fontweight='bold', labelpad=10)
                if graph_title:
                    ax.set_title(graph_title, fontsize=font_title, fontweight='bold', pad=15)

                # Origin Style İnce Ayarlar (Kalın çerçeveler, içe dönük tikler)
                ax.tick_params(axis='both', which='major', direction='in', length=8, width=2.0, labelsize=font_tick, top=True, right=True)
                ax.tick_params(axis='both', which='minor', direction='in', length=4, width=1.5, top=True, right=True)
                
                for label in ax.get_xticklabels() + ax.get_yticklabels():
                    label.set_fontweight('bold')
                for spine in ax.spines.values():
                    spine.set_linewidth(2.0)

                # Grid ve Lejant
                if show_grid:
                    ax.grid(True, linestyle='--', alpha=0.6)
                if show_legend:
                    ax.legend(loc=leg_loc, ncol=leg_ncol, fontsize=font_tick, frameon=leg_frame).get_frame().set_linewidth(1.5)

                plt.tight_layout()

                # Grafiği Ekranda Göster
                st.pyplot(fig)

                # Çıktı Alma Bölümü
                st.markdown("### 📥 Yüksek Çözünürlüklü Dışa Aktar")
                c_dpi1, c_dpi2 = st.columns(2)
                
                with c_dpi1:
                    # PNG İndirme
                    buf_png = io.BytesIO()
                    fig.savefig(buf_png, format="png", dpi=600, bbox_inches='tight')
                    st.download_button(label="PNG Olarak İndir (600 DPI)", data=buf_png.getvalue(), file_name="Master_Plot.png", mime="image/png", use_container_width=True)
                
                with c_dpi2:
                    # SVG İndirme (Vektörel - Adobe Illustrator/Inkscape için)
                    buf_svg = io.BytesIO()
                    fig.savefig(buf_svg, format="svg", bbox_inches='tight')
                    st.download_button(label="SVG Olarak İndir (Vektörel)", data=buf_svg.getvalue(), file_name="Master_Plot.svg", mime="image/svg+xml", use_container_width=True)    
# ==========================================
# MODÜL: formasyon enerji
# ==========================================    

# --- ANA UYGULAMA BLOĞU ---
if secim == "🧪 Formasyon Enerjisi Hesaplama Modülü":
    
    # --- FONKSİYONLAR VE VERİTABANI KURULUMU ---
    DB_FILE = "dft_database.json"

    def parse_formula(formula):
        """Kimyasal formülü parçalar. Örn: KH -> {'K':1, 'H':1}"""
        matches = re.findall(r'([A-Z][a-z]*)(\d*)', formula)
        parsed = {}
        for elem, count in matches:
            parsed[elem] = int(count) if count else 1
        return parsed

    def load_database():
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # DİKKAT: Veritabanı artık Z değerine (Bileşik Formül Sayısına) göre bölünmüştür!
            default_data = {
                "CASTEP": {
                    "Ni": -5417.1471 / 4, "Mg": -1947.8306 / 2, "Bi": -302.1546 / 2, "La": -3449.5115 / 4,
                    "Al": -224.6919 / 4, "Ce": -4245.1783 / 4, "Pr": -2588.4077 / 2, "Ru": -5203.6140 / 2,
                    "Ga": -16423.2421 / 8, "Ba": -1398.5414 / 2, "Cs": -2198.5928 / 4, "Rb": -1318.4020 / 2,
                    "Sr": -1672.5824 / 2, "Te": -668.7100 / 3, 
                    "B2H6": -249.769636 / 1, "KBH4": -1844.560770 / 2, "KH": -3182.07142/ 4, "MgH2": -2012.32738 / 2, 
                    "TiH2": -3272.61447 / 2, "CaH2": -4139.78393 / 4, "ScH2": -5243.26130 / 4, "NaH": -5281.9122 / 4, 
                    "H2": -126.2392 / 4, "Si": -426.9434 / 4, "K": -3116.7716 / 4, "Pt": -2872.3350 / 4, 
                    "Li": -759.3793 / 4, "Ca": -4006.0880 / 4, "Pd": -3194.4586 / 4, "Nd": -6231.2631 / 4, 
                    "Ta": -273.6795 / 2, "Nb": -3102.6874 / 2, "V": -3952.4450 / 2, "N2": -2165.4420 / 4, 
                    "Na": -2608.2724 / 2, "Zn": -3419.6374 / 2, "Ti": -4809.1683 / 3, "Ge": -858.3417 / 8, 
                    "B": -2780.0197 / 36, "Sc": -2554.2800 / 2, "C": -620.3808 / 4, "F2": -5279.1315 / 8, 
                    "Cl2": -3263.5163 / 4, "Sn": -763.8887 / 8
                },
                "VASP": {
                    "Ni": -21.869379 / 4, "Mg": -3.009581 / 2, "Al": -14.960656 / 4, "Ga": -23.208687 / 8,
                    "KH": -19.320636 / 4, "TiH2": -32.158467 / 2, "ScH2": -60.130109 / 4, "BeB2": -69.882194 / 4,
                    "BeH2": -128.309876 / 12, "HfH2": -36.282498 / 2, "ZrH2": -34.018941 / 2, "H2": -6.7719 / 1,
                    "K": -4.1989 / 4, "Li": -7.6284 / 4, "Ca": -7.7165 / 4, "Na": -2.6224 / 2, "Ti": -23.5214 / 3,
                    "B": -241.3409 / 36, "Sc": -12.4989 / 2, "Be": -7.5301 / 2, "Zr": -16.9998 / 2, "Hf": -19.8176 / 2
                }
            }
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=4)
            return default_data

    def save_to_database(db_data):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db_data, f, indent=4)

    # --- ARAYÜZ BAŞLANGICI ---
    st.title("🧪 Formasyon Enerjisi ve Termodinamik Modülü")
    
    if 'main_db' not in st.session_state:
        st.session_state.main_db = load_database()

    # --- ⚙️ VERİTABANI YÖNETİMİ ---
    with st.expander("⚙️ Veritabanı Yönetimi (Kayıt Düzenle / Sil)"):
        st.info("Değerler, bileşikler için 'Formül Başına Enerji', elementler için 'Atom Başına Enerji' cinsindendir.")
        db_cols = st.columns(3)
        with db_cols[0]:
            edit_software = st.selectbox("Yazılım Seç", ["VASP", "CASTEP"], key="edit_soft")
        with db_cols[1]:
            available_elements = sorted(list(st.session_state.main_db[edit_software].keys()))
            element_to_edit = st.selectbox("Element/Bileşik Seç", available_elements, key="edit_elem")
        
        if element_to_edit:
            current_energy = st.session_state.main_db[edit_software][element_to_edit]
            with db_cols[2]:
                new_energy = st.number_input("Formül Başına Enerji (E/Z)", value=float(current_energy), format="%.6f")
            
            btn_col1, btn_col2 = st.columns([1, 5])
            with btn_col1:
                if st.button("Güncelle", type="primary"):
                    st.session_state.main_db[edit_software][element_to_edit] = new_energy
                    save_to_database(st.session_state.main_db)
                    st.success("✅ Güncellendi!")
                    st.rerun()
            with btn_col2:
                if st.button("Kaydı Sil"):
                    del st.session_state.main_db[edit_software][element_to_edit]
                    save_to_database(st.session_state.main_db)
                    st.warning("🗑️ Silindi!")
                    st.rerun()

    st.markdown("---")

    # --- 1. BÖLÜM: YAZILIM SEÇİMİ VE ANA BİLEŞİK GİRİŞİ ---
    software_choice = st.radio("Hesaplama Yapılan Yazılımı Seçiniz:", ["VASP", "CASTEP"], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        formula = st.text_input("Bileşik Formülü (Örn: K2AlH6):", key="main_formula")
    with col2:
        total_energy = st.number_input(f"Bileşiğin Toplam Enerjisi ({software_choice}):", format="%.6f")

    if formula:
        initial_elements = parse_formula(formula)
        st.markdown("### 1️⃣ Element Katsayılarını Doğrula/Gir")
        
        final_coeffs = {}
        cols = st.columns(len(initial_elements))
        
        for i, (elem, coeff) in enumerate(initial_elements.items()):
            with cols[i]:
                final_coeffs[elem] = st.number_input(f"{elem} Katsayısı:", value=coeff, min_value=1, key=f"coeff_{elem}")
        
        total_n = sum(final_coeffs.values())
        
        # Z HESABI (Ana Bileşik İçin)
        unit_cell_atoms = st.number_input("Ana Bileşiğin Birim Hücresindeki Toplam Atom Sayısı:", min_value=1, value=total_n)
        z_value = unit_cell_atoms / total_n
        norm_compound_energy = total_energy / z_value
        st.write(f"**Ana Bileşik Z Değeri:** {z_value:.2f} | **Normalize Enerji ($E/Z$):** {norm_compound_energy:.6f}")

        # --- PATH 1: ELEMENTEL BOZUNMA ---
        st.markdown("### 2️⃣ Path 1 (Elementel Bozunma) Referans Enerjileri")
        path1_ready = True
        total_elemental_subtraction = 0.0
        current_db = st.session_state.main_db[software_choice]
        
        for elem, n_coeff in final_coeffs.items():
            if elem in current_db:
                e_per_atom = current_db[elem]
                contribution = n_coeff * e_per_atom
                total_elemental_subtraction += contribution
            else:
                path1_ready = False
                st.warning(f"⚠️ **{elem}** eksik! Veritabanına ekleyin:")
                with st.expander(f"{elem} Verisini Kaydet"):
                    formula_atoms_p1 = sum(parse_formula(elem).values())
                    c1, c2 = st.columns(2)
                    with c1: e_tot = st.number_input(f"{elem} Toplam Enerji:", format="%.6f", key=f"p1_tot_{elem}")
                    with c2: n_cell = st.number_input(f"{elem} Toplam Atom Sayısı:", min_value=1, key=f"p1_cell_{elem}")
                    
                    st.caption(f"ℹ️ Arka Plan Hesabı: {elem} formülü {formula_atoms_p1} atomlu. Z değeri otomatik olarak `{n_cell} / {formula_atoms_p1}` hesaplanacaktır.")
                    
                    if st.button(f"Kaydet", key=f"p1_btn_{elem}"):
                        z_val_p1 = n_cell / formula_atoms_p1
                        st.session_state.main_db[software_choice][elem] = e_tot / z_val_p1
                        save_to_database(st.session_state.main_db)
                        st.rerun()

        if path1_ready:
            st.markdown("#### 📊 Path 1 Sonuçları")
            formation_energy = (norm_compound_energy - total_elemental_subtraction) / total_n
            delta_e_p1 = total_elemental_subtraction - norm_compound_energy
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(label="E_form (eV/atom)", value=f"{formation_energy:.6f}")
            m2.metric(label="ΔE (eV) [Path 1]", value=f"{delta_e_p1:.6f}")
            
            if 'H' in final_coeffs:
                h2_coeff = final_coeffs['H'] / 2.0
                if h2_coeff > 0:
                    delta_h_p1 = (delta_e_p1 * 96.845) / h2_coeff
                    t_des_p1 = delta_e_p1 / (h2_coeff * 0.00135)
                    m3.metric(label="ΔH (kJ/mol H₂) [Path 1]", value=f"{delta_h_p1:.3f}")
                    m4.metric(label="T_des (K) [Path 1]", value=f"{t_des_p1:.2f}")

        # --- PATH 2: ALTERNATİF BOZUNMA YOLU ---
        st.markdown("---")
        use_path2 = st.checkbox("🔀 Alternatif Bozunma Yolu (Path 2) Hesapla (Örn: 2KH + Al + 4H)")
        
        if use_path2:
            st.info("Deşarj reaksiyonu sonucunda oluşacak ürünleri (bileşik/element) ve katsayılarını girin.")
            num_products = st.number_input("Kaç farklı ürün çıkacak?", min_value=1, max_value=10, value=3)
            
            path2_products = {}
            p_cols = st.columns(int(num_products))
            for i in range(int(num_products)):
                with p_cols[i]:
                    prod_name = st.text_input(f"{i+1}. Ürün Adı", key=f"p2_name_{i}")
                    prod_coeff = st.number_input(f"Katsayısı", min_value=0.0, value=1.0, key=f"p2_coeff_{i}")
                    if prod_name:
                        path2_products[prod_name] = prod_coeff

            if path2_products:
                path2_ready = True
                path2_energy_sum = 0.0
                missing_products = []

                for prod, coeff in path2_products.items():
                    if prod in current_db:
                        path2_energy_sum += coeff * current_db[prod]
                    else:
                        path2_ready = False
                        missing_products.append(prod)

                if not path2_ready:
                    for missing in missing_products:
                        st.warning(f"⚠️ **{missing}** ürünü veritabanında yok! Lütfen ekleyin:")
                        with st.expander(f"{missing} Verisini Kaydet"):
                            # Formülün kaç atom içerdiğini otomatik bul
                            formula_atoms_p2 = sum(parse_formula(missing).values())
                            
                            c1, c2 = st.columns(2)
                            with c1: e_tot_p2 = st.number_input(f"{missing} Toplam Enerjisi:", format="%.6f", key=f"p2_tot_{missing}")
                            with c2: n_cell_p2 = st.number_input(f"{missing} Birim Hücredeki Toplam Atom Sayısı:", min_value=1, key=f"p2_cell_{missing}")
                            
                            # Kullanıcıya arka planda ne olduğunu göster
                            st.caption(f"ℹ️ Arka Plan Hesabı: {missing} formülü {formula_atoms_p2} atomlu. Z değeri otomatik olarak `{n_cell_p2} / {formula_atoms_p2}` hesaplanacaktır.")
                            
                            if st.button(f"Kaydet", key=f"p2_btn_{missing}"):
                                z_val_p2 = n_cell_p2 / formula_atoms_p2
                                st.session_state.main_db[software_choice][missing] = e_tot_p2 / z_val_p2
                                save_to_database(st.session_state.main_db)
                                st.rerun()
                
                if path2_ready:
                    st.markdown("#### 📊 Path 2 Sonuçları")
                    delta_e_p2 = path2_energy_sum - norm_compound_energy
                    
                    st.metric(label="ΔE (eV) [Path 2]", value=f"{delta_e_p2:.6f}")
                    
                    h2_released = st.number_input("Bu reaksiyonda açığa çıkan toplam H₂ mol sayısı (T_des hesabı için):", min_value=0.0, value=0.0)
                    
                    if h2_released > 0:
                        delta_h_p2 = (delta_e_p2 * 96.845) / h2_released
                        t_des_p2 = delta_e_p2 / (h2_released * 0.00135)
                        
                        m1, m2 = st.columns(2)
                        m1.metric(label="ΔH (kJ/mol H₂) [Path 2]", value=f"{delta_h_p2:.3f}")
                        m2.metric(label="T_des (K) [Path 2]", value=f"{t_des_p2:.2f}")
# ==========================================
# MODÜL: AKADEMİK PARAPHRASE (YAPAY ZEKA)
# ==========================================
elif secim == "✍️ Akademik Paraphrase (Yapay Zeka)":
    
    st.header("🎓 Akademik Paraphrase & Redaksiyon")
    st.markdown("*İnsan tonlamalı, verileri koruyan, sıfır yapay zeka izli metin üretim aracı.*")
    st.markdown("---")

    # CSS ile alt bilgi (watermark)
    st.markdown("""
        <style>
        .footer {
            position: fixed;
            right: 20px;
            bottom: 20px;
            background-color: rgba(255, 255, 255, 0.9);
            padding: 8px 15px;
            border-radius: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            font-size: 12px;
            color: #64748b;
            border: 1px solid #e2e8f0;
            z-index: 100;
            font-weight: 600;
        }
        .footer-dot {
            height: 8px;
            width: 8px;
            background-color: #6366f1;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(99, 102, 241, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
        }
        </style>
        <div class="footer"><span class="footer-dot"></span>Hazırlayan Çağatay YAMÇIÇIER</div>
    """, unsafe_allow_html=True)

    # Session State Başlatma (Diğer modüllerle çakışmaması için isim değiştirildi)
    if "para_results" not in st.session_state:
        st.session_state.para_results = None

    # --- YARDIMCI FONKSİYONLAR ---
    def generate_paraphrase(api_key, text, mode):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        mode_instructions = {
            "Standart": "TÜM ALTERNATİFLER İÇİN EK KURAL: Standart, dengeli ve profesyonel bir akademik dil kullan.",
            "Otoriter (Ağır)": "TÜM ALTERNATİFLER İÇİN EK KURAL: Dil kullanımı son derece otoriter, ağır, iddialı ve Q1 sınıfı dergilerdeki baş makaleler seviyesinde olsun.",
            "Yalın (Sade)": "TÜM ALTERNATİFLER İÇİN EK KURAL: Karmaşık terimleri olabildiğince anlaşılır kıl, geniş kitlelerin kolayca okuyabileceği yalın, duru ve akıcı bir dil kullan.",
            "Kısa ve Öz": "TÜM ALTERNATİFLER İÇİN EK KURAL: Gereksiz laf kalabalığından tamamen kaçın. Veriyi koruyarak cümleleri en kısa, en vurucu ve öz (concise) hale getir."
        }
        
        system_prompt = f"""Sen alanında uzman bir profesör ve kusursuz bir proofreader'sın (redaktör). Amacın, intihalden (plagiarism) kaçınmak için verilen metni paraphrase etmektir. 

ÇOK ÖNEMLİ KURAL: Orijinal metindeki HİÇBİR BİLGİ, VERİ, İSTATİSTİK, TEKNİK DETAY VEYA ANA FİKİR KAYBOLMAMALIDIR. Üreteceğin tüm alternatifler, orijinal metnin içerdiği bilimsel ve olgusal bilginin TAMAMINI eksiksiz bir şekilde barındırmak ZORUNDADIR. Sadece kelimeleri, cümle yapılarını ve akışı değiştirmelisin; içeriği veya anlamı ASLA eksiltme.

{mode_instructions.get(mode, mode_instructions["Standart"])}

Görev: Verilen metni aşağıdaki 4 spesifik alternatifte, hem Türkçe (tr) hem de İngilizce (en) olarak üret:
1. Alternatif (alt1): İnsan tonlamasıyla, orijinal metnin BİLGİ VE ANLAM bütünlüğünü %100 eksiksiz koruyan, doğal bir versiyon.
2. Alternatif (alt2): Orijinal verileri ve bilgileri eksiksiz koruyarak; bilimsel dil ve insan tonlamasıyla, A-sınıfı (Q1/Q2) akademik dergilere uygun profesyonel paraphrase.
3. Alternatif (alt3): Orijinal bilgi setini eksiksiz tutarak; yapısal bozuklukları giderilmiş, okuması en akıcı ve anlaşılır hale getirilmiş editoryal versiyon.
4. Alternatif (alt4): Metindeki verileri DEĞİŞTİRMEDEN ve YAPAY ZEKA İZİ TAŞIMADAN, metni anlayıp A sınıfı dergiler için bir baş editör gözüyle "yorumlayan, sentezleyen ve akademik bir perspektif sunan" versiyon."""

        payload = {
            "contents": [{"parts": [{"text": f"İşlenecek metin: \"{text}\""}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "alt1": {"type": "OBJECT", "properties": {"tr": {"type": "STRING"}, "en": {"type": "STRING"}}},
                        "alt2": {"type": "OBJECT", "properties": {"tr": {"type": "STRING"}, "en": {"type": "STRING"}}},
                        "alt3": {"type": "OBJECT", "properties": {"tr": {"type": "STRING"}, "en": {"type": "STRING"}}},
                        "alt4": {"type": "OBJECT", "properties": {"tr": {"type": "STRING"}, "en": {"type": "STRING"}}}
                    },
                    "required": ["alt1", "alt2", "alt3", "alt4"]
                }
            }
        }
        
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
        if response.status_code == 200:
            data = response.json()
            text_response = data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text_response)
        else:
            st.error(f"API Hatası: {response.text}")
            return None

    def tweak_text(api_key, current_text, instruction):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        prompt = f"""Sen uzman bir editörsün. Şu metni al ve verilen talimata göre yeniden yaz. Asla AI izi bırakma. 
ÇOK ÖNEMLİ: Metindeki hiçbir veriyi, bilgiyi veya ana fikri asla kaybetme/eksiltme. Sadece yapısal ve dilsel düzenleme yap.
Metin: "{current_text}"
Talimat: {instruction}. 
Yanıtı doğrudan, tırnak işareti olmadan ve sadece metin olarak ver."""
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            st.error(f"İnce ayar sırasında hata oluştu.")
            return current_text

    # --- UI TASARIMI ---
    # API Key girişi ana ekrana alındı (Menüyü bozmamak için)
    api_key = st.text_input("🔑 Gemini API Anahtarı", type="password", help="Google AI Studio'dan aldığınız ücretsiz API anahtarı")
    if not api_key:
        st.warning("İşleme başlamadan önce lütfen yukarıya API anahtarınızı girin.")

    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        st.subheader("1️⃣ Orijinal Metin")
        input_text = st.text_area("Benzerlikten kaçınmak istediğiniz metni buraya yapıştırın:", height=300)
        
        global_mode = st.selectbox(
            "Genel Ton/Mod Seçimi:",
            ["Standart", "Otoriter (Ağır)", "Yalın (Sade)", "Kısa ve Öz"]
        )
        
        generate_btn = st.button("✨ Profesyonel Paraphrase Üret", type="primary", use_container_width=True)
        
        if generate_btn:
            if not api_key:
                st.error("Lütfen API anahtarınızı girin.")
            elif not input_text.strip():
                st.error("Lütfen işlenecek bir metin girin.")
            else:
                with st.spinner("Profesör metinleri inceliyor ve yeniden yazıyor... (Veriler korunuyor)"):
                    st.session_state.para_results = generate_paraphrase(api_key, input_text, global_mode)

    with col2:
        st.subheader("2️⃣ Sonuçlar")
        
        if st.session_state.para_results:
            alternatives = [
                ("alt1", "1. Alternatif: İnsan Tonlaması (Anlam Odaklı)", "Orijinal metnin anlam bütünlüğünü bozmayan, en doğal versiyon."),
                ("alt2", "2. Alternatif: Bilimsel Makale Formatı", "A sınıfı dergiler için uygun, ileri düzey akademik sözcük dağarcığı."),
                ("alt3", "3. Alternatif: En Akıcı ve Geliştirilmiş", "Yapısal bozuklukları giderilmiş, okuması en keyifli ve akıcı versiyon."),
                ("alt4", "4. Alternatif: Editör Yorumu / Sentez", "A sınıfı dergi editörü gözüyle metnin özünü koruyarak yapılan akademik yorumlama.")
            ]
            
            for alt_key, title, desc in alternatives:
                with st.expander(f"📘 {title}", expanded=True):
                    st.caption(desc)
                    
                    tab_tr, tab_en = st.tabs(["🇹🇷 Türkçe", "🇬🇧 English"])
                    
                    # TÜRKÇE SEKME
                    with tab_tr:
                        st.write(st.session_state.para_results[alt_key]["tr"])
                        
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        if col_btn1.button("✨ Akıcılaştır", key=f"akici_tr_{alt_key}"):
                            with st.spinner("Düzenleniyor..."):
                                st.session_state.para_results[alt_key]["tr"] = tweak_text(api_key, st.session_state.para_results[alt_key]["tr"], "Daha akıcı ve doğal hale getir")
                                st.rerun()
                        if col_btn2.button("🔬 Akademikleştir", key=f"akad_tr_{alt_key}"):
                            with st.spinner("Düzenleniyor..."):
                                st.session_state.para_results[alt_key]["tr"] = tweak_text(api_key, st.session_state.para_results[alt_key]["tr"], "Daha bilimsel ve üst düzey akademik bir dil kullan")
                                st.rerun()
                        
                        tweak_opt = st.selectbox("Mod Değiştir...", ["Seçiniz...", "Otoriter & Ağır Yap", "Yalınlaştır", "Kısa & Öz Yap", "Sunum Dili"], key=f"sel_tr_{alt_key}")
                        if tweak_opt != "Seçiniz...":
                            with st.spinner("Mod değiştiriliyor..."):
                                instructions = {
                                    "Otoriter & Ağır Yap": "Bu metni çok daha ağır, otoriter ve katı bir bilimsel dille yeniden yaz.",
                                    "Yalınlaştır": "Bu metindeki karmaşık yapıları bozup, herkesin anlayabileceği çok yalın ve basit bir dile çevir.",
                                    "Kısa & Öz Yap": "Bu metni gereksiz kelimelerden arındır, en kısa, net ve vurucu haliyle özetle.",
                                    "Sunum Dili": "Bu metni sanki uluslararası bir kongrede sahnede sunum yapıyormuş gibi, ilham verici tonda yeniden yaz."
                                }
                                st.session_state.para_results[alt_key]["tr"] = tweak_text(api_key, st.session_state.para_results[alt_key]["tr"], instructions[tweak_opt])
                                st.rerun()

                    # İNGİLİZCE SEKME
                    with tab_en:
                        st.write(st.session_state.para_results[alt_key]["en"])
                        
                        col_btn1_en, col_btn2_en, col_btn3_en = st.columns(3)
                        if col_btn1_en.button("✨ Fluent", key=f"akici_en_{alt_key}"):
                            with st.spinner("Editing..."):
                                st.session_state.para_results[alt_key]["en"] = tweak_text(api_key, st.session_state.para_results[alt_key]["en"], "Make it more fluent and natural")
                                st.rerun()
                        if col_btn2_en.button("🔬 Academic", key=f"akad_en_{alt_key}"):
                            with st.spinner("Editing..."):
                                st.session_state.para_results[alt_key]["en"] = tweak_text(api_key, st.session_state.para_results[alt_key]["en"], "Use more scientific and high-level academic language")
                                st.rerun()
                                
                        tweak_opt_en = st.selectbox("Change Mode...", ["Select...", "Authoritative & Heavy", "Simplify", "Short & Concise", "Presentation Tone"], key=f"sel_en_{alt_key}")
                        if tweak_opt_en != "Select...":
                            with st.spinner("Changing mode..."):
                                instructions_en = {
                                    "Authoritative & Heavy": "Rewrite this text in a much heavier, authoritative, and strict scientific tone.",
                                    "Simplify": "Break down complex structures and translate this into a very simple and plain language that anyone can understand.",
                                    "Short & Concise": "Remove unnecessary words and summarize this text in its shortest, clearest, and most striking form.",
                                    "Presentation Tone": "Rewrite this text in an inspiring, captivating tone as if giving a presentation on stage at an international conference."
                                }
                                st.session_state.para_results[alt_key]["en"] = tweak_text(api_key, st.session_state.para_results[alt_key]["en"], instructions_en[tweak_opt_en])
                                st.rerun()
        else:
            st.info("👈 Lütfen sol tarafa metninizi yapıştırın ve üret butonuna basın.")
                            # ==========================================
# MODÜL: MURNAGHAN EOS FIT (CASTEP)
# ==========================================
elif secim == "📈 Murnaghan EOS Fit (CASTEP)":
    st.header("Murnaghan Durum Denklemi (EOS) Fit Analizi")
    st.markdown("CASTEP çıktı dosyalarınızı (`.castep`) veya V-E veri dosyalarınızı yükleyin. Sistem hacim ve enerji değerlerini otomatik ayıklar, Murnaghan denklemine fıtler ve Bulk modülünü hesaplar.")
    st.markdown("---")

    # --- 1. MURNAGHAN DENKLEMİ FONKSİYONU ---
    # E(V) = E0 + (B0*V/B0') * [ (V0/V)^B0' / (B0'-1) + 1 ] - (B0*V0)/(B0'-1)
    def murnaghan(V, E0, B0, Bp, V0):
        return E0 + (B0 * V / Bp) * (((V0 / V)**Bp) / (Bp - 1) + 1) - (B0 * V0) / (Bp - 1)

    # --- 2. VERİ YÜKLEME VE PARÇALAMA ---
    c1, c2 = st.columns(2)
    with c1:
        uploaded_eos = st.file_uploader("Veri Dosyası (.castep, .dat, .txt)", type=["castep", "dat", "txt"])
    with c2:
        st.info("💡 **Otomatik Okuyucu:** `.castep` dosyalarından 'Current cell volume' ve 'Final energy' satırlarını otomatik çeker. Veya doğrudan yan yana Hacim-Enerji yazan standart bir `.dat` dosyası da yükleyebilirsiniz.")

    v_data, e_data = [], []

    if uploaded_eos is not None:
        file_ext = uploaded_eos.name.split('.')[-1].lower()
        content = uploaded_eos.getvalue().decode("utf-8").splitlines()

        if file_ext == "castep":
            # CASTEP dosyasından V ve E ayıklama
            temp_v, temp_e = [], []
            for line in content:
                if "Current cell volume" in line or "Unit cell volume" in line:
                    match = re.search(r'volume\s*=\s*([0-9.]+)', line)
                    if match:
                        temp_v.append(float(match.group(1)))
                elif "Final energy, E" in line or "Total energy" in line:
                    match = re.search(r'=\s*([-\d.]+)', line)
                    if match:
                        temp_e.append(float(match.group(1)))
            
            # Veri eşleştirme (Optimizasyon adımlarını temizleyip sadece farklı hacimleri alma mantığı)
            if len(temp_v) > 0 and len(temp_e) > 0:
                # Genellikle single-point serilerinde veya summary'de V ve E eşit sayıdadır
                min_len = min(len(temp_v), len(temp_e))
                v_data = temp_v[-min_len:]
                e_data = temp_e[-min_len:]
                
        else:
            # Standart iki sütunlu txt/dat okuma
            for line in content:
                line = line.strip()
                if not line or line.startswith('#'): continue
                parts = line.replace(',', '.').split()
                if len(parts) >= 2:
                    try:
                        v_data.append(float(parts[0]))
                        e_data.append(float(parts[1]))
                    except ValueError:
                        pass

        # Tekrarlanan (optimizasyon içi) hacimleri temizle, sadece farklı hacim noktalarını al
        df_raw = pd.DataFrame({'V': v_data, 'E': e_data}).round({'V': 4})
        df_clean = df_raw.groupby('V', as_index=False).min() # Aynı hacimde en düşük enerjiyi al
        
        V = df_clean['V'].values
        E = df_clean['E'].values

        if len(V) < 4:
            st.error("❌ HATA: Murnaghan fiti yapabilmek için en az 4 farklı hacim noktasına ihtiyaç vardır.")
        else:
            st.success(f"✅ Başarılı: {len(V)} farklı hacim-enerji veri noktası okundu.")

            # --- 3. FIT İŞLEMİ (SCIPY) ---
            # Başlangıç tahminleri (Initial guesses)
            a, b, c = np.polyfit(V, E, 2) # Parabolik fit ile başlangıç tahmini
            V0_guess = -b / (2*a)
            E0_guess = a*V0_guess**2 + b*V0_guess + c
            B0_guess = 2 * a * V0_guess  # eV/A^3 cinsinden
            Bp_guess = 4.0

            try:
                popt, pcov = curve_fit(murnaghan, V, E, p0=[E0_guess, B0_guess, Bp_guess, V0_guess], maxfev=10000)
                E0_fit, B0_fit, Bp_fit, V0_fit = popt

                # Birim Dönüşümleri (eV/A^3 to GPa)
                # 1 eV/A^3 = 160.21766208 GPa
                B0_GPa = B0_fit * 160.217662

                st.markdown("### 🧮 Fit Sonuçları (Murnaghan Parametreleri)")
                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Denge Hacmi (V₀)", f"{V0_fit:.3f} Å³")
                r2.metric("Min. Enerji (E₀)", f"{E0_fit:.4f} eV")
                r3.metric("Bulk Modülü (B₀)", f"{B0_GPa:.2f} GPa")
                r4.metric("B₀' (Türev)", f"{Bp_fit:.2f}")

                # Fit eğrisi için hassas V dizisi oluştur
                V_fit = np.linspace(min(V)*0.95, max(V)*1.05, 200)
                E_fit = murnaghan(V_fit, *popt)

                st.markdown("---")

                # --- 4. GRAFİK İNCE AYARLARI (TABS) ---
                st.markdown("### 🎨 Origin Stili Grafik Ayarları")
                t1, t2, t3 = st.tabs(["📏 Eksen ve Ölçek", "🖌️ Çizgi ve Semboller", "📝 Tipografi ve Çıktı"])
                
                with t1:
                    c_ex1, c_ex2 = st.columns(2)
                    with c_ex1:
                        st.markdown("**X Ekseni (Hacim)**")
                        x_min = st.number_input("X Min", value=float(min(V)*0.98), step=1.0)
                        x_max = st.number_input("X Max", value=float(max(V)*1.02), step=1.0)
                        x_step = st.number_input("X Adım", value=2.0, step=0.5)
                        x_label = st.text_input("X Başlığı", r"$\mathbf{Volume\ (V,\ \AA^3)}$")
                    with c_ex2:
                        st.markdown("**Y Ekseni (Enerji)**")
                        y_min = st.number_input("Y Min", value=float(min(E) - 0.05), step=0.01)
                        y_max = st.number_input("Y Max", value=float(max(E) + 0.05), step=0.01)
                        y_step = st.number_input("Y Adım", value=0.05, step=0.01)
                        y_label = st.text_input("Y Başlığı", r"$\mathbf{Total\ Energy\ (E,\ eV)}$")

                with t2:
                    cs1, cs2 = st.columns(2)
                    with cs1:
                        st.markdown("**Hesaplanan Veriler (Noktalar)**")
                        m_color = st.color_picker("Nokta Rengi", "#000000")
                        m_style = st.selectbox("Sembol Tipi", ["o", "s", "^", "D"])
                        m_size = st.slider("Sembol Boyutu", 20, 150, 80)
                    with cs2:
                        st.markdown("**Murnaghan Fit (Eğri)**")
                        l_color = st.color_picker("Eğri Rengi", "#E74C3C")
                        l_style = st.selectbox("Çizgi Stili", ["-", "--", "-.", ":"])
                        l_width = st.slider("Çizgi Kalınlığı", 1.0, 5.0, 2.5)

                with t3:
                    ct1, ct2 = st.columns(2)
                    with ct1:
                        f_title = st.slider("Başlık Puntosu", 12, 24, 18)
                        f_label = st.slider("Eksen Puntosu", 12, 24, 16)
                        f_tick = st.slider("Rakam Puntosu", 10, 20, 14)
                    with ct2:
                        show_grid = st.checkbox("Izgara (Grid) Göster", value=False)
                        leg_pos = st.selectbox("Lejant Konumu", ["best", "upper center", "lower right", "upper right"])
                        dpi_val = st.selectbox("İndirme Çözünürlüğü (DPI)", [300, 600, 1200], index=1)

                # --- 5. ÇİZİM MOTORU ---
                if st.button("🚀 Grafiği Oluştur ve Göster", type="primary", use_container_width=True):
                    fig, ax = plt.subplots(figsize=(9, 7))

                    # Gerçek Veriler (Scatter)
                    ax.scatter(V, E, marker=m_style, s=m_size, facecolors='none', edgecolors=m_color, linewidths=2.0, label="DFT Data", zorder=3)
                    
                    # Fit Eğrisi (Line)
                    ax.plot(V_fit, E_fit, color=l_color, linestyle=l_style, linewidth=l_width, label="Murnaghan EOS Fit", zorder=2)

                    # Minimum Nokta İşaretçisi (Opsiyonel Estetik)
                    ax.scatter([V0_fit], [E0_fit], marker='x', color='blue', s=100, linewidths=2.0, label="Equilibrium ($V_0, E_0$)", zorder=4)

                    # Eksen Ayarları
                    ax.set_xlim(x_min, x_max)
                    ax.set_ylim(y_min, y_max)
                    ax.xaxis.set_major_locator(MultipleLocator(x_step))
                    ax.yaxis.set_major_locator(MultipleLocator(y_step))
                    
                    ax.set_xlabel(x_label, fontsize=f_label, fontweight='bold', labelpad=10)
                    ax.set_ylabel(y_label, fontsize=f_label, fontweight='bold', labelpad=10)

                    # Origin Style Çentikler ve Çerçeve
                    ax.tick_params(axis='both', which='major', direction='in', length=8, width=2.0, labelsize=f_tick, right=True, top=True)
                    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
                    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
                    ax.tick_params(axis='both', which='minor', direction='in', length=4, width=1.5, right=True, top=True)

                    for spine in ax.spines.values():
                        spine.set_linewidth(2.0)
                    for label in ax.get_xticklabels() + ax.get_yticklabels():
                        label.set_fontweight('bold')

                    if show_grid:
                        ax.grid(True, linestyle='--', alpha=0.5)

                    # Ekrana Parametreleri Yazan Metin Kutusu (Inset Text)
                    text_str = '\n'.join((
                        r'$V_0=%.2f\ \AA^3$' % (V0_fit, ),
                        r'$E_0=%.4f\ eV$' % (E0_fit, ),
                        r'$B_0=%.1f\ GPa$' % (B0_GPa, ),
                        r'$B_0^\prime=%.2f$' % (Bp_fit, )))
                    
                    props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='gray')
                    ax.text(0.50, 0.95, text_str, transform=ax.transAxes, fontsize=f_tick,
                            verticalalignment='top', horizontalalignment='left', bbox=props, fontweight='bold')

                    ax.legend(loc=leg_pos, frameon=False, fontsize=f_tick, prop={'weight':'bold'})
                    
                    plt.tight_layout()
                    st.pyplot(fig)

                    # --- İNDİRME MOTORU ---
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches='tight', dpi=dpi_val)
                    st.download_button(
                        label=f"📥 Murnaghan Grafiğini İndir (PNG, {dpi_val} DPI)",
                        data=buf.getvalue(),
                        file_name="Murnaghan_EOS_Fit.png",
                        mime="image/png"
                    )

            except Exception as e:
                st.error(f"Fit işlemi sırasında bir matematiksel hata oluştu: {e}")
                st.warning("İpucu: Hacim aralığınız çok dar veya verileriniz parabolik bir kavis (minimum nokta) oluşturmuyor olabilir.")

st.set_page_config(page_title="Kristal Yapı ve Malzeme Keşif Aracı", layout="wide")

# ==========================================
# 1. ORTAK VERİ TABANI (GLOBAL ALAN)
# Tüm modüllerin erişebilmesi için en dışta tanımlanmıştır.
# ==========================================
def get_elements_data():
    """
    Shannon İyonik Yarıçapları (Å).
    r_CN12 : Perovskit A bölgesi için (CN=12)
    r_CN6  : Perovskit B/B' ve Spinel B bölgesi için (Oktahedral, CN=6)
    r_CN4  : Spinel A bölgesi için (Tetrahedral, CN=4)
    """
    return {
        'Boşluk': {'mass': 0.00, 'r_CN12': {0: 1.37}, 'r_CN6': {0: 1.37}, 'r_CN4': {0: 1.37}},
        
        # --- ALKALİ VE TOPRAK ALKALİ METALLER ---
        'Li': {'mass': 6.94,  'r_CN12': {}, 'r_CN6': {1: 0.76}, 'r_CN4': {1: 0.59}},
        'Na': {'mass': 22.99, 'r_CN12': {1: 1.39}, 'r_CN6': {1: 1.02}, 'r_CN4': {1: 0.99}},
        'K':  {'mass': 39.10, 'r_CN12': {1: 1.64}, 'r_CN6': {1: 1.38}, 'r_CN4': {1: 1.37}},
        'Be': {'mass': 9.01,  'r_CN12': {}, 'r_CN6': {2: 0.45}, 'r_CN4': {2: 0.27}},
        'Mg': {'mass': 24.31, 'r_CN12': {}, 'r_CN6': {2: 0.72}, 'r_CN4': {2: 0.57}},
        'Ca': {'mass': 40.08, 'r_CN12': {2: 1.34}, 'r_CN6': {2: 1.00}, 'r_CN4': {}},
        'Sr': {'mass': 87.62, 'r_CN12': {2: 1.44}, 'r_CN6': {2: 1.18}, 'r_CN4': {}},
        'Ba': {'mass': 137.33,'r_CN12': {2: 1.61}, 'r_CN6': {2: 1.35}, 'r_CN4': {}},
        'Rb': {'mass': 85.47, 'r_CN12': {1: 1.72}, 'r_CN6': {1: 1.52}, 'r_CN4': {}},
        'Cs': {'mass': 132.91,'r_CN12': {1: 1.88}, 'r_CN6': {1: 1.67}, 'r_CN4': {}}, 
        
        # --- GEÇİŞ METALLERİ (3d, 4d, 5d) ---
        'Sc': {'mass': 44.96, 'r_CN12': {}, 'r_CN6': {3: 0.745}, 'r_CN4': {}},
        'Ti': {'mass': 47.87, 'r_CN12': {}, 'r_CN6': {2: 0.86, 3: 0.67, 4: 0.605}, 'r_CN4': {4: 0.42}},
        'V':  {'mass': 50.94, 'r_CN12': {}, 'r_CN6': {2: 0.79, 3: 0.64, 4: 0.58, 5: 0.54}, 'r_CN4': {5: 0.355}},
        'Cr': {'mass': 52.00, 'r_CN12': {}, 'r_CN6': {2: 0.73, 3: 0.615, 6: 0.44}, 'r_CN4': {4: 0.41, 6: 0.26}},
        'Mn': {'mass': 54.94, 'r_CN12': {}, 'r_CN6': {2: 0.83, 3: 0.645, 4: 0.53}, 'r_CN4': {2: 0.66, 3: 0.39}},
        'Fe': {'mass': 55.85, 'r_CN12': {}, 'r_CN6': {2: 0.78, 3: 0.645}, 'r_CN4': {2: 0.63, 3: 0.49}},
        'Co': {'mass': 58.93, 'r_CN12': {}, 'r_CN6': {2: 0.745, 3: 0.61}, 'r_CN4': {2: 0.58, 3: 0.33}},
        'Ni': {'mass': 58.69, 'r_CN12': {}, 'r_CN6': {2: 0.69, 3: 0.60}, 'r_CN4': {2: 0.55}},
        'Cu': {'mass': 63.55, 'r_CN12': {}, 'r_CN6': {1: 0.77, 2: 0.73}, 'r_CN4': {1: 0.60, 2: 0.57}},
        'Zn': {'mass': 65.38, 'r_CN12': {}, 'r_CN6': {2: 0.74}, 'r_CN4': {2: 0.60}},
        'Y':  {'mass': 88.91, 'r_CN12': {}, 'r_CN6': {3: 0.90}, 'r_CN4': {}},
        'Zr': {'mass': 91.22, 'r_CN12': {}, 'r_CN6': {4: 0.72}, 'r_CN4': {}},
        'Nb': {'mass': 92.91, 'r_CN12': {}, 'r_CN6': {3: 0.72, 5: 0.64}, 'r_CN4': {}},
        'Mo': {'mass': 95.95, 'r_CN12': {}, 'r_CN6': {3: 0.69, 4: 0.65, 6: 0.59}, 'r_CN4': {6: 0.41}},
        'Ru': {'mass': 101.07, 'r_CN12': {}, 'r_CN6': {3: 0.68, 4: 0.62}, 'r_CN4': {}},
        'Rh': {'mass': 102.91, 'r_CN12': {}, 'r_CN6': {3: 0.665}, 'r_CN4': {}},
        'Pd': {'mass': 106.42, 'r_CN12': {}, 'r_CN6': {2: 0.86, 4: 0.615}, 'r_CN4': {}},
        'Ag': {'mass': 107.87, 'r_CN12': {}, 'r_CN6': {1: 1.15}, 'r_CN4': {1: 1.00}},
        'Cd': {'mass': 112.41, 'r_CN12': {2: 1.31}, 'r_CN6': {2: 0.95}, 'r_CN4': {2: 0.78}},
        
        # --- LANTANİTLER ---
        'La': {'mass': 138.91, 'r_CN12': {3: 1.36}, 'r_CN6': {3: 1.032}, 'r_CN4': {}},
        'Ce': {'mass': 140.12, 'r_CN12': {3: 1.34, 4: 1.14}, 'r_CN6': {3: 1.01, 4: 0.87}, 'r_CN4': {}},
        
        # --- POST-GEÇİŞ METALLERİ ---
        'Al': {'mass': 26.98,  'r_CN12': {}, 'r_CN6': {3: 0.535}, 'r_CN4': {3: 0.39}},
        'Ga': {'mass': 69.72,  'r_CN12': {}, 'r_CN6': {3: 0.62}, 'r_CN4': {3: 0.47}},
        'In': {'mass': 114.82, 'r_CN12': {}, 'r_CN6': {3: 0.80}, 'r_CN4': {3: 0.62}},
        'Sn': {'mass': 118.71, 'r_CN12': {}, 'r_CN6': {2: 1.12, 4: 0.69}, 'r_CN4': {4: 0.55}},
        'Pb': {'mass': 207.20, 'r_CN12': {2: 1.49}, 'r_CN6': {2: 1.19, 4: 0.775}, 'r_CN4': {}}
    }


# ==========================================
# 2. YAN MENÜ (SİDEBAR) VE ANA KONTROL
# ==========================================
st.sidebar.title("Menü")
secim = st.sidebar.radio("Modül Seçin:", ["Ana Sayfa", "🔍 Kristal Yapı Bulucu", "🥞 2D RP Hidrit Bulucu"])

# Tüm elementlerin listesi
tam_element_listesi = list(get_elements_data().keys())

if secim == "Ana Sayfa":
    st.title("🔬 Malzeme Bilimi Keşif Aracına Hoş Geldiniz")
    st.markdown("""
    Bu uygulama, yeni nesil batarya, hidrojen depolama, fotovoltaik ve spintronik uygulamaları için potansiyel kristal yapıları keşfetmenizi sağlar.
    Lütfen sol menüden kullanmak istediğiniz modülü seçin.
    """)

# ==========================================
# 3. MODÜL: KRİSTAL YAPI BULUCU (PEROVSKİT & SPİNEL)
# ==========================================
elif secim == "🔍 Kristal Yapı Bulucu":
    
    # --- PEROVSKİT FONKSİYONLARI ---
    def generate_perovskite(a_els, b_els, bp_els, enforce_charge):
        edata = get_elements_data()
        results = []
        r_H = 1.37
        
        for a, b, bp in itertools.product(a_els, b_els, bp_els):
            vA_list = list(edata[a]['r_CN12'].keys()) 
            vB_list = list(edata[b]['r_CN6'].keys())
            vBP_list = list(edata[bp]['r_CN6'].keys())
            
            if not vA_list: continue 
                
            for vA, vB, vBP in itertools.product(vA_list, vB_list, vBP_list):
                total_charge = (2 * vA) + vB + vBP
                is_balanced = (total_charge == 6)
                if enforce_charge and not is_balanced: continue 
                    
                rA, rB, rBP = edata[a]['r_CN12'][vA], edata[b]['r_CN6'][vB], edata[bp]['r_CN6'][vBP]
                r_B_eff = (rB + rBP) / 2.0
                t_factor = (rA + r_H) / (math.sqrt(2) * (r_B_eff + r_H))
                
                mass_total = (2 * edata[a]['mass']) + edata[b]['mass'] + edata[bp]['mass'] + (6 * 1.008)
                wt_cap = ((6 * 1.008) / mass_total) * 100
                
                t_status = "İdeal Kübik" if 0.90 <= t_factor <= 1.05 else "Bozulmuş" if 0.80 <= t_factor < 0.90 else "Kararsız"
                
                results.append({
                    "Formül": f"{a}2 {b} {bp} H6",
                    "A/B/B'": f"{a} / {b} / {bp}",
                    "Yükler": f"+{vA} / +{vB} / +{vBP}",
                    "Tolerans (t)": round(t_factor, 3),
                    "Yapı": t_status,
                    "H Kapasitesi (%)": round(wt_cap, 2)
                })
        return pd.DataFrame(results).drop_duplicates()

    def generate_cif_perovskite(a, b, bp):
        return f"""data_{a}2{b}{bp}H6\n_symmetry_space_group_name_H-M   'F m -3 m'\n_cell_length_a 7.5000\n_cell_length_b 7.5000\n_cell_length_c 7.5000\n_cell_angle_alpha 90.0\n_cell_angle_beta 90.0\n_cell_angle_gamma 90.0\nloop_\n_atom_site_label\n_atom_site_type_symbol\n_atom_site_fract_x\n_atom_site_fract_y\n_atom_site_fract_z\n_atom_site_occupancy\n{b}1 {b} 0.0 0.0 0.0 1.0\n{bp}1 {bp} 0.5 0.5 0.5 1.0\n{a}1 {a} 0.25 0.25 0.25 1.0\nH1 H 0.24 0.0 0.0 1.0"""

    # --- SPİNEL FONKSİYONLARI ---
    def generate_spinel(a_els, b_els, x_type, enforce_charge):
        edata = get_elements_data()
        results = []
        
        x_mass = 15.999 if x_type == "O (Oksit)" else 32.06
        x_charge = 2 
        x_sym = "O" if x_type == "O (Oksit)" else "S"
        
        for a, b in itertools.product(a_els, b_els):
            vA_list = list(edata[a]['r_CN4'].keys()) 
            vB_list = list(edata[b]['r_CN6'].keys()) 
            
            if not vA_list or not vB_list: continue 
                
            for vA, vB in itertools.product(vA_list, vB_list):
                total_charge = vA + (2 * vB)
                required_charge = 4 * x_charge 
                is_balanced = (total_charge == required_charge)
                
                if enforce_charge and not is_balanced: continue 
                    
                mass_total = edata[a]['mass'] + (2 * edata[b]['mass']) + (4 * x_mass)
                
                results.append({
                    "Formül": f"{a} {b}2 {x_sym}4",
                    "A (Tetra)": f"{a} (+{vA})",
                    "B (Okta)": f"{b} (+{vB})",
                    "Toplam Yük": f"+{total_charge}",
                    "Mol Kütlesi (g/mol)": round(mass_total, 2),
                    "Yük Dengesi": "Sağlanıyor" if is_balanced else "Hatalı!"
                })
        return pd.DataFrame(results).drop_duplicates()

    def generate_cif_spinel(a, b, x_sym):
        return f"""data_{a}{b}2{x_sym}4\n_symmetry_space_group_name_H-M   'F d -3 m'\n_cell_length_a 8.2000\n_cell_length_b 8.2000\n_cell_length_c 8.2000\n_cell_angle_alpha 90.0\n_cell_angle_beta 90.0\n_cell_angle_gamma 90.0\nloop_\n_atom_site_label\n_atom_site_type_symbol\n_atom_site_fract_x\n_atom_site_fract_y\n_atom_site_fract_z\n_atom_site_occupancy\n{a}1 {a} 0.125 0.125 0.125 1.0\n{b}1 {b} 0.5 0.5 0.5 1.0\n{x_sym}1 {x_sym} 0.255 0.255 0.255 1.0"""

    # --- ARAYÜZ (SEKMELER) ---
    st.header("🔬 Kristal Yapı Kombinasyon Üretici")
    tab_perov, tab_spinel = st.tabs(["🔍 Çift Perovskit (A₂BB'H₆)", "💎 Spinel (AB₂X₄)"])
    
    # SEKME 1: PEROVSKİT
    with tab_perov:
        st.markdown("**Hidrojen depolama** için İdeal Kübik Çift Perovskit adayları üretin.")
        cp1, cp2, cp3 = st.columns(3)
        with cp1: sel_A = st.multiselect("A Bölgesi (CN=12)", tam_element_listesi, default=['Li', 'Na', 'Mg'], key="pA")
        with cp2: sel_B = st.multiselect("B Bölgesi (CN=6)", tam_element_listesi, default=['Fe', 'Ti', 'Ni'], key="pB")
        with cp3: sel_BP = st.multiselect("B' Bölgesi (CN=6)", tam_element_listesi, default=['Fe', 'V', 'Co'], key="pBP")
            
        enf_p = st.checkbox("Sadece Yük Dengesi Sağlananları (+6) Göster", value=True, key="chk_p")
        
        if st.button("🚀 Perovskit Üret", type="primary"):
            with st.spinner('Hesaplanıyor...'):
                df_p = generate_perovskite(sel_A, sel_B, sel_BP, enf_p)
                if df_p.empty:
                    st.warning("Bu elementlerle kararlı bir perovskit bulunamadı.")
                else:
                    st.success(f"{len(df_p)} adet perovskit bulundu!")
                    df_p['t_farki'] = abs(df_p['Tolerans (t)'] - 1.0)
                    df_p = df_p.sort_values(by="t_farki").drop(columns=['t_farki']).reset_index(drop=True)
                    st.session_state['df_p'] = df_p

        if 'df_p' in st.session_state:
            def highlight_t(val):
                if val == "İdeal Kübik": return 'background-color: #2ecc71; color: white;'
                elif "Bozulmuş" in val: return 'background-color: #f1c40f; color: black;'
                else: return 'background-color: #e74c3c; color: white;'
            st.dataframe(st.session_state['df_p'].style.applymap(highlight_t, subset=['Yapı']), use_container_width=True)
            
            cp_dl1, cp_dl2 = st.columns(2)
            with cp_dl1:
                st.download_button("📊 Tabloyu CSV İndir", st.session_state['df_p'].to_csv(index=False).encode('utf-8'), 'perovskite.csv', 'text/csv')
            with cp_dl2:
                sec_p = st.selectbox("CIF için malzeme seçin:", st.session_state['df_p']['Formül'].unique(), key="cif_p")
                if sec_p:
                    satir = st.session_state['df_p'][st.session_state['df_p']['Formül'] == sec_p].iloc[0]
                    a_el, b_el, bp_el = satir["A/B/B'"].split(" / ")
                    st.download_button("💾 CIF İndir", generate_cif_perovskite(a_el, b_el, bp_el), f"{a_el}2{b_el}{bp_el}H6.cif", 'text/plain')

    # SEKME 2: SPİNEL
    with tab_spinel:
        st.markdown("**Katalizör ve Batarya** araştırmaları için Spinel yapı adayları üretin.")
        cs1, cs2, cs3 = st.columns(3)
        with cs1: sel_sA = st.multiselect("A Bölgesi (Tetra, CN=4)", tam_element_listesi, default=['Mg', 'Zn', 'Mn', 'Co'], key="sA")
        with cs2: sel_sB = st.multiselect("B Bölgesi (Okta, CN=6)", tam_element_listesi, default=['Al', 'Fe', 'Cr'], key="sB")
        with cs3: sel_sX = st.selectbox("X Bölgesi (Anyon)", ["O (Oksit)", "S (Sülfür)"])
            
        enf_s = st.checkbox("Sadece Yük Dengesi Sağlananları (+8) Göster", value=True, key="chk_s")
        
        if st.button("🚀 Spinel Üret", type="primary"):
            with st.spinner('Hesaplanıyor...'):
                df_s = generate_spinel(sel_sA, sel_sB, sel_sX, enf_s)
                if df_s.empty:
                    st.warning("Bu elementlerle kararlı bir spinel bulunamadı.")
                else:
                    st.success(f"{len(df_s)} adet spinel bulundu!")
                    st.session_state['df_s'] = df_s

        if 'df_s' in st.session_state:
            st.dataframe(st.session_state['df_s'], use_container_width=True)
            
            cs_dl1, cs_dl2 = st.columns(2)
            with cs_dl1:
                st.download_button("📊 Tabloyu CSV İndir", st.session_state['df_s'].to_csv(index=False).encode('utf-8'), 'spinel.csv', 'text/csv', key="dl_scsv")
            with cs_dl2:
                sec_s = st.selectbox("CIF için malzeme seçin:", st.session_state['df_s']['Formül'].unique(), key="cif_s")
                if sec_s:
                    satir = st.session_state['df_s'][st.session_state['df_s']['Formül'] == sec_s].iloc[0]
                    a_el = satir["A (Tetra)"].split(" ")[0]
                    b_el = satir["B (Okta)"].split(" ")[0]
                    x_sym = "O" if "Oksit" in sel_sX else "S"
                    st.download_button("💾 CIF İndir", generate_cif_spinel(a_el, b_el, x_sym), f"{a_el}{b_el}2{x_sym}4.cif", 'text/plain', key="dl_scif")

# ==========================================
# 4. MODÜL: 2D RUDDLESDEN-POPPER (RP) HİDRİT BULUCU
# ==========================================
elif secim == "🥞 2D RP Hidrit Bulucu":

    def generate_rp_hydride(a_prime_els, a_els, b_els, bp_els, n_val, enforce_charge):
        edata = get_elements_data()
        results = []
        r_H = 1.37  
        
        # Eğer n=1 ise A katyonu kullanılmaz
        if n_val == 1:
            a_els = ["Boşluk"]
            
        for ap, a, b, bp in itertools.product(a_prime_els, a_els, b_els, bp_els):
            vAP_list = list(edata[ap]['r_CN12'].keys()) if ap != "Boşluk" else [0]
            vA_list = list(edata[a]['r_CN12'].keys()) if a != "Boşluk" else [0]
            vB_list = list(edata[b]['r_CN6'].keys())
            vBP_list = list(edata[bp]['r_CN6'].keys())
            
            if not vAP_list or not vB_list or not vBP_list: continue
                
            for vAP, vA, vB, vBP in itertools.product(vAP_list, vA_list, vB_list, vBP_list):
                total_metal_charge = (2 * vAP) + ((n_val - 1) * vA) + (n_val / 2 * vB) + (n_val / 2 * vBP)
                target_charge = 3 * n_val + 1
                
                is_balanced = (total_metal_charge == target_charge)
                if enforce_charge and not is_balanced: continue 
                    
                if n_val == 1:
                    formula = f"{ap}4 {b} {bp} H8"
                    mass_total = (4 * edata[ap]['mass']) + edata[b]['mass'] + edata[bp]['mass'] + (8 * 1.008)
                elif n_val % 2 != 0:
                    formula = f"{ap}4 {a if a!='Boşluk' else ''}{2*(n_val-1)} {b}{n_val} {bp}{n_val} H{2*(3*n_val+1)}"
                    mass_total = (4 * edata[ap]['mass']) + (2*(n_val-1)*edata[a]['mass']) + (n_val*edata[b]['mass']) + (n_val*edata[bp]['mass']) + (2*(3*n_val+1)*1.008)
                else:
                    formula = f"{ap}2 {a if a!='Boşluk' else ''}{n_val-1} {b}{int(n_val/2)} {bp}{int(n_val/2)} H{3*n_val+1}"
                    mass_total = (2 * edata[ap]['mass']) + ((n_val-1)*edata[a]['mass']) + (int(n_val/2)*edata[b]['mass']) + (int(n_val/2)*edata[bp]['mass']) + ((3*n_val+1)*1.008)
                
                rB, rBP = edata[b]['r_CN6'][vB], edata[bp]['r_CN6'][vBP]
                r_B_eff = (rB + rBP) / 2.0
                
                r_A_eff = edata[a]['r_CN12'].get(vA, 0) if n_val > 1 else edata[ap]['r_CN12'][vAP]
                t_factor = (r_A_eff + r_H) / (math.sqrt(2) * (r_B_eff + r_H))
                
                wt_cap = ((float(formula.split('H')[-1])) * 1.008 / mass_total) * 100
                
                results.append({
                    "Formül": formula.replace(" 0", "").replace(" 1 ", " ").strip(),
                    "Katman (n)": n_val,
                    "A' / A / B / B'": f"{ap} (+{vAP}) / {'Yok' if n_val==1 else a+' (+'+str(vA)+')'} / {b} (+{vB}) / {bp} (+{vBP})",
                    "Blok Toleransı (t)": round(t_factor, 3),
                    "Mol Kütlesi": round(mass_total, 2),
                    "H Kapasitesi (%)": round(wt_cap, 2)
                })
        return pd.DataFrame(results).drop_duplicates()

    def generate_cif_rp_hydride(ap, a, b, bp, n_val):
        c_length = 12.0 + (n_val * 4.0) 
        
        cif_content = f"""data_{ap}_{a}_{b}_{bp}_H_RP_n{n_val}
_symmetry_space_group_name_H-M   'I 4/m m m'
_cell_length_a 4.0000
_cell_length_b 4.0000
_cell_length_c {c_length:.4f}
_cell_angle_alpha 90.0
_cell_angle_beta 90.0
_cell_angle_gamma 90.0
loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
_atom_site_occupancy
{b}1 {b} 0.0 0.0 0.0 0.5
{bp}1 {bp} 0.0 0.0 0.0 0.5
{ap}1 {ap} 0.0 0.0 0.35 1.0\n"""
        
        if n_val > 1:
            cif_content += f"{a}1 {a} 0.0 0.0 0.15 1.0\n"
            
        cif_content += "H1 H 0.0 0.5 0.0 1.0\nH2 H 0.0 0.0 0.18 1.0"
        return cif_content

    # --- ARAYÜZ TASARIMI ---
    st.header("🥞 2D Ruddlesden-Popper (RP) Hidrit Çift Perovskit Aday Üretici")
    st.markdown("""
    Bu modül **$A'_{2}A_{n-1}B_{n}X_{3n+1}$** genel formülünü temel alarak $H^-$ anyonlu, yüksek boyutlu katmanlı kuantum materyaller (örneğin spintronik için $K_4NiVH_8$) üretir.
    """)
    
    sadece_elementler = [el for el in tam_element_listesi if el != 'Boşluk']
    
    col_n, col_enf = st.columns(2)
    with col_n: n_secim = st.slider("Katman Sayısı (n) [n=1 ise A katyonu otomatik iptal olur]", min_value=1, max_value=3, value=1)
    with col_enf: enf_rp = st.checkbox("Sadece Yük Dengesi Sağlananları Göster", value=True, key="chk_rp")

    crp1, crp2, crp3, crp4 = st.columns(4)
    with crp1: sel_A_prime = st.multiselect("A' Bölgesi (Bariyer)", sadece_elementler, default=['K', 'Rb', 'Cs'], key="rpAP")
    with crp2: sel_A_cage = st.multiselect("A Bölgesi (Kafes)", sadece_elementler, default=['Cs', 'Ba', 'Sr'], key="rpA", disabled=(n_secim==1))
    with crp3: sel_B1 = st.multiselect("B' Bölgesi (Geçiş Metali)", sadece_elementler, default=['Ni', 'Fe', 'Co'], key="rpB")
    with crp4: sel_B2 = st.multiselect("B'' Bölgesi (Geçiş Metali)", sadece_elementler, default=['V', 'Ti', 'Cr'], key="rpBP")

    if st.button("🚀 2D RP Hidrit Üret", type="primary"):
        with st.spinner(f'n={n_secim} Katmanlı RP yapılar hesaplanıyor...'):
            df_rp = generate_rp_hydride(sel_A_prime, sel_A_cage, sel_B1, sel_B2, n_secim, enf_rp)
            if df_rp.empty:
                st.warning("Bu kombinasyonla yük dengesi sağlanan kararlı bir katmanlı yapı bulunamadı.")
            else:
                st.success(f"{len(df_rp)} adet 2D RP hidrit bulundu!")
                st.session_state['df_rp'] = df_rp

    if 'df_rp' in st.session_state:
        st.dataframe(st.session_state['df_rp'], use_container_width=True)
        
        rp_dl1, rp_dl2 = st.columns(2)
        with rp_dl1:
            st.download_button("📊 Tabloyu CSV İndir", st.session_state['df_rp'].to_csv(index=False).encode('utf-8'), '2D_RP_hydrides.csv', 'text/csv', key="dl_rpcsv")
        with rp_dl2:
            sec_rp = st.selectbox("CIF için malzeme seçin (I4/mmm İdeal Yapı):", st.session_state['df_rp']['Formül'].unique(), key="cif_rp")
            if sec_rp:
                satir = st.session_state['df_rp'][st.session_state['df_rp']['Formül'] == sec_rp].iloc[0]
                n_katman = satir["Katman (n)"]
                atom_parcalari = satir["A' / A / B / B'"].split(" / ")
                
                ap_cif = atom_parcalari[0].split(" ")[0]
                a_cif = atom_parcalari[1].split(" ")[0] if n_katman > 1 else "Boşluk"
                b_cif = atom_parcalari[2].split(" ")[0]
                bp_cif = atom_parcalari[3].split(" ")[0]
                
                st.download_button("💾 Yaklaşık CIF İndir", generate_cif_rp_hydride(ap_cif, a_cif, b_cif, bp_cif, n_katman), f"{sec_rp.replace(' ', '')}.cif", 'text/plain', key="dl_rpcif")
    # ==========================================
# MODÜL: SPİN-POLARİZE BANT YAPISI (BAND STRUCTURE)
# ==========================================
elif secim == "⚡ Spin-Polarize Bant Yapısı":
    st.header("Spin-Polarize Elektronik Bant Yapısı (Band Structure)")
    st.markdown("Spin up ve Spin down verilerini içeren elektronik bant yapısı dosyalarınızı yükleyin, Brillouin Zonu k-noktalarını etiketleyin ve Q1 kalitesinde grafikler oluşturun.")
    st.markdown("---")

    # --- 1. KONTROL PANELİ (SEKMELER) ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📂 Veri ve Fermi Seviyesi", 
        "📍 Brillouin Zonu (K-Noktaları)", 
        "🎨 Çizgi ve Renk Ayarları", 
        "📥 Önizleme ve İndirme"
    ])

    # ---------------------------------------------------------
    # TAB 1: VERİ YÜKLEME VE FERMİ AYARLARI
    # ---------------------------------------------------------
    with tab1:
        col_file, col_fermi = st.columns([1.5, 1])
        with col_file:
            uploaded_band = st.file_uploader("Bant Verisi (.dat, .txt)", type=["dat", "txt"])
        
        with col_fermi:
            st.markdown("**Fermi Seviyesi Ayarları**")
            fermi_shift = st.number_input("Veriyi Kaydır (E - Ef)", value=0.000, step=0.1, format="%.4f", help="Eğer veriniz Fermi seviyesine göre 0'a kaydırılmamışsa, buraya Fermi enerjisini girin. Kod otomatik çıkaracaktır.")
            draw_fermi = st.checkbox("Fermi Seviyesini (0 Noktası) Çiz", value=True)

    # ---------------------------------------------------------
    # TAB 2: BRILLOUIN ZONU (K-NOKTALARI) VE EKSENLER
    # ---------------------------------------------------------
    with tab2:
        st.info("💡 **İpucu:** K-Noktası etiketleri için 'G' yazdığınızda grafikte otomatik olarak **$\Gamma$** sembolü görünecektir.")
        
        c_kx, c_kl = st.columns(2)
        with c_kx:
            raw_k_pos = st.text_input("K-Noktası Koordinatları (Virgülle ayırın)", "0.0, 0.25, 0.5, 0.75, 1.0")
        with c_kl:
            raw_k_labels = st.text_input("K-Noktası Etiketleri (Virgülle ayırın)", "G, X, W, K, G")

        st.markdown("---")
        st.markdown("**Y Ekseni (Enerji) Ayarları**")
        c_y1, c_y2, c_y3, c_y4 = st.columns(4)
        with c_y1: y_min = st.number_input("Y Min", value=-5.0, step=1.0)
        with c_y2: y_max = st.number_input("Y Max", value=5.0, step=1.0)
        with c_y3: y_step = st.number_input("Ana Adım", value=2.0, step=0.5)
        with c_y4: y_label = st.text_input("Y Başlığı", "Energy (eV)")

    # ---------------------------------------------------------
    # TAB 3: ÇİZGİ VE RENK AYARLARI
    # ---------------------------------------------------------
    with tab3:
        st.markdown("### Spin (Bant) Çizgileri")
        cs1, cs2 = st.columns(2)
        with cs1:
            st.markdown("**Spin UP (↑)**")
            up_color = st.color_picker("Spin UP Renk", "#E74C3C")
            up_ls = st.selectbox("Spin UP Stili", ["-", "--", "-.", ":"], index=0)
            up_lw = st.slider("Spin UP Kalınlık", 0.5, 4.0, 1.5, 0.5)
            up_label = st.text_input("Spin UP Lejant Adı", r"Spin $\uparrow$")
            
        with cs2:
            st.markdown("**Spin DOWN (↓)**")
            dn_color = st.color_picker("Spin DOWN Renk", "#2980B9")
            dn_ls = st.selectbox("Spin DOWN Stili", ["-", "--", "-.", ":"], index=1)
            dn_lw = st.slider("Spin DOWN Kalınlık", 0.5, 4.0, 1.5, 0.5)
            dn_label = st.text_input("Spin DOWN Lejant Adı", r"Spin $\downarrow$")

        st.markdown("---")
        st.markdown("### Referans Çizgileri")
        cr1, cr2 = st.columns(2)
        with cr1:
            fermi_color = st.color_picker("Fermi Çizgisi Rengi", "#000000")
            fermi_ls = st.selectbox("Fermi Çizgi Stili", ["--", "-", "-.", ":"], index=0)
        with cr2:
            k_line_color = st.color_picker("K-Noktası Dikey Çizgi Rengi", "#7F8C8D")
            f_label_size = st.slider("Yazı (Font) Boyutu", 12, 24, 16)

    # ---------------------------------------------------------
    # TAB 4: VERİ OKUMA, ÇİZİM VE ÇIKTI
    # ---------------------------------------------------------
    with tab4:
        if uploaded_band is not None:
            # 1. K-Noktalarını Parse Etme ve G -> \Gamma Dönüşümü
            try:
                k_pos = [float(x.strip()) for x in raw_k_pos.split(",")]
                k_labels_raw = [x.strip() for x in raw_k_labels.split(",")]
                k_labels = [r"$\mathbf{\Gamma}$" if L.upper() == 'G' or L.upper() == 'GAMMA' else f"$\mathbf{{{L}}}$" for L in k_labels_raw]
                
                if len(k_pos) != len(k_labels):
                    st.warning("⚠️ K-Noktası koordinat sayısı ile etiket sayısı birbirine eşit değil!")
            except:
                st.error("K-Noktası girişlerinde hata var. Lütfen sadece sayı ve harfleri virgülle ayırarak girin.")
                k_pos, k_labels = [], []

            # 2. Veri Okuma ve Bantları Ayırma Algoritması
            content = uploaded_band.getvalue().decode("utf-8").splitlines()
            
            bands_up = []
            bands_dn = []
            curr_up_x, curr_up_y = [], []
            curr_dn_x, curr_dn_y = [], []

            for line in content:
                line = line.strip()
                # Eğer satır boşsa, bir bant bitti demektir. Listeye ekle ve yeni banda geç.
                if not line or line.startswith('#'):
                    if curr_up_x:
                        bands_up.append((curr_up_x, curr_up_y))
                        curr_up_x, curr_up_y = [], []
                    if curr_dn_x:
                        bands_dn.append((curr_dn_x, curr_dn_y))
                        curr_dn_x, curr_dn_y = [], []
                    continue

                parts = line.replace(',', '.').split()
                # Spin Up Sütunları
                if len(parts) >= 2:
                    try:
                        curr_up_x.append(float(parts[0]))
                        curr_up_y.append(float(parts[1]) - fermi_shift)
                    except ValueError: pass
                # Spin Down Sütunları (Varsa)
                if len(parts) >= 4:
                    try:
                        curr_dn_x.append(float(parts[2]))
                        curr_dn_y.append(float(parts[3]) - fermi_shift)
                    except ValueError: pass

            # Dosya sonundaki son bantları ekle
            if curr_up_x: bands_up.append((curr_up_x, curr_up_y))
            if curr_dn_x: bands_dn.append((curr_dn_x, curr_dn_y))

            # 3. ÇİZİM MOTORU
            if st.button("🚀 Bant Yapısını Çiz", type="primary", use_container_width=True):
                fig, ax = plt.subplots(figsize=(8, 10)) # Bant grafikleri genelde uzun ve dardır

                # Spin UP bantlarını çiz
                for i, (bx, by) in enumerate(bands_up):
                    lbl = up_label if i == 0 else "" # Lejantta sadece 1 kez görünsün
                    ax.plot(bx, by, color=up_color, linestyle=up_ls, linewidth=up_lw, label=lbl)

                # Spin DOWN bantlarını çiz
                for i, (bx, by) in enumerate(bands_dn):
                    lbl = dn_label if i == 0 else ""
                    ax.plot(bx, by, color=dn_color, linestyle=dn_ls, linewidth=dn_lw, label=lbl)

                # Y ekseni limitleri ve başlığı
                ax.set_ylim(y_min, y_max)
                ax.set_ylabel(r"$\mathbf{"+y_label.replace(" ", r"\ ")+"}$", fontsize=f_label_size+2, labelpad=10)
                ax.yaxis.set_major_locator(MultipleLocator(y_step))
                ax.yaxis.set_minor_locator(AutoMinorLocator(2))

                # X Eksenine Yüksek Simetri Noktalarını (Brillouin Zone) Ekleme
                if len(k_pos) > 0 and len(k_pos) == len(k_labels):
                    ax.set_xlim(min(k_pos), max(k_pos))
                    ax.set_xticks(k_pos)
                    ax.set_xticklabels(k_labels, fontsize=f_label_size+2)
                    
                    # Noktalar arası dikey çizgileri çiz
                    for kp in k_pos:
                        ax.axvline(x=kp, color=k_line_color, linestyle='-', linewidth=1.0, zorder=1)
                else:
                    st.warning("K-Noktası ayarları eksik olduğu için Brillouin bölgesi çizilemedi.")

                # Fermi Seviyesi (0 Noktası)
                if draw_fermi:
                    ax.axhline(y=0.0, color=fermi_color, linestyle=fermi_ls, linewidth=1.5, zorder=2)

                # Çerçeve ve Estetik İnce Ayarlar
                ax.tick_params(axis='y', which='major', direction='in', length=8, width=2.0, labelsize=f_label_size, right=True)
                ax.tick_params(axis='y', which='minor', direction='in', length=4, width=1.5, right=True)
                ax.tick_params(axis='x', which='major', direction='in', length=10, width=2.0, bottom=True, top=True)
                
                for spine in ax.spines.values():
                    spine.set_linewidth(2.0)
                for label in ax.get_yticklabels():
                    label.set_fontweight('bold')

                # Lejant
                if bands_dn: # Sadece Spin Up ve Spin Down varsa lejant koy
                    ax.legend(loc='upper right', frameon=True, prop={'weight':'bold', 'size':f_label_size-2}).get_frame().set_linewidth(1.5)

                plt.tight_layout()
                st.pyplot(fig)

                # 4. İNDİRME BÖLÜMÜ
                st.markdown("### 📥 Makale Formatında İndir")
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    buf_png = io.BytesIO()
                    fig.savefig(buf_png, format="png", dpi=600, bbox_inches='tight')
                    st.download_button("PNG İndir (600 DPI)", buf_png.getvalue(), "Band_Structure.png", "image/png", use_container_width=True)
                with c_d2:
                    buf_svg = io.BytesIO()
                    fig.savefig(buf_svg, format="svg", bbox_inches='tight')
                    st.download_button("SVG İndir (Vektörel)", buf_svg.getvalue(), "Band_Structure.svg", "image/svg+xml", use_container_width=True)
        else:
            st.info("Lütfen '1. Veri ve Fermi Seviyesi' sekmesinden bant verinizi yükleyin.")