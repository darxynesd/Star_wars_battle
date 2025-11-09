# Tank Game Menu — Pygame single-file demo (~500 lines)
# Features:
# - Animated main menu (hover + click effects)
# - Scenes: Main, Settings (resolution, volume, fullscreen), Controls (rebind keys), Help, Credits, Dummy Game
# - UI widgets: Button, Toggle, Slider, Dropdown
# - Simple transitions, sound feedback
# - Settings persist to settings.json
# ---------------------------------------------------------------
import os
import sys
import json
import math
import time
import random
import pygame
from pygame import mixer

# -------------------------- UTILITIES --------------------------
APP_TITLE = "Tank Game — Menu Demo"
SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "width": 1280,
    "height": 720,
    "fullscreen": False,
    "music_volume": 0.5,
    "sfx_volume": 0.7,
    "controls": {
        "move_up": pygame.K_w,
        "move_down": pygame.K_s,
        "move_left": pygame.K_a,
        "move_right": pygame.K_d,
        "fire": pygame.K_SPACE,
        "pause": pygame.K_ESCAPE,
    }
}

RESOLUTIONS = [
    (1280, 720), (1366, 768), (1600, 900), (1920, 1080),
    (1024, 576), (1600, 1200), (2560, 1440)
]

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
if not os.path.isdir(ASSETS_DIR):
    os.makedirs(ASSETS_DIR, exist_ok=True)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Backward compatibility
            for k, v in DEFAULT_SETTINGS.items():
                if k not in data:
                    data[k] = v
            if "controls" in data:
                for ck, cv in DEFAULT_SETTINGS["controls"].items():
                    if ck not in data["controls"]:
                        data["controls"][ck] = cv
            return data
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(s):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
    except Exception as e:
        print("Failed to save settings:", e)


# -------------------------- INIT --------------------------
pygame.init()
pygame.mixer.init()
pygame.display.set_caption(APP_TITLE)

settings = load_settings()

flags = pygame.DOUBLEBUF
if settings.get("fullscreen"):
    flags |= pygame.FULLSCREEN
SCREEN = pygame.display.set_mode((settings["width"], settings["height"]), flags)
CLOCK = pygame.time.Clock()

# Fonts
try:
    UI_FONT = pygame.font.Font(pygame.font.match_font("verdana,arial,dejavusans"), 24)
    SMALL_FONT = pygame.font.Font(pygame.font.match_font("verdana,arial,dejavusans"), 18)
    BIG_FONT = pygame.font.Font(pygame.font.match_font("verdana,arial,dejavusans"), 64)
except Exception:
    UI_FONT = pygame.font.SysFont(None, 24)
    SMALL_FONT = pygame.font.SysFont(None, 18)
    BIG_FONT = pygame.font.SysFont(None, 64)

# Sounds (generate placeholders if files are missing)
CLICK_SOUND = None
HOVER_SOUND = None


def ensure_tone(filename, freq=880, ms=120):
    path = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path):
        return path
    # Quick sine wave
    sample_rate = 44100
    length = int(sample_rate * ms / 1000)
    buf = bytearray()
    vol = 127
    for i in range(length):
        s = int(vol * math.sin(2 * math.pi * freq * (i / sample_rate)))
        # 8-bit mono unsigned
        buf.append((s + 128) & 0xFF)
    snd = pygame.mixer.Sound(buffer=bytes(buf))
    try:
        snd.set_volume(settings.get("sfx_volume", 0.7))
        snd.export(path)  # Not supported; fallback save raw not trivial
    except Exception:
        pass
    return path


# Load basic sfx (if fails, fallback to generated click with Sound(buffer))
try:
    CLICK_SOUND = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "click.wav"))
except Exception:
    # Generate simple click
    arr = bytearray([128 + int(40 * math.sin(2 * math.pi * i / 10)) for i in range(200)])
    CLICK_SOUND = pygame.mixer.Sound(buffer=bytes(arr))

try:
    HOVER_SOUND = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "hover.wav"))
except Exception:
    arr = bytearray([128 + int(20 * math.sin(2 * math.pi * i / 20)) for i in range(400)])
    HOVER_SOUND = pygame.mixer.Sound(buffer=bytes(arr))

