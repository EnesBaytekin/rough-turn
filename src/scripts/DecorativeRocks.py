import pygame
from pygaminal.screen import Screen
from pygaminal.app import App
import math
import random


# Registry — set by MapLoader, read by Fake3DMovement on deposit
source_area = None
dest_area = None

# Arrow data — set by DecorativeRocks.draw(), drawn by DrawOverlay (depth 9999)
arrow_visible = False
arrow_tip = None
arrow_left = None
arrow_right = None


class DecorativeRocks:
    def __init__(self, positions, roughness=0.6, radius=12, color_hex="#646464",
                 deposit_center=None):
        self.positions = list(positions)
        self.roughness = roughness
        self.radius = radius
        self.color = pygame.Color(color_hex)
        self.deposit_center = deposit_center  # (world_x, world_y) or None
        # List of (surface, half_size) — one per position, each with a random rotation
        self._rock_caches = []
        self._rebuild_caches()

    # ----- rendering helpers (no self, so they can be reused by add_rock) -----

    @staticmethod
    def _gen_base_verts(roughness, radius, seed=73):
        """Generate base (unrotated) rock vertices."""
        effective_r = min(1.0, roughness / 0.7)
        random.seed(seed)
        nv = 24
        verts = []
        for i in range(nv):
            a = (2 * math.pi * i) / nv
            off = random.uniform(-1, 1) * effective_r * radius * 0.4
            r = max(1, radius + off)
            verts.append((r * math.cos(a), r * math.sin(a)))
        return verts, effective_r

    @staticmethod
    def _render_rock_surf(verts, effective_r, color, radius):
        """Render one rock surface from a set of vertices (already rotated)."""
        pad = 16
        size = int(radius * 2 + pad)
        half = size // 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)

        dark = pygame.Color(
            max(0, color.r - 30), max(0, color.g - 30), max(0, color.b - 30))
        light = pygame.Color(
            min(255, color.r + 35), min(255, color.g + 35), min(255, color.b + 35))

        nv = len(verts)
        num_layers = 14
        lx, ly = -0.707, -0.707

        for i in range(num_layers):
            t = i / (num_layers - 1)
            t_center = abs(t - 0.5) * 2
            wscale = 1.0 - t_center * 0.55
            off = int(7 * (1 - t * 2) * effective_r)
            lcx = half + off
            lcy = half + off

            for vi in range(nv):
                vj = (vi + 1) % nv
                v1x, v1y = verts[vi]
                v2x, v2y = verts[vj]

                mx, my = v1x + v2x, v1y + v2y
                ml = math.sqrt(mx * mx + my * my)
                dot = (mx / ml * lx + my / ml * ly) if ml > 0 else 0

                gap = 0.8 * (1 - t_center) * (0.5 + 0.5 * effective_r)
                ct = 1.0 - t * 2.0

                if dot > ct + gap:
                    col = light
                elif dot < ct - gap:
                    col = dark
                else:
                    col = color

                tri = [
                    (int(lcx), int(lcy)),
                    (int(lcx + v1x * wscale), int(lcy + v1y * wscale)),
                    (int(lcx + v2x * wscale), int(lcy + v2y * wscale)),
                ]
                pygame.draw.polygon(surf, col, tri)

        return surf, half

    def _rebuild_caches(self):
        """Pre-render each rock with a unique random rotation."""
        base_verts, effective_r = self._gen_base_verts(
            self.roughness, self.radius)
        rng = random.Random(456)
        self._rock_caches = []
        for _ in range(len(self.positions)):
            angle = rng.uniform(0, 2 * math.pi)
            ca, sa = math.cos(angle), math.sin(angle)
            rotated = [(vx * ca - vy * sa, vx * sa + vy * ca)
                       for vx, vy in base_verts]
            surf, half = self._render_rock_surf(
                rotated, effective_r, self.color, self.radius)
            self._rock_caches.append((surf, half))

    def add_rock(self, world_x, world_y):
        """Add a new rock at the given world position (called on deposit)."""
        base_verts, effective_r = self._gen_base_verts(
            self.roughness, self.radius)
        angle = random.uniform(0, 2 * math.pi)
        ca, sa = math.cos(angle), math.sin(angle)
        rotated = [(vx * ca - vy * sa, vx * sa + vy * ca)
                   for vx, vy in base_verts]
        surf, half = self._render_rock_surf(
            rotated, effective_r, self.color, self.radius)
        self.positions.append((world_x, world_y))
        self._rock_caches.append((surf, half))

    def draw(self, obj):
        scene = App().get_current_scene()
        if not scene:
            return
        rock_objs = scene.get_objects_by_tag("rock")
        if not rock_objs:
            return
        cam_comps = rock_objs[0].get_components("scripts/Camera")
        if not cam_comps:
            return
        cam = cam_comps[0]

        surface = Screen().surface
        for (wx, wy), (surf, half) in zip(self.positions, self._rock_caches):
            sx, sy = cam.world_to_screen(wx, wy)
            sx = int(sx - half)
            sy = int(sy - half)
            surface.blit(surf, (sx, sy))

        # --- Deposit indicator (dest area only, visible only when bar is full) ---
        import scripts.DecorativeRocks as dr_mod
        dr_mod.arrow_visible = False  # reset each frame

        if self.deposit_center is None:
            return
        import scripts.DrawRock as drawrock
        roughness = getattr(drawrock, 'slider_roughness', 1.0)
        if roughness is not None and roughness > 0.001:
            return
        progress = getattr(drawrock, 'deposit_progress', 0.0)

        dx, dy = self.deposit_center
        sx, sy = cam.world_to_screen(dx, dy)
        w, h = Screen().width, Screen().height

        # On-screen check (with padding for the circle)
        on_screen = (-20 < sx < w + 20 and -20 < sy < h + 20)

        if on_screen:
            cx, cy = int(sx), int(sy)
            radius = 40

            # Faint guide circle
            guide_rect = pygame.Rect(cx - radius, cy - radius,
                                     radius * 2, radius * 2)
            pygame.draw.arc(surface, (255, 255, 255, 50),
                            guide_rect, 0, 2 * math.pi, width=1)

            # Progress arc (fills during countdown)
            if progress > 0:
                end_angle = 2 * math.pi * progress
                alpha = int(120 + progress * 135)
                progress_rect = pygame.Rect(cx - radius - 2, cy - radius - 2,
                                            radius * 2 + 4, radius * 2 + 4)
                pygame.draw.arc(surface, (255, 255, 255, min(255, alpha)),
                                progress_rect, 0, end_angle, width=4)
        else:
            # --- Edge arrow pointing toward deposit center ---
            # Store in module vars so DrawOverlay (depth 9999) can draw it
            hw, hh = w // 2, h // 2
            dx_dir = sx - hw
            dy_dir = sy - hh
            dist = (dx_dir * dx_dir + dy_dir * dy_dir) ** 0.5
            if dist == 0:
                return
            dx_dir /= dist
            dy_dir /= dist

            margin = 24
            max_w = hw - margin
            max_h = hh - margin
            tx = max_w / abs(dx_dir) if dx_dir != 0 else float('inf')
            ty = max_h / abs(dy_dir) if dy_dir != 0 else float('inf')
            t = min(tx, ty)
            ax = int(hw + dx_dir * t)
            ay = int(hh + dy_dir * t)

            angle = math.atan2(dy_dir, dx_dir)
            arrow_len = 14
            dr_mod.arrow_visible = True
            dr_mod.arrow_tip = (ax, ay)
            dr_mod.arrow_left = (ax - arrow_len * math.cos(angle - 0.6),
                                 ay - arrow_len * math.sin(angle - 0.6))
            dr_mod.arrow_right = (ax - arrow_len * math.cos(angle + 0.6),
                                  ay - arrow_len * math.sin(angle + 0.6))

    def update(self, obj):
        obj.depth = -1
