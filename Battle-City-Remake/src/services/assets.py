import os
import pygame
import yaml

# шлях до папки з ресурсами (звідки запустиш run.py)
ASSETS_DIR = r"C:\Users\vlad\PycharmProjects\Battle-City-Remake\src\assets"



class ResourceManager:
    """
    Менеджер ресурсів: зчитує resources.yaml і надає методи для отримання зображень, звуків, шрифтів.
    Якщо файл відсутній — створює плейсхолдер (Surface із кольором).
    """

    def __init__(self, yaml_file: str = "resources.yaml"):
        self.yaml_path = os.path.join(ASSETS_DIR, yaml_file)
        self._data = {"sprites": {}, "sounds": {}, "fonts": {}}
        self._cache = {}
        self._load_yaml()

    # ------------------------------------
    def _load_yaml(self):
        if os.path.exists(self.yaml_path):
            with open(self.yaml_path, "r", encoding="utf-8") as f:
                self._data = yaml.safe_load(f) or self._data
        else:
            print(f"[assets] Warning: {self.yaml_path} not found. Using placeholders.")

    # ------------------------------------
    def _full(self, rel_path: str):
        """Отримати повний шлях до файлу."""
        return os.path.join(ASSETS_DIR, rel_path)

    # ------------------------------------
    def image(self, key: str, fallback_size=(32, 32), color=(200, 200, 200)) -> pygame.Surface:
        """Отримати Surface із resources.yaml або плейсхолдер."""
        if key in self._cache:
            return self._cache[key]

        surf = None
        info = self._data.get("sprites", {}).get(key)
        if info:
            path = self._full(info["file"])
            if os.path.exists(path):
                try:
                    surf = pygame.image.load(path).convert_alpha()
                except Exception:
                    surf = None

        if surf is None:
            surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
            surf.fill((*color, 255))

        self._cache[key] = surf
        return surf

    # ------------------------------------
    def sound(self, key: str):
        """Отримати звук (pygame.mixer.Sound)."""
        if key in self._cache:
            return self._cache[key]

        path_rel = self._data.get("sounds", {}).get(key)
        snd = None
        if path_rel:
            path = self._full(path_rel)
            if os.path.exists(path):
                try:
                    snd = pygame.mixer.Sound(path)
                except Exception:
                    snd = None

        self._cache[key] = snd
        return snd

    # ------------------------------------
    def font(self, key: str):
        """Отримати pygame.font.Font."""
        if key in self._cache:
            return self._cache[key]

        info = self._data.get("fonts", {}).get(key)
        if info:
            path = self._full(info.get("file", "")) if info.get("file") else None
            size = info.get("size", 24)
            try:
                font = pygame.font.Font(path if path and os.path.exists(path) else None, size)
            except Exception:
                font = pygame.font.Font(None, size)
        else:
            font = pygame.font.Font(None, 24)

        self._cache[key] = font
        return font
