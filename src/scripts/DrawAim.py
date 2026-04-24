import pygame
from pygaminal.screen import Screen
from pygaminal.input_manager import InputManager
from math import cos, sin, radians


class DrawAim:
    def __init__(self, max_line_len=60):
        self.max_line_len = max_line_len
        self._dot_surf = None
        self._line_surf = None

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
            # Soft muted circle outline
            pygame.draw.circle(surface, (165, 160, 150), (int(mx), int(my)), 4, 1)
        else:
            # Warm white dot
            pygame.draw.circle(surface, (245, 240, 228), (int(mx), int(my)), 3)

        # --- Horizontal direction (warm cream dashed) ---
        line_len = min(dist, self.max_line_len)
        dash_len = 6
        gap_len = 4
        step = dash_len + gap_len
        pos = 0
        while pos < line_len:
            end = min(pos + dash_len, line_len)
            x1 = int(bx + nx * pos)
            y1 = int(by + ny * pos)
            x2 = int(bx + nx * end)
            y2 = int(by + ny * end)
            pygame.draw.line(surface, (225, 218, 200), (x1, y1), (x2, y2), 1)
            pos += step

        # --- 3D vector line (warm amber, semi-transparent) — same base length ---
        a = radians(mov.angle)
        edx = nx * cos(a) * line_len
        edy = (ny * cos(a) - sin(a)) * line_len
        elen = (edx * edx + edy * edy) ** 0.5
        if elen < 0.5:
            edx, edy = 0, -line_len

        # Draw with alpha via temp surface
        ex1 = int(bx)
        ey1 = int(by - mov.z)
        ex2 = int(bx + edx)
        ey2 = int(by - mov.z + edy)
        lsurf = pygame.Surface((Screen().width, Screen().height), pygame.SRCALPHA)
        pygame.draw.line(lsurf, (210, 170, 130, 180), (ex1, ey1), (ex2, ey2), 2)
        surface.blit(lsurf, (0, 0))

    def update(self, obj):
        pass
