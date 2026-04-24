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

    def update(self, obj):
        inp = InputManager()
        dt = App().dt

        if self.moving:
            # Apply friction to scalar speed
            self.speed = max(0, self.speed - self.friction * dt)

            # Move in fixed direction
            obj.x += self.dir_x * self.speed * dt
            obj.y += self.dir_y * self.speed * dt

            # Check if stopped
            if self.speed == 0:
                self.moving = False
        else:
            # Mouse click to launch
            if inp.is_mouse_just_pressed(1):
                mx = inp.get_mouse_x()
                my = inp.get_mouse_y()
                dx = obj.x - mx
                dy = obj.y - my
                dist = (dx * dx + dy * dy) ** 0.5
                if dist > 0:
                    self.dir_x = dx / dist
                    self.dir_y = dy / dist
                    capped = min(dist, self.max_aim_dist)
                    self.speed = max(self.min_launch_speed, (capped / self.max_aim_dist) * self.max_launch_speed)
                    self.moving = True

    def draw(self, obj):
        pass
