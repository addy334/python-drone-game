# main.py

import pygame
import sys
import random
import math
from drone import Drone
from game_elements import Obstacle, Scoreboard, Star, Puff, FloatingRock

# --- Helper Functions ---
def reset_game():
    """Resets the game state for a new round."""
    global spawn_pillar, obstacle_type_counter, wind_timer, wind_strength, obstacle_spawn_timer, start_sound_played
    player.reset(WIDTH, HEIGHT)
    scoreboard.score = 0
    scoreboard.star_count = 0
    obstacles.clear()
    stars.clear()
    spawn_pillar = True 
    obstacle_type_counter = 0
    wind_timer = 300
    wind_strength = 0
    obstacle_spawn_timer = 120
    start_sound_played = False # <-- Reset the start sound flag
    pygame.mixer.music.play(-1)
    return "PLAYING"

def handle_game_over():
    """Handles the transition to the game over state."""
    global game_state
    if game_state == "PLAYING":
        game_state = "GAME_OVER"
        pygame.mixer.music.stop()
        crash_sound.play()
        game_over_sound.play()

def draw_mass(screen, player):
    rope_color = (180, 180, 180)
    mass_color = (200, 50, 50)
    mass_radius = 8
    pygame.draw.line(screen, rope_color, player.rect.center, player.mass_position, 2)
    pygame.draw.circle(screen, mass_color, player.mass_position, mass_radius)

# 1. Initialization
pygame.init()
pygame.mixer.init()

# 2. Screen Setup
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Drone Flappy Bird")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
clock = pygame.time.Clock()
FPS = 60
game_state = "START"

# --- Load Sound Files ---
crash_sound = pygame.mixer.Sound('assets/audio/impact.wav')
star_sound = pygame.mixer.Sound('assets/audio/star_collect.wav')
game_over_sound = pygame.mixer.Sound('assets/audio/game_over.wav')
start_sound = pygame.mixer.Sound('assets/audio/start.wav') # <-- Load new start sound
pygame.mixer.music.load('assets/audio/background.wav')
pygame.mixer.music.set_volume(0.4)

# --- Load UI Graphics ---
get_ready_image = pygame.image.load('assets/textGetReady.png').convert_alpha()
game_over_image = pygame.image.load('assets/textGameOver.png').convert_alpha()
ui_bg_image = pygame.image.load('assets/UIbg.png').convert_alpha()
medal_bronze = pygame.image.load('assets/medalBronze.png').convert_alpha()
medal_silver = pygame.image.load('assets/medalSilver.png').convert_alpha()
medal_gold = pygame.image.load('assets/medalGold.png').convert_alpha()
star_icon = pygame.transform.scale(pygame.image.load('assets/starGold.png').convert_alpha(), (40, 40))

# --- Spawner and Physics Variables ---
spawn_pillar = True
obstacle_type_counter = 0
star_spawn_countdown = random.randint(1, 5)
obstacle_spawn_timer = 120
BASE_SCROLL_SPEED = 5
scroll_speed = BASE_SCROLL_SPEED
wind_strength = 0
wind_timer = 300
start_sound_played = False # <-- New flag for start sound

# --- Create Game Objects ---
player = Drone(WIDTH, HEIGHT)
scoreboard = Scoreboard(WIDTH)
obstacles = []
stars = []

# --- Load Background and Ground Images ---
background_image = pygame.image.load('assets/background.png').convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
bg_x1 = 0
bg_x2 = WIDTH
ground_image = pygame.image.load('assets/groundSnow.png').convert_alpha()
ground_width = ground_image.get_width()
ground_y = HEIGHT - ground_image.get_height()
ground_scroll = 0
num_ground_tiles = math.ceil(WIDTH / ground_width) + 1
bg_scroll_speed = scroll_speed / 2

