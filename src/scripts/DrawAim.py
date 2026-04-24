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
        if inp.is_mouse_pressed(1):
            pygame.draw.circle(surface, (245, 240, 228), (int(mx), int(my)), 3)
        else:
            pygame.draw.circle(surface, (200, 195, 185), (int(mx), int(my)), 4, 1)

        # Shared base length
        line_len = min(dist, self.max_line_len)
        a = radians(mov.angle)
        h_len = line_len * cos(a)
        v_len = line_len * sin(a)

        # --- Horizontal leg (warm cream dashed) ---
        if h_len > 0.5:
            dash_len = 6
            gap_len = 4
            step = dash_len + gap_len
            pos = 0
            while pos < h_len:
                end = min(pos + dash_len, h_len)
                x1 = int(bx + nx * pos)
                y1 = int(by + ny * pos)
                x2 = int(bx + nx * end)
                y2 = int(by + ny * end)
                pygame.draw.line(surface, (225, 218, 200), (x1, y1), (x2, y2), 1)
                pos += step

        # --- Vertical leg (straight up from horizontal endpoint, warm rose) ---
        hx = bx + nx * h_len
        hy = by + ny * h_len
        if v_len > 0.5:
            vx1 = int(hx)
            vy1 = int(hy)
            vx2 = int(hx)
            vy2 = int(hy - v_len)
            pygame.draw.line(surface, (200, 175, 165), (vx1, vy1), (vx2, vy2), 1)

        # --- Diagonal (warm amber, semi-transparent) — from ball to combined endpoint ---
        ex1 = int(bx)
        ey1 = int(by - mov.z)
        ex2 = int(hx)
        ey2 = int(hy - v_len)
        # Fallback if both legs are zero-length: straight up
        if abs(hx - bx) < 0.5 and abs(hy - by - v_len) < 0.5:
            ex2, ey2 = int(bx), int(by - line_len)
        lsurf = pygame.Surface((Screen().width, Screen().height), pygame.SRCALPHA)
        pygame.draw.line(lsurf, (210, 170, 130, 180), (ex1, ey1), (ex2, ey2), 2)
        surface.blit(lsurf, (0, 0))

    def update(self, obj):
        pass
