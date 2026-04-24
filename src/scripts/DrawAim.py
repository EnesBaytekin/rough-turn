import pygame
from pygaminal.screen import Screen
from pygaminal.input_manager import InputManager


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

        # Mouse screen coords → world coords
        mx = inp.get_mouse_x()
        my = inp.get_mouse_y()
        world_mx, world_my = cam.screen_to_world(mx, my) if cam else (mx, my)

        # Direction in world space
        dx = obj.x - world_mx
        dy = obj.y - world_my
        dist = (dx * dx + dy * dy) ** 0.5

        if dist < 3:
            return

        nx = dx / dist
        ny = dy / dist

        # Ball screen position
        bx, by = cam.world_to_screen(obj.x, obj.y) if cam else (obj.x, obj.y)

        # --- Cursor dot (screen space) ---
        behind = world_my < obj.y
        if behind:
            pygame.draw.circle(surface, (200, 200, 200), (int(mx), int(my)), 4, 1)
        else:
            pygame.draw.circle(surface, (255, 255, 255), (int(mx), int(my)), 3)

        # --- Dashed direction line ---
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

    def update(self, obj):
        pass
