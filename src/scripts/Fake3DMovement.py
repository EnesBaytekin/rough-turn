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

    def _get_cam(self, obj):
        cam_comps = obj.get_components("scripts/Camera")
        return cam_comps[0] if cam_comps else None

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
        else:
            if inp.is_mouse_just_pressed(4):
                self.angle = min(90, self.angle + 5)
            if inp.is_mouse_just_pressed(5):
                self.angle = max(0, self.angle - 5)

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

    def draw(self, obj):
        pass
