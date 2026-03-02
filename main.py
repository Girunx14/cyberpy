from collections.abc import KeysView

import pygame
import sys
from background import CyberpunkBackground
from particles import ParticleSystem
from player import Player

pygame.init()

SCREEN_W, SCREEN_H = 900, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Cyberpunk Hacker — Fase 3")

clock = pygame.time.Clock()
bg = CyberpunkBackground(SCREEN_W, SCREEN_H)
particles = ParticleSystem()
player = Player(SCREEN_W // 2, SCREEN_H // 2)

##* muestra el contador de particulas (debug)
font = pygame.font.SysFont("Courier New", 16)

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

        ##* cuando el jugador ataca, emite partiicylas en su posicion
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                particles.emit(
                    int(player.x),
                    int(player.y),
                    count=25,
                    color=(255, 0, 180)
                )

    bg.update(dt)
    particles.update(dt)
    player.update(dt, keys)

    bg.draw(screen)
    particles.draw(screen)
    player.draw(screen)

    ##* muestra cuántas partículas hay activas
    ##* estado actual del jugador
    state_text = font.render(f"Estado: {player.state} | Frame: {player.current_frame}", True, (0, 255, 200))

    screen.blit(state_text, (10, 10))

    pygame.display.flip()