# 3. Main Game Loop
running = True
while running:
    # 4. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            if game_state == "START":
                if event.key == pygame.K_SPACE:
                    start_sound.stop() # Stop the start sound
                    game_state = reset_game()
            # --- UPDATED: Go back to START screen on restart ---
            elif game_state == "GAME_OVER":
                if event.key == pygame.K_SPACE:
                    game_state = "START"

    if game_state == "PLAYING":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]: player.move_up()
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: player.move_down()

    # 5. State-Based Logic and Drawing
    if game_state == "PLAYING":
        wind_timer -= 1
        if wind_timer <= 0:
            wind_choice = random.choice(['tailwind', 'headwind', 'none', 'none'])
            if wind_choice == 'tailwind': wind_strength = 1.0
            elif wind_choice == 'headwind': wind_strength = -0.5
            else: wind_strength = 0
            wind_timer = random.randint(240, 480)
    
    scroll_speed = BASE_SCROLL_SPEED + wind_strength
    bg_scroll_speed = scroll_speed / 2

    bg_x1 -= bg_scroll_speed
    bg_x2 -= bg_scroll_speed
    if bg_x1 <= -WIDTH: bg_x1 = bg_x2 + WIDTH
    if bg_x2 <= -WIDTH: bg_x2 = bg_x1 + WIDTH
    screen.blit(background_image, (bg_x1, 0))
    screen.blit(background_image, (bg_x2, 0))
    
    for i in range(num_ground_tiles):
        screen.blit(ground_image, (i * ground_width + ground_scroll, ground_y))
    ground_scroll -= scroll_speed
    if abs(ground_scroll) > ground_width:
        ground_scroll = 0

    if game_state == "START":
        # --- Play start sound once ---
        if not start_sound_played:
            pygame.mixer.music.stop()
            start_sound.play(-1) # Play start sound on a loop
            start_sound_played = True
        
        ready_rect = get_ready_image.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.blit(get_ready_image, ready_rect)

    elif game_state == "PLAYING":
        start_sound_played = False # Reset flag for next time
        
        obstacle_spawn_timer -= 1
        if obstacle_spawn_timer <= 0:
            def try_spawn_star(pillar_obstacle):
                global star_spawn_countdown
                star_spawn_countdown -= 1
                if star_spawn_countdown <= 0:
                    if len(stars) < 3:
                        gap_top = pillar_obstacle.gap_y
                        gap_bottom = pillar_obstacle.gap_y + pillar_obstacle.gap_size
                        star_padding = 40
                        star_y = random.randint(gap_top + star_padding, gap_bottom - star_padding)
                        stars.append(Star(WIDTH + 100, star_y, scroll_speed))
                    star_spawn_countdown = random.randint(1, 5)
            if scoreboard.score < 15:
                new_pillar = Obstacle(WIDTH, HEIGHT)
                obstacles.append(new_pillar)
                try_spawn_star(new_pillar)
            elif scoreboard.score < 30:
                if spawn_pillar:
                    new_pillar = Obstacle(WIDTH, HEIGHT)
                    obstacles.append(new_pillar)
                    try_spawn_star(new_pillar)
                else:
                    obstacles.append(FloatingRock(WIDTH, HEIGHT, scroll_speed))
                spawn_pillar = not spawn_pillar
            else:
                spawn_type = obstacle_type_counter % 3
                if spawn_type == 0:
                    new_pillar = Obstacle(WIDTH, HEIGHT)
                    obstacles.append(new_pillar)
                    try_spawn_star(new_pillar)
                elif spawn_type == 1:
                    obstacles.append(FloatingRock(WIDTH, HEIGHT, scroll_speed))
                else:
                    obstacles.append(Puff(WIDTH, HEIGHT, scroll_speed))
                obstacle_type_counter += 1
            obstacle_spawn_timer = random.randint(90, 150)

        for obj in obstacles + stars:
            obj.speed = scroll_speed
        player.update()
        for o in obstacles: o.update()
        for s in stars: s.update()
        for star in stars[:]:
            if player.rect.colliderect(star.rect):
                star_sound.play()
                scoreboard.score += 5
                scoreboard.increase_star_count()
                stars.remove(star)
        for o in obstacles:
            if isinstance(o, Obstacle):
                if not o.passed and o.top_rect.right < player.rect.left:
                    o.passed = True
                    scoreboard.increase_score()
                player_hitbox = player.rect.inflate(-15, -15)
                if player_hitbox.colliderect(o.top_rect.inflate(-15,-15)) or player_hitbox.colliderect(o.bottom_rect.inflate(-15,-15)) or player_hitbox.colliderect(o.top_cap_rect.inflate(-15,-15)) or player_hitbox.colliderect(o.bottom_cap_rect.inflate(-15,-15)):
                    handle_game_over()
            elif isinstance(o, (FloatingRock, Puff)):
                if player.rect.inflate(-15, -15).colliderect(o.rect.inflate(-15, -15)):
                    handle_game_over()
        if player.rect.top <= 0 or player.rect.bottom >= ground_y + 10:
            handle_game_over()
        player.draw(screen)
        draw_mass(screen, player)
        for o in obstacles: o.draw(screen)
        for s in stars: s.draw(screen)
        scoreboard.draw(screen)
        
    elif game_state == "GAME_OVER":
        start_sound_played = False # Reset flag for next time
        
        player.draw(screen)
        draw_mass(screen, player)
        for o in obstacles: o.draw(screen)
        for s in stars: s.draw(screen)
        game_over_rect = game_over_image.get_rect(center=(WIDTH/2, HEIGHT/2 - 150))
        screen.blit(game_over_image, game_over_rect)
        ui_bg_rect = ui_bg_image.get_rect(center=(WIDTH/2, HEIGHT/2 + 20))
        screen.blit(ui_bg_image, ui_bg_rect)
        medal_to_show = None
        if scoreboard.score >= 20: medal_to_show = medal_gold
        elif scoreboard.score >= 10: medal_to_show = medal_silver
        elif scoreboard.score >= 5: medal_to_show = medal_bronze
        if medal_to_show:
            medal_rect = medal_to_show.get_rect(center=(WIDTH/2 - 60, HEIGHT/2 + 25))
            screen.blit(medal_to_show, medal_rect)
        prompt_font = pygame.font.Font(None, 40)
        final_score_text = f"{scoreboard.score}"
        score_surf = prompt_font.render(final_score_text, True, WHITE)
        score_rect = score_surf.get_rect(center=(WIDTH/2 + 70, HEIGHT/2 + 5))
        screen.blit(score_surf, score_rect)
        star_icon_rect = star_icon.get_rect(center=(WIDTH/2 + 45, HEIGHT/2 + 50))
        screen.blit(star_icon, star_icon_rect)
        star_count_text = f"x {scoreboard.star_count}"
        star_surf = prompt_font.render(star_count_text, True, WHITE)
        star_rect = star_surf.get_rect(midleft=star_icon_rect.midright)
        screen.blit(star_surf, star_rect)
        restart_surf = prompt_font.render('Press SPACE to Restart', True, WHITE)
        restart_rect = restart_surf.get_rect(center=(WIDTH/2, HEIGHT/2 + 150))
        screen.blit(restart_surf, restart_rect)

    if game_state != "START":
        obstacles_on_screen = []
        for obs in obstacles:
            if isinstance(obs, Obstacle):
                if obs.top_rect.right > 0: obstacles_on_screen.append(obs)
            else:
                if obs.rect.right > 0: obstacles_on_screen.append(obs)
        obstacles = obstacles_on_screen
        stars = [s for s in stars if s.rect.right > 0]

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()