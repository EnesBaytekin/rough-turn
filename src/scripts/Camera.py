from pygaminal.screen import Screen


class Camera:
    def __init__(self, smoothing=0.1):
        self.x = 0
        self.y = 0
        self.smoothing = smoothing

    def update(self, obj):
        screen = Screen()
        target_x = obj.x - screen.width // 2
        target_y = obj.y - screen.height // 2
        self.x += (target_x - self.x) * self.smoothing
        self.y += (target_y - self.y) * self.smoothing

    def draw(self, obj):
        pass

    def world_to_screen(self, wx, wy):
        return (wx - self.x, wy - self.y)

    def screen_to_world(self, sx, sy):
        return (sx + self.x, sy + self.y)