CLICK_SOUND.set_volume(settings.get("sfx_volume", 0.7))
HOVER_SOUND.set_volume(settings.get("sfx_volume", 0.7) * 0.6)

# Music (optional); use a generated silent loop if nothing exists
try:
    music_path = os.path.join(ASSETS_DIR, "menu_music.ogg")
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(settings.get("music_volume", 0.5))
        pygame.mixer.music.play(-1)
except Exception:
    pass


# -------------------------- UI WIDGETS --------------------------
class Button:
    def __init__(self, text, rect, on_click=None):
        self.text = text
        self.base_rect = pygame.Rect(rect)
        self.rect = self.base_rect.copy()
        self.on_click = on_click
        self.hovered = False
        self.pressed = False
        self.last_hover_time = 0

    def handle_event(self, e):
        if e.type == pygame.MOUSEMOTION:
            was = self.hovered
            self.hovered = self.rect.collidepoint(e.pos)
            if self.hovered and not was:
                HOVER_SOUND.play()
                self.last_hover_time = time.time()
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.pressed = True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self.pressed and self.rect.collidepoint(e.pos):
                CLICK_SOUND.play()
                if self.on_click:
                    self.on_click()
            self.pressed = False

    def update(self, dt):
        target = 1.05 if self.hovered else 1.0
        scale = 0.2
        self.rect = self._lerp_rect(self.rect, self.base_rect, 1 - scale)
        w = int(self.base_rect.w * (target * scale + (1 - scale)))
        h = int(self.base_rect.h * (target * scale + (1 - scale)))
        cx, cy = self.base_rect.center
        self.rect.size = (w, h)
        self.rect.center = (cx, cy)

    def draw(self, surf):
        c1 = (40, 180, 200) if self.hovered else (30, 140, 160)
        c2 = (0, 0, 0)
        pygame.draw.rect(surf, c1, self.rect, border_radius=14)
        pygame.draw.rect(surf, c2, self.rect, width=3, border_radius=14)
        label = UI_FONT.render(self.text, True, (240, 240, 240))
        surf.blit(label, label.get_rect(center=self.rect.center))

    @staticmethod
    def _lerp_rect(a: pygame.Rect, b: pygame.Rect, t: float) -> pygame.Rect:
        r = a.copy()
        r.x = int(a.x * t + b.x * (1 - t))
        r.y = int(a.y * t + b.y * (1 - t))
        r.w = int(a.w * t + b.w * (1 - t))
        r.h = int(a.h * t + b.h * (1 - t))
        return r


class Toggle:
    def __init__(self, text, value, pos, on_change=None):
        self.text = text
        self.value = value
        self.pos = pos
        self.on_change = on_change
        self.rect = pygame.Rect(pos[0], pos[1], 42, 22)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.value = not self.value
                CLICK_SOUND.play()
                if self.on_change:
                    self.on_change(self.value)

    def draw(self, surf):
        x, y = self.pos
        label = UI_FONT.render(self.text, True, (230, 230, 230))
        surf.blit(label, (x, y - 6))
        knob_x = self.rect.x + (22 if self.value else 0)
        bg = (80, 200, 120) if self.value else (120, 120, 120)
        pygame.draw.rect(surf, bg, self.rect, border_radius=12)
        pygame.draw.circle(surf, (20, 20, 20), (knob_x + 11, self.rect.y + 11), 10)


class Slider:
    def __init__(self, text, value, pos, width=240, on_change=None):
        self.text = text
        self.value = value  # 0..1
        self.pos = pos
        self.width = width
        self.drag = False
        self.on_change = on_change
        self.rect = pygame.Rect(pos[0], pos[1] + 24, width, 6)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.drag = True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.drag = False
        elif e.type == pygame.MOUSEMOTION and self.drag:
            relx = (e.pos[0] - self.rect.x) / self.width
            self.value = min(1, max(0, relx))
            if self.on_change:
                self.on_change(self.value)

    def draw(self, surf):
        x, y = self.pos
        label = UI_FONT.render(f"{self.text}: {int(self.value*100)}%", True, (230, 230, 230))
        surf.blit(label, (x, y))
        pygame.draw.rect(surf, (70, 70, 70), self.rect, border_radius=3)
        knob_x = int(self.rect.x + self.value * self.width)
        pygame.draw.circle(surf, (200, 200, 200), (knob_x, self.rect.centery), 9)


