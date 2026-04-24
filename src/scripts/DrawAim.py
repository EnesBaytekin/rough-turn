import pygame
from pygaminal.screen import Screen
from pygaminal.input_manager import InputManager


class DrawAim:
    def __init__(self, max_line_len=60):
        self.max_line_len = max_line_len

    def draw(self, obj):
        mov_comps = obj.get_components("scripts/Fake3DMovement")
        if not mov_comps:
            return
        mov = mov_comps[0]

        # Only show aim when idle
        if mov.moving:
            return

        inp = InputManager()
        surface = Screen().surface

        mx = inp.get_mouse_x()
        my = inp.get_mouse_y()

        dx = obj.x - mx
        dy = obj.y - my
        dist = (dx * dx + dy * dy) ** 0.5

        if dist < 3:
            return

        nx = dx / dist
        ny = dy / dist

        # --- Cursor dot ---
        behind = my < obj.y
        if behind:
            # Dotted circle to indicate behind
            pygame.draw.circle(surface, (200, 200, 200), (int(mx), int(my)), 4, 1)
        else:
            # Solid white dot
            pygame.draw.circle(surface, (255, 255, 255), (int(mx), int(my)), 3)

        # --- Dashed direction line ---
        line_len = min(dist, self.max_line_len)
        dash_len = 5
        gap_len = 3
        step = dash_len + gap_len
        pos = 0

        while pos < line_len:
            end = min(pos + dash_len, line_len)
            x1 = int(obj.x + nx * pos)
            y1 = int(obj.y + ny * pos)
            x2 = int(obj.x + nx * end)
            y2 = int(obj.y + ny * end)
            pygame.draw.line(surface, (255, 255, 255), (x1, y1), (x2, y2), 1)
            pos += step

    def update(self, obj):
        pass
