import pygame
import math
import random


POWERUP_CONFIGS = {
    "shield": {
        "color":  (0, 150, 255),
        "label":  "SHIELD",
        "symbol": "S",
    },
    "health": {
        "color":  (0, 255, 80),
        "label":  "INTEGRITY",
        "symbol": "+",
    },
    "rapid_fire": {
        "color":  (255, 220, 0),
        "label":  "RAPID FIRE",
        "symbol": "R",
    },
    "triple_shot": {
        "color":  (255, 0, 180),
        "label":  "TRIPLE SHOT",
        "symbol": "T",
    },
}


class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.powerup_type = powerup_type
        self.radius = 14
        self.alive  = True

        cfg = POWERUP_CONFIGS[powerup_type]
        self.color  = cfg["color"]
        self.label  = cfg["label"]
        self.symbol = cfg["symbol"]

        self.font = pygame.font.SysFont("Courier New", 14, bold=True)

        self.float_timer = random.uniform(0, math.pi * 2)
        self.float_speed = 2.5
        self.float_amp   = 4

        self.lifetime = 8.0
        self.age      = 0

        self.scale    = 0.0
        self.born     = True

    def update(self, dt):
        self.float_timer += self.float_speed * dt
        self.age         += dt

        if self.scale < 1.0:
            self.scale = min(1.0, self.scale + dt * 6)

        if self.age >= self.lifetime:
            self.alive = False

    def draw(self, surface):
        life_ratio = 1.0 - (self.age / self.lifetime)
        if life_ratio < 0.25:
            if int(self.age * 8) % 2 == 0:
                return

        float_offset = math.sin(self.float_timer) * self.float_amp
        draw_y = int(self.y + float_offset)
        draw_x = int(self.x)

        r = int(self.radius * self.scale)
        if r < 1:
            return

        for i in range(3, 0, -1):
            glow_r = r + i * 3
            dim    = i / 3
            glow_color = (
                int(self.color[0] * dim * 0.4),
                int(self.color[1] * dim * 0.4),
                int(self.color[2] * dim * 0.4),
            )
            pygame.draw.circle(surface, glow_color, (draw_x, draw_y), glow_r)

        pygame.draw.circle(surface, self.color, (draw_x, draw_y), r)

        pygame.draw.circle(surface, (255, 255, 255), (draw_x, draw_y), r, 1)

        sym_surf = self.font.render(self.symbol, True, (255, 255, 255))
        surface.blit(sym_surf, (draw_x - sym_surf.get_width() // 2, draw_y - sym_surf.get_height() // 2))

        label_surf = self.font.render(self.label, True, self.color)
        surface.blit(label_surf, (draw_x - label_surf.get_width() // 2, draw_y - r - 18))


class PowerUpManager:
    def __init__(self):
        self.powerups = []

        self.active_effects = {
            "rapid_fire":   0.0,
            "triple_shot":  0.0,
        }

        self.drop_chances = {
            "basic": 0.25,
            "fast":  0.30,
            "tank":  0.80,
        }

        self.font_effect = pygame.font.SysFont("Courier New", 13, bold=True)

    def try_spawn(self, x, y, enemy_type):
        import random
        chance = self.drop_chances.get(enemy_type, 0.2)
        if random.random() > chance:
            return

        types   = ["shield", "health", "rapid_fire", "triple_shot"]
        weights = [0.30,     0.30,     0.20,         0.20]
        chosen  = random.choices(types, weights=weights, k=1)[0]

        self.powerups.append(PowerUp(x, y, chosen))

    def update(self, dt):
        for p in self.powerups:
            p.update(dt)
        self.powerups = [p for p in self.powerups if p.alive]

        for effect in self.active_effects:
            if self.active_effects[effect] > 0:
                self.active_effects[effect] -= dt

    def check_collection(self, player_x, player_y, player_radius=24):
        collected = []
        for p in self.powerups:
            if not p.alive:
                continue
            dist = math.sqrt((p.x - player_x)**2 + (p.y - player_y)**2)
            if dist < p.radius + player_radius:
                p.alive = False
                collected.append(p.powerup_type)
        return collected

    def activate_effect(self, effect_name, duration):
        self.active_effects[effect_name] = duration

    def is_active(self, effect_name):
        return self.active_effects.get(effect_name, 0) > 0

    def draw(self, surface):
        for p in self.powerups:
            p.draw(surface)

    def draw_active_effects(self, surface, screen_w, screen_h):
        active = [(k, v) for k, v in self.active_effects.items() if v > 0]
        if not active:
            return

        cfg = POWERUP_CONFIGS
        x = screen_w - 160
        y = screen_h - 110

        title = self.font_effect.render("ACTIVE BUFFS", True, (0, 150, 120))
        surface.blit(title, (x, y - 18))

        for i, (effect, remaining) in enumerate(active):
            color = cfg[effect]["color"]
            label = cfg[effect]["label"]
            bar_w = 120
            fill  = int((remaining / 10.0) * bar_w)

            ey = y + i * 28

            pygame.draw.rect(surface, (10, 10, 20),   (x, ey, bar_w, 10))
            pygame.draw.rect(surface, color,           (x, ey, max(0, fill), 10))
            pygame.draw.rect(surface, color,           (x, ey, bar_w, 10), 1)

            text = self.font_effect.render(f"{label} {remaining:.1f}s", True, color)
            surface.blit(text, (x, ey + 11))