import streamlit as st

def get_unified_plot_settings(prefix="common_"):
    """
    Tüm modüller için ortak, profesyonel grafik ayarları paneli.
    Döndürdüğü sözlük (dictionary) sayesinde modüller bu ayarları uygular.
    """
    settings = {}
    
    with st.sidebar.expander("🎨 PROFESYONEL GRAFİK AYARLARI", expanded=False):
        
        tab_genel, tab_eksen, tab_font, tab_text = st.tabs(["Genel", "Eksen/Çerçeve", "Fontlar", "Metin/Lejant"])
        
        # -----------------------------
        # TAB 1: GENEL VE MOD
        # -----------------------------
        with tab_genel:
            st.markdown("### Görünüm ve Boyut")
            settings["dark_mode"] = st.toggle("🌙 Koyu Mod (Dark Mode)", value=False, key=f"{prefix}dark_mode")
            settings["dpi"] = st.number_input("Çıktı Çözünürlüğü (DPI)", min_value=100, max_value=1500, value=600, step=100, key=f"{prefix}dpi")
            
            st.markdown("### Grafik Boyutları (inç)")
            c1, c2 = st.columns(2)
            with c1:
                settings["fig_width"] = st.number_input("Genişlik", value=14.0, step=0.5, key=f"{prefix}fig_w")
            with c2:
                settings["fig_height"] = st.number_input("Yükseklik", value=8.0, step=0.5, key=f"{prefix}fig_h")
                
        # -----------------------------
        # TAB 2: EKSEN VE ÇERÇEVE
        # -----------------------------
        with tab_eksen:
            st.markdown("### Çerçeve (Spines)")
            settings["spine_width"] = st.number_input("Çerçeve Kalınlığı", min_value=0.5, max_value=5.0, value=2.5, step=0.1, key=f"{prefix}spine_w")
            settings["spine_color"] = st.color_picker("Çerçeve Rengi", value="#FFFFFF" if settings["dark_mode"] else "#000000", key=f"{prefix}spine_color")
            
            st.markdown("### Adımlar (Ticks)")
            settings["major_tick_len"] = st.number_input("Major Tick Uzunluğu", value=12.0, key=f"{prefix}maj_tick_l")
            settings["minor_tick_len"] = st.number_input("Minor Tick Uzunluğu", value=6.0, key=f"{prefix}min_tick_l")
            settings["tick_width"] = st.number_input("Tick Kalınlığı", value=2.5, step=0.1, key=f"{prefix}tick_w")
            settings["show_minor_ticks"] = st.checkbox("Minor Tick'leri Göster", value=True, key=f"{prefix}show_minor")
            
            st.markdown("### X Eksen Sınırları")
            settings["use_custom_x"] = st.checkbox("Özel X Sınırı", value=False, key=f"{prefix}custom_x")
            if settings["use_custom_x"]:
                cx1, cx2 = st.columns(2)
                with cx1:
                    settings["x_min"] = st.number_input("X Min", value=0.0, key=f"{prefix}x_min")
                with cx2:
                    settings["x_max"] = st.number_input("X Max", value=10.0, key=f"{prefix}x_max")
                settings["x_step"] = st.number_input("X Adım (Step)", value=1.0, min_value=0.01, key=f"{prefix}x_step")
            
            st.markdown("### Y Eksen Sınırları")
            settings["use_custom_y"] = st.checkbox("Özel Y Sınırı", value=False, key=f"{prefix}custom_y")
            if settings["use_custom_y"]:
                cy1, cy2 = st.columns(2)
                with cy1:
                    settings["y_min"] = st.number_input("Y Min", value=-5.0, key=f"{prefix}y_min")
                with cy2:
                    settings["y_max"] = st.number_input("Y Max", value=5.0, key=f"{prefix}y_max")
                settings["y_step"] = st.number_input("Y Adım (Step)", value=1.0, min_value=0.01, key=f"{prefix}y_step")
                    
        # -----------------------------
        # TAB 3: YAZI VE FONTLAR
        # -----------------------------
        with tab_font:
            st.markdown("### Tipografi")
            settings["font_family"] = st.selectbox("Yazı Tipi Ailesi", ["Arial", "Times New Roman", "Helvetica", "Courier New", "serif", "sans-serif"], index=0, key=f"{prefix}font_fam")
            
            st.markdown("### Punto Büyüklükleri")
            settings["title_size"] = st.number_input("Ana Başlık Büyüklüğü", value=28, key=f"{prefix}title_size")
            settings["label_size"] = st.number_input("Eksen İsimleri Büyüklüğü (X/Y Labels)", value=24, key=f"{prefix}label_size")
            settings["tick_label_size"] = st.number_input("Eksen Sayıları Büyüklüğü (Tick Labels)", value=20, key=f"{prefix}tick_lbl_size")
            
            st.markdown("### Ağırlık ve Mesafe")
            settings["font_weight"] = st.selectbox("Yazı Kalınlığı", ["normal", "bold", "heavy", "light"], index=1, key=f"{prefix}font_weight")
            settings["label_pad"] = st.number_input("Eksen İsimlerinin Çerçeveye Uzaklığı (Padding)", value=15, key=f"{prefix}label_pad")
            
            settings["font_color"] = st.color_picker("Yazı Rengi", value="#FFFFFF" if settings["dark_mode"] else "#000000", key=f"{prefix}font_color")

        # -----------------------------
        # TAB 4: ÖZEL METİN VE LEJANT
        # -----------------------------
        with tab_text:
            st.markdown("### Lejant Konumlandırma")
            settings["show_legend"] = st.checkbox("Lejantı Göster", value=True, key=f"{prefix}show_leg")
            if settings["show_legend"]:
                st.info("Lejantın grafikteki konumunu eksen yüzdeleri (0.0 ile 1.0 arası) ile ayarlayın.")
                c_lx, c_ly = st.columns(2)
                with c_lx:
                    settings["leg_x"] = st.slider("Lejant X Konumu", min_value=-0.5, max_value=1.5, value=1.0, step=0.01, key=f"{prefix}leg_x")
                with c_ly:
                    settings["leg_y"] = st.slider("Lejant Y Konumu", min_value=-0.5, max_value=1.5, value=1.0, step=0.01, key=f"{prefix}leg_y")
                settings["leg_size"] = st.number_input("Lejant Punto Büyüklüğü", value=20, key=f"{prefix}leg_size")
                settings["leg_frame"] = st.checkbox("Lejant Çerçevesi Çiz", value=True, key=f"{prefix}leg_frame")
            
            st.markdown("---")
            st.markdown("### Özel Metin (Custom Annotation)")
            settings["custom_text"] = st.text_input("Grafiğe Eklenecek Özel Metin", value="", placeholder="Örn: Band Gap = 1.2 eV", key=f"{prefix}custom_txt")
            if settings["custom_text"].strip() != "":
                c_tx, c_ty = st.columns(2)
                with c_tx:
                    settings["txt_x"] = st.slider("Metin X Konumu", min_value=-0.5, max_value=1.5, value=0.5, step=0.01, key=f"{prefix}txt_x")
                with c_ty:
                    settings["txt_y"] = st.slider("Metin Y Konumu", min_value=-0.5, max_value=1.5, value=0.9, step=0.01, key=f"{prefix}txt_y")
                settings["txt_size"] = st.number_input("Özel Metin Büyüklüğü", value=22, key=f"{prefix}txt_size")
                
    return settings

