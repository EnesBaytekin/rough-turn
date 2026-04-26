import pygame
from pygaminal.app import App
from pygaminal.screen import Screen
from scripts.DrawAim import _get_overlay

# Deposit flash — set by Fake3DMovement, read here
deposit_flash = 0.0


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
                dsq = dx * dx + dy * dy  # 0 at center, 2 at corners
                t = min(1.0, dsq / 2.0)  # 0→1 normalized
                alpha = int(t * 150)
                surf.set_at((x, y), (0, 0, 0, alpha))
        return surf

    def _get_roughness(self):
        import scripts.DrawRock
        return getattr(scripts.DrawRock, 'slider_roughness', None)

    def _draw_roughness_bar(self, surface, w, h):
        roughness = self._get_roughness()
        if roughness is None:
            return

        # Fill ratio: 0 at roughness=0.6, 1 at roughness=0
        fill = max(0.0, min(1.0, 1.0 - roughness / 0.6))

        bar_w = int(w * 0.55)
        bar_h = 3
        bar_x = (w - bar_w) // 2
        bar_y = h - 10

        # Background (dark, subtle)
        bg_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        pygame.draw.rect(surface, (40, 35, 30, 180), bg_rect, border_radius=2)

        # Fill (warm golden, cozy)
        if fill > 0:
            fill_w = max(1, int(bar_w * fill))
            fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
            pygame.draw.rect(surface, (220, 170, 90), fill_rect, border_radius=2)

        # White border highlight when bar is full
        if fill >= 1.0:
            import scripts.DrawRock
            progress = getattr(scripts.DrawRock, 'deposit_progress', 0.0)
            thickness = 1 + int(progress * 2)  # pulses 1→3 during countdown
            alpha = min(255, 160 + int(progress * 95))
            border_rect = pygame.Rect(bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2)
            pygame.draw.rect(surface, (255, 255, 255, alpha), border_rect,
                             width=thickness, border_radius=2)

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

        # Roughness bar
        self._draw_roughness_bar(surface, w, h)

        # Deposit flash overlay
        if deposit_flash > 0:
            alpha = min(255, int(deposit_flash * 200))
            flash_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, alpha))
            surface.blit(flash_surf, (0, 0))

    def update(self, obj):
        import scripts.DrawOverlay as dover
        if dover.deposit_flash > 0:
            dover.deposit_flash = max(0.0, dover.deposit_flash - App().dt * 2.0)
        obj.depth = 9999
