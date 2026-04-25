import pygame
from pygaminal.screen import Screen
from pygaminal.app import App
from math import cos, sin, radians


class Wall:
    def __init__(self, width=100, thickness=8, angle=0, color="#887a6e", height=40):
        self.width = width
        self.thickness = thickness
        self.angle = angle
        self.color = pygame.Color(color)
        self.height = height

    def _get_cam(self, obj):
        scene = App().get_current_scene()
        for other in scene.get_all_objects():
            cam_comps = other.get_components("scripts/Camera")
            if cam_comps:
                return cam_comps[0]
        return None

    def _get_corners(self, sx, sy, z_off=0):
        a = radians(self.angle)
        hw = self.width / 2
        ht = self.thickness / 2
        ca, sa = cos(a), sin(a)
        corners = []
        for lx, ly in [(-hw, -ht), (hw, -ht), (hw, ht), (-hw, ht)]:
            wx = lx * ca - ly * sa
            wy = lx * sa + ly * ca
            corners.append((sx + wx, sy + wy - z_off))
        return corners

    def draw(self, obj):
        surface = Screen().surface
        cam = self._get_cam(obj)
        sx, sy = cam.world_to_screen(obj.x, obj.y) if cam else (obj.x, obj.y)

        bottom = self._get_corners(sx, sy, 0)
        top = self._get_corners(sx, sy, self.height)

        # Side face color (darker)
        r = max(0, self.color.r - 40)
        g = max(0, self.color.g - 40)
        b = max(0, self.color.b - 40)
        side_color = (r, g, b)

        # Build side face quads with depth key (average Y, higher = further)
        side_faces = []
        for i in range(4):
            j = (i + 1) % 4
            quad = [
                (int(bottom[i][0]), int(bottom[i][1])),
                (int(top[i][0]), int(top[i][1])),
                (int(top[j][0]), int(top[j][1])),
                (int(bottom[j][0]), int(bottom[j][1])),
            ]
            avg_y = (bottom[i][1] + top[i][1] + top[j][1] + bottom[j][1]) / 4
            side_faces.append((avg_y, quad))

        # Sort by depth: further (higher Y) drawn first
        side_faces.sort(key=lambda f: f[0])
        for _, quad in side_faces:
            pygame.draw.polygon(surface, side_color, quad)

        # Draw top face last (closest to viewer)
        top_pts = [(int(x), int(y)) for x, y in top]
        pygame.draw.polygon(surface, self.color, top_pts)

    def update(self, obj):
        obj.depth = obj.y
