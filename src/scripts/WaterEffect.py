import pygame
import math
import random
from pygaminal.screen import Screen
from pygaminal.app import App


class WaterEffect:
    def __init__(self, coast_x=500, coast_y=800, coast_angle=-45, water_extent=400):
        self.coast_x = coast_x
        self.coast_y = coast_y
        self.coast_angle = coast_angle
        self.water_extent = water_extent
        self._sparkles = []
        self._init_sparkles()

    def _init_sparkles(self):
        for _ in range(30):
            self._sparkles.append({
                "x": random.uniform(0, self.water_extent),
                "y": random.uniform(0, 200),
                "phase": random.uniform(0, 6.28),
                "size": random.choice([1, 1, 2]),
            })

    def _get_cam(self, obj):
        scene = App().get_current_scene()
        for other in scene.get_all_objects():
            cam_comps = other.get_components("scripts/Camera")
            if cam_comps:
                return cam_comps[0]
        return None

    def draw(self, obj):
        surface = Screen().surface
        cam = self._get_cam(obj)
        if not cam:
            return

        w, h = Screen().width, Screen().height
        t = App().now

        ca = math.radians(self.coast_angle)
        cdx = math.cos(ca)
        cdy = math.sin(ca)
        na = ca + math.pi / 2  # sea normal (bottom-right)
        ndx = math.cos(na)
        ndy = math.sin(na)

        scx, scy = cam.world_to_screen(self.coast_x, self.coast_y)
        coast_len = max(w, h) * 2
        extent = self.water_extent

        p1 = (scx - cdx * coast_len, scy - cdy * coast_len)
        p2 = (scx + cdx * coast_len, scy + cdy * coast_len)

        # --- Base water fill (sea side only) ---
        p3 = (p2[0] + ndx * extent, p2[1] + ndy * extent)
        p4 = (p1[0] + ndx * extent, p1[1] + ndy * extent)
        water_color = (180, 120, 90)
        screen_pts = [(int(x), int(y)) for x, y in [p1, p2, p3, p4]]
        pygame.draw.polygon(surface, water_color, screen_pts)

        # --- Animated wave bands that wash onto sand ---
        # Each band oscillates across the coastline:
        # positive offset = sea side, negative = onto sand
        wave_bands = [
            {"base": 5,   "amp": 24, "speed": 0.9, "phase": 0.0, "width": 9,  "r": 215, "g": 180, "b": 148},
            {"base": 28,  "amp": 20, "speed": 1.0, "phase": 1.1, "width": 11, "r": 200, "g": 165, "b": 135},
            {"base": 52,  "amp": 16, "speed": 1.1, "phase": 2.2, "width": 13, "r": 185, "g": 150, "b": 120},
            {"base": 78,  "amp": 12, "speed": 1.2, "phase": 3.3, "width": 15, "r": 170, "g": 135, "b": 108},
            {"base": 108, "amp": 8,  "speed": 1.3, "phase": 4.4, "width": 17, "r": 155, "g": 120, "b": 95},
        ]

        for band in wave_bands:
            osc = math.sin(t * band["speed"] + band["phase"]) * band["amp"]
            band_center = band["base"] + osc
            band_half = band["width"] // 2

            bn1 = (p1[0] + ndx * (band_center - band_half),
                   p1[1] + ndy * (band_center - band_half))
            bn2 = (p2[0] + ndx * (band_center - band_half),
                   p2[1] + ndy * (band_center - band_half))
            bf2 = (p2[0] + ndx * (band_center + band_half),
                   p2[1] + ndy * (band_center + band_half))
            bf1 = (p1[0] + ndx * (band_center + band_half),
                   p1[1] + ndy * (band_center + band_half))

            # Fade alpha based on how far onto sand the band is
            # More onto sand = more transparent (thinner wash)
            sand_overlap = max(0, -band_center) / 30.0  # 0 on sea, ~1 when deep onto sand
            alpha = int(max(30, 130 - sand_overlap * 100))

            band_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            band_pts = [(int(bn1[0]), int(bn1[1])),
                        (int(bn2[0]), int(bn2[1])),
                        (int(bf2[0]), int(bf2[1])),
                        (int(bf1[0]), int(bf1[1]))]
            pygame.draw.polygon(band_surf, (band["r"], band["g"], band["b"], alpha), band_pts)
            surface.blit(band_surf, (0, 0))

        # --- Foam/white edge that washes up on sand ---
        foam_osc = math.sin(t * 0.9) * 24
        foam_pos = -5 + foam_osc  # oscillates from -29 to +19 relative to coast
        foam_half = 5

        fn1 = (p1[0] + ndx * (foam_pos - foam_half),
               p1[1] + ndy * (foam_pos - foam_half))
        fn2 = (p2[0] + ndx * (foam_pos - foam_half),
               p2[1] + ndy * (foam_pos - foam_half))
        ff2 = (p2[0] + ndx * (foam_pos + foam_half),
               p2[1] + ndy * (foam_pos + foam_half))
        ff1 = (p1[0] + ndx * (foam_pos + foam_half),
               p1[1] + ndy * (foam_pos + foam_half))

        foam_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        foam_pts = [(int(fn1[0]), int(fn1[1])),
                    (int(fn2[0]), int(fn2[1])),
                    (int(ff2[0]), int(ff2[1])),
                    (int(ff1[0]), int(ff1[1]))]
        foam_pulse = 0.6 + 0.4 * abs(math.sin(t * 1.3))
        foam_alpha = int(140 * foam_pulse)
        pygame.draw.polygon(foam_surf, (255, 240, 210, min(255, foam_alpha)), foam_pts)
        surface.blit(foam_surf, (0, 0))

        # --- Sparkles on water ---
        for sp in self._sparkles:
            sp_dist_along = sp["x"]
            sp_dist_sea = 20 + sp["y"]

            sw = scx + cdx * sp_dist_along + ndx * sp_dist_sea
            sh = scy + cdy * sp_dist_along + ndy * sp_dist_sea

            twinkle = 0.3 + 0.7 * abs(math.sin(t * 1.5 + sp["phase"]))
            if twinkle > 0.5:
                alpha = int(180 * twinkle)
                size = sp["size"]
                psurf = pygame.Surface((size + 1, size + 1))
                psurf.set_colorkey((0, 0, 0))
                color = (255, 220, 150)
                pygame.draw.circle(psurf, color, (size // 2 + 1, size // 2 + 1), size)
                psurf.set_alpha(alpha)
                surface.blit(psurf, (int(sw), int(sh)))

    def update(self, obj):
        obj.depth = -2