def apply_plot_settings(fig, settings):
    """
    Bir matplotlib ekseni (ax) üzerine, yukarıdaki arayüzden gelen ayarları uygular.
    """
    import matplotlib.pyplot as plt
    from matplotlib.ticker import AutoMinorLocator, MultipleLocator

    bg_color = "#1E1E1E" if settings["dark_mode"] else "#FFFFFF"
    fg_color = settings["font_color"]
    spine_color = settings["spine_color"]

    
    fig.patch.set_facecolor(bg_color)
    for ax in fig.axes:
        ax.set_facecolor(bg_color)

        for spine in ax.spines.values():
            spine.set_linewidth(settings["spine_width"])
            spine.set_color(spine_color)
        
        if settings["show_minor_ticks"]:
            ax.xaxis.set_minor_locator(AutoMinorLocator())
            ax.yaxis.set_minor_locator(AutoMinorLocator())
            ax.tick_params(axis='both', which='minor', length=settings["minor_tick_len"], width=settings["tick_width"]/1.5, colors=fg_color, direction='in', top=True, right=True)
        else:
            ax.tick_params(axis='both', which='minor', bottom=False, left=False, top=False, right=False)

        ax.tick_params(axis='both', which='major', length=settings["major_tick_len"], width=settings["tick_width"], colors=fg_color, labelsize=settings["tick_label_size"], direction='in', top=True, right=True)

        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontweight(settings["font_weight"])
            label.set_fontfamily(settings["font_family"])
            label.set_color(fg_color)
            
        ax.xaxis.label.set_color(fg_color)
        ax.yaxis.label.set_color(fg_color)
        ax.xaxis.label.set_fontsize(settings["label_size"])
        ax.yaxis.label.set_fontsize(settings["label_size"])
        ax.xaxis.label.set_fontweight(settings["font_weight"])
        ax.yaxis.label.set_fontweight(settings["font_weight"])
        ax.xaxis.label.set_fontfamily(settings["font_family"])
        ax.yaxis.label.set_fontfamily(settings["font_family"])
        
        ax.xaxis.labelpad = settings["label_pad"]
        ax.yaxis.labelpad = settings["label_pad"]
        
        if ax.get_title():
            ax.title.set_color(fg_color)
            ax.title.set_fontsize(settings["title_size"])
            ax.title.set_fontweight(settings["font_weight"])
            ax.title.set_fontfamily(settings["font_family"])

        if settings["use_custom_x"]:
            ax.set_xlim(settings["x_min"], settings["x_max"])
            ax.xaxis.set_major_locator(MultipleLocator(settings["x_step"]))
        if settings["use_custom_y"]:
            ax.set_ylim(settings["y_min"], settings["y_max"])
            ax.yaxis.set_major_locator(MultipleLocator(settings["y_step"]))
            
        if settings.get("custom_text", "").strip() != "":
            ax.text(settings["txt_x"], settings["txt_y"], settings["custom_text"],
                    transform=ax.transAxes, fontsize=settings["txt_size"],
                    fontweight=settings["font_weight"], fontfamily=settings["font_family"],
                    color=fg_color, va='center', ha='center')
