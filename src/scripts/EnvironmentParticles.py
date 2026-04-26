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
                import scripts.Sounds as sounds
                sounds.play_blub_sound()
                self._ripples.append({
                    "x": obj.x, "y": obj.y,
                    "radius": 0,
                    "max_radius": random.uniform(22, 40),
                    "life": 0,
                    "max_life": random.uniform(0.8, 1.4),
                })

        elif not in_water and on_ground and speed > 15:
            self._sand_timer += dt
            if self._sand_timer > 0.04 and len(self._sand_particles) < 40:
                self._sand_timer = 0
                for _ in range(random.randint(1, 3)):
                    base = (200, 170, 120)
                    offset = random.randint(-30, 40)
                    cr = max(0, min(255, base[0] + offset))
                    cg = max(0, min(255, base[1] + offset))
                    cb = max(0, min(255, base[2] + offset))
                    self._sand_particles.append({
                        "x": obj.x + random.uniform(-6, 6),
                        "y": obj.y + random.uniform(-6, 6),
                        "z": 0,
                        "vz": random.uniform(8, 25),
                        "state": "up",
                        "rest_timer": 0,
                        "rest_duration": random.uniform(0.15, 0.4),
                        "size": random.choice([1, 1, 2]),
                        "cr": cr, "cg": cg, "cb": cb,
                    })

        # Update ripples
        for r in self._ripples[:]:
            r["life"] += dt
            r["radius"] = r["max_radius"] * (r["life"] / r["max_life"])
            if r["life"] >= r["max_life"]:
                self._ripples.remove(r)

        # Update sand particles — state machine: up → down → rest → done
        for p in self._sand_particles[:]:
            if p["state"] == "up":
                p["z"] += p["vz"] * dt
                p["vz"] -= 400 * dt  # gravity pulling down
                if p["vz"] <= 0:
                    p["state"] = "down"
            elif p["state"] == "down":
                p["z"] += p["vz"] * dt  # vz is negative, falling
                if p["z"] <= 0:
                    p["z"] = 0
                    p["state"] = "rest"
                    p["rest_timer"] = 0
            elif p["state"] == "rest":
                p["rest_timer"] += dt
                if p["rest_timer"] >= p["rest_duration"]:
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
            sy -= p["z"] * squash  # lift off ground squashed
            size = p["size"]
            sand_color = (p["cr"], p["cg"], p["cb"])

            # Fade out while resting on ground
            alpha = 255
            if p["state"] == "rest":
                alpha = int(200 * (1 - p["rest_timer"] / p["rest_duration"]))

            psurf = pygame.Surface((size + 1, size + 1))
            psurf.set_colorkey((0, 0, 0))
            pygame.draw.circle(psurf, sand_color, (size // 2 + 1, size // 2 + 1), size)
            psurf.set_alpha(alpha)
            surface.blit(psurf, (int(sx), int(sy)))
