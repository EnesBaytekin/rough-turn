from pygaminal.app import App
from pygaminal.input_manager import InputManager


class Fake3DMovement:
    def __init__(self, max_launch_speed=200, friction=150, max_aim_dist=80, min_launch_speed=60):
        self.max_launch_speed = max_launch_speed
        self.friction = friction
        self.max_aim_dist = max_aim_dist
        self.min_launch_speed = min_launch_speed
        self.speed = 0
        self.dir_x = 0
        self.dir_y = 0
        self.z = 0
        self.moving = False

    def _get_cam(self, obj):
        cam_comps = obj.get_components("scripts/Camera")
        return cam_comps[0] if cam_comps else None

    def update(self, obj):
        inp = InputManager()
        dt = App().dt

        if self.moving:
            self.speed = max(0, self.speed - self.friction * dt)
            obj.x += self.dir_x * self.speed * dt
            obj.y += self.dir_y * self.speed * dt
            if self.speed == 0:
                self.moving = False
        else:
            if inp.is_mouse_just_pressed(1):
                mx = inp.get_mouse_x()
                my = inp.get_mouse_y()

                # Screen → world for direction calc
                cam = self._get_cam(obj)
                wx, wy = cam.screen_to_world(mx, my) if cam else (mx, my)

                dx = obj.x - wx
                dy = obj.y - wy
                dist = (dx * dx + dy * dy) ** 0.5
                if dist > 0:
                    self.dir_x = dx / dist
                    self.dir_y = dy / dist
                    capped = min(dist, self.max_aim_dist)
                    self.speed = max(self.min_launch_speed, (capped / self.max_aim_dist) * self.max_launch_speed)
                    self.moving = True

    def draw(self, obj):
        pass
