import pygame
import math
from core.settings import PLAYER_SPEED, PLAYER_SIZE


def create_player_frames():
    frames = {"idle": [], "move": [], "attack": []}
    size = PLAYER_SIZE

    for i in range(6):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        bob = math.sin(i / 6 * math.pi * 2) * 2
        cx, cy = size // 2, size // 2 + int(bob)
        points = []
        for j in range(6):
            angle = math.pi / 6 + j * math.pi / 3
            points.append((cx + math.cos(angle) * 16, cy + math.sin(angle) * 16))
        pygame.draw.polygon(surface, (0, 200, 160), points)
        pygame.draw.polygon(surface, (0, 255, 200), points, 2)
        pulse_r = 5 + int(abs(math.sin(i / 6 * math.pi * 2)) * 3)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), pulse_r)
        pygame.draw.circle(surface, (0, 255, 200), (cx, cy), pulse_r, 1)
        frames["idle"].append(surface)

    for i in range(4):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        lean = math.sin(i / 4 * math.pi * 2) * 3
        points = []
        for j in range(6):
            angle = math.pi / 6 + j * math.pi / 3
            points.append((cx + math.cos(angle) * 16 + lean, cy + math.sin(angle) * 14))
        pygame.draw.polygon(surface, (0, 160, 220), points)
        pygame.draw.polygon(surface, (0, 180, 255), points, 2)
        for k in range(3):
            lx = cx - 18 - k * 5
            ly = cy - 4 + k * 4
            pygame.draw.line(surface, (0, 100, 180), (lx, ly), (lx - 6, ly), 1)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 5)
        frames["move"].append(surface)

    for i in range(5):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        points = []
        for j in range(6):
            angle = math.pi / 6 + j * math.pi / 3
            radius = 16 + (8 if i == 2 else 0)
            points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
        fill_color   = (200, 0, 140) if i == 2 else (160, 0, 100)
        border_color = (255, 0, 180) if i == 2 else (200, 0, 140)
        pygame.draw.polygon(surface, fill_color, points)
        pygame.draw.polygon(surface, border_color, points, 2)
        if i == 2:
            for j in range(6):
                angle = j * math.pi / 3
                ex = cx + math.cos(angle) * 26
                ey = cy + math.sin(angle) * 26
                pygame.draw.line(surface, (255, 100, 200), (cx, cy), (int(ex), int(ey)), 2)
        pygame.draw.circle(surface, (255, 200, 255), (cx, cy), 5)
        frames["attack"].append(surface)

    return frames


class Player:
    def __init__(self, x, y, screen_w, screen_h):
        self.x = x
        self.y = y
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.frames = create_player_frames()
        self.state = "idle"
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_speeds = {"idle": 0.12, "move": 0.08, "attack": 0.07}
        self.speed = PLAYER_SPEED
        self.is_moving = False

    def set_state(self, new_state):
        if new_state != self.state:
            self.state = new_state
            self.current_frame = 0
            self.frame_timer = 0

    def update(self, dt, keys, hand_data=None):
        moving = False

        if hand_data and hand_data["detected"]:
            target_x = hand_data["x"]
            target_y = hand_data["y"]
            self.x += (target_x - self.x) * 8 * dt
            self.y += (target_y - self.y) * 8 * dt
            dist = abs(target_x - self.x) + abs(target_y - self.y)
            if dist > 5:
                moving = True
            if hand_data["gesture"] == "fist":
                self.set_state("idle")
            elif hand_data["gesture"] == "point":
                self.set_state("attack")
            elif moving:
                self.set_state("move")
            else:
                self.set_state("idle")
        else:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.x -= self.speed * dt
                moving = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.x += self.speed * dt
                moving = True
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.y -= self.speed * dt
                moving = True
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.y += self.speed * dt
                moving = True
            if keys[pygame.K_SPACE]:
                self.set_state("attack")
            elif moving:
                self.set_state("move")
            else:
                self.set_state("idle")

        half = PLAYER_SIZE // 2
        self.x = max(half, min(self.screen_w - half, self.x))
        self.y = max(half, min(self.screen_h - half, self.y))
        self.is_moving = moving

        self.frame_timer += dt
        if self.frame_timer >= self.frame_speeds[self.state]:
            self.frame_timer = 0
            total = len(self.frames[self.state])
            self.current_frame = (self.current_frame + 1) % total
            if self.state == "attack" and self.current_frame == 0:
                self.set_state("idle")

    def draw(self, surface):
        frame = self.frames[self.state][self.current_frame]
        draw_x = int(self.x) - frame.get_width() // 2
        draw_y = int(self.y) - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))