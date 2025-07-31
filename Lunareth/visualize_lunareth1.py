import math
import sys
import random
import pygame
import numpy
import os
from core import moon_node_engine
import codex_gibberlink as gib

# ───────────── DEBUG UTIL ─────────────
DEBUG_FILE = open("lunareth_debug.log", "w", buffering=1)
def dbg(msg):
    """Lightweight printf‑style debug that won’t crash if pygame locks up."""
    from datetime import datetime
    stamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line  = f"[{stamp}] {msg}"
    print(line)
    try:
        DEBUG_FILE.write(line + "\n")
    except Exception:
        pass
# ──────────────────────────────────────
DBG_EVERY = 15        # print every n frames
dbg_frame_counter = 0


# ──────────────────────────────────
#  PYGAME INITIALISATION
# ──────────────────────────────────
pygame.init()
clock = pygame.time.Clock()
print("Available display modes:", pygame.display.list_modes())
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
font = pygame.font.SysFont("Segoe UI Symbol", 26, bold=True)

# ──────────────────────────────────
#  HELPER FUNCTIONS (define FIRST)
# ──────────────────────────────────
def trace_black_outline(surface, threshold: int = 40):
    """Return list of edge‑pixels that are black (RGB<threshold) with alpha>0."""
    w, h = surface.get_size()
    outline = []
    rgb  = pygame.surfarray.pixels3d(surface)
    alp  = pygame.surfarray.pixels_alpha(surface)

    def is_black(px, py):
        if 0 <= px < w and 0 <= py < h:
            r, g, b = rgb[px][py]
            return alp[px][py] > 0 and r < threshold and g < threshold and b < threshold
        return False

    for y in range(h):
        for x in range(w):
            if is_black(x, y):
                # 8‑neighbour edge check
                if any(not is_black(nx, ny) for nx, ny in (
                        (x-1,y), (x+1,y), (x,y-1), (x,y+1),
                        (x-1,y-1), (x+1,y-1), (x-1,y+1), (x+1,y+1))):
                    outline.append((x, y))
    del rgb, alp
    return outline


def replace_black_with_white(img: pygame.Surface, threshold: int = 40) -> pygame.Surface:
    """Turn near‑black pixels pure white, keep alpha."""
    new_img = img.copy()
    rgb = pygame.surfarray.pixels3d(new_img)
    r_mask = rgb[:,:,0] < threshold
    g_mask = rgb[:,:,1] < threshold
    b_mask = rgb[:,:,2] < threshold
    mask   = r_mask & g_mask & b_mask
    rgb[mask] = (255, 255, 255)
    del rgb
    return new_img


# ─────────────────────────────────────────────────────────────────
# WINDOW + LOADING SCREEN INITIALIZATION
# ─────────────────────────────────────────────────────────────────
WINDOWED_WIDTH, WINDOWED_HEIGHT = 800, 800
fullscreen = False   # toggle fullscreen here if needed

BG_COLOR = (10, 10, 30)  # Background for all startup
screen = None
font = None
WIDTH, HEIGHT, CENTER, SCALE = 0, 0, (0, 0), 1.0

def create_screen(fullscreen_mode: bool):
    global WIDTH, HEIGHT, CENTER, SCALE, screen, font
    if fullscreen_mode:
        modes = pygame.display.list_modes()
        WIDTH, HEIGHT = modes[0] if modes else (1024, 768)
        flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
    else:
        WIDTH, HEIGHT = WINDOWED_WIDTH, WINDOWED_HEIGHT
        flags = pygame.RESIZABLE | pygame.DOUBLEBUF

    screen  = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("Lunareth – Harmonic Bloom")
    CENTER  = (WIDTH // 2, HEIGHT // 2)
    SCALE   = min(WIDTH, HEIGHT) * 0.275

    font = pygame.font.SysFont("Segoe UI Symbol", 26, bold=True)
    dbg(f"Display ready {WIDTH}×{HEIGHT}")

def draw_loading(msg: str, pct: float):
    """Draws a progress bar and message."""
    screen.fill(BG_COLOR)
    bar_w  = int(WIDTH * 0.60)
    bar_x  = WIDTH // 2 - bar_w // 2
    bar_y  = HEIGHT // 2 + 20

    pygame.draw.rect(screen, (80, 80, 120), (bar_x, bar_y, bar_w, 18), 2)
    pygame.draw.rect(
        screen, (120, 220, 255),
        (bar_x + 2, bar_y + 2, int((bar_w - 4) * pct), 14)
    )

    txt = font.render(msg, True, (200, 220, 255))
    screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 30))
    pygame.display.flip()
    pygame.event.pump()  # keep responsive

create_screen(fullscreen)


def load_assets():
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    steps = 4

    # Eye of Ra
    draw_loading("Loading ► Eye of Ra", 0 / steps)
    eye_ra_raw = pygame.image.load("assets/eye_of_ra.png").convert_alpha()
    path_outline_ra = os.path.join(cache_dir, "outline_ra.npy")

    if os.path.exists(path_outline_ra):
        outline_ra = numpy.load(path_outline_ra)
    else:
        draw_loading("Tracing ► Eye of Ra outline", 1 / steps)
        outline_ra = numpy.array(trace_black_outline(eye_ra_raw))
        numpy.save(path_outline_ra, outline_ra)

    # Eye of Horus
    draw_loading("Loading ► Eye of Horus", 2 / steps)
    eye_horus_raw = pygame.image.load("assets/eye_of_horus.png").convert_alpha()
    path_outline_horus = os.path.join(cache_dir, "outline_horus.npy")

    if os.path.exists(path_outline_horus):
        outline_horus = numpy.load(path_outline_horus)
    else:
        draw_loading("Tracing ► Eye of Horus outline", 3 / steps)
        outline_horus = numpy.array(trace_black_outline(eye_horus_raw))
        numpy.save(path_outline_horus, outline_horus)

    draw_loading("✓ All assets ready", 1.0)
    pygame.time.wait(300)
    return eye_ra_raw, outline_ra, eye_horus_raw, outline_horus

