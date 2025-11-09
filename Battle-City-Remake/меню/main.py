# ----------------------------------  main.py  ----------------------------------
import os
import sys
import json
import math
import time
import random
import pygame
from pygame import mixer
from enami import EnemySystem, ParticleSystem   # ваши модули

# ------------------------------ UTILITIES ------------------------------
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
os.makedirs(ASSETS_DIR, exist_ok=True)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # backward compatibility
            for k, v in DEFAULT_SETTINGS.items():
                data.setdefault(k, v)
            for ck, cv in DEFAULT_SETTINGS["controls"].items():
                data["controls"].setdefault(ck, cv)
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


# ------------------------------ INIT ------------------------------
pygame.init()
mixer.init()
pygame.display.set_caption(APP_TITLE)
settings = load_settings()

flags = pygame.DOUBLEBUF | (pygame.FULLSCREEN if settings["fullscreen"] else 0)
SCREEN = pygame.display.set_mode((settings["width"], settings["height"]), flags)
CLOCK = pygame.time.Clock()

# fonts
UI_FONT = pygame.font.Font(pygame.font.match_font("verdana,arial,dejavusans"), 24)
SMALL_FONT = pygame.font.Font(pygame.font.match_font("verdana,arial,dejavusans"), 18)
BIG_FONT = pygame.font.Font(pygame.font.match_font("verdana,arial,dejavusans"), 64)

# sounds
def make_sound(freq=880, ms=120):
    sr, samples = 44100, int(44100 * ms / 1000)
    buf = bytes((128 + int(60 * math.sin(2 * math.pi * freq * i / sr))) & 0xFF for i in range(samples))
    snd = pygame.mixer.Sound(buffer=buf)
    snd.set_volume(settings.get("sfx_volume", 0.7))
    return snd

CLICK_SOUND = make_sound(880, 80)
HOVER_SOUND = make_sound(660, 60)

try:
    music_path = os.path.join(ASSETS_DIR, "menu_music.ogg")
    if os.path.exists(music_path):
        mixer.music.load(music_path)
        mixer.music.set_volume(settings.get("music_volume", 0.5))
        mixer.music.play(-1)
except Exception:
    pass


# ------------------------------ UI WIDGETS ------------------------------
class Button:
    def __init__(self, text, rect, on_click=None):
        self.text = text
        self.base_rect = pygame.Rect(rect)
        self.rect = self.base_rect.copy()
        self.on_click = on_click
        self.hovered = False
        self.pressed = False

    def handle_event(self, e):
        if e.type == pygame.MOUSEMOTION:
            was = self.hovered
            self.hovered = self.rect.collidepoint(e.pos)
            if self.hovered and not was:
                HOVER_SOUND.play()
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.pressed = self.hovered
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self.pressed and self.hovered:
                CLICK_SOUND.play()
                if self.on_click:
                    self.on_click()
            self.pressed = False

    def update(self, dt):
        target = 1.05 if self.hovered else 1.0
        w = int(self.base_rect.w * target)
        h = int(self.base_rect.h * target)
        self.rect.size = (w, h)
        self.rect.center = self.base_rect.center

    def draw(self, surf):
        c = (40, 180, 200) if self.hovered else (30, 140, 160)
        pygame.draw.rect(surf, c, self.rect, border_radius=14)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, width=3, border_radius=14)
        label = UI_FONT.render(self.text, True, (240, 240, 240))
        surf.blit(label, label.get_rect(center=self.rect.center))


class Toggle:
    def __init__(self, text, value, pos, on_change=None):
        self.text, self.value, self.pos, self.on_change = text, value, pos, on_change
        self.rect = pygame.Rect(pos[0], pos[1], 42, 22)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and self.rect.collidepoint(e.pos):
            self.value = not self.value
            CLICK_SOUND.play()
            if self.on_change:
                self.on_change(self.value)

    def draw(self, surf):
        label = UI_FONT.render(self.text, True, (230, 230, 230))
        surf.blit(label, (self.rect.x, self.rect.y - 6))
        knob = self.rect.x + (22 if self.value else 0)
        col = (80, 200, 120) if self.value else (120, 120, 120)
        pygame.draw.rect(surf, col, self.rect, border_radius=12)
        pygame.draw.circle(surf, (20, 20, 20), (knob + 11, self.rect.centery), 10)


