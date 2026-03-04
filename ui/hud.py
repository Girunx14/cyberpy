import pygame
import math
from core.utils import draw_glow_rect, draw_glow_line


class HealthBar:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.color = color
        self.value = 100
        self.display_value = 100
        self.pulse_timer = 0

    def set_value(self, val):
        self.value = max(0, min(100, val))

    def update(self, dt):
        self.display_value += (self.value - self.display_value) * 8 * dt
        self.pulse_timer += dt

    def draw(self, surface, font, label):
        pygame.draw.rect(surface, (10, 10, 20), (self.x, self.y, self.w, self.h))
        fill_w = int((self.display_value / 100) * self.w)

        if self.value < 30:
            pulse = abs(math.sin(self.pulse_timer * 6))
            bar_color = (int(255 * pulse), int(50 * pulse), int(50 * pulse))
        else:
            bar_color = self.color

        if fill_w > 0:
            pygame.draw.rect(surface, bar_color, (self.x, self.y, fill_w, self.h))

        draw_glow_rect(surface, self.color, (self.x, self.y, self.w, self.h), 1, 2)

        # Líneas de segmento decorativas
        for i in range(1, 10):
            lx = self.x + i * (self.w // 10)
            pygame.draw.line(surface, (5, 5, 15), (lx, self.y), (lx, self.y + self.h), 1)

        surface.blit(font.render(f"{label}: {int(self.display_value)}%", True, self.color), (self.x, self.y - 18))


class ScoreDisplay:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.score = 0
        self.display_score = 0
        self.flash_timer = 0
        self.flashing = False

    def add_score(self, amount):
        self.score += amount
        self.flashing = True
        self.flash_timer = 0

    def update(self, dt):
        diff = self.score - self.display_score
        if abs(diff) > 1:
            self.display_score += diff * 6 * dt
        else:
            self.display_score = self.score
        if self.flashing:
            self.flash_timer += dt
            if self.flash_timer > 0.3:
                self.flashing = False

    def draw(self, surface, font_large, font_small):
        color = (255, 255, 255) if self.flashing else self.color
        surface.blit(font_small.render("SCORE", True, self.color), (self.x, self.y))
        surface.blit(font_large.render(f"{int(self.display_score):07d}", True, color), (self.x, self.y + 16))


class MiniMap:
    def __init__(self, x, y, width, height, game_w, game_h):
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.game_w = game_w
        self.game_h = game_h
        self.pulse_timer = 0

    def update(self, dt):
        self.pulse_timer += dt

    def draw(self, surface, font, player_x, player_y):
        bg = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        bg.fill((0, 10, 20, 180))
        surface.blit(bg, (self.x, self.y))
        draw_glow_rect(surface, (0, 150, 120), (self.x, self.y, self.w, self.h), 1, 2)

        cx, cy = self.x + self.w // 2, self.y + self.h // 2
        pygame.draw.line(surface, (0, 40, 30), (self.x, cy), (self.x + self.w, cy), 1)
        pygame.draw.line(surface, (0, 40, 30), (cx, self.y), (cx, self.y + self.h), 1)

        px = self.x + int((player_x / self.game_w) * self.w)
        py = self.y + int((player_y / self.game_h) * self.h)
        pulse_r = int(3 + abs(math.sin(self.pulse_timer * 3)) * 3)
        pygame.draw.circle(surface, (0, 80, 60), (px, py), pulse_r + 2)
        pygame.draw.circle(surface, (0, 255, 200), (px, py), pulse_r)
        surface.blit(font.render("SYS MAP", True, (0, 150, 120)), (self.x + 2, self.y + self.h + 2))


class HUD:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.font_small  = pygame.font.SysFont("Courier New", 13, bold=True)
        self.font_medium = pygame.font.SysFont("Courier New", 16, bold=True)
        self.font_large  = pygame.font.SysFont("Courier New", 22, bold=True)

        self.health = HealthBar(20, screen_h - 40,  200, 14, (0, 255, 200))
        self.shield = HealthBar(20, screen_h - 75,  200, 14, (0, 150, 255))
        self.score  = ScoreDisplay(screen_w - 160, 20, (0, 255, 200))
        self.minimap = MiniMap(screen_w - 130, screen_h - 130, 110, 110, screen_w, screen_h)

        self.game_time = 0
        self.alert_text = ""
        self.alert_timer = 0
        self.alert_duration = 2.0

    def show_alert(self, text):
        self.alert_text = text
        self.alert_timer = 0

    def add_score(self, amount):
        self.score.add_score(amount)

    def update(self, dt):
        self.health.update(dt)
        self.shield.update(dt)
        self.score.update(dt)
        self.minimap.update(dt)
        self.game_time += dt
        if self.alert_timer < self.alert_duration:
            self.alert_timer += dt

    def draw(self, surface, player_x, player_y):
        self.health.draw(surface, self.font_small, "INTEGRITY")
        self.shield.draw(surface, self.font_small, "SHIELD")
        self.score.draw(surface, self.font_large, self.font_small)
        self.minimap.draw(surface, self.font_small, player_x, player_y)

        minutes = int(self.game_time) // 60
        seconds = int(self.game_time) % 60
        surface.blit(
            self.font_medium.render(f"TIME  {minutes:02d}:{seconds:02d}", True, (0, 200, 160)),
            (self.screen_w // 2 - 60, 15)
        )

        draw_glow_line(surface, (0, 100, 80), (0, 35), (self.screen_w, 35), 1, 2)

        if self.alert_timer < self.alert_duration:
            alpha = 1.0 - (self.alert_timer / self.alert_duration)
            pulse = abs(math.sin(self.alert_timer * 8))
            alert_color = (int(255 * pulse * alpha), int(50 * alpha), int(50 * alpha))
            alert_surf = self.font_large.render(self.alert_text, True, alert_color)
            surface.blit(alert_surf, (self.screen_w // 2 - alert_surf.get_width() // 2, self.screen_h // 2 - 40))