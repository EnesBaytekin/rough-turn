import pygame
import random
import math
from pygaminal.screen import Screen
from pygaminal.app import App


class AmbientParticles:
    def __init__(self, particle_type="dust", count=30, region_x=0, region_y=0,
                 region_w=320, region_h=180, emit_rate=0.02):
        self.particle_type = particle_type
        self.region_x = region_x
        self.region_y = region_y
        self.region_w = region_w
        self.region_h = region_h
        self.emit_rate = emit_rate
        self.particles = []
        self._init_particles(count)

    def _init_particles(self, count):
        for _ in range(count):
            p = self._spawn_one()
            if p:
                self.particles.append(p)

    def _spawn_one(self):
        if self.particle_type == "dust":
            return {
                "x": random.uniform(self.region_x, self.region_x + self.region_w),
                "y": random.uniform(self.region_y, self.region_y + self.region_h),
                "vx": random.uniform(-3, 3),
                "vy": random.uniform(-5, -1),
                "size": random.choice([1, 1, 2]),
                "alpha": random.uniform(20, 50),
                "phase": random.uniform(0, 6.28),
                "life": -1,  # infinite, recycled
            }
        elif self.particle_type == "firefly":
            return {
                "x": random.uniform(self.region_x, self.region_x + self.region_w),
                "y": random.uniform(self.region_y, self.region_y + self.region_h),
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(-2, 2),
                "size": 2,
                "alpha": random.uniform(100, 200),
                "phase": random.uniform(0, 6.28),
                "life": random.uniform(3, 6),
            }
        elif self.particle_type == "leaf":
            return {
                "x": random.uniform(self.region_x, self.region_x + self.region_w),
                "y": self.region_y - 10,
                "vx": random.uniform(-8, -2),
                "vy": random.uniform(8, 15),
                "size": random.choice([2, 3]),
                "alpha": random.uniform(40, 80),
                "phase": random.uniform(0, 6.28),
                "life": random.uniform(2, 4),
                "spin": random.uniform(-3, 3),
            }
        return None

    def draw(self, obj):
        surface = Screen().surface
        w, h = Screen().width, Screen().height
        dt = App().dt
        t = App().now

        # Emit new particles
        if random.random() < self.emit_rate:
            p = self._spawn_one()
            if p:
                self.particles.append(p)

        for p in self.particles[:]:
            p["life"] -= dt

            if p["life"] < -0.1:
                self.particles.remove(p)
                continue

            # Only recycle if we still need to remove
            if p["life"] <= 0 and p["life"] > -0.1:
                if self.particle_type == "dust":
                    # Recycle
                    p["x"] = random.uniform(self.region_x, self.region_x + self.region_w)
                    p["y"] = random.uniform(self.region_y, self.region_y + self.region_h)
                    p["life"] = -1

            if self.particle_type == "dust":
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                p["vx"] += math.sin(t * 0.5 + p["phase"]) * 2 * dt
                p["vy"] += math.cos(t * 0.7 + p["phase"]) * 1 * dt
                # Keep in region
                if p["y"] < self.region_y - 20:
                    p["y"] = self.region_y + self.region_h + 10
                    p["x"] = random.uniform(self.region_x, self.region_x + self.region_w)

                alpha = int(p["alpha"] * (0.7 + 0.3 * math.sin(t + p["phase"])))
                color = (255, 220, 150, min(255, alpha))
                size = p["size"]
                psurf = pygame.Surface((size, size))
                psurf.set_colorkey((0, 0, 0))
                pygame.draw.circle(psurf, color[:3], (size // 2, size // 2), size // 2)
                psurf.set_alpha(alpha)
                surface.blit(psurf, (int(p["x"]), int(p["y"])))

            elif self.particle_type == "firefly":
                p["x"] += math.sin(t * 2 + p["phase"]) * 4 * dt
                p["y"] += math.cos(t * 1.5 + p["phase"]) * 3 * dt
                # Keep in region
                margin = 30
                if p["x"] < self.region_x - margin:
                    p["x"] = self.region_x + self.region_w + margin
                if p["x"] > self.region_x + self.region_w + margin:
                    p["x"] = self.region_x - margin
                if p["y"] < self.region_y - margin:
                    p["y"] = self.region_y + self.region_h + margin
                if p["y"] > self.region_y + self.region_h + margin:
                    p["y"] = self.region_y - margin

                # Pulsing brightness
                glow = 0.5 + 0.5 * math.sin(t * 2.5 + p["phase"])
                alpha = int(p["alpha"] * glow)
                radius = 2 + int(glow * 2)

                psurf = pygame.Surface((radius * 2, radius * 2))
                psurf.set_colorkey((0, 0, 0))
                color = (200, 255, 150)
                for r in range(radius, 0, -1):
                    a = int(alpha * (1 - r / radius))
                    pygame.draw.circle(psurf, color, (radius, radius), r)
                psurf.set_alpha(alpha)
                surface.blit(psurf, (int(p["x"] - radius), int(p["y"] - radius)))

            elif self.particle_type == "leaf":
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                p["vx"] += math.sin(t + p["phase"]) * 5 * dt
                p["vy"] += math.sin(t * 0.5 + p["phase"]) * 3 * dt
                spin_angle = t * p["spin"] + p["phase"]

                if p["life"] <= 0:
                    self.particles.remove(p)
                    continue

                alpha = int(p["alpha"])
                size = p["size"]
                psurf = pygame.Surface((size + 1, size + 1))
                psurf.set_colorkey((0, 0, 0))
                # Leaf as a small rotated line/ellipse
                color = (180 + int(math.sin(p["phase"]) * 20),
                         140 + int(math.cos(p["phase"]) * 20),
                         80)
                # Draw a small rotated rectangle as leaf
                cx, cy = size // 2, size // 2
                pts = []
                for ang in [0, 90, 180, 270]:
                    rad = math.radians(ang + spin_angle * 30)
                    rx = math.cos(rad) * size // 2
                    ry = math.sin(rad) * size // 3
                    pts.append((cx + rx, cy + ry))
                pygame.draw.polygon(psurf, color, pts)
                psurf.set_alpha(alpha)
                surface.blit(psurf, (int(p["x"]), int(p["y"])))

    def update(self, obj):
        obj.depth = 9002
