import pygame
import random
import math

class EnemySystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.enemies = []  # List of [x, y, speed, size, color]
        self.spawn_timer = 0
        self.spawn_rate = 1.5  # seconds between spawns
        self.min_speed = 80
        self.max_speed = 200
        self.score = 0
        self.font = pygame.font.SysFont(None, 36)
        
    def spawn_enemy(self):
        """Spawn a new falling rock enemy"""
        x = random.randint(50, self.screen_width - 50)
        y = -30  # Start above screen
        speed = random.randint(self.min_speed, self.max_speed)
        size = random.randint(15, 35)
        
        # Different rock colors
        colors = [
            (120, 120, 120),  # Gray
            (139, 69, 19),    # Brown
            (105, 105, 105),  # Dim gray
            (160, 82, 45),    # Saddle brown
        ]
        color = random.choice(colors)
        
        self.enemies.append([x, y, speed, size, color])
    
    def update(self, dt):
        """Update all enemies"""
        self.spawn_timer += dt
        
        # Spawn new enemies
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_enemy()
            self.spawn_timer = 0
            
        # Update enemy positions
        for enemy in self.enemies[:]:
            enemy[1] += enemy[2] * dt  # Move down
            
            # Remove enemies that fell off screen
            if enemy[1] > self.screen_height + 50:
                self.enemies.remove(enemy)
    
    def check_tank_collision(self, tank_rect):
        """Check if any enemy hit the tank"""
        for enemy in self.enemies[:]:
            x, y, speed, size, color = enemy
            enemy_rect = pygame.Rect(x - size//2, y - size//2, size, size)
            
            if tank_rect.colliderect(enemy_rect):
                self.enemies.remove(enemy)
                return True
        return False
    
    def check_bullet_collision(self, bullets):
        """Check bullet-enemy collisions and update score"""
        hit_enemies = []
        
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(int(bullet[0]) - 2, int(bullet[1]) - 2, 4, 8)
            
            for enemy in self.enemies[:]:
                x, y, speed, size, color = enemy
                enemy_rect = pygame.Rect(x - size//2, y - size//2, size, size)
                
                if bullet_rect.colliderect(enemy_rect):
                    # Remove both bullet and enemy
                    if bullet in bullets:
                        bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10  # Add 10 points per destroyed rock
                    hit_enemies.append(enemy)
                    break
        
        return hit_enemies
    
    def draw(self, surf):
        """Draw all enemies and score"""
        # Draw enemies as rocks
        for enemy in self.enemies:
            x, y, speed, size, color = enemy
            
            # Draw rock shape (irregular polygon)
            points = []
            for i in range(8):
                angle = (i / 8) * 2 * math.pi
                radius = size // 2 + random.randint(-3, 3)
                px = x + int(math.cos(angle) * radius)
                py = y + int(math.sin(angle) * radius)
                points.append((px, py))
            
            pygame.draw.polygon(surf, color, points)
            pygame.draw.polygon(surf, (0, 0, 0), points, 2)
            
            # Add some texture lines
            pygame.draw.line(surf, (60, 60, 60), (x - size//3, y - size//3), (x + size//3, y + size//3), 1)
            pygame.draw.line(surf, (60, 60, 60), (x + size//3, y - size//3), (x - size//3, y + size//3), 1)
        
        # Draw score at top center
        score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 0))
        score_x = self.screen_width // 2 - score_text.get_width() // 2
        surf.blit(score_text, (score_x, 20))
        
        # Draw score background for better visibility
        score_bg = pygame.Rect(score_x - 10, 15, score_text.get_width() + 20, score_text.get_height() + 10)
        pygame.draw.rect(surf, (0, 0, 0), score_bg, border_radius=8)
        pygame.draw.rect(surf, (255, 255, 0), score_bg, 2, border_radius=8)
        surf.blit(score_text, (score_x, 20))
    
    def reset(self):
        """Reset the enemy system"""
        self.enemies.clear()
        self.score = 0
        self.spawn_timer = 0
    
    def set_difficulty(self, level):
        """Adjust spawn rate based on difficulty level"""
        if level == 1:
            self.spawn_rate = 2.0
            self.min_speed = 60
            self.max_speed = 120
        elif level == 2:
            self.spawn_rate = 1.5
            self.min_speed = 80
            self.max_speed = 180
        elif level == 3:
            self.spawn_rate = 1.0
            self.min_speed = 100
            self.max_speed = 250

# Particle effects for destroyed rocks
class ParticleSystem:
    def __init__(self):
        self.particles = []  # [x, y, vx, vy, life, color]
    
    def create_explosion(self, x, y, color=(255, 100, 0)):
        """Create explosion particles when rock is destroyed"""
        for i in range(8):
            angle = (i / 8) * 2 * math.pi
            speed = random.randint(50, 150)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.uniform(0.3, 0.8)
            self.particles.append([x, y, vx, vy, life, color])
    
    def update(self, dt):
        """Update particles"""
        for particle in self.particles[:]:
            particle[0] += particle[2] * dt  # x
            particle[1] += particle[3] * dt  # y
            particle[4] -= dt  # life
            
            if particle[4] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surf):
        """Draw particles"""
        for particle in self.particles:
            x, y, vx, vy, life, color = particle
            alpha = int(life * 255)
            size = max(1, int(life * 6))
            
            # Create surface with alpha for fading effect
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*color, alpha), (size, size), size)
            surf.blit(particle_surf, (x - size, y - size))