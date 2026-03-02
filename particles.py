##* particles.py
import pygame
import random
import math


class Particle:
    """
    representa una sola particula y cada particula es independiente
    o sea que maneja su propio estado
    """
    def __init__(self, x, y, color):
        self.x = x
        self.y = y

        ##* velocidad en direccion aleatoria
        ##* angle es un angulo en radianes (0 a 2*PI = circulo completo)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(80, 220)

        """ 
        convertimos el angulo a velocidades en X e Y con trigonometria
        cos(angle) da el componente horizontal
        sin(angle) da el componente vertical
        """
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        ##* gravedad: acelera la particula hacia abajo con el tiempo
        self.gravity = 150

        ##* vida en segundos
        self.lifetime = random.uniform(0.4, 0.9)
        self.age = 0  ##* cuanto tiempo lleva viva

        ##* tamaño inicial aleatorio
        self.size = random.randint(3, 7)

        ##* guardamos el color base para poder hacer fade
        self.base_color = color

    def update(self, dt):
        ##* movemos la particula segun su velocidad
        self.x += self.vx * dt
        self.y += self.vy * dt

        ##* la gravedad aumenta la velocidad vertical con el tiempo
        self.vy += self.gravity * dt

        ##* envejecemos la particula
        self.age += dt

    def is_dead(self):
        return self.age >= self.lifetime

    def draw(self, surface):
        ##* calculamos que tan "viva" esta: 1.0 = recien nacida, 0.0 = muriendo
        life_ratio = 1.0 - (self.age / self.lifetime)

        ##* el tamaño se reduce conforme envejece
        current_size = max(1, int(self.size * life_ratio))

        ##* el color se oscurece conforme envejece
        r = int(self.base_color[0] * life_ratio)
        g = int(self.base_color[1] * life_ratio)
        b = int(self.base_color[2] * life_ratio)

        ##* nos aseguramos de que los valores esten en rango valido
        color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), current_size)


class ParticleSystem:
    """
    administra todas las particulas activas en pantalla
    el juego solo necesita hablar con esta clase
    """
    def __init__(self):
        self.particles = []

        ##* colores disponibles para explosiones cyberpunk
        self.colors = [
            (0, 255, 200),    ##* cyan
            (255, 0, 180),    ##* magenta
            (255, 220, 0),    ##* amarillo electrico
            (255, 255, 255),  ##* blanco
            (0, 180, 255),    ##* azul electrico
        ]

    def emit(self, x, y, count=30, color=None):
        """
        crea una explosion de partículas en la posicion (x, y).
        count = cuantas particulas generar
        color = si es None, elige un color aleatorio de la paleta
        """
        for _ in range(count):
            c = color if color else random.choice(self.colors)
            self.particles.append(Particle(x, y, c))

    def update(self, dt):
        ##* actualizamos todas las particulas
        for p in self.particles:
            p.update(dt)

        ##* eliminamos las que ya murieron
        ##* hacemos esto en una sola linea con list comprehension
        self.particles = [p for p in self.particles if not p.is_dead()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def particle_count(self):
        """util para debug: saber cuantas particulas hay activas."""
        return len(self.particles)