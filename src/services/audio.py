"""
Відтворення SFX і музики, глобальна гучність, одночасні канали. Маршрутизація подій зі звуком (наприклад, подія «HIT_STEEL» → звук стіни).
"""
class Audio:
    def __init__(self):
        self.enabled = True

    def play_sfx(self, key: str):
        # заглушка; згодом мапи ключ->wav
        if self.enabled:
            pass
