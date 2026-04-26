import pygame
from pygaminal.app import App
from pygaminal.object import Object
from pygaminal.script_component import ScriptComponent


class MapLoader:
    def __init__(self):
        self._loaded = False

    def update(self, obj):
        if self._loaded:
            return
        self._loaded = True

        scene = App().get_current_scene()
        if not scene:
            return

        from maps.town_map import (
            WALLS,
            DECORATIONS,
            DECOR_WALL_SIZES,
            DECOR_WALL_COLORS,
            DECOR_WALL_HEIGHTS,
        )

        # Create wall objects
        for i, (x, y, w, t, a, c, h) in enumerate(WALLS):
            wall_obj = Object(x, y, name=f"wall_{i}", tags={"wall"}, depth=-1)
            wall_obj.add_component(ScriptComponent("scripts/Wall", (w, t, a, c, h)))
            scene.add_object(wall_obj)

        # Create decoration objects (wall + decorative sprite)
        for i, (typ, dx, dy, params) in enumerate(DECORATIONS):
            wall_size = DECOR_WALL_SIZES.get(typ, (8, 4, 0))
            wall_color = DECOR_WALL_COLORS.get(typ, "#8A7A6A")
            wall_height = DECOR_WALL_HEIGHTS.get(typ, 15)

            decor_obj = Object(dx, dy, name=f"{typ}_{i}", tags={"wall"}, depth=dy)
            decor_obj.add_component(ScriptComponent(
                "scripts/Wall",
                (wall_size[0], wall_size[1], wall_size[2], wall_color, wall_height),
            ))
            decor_obj.add_component(ScriptComponent(
                "scripts/DecorativeSprite",
                (typ, params),
            ))
            scene.add_object(decor_obj)

    def draw(self, obj):
        pass
