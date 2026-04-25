import pygame
from pygaminal.screen import Screen
from scripts.DrawAim import _get_overlay


class DrawOverlay:
    def draw(self, obj):
        overlay = _get_overlay()
        Screen().surface.blit(overlay, (0, 0))

    def update(self, obj):
        obj.depth = 9999
