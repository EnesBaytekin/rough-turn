import pygame
import random
from pygaminal.app import App
from pygaminal.input_manager import InputManager
from pygaminal.screen import Screen
from math import cos, sin, radians


class Fake3DMovement:
    def __init__(self, max_launch_speed=200, friction=150, max_aim_dist=80, min_launch_speed=60, gravity=600, air_friction=50, vertical_force=200):
        self.max_launch_speed = max_launch_speed
        self.friction = friction
        self.max_aim_dist = max_aim_dist
        self.min_launch_speed = min_launch_speed
        self.gravity = gravity
        self.air_friction = air_friction
        self.vertical_force = vertical_force
        self.h_speed = 0
        self.v_speed = 0
        self.dir_x = 0
        self.dir_y = 0
        self.z = 0
        self.angle = 45
        self.moving = False
        self._aim_cancelled = False
        self._aim_start_sx = None
        self._aim_start_sy = None
        self._aim_start_wx = None
        self._aim_start_wy = None
        self._ball_radius = 12
        # Collision debris particles
        self._collision_particles = []
        self._collision_cooldown = 0.0
        # Deposit mechanic
        self._deposit_cooldown = 0.0
        self._deposit_timer = None

    def _get_cam(self, obj):
        cam_comps = obj.get_components("scripts/Camera")
        return cam_comps[0] if cam_comps else None

    def _get_ball_radius(self, obj):
        for comp_type in ("scripts/DrawCircle", "scripts/DrawRock"):
            comps = obj.get_components(comp_type)
            if comps:
                return comps[0].radius
        return self._ball_radius

    def _get_rock_colors(self, obj):
        """Get DrawRock's 3 colors (dark, main, light) for particles."""
        rock_comps = obj.get_components("scripts/DrawRock")
        if rock_comps:
            rock = rock_comps[0]
            return [
                (rock._dark_color.r, rock._dark_color.g, rock._dark_color.b),
                (rock.color.r, rock.color.g, rock.color.b),
                (rock._light_color.r, rock._light_color.g, rock._light_color.b),
            ]
        return [(160, 150, 140)]

    def _spawn_collision_particles(self, obj, cx, cy, ball_r):
        """Spawn small debris at collision point — only falls down."""
        count = random.randint(4, 7)
        colors = self._get_rock_colors(obj)
        for _ in range(count):
            size = random.choices([1, 2, 3], weights=[4, 3, 1])[0]
            self._collision_particles.append({
                "x": cx + random.uniform(-2, 2),
                "y": cy + random.uniform(-2, 2),
                "z": self.z + ball_r,
                "vx": random.uniform(-25, 25),
                "vy": random.uniform(-25, 25),
                "vz": random.uniform(-40, -100),
                "life": random.uniform(0.6, 1.2),
                "size": size,
                "color": random.choice(colors),
            })

    def update(self, obj):
        inp = InputManager()
        dt = App().dt

        # Update cooldowns
        if self._collision_cooldown > 0:
            self._collision_cooldown -= dt
        if self._deposit_cooldown > 0:
            self._deposit_cooldown -= dt

        if self.moving:
            drag = self.air_friction if self.z > 0 else self.friction
            self.h_speed = max(0, self.h_speed - drag * dt)
            obj.x += self.dir_x * self.h_speed * dt
            obj.y += self.dir_y * self.h_speed * dt

            self.v_speed -= self.gravity * dt
            self.z += self.v_speed * dt
            if self.z < 0:
                self.z = 0
                self.v_speed = 0

            if self.h_speed == 0 and self.z == 0:
                self.moving = False

            self._check_wall_collisions(obj)
        else:

            if inp.is_mouse_just_pressed(4):
                self.angle = min(90, self.angle + 5)
            if inp.is_mouse_just_pressed(5):
                self.angle = max(0, self.angle - 5)

            # Left click: record aim start point
            if inp.is_mouse_just_pressed(1):
                self._aim_cancelled = False
                self._aim_start_sx = inp.get_mouse_x()
                self._aim_start_sy = inp.get_mouse_y()
                cam = self._get_cam(obj)
                self._aim_start_wx, self._aim_start_wy = (
                    cam.screen_to_world(self._aim_start_sx, self._aim_start_sy)
                    if cam else (self._aim_start_sx, self._aim_start_sy)
                )

            # Right-click cancels aim while holding left-click
            if inp.is_mouse_just_pressed(3) and inp.is_mouse_pressed(1):
                self._aim_cancelled = True
                self._aim_start_sx = None

            if self._aim_cancelled:
                if inp.is_mouse_released(1):
                    self._aim_cancelled = False
                return

            if inp.is_mouse_released(1):
                if self._aim_start_sx is not None:
                    mx = inp.get_mouse_x()
                    my = inp.get_mouse_y()
                    cam = self._get_cam(obj)
                    wx, wy = cam.screen_to_world(mx, my) if cam else (mx, my)

                    dx = self._aim_start_wx - wx
                    dy = self._aim_start_wy - wy
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist > 0:
                        self.dir_x = dx / dist
                        self.dir_y = dy / dist
                        capped = min(dist, self.max_aim_dist)
                        total = max(self.min_launch_speed, (capped / self.max_aim_dist) * self.max_launch_speed)
                        a = radians(self.angle)
                        self.h_speed = total * cos(a)
                        self.v_speed = self.vertical_force * sin(a)
                        self.z = 0
                        self.moving = True

                self._aim_start_sx = None

        # --- Zone check: deposit smooth rock in destination area ---
        self._check_deposit_zone(obj)

        self._compute_depth(obj)

        # Update collision particles
        self._update_particles(obj)

    def _check_wall_collisions(self, obj):
        scene = App().get_current_scene()
        wall_objs = scene.get_objects_by_tag("wall")
        if not wall_objs:
            return

        r = self._get_ball_radius(obj)
        bx, by = obj.x, obj.y

        for wob in wall_objs:
            wall_comps = wob.get_components("scripts/Wall")
            if not wall_comps:
                continue
            wall = wall_comps[0]
            ht = wall.thickness / 2

            if self.z > wall.height:
                continue

            a = radians(wall.angle)
            hw = wall.width / 2
            ca, sa = cos(a), sin(a)

            sx = wob.x - ca * hw
            sy = wob.y - sa * hw
            ex = wob.x + ca * hw
            ey = wob.y + sa * hw

            sdx = ex - sx
            sdy = ey - sy
            seg_len = (sdx * sdx + sdy * sdy) ** 0.5
            if seg_len < 0.001:
                continue

            ux = sdx / seg_len
            uy = sdy / seg_len

            t = (bx - sx) * ux + (by - sy) * uy
            t = max(0, min(seg_len, t))
            px = sx + ux * t
            py = sy + uy * t

            dx = bx - px
            dy = by - py
            dist = (dx * dx + dy * dy) ** 0.5

            min_dist = r + ht
            if dist >= min_dist:
                continue

            if dist < 0.001:
                nx = -sa
                ny = ca
                if nx * self.dir_x + ny * self.dir_y > 0:
                    nx, ny = -nx, -ny
            else:
                nx = dx / dist
                ny = dy / dist

            pen = min_dist - dist
            bx += nx * pen
            by += ny * pen

            vx = self.h_speed * self.dir_x
            vy = self.h_speed * self.dir_y
            vdotn = vx * nx + vy * ny
            if vdotn < 0:
                vx -= 2 * vdotn * nx
                vy -= 2 * vdotn * ny
                # Slightly inelastic: lose a little speed on bounce
                vx *= 0.92
                vy *= 0.92
                new_speed = (vx * vx + vy * vy) ** 0.5
                if new_speed > 0:
                    self.dir_x = vx / new_speed
                    self.dir_y = vy / new_speed
                    self.h_speed = new_speed

                # --- Spawn particles & smooth rock ---
                if self._collision_cooldown <= 0:
                    # Surface contact point (wall surface, not center line)
                    cx = px + nx * ht
                    cy = py + ny * ht
                    self._spawn_collision_particles(obj, cx, cy, r)
                    self._collision_cooldown = 0.12

                    # Gradually smooth the rock on each collision
                    rock_comps = obj.get_components("scripts/DrawRock")
                    if rock_comps:
                        rock = rock_comps[0]
                        if rock.roughness > 0:
                            rock.roughness = max(0.0, rock.roughness - 0.015)
                            rock._regenerate()
                            import scripts.DrawRock as dr
                            dr.slider_roughness = rock.roughness

        obj.x, obj.y = bx, by

    def _update_particles(self, obj):
        dt = App().dt
        for p in self._collision_particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["z"] += p["vz"] * dt
            p["vz"] -= self.gravity * dt
            if p["z"] < 0:
                p["z"] = 0
                p["vx"] *= 0.9
                p["vy"] *= 0.9
            p["life"] -= dt
        self._collision_particles = [p for p in self._collision_particles if p["life"] > 0]

    def _do_deposit(self, obj):
        """Add sphere to dest, teleport to random source point, reset roughness."""
        import scripts.DecorativeRocks as dr
        import scripts.DrawRock as drawrock

        # Leave a perfect sphere at deposit position
        dest = getattr(dr, 'dest_area', None)
        if dest is not None:
            dest.add_rock(obj.x, obj.y)

        # Random spawn within source zone
        sx1, sy1, sx2, sy2 = getattr(dr, '_source_zone', (30, 600, 280, 750))
        obj.x = random.uniform(sx1 + 10, sx2 - 10)
        obj.y = random.uniform(sy1 + 10, sy2 - 10)
        self.moving = False
        self.h_speed = 0
        self.v_speed = 0
        self.z = 0
        drawrock.slider_roughness = 0.6
        drawrock.deposit_progress = 0.0
        self._deposit_cooldown = 3.0

        # Visual flash
        import scripts.DrawOverlay as dover
        dover.deposit_flash = 1.0

    def _check_deposit_zone(self, obj):
        dt = App().dt
        if self._deposit_cooldown > 0:
            self._deposit_timer = None
            import scripts.DrawRock as drawrock
            drawrock.deposit_progress = 0.0
            return

        import scripts.DecorativeRocks as dr
        import scripts.DrawRock as drawrock

        x1, y1, x2, y2 = getattr(dr, '_dest_zone', (0, 0, 0, 0))
        in_zone = (x1 <= obj.x <= x2 and y1 <= obj.y <= y2)
        roughness = getattr(drawrock, 'slider_roughness', 1.0)
        smooth = (roughness is not None and roughness <= 0.001)

        if in_zone and smooth:
            if self._deposit_timer is None:
                self._deposit_timer = 3.0
            self._deposit_timer -= dt
            drawrock.deposit_progress = max(0.0, 1.0 - self._deposit_timer / 3.0)

            if self._deposit_timer <= 0:
                self._do_deposit(obj)
        else:
            self._deposit_timer = None
            drawrock.deposit_progress = 0.0

    def _draw_particles(self, obj):
        if not self._collision_particles:
            return
        surface = Screen().surface
        cam = self._get_cam(obj)
        for p in self._collision_particles:
            sx, sy = cam.world_to_screen(p["x"], p["y"]) if cam else (p["x"], p["y"])
            sy -= p["z"]
            r, g, b = p["color"]
            size = p["size"]
            psurf = pygame.Surface((size, size))
            psurf.fill((r, g, b))
            surface.blit(psurf, (int(sx - size // 2), int(sy - size // 2)))

    def _compute_depth(self, obj):
        scene = App().get_current_scene()
        wall_objs = scene.get_objects_by_tag("wall")
        if not wall_objs:
            obj.depth = obj.y
            return

        bx, by = obj.x, obj.y
        depth_val = by

        for wob in wall_objs:
            wall_comps = wob.get_components("scripts/Wall")
            if not wall_comps:
                continue
            wall = wall_comps[0]

            a = radians(wall.angle)
            ca, sa = cos(a), sin(a)
            # Perpendicular normal to wall length
            nx = -sa
            ny = ca

            if abs(ny) < 0.001:
                # Vertical wall (parallel to Y) — Y-sort unaffected
                continue

            hw = wall.width / 2
            ht = wall.thickness / 2

            # Wall center line segment
            sx = wob.x - ca * hw
            sy = wob.y - sa * hw
            ex = wob.x + ca * hw
            ey = wob.y + sa * hw

            # Project rock onto segment to find closest point on center line
            sdx = ex - sx
            sdy = ey - sy
            seg_len_2 = sdx * sdx + sdy * sdy

            if seg_len_2 < 0.001:
                proj_x, proj_y = sx, sy
            else:
                t = ((bx - sx) * sdx + (by - sy) * sdy) / seg_len_2
                t = max(0, min(1, t))
                proj_x = sx + t * sdx
                proj_y = sy + t * sdy

            # Perpendicular distance from rock to center line at projected point
            perp_dist = (bx - proj_x) * nx + (by - proj_y) * ny

            # Clamp to wall surface and get surface Y
            clamped_dist = max(-ht, min(ht, perp_dist))
            surface_y = proj_y + clamped_dist * ny

            # Compare rock Y to surface Y (higher Y = closer to screen)
            if by > surface_y:
                depth_val = max(depth_val, wob.y + 1)
            elif by < surface_y:
                depth_val = min(depth_val, wob.y - 1)

        obj.depth = depth_val

    def draw(self, obj):
        self._draw_particles(obj)
