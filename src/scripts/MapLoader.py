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

        from maps.town_map import WALLS, SPRITES, SOURCE_ROCKS, DEST_ROCKS, SOURCE_ZONE, DEST_ZONE, RESPAWN_POINT, DEPOSIT_CENTER

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

        # --- Decorative rock areas ---
        import scripts.DecorativeRocks as dr

        src_obj = Object(0, 0, name="decorative_rocks_source", depth=-1)
        src_obj.add_component(ScriptComponent(
            "scripts/DecorativeRocks", (SOURCE_ROCKS, 0.6, 12, "#646464")
        ))
        scene.add_object(src_obj)
        dr.source_area = src_obj.get_components("scripts/DecorativeRocks")[0]

        dest_obj = Object(0, 0, name="decorative_rocks_dest", depth=-1)
        dest_obj.add_component(ScriptComponent(
            "scripts/DecorativeRocks", (DEST_ROCKS, 0.0, 12, "#646464", DEPOSIT_CENTER)
        ))
        scene.add_object(dest_obj)
        dr.dest_area = dest_obj.get_components("scripts/DecorativeRocks")[0]

        # Store zone info for Fake3DMovement to use
        dr._source_zone = SOURCE_ZONE
        dr._dest_zone = DEST_ZONE
        dr._respawn_point = RESPAWN_POINT

    def draw(self, obj):
        pass
