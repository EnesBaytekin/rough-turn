import pygame
import math
import random
from pygaminal.screen import Screen
from pygaminal.app import App


class EnvironmentParticles:
    def __init__(self, coast_x=500, coast_y=800, coast_angle=-45):
        self.coast_x = coast_x
        self.coast_y = coast_y
        self.coast_angle = coast_angle
        self._ripples = []
        self._sand_particles = []
        self._ripple_timer = 0
        self._sand_timer = 0
        self._initialized = False

    def _get_cam(self, obj):
        scene = App().get_current_scene()
        for other in scene.get_all_objects():
            cam_comps = other.get_components("scripts/Camera")
            if cam_comps:
                return cam_comps[0]
        return None

    def _is_in_water(self, x, y):
        """Check if a world point is on the sea side of the coastline."""
        ca = math.radians(self.coast_angle)
        na = ca + math.pi / 2  # sea normal
        ndx = math.cos(na)
        ndy = math.sin(na)
        dist = (x - self.coast_x) * ndx + (y - self.coast_y) * ndy
        return dist >= -3  # small buffer at shoreline

    def update(self, obj):
        if not self._initialized:
            self._last_x = obj.x
            self._last_y = obj.y
            self._initialized = True
            return

        dt = App().dt
        if dt <= 0:
            return

        dx = obj.x - self._last_x
        dy = obj.y - self._last_y
        speed = math.sqrt(dx * dx + dy * dy) / dt
        self._last_x, self._last_y = obj.x, obj.y

        # Get height above ground from Fake3DMovement
        fm_comps = obj.get_components("scripts/Fake3DMovement")
        on_ground = True
        if fm_comps:
            on_ground = fm_comps[0].z <= 0.5

        in_water = self._is_in_water(obj.x, obj.y)

        if in_water and on_ground and speed > 5:
            self._ripple_timer += dt
            if self._ripple_timer > 0.2 and len(self._ripples) < 15:
                self._ripple_timer = 0
                self._ripples.append({
                    "x": obj.x, "y": obj.y,
                    "radius": 0,
                    "max_radius": random.uniform(22, 40),
                    "life": 0,
                    "max_life": random.uniform(0.8, 1.4),
                })

        elif not in_water and on_ground and speed > 15:
            self._sand_timer += dt
            if self._sand_timer > 0.04 and len(self._sand_particles) < 30:
                self._sand_timer = 0
                angle = math.atan2(dy, dx)
                for _ in range(random.randint(1, 2)):
                    spread = random.uniform(-0.8, 0.8)
                    p_angle = angle + math.pi + spread
                    p_speed = random.uniform(15, 50)
                    self._sand_particles.append({
                        "x": obj.x + random.uniform(-4, 4),
                        "y": obj.y + random.uniform(-4, 4),
                        "vx": math.cos(p_angle) * p_speed + random.uniform(-15, 15),
                        "vy": math.sin(p_angle) * p_speed + random.uniform(-30, -10),
                        "life": 0,
                        "max_life": random.uniform(0.2, 0.6),
                        "size": random.choice([1, 1, 2]),
                    })

        # Update ripples
        for r in self._ripples[:]:
            r["life"] += dt
            r["radius"] = r["max_radius"] * (r["life"] / r["max_life"])
            if r["life"] >= r["max_life"]:
                self._ripples.remove(r)

        # Update sand particles
        for p in self._sand_particles[:]:
            p["life"] += dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 200 * dt  # gravity
            if p["life"] >= p["max_life"]:
                self._sand_particles.remove(p)

    def draw(self, obj):
        surface = Screen().surface
        cam = self._get_cam(obj)
        if not cam:
            return

        squash = 0.4  # match shadow squash

        # Draw ripples
        for r in self._ripples:
            sx, sy = cam.world_to_screen(r["x"], r["y"])
            progress = r["life"] / r["max_life"]
            radius = int(r["radius"])
            if radius < 1:
                continue

            alpha = int(80 * (1 - progress))
            ew = radius * 2 + 2
            eh = max(2, int(radius * 2 * squash) + 2)
            surf = pygame.Surface((ew, eh), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (180, 220, 240, alpha),
                                (0, 0, ew - 1, eh - 1), 1)
            surface.blit(surf, (int(sx) - ew // 2, int(sy) - eh // 2))

        # Draw sand particles
        for p in self._sand_particles:
            sx, sy = cam.world_to_screen(p["x"], p["y"])
            progress = p["life"] / p["max_life"]
            alpha = int(200 * (1 - progress))
            size = p["size"]
            c = max(0, 200 - int(progress * 80))
            sand_color = (c, max(0, c - 30), max(0, c - 60))

            psurf = pygame.Surface((size + 1, size + 1))
            psurf.set_colorkey((0, 0, 0))
            pygame.draw.circle(psurf, sand_color, (size // 2 + 1, size // 2 + 1), size)
            psurf.set_alpha(alpha)
            surface.blit(psurf, (int(sx), int(sy)))
