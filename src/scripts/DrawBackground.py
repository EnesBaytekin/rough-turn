import pygame
from pygaminal.screen import Screen


class DrawBackground:
    def __init__(self, grid_size=32):
        self.grid_size = grid_size

    def _get_cam(self, obj):
        cam_comps = obj.get_components("scripts/Camera")
        return cam_comps[0] if cam_comps else None

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
