from pygaminal.app import App
from pygaminal.input_manager import InputManager


class Fake3DMovement:
    def __init__(self, launch_force=300, friction=150):
        self.launch_force = launch_force
        self.friction = friction
        self.velocity_x = 0
        self.velocity_y = 0
        self.z = 0
        self.moving = False

    def update(self, obj):
        inp = InputManager()
        dt = App().dt

        if self.moving:
            # Apply friction to X
            if self.velocity_x != 0:
                if self.velocity_x > 0:
                    self.velocity_x = max(0, self.velocity_x - self.friction * dt)
                else:
                    self.velocity_x = min(0, self.velocity_x + self.friction * dt)

            # Apply friction to Y
            if self.velocity_y != 0:
                if self.velocity_y > 0:
                    self.velocity_y = max(0, self.velocity_y - self.friction * dt)
                else:
                    self.velocity_y = min(0, self.velocity_y + self.friction * dt)

            # Apply movement
            obj.x += self.velocity_x * dt
            obj.y += self.velocity_y * dt

            # Check if fully stopped
            if self.velocity_x == 0 and self.velocity_y == 0:
                self.moving = False
        else:
            # Mouse click to launch toward aim direction
            if inp.is_mouse_just_pressed(1):
                mx = inp.get_mouse_x()
                my = inp.get_mouse_y()
                dx = obj.x - mx
                dy = obj.y - my
                dist = (dx * dx + dy * dy) ** 0.5
                if dist > 0:
                    self.velocity_x = (dx / dist) * self.launch_force
                    self.velocity_y = (dy / dist) * self.launch_force
                    self.moving = True

    def draw(self, obj):
        pass
