# core/game.py
import pygame
import sys
import math
import cv2

from core.settings import SCREEN_W, SCREEN_H, FPS
from systems.background import CyberpunkBackground
from systems.particles import ParticleSystem
from systems.audio import AudioManager
from systems.hand_controller import HandController
from systems.wave_manager import WaveManager
from entities.player import Player
from entities.projectile import Projectile
from entities.powerup import PowerUpManager
from ui.hud import HUD
from ui.screens import MenuScreen, PauseScreen


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Cyberpunk Hacker")
        self.clock = pygame.time.Clock()

        self.bg        = CyberpunkBackground(SCREEN_W, SCREEN_H)
        self.particles = ParticleSystem()
        self.audio     = AudioManager()
        self.hand      = HandController(SCREEN_W, SCREEN_H)
        self.waves     = WaveManager(SCREEN_W, SCREEN_H)
        self.hud       = HUD(SCREEN_W, SCREEN_H)
        self.menu      = MenuScreen(SCREEN_W, SCREEN_H)
        self.pause     = PauseScreen(SCREEN_W, SCREEN_H)
        self.powerups  = PowerUpManager()

        self.player1 = Player(SCREEN_W // 3,     SCREEN_H // 2, SCREEN_W, SCREEN_H, player_id=1)
        self.player2 = Player(SCREEN_W * 2 // 3, SCREEN_H // 2, SCREEN_W, SCREEN_H, player_id=2)
        self.players = [self.player1, self.player2]

        self.projectiles = []
        self.font_hud    = pygame.font.SysFont("Courier New", 13, bold=True)
        self.font_large  = pygame.font.SysFont("Courier New", 36, bold=True)
        self.font_medium = pygame.font.SysFont("Courier New", 20, bold=True)

        self.game_state    = "menu"
        self.last_gestures = {"Left": "none", "Right": "none"}

        self.shoot_cooldowns       = {1: 0, 2: 0}
        self.shoot_cooldown_max    = 0.25
        self.player_invincibles    = {1: 0, 2: 0}
        self.player_invincible_max = 1.5
        self.player_dead           = {1: False, 2: False}

        self.audio.start_bgm()
        self.hand.start()

    def _start_game(self):
        self.game_state = "playing"
        self.hud.show_alert("SYSTEM BREACH DETECTED")

    def _restart(self):
        self.waves       = WaveManager(SCREEN_W, SCREEN_H)
        self.player1     = Player(SCREEN_W // 3,     SCREEN_H // 2, SCREEN_W, SCREEN_H, player_id=1)
        self.player2     = Player(SCREEN_W * 2 // 3, SCREEN_H // 2, SCREEN_W, SCREEN_H, player_id=2)
        self.players     = [self.player1, self.player2]
        self.hud         = HUD(SCREEN_W, SCREEN_H)
        self.menu        = MenuScreen(SCREEN_W, SCREEN_H)
        self.pause       = PauseScreen(SCREEN_W, SCREEN_H)
        self.powerups    = PowerUpManager()
        self.projectiles = []
        self.game_state  = "menu"
        self.last_gestures      = {"Left": "none", "Right": "none"}
        self.shoot_cooldowns    = {1: 0, 2: 0}
        self.player_invincibles = {1: 0, 2: 0}
        self.player_dead        = {1: False, 2: False}

    def _get_nearest_enemy(self, from_x, from_y):
        enemies = self.waves.get_enemies()
        if not enemies:
            return None
        return min(enemies, key=lambda e: math.sqrt((e.x - from_x)**2 + (e.y - from_y)**2))

    def _get_nearest_enemy_target(self, enemy):
        """Retorna coordenadas del jugador vivo más cercano al enemigo."""
        candidates = []
        if not self.player_dead[1]:
            d1 = math.sqrt((enemy.x - self.player1.x)**2 + (enemy.y - self.player1.y)**2)
            candidates.append((d1, self.player1.x, self.player1.y))
        if not self.player_dead[2]:
            d2 = math.sqrt((enemy.x - self.player2.x)**2 + (enemy.y - self.player2.y)**2)
            candidates.append((d2, self.player2.x, self.player2.y))
        if not candidates:
            return (SCREEN_W // 2, SCREEN_H // 2)
        candidates.sort(key=lambda c: c[0])
        return (candidates[0][1], candidates[0][2])

    def _shoot_toward(self, player, target_x, target_y):
        pid = player.player_id
        if self.shoot_cooldowns[pid] > 0:
            return
        cooldown = self.shoot_cooldown_max * 0.5 if self.powerups.is_active("rapid_fire") else self.shoot_cooldown_max
        self.shoot_cooldowns[pid] = cooldown

        if self.powerups.is_active("triple_shot"):
            dx         = target_x - player.x
            dy         = target_y - player.y
            base_angle = math.atan2(dy, dx)
            for offset in [-0.26, 0, 0.26]:
                angle = base_angle + offset
                tx = player.x + math.cos(angle) * 300
                ty = player.y + math.sin(angle) * 300
                self.projectiles.append(Projectile(player.x, player.y, tx, ty))
        else:
            self.projectiles.append(Projectile(player.x, player.y, target_x, target_y))

        self.audio.play("shoot")
        self.hud.add_score(5)

    def _shoot_at_nearest(self, player):
        enemy = self._get_nearest_enemy(player.x, player.y)
        if enemy:
            self._shoot_toward(player, enemy.x, enemy.y)

    def _apply_powerup(self, powerup_type):
        self.audio.play("explosion")
        if powerup_type == "health":
            self.hud.health_p1.set_value(self.hud.health_p1.value + 25)
            self.hud.health_p2.set_value(self.hud.health_p2.value + 25)
            self.hud.show_alert("INTEGRITY RESTORED +25")
        elif powerup_type == "shield":
            self.hud.shield_p1.set_value(self.hud.shield_p1.value + 30)
            self.hud.shield_p2.set_value(self.hud.shield_p2.value + 30)
            self.hud.show_alert("SHIELD RECHARGED +30")
        elif powerup_type == "rapid_fire":
            self.powerups.activate_effect("rapid_fire", 8.0)
            self.hud.show_alert("RAPID FIRE ACTIVATED")
            for p in self.players:
                self.particles.emit(int(p.x), int(p.y), count=20, color=(255, 220, 0))
        elif powerup_type == "triple_shot":
            self.powerups.activate_effect("triple_shot", 10.0)
            self.hud.show_alert("TRIPLE SHOT ACTIVATED")
            for p in self.players:
                self.particles.emit(int(p.x), int(p.y), count=20, color=(255, 0, 180))

    def _check_collisions(self):
        enemies     = self.waves.get_enemies()
        health_bars = {1: self.hud.health_p1, 2: self.hud.health_p2}

        for proj in self.projectiles:
            if not proj.alive:
                continue
            for enemy in enemies:
                if enemy.dying:
                    continue
                dist = math.sqrt((proj.x - enemy.x)**2 + (proj.y - enemy.y)**2)
                if dist < proj.radius + enemy.radius:
                    proj.alive = False
                    enemy.take_damage()
                    self.particles.emit(int(enemy.x), int(enemy.y), count=15, color=(255, 80, 80))
                    self.audio.play("explosion")
                    if enemy.dying:
                        self.hud.add_score(enemy.score_value)
                        self.particles.emit(int(enemy.x), int(enemy.y), count=30, color=(255, 50, 50))
                        self.powerups.try_spawn(int(enemy.x), int(enemy.y), enemy.enemy_type)

        for player in self.players:
            pid = player.player_id
            if self.player_dead[pid]:
                continue
            if self.player_invincibles[pid] > 0:
                continue

            health_bar = self.hud.health_p1 if pid == 1 else self.hud.health_p2
            shield_bar = self.hud.shield_p1 if pid == 1 else self.hud.shield_p2

            for enemy in enemies:
                if enemy.dying:
                    continue
                dist = math.sqrt((enemy.x - player.x)**2 + (enemy.y - player.y)**2)
                if dist < enemy.radius + 20:
                    self.player_invincibles[pid] = self.player_invincible_max
                    self.particles.emit(int(player.x), int(player.y), count=20, color=(255, 0, 100))
                    self.audio.play("explosion")

                    # El escudo absorbe el daño primero
                    if shield_bar.value > 0:
                        shield_bar.set_value(shield_bar.value - 20)
                        self.hud.show_alert(f"P{pid} SHIELD HIT")
                    else:
                        # Sin escudo el daño va directo a la vida
                        health_bar.set_value(health_bar.value - 20)
                        self.hud.show_alert(f"P{pid} INTEGRITY COMPROMISED")

                    if health_bar.value <= 0:
                        self.player_dead[pid] = True
                        player.is_dead = True
                        self.hud.show_alert(f"P{pid} DISCONNECTED")
                        self.particles.emit(int(player.x), int(player.y), count=50, color=(255, 0, 80))

        if self.player_dead[1] and self.player_dead[2]:
            self.game_state = "game_over"

        self.projectiles = [p for p in self.projectiles if p.alive]

    def handle_events(self, hands):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.hand.stop()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    if event.key == pygame.K_ESCAPE:
                        self.hand.stop()
                        pygame.quit()
                        sys.exit()
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        if self.menu.ready:
                            self._start_game()

                elif self.game_state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "paused"
                        self.pause = PauseScreen(SCREEN_W, SCREEN_H)
                    elif event.key == pygame.K_SPACE:
                        if not self.player_dead[1]:
                            self._shoot_at_nearest(self.player1)
                    elif event.key in (pygame.K_u, pygame.K_KP0):
                        if not self.player_dead[2]:
                            self._shoot_at_nearest(self.player2)

                elif self.game_state == "paused":
                    action = self.pause.handle_input(event)
                    if action == "RESUME":
                        self.game_state = "playing"
                    elif action in ("RESTART", "QUIT TO MENU"):
                        self._restart()
                    elif action == "EXIT GAME":
                        self.hand.stop()
                        pygame.quit()
                        sys.exit()

                elif self.game_state in ("game_over", "victory"):
                    if event.key == pygame.K_r:
                        self._restart()

        for side, player in [("Left", self.player1), ("Right", self.player2)]:
            current = hands[side]["gesture"]
            last    = self.last_gestures[side]
            if self.game_state == "playing":
                if current == "point" and last != "point":
                    if not self.player_dead[player.player_id]:
                        self._shoot_at_nearest(player)
            self.last_gestures[side] = current

        if self.game_state == "menu":
            if hands["Left"]["gesture"] == "open" or hands["Right"]["gesture"] == "open":
                if self.menu.ready:
                    self._start_game()

        if self.game_state == "playing":
            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                if not self.player_dead[1]:
                    self._shoot_toward(self.player1, mx, my)

    def update(self, dt, keys, hands):
        self.bg.update(dt)
        self.menu.update(dt)

        if self.game_state == "paused":
            self.pause.update(dt)
            return

        if self.game_state != "playing":
            return

        for pid in self.shoot_cooldowns:
            if self.shoot_cooldowns[pid] > 0:
                self.shoot_cooldowns[pid] -= dt
        for pid in self.player_invincibles:
            if self.player_invincibles[pid] > 0:
                self.player_invincibles[pid] -= dt

        for enemy in self.waves.enemies:
            if enemy.alive:
                target = self._get_nearest_enemy_target(enemy)
                enemy.update(dt, target[0], target[1])

        self.waves.enemies = [e for e in self.waves.enemies if e.alive]

        if self.waves.spawn_queue:
            self.waves.spawn_timer += dt
            if self.waves.spawn_timer >= self.waves.spawn_interval:
                self.waves.spawn_timer = 0
                enemy_type, speed_mult = self.waves.spawn_queue.pop(0)
                self.waves._spawn_enemy(enemy_type, speed_mult)

        if self.waves.wave_active and not self.waves.spawn_queue and not self.waves.enemies:
            self.waves.wave_active        = False
            self.waves.wave_complete      = True
            self.waves.between_wave_timer = 0

        if not self.waves.wave_active and not self.waves.all_waves_done:
            self.waves.between_wave_timer += dt
            if self.waves.between_wave_timer >= self.waves.between_wave_duration:
                self.waves.between_wave_timer = 0
                if self.waves.current_wave < self.waves.total_waves:
                    self.waves.start_next_wave()
                    self.hud.show_alert(f"WAVE {self.waves.current_wave} INCOMING")
                else:
                    self.waves.all_waves_done = True
                    self.game_state = "victory"

        for proj in self.projectiles:
            proj.update(dt, SCREEN_W, SCREEN_H)
        self.projectiles = [p for p in self.projectiles if p.alive]

        self.powerups.update(dt)
        for player in self.players:
            if not self.player_dead[player.player_id]:
                collected = self.powerups.check_collection(player.x, player.y)
                for powerup_type in collected:
                    self._apply_powerup(powerup_type)

        self._check_collisions()
        self.particles.update(dt)

        if not self.player_dead[1]:
            self.player1.update(dt, keys, hands["Left"])
        if not self.player_dead[2]:
            self.player2.update(dt, keys, hands["Right"])

        self.audio.update(dt, self.player1.is_moving or self.player2.is_moving)
        self.hud.update(dt)

    def _draw_wave_info(self):
        wave_text = f"WAVE {self.waves.current_wave} / {self.waves.total_waves}"
        self.screen.blit(
            self.font_medium.render(wave_text, True, (0, 255, 200)),
            (SCREEN_W // 2 - 80, 45)
        )
        self.screen.blit(
            self.font_hud.render(f"ENEMIES: {len(self.waves.enemies)}", True, (0, 200, 160)),
            (SCREEN_W // 2 - 55, 68)
        )
        if not self.waves.wave_active and not self.waves.all_waves_done and self.waves.current_wave > 0:
            remaining = self.waves.between_wave_duration - self.waves.between_wave_timer
            cd_surf   = self.font_medium.render(f"NEXT WAVE IN {remaining:.1f}s", True, (255, 200, 0))
            self.screen.blit(cd_surf, (SCREEN_W // 2 - cd_surf.get_width() // 2, SCREEN_H // 2))

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        title = self.font_large.render("SYSTEM COMPROMISED",  True, (255, 0, 80))
        sub   = self.font_medium.render("PRESS R TO RESTART", True, (200, 0, 60))
        score = self.font_medium.render(f"FINAL SCORE: {int(self.hud.score.score):07d}", True, (0, 255, 200))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 2 - 60))
        self.screen.blit(score, (SCREEN_W // 2 - score.get_width() // 2, SCREEN_H // 2))
        self.screen.blit(sub,   (SCREEN_W // 2 - sub.get_width()   // 2, SCREEN_H // 2 + 40))

    def _draw_victory(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        title = self.font_large.render("SYSTEM SECURED",         True, (0, 255, 200))
        sub   = self.font_medium.render("PRESS R TO PLAY AGAIN", True, (0, 200, 160))
        score = self.font_medium.render(f"FINAL SCORE: {int(self.hud.score.score):07d}", True, (255, 220, 0))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 2 - 60))
        self.screen.blit(score, (SCREEN_W // 2 - score.get_width() // 2, SCREEN_H // 2))
        self.screen.blit(sub,   (SCREEN_W // 2 - sub.get_width()   // 2, SCREEN_H // 2 + 40))

    def _draw_camera(self, hands):
        debug_frame = self.hand.get_debug_frame()
        if debug_frame is None:
            return
        small     = cv2.resize(debug_frame, (180, 120))
        small_rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
        self.screen.blit(pygame.surfarray.make_surface(small_rgb), (10, 45))
        pygame.draw.rect(self.screen, (0, 255, 200), (10, 45, 180, 120), 1)
        for i, (side, color) in enumerate([("Left", (0, 255, 200)), ("Right", (255, 0, 180))]):
            detected = hands[side]["detected"]
            gesture  = hands[side]["gesture"].upper()
            label    = f"P{i+1}: {gesture if detected else 'NO SIGNAL'}"
            surf     = self.font_hud.render(label, True, color if detected else (100, 100, 100))
            self.screen.blit(surf, (10, 168 + i * 16))

    def draw(self, hands):
        self.bg.draw(self.screen)

        if self.game_state == "menu":
            self.menu.draw(self.screen)
            self._draw_camera(hands)
            pygame.display.flip()
            return

        self.particles.draw(self.screen)

        for proj in self.projectiles:
            proj.draw(self.screen)

        for enemy in self.waves.get_enemies():
            enemy.draw(self.screen)

        self.powerups.draw(self.screen)

        for player in self.players:
            if not getattr(player, 'is_dead', False):
                player.draw(self.screen)

        self.hud.draw(self.screen, self.players)
        self.powerups.draw_active_effects(self.screen, SCREEN_W, SCREEN_H)
        self._draw_wave_info()
        self._draw_camera(hands)

        if self.game_state == "paused":
            self.pause.draw(self.screen, self.hud.score.score, self.waves.current_wave)
            pygame.display.flip()
            return

        if self.game_state == "game_over":
            self._draw_game_over()
        elif self.game_state == "victory":
            self._draw_victory()

        pygame.display.flip()

    def run(self):
        while True:
            dt    = self.clock.tick(FPS) / 1000.0
            keys  = pygame.key.get_pressed()
            hands = self.hand.get_both_states()
            self.handle_events(hands)
            self.update(dt, keys, hands)
            self.draw(hands)