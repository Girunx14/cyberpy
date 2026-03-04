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
from ui.hud import HUD


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
        self.player    = Player(SCREEN_W // 2, SCREEN_H // 2, SCREEN_W, SCREEN_H)
        self.hud       = HUD(SCREEN_W, SCREEN_H)

        self.projectiles  = []
        self.font_hud     = pygame.font.SysFont("Courier New", 13, bold=True)
        self.font_large   = pygame.font.SysFont("Courier New", 36, bold=True)
        self.font_medium  = pygame.font.SysFont("Courier New", 20, bold=True)

        self.game_state   = "playing"
        self.last_gesture = "none"

        self.shoot_cooldown      = 0
        self.shoot_cooldown_max  = 0.25

        self.player_invincible      = 0
        self.player_invincible_max  = 1.5

        self.audio.start_bgm()
        self.hand.start()
        self.hud.show_alert("SYSTEM BREACH DETECTED")

    def _shoot_toward(self, target_x, target_y):
        if self.shoot_cooldown > 0:
            return
        self.shoot_cooldown = self.shoot_cooldown_max
        self.projectiles.append(Projectile(self.player.x, self.player.y, target_x, target_y))
        self.audio.play("shoot")
        self.hud.add_score(5)

    def _shoot_at_nearest_enemy(self):
        enemies = self.waves.get_enemies()
        if not enemies:
            return

        nearest = min(
            enemies,
            key=lambda e: math.sqrt((e.x - self.player.x)**2 + (e.y - self.player.y)**2)
        )
        self._shoot_toward(nearest.x, nearest.y)

    def _check_collisions(self):
        enemies = self.waves.get_enemies()

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

                    if not enemy.alive or enemy.dying:
                        self.hud.add_score(enemy.score_value)
                        self.particles.emit(int(enemy.x), int(enemy.y), count=30, color=(255, 50, 50))

        if self.player_invincible <= 0:
            for enemy in enemies:
                if enemy.dying:
                    continue
                dist = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
                if dist < enemy.radius + 20:
                    self.hud.health.set_value(self.hud.health.value - 20)
                    self.player_invincible = self.player_invincible_max
                    self.particles.emit(int(self.player.x), int(self.player.y), count=20, color=(255, 0, 100))
                    self.audio.play("explosion")
                    self.hud.show_alert("INTEGRITY COMPROMISED")

                    if self.hud.health.value <= 0:
                        self.game_state = "game_over"

        self.projectiles = [p for p in self.projectiles if p.alive]

    def handle_events(self, hand_data):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.hand.stop()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if self.game_state == "playing":
                    if event.key == pygame.K_SPACE:
                        self._shoot_at_nearest_enemy()

                if event.key == pygame.K_r:
                    self.__init__()

        current_gesture = hand_data["gesture"]
        if current_gesture == "point" and self.last_gesture != "point":
            if self.game_state == "playing":
                self._shoot_at_nearest_enemy()
        self.last_gesture = current_gesture

        if self.game_state == "playing":
            mouse = pygame.mouse.get_pressed()
            if mouse[0]:
                mx, my = pygame.mouse.get_pos()
                self._shoot_toward(mx, my)

    def update(self, dt, keys, hand_data):
        if self.game_state != "playing":
            return

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.player_invincible > 0:
            self.player_invincible -= dt

        for enemy in self.waves.get_enemies():
            enemy.update(dt, self.player.x, self.player.y)

        self.waves.spawn_timer += dt
        if self.waves.spawn_queue and self.waves.spawn_timer >= self.waves.spawn_interval:
            self.waves.spawn_timer = 0
            enemy_type, speed_mult = self.waves.spawn_queue.pop(0)
            self.waves._spawn_enemy(enemy_type, speed_mult)

        if not self.waves.spawn_queue and not self.waves.enemies and self.waves.wave_active:
            self.waves.wave_active   = False
            self.waves.wave_complete = True

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

        self._check_collisions()

        self.bg.update(dt)
        self.particles.update(dt)
        self.player.update(dt, keys, hand_data)
        self.audio.update(dt, self.player.is_moving)
        self.hud.update(dt)

    def _draw_wave_info(self):
        wave_text = f"WAVE {self.waves.current_wave} / {self.waves.total_waves}"
        enemies_text = f"ENEMIES: {len(self.waves.enemies)}"

        w_surf = self.font_medium.render(wave_text, True, (0, 255, 200))
        e_surf = self.font_hud.render(enemies_text, True, (0, 200, 160))

        self.screen.blit(w_surf, (SCREEN_W // 2 - w_surf.get_width() // 2, 45))
        self.screen.blit(e_surf, (SCREEN_W // 2 - e_surf.get_width() // 2, 68))

        if not self.waves.wave_active and not self.waves.all_waves_done and self.waves.current_wave > 0:
            remaining = self.waves.between_wave_duration - self.waves.between_wave_timer
            cd_text = f"NEXT WAVE IN {remaining:.1f}s"
            cd_surf = self.font_medium.render(cd_text, True, (255, 200, 0))
            self.screen.blit(cd_surf, (SCREEN_W // 2 - cd_surf.get_width() // 2, SCREEN_H // 2))

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("SYSTEM COMPROMISED", True, (255, 0, 80))
        sub   = self.font_medium.render("PRESS R TO RESTART", True, (200, 0, 60))
        score = self.font_medium.render(f"FINAL SCORE: {int(self.hud.score.score):07d}", True, (0, 255, 200))

        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 2 - 60))
        self.screen.blit(score, (SCREEN_W // 2 - score.get_width() // 2, SCREEN_H // 2))
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2 + 40))

    def _draw_victory(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("SYSTEM SECURED", True, (0, 255, 200))
        sub   = self.font_medium.render("PRESS R TO PLAY AGAIN", True, (0, 200, 160))
        score = self.font_medium.render(f"FINAL SCORE: {int(self.hud.score.score):07d}", True, (255, 220, 0))

        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, SCREEN_H // 2 - 60))
        self.screen.blit(score, (SCREEN_W // 2 - score.get_width() // 2, SCREEN_H // 2))
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, SCREEN_H // 2 + 40))

    def _draw_camera(self, hand_data):
        debug_frame = self.hand.get_debug_frame()
        if debug_frame is None:
            return
        small = cv2.resize(debug_frame, (180, 120))
        small_rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
        self.screen.blit(pygame.surfarray.make_surface(small_rgb), (10, 45))
        pygame.draw.rect(self.screen, (0, 255, 200), (10, 45, 180, 120), 1)
        gesture_color = (0, 255, 200) if hand_data["detected"] else (100, 100, 100)
        g_surf = self.font_hud.render(f"GESTO: {hand_data['gesture'].upper()}", True, gesture_color)
        self.screen.blit(g_surf, (10, 168))

    def draw(self, hand_data):
        self.bg.draw(self.screen)
        self.particles.draw(self.screen)

        for proj in self.projectiles:
            proj.draw(self.screen)

        for enemy in self.waves.get_enemies():
            enemy.draw(self.screen)

        self.player.draw(self.screen)
        self.hud.draw(self.screen, self.player.x, self.player.y)
        self._draw_wave_info()
        self._draw_camera(hand_data)

        if self.game_state == "game_over":
            self._draw_game_over()
        elif self.game_state == "victory":
            self._draw_victory()

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            keys = pygame.key.get_pressed()
            hand_data = self.hand.get_state()

            self.handle_events(hand_data)
            self.update(dt, keys, hand_data)
            self.draw(hand_data)