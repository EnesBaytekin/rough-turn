from pygaminal.app import App
from pygaminal.input_manager import InputManager
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
        self._ball_radius = 12

    def _get_cam(self, obj):
        cam_comps = obj.get_components("scripts/Camera")
        return cam_comps[0] if cam_comps else None

    def _get_ball_radius(self, obj):
        dc = obj.get_components("scripts/DrawCircle")
        return dc[0].radius if dc else self._ball_radius

    def update(self, obj):
        inp = InputManager()
        dt = App().dt

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

            # Right-click cancels aim while holding left-click
            if inp.is_mouse_just_pressed(3):
                self._aim_cancelled = True

            if self._aim_cancelled:
                if inp.is_mouse_released(1):
                    self._aim_cancelled = False
                return

            if inp.is_mouse_released(1):
                mx = inp.get_mouse_x()
                my = inp.get_mouse_y()
                cam = self._get_cam(obj)
                wx, wy = cam.screen_to_world(mx, my) if cam else (mx, my)

                dx = obj.x - wx
                dy = obj.y - wy
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

        self._compute_depth(obj)

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
                new_speed = (vx * vx + vy * vy) ** 0.5
                if new_speed > 0:
                    self.dir_x = vx / new_speed
                    self.dir_y = vy / new_speed
                    self.h_speed = new_speed

        obj.x, obj.y = bx, by

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
            # Wall normal (perpendicular to length direction)
            nx = -sin(a)
            ny = cos(a)

            ht = wall.thickness / 2
            wcx, wcy = wob.x, wob.y

            # The wall has two long sides, offset by ±thickness/2 along the normal.
            # In 2.5D the side with higher Y is "closer to screen".
            # Pick the near side's center and measure ball relative to it.
            near_side_y = wcy + ny * ht
            far_side_y = wcy - ny * ht

            if abs(near_side_y - far_side_y) < 0.001:
                # Vertical wall – both sides same Y, y-sort is fine
                continue

            # near normal points from wall center toward the near (high-Y) side
            if ny > 0:
                nfx, nfy = nx, ny
            else:
                nfx, nfy = -nx, -ny

            near_cx = wcx + nfx * ht
            near_cy = wcy + nfy * ht

            # Signed distance from the near-side plane
            ball_side = (bx - near_cx) * nfx + (by - near_cy) * nfy

            if ball_side > 0:
                # Ball is even closer to screen than the near side → in front
                depth_val = max(depth_val, wcy + 1)
            else:
                # Ball is on the far side of the near plane → behind
                depth_val = min(depth_val, wcy - 1)

        obj.depth = depth_val

    def draw(self, obj):
        pass