class Dropdown:
    def __init__(self, text, options, index, rect, on_change=None):
        self.text = text
        self.options = options
        self.index = index
        self.rect = pygame.Rect(rect)
        self.open = False
        self.on_change = on_change

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self.rect.collidepoint(e.pos):
                self.open = not self.open
                CLICK_SOUND.play()
            elif self.open:
                # Option click
                for i, _ in enumerate(self.options):
                    orect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.h, self.rect.w, self.rect.h)
                    if orect.collidepoint(e.pos):
                        self.index = i
                        self.open = False
                        CLICK_SOUND.play()
                        if self.on_change:
                            self.on_change(self.options[self.index])
                        break
                else:
                    self.open = False

    def draw(self, surf):
        label = UI_FONT.render(self.text, True, (230, 230, 230))
        surf.blit(label, (self.rect.x, self.rect.y - 36))
        pygame.draw.rect(surf, (30, 30, 30), self.rect, border_radius=8)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, width=2, border_radius=8)
        txt = UI_FONT.render(str(self.options[self.index]), True, (240, 240, 240))
        surf.blit(txt, txt.get_rect(center=self.rect.center))
        # Arrow
        pygame.draw.polygon(surf, (200, 200, 200), [
            (self.rect.right - 24, self.rect.centery - 4),
            (self.rect.right - 12, self.rect.centery - 4),
            (self.rect.right - 18, self.rect.centery + 6)
        ])
        if self.open:
            for i, opt in enumerate(self.options):
                orect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.h, self.rect.w, self.rect.h)
                pygame.draw.rect(surf, (45, 45, 45), orect)
                pygame.draw.rect(surf, (0, 0, 0), orect, width=1)
                t = UI_FONT.render(str(opt), True, (220, 220, 220))
                surf.blit(t, t.get_rect(center=orect.center))


# -------------------------- SCENE SYSTEM --------------------------
class Scene:
    def __init__(self, manager):
        self.mgr = manager

    def handle_event(self, e):
        pass

    def update(self, dt):
        pass

    def draw(self, surf):
        pass


class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.current = None
        self.fade_alpha = 0
        self.fading = False
        self.next_key = None

    def register(self, key, scene):
        self.scenes[key] = scene

    def change(self, key):
        self.fading = True
        self.fade_alpha = 0
        self.next_key = key

    def _apply_change(self):
        self.current = self.scenes[self.next_key]
        self.fading = False
        self.fade_alpha = 0

    def handle_event(self, e):
        if self.current:
            self.current.handle_event(e)

    def update(self, dt):
        if self.fading:
            self.fade_alpha += dt * 400
            if self.fade_alpha >= 255:
                self._apply_change()
        if self.current:
            self.current.update(dt)

    def draw(self, surf):
        if self.current:
            self.current.draw(surf)
        if self.fading:
            overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(min(255, self.fade_alpha))))
            surf.blit(overlay, (0, 0))


# -------------------------- BACKGROUND FX --------------------------
class GridBG:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.t = 0
        self.stars = [(random.randint(0, w), random.randint(0, h), random.random()*1.0+0.2) for _ in range(120)]

    def update(self, dt):
        self.t += dt * 0.6
        # parallax drift
        for i in range(len(self.stars)):
            x, y, s = self.stars[i]
            x -= s * 30 * dt
            if x < 0:
                x = self.w
                y = random.randint(0, self.h)
            self.stars[i] = (x, y, s)

    def draw(self, surf):
        surf.fill((14, 16, 22))
        # moving grid lines
        spacing = 40
        offset = int((math.sin(self.t)*0.5+0.5) * spacing)
        for x in range(-offset, self.w, spacing):
            pygame.draw.line(surf, (22, 30, 48), (x, 0), (x, self.h), 1)
        for y in range(offset, self.h, spacing):
            pygame.draw.line(surf, (22, 30, 48), (0, y), (self.w, y), 1)
        # stars
        for x, y, s in self.stars:
            pygame.draw.circle(surf, (180, 220, 255), (int(x), int(y)), max(1, int(2*s)))


