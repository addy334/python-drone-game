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
        self.image_original = pygame.transform.scale(self.image_original, (60, 45))
        
        self.image = self.image_original.copy()
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

    def mass_collide(self):
        """Reverses the pendulum's swing to simulate a bounce."""
        self.mass_angular_velocity *= -0.8

    def update(self):
        """Updates the drone's physics state for one frame."""
        # --- REMOVED self.update_wind() call ---
        self.update_mass()

        # Update Drone Rotation
        self.rotational_acceleration += self.torque_from_mass
        self.rotational_velocity += self.rotational_acceleration
        self.rotation_angle += self.rotational_velocity
        self.rotational_velocity *= 0.95
        self.rotation_angle = max(-30, min(self.rotation_angle, 30))
        self.rotational_acceleration = 0
        self.torque_from_mass = 0

        # Linear Physics Calculation
        self.apply_force(self.gravity)
        self.velocity += self.acceleration
        self.velocity *= self.drag
        if abs(self.velocity.y) > self.max_vertical_velocity:
            self.velocity.y = math.copysign(self.max_vertical_velocity, self.velocity.y)
        self.position += self.velocity
        self.acceleration = vec(0, 0)
        self.rect.center = self.position

    def draw(self, screen):
        """Rotates the image and draws it on the screen."""
        self.image = pygame.transform.rotate(self.image_original, self.rotation_angle)
        self.rect = self.image.get_rect(center=self.position)
        screen.blit(self.image, self.rect)
        
    def reset(self, screen_width, screen_height):
        """Resets the drone to its initial state."""
        self.position = vec(screen_width / 4, screen_height / 2)
        self.velocity = vec(0, 0)
        self.acceleration = vec(0, 0)
        
        self.mass = 1.0
        self.gravity = vec(0, 0.2 * self.mass)
        self.thrust_force = vec(0, -0.5)
        self.down_thrust_force = vec(0, 0.3)
        self.drag = 0.985
        self.max_vertical_velocity = 8

        self.rotation_angle = 0
        self.rotational_velocity = 0
        self.rotational_acceleration = 0
        self.torque_from_mass = 0

        self.rect.center = self.position
        
        # --- REMOVED wind properties ---
        
        self.rope_length = 70
        self.mass_angle = 0
        self.mass_angular_velocity = 0
        self.mass_angular_acceleration = 0
        self.mass_position = vec(0, 0)
        
        self.mass_radius = 8

    # --- REMOVED update_wind() method ---
    
    def update_mass(self):
        """Calculates the swing of the suspended mass and its effect on the drone."""
        gravity_pull = -0.02
        self.mass_angular_acceleration = gravity_pull * math.sin(self.mass_angle)
        self.mass_angular_acceleration += (self.acceleration.x * 0.1) * math.cos(self.mass_angle)
        self.mass_angular_velocity += self.mass_angular_acceleration
        self.mass_angle += self.mass_angular_velocity
        self.mass_angular_velocity *= 0.99
        
        mass_pull_strength = 0.02
        force_x = self.mass_angle * mass_pull_strength
        self.apply_force(vec(force_x, 0))
        
        torque_strength = 0.008
        self.torque_from_mass = self.mass_angle * torque_strength

        self.mass_position.x = self.position.x + self.rope_length * math.sin(self.mass_angle)
        self.mass_position.y = self.position.y + self.rope_length * math.cos(self.mass_angle)