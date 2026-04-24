import pygame
from pygaminal.app import App
from pygaminal.input_manager import InputManager


class Fake3DMovement:
    def __init__(self, speed=100, jump_force=180, gravity=-500):
        self.speed = speed
        self.jump_force = jump_force
        self.gravity = gravity
        self.velocity_z = 0
        self.z = 0

    def update(self, obj):
        app = App()
        inp = InputManager()
        dt = app.dt

        # Horizontal movement (WASD)
        dx = 0
        dy_world = 0

        if inp.is_pressed(pygame.K_a):
            dx -= self.speed * dt
        if inp.is_pressed(pygame.K_d):
            dx += self.speed * dt
        if inp.is_pressed(pygame.K_w):
            dy_world -= self.speed * dt
        if inp.is_pressed(pygame.K_s):
            dy_world += self.speed * dt

        # Jump
        if inp.is_pressed(pygame.K_SPACE) and self.z == 0:
            self.velocity_z = self.jump_force

        # Gravity
        self.velocity_z += self.gravity * dt
        self.z += self.velocity_z * dt
        if self.z < 0:
            self.z = 0
            self.velocity_z = 0

        # Apply to world coordinates
        obj.x += dx
        obj.y += dy_world

    def draw(self, obj):
        pass
