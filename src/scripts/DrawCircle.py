import pygame
from pygaminal.screen import Screen


class DrawCircle:
    def __init__(self, color="#4488ff", radius=16, shadow=True):
        self.color = pygame.Color(color)
        self.radius = radius
        self.shadow = shadow

    def draw(self, obj):
        surface = Screen().surface
        cx = int(obj.x)
        cy = int(obj.y)

        # Check for 3D depth offset
        z = 0
        mov_comps = obj.get_components("scripts/Fake3DMovement")
        if mov_comps:
            z = mov_comps[0].z

        # Shadow on the ground (always visible)
        if self.shadow:
            size_scale = max(0.3, 1 - (z / 100))
            sw = max(2, int(self.radius * size_scale))
            sh = max(1, int(self.radius * 0.4 * size_scale))
            shadow_alpha = max(20, int(50 * size_scale))
            shadow_surf = pygame.Surface((sw * 2, sh * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha), shadow_surf.get_rect())
            surface.blit(shadow_surf, (cx - sw, cy - sh))

        # Circle bottom aligned with (cy - z)
        screen_y = cy - z - self.radius
        pygame.draw.circle(surface, self.color, (cx, screen_y), self.radius)

    def update(self, obj):
        pass
