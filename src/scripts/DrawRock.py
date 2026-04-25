import pygame
import math
import random
from pygaminal.screen import Screen
from pygaminal.app import App


class DrawRock:
    def __init__(self, color="#646464", radius=12, shadow=True,
                 num_vertices=12, roughness=0.4,
                 rotation_scale=0.02, tilt_sensitivity=0.003,
                 shading_offset=3, highlight_scale=0.75):
        self.color = pygame.Color(color)
        self.radius = radius
        self.shadow = shadow
        self.num_vertices = num_vertices
        self.roughness = roughness
        self.rotation_scale = rotation_scale
        self.tilt_sensitivity = tilt_sensitivity
        self.shading_offset = shading_offset
        self.highlight_scale = highlight_scale

        # Pre-compute stable random offsets so shape is consistent across frames
        random.seed(42)
        self._radial_offsets = [random.uniform(-1, 1) for _ in range(num_vertices)]

        # Build the base polygon vertices (centered at origin)
        self._base_vertices = self._generate_shape()

        # Accumulated visual rotation angle (radians)
        self._rotation_angle = 0.0

        # Pre-compute derived colors for shading
        self._dark_color = pygame.Color(
            max(0, self.color.r - 50),
            max(0, self.color.g - 50),
            max(0, self.color.b - 50)
        )
        self._light_color = pygame.Color(
            min(255, self.color.r + 60),
            min(255, self.color.g + 60),
            min(255, self.color.b + 60)
        )

    def _generate_shape(self):
        """Build base polygon vertices centered at (0, 0)."""
        verts = []
        for i in range(self.num_vertices):
            angle = (2 * math.pi * i) / self.num_vertices
            pert = self._radial_offsets[i] * self.roughness * self.radius
            r = max(1, self.radius + pert)
            verts.append((r * math.cos(angle), r * math.sin(angle)))
        return verts

    def _transform_vertices(self, rot_angle, y_tilt):
        """Apply 2D rotation and Y squash/stretch to base vertices."""
        ca = math.cos(rot_angle)
        sa = math.sin(rot_angle)
        result = []
        for vx, vy in self._base_vertices:
            rx = vx * ca - vy * sa
            ry = vx * sa + vy * ca
            ry *= y_tilt
            result.append((rx, ry))
        return result

    def _get_cam(self, obj):
        cam_comps = obj.get_components("scripts/Camera")
        return cam_comps[0] if cam_comps else None

    def update(self, obj):
        mov_comps = obj.get_components("scripts/Fake3DMovement")
        if mov_comps:
            mov = mov_comps[0]
            if mov.moving:
                dt = App().dt
                ang_vel = mov.dir_x * mov.h_speed * self.rotation_scale
                self._rotation_angle += ang_vel * dt
                self._rotation_angle %= 2 * math.pi

    def draw(self, obj):
        surface = Screen().surface
        cam = self._get_cam(obj)

        sx, sy = cam.world_to_screen(obj.x, obj.y) if cam else (obj.x, obj.y)
        sx = int(sx)
        sy = int(sy)

        # Read movement state
        z = 0
        y_tilt = 1.0
        mov_comps = obj.get_components("scripts/Fake3DMovement")
        if mov_comps:
            mov = mov_comps[0]
            z = mov.z
            y_tilt = 1.0 + (mov.dir_y * mov.h_speed) * self.tilt_sensitivity
            y_tilt = max(0.6, min(1.4, y_tilt))

        # --- Ground shadow ---
        if self.shadow:
            size_scale = max(0.3, 1 - (z / 100))
            sw = max(2, int(self.radius * size_scale))
            sh = max(1, int(self.radius * 0.4 * size_scale))
            shadow_alpha = max(20, int(50 * size_scale))
            shadow_surf = pygame.Surface((sw * 2, sh * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha), shadow_surf.get_rect())
            surface.blit(shadow_surf, (sx - sw, sy - sh))

        # --- Transformed polygon vertices ---
        bottom_y = sy - z  # rock sits on this y
        verts = self._transform_vertices(self._rotation_angle, y_tilt)
        poly_pts = [(int(sx + vx), int(bottom_y + vy)) for vx, vy in verts]

        # --- Dark base (offset down-right) ---
        do = self.shading_offset
        dark_pts = [(int(sx + vx + do), int(bottom_y + vy + do)) for vx, vy in verts]
        pygame.draw.polygon(surface, self._dark_color, dark_pts)

        # --- Main color ---
        pygame.draw.polygon(surface, self.color, poly_pts)

        # --- Light highlight (offset up-left, scaled down) ---
        lo = self.shading_offset + 2
        hl_pts = [
            (int(sx + vx * self.highlight_scale - lo),
             int(bottom_y + vy * self.highlight_scale - lo))
            for vx, vy in verts
        ]
        pygame.draw.polygon(surface, self._light_color, hl_pts)
