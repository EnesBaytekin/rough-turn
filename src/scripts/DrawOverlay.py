import pygame
from pygaminal.screen import Screen
from scripts.DrawAim import _get_overlay


class DrawOverlay:
    def __init__(self):
        self._vignette = None
        self._warm_wash = None

    def _build_vignette(self, w, h):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(h):
            for x in range(w):
                dx = (x / w - 0.5) * 2
                dy = (y / h - 0.5) * 2
                dist = min(1.0, (dx * dx + dy * dy) * 1.5)
                alpha = int(dist * 100)
                surf.set_at((x, y), (0, 0, 0, alpha))
        return surf

    def draw(self, obj):
        surface = Screen().surface
        w, h = Screen().width, Screen().height

        # DrawAim overlay
        overlay = _get_overlay()
        surface.blit(overlay, (0, 0))

        # Vignette
        if self._vignette is None or self._vignette.get_size() != (w, h):
            self._vignette = self._build_vignette(w, h)
        surface.blit(self._vignette, (0, 0))

        # Warm color wash
        if self._warm_wash is None or self._warm_wash.get_size() != (w, h):
            self._warm_wash = pygame.Surface((w, h), pygame.SRCALPHA)
            self._warm_wash.fill((200, 150, 80, 15))
        surface.blit(self._warm_wash, (0, 0))

    def update(self, obj):
        obj.depth = 9999
