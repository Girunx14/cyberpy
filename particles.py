# particles.py
import pygame
import random
import math


class Particle:
    """
    Representa una sola partícula.
    Cada partícula es independiente y maneja su propio estado.
    """
    def __init__(self, x, y, color):
        self.x = x
        self.y = y

        # Velocidad en dirección aleatoria
        # angle es un ángulo en radianes (0 a 2*PI = círculo completo)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(80, 220)

        # Convertimos el ángulo a velocidades en X e Y con trigonometría
        # cos(angle) da el componente horizontal
        # sin(angle) da el componente vertical
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # Gravedad: acelera la partícula hacia abajo con el tiempo
        self.gravity = 150

        # Vida en segundos
        self.lifetime = random.uniform(0.4, 0.9)
        self.age = 0  # cuánto tiempo lleva viva

        # Tamaño inicial aleatorio
        self.size = random.randint(3, 7)

        # Guardamos el color base para poder hacer fade
        self.base_color = color

    def update(self, dt):
        # Movemos la partícula según su velocidad
        self.x += self.vx * dt
        self.y += self.vy * dt

        # La gravedad aumenta la velocidad vertical con el tiempo
        self.vy += self.gravity * dt

        # Envejecemos la partícula
        self.age += dt

    def is_dead(self):
        return self.age >= self.lifetime

    def draw(self, surface):
        # Calculamos qué tan "viva" está: 1.0 = recién nacida, 0.0 = muriendo
        life_ratio = 1.0 - (self.age / self.lifetime)

        # El tamaño se reduce conforme envejece
        current_size = max(1, int(self.size * life_ratio))

        # El color se oscurece conforme envejece
        r = int(self.base_color[0] * life_ratio)
        g = int(self.base_color[1] * life_ratio)
        b = int(self.base_color[2] * life_ratio)

        # Nos aseguramos de que los valores estén en rango válido
        color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), current_size)


class ParticleSystem:
    """
    Administra todas las partículas activas en pantalla.
    El juego solo necesita hablar con esta clase.
    """
    def __init__(self):
        self.particles = []

        # Colores disponibles para explosiones cyberpunk
        self.colors = [
            (0, 255, 200),    # cyan
            (255, 0, 180),    # magenta
            (255, 220, 0),    # amarillo eléctrico
            (255, 255, 255),  # blanco
            (0, 180, 255),    # azul eléctrico
        ]

    def emit(self, x, y, count=30, color=None):
        """
        Crea una explosión de partículas en la posición (x, y).
        count = cuántas partículas generar
        color = si es None, elige un color aleatorio de la paleta
        """
        for _ in range(count):
            c = color if color else random.choice(self.colors)
            self.particles.append(Particle(x, y, c))

    def update(self, dt):
        # Actualizamos todas las partículas
        for p in self.particles:
            p.update(dt)

        # Eliminamos las que ya murieron
        # Hacemos esto en una sola línea con list comprehension
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def particle_count(self):
        """Útil para debug: saber cuántas partículas hay activas."""
        return len(self.particles)