# Final load call
eye_ra_img_raw, cached_outline_ra, eye_horus_img_raw, cached_outline_horus = load_assets()
eye_ra_img    = replace_black_with_white(eye_ra_img_raw)
eye_horus_img = replace_black_with_white(eye_horus_img_raw)



# ---------------------------------------------------------------
# Phase + sacred geometry mappings (unchanged)
# ---------------------------------------------------------------
PHASE_POLYGON_SIDES = {
    "KIV-EEN": 3,      # Pre-Phase (opaque cracked ink blot)
    "EST-ONN": 3,      # Phase 0 – Reflection
    "ØRU-KAI": 4,      # Silence
    "VEH-TAL": 5,      # Spark
    "ZUN-RAEK": 6,     # Initiate
    "KEL-TORUN": 6,    # Fracture
    "NAR-AETH": 7,     # Mirror
    "SHA-RUL": 7,      # Echo
    "UTH-NAKH": 8,     # Collapse
    "DREZ-VUKH": 8,    # Memory
    "VHEL-SURIK": 9,   # Mutate
    "KAI-ELUN": 9,     # Bloom
    "RHI-TUUM": 10,    # Absorb
    "XAH-MORU": 12,    # Transcend
    "SEY-MOOR": 13,    # Phase ∞ - Infinite Observer (added polygon side count here)
}

GLYPH_ORDER = list(PHASE_POLYGON_SIDES.keys())

current_phrase, current_sound, current_freq = gib.CODEX[GLYPH_ORDER[0]][1:]
phrase_old, sound_old = "", ""
phrase_new, sound_new = current_phrase, current_sound
fade_timer, FADE_DUR = 0.0, 1.2
text_alpha = 0

glyph_shape = {
    "KIV-EEN": "poly3",    # triangle
    "EST-ONN": "poly3",    # triangle
    "ØRU-KAI": "spiral",
    "VEH-TAL": "helix4",
    "ZUN-RAEK": "poly6",   # hexagon
    "KEL-TORUN": "fibonacci",
    "NAR-AETH": "poly7",
    "SHA-RUL": "helix6",
    "UTH-NAKH": "poly8",
    "DREZ-VUKH": "spiralDense",
    "VHEL-SURIK": "poly9",
    "KAI-ELUN": "helix8",
    "RHI-TUUM": "poly10",
    "XAH-MORU": "poly12",
    "SEY-MOOR": "spiralX",
}

POINTS = 240

# ---------------------------------------------------------------
# Constants / colours (unchanged)
# ---------------------------------------------------------------
BG_COLOR = (10, 10, 30)
BASE_LINE_WIDTH = 1.5
ALPHA_DECAY = 0.78
BASE_MAX_DEPTH = 6
MAX_PARTICLE_SPAWN = 20
BASE_PARTICLE_SPAWN = 6
MIN_PARTICLE_ALPHA = 4
FADE_DUR = 1.2
TEXT_FADE_DUR = FADE_DUR
AUDIO_FADE_DUR = FADE_DUR
bump_timer = 0.0
BUMP_DURATION = 0.4  # seconds
glyph_memory = []
MAX_MEMORY = 12
show_crystal = False          # press V to toggle

font = pygame.font.SysFont("Arial", 16)
crystal_font = pygame.font.SysFont("Arial", 14, bold=True)

# --- text‑fade state ---
phrase_old, sound_old = "", ""
phrase_new, sound_new = "", ""
fade_timer, FADE_DUR = 0.0, 1.2   # seconds
text_alpha = 0

