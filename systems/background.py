import pygame
import random
import math
from core.settings import BLACK, GRID_COLOR


class GridLayer:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.offset = 0
        self.speed = 60
        self.cell_size = 60

    def update(self, dt):
        self.offset += self.speed * dt
        if self.offset >= self.cell_size:
            self.offset = 0

    def draw(self, surface):
        y = (self.offset % self.cell_size)
        while y < self.h:
            brightness = int((y / self.h) * 255)
            color = (0, min(brightness, 40), min(brightness, 60))
            pygame.draw.line(surface, color, (0, int(y)), (self.w, int(y)), 1)
            y += self.cell_size

        x = 0
        while x < self.w:
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, self.h), 1)
            x += self.cell_size


class DataStream:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.font = pygame.font.SysFont("Courier New", 14, bold=True)
        self.char_h = 18
        self.col_w  = 22
        num_cols = screen_w // self.col_w
        self.streams = [self._new_stream(i) for i in range(num_cols)]

    def _new_stream(self, col_index):
        return {
            "x": col_index * self.col_w,
            "y": random.randint(-self.h, 0),
            "speed": random.uniform(80, 200),
            "chars": [self._random_char() for _ in range(random.randint(5, 20))],
            "timer": 0,
            "char_interval": random.uniform(0.05, 0.15),
        }

    def _random_char(self):
        pool = "0123456789ABCDEF<>[]{}|/\\!@#$%^&*ｱｲｳｴｵｶｷｸｹｺ"
        return random.choice(pool)

    def update(self, dt):
        for s in self.streams:
            s["y"] += s["speed"] * dt
            s["timer"] += dt
            if s["timer"] >= s["char_interval"]:
                s["timer"] = 0
                idx = random.randint(0, len(s["chars"]) - 1)
                s["chars"][idx] = self._random_char()
            if s["y"] > self.h + len(s["chars"]) * self.char_h:
                col_index = s["x"] // self.col_w
                s.update(self._new_stream(col_index))

    def draw(self, surface):
        for s in self.streams:
            for i, char in enumerate(s["chars"]):
                y_pos = int(s["y"]) - i * self.char_h
                if not (0 <= y_pos <= self.h):
                    continue
                if i == 0:
                    color = (200, 255, 230)
                else:
                    total = len(s["chars"])
                    fade = max(0, min(255, 255 - i * (255 // total)))
                    color = (0, fade, int(fade * 0.7))
                text_surface = self.font.render(char, True, color)
                surface.blit(text_surface, (s["x"], y_pos))


class ScanLine:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h
        self.y = 0
        self.speed = 200

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > self.h:
            self.y = 0

    def draw(self, surface):
        pygame.draw.line(surface, (0, 100, 80), (0, int(self.y)), (self.w, int(self.y)), 2)
        for offset, color in [(1, (0, 50, 40)), (2, (0, 20, 15)), (-1, (0, 50, 40))]:
            gy = int(self.y) + offset
            if 0 <= gy < self.h:
                pygame.draw.line(surface, color, (0, gy), (self.w, gy), 1)


class CyberpunkBackground:
    def __init__(self, screen_w, screen_h):
        self.base_surface = pygame.Surface((screen_w, screen_h))
        self.grid     = GridLayer(screen_w, screen_h)
        self.streams  = DataStream(screen_w, screen_h)
        self.scanline = ScanLine(screen_w, screen_h)

    def update(self, dt):
        self.grid.update(dt)
        self.streams.update(dt)
        self.scanline.update(dt)

    def draw(self, screen):
        self.base_surface.fill(BLACK)
        self.grid.draw(self.base_surface)
        self.streams.draw(self.base_surface)
        self.scanline.draw(self.base_surface)
        screen.blit(self.base_surface, (0, 0))