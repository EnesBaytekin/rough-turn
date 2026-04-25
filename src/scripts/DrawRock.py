import pygame
import math
import random
from pygaminal.screen import Screen
from pygaminal.app import App


class DrawRock:
    def __init__(self, color="#646464", radius=12, shadow=True,
                 num_vertices=12, roughness=0.4,
                 rotation_scale=0.02, tilt_sensitivity=0.003,
                 num_layers=14, layer_spread=7):
        self.color = pygame.Color(color)
        self.radius = radius
        self.shadow = shadow
        self.num_vertices = num_vertices
        self.roughness = roughness
        self.rotation_scale = rotation_scale
        self.tilt_sensitivity = tilt_sensitivity
        self.num_layers = num_layers
        self.layer_spread = layer_spread

        # Pre-compute stable random offsets so shape is consistent across frames
        random.seed(42)
        self._radial_offsets = [random.uniform(-1, 1) for _ in range(num_vertices)]

        # Build the base polygon vertices (centered at origin)
        self._base_vertices = self._generate_shape()

        # Accumulated visual rotation angle (radians)
        self._rotation_angle = 0.0

        # Pre-compute derived colors
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

        # Pre-compute per-layer triangle colors from base (unrotated) geometry
        # so each triangle keeps its color no matter how the rock rotates.
        self._triangle_colors = self._compute_triangle_colors()

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

    def _compute_triangle_colors(self):
        """Assign a fixed color to each triangle of each layer (unrotated)."""
        light_angle = math.atan2(-1, -1)
        lx = math.cos(light_angle)
        ly = math.sin(light_angle)
        nv = len(self._base_vertices)

        light_rgb = (self._light_color.r, self._light_color.g, self._light_color.b)
        main_rgb = (self.color.r, self.color.g, self.color.b)
        dark_rgb = (self._dark_color.r, self._dark_color.g, self._dark_color.b)

        all_colors = []
        for i in range(self.num_layers):
            t = i / (self.num_layers - 1)
            t_center = abs(t - 0.5) * 2
            center_thresh = 1.0 - t * 2.0
            gap = 0.8 * (1 - t_center)
            dark_thresh = center_thresh - gap
            light_thresh = center_thresh + gap

            layer_colors = []
            for vi in range(nv):
                vj = (vi + 1) % nv
                v1x, v1y = self._base_vertices[vi]
                v2x, v2y = self._base_vertices[vj]
                mx = v1x + v2x
                my = v1y + v2y
                ml = math.sqrt(mx * mx + my * my)
                if ml > 0:
                    dot = (mx / ml) * lx + (my / ml) * ly
                else:
                    dot = 0

                if dot > light_thresh:
                    col = light_rgb
                elif dot < dark_thresh:
                    col = dark_rgb
                else:
                    col = main_rgb
                layer_colors.append(col)
            all_colors.append(layer_colors)
        return all_colors

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

        # --- Sprite-stacked layers with fixed per-triangle colors ---
        bottom_y = sy - z
        verts = self._transform_vertices(self._rotation_angle, y_tilt)
        nv = len(verts)

        for i in range(self.num_layers):
            t = i / (self.num_layers - 1)  # 0 (bottom) → 1 (top)

            # Width scale: spherical volume
            t_center = abs(t - 0.5) * 2
            wscale = 1.0 - t_center * 0.55

            # Diagonal offset per layer
            off = int(self.layer_spread * (1 - t * 2))
            cx = sx + off
            cy = bottom_y + off

            layer_colors = self._triangle_colors[i]

            # Triangle fan from center
            for vi in range(nv):
                vj = (vi + 1) % nv
                v1x, v1y = verts[vi]
                v2x, v2y = verts[vj]

                tri = [
                    (int(cx), int(cy)),
                    (int(cx + v1x * wscale), int(cy + v1y * wscale)),
                    (int(cx + v2x * wscale), int(cy + v2y * wscale)),
                ]
                pygame.draw.polygon(surface, layer_colors[vi], tri)
