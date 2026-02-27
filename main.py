import pygame 
import sys
from background import CyberpunkBackground

pygame.init()

SCREEN_W, SCREEN_H = 900, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("CyberPy Hacker - Fase 1")

clock = pygame.time.Clock()
bg = CyberpunkBackground(SCREEN_W, SCREEN_H)

while True: 
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    bg.update(dt)
    bg.draw(screen)

    pygame.display.flip()