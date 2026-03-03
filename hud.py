import pygame
import math

def draw_glow_rect(surface, color, rect, width, blur_levels=3):
    x, y, w, h = rect
    for i in range(blur_levels, 0, -1):
        #* cada nivel es mas grande y mas oscuro
        alpha = int(60 / i)
        glow_color = (
            min(255, color[0]),
            min(255, color[1]),
            min(255, color[2])
        )
        #* oscurecemos el color según el nivel
        dim = i / blur_levels
        dimmed = (
            int(glow_color[0] * dim),
            int(glow_color[1] * dim),
            int(glow_color[2] * dim),
        )
        expand = i * 2
        pygame.draw.rect(
            surface, dimmed,
            (x - expand, y - expand, w + expand * 2, h + expand * 2),
            width + i
        )
    #* linea principal encima de todo
    pygame.draw.rect(surface, color, rect, width)

def draw_glow_line(surface, color, start, end, width=1, blur_levels=3):
    for i in range(blur_levels, 0, -1):
        dim = i / blur_levels
        dimmed = (
            int(color[0] * dim),
            int(color[1] * dim),
            int(color[2] * dim),
        )
        pygame.draw.line(surface, dimmed, start, end, width + i * 2)
    pygame.draw.line(surface, color, start, end, width)


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
        diff = self.value - self.display_value
        self.display_value += diff * 8 * dt

        self.pulse_timer += dt

    def draw(self, surface, font, label):
        #* fondo de la barra
        pygame.draw.rect(surface, (10, 10, 20), (self.x, self.y, self.w, self.h))

        fill_w = int((self.display_value / 100) * self.w)
        #* color cambia si la vida es baja
        if self.value < 30:
            #* parpadeo de advertencia
            pulse = abs(math.sin(self.pulse_timer * 6))
            bar_color = (
                int(255 * pulse),
                int(50 * pulse),
                int(50 * pulse),
            )
        else:
            bar_color = self.color

        if fill_w > 0:
            pygame.draw.rect(surface, bar_color, (self.x, self.y, fill_w, self.h))

        #* neon
        draw_glow_rect(surface, self.color, (self.x, self.y, self.w, self.h), 1, 2)

        segments = 10
        seg_w = self.w // segments
        for i in range(1, segments):
            lx = self.x + i * seg_w
            pygame.draw.line(surface, (5, 5, 15), (lx, self.y), (lx, self.y + self.h), 1)

        #* etiqueta y valor
        text = font.render(f"{label}: {int(self.display_value)}%", True, self.color)
        surface.blit(text, (self.x, self.y - 18))


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
        #* color con flash q suma los puntos
        color = (255, 255, 255) if self.flashing else self.color

        label = font_small.render("SCORE", True, self.color)
        value = font_large.render(f"{int(self.display_score):07d}", True, color)

        surface.blit(label, (self.x, self.y))
        surface.blit(value, (self.x, self.y + 16))

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

    def draw(self, surface, font, player_x, player_y, enemies=None):
        #* fondo semitransparente
        bg = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        bg.fill((0, 10, 20, 180))
        surface.blit(bg, (self.x, self.y))
        #* borde neon
        draw_glow_rect(surface, (0, 150, 120), (self.x, self.y, self.w, self.h), 1, 2)

        #* cruz central
        cx = self.x + self.w // 2
        cy = self.y + self.h // 2
        pygame.draw.line(surface, (0, 40, 30), (self.x, cy), (self.x + self.w, cy), 1)
        pygame.draw.line(surface, (0, 40, 30), (cx, self.y), (cx, self.y + self.h), 1)

        #* posicion del jugador escalada al minimapa
        px = self.x + int((player_x / self.game_w) * self.w)
        py = self.y + int((player_y / self.game_h) * self.h)

        #* pulso del jugador en el minimapa
        pulse = abs(math.sin(self.pulse_timer * 3))
        pulse_r = int(3 + pulse * 3)
        pygame.draw.circle(surface, (0, 80, 60), (px, py), pulse_r + 2)
        pygame.draw.circle(surface, (0, 255, 200), (px, py), pulse_r)

        label = font.render("SYS MAP", True, (0, 150, 120))
        surface.blit(label, (self.x + 2, self.y + self.h + 2))

class HUD:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.font_small  = pygame.font.SysFont("Courier New", 13, bold=True)
        self.font_medium = pygame.font.SysFont("Courier New", 16, bold=True)
        self.font_large  = pygame.font.SysFont("Courier New", 22, bold=True)
        #* componentes
        self.health = HealthBar(
            x=20, y=screen_h - 40,
            width=200, height=14,
            color=(0, 255, 200)
        )
        self.shield = HealthBar(
            x=20, y=screen_h - 75,
            width=200, height=14,
            color=(0, 150, 255)
        )
        self.score = ScoreDisplay(
            x=screen_w - 160, y=20,
            color=(0, 255, 200)
        )
        self.minimap = MiniMap(
            x=screen_w - 130, y=screen_h - 130,
            width=110, height=110,
            game_w=screen_w, game_h=screen_h
        )
        #* timmer de partida
        self.game_time = 0
        #* mensaje de advertencia
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
        #* barras de estado
        self.health.draw(surface, self.font_small, "INTEGRITY")
        self.shield.draw(surface, self.font_small, "SHIELD")

        #* puntuacion
        self.score.draw(surface, self.font_large, self.font_small)

        #* minimapa
        self.minimap.draw(surface, self.font_small, player_x, player_y)

        #* tiempo de partida
        minutes = int(self.game_time) // 60
        seconds = int(self.game_time) % 60
        time_text = self.font_medium.render(f"TIME  {minutes:02d}:{seconds:02d}", True, (0, 200, 160))
        surface.blit(time_text, (self.screen_w // 2 - 60, 15))

        #* linea decorativa superior
        draw_glow_line(surface, (0, 100, 80), (0, 35), (self.screen_w, 35), 1, 2)

        #* alerta centrada 
        if self.alert_timer < self.alert_duration:
            alpha = 1.0 - (self.alert_timer / self.alert_duration)
            pulse = abs(math.sin(self.alert_timer * 8))
            alert_color = (
                int(255 * pulse * alpha),
                int(50 * alpha),
                int(50 * alpha),
            )
            alert_surf = self.font_large.render(self.alert_text, True, alert_color)
            ax = self.screen_w // 2 - alert_surf.get_width() // 2
            ay = self.screen_h // 2 - 40
            surface.blit(alert_surf, (ax, ay))