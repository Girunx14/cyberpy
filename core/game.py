import pygame
import sys
import cv2

from core.settings import SCREEN_W, SCREEN_H, FPS
from systems.background import CyberpunkBackground
from systems.particles import ParticleSystem
from systems.audio import AudioManager
from systems.hand_controller import HandController
from entities.player import Player
from ui.hud import HUD


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Cyberpunk Hacker")
        self.clock = pygame.time.Clock()

        # Sistemas
        self.bg       = CyberpunkBackground(SCREEN_W, SCREEN_H)
        self.particles = ParticleSystem()
        self.audio    = AudioManager()
        self.hand     = HandController(SCREEN_W, SCREEN_H)

        # Entidades
        self.player = Player(SCREEN_W // 2, SCREEN_H // 2, SCREEN_W, SCREEN_H)

        # UI
        self.hud = HUD(SCREEN_W, SCREEN_H)
        self.font_hud = pygame.font.SysFont("Courier New", 13, bold=True)

        # Estado del juego
        self.last_gesture = "none"

        self.audio.start_bgm()
        self.hand.start()

        self.hud.health.set_value(75)
        self.hud.shield.set_value(50)
        self.hud.show_alert("SYSTEM BREACH DETECTED")

    def handle_events(self, hand_data):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.hand.stop()
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                self.particles.emit(mx, my, count=40)
                self.audio.play("explosion")
                self.hud.add_score(100)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self._shoot()
                if event.key == pygame.K_h:
                    self.hud.health.set_value(self.hud.health.value - 10)
                if event.key == pygame.K_j:
                    self.hud.shield.set_value(self.hud.shield.value - 10)
                if event.key == pygame.K_r:
                    self.hud.show_alert("FIREWALL RESTORED")

    def _shoot(self):
        """Centraliza la lógica de disparo para no duplicarla."""
        self.particles.emit(
            int(self.player.x), int(self.player.y),
            count=25, color=(255, 0, 180)
        )
        self.audio.play("shoot")
        self.hud.add_score(10)

    def update(self, dt, keys, hand_data):
        # Disparo por gesto: solo se activa en el momento que cambia a "point"
        current_gesture = hand_data["gesture"]
        if current_gesture == "point" and self.last_gesture != "point":
            self._shoot()
        self.last_gesture = current_gesture

        self.bg.update(dt)
        self.particles.update(dt)
        self.player.update(dt, keys, hand_data)
        self.audio.update(dt, self.player.is_moving)
        self.hud.update(dt)

    def draw(self, hand_data):
        self.bg.draw(self.screen)
        self.particles.draw(self.screen)
        self.player.draw(self.screen)
        self.hud.draw(self.screen, self.player.x, self.player.y)
        self._draw_camera(hand_data)
        pygame.display.flip()

    def _draw_camera(self, hand_data):
        """Muestra la vista de la cámara con landmarks en esquina superior izquierda."""
        debug_frame = self.hand.get_debug_frame()
        if debug_frame is None:
            return

        small = cv2.resize(debug_frame, (180, 120))
        small_rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        small_rgb = small_rgb.swapaxes(0, 1)
        cam_surface = pygame.surfarray.make_surface(small_rgb)
        self.screen.blit(cam_surface, (10, 45))
        pygame.draw.rect(self.screen, (0, 255, 200), (10, 45, 180, 120), 1)

        gesture_color = (0, 255, 200) if hand_data["detected"] else (100, 100, 100)
        g_surf = self.font_hud.render(f"GESTO: {hand_data['gesture'].upper()}", True, gesture_color)
        self.screen.blit(g_surf, (10, 168))

    def run(self):
        """Loop principal. Único lugar donde corre el tiempo del juego."""
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            keys = pygame.key.get_pressed()
            hand_data = self.hand.get_state()

            self.handle_events(hand_data)
            self.update(dt, keys, hand_data)
            self.draw(hand_data)