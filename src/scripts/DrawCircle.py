import pygame
from pygaminal.screen import Screen


class DrawCircle:
    def __init__(self, color="#4488ff", radius=16, shadow=True):
        self.color = pygame.Color(color)
        self.radius = radius
        self.shadow = shadow

    def _get_cam(self, obj):
        cam_comps = obj.get_components("scripts/Camera")
        return cam_comps[0] if cam_comps else None

    def draw(self, obj):
        surface = Screen().surface
        cam = self._get_cam(obj)

        # World to screen
        sx, sy = cam.world_to_screen(obj.x, obj.y) if cam else (obj.x, obj.y)
        sx = int(sx)
        sy = int(sy)

        # Check for 3D depth offset
        z = 0
        mov_comps = obj.get_components("scripts/Fake3DMovement")
        if mov_comps:
            z = mov_comps[0].z

        # Shadow on the ground
        if self.shadow:
            size_scale = max(0.3, 1 - (z / 100))
            sw = max(2, int(self.radius * size_scale))
            sh = max(1, int(self.radius * 0.4 * size_scale))
            shadow_alpha = max(20, int(50 * size_scale))
            shadow_surf = pygame.Surface((sw * 2, sh * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha), shadow_surf.get_rect())
            surface.blit(shadow_surf, (sx - sw, sy - sh))

        # Circle bottom aligned with (world_y - z)
        screen_y = sy - z - self.radius
        pygame.draw.circle(surface, self.color, (sx, screen_y), self.radius)

    def update(self, obj):
        pass
