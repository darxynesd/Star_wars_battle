import pygame


class AudioManager:
    def __init__(self, assets, sfx_volume=0.7, music_volume=0.5, max_channels=8):
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(max_channels)
        except Exception:
            print("[audio] mixer init failed; sounds disabled")
        self.assets = assets
        self.sfx_volume = sfx_volume
        self.music_volume = music_volume

    def play_sfx(self, key: str):
        snd = self.assets.sound(key)
        if snd:
            snd.set_volume(self.sfx_volume)
            snd.play()

    def play_music(self, key: str, loops=-1):
        path_rel = self.assets._data.get("sounds", {}).get(key)
        if not path_rel:
            return
        path = self.assets._full(path_rel)
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops)
        except Exception:
            pass
