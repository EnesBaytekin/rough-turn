"""
Town map — BIG WORLD.
Diagonal coastline bottom-left to top-right at -45°.
Rock is a tiny pebble; everything is huge around it.
Camera follows the rock so things can be off-screen.

Wall: (x, y, width, thickness, angle_deg, color_hex, height)
Decor: (type, x, y, params_dict)
"""

WALL_COLOR = "#B8956A"

# === COASTLINE ===
# Massive wall along the diagonal coastline
COAST_WALL = [
    (500, 800, 2500, 20, -45, "#C4956A", 16),
]

# === PROMENADE ROAD (200 units wide — a real boulevard) ===
PROMENADE_WALLS = [
    (400, 700, 1400, 20, -45, WALL_COLOR, 22),     # sea side
    (240, 580, 1400, 20, -45, WALL_COLOR, 100),     # land side (massive wall)
    (-100, 850, 200, 20, 45, WALL_COLOR, 100),      # SW end
    (750, 430, 200, 20, 45, WALL_COLOR, 100),       # NE end
]

# === PARK (gigantic open area) ===
PARK_WALLS = [
    (-100, 620, 200, 20, 45, WALL_COLOR, 80),
    (650, 420, 200, 20, 45, WALL_COLOR, 80),
    (300, 520, 700, 20, -45, WALL_COLOR, 80),
    # Angled inner walls for bounces
    (200, 640, 150, 16, 25, WALL_COLOR, 50),
    (450, 540, 160, 16, -55, WALL_COLOR, 55),
    (120, 540, 120, 16, -35, WALL_COLOR, 45),
    (380, 420, 140, 16, 15, WALL_COLOR, 50),
]

# === BUILDING BLOCKS (massive structures) ===
BUILDING_WALLS = [
    (-150, 500, 300, 200, -45, "#8A7A6A", 120),
    (200, 380, 350, 220, -45, "#7A6A5A", 130),
    (650, 300, 350, 200, -45, "#8A7A6A", 120),
    (430, 180, 450, 180, -45, "#7A6A5A", 140),
]

# === WORLD BOUNDARY ===
BOUNDARY_WALLS = [
    (-350, 450, 600, 24, -45, "#665544", 140),
    (-200, 950, 280, 24, 45, "#665544", 140),
    (950, 350, 280, 24, 45, "#665544", 140),
]

WALLS = (
    COAST_WALL
    + PROMENADE_WALLS
    + PARK_WALLS
    + BUILDING_WALLS
    + BOUNDARY_WALLS
)

# === TERRAIN ZONES ===
# Strips parallel to the coastline, going landward.
# coast_anchor (wx, wy), coast_angle (deg), dist_start, dist_end, terrain_type
# dist is perpendicular distance from coast (positive = landward / top-left)
BEACH_ZONE   = ((500, 800, -45), 0, 55, "sand")
ROAD_ZONE    = ((500, 800, -45), 55, 220, "pavement")
GRASS_ZONE   = ((500, 800, -45), 220, 600, "grass")

TERRAIN_ZONES = [BEACH_ZONE, ROAD_ZONE, GRASS_ZONE]

# === DECORATIONS ===

# Lampposts along promenade (spaced far apart)
LAMPPOSTS = [
    ("lamppost", 100, 780, {}),
    ("lamppost", 280, 710, {}),
    ("lamppost", 460, 640, {}),
    ("lamppost", 640, 570, {}),
]

# Huge trees
TREES = [
    ("tree", 100, 600, {"color": (70, 120, 55), "height": 80}),
    ("tree", 320, 640, {"color": (85, 135, 50), "height": 90}),
    ("tree", 500, 590, {"color": (75, 125, 55), "height": 85}),
    ("tree", 200, 520, {"color": (80, 130, 60), "height": 88}),
    ("tree", 560, 520, {"color": (70, 120, 55), "height": 80}),
    ("tree", 400, 470, {"color": (85, 135, 50), "height": 75}),
]

# Big statue
STATUES = [
    ("statue", 360, 580, {}),
]

# Benches
BENCHES = [
    ("bench", 60, 740, {}),
    ("bench", 440, 660, {}),
    ("bench", 640, 550, {}),
    ("bench", 260, 490, {}),
]

DECORATIONS = LAMPPOSTS + TREES + STATUES + BENCHES

# Hitbox sizes (massive)
DECOR_WALL_SIZES = {
    "lamppost": (12, 12, 0),
    "tree": (50, 28, 0),
    "statue": (30, 30, 0),
    "bench": (44, 16, 0),
}

DECOR_WALL_COLORS = {
    "lamppost": "#3A3A3A",
    "tree": "#5A4A3A",
    "statue": "#8A8A8A",
    "bench": "#7A5A3A",
}

DECOR_WALL_HEIGHTS = {
    "lamppost": 60,
    "tree": 50,
    "statue": 70,
    "bench": 30,
}
