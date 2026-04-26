import os
import pygame
from pygaminal.screen import Screen
from pygaminal.app import App


class DrawSprite:
    def __init__(self, image_path, scale=1.0, ground_from_top=0):
        self.image_path = image_path
        self.scale = scale
        self.ground_from_top = ground_from_top
        self._image = None
        self._depth_set = False

    def _load_image(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.join(script_dir, "..", "images")
        full_path = os.path.join(images_dir, self.image_path)
        try:
            img = pygame.image.load(full_path).convert_alpha()
            if self.scale != 1.0:
                w = int(img.get_width() * self.scale)
                h = int(img.get_height() * self.scale)
                img = pygame.transform.smoothscale(img, (w, h))
            self._image = img
        except pygame.error:
            self._image = None

    def _get_cam(self, obj):
        scene = App().get_current_scene()
        for other in scene.get_all_objects():
            cam_comps = other.get_components("scripts/Camera")
            if cam_comps:
                return cam_comps[0]
        return None

    def draw(self, obj):
        if self._image is None:
            self._load_image()
        if self._image is None:
            return

        # Set depth for Y-sorting (once, after image is loaded)
        if not self._depth_set and self.ground_from_top > 0:
            # ground_from_top pixels from image top = ground-contact point
            # bottom of image is at obj.y, so ground-contact y = obj.y - (img_h - ground_from_top)
            obj.depth = obj.y - (self._image.get_height() - self.ground_from_top)
            self._depth_set = True

        cam = self._get_cam(obj)
        if not cam:
            return

        sx, sy = cam.world_to_screen(obj.x, obj.y)
        rect = self._image.get_rect()
        # Anchor bottom-center of image at the object's world position
        screen_x = int(sx - rect.width // 2)
        screen_y = int(sy - rect.height)

        surface = Screen().surface
        surface.blit(self._image, (screen_x, screen_y))

    def update(self, obj):
        pass
