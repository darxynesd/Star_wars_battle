import pygame
import sys
import os
import math
import random
import json
from enami import EnemySystem, ParticleSystem

# Import your existing settings and utilities from main.py
# You'll need to make sure these are accessible

class GameWithEnemies:
    """Enhanced Game scene with enemy system"""
    
    def __init__(self, screen, settings, manager):
        self.screen = screen
        self.settings = settings
        self.manager = manager
        self.screen_width, self.screen_height = screen.get_size()
        
        # Initialize enemy system
        self.enemy_system = EnemySystem(self.screen_width, self.screen_height)
        self.particle_system = ParticleSystem()
        
        # Game state
        self.bg = self.create_background()
        self.tank = pygame.Rect(self.screen_width//2 - 20, self.screen_height//2 - 20, 40, 40)
        self.speed = 200
        self.bullets = []
        self.cooldown = 0
        self.paused = False
        self.game_over = False
        
        # Fonts
        self.ui_font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 64)
        self.pause_text = self.ui_font.render("PAUSED — press Esc to resume", True, (240, 240, 240))
        self.game_over_text = self.big_font.render("GAME OVER", True, (255, 0, 0))
        self.restart_text = self.ui_font.render("Press R to restart or ESC for menu", True, (255, 255, 255))
        
    def create_background(self):
        """Create background (reuse your existing GridBG or similar)"""
        # This would be your existing GridBG class
        return GridBG(self.screen_width, self.screen_height)
    
    def handle_event(self, e):
        """Handle game events"""
        if e.type == pygame.KEYUP:
            if e.key == self.settings["controls"]["pause"]:
                if not self.game_over:
                    self.paused = not self.paused
                    # Play pause sound if you have one
            elif e.key == pygame.K_r and self.game_over:
                self.restart_game()
            elif e.key == pygame.K_ESCAPE:
                if self.game_over:
                    self.manager.change("main")
                else:
                    self.paused = not self.paused
        
        if self.paused or self.game_over:
            return
            
        if e.type == pygame.KEYUP and e.key == self.settings["controls"]["fire"]:
            if self.cooldown <= 0:
                bx = self.tank.centerx
                by = self.tank.top - 8
                self.bullets.append([bx, by, -400])  # x, y, velocity_y
                self.cooldown = 0.2
                # Play shoot sound
    
    def update(self, dt):
        """Update game state"""
        if self.game_over:
            return
            
        if self.paused:
            return
            
        # Update background
        self.bg.update(dt)
        
        # Update tank movement
        keys = pygame.key.get_pressed()
        vx = vy = 0
        if keys[self.settings["controls"]["move_left"]]:
            vx -= 1
        if keys[self.settings["controls"]["move_right"]]:
            vx += 1
        if keys[self.settings["controls"]["move_up"]]:
            vy -= 1
        if keys[self.settings["controls"]["move_down"]]:
            vy += 1
            
        if vx != 0 and vy != 0:
            inv = 1 / math.sqrt(2)
            vx *= inv
            vy *= inv
            
        self.tank.x += int(vx * self.speed * dt)
        self.tank.y += int(vy * self.speed * dt)
        self.tank.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet[1] += bullet[2] * dt
            if bullet[1] < -10:
                self.bullets.remove(bullet)
        
        self.cooldown = max(0, self.cooldown - dt)
        
        # Update enemy system
        self.enemy_system.update(dt)
        
        # Check bullet-enemy collisions
        hit_enemies = self.enemy_system.check_bullet_collision(self.bullets)
        for enemy in hit_enemies:
            x, y, speed, size, color = enemy
            self.particle_system.create_explosion(x, y, color)
        
        # Check tank-enemy collisions
        if self.enemy_system.check_tank_collision(self.tank):
            self.game_over = True
            # Play death sound
        
        # Update particles
        self.particle_system.update(dt)
    
    def draw(self, surf):
        """Draw everything"""
        # Draw background
        self.bg.draw(surf)
        
        # Draw tank
        pygame.draw.rect(surf, (60, 200, 120), self.tank, border_radius=6)
        pygame.draw.rect(surf, (40, 120, 80), (self.tank.centerx - 3, self.tank.y - 12, 6, 12))
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(surf, (230, 230, 90), (int(bullet[0]), int(bullet[1])), 4)
        
        # Draw enemies and score
        self.enemy_system.draw(surf)
        
        # Draw particles
        self.particle_system.draw(surf)
        
        # Draw UI
        hud_text = self.ui_font.render("Esc: pause | Backspace: menu", True, (220, 220, 230))
        surf.blit(hud_text, (10, 10))
        
        # Draw pause overlay
        if self.paused:
            surf.blit(self.pause_text, self.pause_text.get_rect(
                center=(self.screen_width//2, self.screen_height//2)))
        
        # Draw game over overlay
        if self.game_over:
            surf.blit(self.game_over_text, self.game_over_text.get_rect(
                center=(self.screen_width//2, self.screen_height//2 - 50)))
            surf.blit(self.restart_text, self.restart_text.get_rect(
                center=(self.screen_width//2, self.screen_height//2 + 50)))
    
    def restart_game(self):
        """Restart the game"""
        self.tank = pygame.Rect(self.screen_width//2 - 20, self.screen_height//2 - 20, 40, 40)
        self.bullets.clear()
        self.enemy_system.reset()
        self.particle_system = ParticleSystem()
        self.cooldown = 0
        self.game_over = False
        self.paused = False

# Placeholder GridBG class (you should use your existing one)
class GridBG:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.t = 0
        self.stars = [(random.randint(0, w), random.randint(0, h), random.random()*1.0+0.2) for _ in range(120)]

    def update(self, dt):
        self.t += dt * 0.6
        for i in range(len(self.stars)):
            x, y, s = self.stars[i]
            x -= s * 30 * dt
            if x < 0:
                x = self.w
                y = random.randint(0, self.h)
            self.stars[i] = (x, y, s)

    def draw(self, surf):
        surf.fill((14, 16, 22))
        spacing = 40
        offset = int((math.sin(self.t)*0.5+0.5) * spacing)
        for x in range(-offset, self.w, spacing):
            pygame.draw.line(surf, (22, 30, 48), (x, 0), (x, self.h), 1)
        for y in range(offset, self.h, spacing):
            pygame.draw.line(surf, (22, 30, 48), (0, y), (self.w, y), 1)
        for x, y, s in self.stars:
            pygame.draw.circle(surf, (180, 220, 255), (int(x), int(y)), max(1, int(2*s)))