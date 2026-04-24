import pygame
from pygaminal.screen import Screen
from pygaminal.input_manager import InputManager
from math import cos, sin, radians


class DrawAim:
    def __init__(self, max_line_len=60):
        self.max_line_len = max_line_len

    def _get_cam(self, obj):
        cam_comps = obj.get_components("scripts/Camera")
        return cam_comps[0] if cam_comps else None

    def draw(self, obj):
        mov_comps = obj.get_components("scripts/Fake3DMovement")
        if not mov_comps:
            return
        mov = mov_comps[0]

        if mov.moving:
            return

        inp = InputManager()
        surface = Screen().surface
        cam = self._get_cam(obj)

        mx = inp.get_mouse_x()
        my = inp.get_mouse_y()
        world_mx, world_my = cam.screen_to_world(mx, my) if cam else (mx, my)

        dx = obj.x - world_mx
        dy = obj.y - world_my
        dist = (dx * dx + dy * dy) ** 0.5

        if dist < 3:
            return

        nx = dx / dist
        ny = dy / dist

        bx, by = cam.world_to_screen(obj.x, obj.y) if cam else (obj.x, obj.y)

        # --- Cursor dot ---
        behind = world_my < obj.y
        if behind:
            pygame.draw.circle(surface, (200, 200, 200), (int(mx), int(my)), 4, 1)
        else:
            pygame.draw.circle(surface, (255, 255, 255), (int(mx), int(my)), 3)

        # --- Horizontal direction (white dashed) ---
        line_len = min(dist, self.max_line_len)
        dash_len = 5
        gap_len = 3
        step = dash_len + gap_len
        pos = 0
        while pos < line_len:
            end = min(pos + dash_len, line_len)
            x1 = int(bx + nx * pos)
            y1 = int(by + ny * pos)
            x2 = int(bx + nx * end)
            y2 = int(by + ny * end)
            pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 1)
            pos += step

        # --- 3D vector line (cyan) — same base length as horizontal ---
        a = radians(mov.angle)
        edx = nx * cos(a) * line_len
        edy = (ny * cos(a) - sin(a)) * line_len
        elen = (edx * edx + edy * edy) ** 0.5
        if elen < 0.5:
            edx, edy = 0, -line_len
        ex1 = int(bx)
        ey1 = int(by - mov.z)
        ex2 = int(bx + edx)
        ey2 = int(by - mov.z + edy)
        pygame.draw.line(surface, (100, 220, 255), (ex1, ey1), (ex2, ey2), 2)

    def update(self, obj):
        pass
