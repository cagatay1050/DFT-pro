import os
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QCheckBox, QDoubleSpinBox, QGroupBox, QFormLayout, QScrollArea, QLineEdit
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import ConvexHull
import warnings

try:
    from pymatgen.core import Structure
    HAS_PYMATGEN = True
except ImportError:
    HAS_PYMATGEN = False

# Standard Jmol Colors for elements
JMOL_COLORS = {
    "H": "#FFFFFF", "He": "#D9FFFF", "Li": "#CC80FF", "Be": "#C2FF00", "B": "#FFB5B5", 
    "C": "#909090", "N": "#3050F8", "O": "#FF0D0D", "F": "#90E050", "Ne": "#B3E3F5", 
    "Na": "#AB5CF2", "Mg": "#8AFF00", "Al": "#BFA6A6", "Si": "#F0C8A0", "P": "#FF8000", 
    "S": "#FFFF30", "Cl": "#1FF01F", "Ar": "#80D1E3", "K": "#8F40D4", "Ca": "#3DFF00", 
    "Sc": "#E6E6E6", "Ti": "#BFC2C7", "V": "#A6A6AB", "Cr": "#8A99C7", "Mn": "#9C7AC7", 
    "Fe": "#E06633", "Co": "#F090A0", "Ni": "#50D050", "Cu": "#C88033", "Zn": "#7D80B0", 
    "Ga": "#C28F8F", "Ge": "#668F8F", "As": "#BD80E3", "Se": "#FFA100", "Br": "#A62929", 
    "Kr": "#5CB8D1", "Rb": "#702EB0", "Sr": "#00FF00", "Y": "#94FFFF", "Zr": "#94E0E0", 
    "Nb": "#73C2C9", "Mo": "#54B5B5", "Tc": "#3B9E9E", "Ru": "#248F8F", "Rh": "#0A7D8C", 
    "Pd": "#006985", "Ag": "#C0C0C0", "Cd": "#FFD98F", "In": "#A67573", "Sn": "#668080", 
    "Sb": "#9E63B5", "Te": "#D47A00", "I": "#940094", "Xe": "#429EB0", "Cs": "#57178F", 
    "Ba": "#00C900"
}

class KristalGoruntuleyiciWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.structure = None
        self.unique_species = []
        self.legend_inputs = {}
        self.initUI()
        
    def initUI(self):
        main_layout = QHBoxLayout(self)
        
        # LEFT PANEL: Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(320)
        
        # 1. File Upload
        grp_file = QGroupBox("1. Kristal Dosyası (POSCAR/CIF)")
        v_file = QVBoxLayout()
        self.btn_load = QPushButton("📂 Yapı Dosyası Yükle")
        self.btn_load.setStyleSheet("background-color: #2980b9; color: white; padding: 10px; font-weight: bold;")
        self.btn_load.clicked.connect(self.load_file)
        self.lbl_file = QLabel("Yüklü Dosya: Yok")
        self.lbl_file.setWordWrap(True)
        v_file.addWidget(self.btn_load)
        v_file.addWidget(self.lbl_file)
        grp_file.setLayout(v_file)
        left_layout.addWidget(grp_file)
        
        # 2. Plot Settings
        grp_settings = QGroupBox("2. Görüntüleme Ayarları")
        f_settings = QFormLayout()
        
        self.chk_bonds = QCheckBox("Bağları Çiz (Sticks)")
        self.chk_bonds.setChecked(True)
        
        self.spn_cutoff = QDoubleSpinBox()
        self.spn_cutoff.setRange(0.5, 5.0)
        self.spn_cutoff.setSingleStep(0.1)
        self.spn_cutoff.setValue(2.5)
        
        self.chk_polyhedra = QCheckBox("Polihedra (Çok Yüzlü) Göster")
        self.chk_polyhedra.setChecked(False)
        
        self.chk_labels = QCheckBox("Atom İsimlerini (Sembol) Göster")
        self.chk_labels.setChecked(False)
        
        self.chk_axes = QCheckBox("Eksen Oklarını (a, b, c) Göster")
        self.chk_axes.setChecked(True)
        
        f_settings.addRow("", self.chk_bonds)
        f_settings.addRow("Bağ Uzunluk Sınırı (Å):", self.spn_cutoff)
        f_settings.addRow("", self.chk_polyhedra)
        f_settings.addRow("", self.chk_labels)
        f_settings.addRow("", self.chk_axes)
        
        grp_settings.setLayout(f_settings)
        left_layout.addWidget(grp_settings)
        
        # 3. Dynamic Legend Panel
        grp_legend = QGroupBox("3. Atom Lejantı (Açıklamalar)")
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
        
        # Draw Button
        self.btn_draw = QPushButton("🎨 Kristali Çiz")
        self.btn_draw.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; font-weight: bold; font-size: 14px;")
        self.btn_draw.clicked.connect(self.plot_graph)
        left_layout.addWidget(self.btn_draw)
        
        left_layout.addStretch()
        
        # RIGHT PANEL: Canvas
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.figure = plt.figure(figsize=(8, 6), dpi=150)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.canvas)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, stretch=1)
        
    def load_file(self):
        if not HAS_PYMATGEN:
            self.lbl_file.setText("HATA: pymatgen kütüphanesi bulunamadı!")
            return
            
        file_path, _ = QFileDialog.getOpenFileName(self, "Kristal Dosyası Seç (POSCAR, .cif)", "", "All Files (*)")
        if file_path:
            try:
                self.structure = Structure.from_file(file_path)
                self.lbl_file.setText(f"Yüklü: {os.path.basename(file_path)}\n"
                                      f"Atom Sayısı: {len(self.structure)}\n"
                                      f"Formül: {self.structure.composition.reduced_formula}")
                self.build_legend_ui()
                self.plot_graph()
            except Exception as e:
                self.lbl_file.setText(f"Hata: Dosya okunamadı.\nDetay: {str(e)}")
                
    def build_legend_ui(self):
        # Clear old legend
        for i in reversed(range(self.legend_layout.count())): 
            widget = self.legend_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        self.unique_species = []
        self.legend_inputs = {}
        
        if not self.structure: return
        
        # Find unique elements
        for site in self.structure:
            if site.species_string not in self.unique_species:
                self.unique_species.append(site.species_string)
                
        # Create UI for each element
        for elem in self.unique_species:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            color = JMOL_COLORS.get(elem, "#888888")
            
            # Colored dot
            lbl_color = QLabel()
            lbl_color.setFixedSize(20, 20)
            lbl_color.setStyleSheet(f"background-color: {color}; border-radius: 10px; border: 1px solid black;")
            
            lbl_elem = QLabel(elem)
            lbl_elem.setFixedWidth(30)
            lbl_elem.setStyleSheet("font-weight: bold;")
            
            txt_desc = QLineEdit()
            txt_desc.setPlaceholderText(f"{elem} atomu için açıklama...")
            
            self.legend_inputs[elem] = txt_desc
            
            row_layout.addWidget(lbl_color)
            row_layout.addWidget(lbl_elem)
            row_layout.addWidget(txt_desc)
            self.legend_layout.addWidget(row_widget)
            
    def plot_graph(self):
        if not self.structure: return
        
        self.figure.clear()
        # Custom 3D axis
        ax = self.figure.add_subplot(111, projection='3d')
        
        draw_bonds = self.chk_bonds.isChecked()
        draw_poly = self.chk_polyhedra.isChecked()
        draw_labels = self.chk_labels.isChecked()
        draw_axes = self.chk_axes.isChecked()
        cutoff = self.spn_cutoff.value()
        
        # 1. Plot Atoms
        x, y, z, colors, sizes = [], [], [], [], []
        
        for site in self.structure:
            x.append(site.coords[0])
            y.append(site.coords[1])
            z.append(site.coords[2])
            colors.append(JMOL_COLORS.get(site.species_string, "#888888"))
            sizes.append(200 if site.species_string in ["O", "H", "C", "N", "F"] else 400)
            
            if draw_labels:
                ax.text(*site.coords, site.species_string, size=10, zorder=5, color='black',
                        horizontalalignment='center', verticalalignment='center')
                
        ax.scatter(x, y, z, c=colors, s=sizes, depthshade=True, edgecolors='black', linewidths=0.5, zorder=4)
        
        # 2. Draw Bonds (Sticks) & Polyhedra
        # We need a robust way for polyhedra. Just looking for neighbors within cutoff.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for site in self.structure:
                neighbors = self.structure.get_neighbors(site, r=cutoff)
                if not neighbors: continue
                
                # Draw bonds
                if draw_bonds:
                    for n in neighbors:
                        # Only draw half bond to avoid overlapping lines
                        dx = (n.coords[0] - site.coords[0]) / 2.0
                        dy = (n.coords[1] - site.coords[1]) / 2.0
                        dz = (n.coords[2] - site.coords[2]) / 2.0
                        ax.plot([site.coords[0], site.coords[0]+dx],
                                [site.coords[1], site.coords[1]+dy],
                                [site.coords[2], site.coords[2]+dz],
                                color=JMOL_COLORS.get(site.species_string, "#888888"), linewidth=4, zorder=2)
                                
                # Draw Polyhedra (only for cations, simplistically: assume large atoms are centers)
                # To keep it generic, draw polyhedra if it has 4 or more neighbors
                if draw_poly and len(neighbors) >= 4:
                    pts = [n.coords for n in neighbors]
                    try:
                        hull = ConvexHull(pts)
                        poly_color = JMOL_COLORS.get(site.species_string, "#888888")
                        for simplex in hull.simplices:
                            poly = Poly3DCollection([np.array(pts)[simplex]], alpha=0.2, facecolors=poly_color, edgecolors='gray', linewidths=0.5, zorder=1)
                            ax.add_collection3d(poly)
                    except Exception:
                        pass
                        
        # 3. Draw Cell Borders (Bounding Box)
        lattice = self.structure.lattice.matrix
        # origin
        o = np.array([0,0,0])
        a, b, c = lattice[0], lattice[1], lattice[2]
        corners = [
            (o, a), (o, b), (o, c),
            (a, a+b), (a, a+c),
            (b, a+b), (b, b+c),
            (c, a+c), (c, b+c),
            (a+b, a+b+c), (a+c, a+b+c), (b+c, a+b+c)
        ]
        for p1, p2 in corners:
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color='black', linestyle='--', linewidth=1, zorder=0)
            
        # 4. Axes Arrows
        if draw_axes:
            max_len = max(np.linalg.norm(a), np.linalg.norm(b), np.linalg.norm(c)) * 0.2
            # a = red, b = green, c = blue
            ax.quiver(0,0,0, a[0], a[1], a[2], color='red', length=max_len/np.linalg.norm(a), normalize=True, arrow_length_ratio=0.2)
            ax.quiver(0,0,0, b[0], b[1], b[2], color='green', length=max_len/np.linalg.norm(b), normalize=True, arrow_length_ratio=0.2)
            ax.quiver(0,0,0, c[0], c[1], c[2], color='blue', length=max_len/np.linalg.norm(c), normalize=True, arrow_length_ratio=0.2)
            
            # a b c labels
            ax.text(*(a * (max_len/np.linalg.norm(a) * 1.2)), "a", color='red', weight='bold')
            ax.text(*(b * (max_len/np.linalg.norm(b) * 1.2)), "b", color='green', weight='bold')
            ax.text(*(c * (max_len/np.linalg.norm(c) * 1.2)), "c", color='blue', weight='bold')
            
        # 5. Draw Legend Texts on the Plot
        # We will collect the texts from the inputs and plot them as a custom legend
        legend_elements = []
        for elem, txt_input in self.legend_inputs.items():
            desc = txt_input.text().strip()
            if desc:
                label = f"{elem}: {desc}"
            else:
                label = elem
                
            color = JMOL_COLORS.get(elem, "#888888")
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', label=label,
                                              markerfacecolor=color, markeredgecolor='k', markersize=12))
                                              
        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.05, 1), title="Atom Tanımları", borderaxespad=0.)
            
        # Equal aspect ratio for 3D is tricky in matplotlib, we set limits based on max range
        all_coords = self.structure.cart_coords
        max_range = np.array([all_coords[:,0].max()-all_coords[:,0].min(), 
                              all_coords[:,1].max()-all_coords[:,1].min(), 
                              all_coords[:,2].max()-all_coords[:,2].min()]).max() / 2.0
                              
        mid_x = (all_coords[:,0].max()+all_coords[:,0].min()) * 0.5
        mid_y = (all_coords[:,1].max()+all_coords[:,1].min()) * 0.5
        mid_z = (all_coords[:,2].max()+all_coords[:,2].min()) * 0.5
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        
        ax.axis('off') # Hide grids and ticks for clean look
        self.figure.tight_layout()
        
        try:
            from utils.style_manager import apply_custom_axes_settings
            apply_custom_axes_settings(self.figure)
        except Exception:
            pass
            
        self.canvas.draw()
