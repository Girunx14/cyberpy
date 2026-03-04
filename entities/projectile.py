import pygame
import math


class Projectile:
    def __init__(self, x, y, target_x, target_y):
        self.x = float(x)
        self.y = float(y)
        self.radius = 5
        self.speed = 450
        self.alive = True

        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        else:
            self.vx = 0
            self.vy = -self.speed

        self.trail = []
        self.trail_length = 8

    def update(self, dt, screen_w, screen_h):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

        self.x += self.vx * dt
        self.y += self.vy * dt

        if not (0 <= self.x <= screen_w and 0 <= self.y <= screen_h):
            self.alive = False

    def draw(self, surface):
        for i, (tx, ty) in enumerate(self.trail):
            ratio = i / len(self.trail)
            r = max(1, int(self.radius * ratio * 0.6))
            brightness = int(ratio * 200)
            color = (brightness, 255, int(brightness * 0.8))
            pygame.draw.circle(surface, color, (int(tx), int(ty)), r)

        pygame.draw.circle(surface, (200, 255, 220), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (0, 255, 200), (int(self.x), int(self.y)), self.radius + 2, 1)