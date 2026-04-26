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
        self._num_pts = 80

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

    def _make_s_curve(self, scx, scy, cdx, cdy, ndx, ndy, coast_len, t):
        """Generate S-curved coastline points with reversing curves."""
        # Phase oscillates back and forth so S-curves reverse direction
        phase1 = math.sin(t * 0.20) * math.pi  # -pi to +pi, ~31s cycle
        phase2 = math.sin(t * 0.30) * math.pi * 0.6

        # Magnitude also changes slowly
        mag1 = 10 + math.sin(t * 0.10) * 3
        mag2 = 5 + math.sin(t * 0.16) * 2

        pts = []
        for i in range(self._num_pts):
            frac = i / (self._num_pts - 1)
            px = scx + cdx * coast_len * (frac * 2 - 1)
            py = scy + cdy * coast_len * (frac * 2 - 1)

            # S-curves oscillate: sin(wave + oscillating_phase)
            s = math.sin(frac * 4 * math.pi + phase1) * mag1
            s += math.sin(frac * 7 * math.pi + phase2) * mag2

            pts.append((px + ndx * s, py + ndy * s))
        return pts

    def _band_offset(self, pts, ndx, ndy, offset):
        """Offset all points in the normal direction."""
        return [(x + ndx * offset, y + ndy * offset) for x, y in pts]

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
        coast_len = max(w, h) * 10
        extent = self.water_extent

        # S-curved coastline
        coast_pts = self._make_s_curve(scx, scy, cdx, cdy, ndx, ndy, coast_len, t)

        # --- Water body (S-curved top edge, extends into sea) ---
        water_pts = [(int(x), int(y)) for x, y in coast_pts]
        for x, y in reversed(coast_pts):
            water_pts.append((int(x + ndx * extent), int(y + ndy * extent)))

        water_color = (90, 130, 170)  # blue
        pygame.draw.polygon(surface, water_color, water_pts)

        # --- S-curved wave bands that oscillate in/out ---
        wave_bands = [
            {"base": 8,   "amp": 14, "speed": 0.9, "phase": 0.0, "width": 9,  "r": 155, "g": 190, "b": 215},
            {"base": 32,  "amp": 12, "speed": 1.0, "phase": 1.1, "width": 11, "r": 135, "g": 170, "b": 200},
            {"base": 58,  "amp": 10, "speed": 1.1, "phase": 2.2, "width": 13, "r": 115, "g": 150, "b": 185},
            {"base": 86,  "amp": 8,  "speed": 1.2, "phase": 3.3, "width": 15, "r": 100, "g": 135, "b": 170},
            {"base": 118, "amp": 5,  "speed": 1.3, "phase": 4.4, "width": 17, "r": 85,  "g": 120, "b": 155},
        ]

        for band in wave_bands:
            osc = math.sin(t * band["speed"] + band["phase"]) * band["amp"]
            band_center = band["base"] + osc
            half_w = band["width"] / 2

            inner_pts = self._band_offset(coast_pts, ndx, ndy, band_center - half_w)
            outer_pts = self._band_offset(coast_pts, ndx, ndy, band_center + half_w)

            band_poly = [(int(x), int(y)) for x, y in inner_pts]
            band_poly.extend([(int(x), int(y)) for x, y in reversed(outer_pts)])

            sand_overlap = max(0, -band_center) / 30.0
            alpha = int(max(30, 130 - sand_overlap * 100))

            band_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.polygon(band_surf, (band["r"], band["g"], band["b"], alpha), band_poly)
            surface.blit(band_surf, (0, 0))

        # --- Foam edge (follows S-curve, oscillates) ---
        foam_osc = math.sin(t * 0.9) * 16
        foam_pos = -3 + foam_osc
        foam_half = 5

        foam_inner = self._band_offset(coast_pts, ndx, ndy, foam_pos - foam_half)
        foam_outer = self._band_offset(coast_pts, ndx, ndy, foam_pos + foam_half)

        foam_poly = [(int(x), int(y)) for x, y in foam_inner]
        foam_poly.extend([(int(x), int(y)) for x, y in reversed(foam_outer)])

        foam_pulse = 0.6 + 0.4 * abs(math.sin(t * 1.3))
        foam_alpha = int(140 * foam_pulse)
        foam_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(foam_surf, (255, 240, 210, min(255, foam_alpha)), foam_poly)
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
        obj.depth = -99999
