import pygame
import random
import math
from pygaminal.screen import Screen
from pygaminal.app import App


class LaunchParticles:
    def __init__(self, count=16, spread_speed=60, lifetime=0.3):
        self.count = count
        self.spread_speed = spread_speed
        self.lifetime = lifetime
        self.particles = []
        self._was_moving = False

    def _get_mov(self, obj):
        mov_comps = obj.get_components("scripts/Fake3DMovement")
        return mov_comps[0] if mov_comps else None

    def update(self, obj):
        mov = self._get_mov(obj)
        if not mov:
            return

        if mov.moving and not self._was_moving:
            from pygaminal.input_manager import InputManager
            inp = InputManager()
            mx = inp.get_mouse_x()
            my = inp.get_mouse_y()

            self.particles = []
            colors = [(255, 240, 210), (240, 215, 190), (220, 195, 175), (200, 180, 160)]
            for _ in range(self.count):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(self.spread_speed * 0.4, self.spread_speed)
                self.particles.append({
                    "x": mx,
                    "y": my,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": self.lifetime,
                    "color": random.choice(colors),
                })

        self._was_moving = mov.moving

        dt = App().dt
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["vx"] *= 0.85
            p["y"] += p["vy"] * dt
            p["vy"] *= 0.85
            p["life"] -= dt

        self.particles = [p for p in self.particles if p["life"] > 0]

    def draw(self, obj):
        if not self.particles:
            return

        surface = Screen().surface
        for p in self.particles:
            t = p["life"] / self.lifetime
            alpha = max(0, min(255, int(255 * t)))
            r, g, b = p["color"]
            psurf = pygame.Surface((1, 1), pygame.SRCALPHA)
            psurf.set_at((0, 0), (r, g, b, alpha))
            surface.blit(psurf, (int(p["x"]), int(p["y"])))
