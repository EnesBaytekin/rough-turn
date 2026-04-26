import pygame
import random
import math
from pygaminal.screen import Screen
from pygaminal.app import App


class Drizzles:
    def __init__(self, count=40, angle=20, speed=250):
        self.count = count
        self.angle = angle  # degrees from vertical
        self.speed = speed  # pixels per second
        self._drops = []
        self._initialized = False

    def _init_drops(self):
        w, h = Screen().width, Screen().height
        if w == 0 or h == 0:
            return False
        rad = math.radians(self.angle)
        self._dx = math.sin(rad) * self.speed
        self._dy = math.cos(rad) * self.speed
        for _ in range(self.count):
            self._drops.append({
                "x": random.uniform(0, w),
                "y": random.uniform(0, h),
                "len": random.uniform(4, 12),
                "alpha": random.uniform(10, 30),
                "speed_mul": random.uniform(0.6, 1.4),
            })
        return True

    def draw(self, obj):
        if not self._initialized:
            self._initialized = self._init_drops()
            return

        surface = Screen().surface
        w, h = Screen().width, Screen().height
        dt = App().dt
        t = App().now

        for drop in self._drops:
            sm = drop["speed_mul"]
            drop["x"] += self._dx * sm * dt
            drop["y"] += self._dy * sm * dt

            # Also add a gentle horizontal drift for cozy feel
            drift = math.sin(t * 0.5 + drop["x"] * 0.1) * 0.3 * dt * 60
            drop["x"] += drift * sm

            # Wrap around
            margin = 30
            if drop["y"] > h + margin:
                drop["y"] = -margin
                drop["x"] = random.uniform(-margin, w + margin)
            if drop["x"] > w + margin:
                drop["x"] = -margin
            if drop["x"] < -margin:
                drop["x"] = w + margin

            # Draw
            rad = math.radians(self.angle)
            lx = math.sin(rad) * drop["len"]
            ly = math.cos(rad) * drop["len"]

            alpha = int(drop["alpha"] * (0.8 + 0.2 * math.sin(t * 1.5 + drop["x"])))
            color = (255, 220, 180, min(255, alpha))
            pygame.draw.line(
                surface,
                color[:3],
                (drop["x"], drop["y"]),
                (drop["x"] + lx, drop["y"] + ly),
                1,
            )

    def update(self, obj):
        obj.depth = 9001
