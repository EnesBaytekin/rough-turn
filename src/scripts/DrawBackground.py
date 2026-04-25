import pygame
from pygaminal.screen import Screen
from pygaminal.app import App


class DrawBackground:
    def __init__(self, grid_size=32):
        self.grid_size = grid_size

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
        w = Screen().width
        h = Screen().height

        cam_x = cam.x if cam else 0
        cam_y = cam.y if cam else 0

        off_x = -cam_x % self.grid_size
        off_y = -cam_y % self.grid_size

        color = (100, 130, 140)

        # Vertical lines
        x = off_x
        while x < w:
            pygame.draw.line(surface, color, (x, 0), (x, h), 1)
            x += self.grid_size

        # Horizontal lines
        y = off_y
        while y < h:
            pygame.draw.line(surface, color, (0, y), (w, y), 1)
            y += self.grid_size

    def update(self, obj):
        pass
