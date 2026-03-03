from collections.abc import KeysView

import pygame
import sys
from background import CyberpunkBackground
from particles import ParticleSystem
from player import Player
from audio import AudioManager
from hud import HUD

pygame.init()

SCREEN_W, SCREEN_H = 900, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Cyberpunk Hacker — Fase 3")

clock = pygame.time.Clock()
bg = CyberpunkBackground(SCREEN_W, SCREEN_H)
particles = ParticleSystem()
player = Player(SCREEN_W // 2, SCREEN_H // 2, SCREEN_W, SCREEN_H)
audio = AudioManager()
hud = HUD(SCREEN_W, SCREEN_H)

##* muestra el contador de particulas (debug)
font = pygame.font.SysFont("Courier New", 16)

audio.start_bgm()

hud.health.set_value(75)
hud.shield.set_value(50)
hud.show_alert("SYSTEM BREACH DETECTED")

while True:
    dt = clock.tick(60) / 1000.0
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        ##*  explosión de partículas donde haces click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            particles.emit(mx, my, count=40)
            audio.play("explosion")
            hud.add_score(100)

        ##* cuando el jugador ataca, emite partiicylas en su posicion
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                particles.emit(
                    int(player.x),
                    int(player.y),
                    count=25,
                    color=(255, 0, 180)
                )
                audio.play("shoot")
                hud.add_score(10)

            if event.key == pygame.K_h:
                hud.health.set_value(hud.health.value - 10)
            if event.key == pygame.K_j:
                hud.shield.set_value(hud.shield.value - 10)
            if event.key == pygame.K_r:
                hud.show_alert("FIREWALL RESTORED")

    bg.update(dt)
    particles.update(dt)
    player.update(dt, keys)
    audio.update(dt, player.is_moving)
    hud.update(dt)

    bg.draw(screen)
    particles.draw(screen)
    player.draw(screen)
    hud.draw(screen, player.x, player.y)

    ##* muestra cuántas partículas hay activas
    ##* estado actual del jugador
    state_text = font.render(f"Estado: {player.state} | Frame: {player.current_frame}", True, (0, 255, 200))
    screen.blit(state_text, (10, 10))

    pygame.display.flip()