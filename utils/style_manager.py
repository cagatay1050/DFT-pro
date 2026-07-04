import matplotlib as mpl
import matplotlib.pyplot as plt
from PyQt6.QtCore import QObject, pyqtSignal

class StyleNotifier(QObject):
    style_changed = pyqtSignal()

notifier = StyleNotifier()


# Global state for settings
current_settings = {
    "dpi": 150, "save_dpi": 600, "fig_width": 8.0, "fig_height": 5.0,
    "font_family": "Times New Roman", "font_base": 14, "font_title": 16,
    "font_label": 15, "font_tick": 13, "axes_width": 2.0, "line_width": 2.5,
    "cmap": "tab10", "tick_dir": "in", "maj_tick_len": 6.0, "maj_tick_wid": 2.0,
    "minor_ticks": True, "min_tick_len": 3.0, "min_tick_wid": 1.2,
    "top_right_ticks": True, "grid": False, "legend_frame": False,
    "dark_mode": False, 
    "use_custom_x": False, "x_min": 0.0, "x_max": 10.0, "x_step": 1.0,
    "use_custom_y": False, "y_min": -5.0, "y_max": 5.0, "y_step": 1.0,
    "show_legend": True, "leg_x": 1.0, "leg_y": 1.0, "leg_size": 14,
    "custom_text": "", "txt_x": 0.5, "txt_y": 0.9, "txt_size": 16
}

def apply_global_style():
    """
    Applies the OriginLab style global matplotlib settings using current_settings.
    """
    s = current_settings
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.rcParams['mathtext.fontset'] = 'stix'
    
    mpl.rcParams.update({
        "figure.figsize": (s["fig_width"], s["fig_height"]),
        "figure.dpi": s["dpi"],
        "savefig.dpi": s["save_dpi"],
        "savefig.bbox": "tight",
        "font.family": "sans-serif" if s["font_family"] != "Times New Roman" else "serif",
        "font.sans-serif": [s["font_family"]],
        "font.serif": [s["font_family"]],
        "font.size": s["font_base"],
        "axes.titlesize": s["font_title"],
        "axes.labelsize": s["font_label"],
        "xtick.labelsize": s["font_tick"],
        "ytick.labelsize": s["font_tick"],
        "legend.fontsize": s["font_base"] - 2,
        "axes.linewidth": s["axes_width"],
        "lines.linewidth": s["line_width"],
        "axes.prop_cycle": plt.cycler('color', plt.get_cmap(s["cmap"]).colors) if s["cmap"] in ['tab10', 'Set1', 'Dark2'] else plt.rcParams['axes.prop_cycle'],
        "xtick.direction": s["tick_dir"],
        "ytick.direction": s["tick_dir"],
        "xtick.major.size": s["maj_tick_len"],
        "ytick.major.size": s["maj_tick_len"],
        "xtick.major.width": s["maj_tick_wid"],
        "ytick.major.width": s["maj_tick_wid"],
        "xtick.minor.visible": s["minor_ticks"],
        "ytick.minor.visible": s["minor_ticks"],
        "xtick.minor.size": s["min_tick_len"],
        "ytick.minor.size": s["min_tick_len"],
        "xtick.minor.width": s["min_tick_wid"],
        "ytick.minor.width": s["min_tick_wid"],
        "xtick.top": s["top_right_ticks"],
        "ytick.right": s["top_right_ticks"],
        "axes.grid": s["grid"],
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
        "legend.frameon": s["legend_frame"],
        "legend.edgecolor": "black",
        "legend.fancybox": False
    })


def apply_custom_axes_settings(fig):
    s = current_settings
    bg_color = "#1E1E1E" if s.get("dark_mode", False) else "#FFFFFF"
    fg_color = "#FFFFFF" if s.get("dark_mode", False) else "#000000"
    spine_color = "#FFFFFF" if s.get("dark_mode", False) else "#000000"
    
    fig.patch.set_facecolor(bg_color)
    
    from matplotlib.ticker import MultipleLocator
    
    for ax in fig.axes:
        ax.set_facecolor(bg_color)
        
        for spine in ax.spines.values():
            spine.set_color(spine_color)
            
        ax.tick_params(colors=fg_color, which='both')
        
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color(fg_color)
            
        ax.xaxis.label.set_color(fg_color)
        ax.yaxis.label.set_color(fg_color)
        
        if ax.get_title():
            ax.title.set_color(fg_color)
            
        if s.get("use_custom_x", False):
            ax.set_xlim(s["x_min"], s["x_max"])
            ax.xaxis.set_major_locator(MultipleLocator(s["x_step"]))
            
        if s.get("use_custom_y", False):
            ax.set_ylim(s["y_min"], s["y_max"])
            ax.yaxis.set_major_locator(MultipleLocator(s["y_step"]))
            
        if s.get("custom_text", "").strip() != "":
            ax.text(s["txt_x"], s["txt_y"], s["custom_text"],
                    transform=ax.transAxes, fontsize=s["txt_size"],
                    color=fg_color, va='center', ha='center')
                    
        # Find legend and update it if it exists
        leg = ax.get_legend()
        if leg:
            if not s.get("show_legend", True):
                leg.set_visible(False)
            else:
                leg.set_visible(True)
                leg.set_bbox_to_anchor((s.get("leg_x", 1.0), s.get("leg_y", 1.0)))
                
                for text in leg.get_texts():
                    text.set_color(fg_color)
                    text.set_fontsize(s.get("leg_size", 14))
                
                frame = leg.get_frame()
                if s.get("legend_frame", False):
                    frame.set_linewidth(1)
                    frame.set_edgecolor(spine_color)
                    frame.set_facecolor(bg_color)
                else:
                    frame.set_linewidth(0)
                    frame.set_facecolor('none')