class Slider:
    def __init__(self, text, value, pos, width=240, on_change=None):
        self.text, self.value, self.pos, self.width, self.on_change = text, value, pos, width, on_change
        self.drag = False
        self.rect = pygame.Rect(pos[0], pos[1] + 24, width, 6)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.drag = self.rect.collidepoint(e.pos)
        elif e.type == pygame.MOUSEBUTTONUP:
            self.drag = False
        elif e.type == pygame.MOUSEMOTION and self.drag:
            self.value = min(1, max(0, (e.pos[0] - self.rect.x) / self.width))
            if self.on_change:
                self.on_change(self.value)

    def draw(self, surf):
        label = UI_FONT.render(f"{self.text}: {int(self.value*100)}%", True, (230, 230, 230))
        surf.blit(label, self.pos)
        pygame.draw.rect(surf, (70, 70, 70), self.rect, border_radius=3)
        knob_x = int(self.rect.x + self.value * self.width)
        pygame.draw.circle(surf, (200, 200, 200), (knob_x, self.rect.centery), 9)


class Dropdown:
    def __init__(self, text, options, index, rect, on_change=None):
        self.text, self.options, self.index, self.rect, self.on_change = text, options, index, pygame.Rect(rect), on_change
        self.open = False

    def handle_event(self, e):
        if e.type != pygame.MOUSEBUTTONUP or e.button != 1:
            return
        if self.rect.collidepoint(e.pos):
            self.open = not self.open
            CLICK_SOUND.play()
        elif self.open:
            for i, _ in enumerate(self.options):
                r = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.h, self.rect.w, self.rect.h)
                if r.collidepoint(e.pos):
                    self.index, self.open = i, False
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
        # стрелка
        pygame.draw.polygon(surf, (200, 200, 200), [
            (self.rect.right - 24, self.rect.centery - 4),
            (self.rect.right - 12, self.rect.centery - 4),
            (self.rect.right - 18, self.rect.centery + 6)
        ])
        if self.open:
            for i, opt in enumerate(self.options):
                r = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.h, self.rect.w, self.rect.h)
                pygame.draw.rect(surf, (45, 45, 45), r)
                pygame.draw.rect(surf, (0, 0, 0), r, width=1)
                t = UI_FONT.render(str(opt), True, (220, 220, 220))
                surf.blit(t, t.get_rect(center=r.center))


# ------------------------------ SCENE SYSTEM ------------------------------
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
        self.scenes, self.current = {}, None
        self.fade_alpha, self.fading, self.next_key = 0, False, None

    def register(self, key, scene):
        self.scenes[key] = scene

    def change(self, key):
        self.fading, self.fade_alpha, self.next_key = True, 0, key

    def _apply_change(self):
        self.current = self.scenes[self.next_key]
        self.fading, self.fade_alpha = False, 0

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


# ------------------------------ BACKGROUND FX ------------------------------
class GridBG:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.t = 0
        self.stars = [(random.randint(0, w), random.randint(0, h), random.random() * 1 + 0.2) for _ in range(120)]

    def update(self, dt):
        self.t += dt * 0.6
        for i, (x, y, s) in enumerate(self.stars):
            x -= s * 30 * dt
            if x < 0:
                x, y = self.w, random.randint(0, self.h)
            self.stars[i] = (x, y, s)

    def draw(self, surf):
        surf.fill((14, 16, 22))
        spacing = 40
        offset = int((math.sin(self.t) * 0.5 + 0.5) * spacing)
        for x in range(-offset, self.w, spacing):
            pygame.draw.line(surf, (22, 30, 48), (x, 0), (x, self.h), 1)
        for y in range(offset, self.h, spacing):
            pygame.draw.line(surf, (22, 30, 48), (0, y), (self.w, y), 1)
        for x, y, s in self.stars:
            pygame.draw.circle(surf, (180, 220, 255), (int(x), int(y)), max(1, int(2 * s)))


