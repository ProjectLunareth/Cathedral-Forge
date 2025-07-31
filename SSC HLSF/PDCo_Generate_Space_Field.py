"""
PDCo Open-Source High-Level Space Field Python Generator
© 02/14/2025 by Primary Design Co. (Alex London)

https://www.primarydesignco.com
"""

import logging
import math
from collections.abc import Iterable
from typing import List, Tuple, Optional, Callable, Any

import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.transforms import Affine2D
from matplotlib.animation import FuncAnimation

import tkinter as tk
from tkinter import messagebox, font as tkFont, filedialog

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

vTitle: str = "PDCo Open-Source High-Level Space Field Python Generator"

colors_mapped: List[str] = [
    'red', 'green', 'blue', 'yellow',
    'pink', 'purple', 'orange', 'cyan', 'magenta',
    'lime', 'maroon', 'navy', 'olive', 'teal', 'violet',
    'brown', 'gold', 'lightcoral', 'darkkhaki', 'darkgreen',
    'darkblue', 'darkred', 'turquoise', 'indigo', 'darkorange',
    'lightgreen', 'tan', 'salmon', 'plum', 'orchid', 'sienna',
    'skyblue', 'khaki', 'slateblue', 'goldenrod', 'mediumblue',
    'greenyellow', 'burlywood', 'seagreen', 'slategray',
    'cornflowerblue', 'mediumorchid', 'sandybrown', 'tomato',
    'lightblue', 'limegreen', 'lightgrey', 'lightpink', 'thistle',
    'palegreen', 'azure', 'lavender', 'honeydew', 'mintcream', 'aliceblue',
    'black', 'white'
]


def get_numeric_entry(entry_widget: tk.Entry, min_val: float = 0, max_val: float = 1) -> Optional[float]:
    try:
        value = float(entry_widget.get())
        if min_val <= value <= max_val:
            return value
        else:
            messagebox.showerror("Error", f"Value must be between {min_val} and {max_val}.")
            return None
    except ValueError:
        messagebox.showerror("Error", "Invalid numeric value entered.")
        return None


def create_labeled_frame(parent: tk.Widget, text: str, font: tkFont.Font) -> tk.LabelFrame:
    frame = tk.LabelFrame(parent, text=text, font=font)
    frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
    return frame


def calculate_symmetry_point_adjusted(center: Tuple[float, float],
                                      radius: float,
                                      sides: int,
                                      level: int) -> np.ndarray:
    """
    For level 1, return the center.
    For higher levels, accumulate the offset computed at each level.
    
    With center=(0,0), radius=1, and sides=4 this produces:
      Level 1: [0, 0, 0]
      Level 2: [0, 1, 0]
      Level 3: [0, 3, 0]
      Level 4: [0, 7, 0]
      Level 5: [0, 17, 0]
    """
    center3d = np.array([center[0], center[1], 0])
    if level <= 1:
        print(f"Level {level} <= 1, returning center: {center3d}")
        return center3d

    cumulative_offset = np.array([0.0, 0.0, 0.0])
    for current_level in range(2, level + 1):
        scaling_factor = multiplier(current_level, sides)
        current_adjustment = radius * scaling_factor
        verts = generate_vertices(center, current_adjustment, sides)
        # For even sides, use vertex 0 (which lies directly above the center)
        if sides % 2 == 1:
            current_offset = np.array(midpoint(verts[0], verts[1])) - center3d
        else:
            current_offset = np.array(verts[0]) - center3d

        cumulative_offset += current_offset
        print(f"Level {current_level}: scaling_factor={scaling_factor}, "
              f"current_adjustment={current_adjustment}, "
              f"current_offset={current_offset}, "
              f"cumulative_offset={cumulative_offset}")

    new_origin = center3d + cumulative_offset
    print(f"Returning symmetry point: {new_origin}")
    return new_origin


def multiplier(level: int, sides: int) -> float:
    if sides % 2 == 0:
        return 2 ** (level - 2)
    else:
        return 1.5 ** (level - 2)



