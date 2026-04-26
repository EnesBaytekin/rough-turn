import pygame
import math
import random
from pygaminal.screen import Screen
from pygaminal.app import App


class DecorativeSprite:
    def __init__(self, decor_type, params=None):
        self.decor_type = decor_type
        self.params = params or {}
        self._seed = random.randint(0, 9999)
        self._time_offset = random.uniform(0, 100)

    def _get_cam(self, obj):
        scene = App().get_current_scene()
        for other in scene.get_all_objects():
            cam_comps = other.get_components("scripts/Camera")
            if cam_comps:
                return cam_comps[0]
        return None

    def draw(self, obj):
        surface = Screen().surface
        cam = self._get_cam(obj)
        if not cam:
            return

        sx, sy = cam.world_to_screen(obj.x, obj.y)
        # Cull if way off screen (with margin for tall objects)
        margin = 200
        if sx < -margin or sx > Screen().width + margin or sy < -margin or sy > Screen().height + margin:
            return

        t = App().now + self._time_offset

        draw_fn = {
            "tree": self._draw_tree,
            "lamppost": self._draw_lamppost,
            "statue": self._draw_statue,
            "bench": self._draw_bench,
        }.get(self.decor_type)

        if draw_fn:
            draw_fn(surface, sx, sy, t)

    def update(self, obj):
        pass

    def _draw_tree(self, surface, sx, sy, t):
        sway = math.sin(t * 1.5 + self._seed) * 2.5
        trunk_color = (90, 75, 55)
        foliage_color = self.params.get("color", (70, 120, 50))
        h = self.params.get("height", 50)

        # Trunk (proportional to height)
        trunk_w = max(4, h * 0.06)
        trunk_h = h * 0.35
        tx = sx + sway * 0.5
        ty = sy - h
        pygame.draw.rect(surface, trunk_color,
                         (tx - trunk_w // 2, ty, trunk_w, trunk_h))

        # Foliage layers (triangles)
        layers = 4
        for i in range(layers):
            layer_y = ty - i * h * 0.17
            layer_c = (
                max(0, foliage_color[0] - i * 6),
                max(0, foliage_color[1] - i * 4),
                max(0, foliage_color[2] - i * 3),
            )
            bw = (h * 0.30) * (1 - i * 0.12) + sway * 1.0
            x0 = tx + sway * (1 - i * 0.15)
            pts = [
                (x0, layer_y - h * 0.18),
                (x0 - bw, layer_y + h * 0.05),
                (x0 + bw, layer_y + h * 0.05),
            ]
            pygame.draw.polygon(surface, layer_c, pts)

        # Ground shadow
        shadow_r = h * 0.2
        shadow_surf = pygame.Surface((shadow_r * 2, shadow_r * 2 // 3))
        shadow_surf.set_colorkey((0, 0, 0))
        pygame.draw.ellipse(shadow_surf, (30, 25, 20, 60),
                            (0, 0, shadow_r * 2, shadow_r * 2 // 3))
        shadow_surf.set_alpha(40)
        surface.blit(shadow_surf, (sx - shadow_r, sy - shadow_r // 3))

    def _draw_lamppost(self, surface, sx, sy, t):
        h = self.params.get("height", 50)

        # Post
        post_w = max(2, h * 0.05)
        post_h = h * 0.75
        post_color = (55, 55, 55)
        pygame.draw.rect(surface, post_color,
                         (sx - post_w // 2, sy - post_h, post_w, post_h))

        # Light housing
        housing_color = (70, 65, 55)
        housing_w = h * 0.12
        housing_h = h * 0.06
        pygame.draw.rect(surface, housing_color,
                         (sx - housing_w // 2, sy - post_h - housing_h, housing_w, housing_h))

        # Glow
        glow_radius = int(h * 0.15 + math.sin(t * 2.5) * 3)
        glow_alpha = 120 + int(math.sin(t * 2.5) * 40)
        glow_center = (sx, sy - post_h - housing_h // 2)
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2))
        glow_surf.set_colorkey((0, 0, 0))
        for r in range(glow_radius, 0, -1):
            a = int(glow_alpha * (1 - r / glow_radius))
            color = (255, 200, 120, min(255, a))
            pygame.draw.circle(glow_surf, color[:3],
                               (glow_radius, glow_radius), r)
        glow_surf.set_alpha(glow_alpha)
        surface.blit(glow_surf,
                     (glow_center[0] - glow_radius, glow_center[1] - glow_radius))

        # Light cone
        cone_w = h * 0.4
        cone_h = h * 0.2
        cone_surf = pygame.Surface((cone_w, cone_h))
        cone_surf.set_colorkey((0, 0, 0))
        cone_color = (255, 200, 120)
        pts = [(cone_w / 2, 0), (0, cone_h), (cone_w, cone_h)]
        pygame.draw.polygon(cone_surf, cone_color, pts)
        cone_surf.set_alpha(15)
        surface.blit(cone_surf, (glow_center[0] - cone_w // 2, glow_center[1]))

    def _draw_statue(self, surface, sx, sy, t):
        h = self.params.get("height", 50)

        # Pedestal
        pedestal_color = (110, 105, 100)
        pw = h * 0.15
        ph = h * 0.08
        pygame.draw.rect(surface, pedestal_color,
                         (sx - pw // 2, sy - ph, pw, ph))

        # Pedestal top trim
        trim_color = (130, 125, 120)
        tw = h * 0.14
        th = h * 0.03
        pygame.draw.rect(surface, trim_color,
                         (sx - tw // 2, sy - ph - th, tw, th))

        # Figure
        figure_color = (100, 95, 90)
        body_w = h * 0.08
        body_h = h * 0.2
        pygame.draw.ellipse(surface, figure_color,
                           (sx - body_w // 2, sy - ph - th - body_h, body_w, body_h))

        # Head
        head_r = h * 0.05
        pygame.draw.circle(surface, figure_color,
                          (sx, sy - ph - th - body_h - head_r), head_r)

        # Arms
        arm_color = (90, 85, 80)
        arm_len = h * 0.08
        pygame.draw.line(surface, arm_color,
                        (sx - body_w // 2, sy - ph - th - body_h * 0.6),
                        (sx - body_w // 2 - arm_len, sy - ph - th - body_h * 0.3),
                        1)
        pygame.draw.line(surface, arm_color,
                        (sx + body_w // 2, sy - ph - th - body_h * 0.6),
                        (sx + body_w // 2 + arm_len, sy - ph - th - body_h * 0.3),
                        1)

    def _draw_bench(self, surface, sx, sy, t):
        h = self.params.get("height", 20)

        bench_color = (100, 75, 50)
        metal_color = (60, 60, 60)

        bw = h * 0.6
        bh = h * 0.12

        # Seat
        pygame.draw.rect(surface, bench_color,
                         (sx - bw // 2, sy - bh, bw, bh))

        # Backrest
        back_h = h * 0.2
        pygame.draw.rect(surface, bench_color,
                         (sx - bw // 2, sy - bh - back_h, bw, back_h))

        # Legs
        leg_h = h * 0.08
        pygame.draw.rect(surface, metal_color,
                         (sx - bw // 2 + 1, sy, 1, leg_h))
        pygame.draw.rect(surface, metal_color,
                         (sx + bw // 2 - 2, sy, 1, leg_h))

        # Armrests
        pygame.draw.rect(surface, metal_color,
                         (sx - bw // 2, sy - bh - back_h, 1, back_h + bh))
        pygame.draw.rect(surface, metal_color,
                         (sx + bw // 2 - 1, sy - bh - back_h, 1, back_h + bh))