# ------------------------------ SCENES ------------------------------
class MainMenu(Scene):
    def __init__(self, mgr):
        super().__init__(mgr)
        self.bg = GridBG(*SCREEN.get_size())
        w, h = SCREEN.get_size()
        bx, by = w // 2 - 160, h // 2 - 40
        self.buttons = [
            Button("Почати гру", (bx, by, 320, 54), lambda: self.goto("game")),
            Button("Налаштування", (bx, by + 70, 320, 54), lambda: self.goto("settings")),
            Button("Налаштування руху", (bx, by + 140, 320, 54), lambda: self.goto("controls")),
            Button("Допомога", (bx, by + 210, 320, 54), lambda: self.goto("help")),
            Button("Розробники", (bx, by + 280, 320, 54), lambda: self.goto("credits")),
            Button("Вийти", (bx, by + 350, 320, 54), self.exit_game),
        ]
        self.logo_phase = 0

    def goto(self, key):
        self.mgr.change(key)

    def exit_game(self):
        pygame.quit()
        sys.exit()

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
        tip = SMALL_FONT.render("Homework demo: Menu + scenes (Pygame)", True, (200, 200, 220))
        surf.blit(tip, (10, surf.get_height() - 26))


class Settings(Scene):
    def __init__(self, mgr):
        super().__init__(mgr)
        self.bg = GridBG(*SCREEN.get_size())
        w, h = SCREEN.get_size()
        res_idx = 0
        for i, r in enumerate(RESOLUTIONS):
            if (settings["width"], settings["height"]) == r:
                res_idx = i
                break
        self.drop_res = Dropdown("Resolution", RESOLUTIONS, res_idx, (w // 2 - 150, 200, 300, 44), self.on_res_change)
        self.tgl_full = Toggle("Fullscreen", settings.get("fullscreen", False), (w // 2 - 150, 280), self.on_full_change)
        self.sld_music = Slider("Music", settings.get("music_volume", 0.5), (w // 2 - 150, 350), on_change=self.on_music_change)
        self.sld_sfx = Slider("SFX", settings.get("sfx_volume", 0.7), (w // 2 - 150, 420), on_change=self.on_sfx_change)
        self.btn_apply = Button("APPLY", (w // 2 - 150, 500, 140, 48), self.apply_changes)
        self.btn_back = Button("BACK", (w // 2 + 10, 500, 140, 48), lambda: mgr.change("main"))
        self.pending = {"resolution": (settings["width"], settings["height"]), "fullscreen": settings.get("fullscreen", False)}

    def on_res_change(self, value):
        self.pending["resolution"] = value

    def on_full_change(self, value):
        self.pending["fullscreen"] = value

    def on_music_change(self, value):
        settings["music_volume"] = float(value)
        try:
            mixer.music.set_volume(settings["music_volume"])
        except Exception:
            pass

    def on_sfx_change(self, value):
        settings["sfx_volume"] = float(value)
        CLICK_SOUND.set_volume(settings["sfx_volume"])
        HOVER_SOUND.set_volume(settings["sfx_volume"] * 0.6)

    def apply_changes(self):
        w, h = self.pending["resolution"]
        settings["width"], settings["height"] = int(w), int(h)
        settings["fullscreen"] = bool(self.pending["fullscreen"])
        save_settings(settings)
        global SCREEN
        flags = pygame.DOUBLEBUF | (pygame.FULLSCREEN if settings["fullscreen"] else 0)
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
        surf.blit(title, (surf.get_width() // 2 - title.get_width() // 2, 90))
        self.drop_res.draw(surf)
        self.tgl_full.draw(surf)
        self.sld_music.draw(surf)
        self.sld_sfx.draw(surf)
        self.btn_apply.draw(surf)
        self.btn_back.draw(surf)


class Controls(Scene):
    def __init__(self, mgr):
        super().__init__(mgr)
        self.bg = GridBG(*SCREEN.get_size())
        self.waiting_key = None
        self.actions = [
            ("move_up", "Move Up"),
            ("move_down", "Move Down"),
            ("move_left", "Move Left"),
            ("move_right", "Move Right"),
            ("fire", "Fire"),
            ("pause", "Pause"),
        ]
        self.btn_back = Button("BACK", (SCREEN.get_width() // 2 - 70, SCREEN.get_height() - 90, 140, 48), lambda: mgr.change("main"))

    def handle_event(self, e):
        if e.type == pygame.KEYUP and self.waiting_key:
            settings["controls"][self.waiting_key] = e.key
            save_settings(settings)
            CLICK_SOUND.play()
            self.waiting_key = None
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            mx, my = e.pos
            left, top = SCREEN.get_width() // 2 - 260, 220
            for i, (key, label) in enumerate(self.actions):
                r = pygame.Rect(left, top + i * 54, 520, 44)
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
        surf.blit(title, (surf.get_width() // 2 - title.get_width() // 2, 90))
        left, top = SCREEN.get_width() // 2 - 260, 220
        for i, (key, label) in enumerate(self.actions):
            r = pygame.Rect(left, top + i * 54, 520, 44)
            pygame.draw.rect(surf, (28, 28, 36), r, border_radius=10)
            pygame.draw.rect(surf, (0, 0, 0), r, width=2, border_radius=10)
            text = UI_FONT.render(label, True, (230, 230, 230))
            val = pygame.key.name(settings["controls"][key])
            val_text = UI_FONT.render(("<press a key>" if self.waiting_key == key else val), True, (180, 240, 200))
            surf.blit(text, (r.x + 12, r.y + 10))
            surf.blit(val_text, val_text.get_rect(right=r.right - 12, centery=r.centery))
        tip = SMALL_FONT.render("Click a row to rebind. Press any key to set.", True, (200, 200, 220))
        surf.blit(tip, (surf.get_width() // 2 - tip.get_width() // 2, top + len(self.actions) * 54 + 12))
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
        self.btn_back = Button("BACK", (SCREEN.get_width() // 2 - 70, SCREEN.get_height() - 90, 140, 48), lambda: mgr.change("main"))

    def handle_event(self, e):
        self.btn_back.handle_event(e)

    def update(self, dt):
        self.bg.update(dt)
        self.btn_back.update(dt)

    def draw(self, surf):
        self.bg.draw(surf)
        title = BIG_FONT.render("HELP", True, (240, 240, 255))
        surf.blit(title, (surf.get_width() // 2 - title.get_width() // 2, 90))
        y = 210
        for line in self.HELP_TEXT:
            txt = UI_FONT.render(line, True, (230, 230, 230))
            surf.blit(txt, (surf.get_width() // 2 - txt.get_width() // 2, y))
            y += 38
        self.btn_back.draw(surf)


class Credits(Scene):
    LINES = [
        "ДЕМО МЕНЮ ТАНКІВ", "",
        "Розробники проєкту:",
        "• Карта — Рома: создал детальную локацию, наполненную атмосферой битвы.",
        "• Механіки — Вячеслав: реализовал логику и движение танков, стрельбу и физику.",
        "• Настройки, музыка, звуки — Яна: баланс громкости, мелодия и эффекты.",
        "• Меню — Ярослав: главное меню, сцены и переходы.",
        "• Дизайн — Кирилл: стиль, цвета, интерфейс и визуальные эффекты.", "",
        "Pygame (c) pygame.org",
        "Гра создана с любовью и вдохновением ❤️"
    ]

    def __init__(self, mgr):
        super().__init__(mgr)
        self.bg = GridBG(*SCREEN.get_size())
        self.scroll = SCREEN.get_height() + 120
        self.speed = 40
        self.btn_back = Button("НАЗАД", (SCREEN.get_width() // 2 - 70, SCREEN.get_height() - 90, 140, 48), self.exit_credits)

    def enter(self):
        path = os.path.join(ASSETS_DIR, "menu_music.mp3")
        if os.path.exists(path):
            try:
                mixer.music.load(path)
                mixer.music.set_volume(settings.get("music_volume", 0.5))
                mixer.music.play(-1, fade_ms=1500)
            except Exception as e:
                print("Credits music error:", e)

    def exit_credits(self):
        try:
            mixer.music.fadeout(1500)
        except Exception:
            pass
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
            surf.blit(txt, (surf.get_width() // 2 - txt.get_width() // 2, y))
            y += 50
        self.btn_back.draw(surf)
class ParticleSystem:
    def __init__(self):
        self.particles = []          # пока что пустой список частиц

    def reset(self):
        """Очистить все партиклы при перезапуске уровня."""
        self.particles.clear()

    def update(self, dt):
        # заглушка, если пока не реализовываете
        pass

    def draw(self, surf):
        # заглушка
        pass

    def create_explosion(self, x, y, color):
        # заглушка; при желании добавьте простые кружочки
        pass

# ------------------------------ GAME SCENE ------------------------------
class Game(Scene):
    def __init__(self, mgr):
        super().__init__(mgr)
        self.bg = GridBG(*SCREEN.get_size())
        w, h = SCREEN.get_size()
        self.speed = 200
        self.cooldown = 0
        self.paused = False
        self.pause_text = UI_FONT.render("PAUSED — press Esc to resume", True, (240, 240, 240))

        # все «живые» объекты создаём один раз
        self.enemy_system = EnemySystem(*SCREEN.get_size())
        self.particle_system = ParticleSystem()
        self.big_font = BIG_FONT
        self.ui_font = UI_FONT

        # вызываем сброс – он создаст танк, пули, счёт и т.д.
        self.reset()

    # ---------- новый метод ----------
    def reset(self):
        """Полный сброс уровня после смерти или по желанию игрока."""
        w, h = SCREEN.get_size()
        self.tank = pygame.Rect(w // 2 - 20, h // 2 - 20, 40, 40)
        self.bullets = []
        self.cooldown = 0
        self.paused = False
        self.game_over = False
        self.score = 0
        # пересоздаём врагов (если у EnemySystem есть сброс – вызываем его)
        self.enemy_system.reset()
        self.particle_system.reset()
        # тексты пересоздаём, чтобы цвет/размер не хранить вручную
        self.game_over_text = self.big_font.render("GAME OVER", True, (255, 0, 0))
        self.restart_text = self.ui_font.render("Press R to restart or ESC for menu", True, (255, 255, 255))
        self.score_text = self.ui_font.render(f"Score: {self.score}", True, (240, 240, 240))

    # ---------- обработка клавиш ----------
    def handle_event(self, e):
        if e.type == pygame.KEYUP:
            if e.key == settings["controls"]["pause"]:
                self.paused = not self.paused
                CLICK_SOUND.play()
        if self.paused or self.game_over:
            return
        if e.type == pygame.KEYUP and e.key == settings["controls"]["fire"]:
            if self.cooldown <= 0:
                bx = self.tank.centerx
                by = self.tank.top - 8
                self.bullets.append([bx, by, -400])
                self.cooldown = 0.2
                CLICK_SOUND.play()

    def handle_event_global(self, e):
        if e.type == pygame.KEYUP:
            if e.key == pygame.K_BACKSPACE:
                self.mgr.change("main")
            # ======  новое: рестарт  ======
            elif e.key == pygame.K_r and self.game_over:
                self.reset()
                CLICK_SOUND.play()

    # ---------- игровая логика ----------
    def update(self, dt):
        self.bg.update(dt)
        if self.paused or self.game_over:
            self.particle_system.update(dt)
            return

        # управление
        keys = pygame.key.get_pressed()
        vx = keys[settings["controls"]["move_right"]] - keys[settings["controls"]["move_left"]]
        vy = keys[settings["controls"]["move_down"]] - keys[settings["controls"]["move_up"]]
        if vx and vy:
            inv = 1 / math.sqrt(2)
            vx *= inv
            vy *= inv
        self.tank.x += int(vx * self.speed * dt)
        self.tank.y += int(vy * self.speed * dt)
        self.tank.clamp_ip(pygame.Rect(0, 0, *SCREEN.get_size()))

        # враги
        self.enemy_system.update(dt)

        # пули
        for b in self.bullets:
            b[1] += b[2] * dt
        self.bullets = [b for b in self.bullets if b[1] > -10]
        self.cooldown = max(0, self.cooldown - dt)

        # попадания
        hit_enemies = self.enemy_system.check_bullet_collision(self.bullets)
        for enemy in hit_enemies:
            x, y, speed, size, color = enemy
            self.particle_system.create_explosion(x, y, color)
            self.score += 10
            self.score_text = self.ui_font.render(f"Score: {self.score}", True, (240, 240, 240))

        # столкновение с танком
        if self.enemy_system.check_tank_collision(self.tank):
            self.game_over = True

        self.particle_system.update(dt)

    # ---------- отрисовка ----------
    def draw(self, surf):
        self.bg.draw(surf)
        # танк
        pygame.draw.rect(surf, (60, 200, 120), self.tank, border_radius=6)
        pygame.draw.rect(surf, (40, 120, 80), (self.tank.centerx - 3, self.tank.y - 12, 6, 12))
        # пули
        for b in self.bullets:
            pygame.draw.circle(surf, (230, 230, 90), (int(b[0]), int(b[1])), 4)
        # враги / партиклы
        self.enemy_system.draw(surf)
        self.particle_system.draw(surf)

        # HUD
        surf.blit(self.score_text, (10, 10))
        hint = SMALL_FONT.render("Esc: pause | Backspace: menu", True, (220, 220, 230))
        surf.blit(hint, (10, 34))

        # поверх всего
        if self.paused:
            surf.blit(self.pause_text, self.pause_text.get_rect(center=surf.get_rect().center))
        if self.game_over:
            surf.blit(self.game_over_text, self.game_over_text.get_rect(center=(surf.get_width() // 2, surf.get_height() // 2 - 40)))
            surf.blit(self.restart_text, self.restart_text.get_rect(center=(surf.get_width() // 2, surf.get_height() // 2 + 20)))

# ------------------------------ APP SETUP ------------------------------
manager = SceneManager()
scene_main = MainMenu(manager)
scene_settings = Settings(manager)
scene_controls = Controls(manager)
scene_help = Help(manager)
scene_credits = Credits(manager)
scene_game = Game(manager)

for k, s in (("main", scene_main), ("settings", scene_settings), ("controls", scene_controls),
             ("help", scene_help), ("credits", scene_credits), ("game", scene_game)):
    manager.register(k, s)
manager.current = scene_main


# ------------------------------ MAIN LOOP ------------------------------
running = True
while running:
    dt = CLOCK.tick(60) / 1000.0

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
                manager.change("main")

        manager.handle_event(event)
        if manager.current is scene_game:
            scene_game.handle_event_global(event)

    manager.update(dt)
    manager.draw(SCREEN)

    fps_str = f"{CLOCK.get_fps():.0f} FPS"
    SCREEN.blit(SMALL_FONT.render(fps_str, True, (180, 180, 190)), (SCREEN.get_width() - 60, 8))
    pygame.display.flip()

pygame.quit()
sys.exit()