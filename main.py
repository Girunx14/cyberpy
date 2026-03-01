# main.py
import pygame
import sys
from background import CyberpunkBackground
from particles import ParticleSystem

pygame.init()

SCREEN_W, SCREEN_H = 900, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Cyberpunk Hacker — Fase 2")

clock = pygame.time.Clock()
bg = CyberpunkBackground(SCREEN_W, SCREEN_H)
particles = ParticleSystem()

# Fuente para mostrar el contador de partículas (debug)
font = pygame.font.SysFont("Courier New", 16)

while True:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Click izquierdo: explosión de partículas donde haces click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            particles.emit(mx, my, count=40)

    bg.update(dt)
    particles.update(dt)

    bg.draw(screen)
    particles.draw(screen)

    # Debug: muestra cuántas partículas hay activas
    count_text = font.render(f"Partículas: {particles.particle_count()}", True, (0, 255, 200))
    screen.blit(count_text, (10, 10))

    pygame.display.flip()