# -------------------------- SCENES --------------------------
class MainMenu(Scene):
    def __init__(self, mgr):
        super().__init__(mgr)
        self.bg = GridBG(*SCREEN.get_size())
        w, h = SCREEN.get_size()
        bx = w // 2 - 160
        by = h // 2 - 40
        self.buttons = [
            Button("Почати гру", (bx, by, 320, 54), lambda: self.goto("game")),
            Button("Налаштування", (bx, by + 70, 320, 54), lambda: self.goto("settings")),
            Button("Налуштквання руху", (bx, by + 140, 320, 54), lambda: self.goto("controls")),
            Button("Допомога", (bx, by + 210, 320, 54), lambda: self.goto("help")),
            Button("Розробники", (bx, by + 280, 320, 54), lambda: self.goto("credits")),
            Button("Выйти", (bx, by + 350, 320, 54), self.exit_game),
        ]
        self.logo_phase = 0

    def goto(self, key):
        self.mgr.change(key)

    def exit_game(self):
        pygame.quit()
        sys.exit(0)

    def handle_event(self, e):
        for b in self.buttons:
            b.handle_event(e)

    def update(self, dt):
        self.bg.update(dt)
        self.logo_phase += dt
        for b in self.buttons:
            b.update(dt)

    def draw(self, surf):
        self.bg.draw(surf)
        title = BIG_FONT.render("TANK BATTLES", True, (240, 240, 255))
        tw, th = title.get_size()
        wobble = int(math.sin(self.logo_phase * 1.8) * 6)
        surf.blit(title, (surf.get_width() // 2 - tw // 2, 90 + wobble))
        for b in self.buttons:
            b.draw(surf)
        # hint
        tip = SMALL_FONT.render("Homework demo: Menu + scenes (Pygame)", True, (200, 200, 220))
        surf.blit(tip, (10, surf.get_height() - 26))


class Settings(Scene):
    def __init__(self, mgr):
        super().__init__(mgr)
        w, h = SCREEN.get_size()
        self.bg = GridBG(w, h)
        # Controls
        res_idx = 0
        for i, r in enumerate(RESOLUTIONS):
            if (settings["width"], settings["height"]) == r:
                res_idx = i
                break
        self.drop_res = Dropdown("Resolution", RESOLUTIONS, res_idx, (w//2 - 150, 200, 300, 44), self.on_res_change)
        self.tgl_full = Toggle("Fullscreen", settings.get("fullscreen", False), (w//2 - 150, 280), self.on_full_change)
        self.sld_music = Slider("Music", settings.get("music_volume", 0.5), (w//2 - 150, 350), on_change=self.on_music_change)
        self.sld_sfx = Slider("SFX", settings.get("sfx_volume", 0.7), (w//2 - 150, 420), on_change=self.on_sfx_change)
        self.btn_apply = Button("APPLY", (w//2 - 150, 500, 140, 48), self.apply_changes)
        self.btn_back = Button("BACK", (w//2 + 10, 500, 140, 48), lambda: mgr.change("main"))
        self.pending = {"resolution": (settings["width"], settings["height"]), "fullscreen": settings.get("fullscreen", False)}

    def on_res_change(self, value):
        self.pending["resolution"] = value

    def on_full_change(self, value):
        self.pending["fullscreen"] = value

    def on_music_change(self, value):
        settings["music_volume"] = float(value)
        try:
            pygame.mixer.music.set_volume(settings["music_volume"])
        except Exception:
            pass

    def on_sfx_change(self, value):
        settings["sfx_volume"] = float(value)
        CLICK_SOUND.set_volume(settings["sfx_volume"])
        HOVER_SOUND.set_volume(settings["sfx_volume"] * 0.6)

    def apply_changes(self):
        # Apply display
        w, h = self.pending["resolution"]
        settings["width"], settings["height"] = int(w), int(h)
        settings["fullscreen"] = bool(self.pending["fullscreen"])
        save_settings(settings)
        global SCREEN
        flags = pygame.DOUBLEBUF
        if settings["fullscreen"]:
            flags |= pygame.FULLSCREEN
        SCREEN = pygame.display.set_mode((settings["width"], settings["height"]), flags)
        self.bg = GridBG(*SCREEN.get_size())
        CLICK_SOUND.play()

    def handle_event(self, e):
        self.drop_res.handle_event(e)
        self.tgl_full.handle_event(e)
        self.sld_music.handle_event(e)
        self.sld_sfx.handle_event(e)
        self.btn_apply.handle_event(e)
        self.btn_back.handle_event(e)

    def update(self, dt):
        self.bg.update(dt)
        self.btn_apply.update(dt)
        self.btn_back.update(dt)

    def draw(self, surf):
        self.bg.draw(surf)
        title = BIG_FONT.render("SETTINGS", True, (240, 240, 255))
        surf.blit(title, (surf.get_width()//2 - title.get_width()//2, 90))
        self.drop_res.draw(surf)
        self.tgl_full.draw(surf)
        self.sld_music.draw(surf)
        self.sld_sfx.draw(surf)
        self.btn_apply.draw(surf)
        self.btn_back.draw(surf)


class Controls(Scene):
    def __init__(self, mgr):
        super().__init__(mgr)
        w, h = SCREEN.get_size()
        self.bg = GridBG(w, h)
        self.waiting_key = None  # which action is awaiting new key
        self.actions = [
            ("move_up", "Move Up"),
            ("move_down", "Move Down"),
            ("move_left", "Move Left"),
            ("move_right", "Move Right"),
            ("fire", "Fire"),
            ("pause", "Pause"),
        ]
        self.btn_back = Button("BACK", (w//2 - 70, h - 90, 140, 48), lambda: mgr.change("main"))

    def handle_event(self, e):
        if e.type == pygame.KEYUP and self.waiting_key:
            # assign
            action = self.waiting_key
            settings["controls"][action] = e.key
            save_settings(settings)
            CLICK_SOUND.play()
            self.waiting_key = None
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            # detect which row
            mx, my = e.pos
            w, h = SCREEN.get_size()
            left = w//2 - 260
            top = 220
            for i, (key, label) in enumerate(self.actions):
                r = pygame.Rect(left, top + i*54, 520, 44)
                if r.collidepoint(mx, my):
                    self.waiting_key = key
                    HOVER_SOUND.play()
                    break
        self.btn_back.handle_event(e)

    def update(self, dt):
        self.bg.update(dt)
        self.btn_back.update(dt)

    def draw(self, surf):
        self.bg.draw(surf)
        title = BIG_FONT.render("CONTROLS", True, (240, 240, 255))
        surf.blit(title, (surf.get_width()//2 - title.get_width()//2, 90))
        w, h = surf.get_size()
        left = w//2 - 260
        top = 220
        for i, (key, label) in enumerate(self.actions):
            r = pygame.Rect(left, top + i*54, 520, 44)
            pygame.draw.rect(surf, (28, 28, 36), r, border_radius=10)
            pygame.draw.rect(surf, (0, 0, 0), r, width=2, border_radius=10)
            text = UI_FONT.render(label, True, (230, 230, 230))
            val = pygame.key.name(settings["controls"][key])
            val_text = UI_FONT.render(("<press a key>" if self.waiting_key == key else val), True, (180, 240, 200))
            surf.blit(text, (r.x + 12, r.y + 10))
            surf.blit(val_text, val_text.get_rect(right=r.right - 12, centery=r.centery))
        tip = SMALL_FONT.render("Click a row to rebind. Press any key to set.", True, (200, 200, 220))
        surf.blit(tip, (w//2 - tip.get_width()//2, top + len(self.actions)*54 + 12))
        self.btn_back.draw(surf)


class Help(Scene):
    HELP_TEXT = [
        "Цель: войти в бой танков и победить!",
        "WASD — движение (по умолчанию)",
        "Space — выстрел",
        "Esc — пауза",
        "Можете переназначить клавиши в разделе Controls",
        "В настройках доступны звук, разрешение и фуллскрин",
    ]

    def __init__(self, mgr):
        super().__init__(mgr)
        self.bg = GridBG(*SCREEN.get_size())
        w, h = SCREEN.get_size()
        self.btn_back = Button("BACK", (w//2 - 70, h - 90, 140, 48), lambda: mgr.change("main"))

    def handle_event(self, e):
        self.btn_back.handle_event(e)

    def update(self, dt):
        self.bg.update(dt)
        self.btn_back.update(dt)

    def draw(self, surf):
        self.bg.draw(surf)
        title = BIG_FONT.render("HELP", True, (240, 240, 255))
        surf.blit(title, (surf.get_width()//2 - title.get_width()//2, 90))
        y = 210
        for line in self.HELP_TEXT:
            txt = UI_FONT.render(line, True, (230, 230, 230))
            surf.blit(txt, (surf.get_width()//2 - txt.get_width()//2, y))
            y += 38
        self.btn_back.draw(surf)


class Credits(Scene):
    LINES = [
        "ДЕМО МЕНЮ ТАНКІВ",
        "",
        "Розробники проєкту:",
        "• Карта — Рома: створив детальну локацію, наповнену атмосферою битви.",
        "• Механіки — Вячеслав: реалізував логіку та рух танків, стрільбу й фізику гри.",
        "• Налаштування, музика, звуки — Яна: відповідала за баланс гучності, мелодію та ефекти.",
        "• Меню — Ярослав: розробив головне меню, сцени й систему переходів.",
        "• Дизайн — Кирило: оформив стиль гри, кольори, інтерфейс і візуальні ефекти.",
        "",
        "Pygame (c) pygame.org",
        "Гра створена з любов’ю і натхненням ❤️"
    ]

    def __init__(self, mgr):
        super().__init__(mgr)
        self.bg = GridBG(*SCREEN.get_size())
        self.scroll = SCREEN.get_height() + 120
        self.speed = 40
        w, h = SCREEN.get_size()
        self.btn_back = Button("НАЗАД", (w//2 - 70, h - 90, 140, 48), self.exit_credits)

    def enter(self):
        """Запускається, коли відкривається сцена титрів"""
        music_path = os.path.join(ASSETS_DIR, "menu_music.mp3")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(settings.get("music_volume", 0.5))
                pygame.mixer.music.play(-1, fade_ms=1500)  # плавний старт
                print("🎬 Музика титрів запущена.")
            except Exception as e:
                print("Не вдалося запустити музику титрів:", e)
        else:
            print("⚠️ Файл menu_music.mp3 не знайдено у assets.")

    def exit_credits(self):
        """При виході з титрів — плавне загасання музики"""
        try:
            pygame.mixer.music.fadeout(1500)
            print("🛑 Музика титрів зупинена.")
        except Exception as e:
            print("Не вдалося зупинити музику:", e)
        self.mgr.change("main")

    def handle_event(self, e):
        self.btn_back.handle_event(e)

    def update(self, dt):
        self.bg.update(dt)
        self.scroll -= self.speed * dt
        if self.scroll < -len(self.LINES) * 70:
            self.scroll = SCREEN.get_height() + 120
        self.btn_back.update(dt)

    def draw(self, surf):
        self.bg.draw(surf)
        y = int(self.scroll)
        for i, line in enumerate(self.LINES):
            size = 44 if i == 0 else 24
            f = pygame.font.Font(pygame.font.match_font("verdana,arial,dejavusans"), size)
            txt = f.render(line, True, (230, 230, 230))
            surf.blit(txt, (surf.get_width()//2 - txt.get_width()//2, y))
            y += 50
        self.btn_back.draw(surf)


class Game(Scene):
    # Dummy play scene: simple tank you can move & fire bullets to prove controls
    def __init__(self, mgr):
        super().__init__(mgr)
        self.bg = GridBG(*SCREEN.get_size())
        w, h = SCREEN.get_size()
        self.tank = pygame.Rect(w//2 - 20, h//2 - 20, 40, 40)
        self.speed = 200
        self.bullets = []
        self.cooldown = 0
        self.paused = False
        self.pause_text = UI_FONT.render("PAUSED — press Esc to resume", True, (240, 240, 240))

    def handle_event(self, e):
        if e.type == pygame.KEYUP:
            if e.key == settings["controls"]["pause"]:
                self.paused = not self.paused
                CLICK_SOUND.play()
        if self.paused:
            return
        if e.type == pygame.KEYUP and e.key == settings["controls"]["fire"]:
            if self.cooldown <= 0:
                bx = self.tank.centerx
                by = self.tank.top - 8
                self.bullets.append([bx, by, -400])
                self.cooldown = 0.2
                CLICK_SOUND.play()

    def update(self, dt):
        self.bg.update(dt)
        if self.paused:
            return
        keys = pygame.key.get_pressed()
        vx = vy = 0
        if keys[settings["controls"]["move_left"]]:
            vx -= 1
        if keys[settings["controls"]["move_right"]]:
            vx += 1
        if keys[settings["controls"]["move_up"]]:
            vy -= 1
        if keys[settings["controls"]["move_down"]]:
            vy += 1
        if vx != 0 and vy != 0:
            inv = 1 / math.sqrt(2)
            vx *= inv
            vy *= inv
        self.tank.x += int(vx * self.speed * dt)
        self.tank.y += int(vy * self.speed * dt)
        self.tank.clamp_ip(pygame.Rect(0, 0, *SCREEN.get_size()))
        # bullets
        for b in self.bullets:
            b[1] += b[2] * dt
        self.bullets = [b for b in self.bullets if b[1] > -10]
        self.cooldown = max(0, self.cooldown - dt)

    def draw(self, surf):
        self.bg.draw(surf)
        # draw tank
        pygame.draw.rect(surf, (60, 200, 120), self.tank, border_radius=6)
        # turret
        pygame.draw.rect(surf, (40, 120, 80), (self.tank.centerx - 3, self.tank.y - 12, 6, 12))
        for b in self.bullets:
            pygame.draw.circle(surf, (230, 230, 90), (int(b[0]), int(b[1])), 4)
        hud = SMALL_FONT.render("Esc: pause | Backspace: return to menu", True, (220, 220, 230))
        surf.blit(hud, (10, 10))
        if self.paused:
            surf.blit(self.pause_text, self.pause_text.get_rect(center=(surf.get_width()//2, surf.get_height()//2)))

    def handle_event_global(self, e):
        # Separate from handle_event used by manager; called below in game loop
        if e.type == pygame.KEYUP and e.key == pygame.K_BACKSPACE:
            self.mgr.change("main")


# -------------------------- APP SETUP --------------------------
manager = SceneManager()
scene_main = MainMenu(manager)
scene_settings = Settings(manager)
scene_controls = Controls(manager)
scene_help = Help(manager)
scene_credits = Credits(manager)
scene_game = Game(manager)

manager.register("main", scene_main)
manager.register("settings", scene_settings)
manager.register("controls", scene_controls)
manager.register("help", scene_help)
manager.register("credits", scene_credits)
manager.register("game", scene_game)
manager.current = scene_main


# -------------------------- MAIN LOOP --------------------------
running = True
accum = 0
while running:
    dt = CLOCK.tick(60) / 1000.0
    accum += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_F11:
                settings["fullscreen"] = not settings.get("fullscreen", False)
                flags = pygame.DOUBLEBUF | (pygame.FULLSCREEN if settings["fullscreen"] else 0)
                SCREEN = pygame.display.set_mode((settings["width"], settings["height"]), flags)
                save_settings(settings)
            elif event.key == pygame.K_ESCAPE:
                manager.change("main")  # ← тепер Esc повертає в головне меню!

        # передаємо події активній сцені
        manager.handle_event(event)

        # якщо поточна сцена — Game, додаємо обробку Backspace
        if manager.current is scene_game:
            scene_game.handle_event_global(event)

    manager.update(dt)
    manager.draw(SCREEN)

    # FPS лічильник
    fps_str = f"{CLOCK.get_fps():.0f} FPS"
    fps_img = SMALL_FONT.render(fps_str, True, (180, 180, 190))
    SCREEN.blit(fps_img, (SCREEN.get_width() - fps_img.get_width() - 10, 8))

    pygame.display.flip()




    manager.update(dt)
    manager.draw(SCREEN)

    # FPS counter (small)
    fps_str = f"{CLOCK.get_fps():.0f} FPS"
    fps_img = SMALL_FONT.render(fps_str, True, (180, 180, 190))
    SCREEN.blit(fps_img, (SCREEN.get_width() - fps_img.get_width() - 10, 8))

    pygame.display.flip()


pygame.quit()
