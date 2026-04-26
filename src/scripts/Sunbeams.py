import pygame
import math
from pygaminal.screen import Screen
from pygaminal.app import App


class Sunbeams:
    def __init__(self, sun_x=-200, sun_y=-100, num_rays=3):
        self.sun_x = sun_x
        self.sun_y = sun_y
        self.num_rays = num_rays
        self._surf = None

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

        if self._surf is None or self._surf.get_size() != (w, h):
            self._surf = pygame.Surface((w, h), pygame.SRCALPHA)

        self._surf.fill((0, 0, 0, 0))

        # Sun position in screen coordinates
        sun_sx, sun_sy = cam.world_to_screen(self.sun_x, self.sun_y)
        t = App().now
        alpha_base = 18 + int(math.sin(t * 0.3) * 5)

        ray_angles = [-15, -5, 5, 15] if self.num_rays >= 4 else [-10, 0, 10]

        for i, angle in enumerate(ray_angles[:self.num_rays]):
            rad = math.radians(angle)
            dx = math.sin(rad)
            dy = math.cos(rad)

            # Ray extends downward from sun
            ray_len = max(w, h) * 1.5
            ex = sun_sx + dx * ray_len
            ey = sun_sy + dy * ray_len

            # Wide beam (trapezoid)
            spread = 15 + i * 3
            rad2 = math.radians(angle + spread)
            dx2 = math.sin(rad2)
            dy2 = math.cos(rad2)
            ex2 = sun_sx + dx2 * ray_len
            ey2 = sun_sy + dy2 * ray_len

            rad3 = math.radians(angle - spread)
            dx3 = math.sin(rad3)
            dy3 = math.cos(rad3)
            ex3 = sun_sx + dx3 * ray_len
            ey3 = sun_sy + dy3 * ray_len

            alpha = max(5, alpha_base - i * 3)
            color = (255, 200, 100, alpha)

            pts = [(sun_sx, sun_sy), (ex2, ey2), (ex3, ey3)]
            pygame.draw.polygon(self._surf, color, pts)

        surface.blit(self._surf, (0, 0))

    def update(self, obj):
        obj.depth = 9000
