#*main.py
import pygame
import sys
import cv2
from background import CyberpunkBackground
from particles import ParticleSystem
from player import Player
from audio import AudioManager
from hud import HUD
from hand_controller import HandController

pygame.init()

SCREEN_W, SCREEN_H = 900, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Cyberpunk Hacker — Fase 6")

clock = pygame.time.Clock()
bg = CyberpunkBackground(SCREEN_W, SCREEN_H)
particles = ParticleSystem()
player = Player(SCREEN_W // 2, SCREEN_H // 2, SCREEN_W, SCREEN_H)
audio = AudioManager()
hud = HUD(SCREEN_W, SCREEN_H)
hand = HandController(SCREEN_W, SCREEN_H)

audio.start_bgm()
hand.start()

hud.health.set_value(75)
hud.shield.set_value(50)
hud.show_alert("SYSTEM BREACH DETECTED")

last_gesture = "none"
font_hud = pygame.font.SysFont("Courier New", 13, bold=True)

while True:
    dt = clock.tick(60) / 1000.0
    keys = pygame.key.get_pressed()
    hand_data = hand.get_state()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            hand.stop()
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            particles.emit(mx, my, count=40)
            audio.play("explosion")
            hud.add_score(100)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                particles.emit(int(player.x), int(player.y), count=25, color=(255, 0, 180))
                audio.play("shoot")
                hud.add_score(10)
            if event.key == pygame.K_h:
                hud.health.set_value(hud.health.value - 10)
            if event.key == pygame.K_j:
                hud.shield.set_value(hud.shield.value - 10)
            if event.key == pygame.K_r:
                hud.show_alert("FIREWALL RESTORED")

    #* disparo automático cuando el gesto cambia a "point"
    current_gesture = hand_data["gesture"]
    if current_gesture == "point" and last_gesture != "point":
        particles.emit(int(player.x), int(player.y), count=25, color=(255, 0, 180))
        audio.play("shoot")
        hud.add_score(10)
    last_gesture = current_gesture

    bg.update(dt)
    particles.update(dt)
    player.update(dt, keys, hand_data)
    audio.update(dt, player.is_moving)
    hud.update(dt)

    bg.draw(screen)
    particles.draw(screen)
    player.draw(screen)
    hud.draw(screen, player.x, player.y)

    #*Mini ventana de la cámara en esquina superior izquierda
    debug_frame = hand.get_debug_frame()
    if debug_frame is not None:
        small = cv2.resize(debug_frame, (180, 120))
        small_rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        small_rgb = small_rgb.swapaxes(0, 1)
        cam_surface = pygame.surfarray.make_surface(small_rgb)
        screen.blit(cam_surface, (10, 45))

        pygame.draw.rect(screen, (0, 255, 200), (10, 45, 180, 120), 1)

        gesture_color = (0, 255, 200) if hand_data["detected"] else (100, 100, 100)
        gesture_text = f"GESTO: {hand_data['gesture'].upper()}"
        g_surf = font_hud.render(gesture_text, True, gesture_color)
        screen.blit(g_surf, (10, 168))

    pygame.display.flip()