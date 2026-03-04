import pygame
import random
import math
from core.settings import PARTICLE_COLORS


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(80, 220)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = 150
        self.lifetime = random.uniform(0.4, 0.9)
        self.age = 0
        self.size = random.randint(3, 7)
        self.base_color = color

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.age += dt

    def is_dead(self):
        return self.age >= self.lifetime

    def draw(self, surface):
        life_ratio = 1.0 - (self.age / self.lifetime)
        current_size = max(1, int(self.size * life_ratio))
        r = max(0, min(255, int(self.base_color[0] * life_ratio)))
        g = max(0, min(255, int(self.base_color[1] * life_ratio)))
        b = max(0, min(255, int(self.base_color[2] * life_ratio)))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), current_size)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, count=30, color=None):
        for _ in range(count):
            c = color if color else random.choice(PARTICLE_COLORS)
            self.particles.append(Particle(x, y, c))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def particle_count(self):
        return len(self.particles)