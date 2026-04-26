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

        from maps.town_map import WALLS, SPRITES

        for i, (x, y, w, t, a, c, h) in enumerate(WALLS):
            wall_obj = Object(x, y, name=f"wall_{i}", tags={"wall"}, depth=-1)
            wall_obj.add_component(ScriptComponent("scripts/Wall", (w, t, a, c, h)))
            scene.add_object(wall_obj)

        for i, sprite_data in enumerate(SPRITES):
            img_path, sx, sy, sw, st, sa, sh = sprite_data[:7]
            ground_from_top = sprite_data[7] if len(sprite_data) > 7 else 0

            # Visible sprite at visual position
            vis_obj = Object(sx, sy, name=f"sprite_{i}_vis", depth=sy)
            vis_obj.add_component(ScriptComponent(
                "scripts/DrawSprite", (img_path, 1.0, ground_from_top)
            ))
            scene.add_object(vis_obj)

            # Invisible wall shifted up so its bottom aligns with sprite base
            wall_y = sy - 28
            wall_obj = Object(sx, wall_y, name=f"sprite_{i}_wall", tags={"wall"}, depth=wall_y)
            wall_obj.add_component(ScriptComponent(
                "scripts/Wall", (sw, st, sa, "#00000000", sh)
            ))
            scene.add_object(wall_obj)

    def draw(self, obj):
        pass
