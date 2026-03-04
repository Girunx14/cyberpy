import pygame
import math
import random
from core.utils import draw_glow_rect, draw_glow_line


class GlitchText:
    def __init__(self, text, font, x, y, base_color):
        self.text       = text
        self.font       = font
        self.x          = x
        self.y          = y
        self.base_color = base_color

        self.glitch_timer    = 0
        self.glitch_interval = random.uniform(2.0, 4.0)
        self.glitch_active   = False
        self.glitch_duration = 0
        self.glitch_max      = 0.15
        self.offset_x        = 0

    def update(self, dt):
        self.glitch_timer += dt

        if self.glitch_timer >= self.glitch_interval:
            self.glitch_timer    = 0
            self.glitch_interval = random.uniform(2.0, 4.0)
            self.glitch_active   = True
            self.glitch_duration = 0

        if self.glitch_active:
            self.glitch_duration += dt
            self.offset_x = random.randint(-6, 6)

            if self.glitch_duration >= self.glitch_max:
                self.glitch_active = False
                self.offset_x      = 0

    def draw(self, surface):
        if self.glitch_active:
            red_surf = self.font.render(self.text, True, (255, 0, 80))
            surface.blit(red_surf, (self.x - 4 + self.offset_x, self.y))

            cyan_surf = self.font.render(self.text, True, (0, 255, 200))
            surface.blit(cyan_surf, (self.x + 4 + self.offset_x, self.y))

        main_surf = self.font.render(self.text, True, self.base_color)
        surface.blit(main_surf, (self.x + self.offset_x, self.y))


class MenuScreen:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.font_title  = pygame.font.SysFont("Courier New", 52, bold=True)
        self.font_sub    = pygame.font.SysFont("Courier New", 18, bold=True)
        self.font_small  = pygame.font.SysFont("Courier New", 14)
        self.font_medium = pygame.font.SysFont("Courier New", 22, bold=True)

        cx = screen_w // 2

        title_surf = self.font_title.render("CYBERPUNK HACKER", True, (255, 255, 255))
        title_x    = cx - title_surf.get_width() // 2
        self.title = GlitchText("CYBERPUNK HACKER", self.font_title, title_x, 80, (0, 255, 200))

        self.subtitle = GlitchText("DEFEND THE SYSTEM", self.font_sub, cx - 110, 148, (255, 0, 180))

        self.blink_timer  = 0
        self.blink_state  = True

        self.panel_y      = -400
        self.panel_target = screen_h // 2 - 160
        self.panel_speed  = 600

        self.deco_particles = []
        self.deco_timer     = 0

        self.ready = False

    def _spawn_deco_particle(self):
        self.deco_particles.append({
            "x":     random.randint(0, self.screen_w),
            "y":     random.randint(0, self.screen_h),
            "vx":    random.uniform(-20, 20),
            "vy":    random.uniform(-40, -10),
            "life":  random.uniform(2.0, 4.0),
            "age":   0,
            "size":  random.randint(1, 3),
            "color": random.choice([(0, 255, 200), (255, 0, 180), (255, 220, 0)]),
        })

    def update(self, dt):
        if self.panel_y < self.panel_target:
            self.panel_y += self.panel_speed * dt
            if self.panel_y >= self.panel_target:
                self.panel_y = self.panel_target
                self.ready   = True

        self.title.update(dt)
        self.subtitle.update(dt)

        self.blink_timer += dt
        if self.blink_timer >= 0.6:
            self.blink_timer = 0
            self.blink_state = not self.blink_state

        self.deco_timer += dt
        if self.deco_timer >= 0.1:
            self.deco_timer = 0
            self._spawn_deco_particle()

        for p in self.deco_particles:
            p["x"]   += p["vx"] * dt
            p["y"]   += p["vy"] * dt
            p["age"] += dt

        self.deco_particles = [
            p for p in self.deco_particles if p["age"] < p["life"]
        ]

    def draw(self, surface):
        cx = self.screen_w // 2

        for p in self.deco_particles:
            ratio = 1.0 - (p["age"] / p["life"])
            r = max(1, int(p["size"] * ratio))
            c = (
                int(p["color"][0] * ratio),
                int(p["color"][1] * ratio),
                int(p["color"][2] * ratio),
            )
            pygame.draw.circle(surface, c, (int(p["x"]), int(p["y"])), r)

        panel_w = 620
        panel_h = 380
        panel_x = cx - panel_w // 2
        panel_y = int(self.panel_y)

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((0, 5, 15, 210))
        surface.blit(panel, (panel_x, panel_y))

        draw_glow_rect(surface, (0, 255, 200), (panel_x, panel_y, panel_w, panel_h), 1, 3)

        draw_glow_line(surface, (0, 80, 60), (panel_x + 20, panel_y + 70), (panel_x + panel_w - 20, panel_y + 70), 1, 1)
        draw_glow_line(surface, (0, 80, 60), (panel_x + 20, panel_y + panel_h - 70), (panel_x + panel_w - 20, panel_y + panel_h - 70), 1, 1)

        self.title.draw(surface)
        self.subtitle.draw(surface)

        if not self.ready:
            return

        controls_y = panel_y + 90
        ctrl_title = self.font_medium.render("[ CONTROL INTERFACE ]", True, (0, 200, 160))
        surface.blit(ctrl_title, (cx - ctrl_title.get_width() // 2, controls_y))

        gestures = [
            ("✋  MANO ABIERTA",   "MOVER JUGADOR"),
            ("☝️  ÍNDICE ARRIBA",  "DISPARAR"),
            ("✊  PUÑO CERRADO",   "MODO DEFENSA"),
            ("⌨️  WASD / FLECHAS", "MOVER (TECLADO)"),
            ("⌨️  ESPACIO",        "DISPARAR (TECLADO)"),
        ]

        for i, (gesto, accion) in enumerate(gestures):
            gy = controls_y + 30 + i * 28
            gesto_surf  = self.font_small.render(gesto,  True, (0, 200, 160))
            accion_surf = self.font_small.render(accion, True, (255, 255, 255))
            sep_surf    = self.font_small.render("→",    True, (255, 0, 180))

            gx = cx - 220
            surface.blit(gesto_surf,  (gx, gy))
            surface.blit(sep_surf,    (gx + 180, gy))
            surface.blit(accion_surf, (gx + 210, gy))

        if self.blink_state:
            start_text  = "[ PRESS ENTER OR SPACE TO START ]"
            start_surf  = self.font_medium.render(start_text, True, (255, 220, 0))
            start_x     = cx - start_surf.get_width() // 2
            start_y     = panel_y + panel_h - 50
            surface.blit(start_surf, (start_x, start_y))

        corner = 12
        corners = [
            (panel_x,             panel_y),
            (panel_x + panel_w,   panel_y),
            (panel_x,             panel_y + panel_h),
            (panel_x + panel_w,   panel_y + panel_h),
        ]
        for (cx2, cy2) in corners:
            pygame.draw.circle(surface, (0, 255, 200), (cx2, cy2), corner // 2)