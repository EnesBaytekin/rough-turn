"""
Town map — coastal walls & structures.
Diagonal coastline at -45° through (500, 800).
Land is top-left, sea is bottom-right.
Rock starts at (280, 650).

Wall: (x, y, width, thickness, angle_deg, color_hex, height)
"""

# Walls: (x, y, width, thickness, angle_deg, color_hex, height)
WALLS = [
    # === PATH LOW WALLS === (parallel to coast)
    (320, 600, 120, 3, -45, "#7A7A6A", 8),
    (310, 588, 120, 3, -45, "#7A7A6A", 8),

    # === CROSS PATH WALL === (perpendicular to coast)
    (280, 570, 50, 3, 45, "#7A7A6A", 8),

    # === BIG BLOCKS === (thick walls at various angles for bouncing)
    (350, 480, 50, 12, 15, "#5A5A5A", 40),
    (300, 420, 60, 10, -30, "#6A5A4A", 45),
    (420, 550, 40, 10, 70, "#5A5A6A", 35),

    # === SCATTERED WALLS ===
    (180, 380, 30, 8, -15, "#6A5A5A", 30),
    (400, 430, 35, 6, 60, "#5A6A5A", 25),
]

# Sprites: (image_path, x, y, wall_width, wall_thickness, wall_angle, wall_height, ground_from_top)
# Invisible wall matching the sprite's position/shape for collision.
SPRITES = [
    ("bucket.png", 0, 650, 80, 50, 0, 80, 155),
]
