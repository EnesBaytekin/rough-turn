import pygame
import random
import os


_sounds_loaded = False
_stone_sounds = []
_blub_sounds = []


def _get_sound_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "sounds")


def init_sounds():
    global _sounds_loaded, _stone_sounds, _blub_sounds
    if _sounds_loaded:
        return
    _sounds_loaded = True

    sound_dir = _get_sound_dir()

    # Load stone collision sounds
    for name in ["stone1.mp3", "stone2.ogg", "stone3.ogg", "stone4.ogg"]:
        path = os.path.join(sound_dir, name)
        try:
            _stone_sounds.append(pygame.mixer.Sound(path))
        except Exception:
            pass

    # Load blub water sounds
    for name in ["blub1.mp3", "blub2.mp3"]:
        path = os.path.join(sound_dir, name)
        try:
            _blub_sounds.append(pygame.mixer.Sound(path))
        except Exception:
            pass


def play_stone_sound():
    if _stone_sounds:
        random.choice(_stone_sounds).play()


def play_blub_sound():
    if _blub_sounds:
        random.choice(_blub_sounds).play()


def start_music():
    from pygaminal.audio_manager import AudioManager
    path = os.path.join(_get_sound_dir(), "lofi.ogg")
    try:
        AudioManager().play_music(path, loop=True, volume=0.5)
    except Exception:
        pass
