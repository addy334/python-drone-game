# drone.py

import pygame
import random
import math

vec = pygame.math.Vector2

class Drone:
    def __init__(self, screen_width, screen_height):
        """Initializes the Drone's properties."""
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.image_original = pygame.image.load('assets/planeBlue1.png').convert_alpha()
        self.image = pygame.transform.scale(self.image_original, (60, 45))
        self.rect = self.image.get_rect()

        self.reset(screen_width, screen_height)

    def move_up(self):
        """Applies a continuous upward thrust force."""
        self.apply_force(self.thrust_force)

    def move_down(self):
        """Applies a continuous downward thrust force."""
        self.apply_force(self.down_thrust_force)

    def apply_force(self, force):
        """Adds a force to the drone's acceleration (F=ma => a=F/m)."""
        self.acceleration += force / self.mass

    def update(self):
        """Updates the drone's physics state for one frame."""
        # --- Run simulations for external forces ---
        self.update_wind()
        self.update_mass()

        # --- REWRITTEN Physics Calculation ---
        # 1. Apply constant force of gravity
        self.apply_force(self.gravity)

        # 2. Update velocity based on total acceleration (from all forces)
        self.velocity += self.acceleration

        # 3. Apply drag to simulate air resistance
        self.velocity *= self.drag
        
        # 4. Cap the vertical velocity to a maximum speed
        if abs(self.velocity.y) > self.max_vertical_velocity:
            self.velocity.y = math.copysign(self.max_vertical_velocity, self.velocity.y)

        # 5. Update the drone's position
        self.position += self.velocity
        
        # 6. Reset acceleration for the next frame
        self.acceleration = vec(0, 0)
        self.rect.center = self.position

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        
    def reset(self, screen_width, screen_height):
        """Resets the drone to its initial state."""
        self.position = vec(screen_width / 4, screen_height / 2)
        self.velocity = vec(0, 0)
        self.acceleration = vec(0, 0)
        
        # --- UPDATED Physics Properties ---
        self.mass = 1.0
        self.gravity = vec(0, 0.2 * self.mass) # Gravity is now affected by mass
        self.thrust_force = vec(0, -0.5)
        self.down_thrust_force = vec(0, 0.3)
        self.drag = 0.985 # Value slightly less than 1 for air resistance
        self.max_vertical_velocity = 8

        self.rect.center = self.position
        
        self.wind_force = vec(0, 0)
        self.wind_timer = random.randint(180, 360) 
        self.wind_duration = 0
        self.rope_length = 70
        self.mass_angle = 0
        self.mass_angular_velocity = 0
        self.mass_angular_acceleration = 0
        self.mass_position = vec(0, 0)
        
    def update_wind(self):
        """Manages the timing and application of wind gusts."""
        if self.wind_duration > 0:
            self.apply_force(self.wind_force)
            self.wind_duration -= 1
            if self.wind_duration <= 0:
                self.wind_timer = random.randint(180, 360)
        elif self.wind_timer > 0:
            self.wind_timer -= 1
        else:
            self.wind_duration = random.randint(60, 150)
            strength = random.uniform(0.1, 0.25)
            direction = random.choice([-1, 1])
            self.wind_force = vec(strength * direction, 0)
    
    def update_mass(self):
        """Calculates the swing of the suspended mass and its effect on the drone."""
        gravity_pull = -0.005
        self.mass_angular_acceleration = gravity_pull * math.sin(self.mass_angle)
        self.mass_angular_acceleration += (self.acceleration.x * 0.1) * math.cos(self.mass_angle)
        self.mass_angular_velocity += self.mass_angular_acceleration
        self.mass_angle += self.mass_angular_velocity
        self.mass_angular_velocity *= 0.99
        mass_pull_strength = 0.05
        force_x = self.mass_angle * mass_pull_strength
        self.apply_force(vec(force_x, 0))
        self.mass_position.x = self.position.x + self.rope_length * math.sin(self.mass_angle)
        self.mass_position.y = self.position.y + self.rope_length * math.cos(self.mass_angle)