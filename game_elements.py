# game_elements.py

import pygame
import random

class Obstacle:
    def __init__(self, screen_width, screen_height):
        """Initializes the Obstacle's properties (pillars)."""
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.gap_size = random.randint(250, 350)
        self.speed = 5
        self.width = 80
        self.body_color = (94, 73, 52) 

        themes = ['rock', 'rockGrass', 'rockIce', 'rockSnow']
        chosen_theme = random.choice(themes)
        top_image_path = f'assets/{chosen_theme}Down.png'
        bottom_image_path = f'assets/{chosen_theme}.png'

        image_top_original = pygame.image.load(top_image_path).convert_alpha()
        image_bottom_original = pygame.image.load(bottom_image_path).convert_alpha()
        
        self.image_top = pygame.transform.scale(image_top_original, (self.width, 50))
        self.image_bottom = pygame.transform.scale(image_bottom_original, (self.width, 50))

        self.x = self.screen_width
        gap_margin = 100
        self.gap_y = random.randint(gap_margin, self.screen_height - gap_margin - self.gap_size)

        self.top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        self.bottom_rect = pygame.Rect(self.x, self.gap_y + self.gap_size, self.width, self.screen_height)
        
        self.top_cap_rect = self.image_top.get_rect(midtop=self.top_rect.midbottom)
        self.bottom_cap_rect = self.image_bottom.get_rect(midbottom=self.bottom_rect.midtop)

        self.passed = False

    def update(self):
        self.x -= self.speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
        self.top_cap_rect.x = self.x
        self.bottom_cap_rect.x = self.x

    def draw(self, screen):
        pygame.draw.rect(screen, self.body_color, self.top_rect)
        pygame.draw.rect(screen, self.body_color, self.bottom_rect)
        screen.blit(self.image_top, self.top_cap_rect)
        screen.blit(self.image_bottom, self.bottom_cap_rect)

class Scoreboard:
    def __init__(self, screen_width):
        self.score = 0
        self.star_count = 0
        self.font = pygame.font.Font(None, 50)
        self.color = (255, 255, 255)
        self.position = (screen_width / 2, 30)
    def increase_score(self):
        self.score += 1
    def increase_star_count(self):
        self.star_count += 1
    def draw(self, screen):
        score_text = f"Score: {self.score}"
        text_surface = self.font.render(score_text, True, self.color)
        text_rect = text_surface.get_rect(center=self.position)
        screen.blit(text_surface, text_rect)

class Star:
    def __init__(self, x, y, speed):
        self.image_original = pygame.image.load('assets/starGold.png').convert_alpha()
        self.image = pygame.transform.scale(self.image_original, (35, 35))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
    def update(self):
        self.rect.x -= self.speed
    def draw(self, screen):
        screen.blit(self.image, self.rect)

class FloatingRock:
    def __init__(self, screen_width, screen_height, speed):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = speed
        self.image_original = pygame.image.load('assets/rock.png').convert_alpha()
        self.image = pygame.transform.scale(self.image_original, (100, 100))
        self.rect = self.image.get_rect(
            center=(screen_width + 100, random.randint(150, screen_height - 250))
        )
    def update(self):
        self.rect.x -= self.speed
    def draw(self, screen):
        screen.blit(self.image, self.rect)

# --- NEW PUFF CLASS ---
class Puff:
    def __init__(self, screen_width, screen_height, speed):
        """Initializes a new puff obstacle."""
        self.speed = speed
        
        # Randomly choose between the large and small puff image
        puff_choice = random.choice(['puffLarge.png', 'puffSmall.png'])
        self.image_original = pygame.image.load(f'assets/{puff_choice}').convert_alpha()
        
        # Scale the image based on which one was chosen
        if puff_choice == 'puffLarge.png':
            self.image = pygame.transform.scale(self.image_original, (80, 80))
        else:
            self.image = pygame.transform.scale(self.image_original, (50, 50))

        # Position it randomly in the vertical center of the screen
        self.rect = self.image.get_rect(
            center=(screen_width + 100, random.randint(150, screen_height - 250))
        )

    def update(self):
        """Moves the puff from right to left."""
        self.rect.x -= self.speed
    
    def draw(self, screen):
        """Draws the puff on the screen."""
        screen.blit(self.image, self.rect)