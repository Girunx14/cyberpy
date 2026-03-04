import pygame
import math
import random
from core.utils import clamp_color


def create_enemy_frames(enemy_type="basic"):
    frames = {"idle": [], "death": []}
    size = 40

    if enemy_type == "basic":
        color_fill   = (180, 0, 50)
        color_border = (255, 0, 80)
        sides = 5        
    elif enemy_type == "fast":
        color_fill   = (180, 0, 180)
        color_border = (255, 0, 255)
        sides = 3         
    elif enemy_type == "tank":
        color_fill   = (100, 0, 0)
        color_border = (200, 50, 0)
        sides = 6        

    for i in range(8):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        angle_offset = i * (math.pi * 2 / 8)

        points = []
        for j in range(sides):
            angle = angle_offset + j * (math.pi * 2 / sides)
            r = 14 if enemy_type != "tank" else 16
            px = cx + math.cos(angle) * r
            py = cy + math.sin(angle) * r
            points.append((px, py))

        pygame.draw.polygon(surface, color_fill, points)
        pygame.draw.polygon(surface, color_border, points, 2)

        core_r = 4 + int(math.sin(i / 8 * math.pi * 2) * 2)
        pygame.draw.circle(surface, (255, 80, 80), (cx, cy), core_r)

        frames["idle"].append(surface)

    for i in range(6):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        progress = i / 5

        points = []
        for j in range(sides):
            angle = j * (math.pi * 2 / sides)
            r = 14 + progress * 12
            px = cx + math.cos(angle) * r
            py = cy + math.sin(angle) * r
            points.append((px, py))

        alpha = int(255 * (1.0 - progress))
        fade_fill   = clamp_color(color_fill[0],   color_fill[1],   int(color_fill[2]   * (1 - progress)))
        fade_border = clamp_color(color_border[0], color_border[1], int(color_border[2] * (1 - progress)))

        pygame.draw.polygon(surface, fade_fill,   points)
        pygame.draw.polygon(surface, fade_border, points, 2)

        frames["death"].append(surface)

    return frames


class Enemy:
    CONFIGS = {
        "basic": {"speed": 80,  "hp": 1, "radius": 16, "score": 100, "size": 40},
        "fast":  {"speed": 160, "hp": 1, "radius": 12, "score": 150, "size": 36},
        "tank":  {"speed": 40,  "hp": 3, "radius": 20, "score": 300, "size": 44},
    }

    def __init__(self, x, y, enemy_type="basic"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        cfg = self.CONFIGS[enemy_type]

        self.speed  = cfg["speed"]
        self.hp     = cfg["hp"]
        self.max_hp = cfg["hp"]
        self.radius = cfg["radius"]
        self.score_value = cfg["score"]

        self.frames = create_enemy_frames(enemy_type)
        self.state = "idle"
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_speed = 0.08

        self.alive = True
        self.dying = False

        self.hit_flash = 0.0

    def take_damage(self):
        self.hp -= 1
        self.hit_flash = 0.15

        if self.hp <= 0:
            self.dying = True
            self.state = "death"
            self.current_frame = 0
            self.frame_timer = 0

    def update(self, dt, player_x, player_y):
        if self.dying:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_speed:
                self.frame_timer = 0
                self.current_frame += 1
                if self.current_frame >= len(self.frames["death"]):
                    self.alive = False
            return

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

        if self.hit_flash > 0:
            self.hit_flash -= dt

        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            total = len(self.frames["idle"])
            self.current_frame = (self.current_frame + 1) % total

    def draw(self, surface):
        frame_list = self.frames[self.state]
        if self.current_frame >= len(frame_list):
            return

        frame = frame_list[self.current_frame]

        if self.hit_flash > 0:
            white_frame = frame.copy()
            white_frame.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
            frame = white_frame

        draw_x = int(self.x) - frame.get_width() // 2
        draw_y = int(self.y) - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))

        if self.enemy_type == "tank" and not self.dying:
            bar_w = 36
            bar_h = 4
            bx = int(self.x) - bar_w // 2
            by = int(self.y) - 26
            pygame.draw.rect(surface, (60, 0, 0), (bx, by, bar_w, bar_h))
            fill = int((self.hp / self.max_hp) * bar_w)
            pygame.draw.rect(surface, (200, 50, 0), (bx, by, fill, bar_h))