def generate_base_level_polygon(
    vertices: np.ndarray,
    fig: plt.Figure,
    ax: plt.Axes,
    center: Tuple[float, float],
    radius: float,
    sides: int,
    alpha: float,
    draw_base: bool,
    levels: int,
    colors_mapped: List[str],
    edges_only: bool = False,
    line_width: float = 1
) -> List[patches.Polygon]:
    base_level_rays: List[patches.Polygon] = []
    polygon = patches.Polygon(vertices, closed=True, edgecolor='black' if edges_only else 'none',
                              facecolor='none', linewidth=line_width)
    #ax.add_patch(polygon)
    if draw_base:
        for j in range(1, (sides // 2 + 2) if sides % 2 else (sides // 2 + 1)):
            i = 0
            start_vertex = vertices[i]
            end_vertex = vertices[(i + j + 1) % sides]
            if j < sides // 2:
                ax.plot([start_vertex[0], end_vertex[0]], [start_vertex[1], end_vertex[1]], color='None')
            start_vertex = vertices[i]
            middle_vertex = vertices[(i + j) % sides]
            end_vertex = vertices[(i + j - 1) % sides]
            triangle = np.array([start_vertex, middle_vertex, end_vertex])
            color_index = (j - 2) % len(colors_mapped)
            color = colors_mapped[color_index] if not edges_only else 'none'
            base_level_ray = patches.Polygon(
                triangle, closed=True,
                edgecolor='black' if edges_only else 'none',
                fill=not edges_only, facecolor=color, alpha=alpha, linewidth=line_width
            )
            ax.add_patch(base_level_ray)
            base_level_rays.append(base_level_ray)
    return base_level_rays

def generate_vertices(center, radius, sides):
    """
    Generates vertices for a regular polygon.
    For even sides, vertex0 is at angle 0, i.e. directly above the center.
    """
    vertices = []
    angle = (2 * math.pi) / sides
    cx, cy = center
    for side in range(sides):
        theta = angle * side
        x = cx + radius * math.sin(theta)
        y = cy + radius * math.cos(theta)
        vertices.append((x, y, 0))
    return vertices


def midpoint(p1, p2):
    """Returns the midpoint between two 3D points."""
    return ((p1[0] + p2[0]) / 2,
            (p1[1] + p2[1]) / 2,
            (p1[2] + p2[2]) / 2)

def generate_first_level_polygon(
    fig: plt.Figure,
    ax: plt.Axes,
    center: Tuple[float, float],
    sides: int,
    alpha: float,
    base_level_rays: List[patches.Polygon],
    edges_only: bool = False,
    line_width: float = 1
) -> List[patches.Polygon]:
    first_level_rays: List[patches.Polygon] = [base_level_rays]
    layers = sides
    for i in range(1, layers):
        angle = 360 / layers * i
        rotation = Affine2D().rotate_deg_around(center[0], center[1], angle)
        for patch in base_level_rays:
            rotated_patch = patches.Polygon(
                patch.get_xy(), closed=True,
                edgecolor='black' if edges_only else 'none',
                fill=not edges_only, facecolor=patch.get_facecolor() if not edges_only else 'none',
                alpha=alpha, linewidth=line_width
            )
            rotated_patch.set_transform(rotation + ax.transData)
            ax.add_patch(rotated_patch)
            first_level_rays.append(rotated_patch)
    ax.set_aspect('equal')
    return first_level_rays


def generate_higher_levels(
    vertices: np.ndarray,
    fig,
    ax,
    center: tuple,
    radius: float,
    sides: int,
    current_level: int,
    max_levels: int,
    n_levels_rays: list,
    edges_only: bool = False,
    line_width: float = 1,
    cancel_callback=lambda: False
) -> None:
    if cancel_callback():
        return
    if current_level > max_levels or n_levels_rays[0][0].get_alpha() < 0.01:
        return

    new_level_patches = []

    def process_patches(patch_list, rotation: Affine2D, accumulated_patches: list) -> None:
        for patch in patch_list:
            if cancel_callback():
                return
            if isinstance(patch, Iterable) and not isinstance(patch, str):
                sub_patches = []
                process_patches(patch, rotation, sub_patches)
                accumulated_patches.append(sub_patches)
            else:
                orig_vertices = patch.get_xy()
                rotated_vertices = rotation.transform(orig_vertices)
                rotated_patch = patches.Polygon(
                    rotated_vertices, closed=True,
                    edgecolor='black' if edges_only else 'none',
                    fill=not edges_only,
                    facecolor=patch.get_facecolor() if not edges_only else 'none',
                    alpha=patch.get_alpha(), linewidth=line_width
                )
                ax.add_patch(rotated_patch)
                accumulated_patches.append(rotated_patch)

    for i in range(1, sides):
        if cancel_callback():
            return
        symmetry_point = calculate_symmetry_point_adjusted(center, radius, sides, current_level)
        angle = 360 / sides * i
        rotation = Affine2D().rotate_deg_around(symmetry_point[0], symmetry_point[1], angle)
        process_patches(n_levels_rays, rotation, new_level_patches)
    n_levels_rays += new_level_patches

    generate_higher_levels(
        vertices, fig, ax, center, radius, sides,
        current_level + 1, max_levels, n_levels_rays,
        edges_only, line_width, cancel_callback
    )
    fig.canvas.draw_idle()


def update_plot(self, alpha: float) -> None:
    self.clear_plot()
    effective_alpha = calculate_effective_alpha(self.sides, self.levels, base_alpha=alpha)
    line_width = calculate_line_width(self.levels)
    base_patches = generate_base_level_polygon(
        vertices=self.vertices, fig=self.fig, ax=self.ax,
        center=self.center, radius=self.radius, sides=self.sides,
        alpha=effective_alpha, draw_base=self.draw_base, levels=self.levels,
        colors_mapped=colors_mapped,
        edges_only=self.edges_only, line_width=line_width
    )
    first_level_patches = [base_patches]
    if self.first_level:
        expanded_first = generate_first_level_polygon(
            fig=self.fig, ax=self.ax, center=self.center,
            sides=self.sides, alpha=effective_alpha, base_level_rays=base_patches,
            edges_only=self.edges_only, line_width=line_width
        )
        first_level_patches.append(expanded_first)
    if self.levels > 1:
        generate_higher_levels(
            vertices=self.vertices, fig=self.fig, ax=self.ax,
            center=self.center, radius=self.radius, sides=self.sides,
            current_level=1, max_levels=self.levels,
            n_levels_rays=first_level_patches,
            edges_only=self.edges_only, line_width=line_width,
            cancel_callback=lambda: self.cancel_generation_flag
        )
    self.fig.canvas.draw()


def calculate_level_alpha(base_alpha: float, level: int, sides: int) -> float:
    if level == 1:
        return base_alpha
    else:
        return base_alpha / (1.2 * (sides ** (level / 2)))


def calculate_effective_alpha(sides: int, levels: int, base_alpha: float = 1.0) -> float:
    """
    Computes the effective alpha after a given number of levels, where level 1 uses
    the base alpha and for each subsequent level the alpha is divided by (1.2 * sides**(level/2)).
    
    This closed-form computation avoids the iterative “feeding” of the previous alpha.
    """
    if levels < 1:
        return base_alpha
    mult_log = - (levels - 1) * math.log(1.2) - (math.log(sides) / 2) * ((levels * (levels + 1)) / 2 - 1)
    effective_alpha = base_alpha * math.exp(mult_log)
    return effective_alpha


def calculate_alpha(sides: int, levels: int) -> float:
    target_alpha = 1.0
    alpha = target_alpha
    for level in range(1, levels + 1):
        alpha = calculate_level_alpha(alpha, level, sides)
    return alpha


def calculate_line_width(levels: int) -> float:
    return max(0.5, 2.0 / (levels + 1))


def estimate_max_overlaps(sides: int, levels: int) -> int:
    overlaps = sides
    for level in range(2, levels + 1):
        overlaps += sides ** level
    return overlaps


class PolygonGUI(tk.Tk):
    def __init__(
        self,
        center: List[float],
        radius: float,
        sides: int,
        levels: int,
        is_rotation_animation_running: bool
    ) -> None:
        super().__init__()
        self.title(vTitle)
        self.geometry("1275x1550")
        self.cancel_generation_flag: bool = False
        self.center: List[float] = center
        self.radius: float = radius
        self.sides: int = sides
        self.levels: int = levels
        self.rotation_speed: float = 5.0
        self.last_frame_time: float = time.time()
        self.alpha: float = 0.444
        self.draw_base: bool = True
        self.first_level: bool = True
        self.rotation_angle: float = 0
        self.vertices: np.ndarray = np.array([])
        self.is_rotation_animation_running: bool = is_rotation_animation_running
        self.rotation_animation: bool = False
        self.edges_only: bool = True
        self.edges_only_enforced: bool = False
        self.animation: Optional[FuncAnimation] = None
        self.emergent_rotation_active: bool = False
        self.zoom_factor: float = 1.0
        self.translation_x: float = 0.0
        self.translation_y: float = 0.0
        self.drag_start_x: int = 0
        self.drag_start_y: int = 0
        self.initial_xlim: Optional[Tuple[float, float]] = None
        self.initial_ylim: Optional[Tuple[float, float]] = None
        self._popup_shown: bool = False
        start_angle = np.pi / (2 * sides) if sides % 2 != 0 else 0
        angles = np.linspace(start_angle, start_angle + 2 * np.pi, sides, endpoint=False)
        self.vertices = np.array([
            np.array(center) + radius * np.array([np.cos(angle), np.sin(angle)]) for angle in angles
        ])
        self.create_widgets()
        self.bind_events()
        self.create_menu_bar()
        self.create_status_bar()
        self.update_plot(self.alpha)
        self.toggle_rotation_animation()
        self.bind("<r>", lambda event: self.reset_view())

    def create_menu_bar(self) -> None:
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Image", command=self.save_image)
        file_menu.add_command(label="Save SVG", command=self.save_as_svg)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Reset View", command=self.reset_view)
        view_menu.add_command(label="Zoom to Design", command=self.zoom_to_design_extent)
        view_menu.add_command(label="Zoom to Boundary", command=self.zoom_to_rotation_boundary)
        menubar.add_cascade(label="View", menu=view_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Instructions", command=self.show_help_instructions)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def create_status_bar(self) -> None:
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status_bar(self) -> None:
        status_text = (
            f"Sides: {self.sides} | "
            f"Levels: {self.levels} | "
            f"Alpha: {self.alpha:.3f} | "
            f"Rotation Speed: {self.rotation_speed:.1f}"
        )
        self.status_var.set(status_text)

    def save_image(self) -> None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                self.fig.savefig(file_path)
                messagebox.showinfo("Image Saved", f"Image successfully saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving image: {e}")

    def save_as_svg(self) -> None:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG File", "*.svg"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                self.fig.savefig(file_path, format="svg")
                messagebox.showinfo("SVG Saved", f"SVG successfully saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving SVG: {e}")

    def reset_view(self) -> None:
        self.zoom_factor = 1.0
        self.translation_x = 0.0
        self.translation_y = 0.0
        self.initial_xlim = None
        self.initial_ylim = None
        self.ax.autoscale()
        self.fig.canvas.draw_idle()

    def cancel_generation(self) -> None:
        self.cancel_generation_flag = True
        logging.info("User requested generation cancellation.")

    def create_widgets(self) -> None:
        larger_font = tkFont.Font(family="Helvetica", size=15)
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X)
        code_frame = tk.LabelFrame(control_frame, text="Plot Code", font=larger_font)
        code_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # == New GUI Frame For Base Level Patterns == #
        pattern_frame = tk.LabelFrame(control_frame, text="Pattern(s)", font=larger_font)
        pattern_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        sides_frame = tk.LabelFrame(control_frame, text="Dimension & Level", font=larger_font)
        sides_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        appearance_frame = tk.LabelFrame(control_frame, text="Appearance", font=larger_font)
        appearance_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        rotation_frame = tk.LabelFrame(control_frame, text="Rotation", font=larger_font)
        rotation_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        view_frame = tk.LabelFrame(control_frame, text="View Controls", font=larger_font)
        view_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # == New GUI Buttons For Base Level Patterns == #
        self.CC_button = tk.Button(pattern_frame, text="CC", font=larger_font, command=lambda: self.toggle_CC)
        self.MSC_button = tk.Button(pattern_frame, text="MSC", font=larger_font, command=lambda: self.toggle_MSC)
        self.MSCC_button = tk.Button(pattern_frame, text="MSCC", font=larger_font, command=lambda: self.toggle_MSCC)
        
        self.zoom_in_button = tk.Button(view_frame, text="Zoom In", font=larger_font, command=lambda: self.zoom(1.1))
        self.zoom_out_button = tk.Button(view_frame, text="Zoom Out", font=larger_font, command=lambda: self.zoom(0.9))
        self.zoom_in_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.zoom_out_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.pan_left_button = tk.Button(view_frame, text="Pan Left", font=larger_font, command=lambda: self.pan('left'))
        self.pan_right_button = tk.Button(view_frame, text="Pan Right", font=larger_font, command=lambda: self.pan('right'))
        self.pan_up_button = tk.Button(view_frame, text="Pan Up", font=larger_font, command=lambda: self.pan('up'))
        self.pan_down_button = tk.Button(view_frame, text="Pan Down", font=larger_font, command=lambda: self.pan('down'))
        self.pan_left_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.pan_right_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.pan_up_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.pan_down_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.reset_view_button = tk.Button(view_frame, text="Reset View", font=larger_font, command=self.reset_view)
        self.reset_view_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.view_portal_button = tk.Button(view_frame, text="View Portal", font=larger_font, command=self.view_portal)
        self.view_portal_button.pack(side=tk.LEFT, padx=5, pady=5)
        if self.levels < 1:
            self.view_portal_button.config(state=tk.DISABLED)
        help_button = tk.Button(view_frame, text="?", font=larger_font, command=self.show_help_instructions, width=2)
        help_button.pack(side=tk.RIGHT, padx=20, pady=5)
        self.alpha_label = tk.Label(appearance_frame, text="Alpha (α):", font=larger_font)
        self.alpha_entry = tk.Entry(appearance_frame, font=larger_font, justify='center')
        self.alpha_entry.insert(0, str(self.alpha))
        apply_alpha_button = tk.Button(appearance_frame, text="Apply α", font=larger_font, command=self.apply_alpha)
        apply_max_alpha_button = tk.Button(appearance_frame, text="Auto α", font=larger_font, command=self.apply_max_safe_alpha)
        self.alpha_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.alpha_entry.pack(side=tk.LEFT, padx=5, pady=5)
        apply_alpha_button.pack(side=tk.LEFT, padx=5, pady=5)
        apply_max_alpha_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.overlayed_alpha_label = tk.Label(appearance_frame, text="Overlayed α:", font=larger_font)
        self.overlayed_alpha_value = tk.Label(appearance_frame, text="", font=larger_font)
        self.overlayed_alpha_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.overlayed_alpha_value.pack(side=tk.LEFT, padx=5, pady=5)
        self.toggle_edges_button = tk.Button(appearance_frame, text="Display Colors", font=larger_font, command=self.toggle_edges)
        self.toggle_edges_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.rotation_mode = tk.StringVar(value="Central Design Axis")
        self.increase_speed_button = tk.Button(rotation_frame, text="Speed +", font=larger_font, command=self.increase_speed)
        self.decrease_speed_button = tk.Button(rotation_frame, text="Speed -", font=larger_font, command=self.decrease_speed)
        self.animate_rotation_button = tk.Button(rotation_frame, text="Start Rotation", font=larger_font, command=self.toggle_rotation_animation)
        self.emergent_rotation_button = tk.Button(rotation_frame, text="Emergent Rotation", font=larger_font, command=self.toggle_emergent_rotation)

        # == New GUI Buttons Packing For Base Level Patterns == #
        self.CC_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.MSC_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.MSCC_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.increase_speed_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.decrease_speed_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.animate_rotation_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.emergent_rotation_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.emergent_rotation_button.config(state=tk.NORMAL)
        self.sides_label = tk.Label(sides_frame, text="Dimension (n):", font=larger_font)
        self.sides_entry = tk.Entry(sides_frame, font=larger_font, justify='center')
        self.sides_entry.insert(0, str(self.sides))
        update_button = tk.Button(sides_frame, text="Update Plot", font=larger_font, command=lambda: self.update_sides(0))
        self.increment_button = tk.Button(sides_frame, text="n +1", font=larger_font, command=lambda: self.update_sides(1))
        self.decrement_button = tk.Button(sides_frame, text="n -1", font=larger_font, command=lambda: self.update_sides(-1))
        self.sides_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.sides_entry.pack(side=tk.LEFT, padx=5, pady=5)
        update_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.increment_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.decrement_button.pack(side=tk.LEFT, padx=5, pady=5)
        level_label = tk.Label(sides_frame, text="Level:", font=larger_font)
        level_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.level_buttons = []
        for i in range(0, 11):
            level_button = tk.Button(sides_frame, text=str(i), font=larger_font, command=lambda i=i: self.set_level(i))
            level_button.pack(side=tk.LEFT, padx=2, pady=2)
            self.level_buttons.append(level_button)
        self.level_buttons[self.levels].config(relief=tk.SUNKEN)
        self.cancel_button = tk.Button(sides_frame, text="Cancel Generation", font=larger_font, command=self.cancel_generation)
        self.cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
        self.code_label = tk.Label(code_frame, text="", font=("Helvetica", 16))
        self.code_label.pack(side=tk.BOTTOM, padx=5, pady=5)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.get_tk_widget().focus_set()

    def on_pattern_toggle(self) -> None:
        # Disable the color toggle button if no pattern is active.
        if not (self.pattern_cc.get() or self.pattern_msc.get() or self.pattern_mscc.get()):
            self.toggle_edges_button.config(state=tk.DISABLED)
        else:
            self.toggle_edges_button.config(state=tk.NORMAL)
        self.update_plot(self.alpha)


    def bind_events(self) -> None:
        widget = self.canvas.get_tk_widget()
        widget.bind("<ButtonPress-1>", self.on_press)
        widget.bind("<B1-Motion>", self.on_drag)
        widget.bind("<ButtonRelease-1>", self.on_release)
        widget.bind("<MouseWheel>", self.on_mouse_wheel)
        widget.bind("<Button-4>", self.on_mouse_wheel)
        widget.bind("<Button-5>", self.on_mouse_wheel)
        widget.bind("<Up>", lambda event: self.pan('up'))
        widget.bind("<Down>", lambda event: self.pan('down'))
        widget.bind("<Left>", lambda event: self.pan('left'))
        widget.bind("<Right>", lambda event: self.pan('right'))

    def show_help_instructions(self) -> None:
        instructions = (
            "Mouse Controls:\n"
            "1. Panning:\n"
            "   - Click and drag with the left mouse button to pan the view.\n"
            "   - Use the arrow keys on the keyboard to pan up, down, left, or right.\n"
            "\n"
            "2. Zooming:\n"
            "   - Use the mouse wheel to zoom in and out (scroll up to zoom in, scroll down to zoom out).\n"
            "   - Use the Zoom In, Zoom Out, and Reset View buttons on the control panel.\n"
            "\n"
            "Keyboard Shortcuts:\n"
            "   - Press 'r' to reset the view."
        )
        messagebox.showinfo("Mouse Panning and Zooming Instructions", instructions)

    def show_about(self) -> None:
        about_text = (
            f"{vTitle}\n\n"
            f"© 02/01/2025 by Primary Design Co. (Alex London)\n\n"
            f"Visit: https://www.primarydesignco.com"
        )
        messagebox.showinfo("About", about_text)

    def apply_max_safe_alpha(self) -> None:
        max_overlaps = estimate_max_overlaps(self.sides, self.levels)
        target_1stlvl_overlayed_alpha = 0.600
        target_2ndlvl_overlayed_alpha = 0.900
        if self.levels == 1:
            optimal_alpha = 1 - (1 - target_1stlvl_overlayed_alpha) ** (1 / max_overlaps)
        else:
            optimal_alpha = 1 - (1 - target_2ndlvl_overlayed_alpha) ** (1 / max_overlaps)
            if optimal_alpha < 0.01:
                optimal_alpha = 0.01
        self.alpha = optimal_alpha
        self.alpha_entry.delete(0, tk.END)
        self.alpha_entry.insert(0, f"{self.alpha:.4f}")
        self.update_plot(self.alpha)

    def apply_alpha(self) -> None:
        new_alpha = get_numeric_entry(self.alpha_entry, 0, 1)
        if new_alpha is not None:
            self.alpha = new_alpha
            self.update_plot(self.alpha)

    def zoom(self, zoom_factor: float) -> None:
        self.zoom_factor *= zoom_factor
        self.apply_zoom_and_translation()
        self.canvas.draw()

    def apply_zoom_and_translation(self) -> None:
        if self.initial_xlim is None or self.initial_ylim is None:
            self.initial_xlim = self.ax.get_xlim()
            self.initial_ylim = self.ax.get_ylim()
        xlim_range = self.initial_xlim[1] - self.initial_xlim[0]
        ylim_range = self.initial_ylim[1] - self.initial_ylim[0]
        x_mid = (self.initial_xlim[0] + self.initial_xlim[1]) / 2
        y_mid = (self.initial_ylim[0] + self.initial_ylim[1]) / 2
        scaled_xlim = [x_mid - xlim_range / (2 * self.zoom_factor),
                       x_mid + xlim_range / (2 * self.zoom_factor)]
        scaled_ylim = [y_mid - ylim_range / (2 * self.zoom_factor),
                       y_mid + ylim_range / (2 * self.zoom_factor)]
        translated_xlim = [scaled_xlim[0] + self.translation_x, scaled_xlim[1] + self.translation_x]
        translated_ylim = [scaled_ylim[0] + self.translation_y, scaled_ylim[1] + self.translation_y]
        self.ax.set_xlim(translated_xlim)
        self.ax.set_ylim(translated_ylim)

    def pan(self, direction: str) -> None:
        pan_step = 0.1 / self.zoom_factor
        if direction == 'left':
            self.translation_x += pan_step
        elif direction == 'right':
            self.translation_x -= pan_step
        elif direction == 'up':
            self.translation_y -= pan_step
        elif direction == 'down':
            self.translation_y += pan_step
        self.apply_zoom_and_translation()
        self.canvas.draw()

    def increase_speed(self) -> None:
        self.rotation_speed = min(10.00, self.rotation_speed + 0.1)
        self.update_status_bar()

    def decrease_speed(self) -> None:
        self.rotation_speed = max(0.1, self.rotation_speed - 0.1)
        self.update_status_bar()

    def toggle_rotation_animation(self) -> None:
        if self.is_rotation_animation_running:
            if self.animation:
                self.animation.event_source.stop()
                self.animation = None
            self.is_rotation_animation_running = False
            self.animate_rotation_button.config(text="Start Rotation")
        else:
            self.is_rotation_animation_running = True
            self.animate_rotation_button.config(text="Stop Rotation")
            self.animate_rotation()
            self.fig.canvas.draw_idle()

    def toggle_emergent_rotation(self) -> None:
        if self.emergent_rotation_active:
            if self.animation:
                self.animation.event_source.stop()
                self.animation = None
            self.emergent_rotation_active = False
            self.emergent_rotation_button.config(text="Emergent Rotation")
        else:
            if self.animation:
                self.animation.event_source.stop()
                self.animation = None
            self.emergent_rotation_active = True
            self.emergent_rotation_button.config(text="Stop Emergent Rotation")
            self.animate_emergent_rotation()

    def get_color_abbreviation(self, color_name: str) -> str:
        color_map = {
            "White": "W", "Black": "Bl", "Red": "R", "Green": "G", "Blue": "B",
            "Yellow": "Y", "Pink": "Pi", "Purple": "P", "Orange": "O", "Cyan": "C",
            "Magenta": "M", "Lime": "Li", "Maroon": "Ma", "Navy": "Na",
            "Olive": "Ol", "Teal": "T", "Violet": "V", "Brown": "Br",
            "Gold": "Go", "Lightcoral": "Lc", "Darkkhaki": "Dk",
            "Darkgreen": "Dg", "Darkblue": "Db", "Darkred": "Dr",
            "Turquoise": "Tu", "Indigo": "In", "Darkorange": "Do",
            "Lightgreen": "Lg", "Tan": "Ta", "Salmon": "Sa",
            "Plum": "Pl", "Orchid": "Or", "Sienna": "Si",
            "Skyblue": "Sk", "Khaki": "K", "Slateblue": "Sb",
            "Goldenrod": "Gr", "Mediumblue": "Mb", "Greenyellow": "Gy",
            "Burlywood": "Bw", "Seagreen": "Sg", "Slategray": "Sg",
            "Cornflowerblue": "Cb", "Mediumorchid": "Mo", "Sandybrown": "Sb",
            "Tomato": "To", "Lightblue": "Lb", "Limegreen": "Lg",
            "Lightgrey": "Lg", "Lightpink": "Lp", "Thistle": "Th",
            "Palegreen": "Pg", "Azure": "Az", "Lavender": "Lv",
            "Honeydew": "Hd", "Mintcream": "Mc", "Aliceblue": "Ab"
        }
        standardized_name = color_name.capitalize()
        abbreviation = color_map.get(standardized_name)
        if abbreviation is None:
            abbreviation = (color_name[:2]).capitalize()
        return abbreviation

    def update_code_label(self) -> None:
        n = self.sides
        radial_level = self.levels
        level_code = f"O{n}CC{'' if radial_level > 0 else '0'}"
        code_string = ""
        color_count = min(n // 2 - 1, len(colors_mapped))
        color_abbr = ""
        if not self.edges_only:
            color_abbr = "".join(self.get_color_abbreviation(color) for color in colors_mapped[:color_count])
        if radial_level > 1:
            code_string = f"{level_code}_{color_abbr}xx{radial_level}" if color_abbr else f"{level_code}xx{radial_level}"
        else:
            code_string = f"{level_code}_{color_abbr}" if color_abbr else f"{level_code}"
        self.code_label.config(text=code_string)

    def rotate_patches(self, angle_increment: float, emergent: bool = False) -> None:
        for patch in self.ax.patches:
            xy = patch.get_xy()
            if emergent:
                patch_center = np.mean(xy, axis=0)
            else:
                patch_center = self.center
            new_xy = np.zeros_like(xy)
            radians = np.radians(angle_increment)
            cos_angle, sin_angle = np.cos(radians), np.sin(radians)
            for i, (x, y) in enumerate(xy):
                translated_x, translated_y = x - patch_center[0], y - patch_center[1]
                rotated_x = cos_angle * translated_x - sin_angle * translated_y
                rotated_y = sin_angle * translated_x + cos_angle * translated_y
                new_xy[i, 0] = rotated_x + patch_center[0]
                new_xy[i, 1] = rotated_y + patch_center[1]
            patch.set_xy(new_xy)

    def store_patch_info(self) -> None:
        """
        Store the original vertex coordinates and local center (centroid) for each patch.
        Call this after the design is fully drawn.
        """
        self.patch_info = []
        for patch in self.ax.patches:
            coords = patch.get_xy()
            center = np.mean(coords, axis=0)
            self.patch_info.append((patch, coords.copy(), center))

    def animate_rotation(self, interval: int = 30) -> None:
        """
        Smoothly rotate all patches about the global center (self.center)
        using a cumulative rotation angle based on the original (stored) patch coordinates.
        """
        if not hasattr(self, 'global_patch_info'):
            self.global_patch_info = []
            for patch in self.ax.patches:
                coords = patch.get_xy()
                self.global_patch_info.append((patch, coords.copy()))
            self.global_angle = 0.0

        def update(frame: int) -> None:
            self.global_angle += self.rotation_speed
            radians = np.radians(self.global_angle)
            cos_angle, sin_angle = np.cos(radians), np.sin(radians)
            for patch, init_coords in self.global_patch_info:
                new_coords = []
                for (x, y) in init_coords:
                    dx, dy = x - self.center[0], y - self.center[1]
                    new_x = cos_angle * dx - sin_angle * dy
                    new_y = sin_angle * dx + cos_angle * dy
                    new_coords.append([new_x + self.center[0], new_y + self.center[1]])
                patch.set_xy(np.array(new_coords))
            self.fig.canvas.draw_idle()

        if self.animation:
            self.animation.event_source.stop()
            self.animation = None

        self.animation = FuncAnimation(
            self.fig, update,
            interval=max(10, int(1000 / self.rotation_speed)),
            cache_frame_data=False
        )

    def animate_emergent_rotation(self, interval: int = 30) -> None:
        if not hasattr(self, 'patch_info'):
            self.store_patch_info()
        if not hasattr(self, 'emergent_angle'):
            self.emergent_angle = 0.0

        def update(frame: int) -> None:
            self.emergent_angle += self.rotation_speed
            radians = np.radians(self.emergent_angle)
            cos_angle, sin_angle = np.cos(radians), np.sin(radians)
            for patch, init_coords, center in self.patch_info:
                new_coords = []
                for (x, y) in init_coords:
                    dx, dy = x - center[0], y - center[1]
                    new_x = cos_angle * dx - sin_angle * dy
                    new_y = sin_angle * dx + cos_angle * dy
                    new_coords.append([new_x + center[0], new_y + center[1]])
                patch.set_xy(np.array(new_coords))
            now = time.time()
            dt = now - self.last_frame_time
            self.fps = 1 / dt if dt > 0 else 0
            self.last_frame_time = now
            self.update_status_bar()

        if self.animation:
            self.animation.event_source.stop()
            self.animation = None

        self.animation = FuncAnimation(
            self.fig, update, interval=max(10, int(1000 / self.rotation_speed)),
            cache_frame_data=False
        )
        self.canvas.draw_idle()

    def toggle_edges(self) -> None:
        self.edges_only = not self.edges_only
        if self.edges_only:
            self.alpha = 0.5
            self.toggle_edges_button.config(text="Display Colors")
        else:
            self.apply_max_safe_alpha()
            self.toggle_edges_button.config(text="Show Edges Only")
        self.update_plot(self.alpha)
        self.update_code_label()

    def calculate_design_extent(self) -> Optional[Tuple[float, float, float, float]]:
        all_x, all_y = [], []
        for patch in self.ax.patches:
            xy = patch.get_xy()
            all_x.extend(xy[:, 0])
            all_y.extend(xy[:, 1])
        if not all_x or not all_y:
            return None
        return (min(all_x), max(all_x), min(all_y), max(all_y))

    def zoom_to_design_extent(self) -> None:
        design_extent = self.calculate_design_extent()
        if design_extent:
            x_min, x_max, y_min, y_max = design_extent
            margin_x = (x_max - x_min) * 0.1
            margin_y = (y_max - y_min) * 0.1
            self.ax.set_xlim(x_min - margin_x, x_max + margin_x)
            self.ax.set_ylim(y_min - margin_y, y_max + margin_y)
            self.fig.canvas.draw_idle()

    def calculate_rotation_boundary_radius(self) -> float:
        all_distances = []
        for patch in self.ax.patches:
            xy = patch.get_xy()
            for x, y in xy:
                distance = np.hypot(x - self.center[0], y - self.center[1])
                all_distances.append(distance)
        return max(all_distances) if all_distances else 0

    def zoom_to_rotation_boundary(self) -> None:
        rotation_radius = self.calculate_rotation_boundary_radius()
        if rotation_radius > 0:
            margin = rotation_radius * 0.2
            x_min = self.center[0] - rotation_radius - margin
            x_max = self.center[0] + rotation_radius + margin
            y_min = self.center[1] - rotation_radius - margin
            y_max = self.center[1] + rotation_radius + margin
            current_aspect_ratio = (
                (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) /
                (self.ax.get_ylim()[1] - self.ax.get_ylim()[0])
            )
            new_aspect_ratio = (x_max - x_min) / (y_max - y_min)
            if new_aspect_ratio > current_aspect_ratio:
                y_center = (y_min + y_max) / 2
                new_height = (x_max - x_min) / current_aspect_ratio
                y_min = y_center - new_height / 2
                y_max = y_center + new_height / 2
            else:
                x_center = (x_min + x_max) / 2
                new_width = (y_max - y_min) * current_aspect_ratio
                x_min = x_center - new_width / 2
                x_max = x_center + new_width / 2
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            self.fig.canvas.draw_idle()

    def clear_plot(self) -> None:
        self.ax.clear()

    def draw_polygons(self, alpha: float) -> List[Any]:
        line_width = calculate_line_width(self.levels)
        base_patches = generate_base_level_polygon(
            vertices=self.vertices, fig=self.fig, ax=self.ax,
            center=self.center, radius=self.radius, sides=self.sides,
            alpha=alpha, draw_base=self.draw_base, levels=self.levels,
            colors_mapped=colors_mapped,
            edges_only=self.edges_only, line_width=line_width
        )
        first_level_patches = [base_patches]
        if self.first_level:
            expanded_first = generate_first_level_polygon(
                fig=self.fig, ax=self.ax, center=self.center,
                sides=self.sides, alpha=alpha, base_level_rays=base_patches,
                edges_only=self.edges_only, line_width=line_width
            )
            first_level_patches.append(expanded_first)
        if self.levels > 1:
            generate_higher_levels(
                vertices=self.vertices, fig=self.fig, ax=self.ax,
                center=self.center, radius=self.radius, sides=self.sides,
                current_level=1, max_levels=self.levels,
                n_levels_rays=first_level_patches,
                edges_only=self.edges_only, line_width=line_width,
                cancel_callback=lambda: self.cancel_generation_flag
            )
        return first_level_patches

    def check_generation_warning(self) -> bool:
        if self.levels < 2:
            return True
        triangle_count = self.sides
        for i in range(2, self.levels + 1):
            triangle_count += self.sides ** i
        time_per_triangle = 0.00065
        estimated_time = triangle_count * time_per_triangle
        threshold = 3.0
        if estimated_time > threshold:
            return messagebox.askokcancel(
                "Warning",
                f"This configuration will generate approximately {triangle_count} triangles and take about {estimated_time:.2f} seconds. Do you wish to proceed?"
            )
        return True

    def update_plot(self, alpha: float) -> None:
        if not self._popup_shown:
            if not self.check_generation_warning():
                return
            self._popup_shown = True
        logging.info(f"Updating plot with alpha: {alpha:.3f}")
        if self.edges_only:
            alpha = 0.444
        if not (0.0 <= alpha <= 1.0):
            alpha = 0.5
        self.clear_plot()
        self.draw_polygons(alpha)
        self.alpha_entry.delete(0, tk.END)
        self.alpha_entry.insert(0, f"{alpha:.3f}")
        max_overlaps = estimate_max_overlaps(self.sides, self.levels)
        cumulative_opacity = 1 - (1 - alpha) ** (max_overlaps ** 0.333)
        if cumulative_opacity >= 0.99999999:
            self.edges_only_enforced = True
            self.edges_only = True
            self.overlayed_alpha_value.config(text="α > 0.999")
            self.toggle_edges_button.config(state=tk.DISABLED)
        else:
            self.edges_only_enforced = False
            self.toggle_edges_button.config(state=tk.NORMAL)
            self.overlayed_alpha_value.config(text=f"{cumulative_opacity:.3f}")
        self.cancel_generation_flag = False
        self.fig.canvas.draw()
        self.update_code_label()
        self.update_status_bar()
        logging.info("Plot update complete.")
        self.store_patch_info()
        self.global_patch_info = []
        for patch in self.ax.patches:
            coords = patch.get_xy()
            self.global_patch_info.append((patch, coords.copy()))
        self.global_angle = 0.0

    def on_press(self, event: Any) -> None:
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.canvas.get_tk_widget().config(cursor="hand2")

    def on_drag(self, event: Any) -> None:
        canvas_widget = self.canvas.get_tk_widget()
        width = canvas_widget.winfo_width()
        height = canvas_widget.winfo_height()
        dx = (event.x - self.drag_start_x) * (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) / width
        dy = (event.y - self.drag_start_y) * (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) / height
        self.translation_x -= dx
        self.translation_y += dy
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.apply_zoom_and_translation()
        self.canvas.draw()

    def on_release(self, event: Any) -> None:
        self.canvas.get_tk_widget().config(cursor="")

    def on_mouse_wheel(self, event: Any) -> None:
        if hasattr(event, 'delta'):
            if event.delta > 0:
                self.zoom(1.1)
            elif event.delta < 0:
                self.zoom(0.9)
        elif hasattr(event, 'num'):
            if event.num == 4:
                self.zoom(1.1)
            elif event.num == 5:
                self.zoom(0.9)

    def update_sides(self, delta: int) -> None:
        try:
            current_sides = int(self.sides_entry.get())
            new_sides = current_sides + delta
            if new_sides > 3:
                self.sides = new_sides
                self.sides_entry.delete(0, tk.END)
                self.sides_entry.insert(0, str(new_sides))
                self.calculate_vertices()
                self._popup_shown = False
                self.update_plot(self.alpha)
                self.apply_max_safe_alpha()
            else:
                messagebox.showerror("Error", "Number of sides must be greater than 3.")
        except ValueError:
            messagebox.showerror("Error", "Invalid number of sides.")

    def calculate_vertices(self) -> None:
        start_angle = np.pi / self.sides if self.sides % 2 != 0 else 0
        angles = np.linspace(start_angle, start_angle + 2 * np.pi, self.sides, endpoint=False)
        self.vertices = np.array([
            np.array(self.center) + self.radius * np.array([np.cos(angle), np.sin(angle)]) for angle in angles
        ])

    def set_level(self, level: int) -> None:
        self.levels = level
        for i, button in enumerate(self.level_buttons):
            button.config(relief=tk.SUNKEN if i == level else tk.RAISED)
        self._popup_shown = False
        if self.levels == 0:
            self.first_level = False
            self.edges_only = False
            self.toggle_edges_button.config(text="Show Edges Only")
            self.alpha = 0.34
            self.animate_rotation_button.config(state=tk.NORMAL)
            self.increase_speed_button.config(state=tk.NORMAL)
            self.decrease_speed_button.config(state=tk.NORMAL)
            self.emergent_rotation_button.config(state=tk.NORMAL)
            if getattr(self, 'emergent_rotation_active', False):
                self.toggle_emergent_rotation()
        elif self.levels == 1:
            self.first_level = True
            self.apply_max_safe_alpha()
            self.animate_rotation_button.config(state=tk.NORMAL)
            self.increase_speed_button.config(state=tk.NORMAL)
            self.decrease_speed_button.config(state=tk.NORMAL)
            self.emergent_rotation_button.config(state=tk.NORMAL)
            if getattr(self, 'emergent_rotation_active', False):
                self.toggle_emergent_rotation()
            self.zoom_to_design_extent()
        else:
            self.first_level = False
            self.apply_max_safe_alpha()
            self.animate_rotation_button.config(state=tk.NORMAL)
            self.increase_speed_button.config(state=tk.NORMAL)
            self.decrease_speed_button.config(state=tk.NORMAL)
            self.emergent_rotation_button.config(state=tk.NORMAL)
            if level == 2:
                self.zoom_to_rotation_boundary()
            if level >= 1:
                self.view_portal_button.config(state=tk.NORMAL)
            else:
                self.view_portal_button.config(state=tk.DISABLED)
        if self.levels < 1:
            self.view_portal_button.config(state=tk.DISABLED)
        self.update_plot(self.alpha)

    def view_portal(self) -> None:
        if self.levels < 1:
            messagebox.showinfo("Information", "View Portal is available only for levels 3 and above.")
            return
        portal_center = calculate_symmetry_point_adjusted(
            list(self.vertices), self.center, self.radius, self.sides, self.levels
        )
        extent = self.radius / self.levels * 1.333
        x_min = portal_center[0] - extent / 2
        x_max = portal_center[0] + extent / 2
        y_min = portal_center[1] - extent / 2
        y_max = portal_center[1] + extent / 2
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.fig.canvas.draw_idle()


if __name__ == "__main__":
    for lvl in range(1, 6):
        origin = calculate_symmetry_point_adjusted((0, 0), 1, 4, lvl)
        print(f"Level {lvl} origin: {origin}")
    app = PolygonGUI(center=[0, 0], radius=1, sides=4, levels=4, is_rotation_animation_running=True)
    app.mainloop()

"""
PDCo Open-Source High-Level Space Field Python Generator
© 02/14/2025 by Primary Design Co. (Alex London)

https://www.primarydesignco.com
"""