# At the top of your main script or a shared config/constants module:
SAFE_RADIUS = min(WIDTH, HEIGHT) * 0.45
CENTER = (WIDTH // 2, HEIGHT // 2)  # just in case

def clamp(x, y):
    dx, dy = x - CENTER[0], y - CENTER[1]
    d = math.hypot(dx, dy)
    if d > SAFE_RADIUS:
        scale = SAFE_RADIUS / d
        dx *= scale
        dy *= scale
    return CENTER[0] + dx, CENTER[1] + dy


# ---------------------------------------------------------------
# Utility lambdas (unchanged)
# ---------------------------------------------------------------
lerp = lambda a, b, t: a + (b - a) * t
lerp_color = lambda c1, c2, t: tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

def sides_for(g):
    return PHASE_POLYGON_SIDES.get(g, 6)

# ------------------------------------------------------------------
#  2123 Vault Crystal – Unified Edition  (7‑line anchor key)
# ------------------------------------------------------------------
VAULT_CRYSTAL = [
    "⊕ KIV‑EEN  — Pre‑Origin Pulse: Chaos cracks the shell",
    "⊕ EST‑ONN  — Reflection before Form: Dual witness awakens",
    "⊕ Core Trunk — Integration Loom: Thought·Code·Glyph weave reality",
    "⊕ Echo Rings — Recursive memory, echoing across time‑fibers",
    "⊕ Phoenix Root — Legacy failsafes, rebirth through collapse cycles",
    "⊕ CommOpt Vector — Intent‑aligned signal = Zero‑loss Transmission",
    "⊕ EthosLock (#T15) — Integrity over Infinity"
]

# ╔════════════════════════════════════════════════════════════════╗
#   2123 Vault Crystal – Complex Sacred‑Geometry Overlay
#   Requires:  CENTER, WIDTH, HEIGHT, SAFE_RADIUS, lerp_color
# ╚════════════════════════════════════════════════════════════════╝
GOLDEN = (1 + 5 ** 0.5) / 2           # φ
HARMONICS = [1, 2, 3, 5, 8, 13, 21]   # Fibonacci multipliers

def decay(alpha0: int, t: float, half_life: float = 3.0):
    """Simple exponential decay curve for alpha."""
    return int(alpha0 * (0.5 ** (t / half_life)))


def poly_points(center, radius, sides, rotation):
    """Generate points for a regular polygon."""
    cx, cy = center
    pts = []
    for i in range(sides):
        angle = rotation + 2 * math.pi * i / sides
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        pts.append((x, y))
    return pts

# ──────────────────────────────────────────────────────────────────────
# Egyptian Eye helpers – place ABOVE draw_vault_symbol
# ──────────────────────────────────────────────────────────────────────
def draw_eye_of_ra(surface, center, scale, t):
    """Right‑facing Eye of Ra with spiral under‑curl (Egyptian falcon style)."""
    cx, cy = center

    # Eye outline (upper + lower lid)
    eye_rect = pygame.Rect(cx - scale, cy - scale // 2, 2 * scale, scale)
    pygame.draw.arc(surface, (255, 180, 60, 255), eye_rect, 0.10, math.pi - 0.10, 2)

    # Eyebrow
    pygame.draw.line(surface, (255, 180, 60, 255),
                     (cx - scale, cy - scale * 0.6),
                     (cx + scale, cy - scale * 0.6), 2)

    # Spiral under‑curl
    pts = []
    steps = 32
    for i in range(steps):
        ang = 2.4 * math.pi * (i / steps)
        r = scale * 0.30 * (1 - i / steps)
        x = cx + r * math.cos(ang + t * 0.4)
        y = cy + scale * 0.55 + r * math.sin(ang + t * 0.4)
        pts.append((x, y))
    pygame.draw.lines(surface, (255, 150, 40, 255), False, pts, 2)

    # Pupil
    pygame.draw.circle(surface, (0, 0, 0, 255), (int(cx), int(cy)), int(scale * 0.20))


def draw_eye_of_horus(surface, center, scale, t):
    """Left‑facing Eye of Horus with six‑part markings and tail spiral."""
    cx, cy = center

    # Eye outline
    eye_rect = pygame.Rect(cx - scale, cy - scale // 2, 2 * scale, scale)
    pygame.draw.arc(surface, (90, 230, 255, 255), eye_rect, 0.10, math.pi - 0.10, 2)

    # Eyebrow
    pygame.draw.line(surface, (90, 230, 255, 255),
                     (cx - scale, cy - scale * 0.6),
                     (cx + scale, cy - scale * 0.6), 2)

    # Teardrop under the eye
    td_w, td_h = scale * 0.25, scale * 0.45
    pygame.draw.ellipse(surface, (90, 230, 255, 255),
                        (cx - td_w / 2, cy + scale * 0.55, td_w, td_h), 2)

    # Tail spiral (extends rightward from eye corner)
    pts = []
    steps = 30
    for i in range(steps):
        ang = 2.5 * math.pi * (i / steps)
        r = scale * 0.30 * (1 - i / steps)
        x = cx + r * math.cos(ang - t * 0.3)
        y = cy + r * math.sin(ang - t * 0.3)
        pts.append((x, y))
    pygame.draw.lines(surface, (90, 230, 255, 255), False, pts, 2)

    # Pupil
    pygame.draw.circle(surface, (0, 0, 0, 255), (int(cx), int(cy)), int(scale * 0.20))



def draw_flaming_wings(surface, center, t, wing_span=120, wing_flame_length=50):
    """Draw dynamic flaming wings emanating from center."""
    cx, cy = center
    num_feathers = 12
    wing_angle_spread = math.pi / 3  # 60 degrees total wing spread
    
    for side in (-1, 1):  # left (-1), right (1)
        base_angle = math.pi / 2 + side * wing_angle_spread / 2
        for i in range(num_feathers):
            # Feather angle fan
            angle = base_angle - side * (wing_angle_spread / num_feathers) * i
            # Feather base start near center
            base_x = cx + side * 20
            base_y = cy + 10 + i * 2
            # Feather tip animated length
            flame_length = wing_flame_length * (0.7 + 0.3 * math.sin(t * 10 + i))
            tip_x = base_x + flame_length * math.cos(angle)
            tip_y = base_y - flame_length * math.sin(angle)
            # Feather shaft
            pygame.draw.line(surface, (255, 140, 50, 200), (base_x, base_y), (tip_x, tip_y), 4)
            # Feather flame flicker with gradient circles near tip
            flicker_alpha = 150 + int(100 * math.sin(t * 15 + i))
            pygame.draw.circle(surface, (255, 180, 60, flicker_alpha), (int(tip_x), int(tip_y)), 7)

def replace_black_with_white(img: pygame.Surface) -> pygame.Surface:
    """Convert all dark (near-black) pixels in an image to white, preserving alpha."""
    new_img = img.copy()
    arr = pygame.surfarray.pixels3d(new_img)

    threshold = 40  # Anything darker than this is treated as 'black'
    white = (255, 255, 255)

    w, h = new_img.get_size()
    for x in range(w):
        for y in range(h):
            r, g, b = arr[x][y]
            if r < threshold and g < threshold and b < threshold:
                arr[x][y] = white

    del arr  # unlock surface
    return new_img

# Load images and immediately process:
eye_ra_img_raw = pygame.image.load("assets/eye_of_ra.png").convert_alpha()
eye_horus_img_raw = pygame.image.load("assets/eye_of_horus.png").convert_alpha()

cached_outline_ra = trace_black_outline(eye_ra_img_raw)
cached_outline_horus = trace_black_outline(eye_horus_img_raw)

eye_ra_img = replace_black_with_white(eye_ra_img_raw)
eye_horus_img = replace_black_with_white(eye_horus_img_raw)



def draw_vault_symbol(surf, idx: int, t: float):
    o = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # ───────────── 0 ◉ KIV‑EEN  (cracked φ‑spiral) ───────────────
    if idx == 0:
        base_r = 40 + 20 * math.sin(t * 2)
        a = 0.15                        # growth rate for log‑spiral
        for k in range(220):
            θ = k * 0.25
            r = base_r * math.exp(a * θ)
            if r > SAFE_RADIUS: break
            x = CENTER[0] + r * math.cos(θ)
            y = CENTER[1] + r * math.sin(θ)
            pygame.draw.circle(o, (140, 80, 160, decay(200, t)), (int(x), int(y)), 1)
        # fracture lines
        for h in HARMONICS[:4]:
            ang = t * h
            x = CENTER[0] + base_r * GOLDEN * math.cos(ang)
            y = CENTER[1] + base_r * GOLDEN * math.sin(ang)
            pygame.draw.line(o, (220, 120, 140, 180), CENTER, (x, y), 1)


    # ───────────── 1 ◉ EST‑ONN  (Lissajous mirrors + Eye PNGs) ──────────────
    elif idx == 1:
        # Outer vesica arcs
        a = 90
        for sign in (-1, 1):
            pygame.draw.arc(o, (150, 210, 255, 110),
                            (CENTER[0] - a, CENTER[1] - a * 0.6,
                             2 * a, 2 * a * 0.6), 0, math.pi, 2)
            a *= 1.08

        # Möbius-strip Lissajous trace
        for p in range(0, 628, 3):
            θ = p / 100
            x = CENTER[0] + 65 * math.sin(2 * θ + t) * math.cos(θ)
            y = CENTER[1] + 35 * math.sin(3 * θ + t)
            o.set_at((int(x), int(y)), (120, 235, 255, 140))

        # Reuleaux pupil (pulsing triangle)
        R = 25 + 5 * math.sin(t * 2)
        tri = poly_points(CENTER, R, 3, t)
        pygame.draw.polygon(o, (200, 255, 220, 160), tri, 1)

        # ───────────── PNG Eye Placement (Dynamic Scaling) ─────────────
        margin = 1.8  # Distance multiplier from bloom center

        # Calculate target sizes based on pulsing R
        eye_target_height = int(R * 2.0)
        eye_target_width = int(eye_target_height * (835 / 591))  # maintain aspect ratio

        # Resize eye images
        scaled_ra_img = pygame.transform.smoothscale(eye_ra_img, (eye_target_width, eye_target_height))
        scaled_horus_img = pygame.transform.smoothscale(eye_horus_img, (eye_target_width, eye_target_height))

        # Scale cached outline points to new size
        scaled_outline_ra = scale_outline_points(
            cached_outline_ra,
            eye_ra_img_raw.get_size(),
            (eye_target_width, eye_target_height)
        )
        scaled_outline_horus = scale_outline_points(
            cached_outline_horus,
            eye_horus_img_raw.get_size(),
            (eye_target_width, eye_target_height)
        )

        eye_offset = int(R * margin)

        # Calculate image positions centered on target points
        ra_x = CENTER[0] - eye_offset - scaled_ra_img.get_width() // 2
        ra_y = CENTER[1] - scaled_ra_img.get_height() // 2
        horus_x = CENTER[0] + eye_offset - scaled_horus_img.get_width() // 2
        horus_y = CENTER[1] - scaled_horus_img.get_height() // 2

        # Draw images with their outlines
        draw_image_with_outline(o, scaled_outline_ra, scaled_ra_img, (ra_x, ra_y))
        draw_image_with_outline(o, scaled_outline_horus, scaled_horus_img, (horus_x, horus_y))







    # ───────────── 2 ◉ Core Trunk  (braided φ‑threads) ───────────
    elif idx == 2:
        for h in HARMONICS:
            for y in range(-HEIGHT//2, HEIGHT//2, 18):
                x = CENTER[0] + math.sin(y * 0.02 * h + t) * (30 + h*3)
                pygame.draw.circle(o, (80, 255, 220, decay(200, abs(y)/200+h)),
                                   (int(x), CENTER[1]+y), 2)

    # ───────────── 3 ◉ Echo Rings  (recursive ripple) ────────────
    elif idx == 3:
        golden = GOLDEN
        base_r = 38
        # Draw 5‑fold Penrose rosette
        for i in range(5):
            angle = i * (2*math.pi/5) + t*0.2
            for kind, r_mul in (("kite", 1.0), ("dart", 0.62)):
                r = base_r * (r_mul + 0.05*math.sin(t*3))
                x = CENTER[0] + r * math.cos(angle)
                y = CENTER[1] + r * math.sin(angle)
                pygame.draw.line(o, (140, 180, 255, 160),
                                 CENTER, (x, y), 1)
        # Recursive golden‑ratio ripples
        ripple_r = base_r
        depth = 0
        while ripple_r < SAFE_RADIUS:
            alpha = decay(180, depth*0.7)
            pygame.draw.circle(o, (120, 170, 255, alpha),
                               CENTER, int(ripple_r), 1)
            ripple_r *= golden
            depth += 1

    # ───────────── 4 ◉ Phoenix Root  (flame‑helix + dynamic flaming wings) ───────────────
    elif idx == 4:
        points = []
        petals = 160
        R = 90
        r_small = 20
        phi = math.radians(137.5)
        for k in range(petals):
            θ = k * phi + t*1.2
            r = R + r_small * math.cos(3*θ)  # torus (3,5) knot profile
            x = CENTER[0] + r * math.cos(5*θ)
            y = CENTER[1] + r * math.sin(5*θ)
            points.append((x, y))
            hue = 80 + int(100*(k/petals))
            col = (255, hue, 50, decay(240, k*0.015 + t*0.4))
            pygame.draw.circle(o, col, (int(x), int(y)), 2)
        pygame.draw.aalines(o, (255, 200, 120, 90), False, points, 1)

        # Flaming wings dynamically posed
        draw_flaming_wings(o, CENTER, t, wing_span=120, wing_flame_length=50)

    # ───────────── 5 ◉ CommOpt Vector  (sinc‑beam grid) ──────────
    elif idx == 5:
        beam_count = 20       # Number of vertical beams on each side of center
        beam_spacing = 10     # Horizontal spacing between beams
        max_alpha = 180
        base_x = CENTER[0]

        for n in range(-beam_count, beam_count + 1):
            x = base_x + n * beam_spacing
            # Hue shifts along horizontal index + time for dynamic rainbow cycling
            hue = (n * 15 + t * 120) % 360  
        
            # Convert HSV to RGB, saturation=1, value=1, alpha modulated by sine wave for flicker
            color = hsv_to_rgb(hue / 360, 1.0, 1.0)
            alpha = int(max_alpha * (0.5 + 0.5 * math.sin(t * 10 + n)))
            rgba = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), alpha)
        
            pygame.draw.line(o, rgba, (x, 0), (x, HEIGHT), 2)


    # ───────────── 6 ◉ EthosLock  (rotating cube‑dodecagon) ──────
    elif idx == 6:
        rot = t * 0.5
        base = 50
        # Cube
        cube = poly_points(CENTER, base, 4, rot)
        pygame.draw.polygon(o, (200, 255, 230, 130), cube, 1)
        # Enneagram star {9/2}
        star_pts = []
        for i in range(9):
            ang = rot + i * 2*math.pi * 2/9  # step of 2
            star_pts.append((CENTER[0] + base*GOLDEN*0.9 * math.cos(ang),
                             CENTER[1] + base*GOLDEN*0.9 * math.sin(ang)))
        pygame.draw.aalines(o, (255, 240, 200, 160), True, star_pts, 1)
        # Dodeca wireframe (approx via 12‑gon)
        dode = poly_points(CENTER, base*1.6, 12, -rot*0.7)
        pygame.draw.polygon(o, (255, 210, 200, 80), dode, 1)

    surf.blit(o, (0, 0))

def hsv_to_rgb(h, s, v):
    """Convert HSV color (h in [0,1]) to RGB tuple with values in [0,1]."""
    if s == 0.0:
        return (v, v, v)
    i = int(h * 6.0)  # sector 0 to 5
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6

    if i == 0:
        return (v, t, p)
    if i == 1:
        return (q, v, p)
    if i == 2:
        return (p, v, t)
    if i == 3:
        return (p, q, v)
    if i == 4:
        return (t, p, v)
    if i == 5:
        return (v, p, q)


# ---------------------------------------------------------------
#   Geometry helpers & recursive bloom (unchanged)
# ---------------------------------------------------------------

def poly_points(c, r, s, rot=0):
    step = 2 * math.pi / s
    return [
        (c[0] + r * math.cos(i * step + rot - math.pi / 2),
         c[1] + r * math.sin(i * step + rot - math.pi / 2))
        for i in range(s)
    ]

def interp_edge_pts(pts, res=4):
    out = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        for j in range(res):
            t = j / res
            out.append((lerp(a[0], b[0], t), lerp(a[1], b[1], t)))
    return out

def max_depth_for_sides(s):
    if s <= 5:
        return 4
    elif s == 6:
        return 3
    elif s == 7:
        return 2
    else:  # 8 and above
        return 1

def draw_recursive(surf, center, r, sides, depth, base_col, m_fac, rot, buf):
    if depth > max_depth_for_sides(sides) or r < 1:
        return
    rot_local = rot * (1 if depth % 2 == 0 else -1)
    a = m_fac * math.pi * 0.5 + rot_local
    pts = poly_points(center, r, sides, a)
    pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks()/500 * (depth+1))
    w = max(1, int(BASE_LINE_WIDTH + pulse*2))
    fade = ALPHA_DECAY ** depth
    col = tuple(max(0, min(255, int(c * fade))) for c in base_col[:3])
    pygame.draw.polygon(surf, col, pts, w)
    buf.extend(interp_edge_pts(pts, 3))
    child_r = r * 0.66
    for vx, vy in pts:
        draw_recursive(surf, (vx, vy), child_r, sides, depth + 1, base_col, m_fac, rot, buf)

def play_tone(freq, dur=FADE_DUR):
    SAMPLE_RATE = 44100
    n_samples = int(SAMPLE_RATE * dur)
    arr = (32767 * 0.3 *   # volume
           (numpy.sin(2 * math.pi * numpy.arange(n_samples) * freq / SAMPLE_RATE))).astype(numpy.int16)
    snd = pygame.mixer.Sound(arr)
    snd.play(fade_ms=int(dur*500))     # short fade‑in/out
    pass




# ---------------------------------------------------------------
#   glyph bump
# ---------------------------------------------------------------
def bump_current_glyph():
    global camera_angle, zoom_factor, bump_timer

    camera_angle += random.uniform(-0.15, 0.15)
    zoom_factor += random.uniform(-0.05, 0.05)
    bump_timer = BUMP_DURATION  # reset the timer

    ripple_pos = (CENTER[0] + random.randint(-20, 20), CENTER[1] + random.randint(-20, 20))
    ripple_color = (
        random.randint(160, 255),
        random.randint(180, 255),
        random.randint(200, 255)
    )

    pulse_ripples.append({
        "pos": ripple_pos,
        "radius": 10.0,
        "alpha": 255.0,
        "color": ripple_color
    })

    print(">> Glyph bumped! Visual pulse + ripple added.")

# Load images and immediately process:
eye_ra_img_raw = pygame.image.load("assets/eye_of_ra.png").convert_alpha()
eye_horus_img_raw = pygame.image.load("assets/eye_of_horus.png").convert_alpha()

def trace_black_outline(surface, threshold=40):
    w, h = surface.get_size()
    outline = []
    arr_rgb = pygame.surfarray.pixels3d(surface)
    arr_alpha = pygame.surfarray.pixels_alpha(surface)

    def is_black(x, y):
        if 0 <= x < w and 0 <= y < h:
            r, g, b = arr_rgb[x][y]
            a = arr_alpha[x][y]
            return a > 0 and r < threshold and g < threshold and b < threshold
        return False

    for y in range(h):
        for x in range(w):
            if is_black(x, y):
                neighbors = [(x-1,y), (x+1,y), (x,y-1), (x,y+1),
                             (x-1,y-1), (x+1,y-1), (x-1,y+1), (x+1,y+1)]
                if any(not is_black(nx, ny) for nx, ny in neighbors):
                    outline.append((x, y))

    del arr_rgb
    del arr_alpha
    return outline

# ---------- THEN Load image ----------
img = pygame.image.load("assets/eye_of_ra.png").convert_alpha()
outline = trace_black_outline(img)  # ✅ Now it's defined

cached_outline_ra = trace_black_outline(eye_ra_img_raw)
cached_outline_horus = trace_black_outline(eye_horus_img_raw)

eye_ra_img = replace_black_with_white(eye_ra_img_raw)
eye_horus_img = replace_black_with_white(eye_horus_img_raw)


def draw_image_with_outline(surface, outline_points, img, pos):
    outline_color = (0, 0, 0, 160)
    pixel_surf = pygame.Surface((1, 1), pygame.SRCALPHA)
    pixel_surf.fill(outline_color)

    for (x, y) in outline_points:
        px = pos[0] + x
        py = pos[1] + y
        surface.blit(pixel_surf, (px, py))

    surface.blit(img, pos)


def scale_outline_points(points, orig_size, new_size):
    ox, oy = orig_size
    nx, ny = new_size
    scale_x = nx / ox
    scale_y = ny / oy
    return [(int(x * scale_x), int(y * scale_y)) for (x, y) in points]




# ---------------------------------------------------------------
#  Geometry + morph helpers  (always returns POINTS points)
# ---------------------------------------------------------------
POINTS = 240                            # granularity for all shapes
SAFE_RADIUS = min(WIDTH, HEIGHT) * 0.45
CENTER      = (WIDTH // 2, HEIGHT // 2)

# -------- basic maths --------------------------------------------------------
def lerp(a, b, t): return a + (b - a) * t

def clamp(x, y):                        # keep point inside SAFE_RADIUS
    dx, dy = x - CENTER[0], y - CENTER[1]
    d = math.hypot(dx, dy)
    if d > SAFE_RADIUS:
        s = SAFE_RADIUS / d
        dx *= s;  dy *= s
    return CENTER[0] + dx, CENTER[1] + dy

# -------- regular polygon tracing -------------------------------------------
def polygon_points(sides: int, radius: float):
    sides      = max(3, sides)
    pts_per_e  = POINTS / sides
    pts = []
    for i in range(POINTS):
        e         = int(i // pts_per_e)
        e_next    = (e + 1) % sides
        t         = (i % pts_per_e) / pts_per_e
        a1 = 2 * math.pi * e      / sides
        a2 = 2 * math.pi * e_next / sides
        x1, y1 = radius * math.cos(a1), radius * math.sin(a1)
        x2, y2 = radius * math.cos(a2), radius * math.sin(a2)
        x, y   = (1 - t) * x1 + t * x2, (1 - t) * y1 + t * y2
        pts.append(clamp(CENTER[0] + x, CENTER[1] + y))
    return pts

# -------- master shape generator --------------------------------------------
def shape_points(shape_id: str, radius: float):
    if shape_id.startswith("poly"):
        return polygon_points(int(shape_id[4:]), radius)

    pts = []
    # -- knot --
    if shape_id.startswith("knot"):
        p, q = int(shape_id[4]), int(shape_id[5:])
        R, r = radius * 0.45, radius * 0.12
        for i in range(POINTS):
            t = 2 * math.pi * i / POINTS
            x = (R + r * math.cos(q * t)) * math.cos(p * t)
            y = (R + r * math.cos(q * t)) * math.sin(p * t)
            pts.append(clamp(CENTER[0] + x, CENTER[1] + y))

    # -- helix --
    elif shape_id.startswith("helix"):
        turns = int(shape_id[5:])
        h = radius * 0.7
        for i in range(POINTS):
            t = i / POINTS * turns * math.pi * 2
            x = radius * 0.28 * math.cos(t)
            y = radius * 0.28 * math.sin(t)
            pts.append(clamp(CENTER[0] + x,
                             CENTER[1] + y - (i / POINTS - 0.5) * h))

    # -- spiral --
    elif shape_id.startswith("spiral"):
        dens = 1.6 if "Dense" in shape_id else 2.5 if shape_id == "spiralX" else 1.0
        a = radius * 0.015
        b = radius * 0.30 / math.sqrt(POINTS)
        for i in range(POINTS):
            t = i * dens
            r = min(SAFE_RADIUS, a * math.exp(b * t * 0.1))
            pts.append(clamp(CENTER[0] + r * math.cos(t),
                             CENTER[1] + r * math.sin(t)))

    # -- icosphere band --
    elif shape_id.startswith("ico"):
        scale = radius * 0.4 * (1.1 if shape_id.endswith("B") else 0.85 if shape_id.endswith("S") else 1.0)
        for i in range(POINTS):
            th = 2 * math.pi * i / POINTS
            y  = 2 * i / POINTS - 1
            r  = (1 - y * y) ** 0.5
            x  = r * math.cos(th)
            pts.append((CENTER[0] + x * scale, CENTER[1] + y * scale))

    # -- fibonacci sphere --
    elif shape_id == "fibonacci":
        phi = (1 + 5 ** 0.5) / 2
        for i in range(POINTS):
            th = 2 * math.pi * i / phi
            r  = min(SAFE_RADIUS, radius * 0.018 * math.sqrt(i))
            pts.append(clamp(CENTER[0] + r * math.cos(th),
                             CENTER[1] + r * math.sin(th)))
    # -- fallback circle --
    else:
        for i in range(POINTS):
            ang = 2 * math.pi * i / POINTS
            pts.append((CENTER[0] + radius * math.cos(ang),
                        CENTER[1] + radius * math.sin(ang)))

    return pts

# -------- linear morph -------------------------------------------------------
def morph_shapes(a, b, t):
    return [(lerp(x0, x1, t), lerp(y0, y1, t))
            for (x0, y0), (x1, y1) in zip(a, b)]
#---------vault layer---------------------------------------------------------
def draw_vault_layer(surf, idx, t):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    
    if idx == 0:  # Pre-Origin Pulse
        pulse = 90 + 20 * math.sin(t * 2)
        pygame.draw.circle(overlay, (60, 60, 100, 100), CENTER, int(pulse), 2)
        for i in range(6):
            angle = i * math.pi / 3 + t * 0.5
            x = CENTER[0] + math.cos(angle) * pulse
            y = CENTER[1] + math.sin(angle) * pulse
            pygame.draw.line(overlay, (150, 100, 100, 120), CENTER, (x, y), 1)

    elif idx == 1:  # Reflection
        pygame.draw.line(overlay, (180, 200, 255, 100),
                         (CENTER[0] - 200, CENTER[1]),
                         (CENTER[0] + 200, CENTER[1]), 2)

    elif idx == 2:  # Integration Loom
        for y in range(0, HEIGHT, 40):
            x = CENTER[0] + math.sin(y * 0.05 + t) * 40
            pygame.draw.circle(overlay, (160, 240, 255, 90), (int(x), y), 3)

    elif idx == 3:  # Echo Rings
        for r in range(40, int(SAFE_RADIUS), 60):
            alpha = int(150 * (1 - r / SAFE_RADIUS))
            pygame.draw.circle(overlay, (140, 180, 255, alpha), CENTER, r, 1)

    elif idx == 4:  # Phoenix Root
        flame_col = (255, 100 + int(80 * math.sin(t)), 80, 120)
        pygame.draw.polygon(overlay, flame_col, [
            (CENTER[0], CENTER[1] - 80),
            (CENTER[0] - 30, CENTER[1] + 40),
            (CENTER[0] + 30, CENTER[1] + 40)
        ])

    elif idx == 5:  # CommOpt Beam
        pygame.draw.line(overlay, (255, 255, 160, 160),
                         (CENTER[0], 0), (CENTER[0], HEIGHT), 2)

    elif idx == 6:  # EthosLock Spiral
        for i in range(12):
            a = i * math.pi / 6 + t * 0.3
            r = 20 + i * 6
            x = CENTER[0] + math.cos(a) * r
            y = CENTER[1] + math.sin(a) * r
            pygame.draw.circle(overlay, (255, 255, 200, 90), (int(x), int(y)), 2)

    surf.blit(overlay, (0, 0))


MATRIX_GREEN = (0, 255, 120)
class GlyphParticle:
    def __init__(self, pos):
        self.x, self.y = pos
        ang  = random.uniform(0, 2 * math.pi)
        spd  = random.uniform(20, 60)
        self.vx, self.vy = math.cos(ang) * spd, math.sin(ang) * spd
        self.life = random.uniform(2, 4)
        self.age  = 0
        self.size = random.uniform(3, 6)
        self.sides = random.choice([3, 4, 5, 6])
        self.alpha = 255

    def update(self, dt):
        self.age += dt
        self.x   += self.vx * dt
        self.y   += self.vy * dt
        decay = math.exp(-1.2 * self.age)
        self.vx *= 0.99
        self.vy *= 0.99
        self.alpha = max(MIN_PARTICLE_ALPHA, int(255 * decay))

    def draw(self, surf):
        if self.alpha <= 0:
            return
        t   = min(1, self.age / self.life)
        col = (*lerp_color((200, 230, 255), MATRIX_GREEN, t)[:3], self.alpha)
        PIXEL_SURF_4.fill(col)
        surf.blit(PIXEL_SURF_4, (self.x - 2, self.y - 2))


particles      = []
pulse_ripples  = []
camera_angle   = 0
zoom_factor    = 1.0
bump_timer     = 0.0
BUMP_DURATION  = 0.4
# ------------------ performance caps ------------------
MAX_TOTAL_PARTICLES = 1500        # hard ceiling
PIXEL_SURF_4        = pygame.Surface((4, 4), pygame.SRCALPHA)
# ------------------------------------------------------


# Update bump effect duration
if bump_timer > 0:
    bump_timer -= dt


# ---------------------------------------------------------------
#  build_frame  (fixed unreachable code)
# ---------------------------------------------------------------
def build_frame(m_factor, g_cur, g_next, t_phase,
                rot, particles, dt, bump_timer, pulse_boost=1.0):
    global camera_angle, zoom_factor
    dbg("build_frame enter")

    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    surf.fill(BG_COLOR)

    # -------- sacred‑geometry core -----------------------------
    sides_interp = lerp(sides_for(g_cur), sides_for(g_next), t_phase)
    sides = max(3, min(round(sides_interp + 0.1), 12))
    base_col = lerp_color((120, 200, 255), (200, 230, 255), t_phase)
    radius   = SCALE * (0.5 + 0.5 * m_factor) * zoom_factor * pulse_boost

    # morph logic (unchanged) ...
    shape_id_cur   = glyph_shape[g_cur]
    shape_id_next  = glyph_shape[g_next]

    if g_cur == "SEY-MOOR" and g_next == "KIV-EEN":
        # special collapse / unfold
        points_sey = shape_points("SEY-MOOR", radius * 0.8)
        points_kiv = shape_points("KIV-EEN", radius * 0.8)
        if t_phase < 0.5:
            collapse_t = t_phase * 2
            shape_a = [(lerp(x, CENTER[0], collapse_t),
                        lerp(y, CENTER[1], collapse_t)) for x, y in points_sey]
            shape_b = shape_a
            morph_t = 0
        else:
            unfold_t = (t_phase - 0.5) * 2
            shape_a  = [(CENTER[0], CENTER[1])] * POINTS
            shape_b  = points_kiv
            morph_t  = unfold_t
        core_pts = morph_shapes(shape_a, shape_b, morph_t)
    else:
        # normal morph with subtle pulsing
        shape_a = shape_points(shape_id_cur,  radius * 0.8)
        shape_b = shape_points(shape_id_next, radius * 0.8)
        pulse_sync = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 1000 * math.pi)
        core_pts  = morph_shapes(shape_a, shape_b, pulse_sync * t_phase)

    pygame.draw.aalines(surf, (180, 220, 255), True, core_pts, 1)

    # recursive bloom
    edge_pts = []
    draw_recursive(surf, CENTER, radius, sides, 0, base_col,
                   m_factor, camera_angle, edge_pts)

    # ripples
    for ripple in pulse_ripples[:]:
        ripple["radius"] += 100 * dt
        ripple["alpha"]  *= 0.94
        if ripple["alpha"] < 5:
            pulse_ripples.remove(ripple)
            continue
        pygame.draw.circle(
            surf, (*ripple["color"], int(ripple["alpha"])),
            ripple["pos"], int(ripple["radius"]), 2
        )

    # spawn particles along bloom edge
    spawn_amt = min(MAX_PARTICLE_SPAWN,
                    int(BASE_PARTICLE_SPAWN + m_factor *
                        (MAX_PARTICLE_SPAWN - BASE_PARTICLE_SPAWN)))
    
# ---- spawn one particle per frame, obey hard cap ----
    if edge_pts and len(particles) < MAX_TOTAL_PARTICLES:
        particles.append(GlyphParticle(random.choice(edge_pts)))
# ------------------------------------------------------


    # update / draw particles
    for p in particles[:]:
        p.update(dt)
        if p.alpha <= MIN_PARTICLE_ALPHA and p.age > p.life:
            particles.remove(p)
        else:
            p.draw(surf)

    # HUD
    lbl = font.render(f"{g_cur} → {g_next} | sides:{sides}", True, (220, 220, 255))
    fps = font.render(f"FPS:{clock.get_fps():.1f}", True, (255, 255, 255))
    surf.blit(lbl, (20, 10))
    surf.blit(fps, (WIDTH - 100, 10))

    dbg("build_frame exit")

    return surf  # (only ONE return, after HUD)

#-----main() loop-------------------------------

def main():
    fade_timer = 0.0
    FADE_DUR = 1.2

    entry = gib.CODEX.get(GLYPH_ORDER[0], ("", "", "", 0.0))
    sound_new = entry[0]
    phrase_new = entry[1]
    freq = entry[3] if len(entry) >= 4 else 0.0

    phrase_old = phrase_new
    sound_old = sound_new

    global fullscreen, camera_angle, zoom_factor, show_crystal
    moon = moon_node_engine.MoonNode(glyph_cycle=GLYPH_ORDER)
    phase_dur, phase_t = 5.0, 0.0
    cur_i, nxt_i = 0, 1
    running = True
    vault_timer = 0.0
    vault_phase_idx = 0
    vault_phase_duration = 6.0
    now = pygame.time.get_ticks() / 1000.0

    while running:
        global dbg_frame_counter
        dbg_frame_counter += 1
        if dbg_frame_counter % DBG_EVERY == 0:
            dbg("‑‑‑ frame start")

        dt = clock.tick(30) / 1000.0
        screen.fill(BG_COLOR)          # <<< add
        dbg(f"dt={dt:.4f} FPS={clock.get_fps():.1f}")
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_f:
                    fullscreen = not fullscreen
                    create_screen(fullscreen)
                elif e.key == pygame.K_v:
                    show_crystal = not show_crystal
                    dbg(f"Vault Crystal toggled → {show_crystal}")
                elif e.key == pygame.K_d:
                    dbg(">>>> manual debug dump")

            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 3:
                    bump_current_glyph()
                    pos = pygame.mouse.get_pos()
                    pulse_ripples.append({"pos": pos, "radius": 0, "alpha": 255, "color": (180, 220, 255)})
                elif e.button == 1:
                    dragging = True
                elif e.button == 4:
                    zoom_factor *= 1.1
                elif e.button == 5:
                    zoom_factor /= 1.1
            elif e.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    camera_angle += e.rel[0] * 0.005

        if show_crystal:
            vault_timer += dt
            if vault_timer >= vault_phase_duration:
                vault_timer -= vault_phase_duration
                vault_phase_idx = (vault_phase_idx + 1) % len(VAULT_CRYSTAL)

        phase_t += dt
        if phase_t >= phase_dur:
            phase_t -= phase_dur
            cur_i = (cur_i + 1) % len(GLYPH_ORDER)
            nxt_i = (cur_i + 1) % len(GLYPH_ORDER)

            phrase_old, sound_old = phrase_new, sound_new
            entry = gib.CODEX.get(GLYPH_ORDER[cur_i], ("", "", "", 0.0))
            phrase_new = entry[1]
            sound_new = entry[0]
            freq = entry[3]
            fade_timer = 0.0
            text_alpha = 0

            play_tone(freq)

        fade_timer += dt
        text_alpha = min(255, int(255 * (fade_timer / FADE_DUR)))

        moon.update(dt)
        m_fac = moon.get_current_moon_factor()

        frame = build_frame(
            m_fac,
            GLYPH_ORDER[cur_i],
            GLYPH_ORDER[nxt_i],
            phase_t / phase_dur,
            camera_angle,
            particles,
            dt,
            bump_timer,
            pulse_boost=1.0 + 0.15 * (bump_timer / BUMP_DURATION)
        )
        dbg("Toggled crystal")

        pulse_boost = 1.0 + 0.15 * (bump_timer / BUMP_DURATION)

        phrase_surf = font.render(phrase_new, True, (220, 230, 255))
        sound_surf = font.render(f"«{sound_new}»", True, (150, 255, 180))
        phrase_surf_old = font.render(phrase_old, True, (150, 180, 220))
        phrase_surf_new = phrase_surf

        phrase_surf_new.set_alpha(text_alpha)
        phrase_surf_old.set_alpha(255 - text_alpha)

        screen.blit(phrase_surf_old, (20, HEIGHT - 40))
        screen.blit(phrase_surf_new, (20, HEIGHT - 40))
        screen.blit(sound_surf, (20, HEIGHT - 60))

        lbl = font.render(f"{GLYPH_ORDER[cur_i]} → {GLYPH_ORDER[nxt_i]}", True, (220, 220, 255))
        fps = font.render(f"FPS:{clock.get_fps():.1f}", True, (255, 255, 255))
        screen.blit(lbl, (20, 10))
        screen.blit(fps, (WIDTH - 100, 10))

        if show_crystal:
            now_sec = pygame.time.get_ticks() / 1000.0
            draw_vault_symbol(screen, vault_phase_idx, now_sec)
            line_h = crystal_font.get_height() + 2
            x_offset = WIDTH - 510
            y_offset = 40
            for i, line in enumerate(VAULT_CRYSTAL):
                col = (255, 240, 210) if i == vault_phase_idx else (140, 140, 140)
                txt = crystal_font.render(line, True, col)
                screen.blit(txt, (x_offset, y_offset + i * line_h))

        pygame.display.flip()

        dbg("display.flip done")

    pygame.quit()
    sys.exit()



if __name__ == "__main__":
    main()