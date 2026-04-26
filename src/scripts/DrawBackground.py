import pygame
import math
import random
from pygaminal.screen import Screen
from pygaminal.app import App


class DrawBackground:
    def __init__(self, coast_x=500, coast_y=800, coast_angle=-45, sand_width=200, tile_size=32):
        self.coast_x = coast_x
        self.coast_y = coast_y
        self.coast_angle = coast_angle
        self.sand_width = sand_width
        self.tile_size = tile_size
        self._sand_tile = None

    def _get_cam(self, obj):
        scene = App().get_current_scene()
        for other in scene.get_all_objects():
            cam_comps = other.get_components("scripts/Camera")
            if cam_comps:
                return cam_comps[0]
        return None

    def _make_sand_tile(self, size):
        """Procedural sand texture tile."""
        if self._sand_tile is not None:
            return self._sand_tile

        surf = pygame.Surface((size, size))
        base = (200, 170, 120)
        surf.fill(base)
        rng = random.Random(42)
        for _ in range(size * size // 6):
            x = rng.randint(0, size - 1)
            y = rng.randint(0, size - 1)
            v = rng.randint(-12, 8)
            surf.set_at((x, y), (max(0, base[0] + v), max(0, base[1] + v),
                                 max(0, base[2] + v - 5)))
        for _ in range(size * size // 20):
            x = rng.randint(0, size - 1)
            y = rng.randint(0, size - 1)
            surf.set_at((x, y), (base[0] - 25, base[1] - 20, base[2] - 15))

        self._sand_tile = surf
        return surf

    def _make_strip_poly(self, cam, d_start, d_end, coast_len):
        cx, cy = self.coast_x, self.coast_y
        ca = math.radians(self.coast_angle)
        cdx = math.cos(ca)
        cdy = math.sin(ca)
        ndx = -math.sin(ca)  # seaward normal
        ndy = math.cos(ca)

        scx, scy = cam.world_to_screen(cx, cy)

        p1 = (scx - cdx * coast_len, scy - cdy * coast_len)
        p2 = (scx + cdx * coast_len, scy + cdy * coast_len)

        near1 = (p1[0] - ndx * d_start, p1[1] - ndy * d_start)
        near2 = (p2[0] - ndx * d_start, p2[1] - ndy * d_start)
        far1  = (p1[0] - ndx * d_end, p1[1] - ndy * d_end)
        far2  = (p2[0] - ndx * d_end, p2[1] - ndy * d_end)

        return [(int(near1[0]), int(near1[1])),
                (int(near2[0]), int(near2[1])),
                (int(far2[0]), int(far2[1])),
                (int(far1[0]), int(far1[1]))]

    def draw(self, obj):
        surface = Screen().surface
        cam = self._get_cam(obj)
        if not cam:
            return

        w, h = Screen().width, Screen().height
        coast_len = max(w, h) * 10
        off_x = int(-cam.x) % self.tile_size
        off_y = int(-cam.y) % self.tile_size

        # Draw sand covering both sides of coast so no black shows through
        strip_pts = self._make_strip_poly(cam, -self.sand_width, self.sand_width, coast_len)

        zone_surf = pygame.Surface((w, h))
        zone_surf.fill((200, 170, 120))

        tile = self._make_sand_tile(self.tile_size)
        tx = off_x - self.tile_size
        while tx < w:
            ty = off_y - self.tile_size
            while ty < h:
                zone_surf.blit(tile, (tx, ty))
                ty += self.tile_size
            tx += self.tile_size

        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), strip_pts)
        zone_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(zone_surf, (0, 0))

    def update(self, obj):
        obj.depth = -999999
