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
    "top_right_ticks": True, "grid": False, "legend_frame": False
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
