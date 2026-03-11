# entities/player.py
import pygame
import math
from core.settings import PLAYER_SPEED, PLAYER_SIZE


def create_player_frames(player_id=1):
    """Genera frames con colores diferentes según el ID del jugador."""
    frames = {"idle": [], "move": [], "attack": []}
    size   = PLAYER_SIZE

    # Jugador 1: cyan / Jugador 2: magenta
    if player_id == 1:
        color_fill   = (0, 200, 160)
        color_border = (0, 255, 200)
        color_move   = (0, 160, 220)
        color_attack = (200, 0, 140)
        color_atk_b  = (255, 0, 180)
    else:
        color_fill   = (180, 0, 140)
        color_border = (255, 0, 200)
        color_move   = (200, 0, 180)
        color_attack = (140, 100, 0)
        color_atk_b  = (255, 180, 0)

    # --- IDLE ---
    for i in range(6):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        bob = math.sin(i / 6 * math.pi * 2) * 2
        cx, cy = size // 2, size // 2 + int(bob)
        points = []
        for j in range(6):
            angle = math.pi / 6 + j * math.pi / 3
            points.append((cx + math.cos(angle) * 16, cy + math.sin(angle) * 16))
        pygame.draw.polygon(surface, color_fill,   points)
        pygame.draw.polygon(surface, color_border, points, 2)
        pulse_r = 5 + int(abs(math.sin(i / 6 * math.pi * 2)) * 3)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), pulse_r)
        pygame.draw.circle(surface, color_border,   (cx, cy), pulse_r, 1)
        frames["idle"].append(surface)

    # --- MOVE ---
    for i in range(4):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy  = size // 2, size // 2
        lean    = math.sin(i / 4 * math.pi * 2) * 3
        points  = []
        for j in range(6):
            angle = math.pi / 6 + j * math.pi / 3
            points.append((cx + math.cos(angle) * 16 + lean, cy + math.sin(angle) * 14))
        pygame.draw.polygon(surface, color_move,   points)
        pygame.draw.polygon(surface, color_border, points, 2)
        for k in range(3):
            lx = cx - 18 - k * 5
            ly = cy - 4 + k * 4
            pygame.draw.line(surface, color_fill, (lx, ly), (lx - 6, ly), 1)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 5)
        frames["move"].append(surface)

    # --- ATTACK ---
    for i in range(5):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy  = size // 2, size // 2
        points  = []
        for j in range(6):
            angle  = math.pi / 6 + j * math.pi / 3
            radius = 16 + (8 if i == 2 else 0)
            points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
        fill   = color_attack if i != 2 else color_atk_b
        border = color_atk_b
        pygame.draw.polygon(surface, fill,   points)
        pygame.draw.polygon(surface, border, points, 2)
        if i == 2:
            for j in range(6):
                angle = j * math.pi / 3
                ex = cx + math.cos(angle) * 26
                ey = cy + math.sin(angle) * 26
                pygame.draw.line(surface, color_atk_b, (cx, cy), (int(ex), int(ey)), 2)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 5)
        frames["attack"].append(surface)

    return frames


class Player:
    def __init__(self, x, y, screen_w, screen_h, player_id=1):
        self.x         = x
        self.y         = y
        self.screen_w  = screen_w
        self.screen_h  = screen_h
        self.player_id = player_id
        self.frames    = create_player_frames(player_id)

        self.state         = "idle"
        self.current_frame = 0
        self.frame_timer   = 0
        self.frame_speeds  = {"idle": 0.12, "move": 0.08, "attack": 0.07}
        self.speed         = PLAYER_SPEED
        self.is_moving     = False

        # Controles de teclado para cada jugador
        if player_id == 1:
            self.keys_map = {
                "up":    [pygame.K_w,     pygame.K_UP],
                "down":  [pygame.K_s,     pygame.K_DOWN],
                "left":  [pygame.K_a,     pygame.K_LEFT],
                "right": [pygame.K_d,     pygame.K_RIGHT],
                "shoot": [pygame.K_SPACE],
            }
        else:
            # Jugador 2 usa numpad o IJKL
            self.keys_map = {
                "up":    [pygame.K_i, pygame.K_KP8],
                "down":  [pygame.K_k, pygame.K_KP5],
                "left":  [pygame.K_j, pygame.K_KP4],
                "right": [pygame.K_l, pygame.K_KP6],
                "shoot": [pygame.K_u, pygame.K_KP0],
            }

    def set_state(self, new_state):
        if new_state != self.state:
            self.state         = new_state
            self.current_frame = 0
            self.frame_timer   = 0

    def _key_pressed(self, keys, action):
        return any(keys[k] for k in self.keys_map[action])

    def update(self, dt, keys, hand_data=None):
        moving = False

        if hand_data and hand_data["detected"]:
            target_x = hand_data["x"]
            target_y = hand_data["y"]
            self.x  += (target_x - self.x) * 8 * dt
            self.y  += (target_y - self.y) * 8 * dt
            dist     = abs(target_x - self.x) + abs(target_y - self.y)
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
            if self._key_pressed(keys, "left"):
                self.x -= self.speed * dt
                moving  = True
            if self._key_pressed(keys, "right"):
                self.x += self.speed * dt
                moving  = True
            if self._key_pressed(keys, "up"):
                self.y -= self.speed * dt
                moving  = True
            if self._key_pressed(keys, "down"):
                self.y += self.speed * dt
                moving  = True

            if self._key_pressed(keys, "shoot"):
                self.set_state("attack")
            elif moving:
                self.set_state("move")
            else:
                self.set_state("idle")

        half      = PLAYER_SIZE // 2
        self.x    = max(half, min(self.screen_w - half, self.x))
        self.y    = max(half, min(self.screen_h - half, self.y))
        self.is_moving = moving

        self.frame_timer += dt
        if self.frame_timer >= self.frame_speeds[self.state]:
            self.frame_timer   = 0
            total              = len(self.frames[self.state])
            self.current_frame = (self.current_frame + 1) % total
            if self.state == "attack" and self.current_frame == 0:
                self.set_state("idle")

    def draw(self, surface):
        frame  = self.frames[self.state][self.current_frame]
        draw_x = int(self.x) - frame.get_width()  // 2
        draw_y = int(self.y) - frame.get_height() // 2
        surface.blit(frame, (draw_x, draw_y))