import pygame


def draw_glow_rect(surface, color, rect, width, blur_levels=3):
    x, y, w, h = rect
    for i in range(blur_levels, 0, -1):
        dim = i / blur_levels
        dimmed = (
            int(color[0] * dim),
            int(color[1] * dim),
            int(color[2] * dim),
        )
        expand = i * 2
        pygame.draw.rect(
            surface, dimmed,
            (x - expand, y - expand, w + expand * 2, h + expand * 2),
            width + i
        )
    pygame.draw.rect(surface, color, rect, width)


def draw_glow_line(surface, color, start, end, width=1, blur_levels=3):
    for i in range(blur_levels, 0, -1):
        dim = i / blur_levels
        dimmed = (
            int(color[0] * dim),
            int(color[1] * dim),
            int(color[2] * dim),
        )
        pygame.draw.line(surface, dimmed, start, end, width + i * 2)
    pygame.draw.line(surface, color, start, end, width)


def clamp_color(r, g, b):
    """Evita que valores de color salgan del rango 0-255."""
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))