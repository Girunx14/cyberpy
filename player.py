import pygame
import math

def create_player_frames ():
    frames = {
        "idle": [],
        "move": [],
        "attack": [],
    }

    size = 48 

    for i in range(6):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        bob = math.sin(i / 6 * math.pi *2) * 2
        cx, cy = size // 2, size // 2 + int(bob)
        points = []
        for j in range(6):
            angle = math.pi / 6 + j * math.pi / 3
            px = cx + math.cos(angle) * 16
            py = cy + math.sin(angle) * 16
            points.append((px, py))

        pygame.draw.polygon(surface, (0, 200, 160), points)
        pygame.draw.polygon(surface, (0, 255, 200), points, 2)

        pulse_r = 5 + int(abs(math.sin(i / 6 * math.pi * 2)) * 3)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), pulse_r)
        pygame.draw.circle(surface, (0, 255, 200), (cx, cy), pulse_r, 1)

        frames["idle"].append(surface)

    ##* move:: el jugador se inclina y tiene estela
    for i in range(4):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        ##* inclinacion lateral seguun el frame
        lean = math.sin(i / 4 * math.pi * 2) * 3

        points = []
        for j in range(6):
            angle = math.pi / 6 + j * math.pi / 3
            px = cx + math.cos(angle) * 16 + lean
            py = cy + math.sin(angle) * 14
            points.append((px, py))

        pygame.draw.polygon(surface, (0, 160, 220), points)
        pygame.draw.polygon(surface, (0, 180, 255), points, 2)

        ##* estelas
        for k in range(3):
            lx = cx - 18 - k * 5
            ly = cy - 4 + k * 4
            pygame.draw.line(surface, (0, 100, 180), (lx, ly), (lx - 6, ly), 1)

        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 5)

        frames["move"].append(surface)

        ##* attack - destello de energia
        for i in range(5): 
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            cx, cy = size // 2, size // 2

        points = []
        for j in range(6):
            angle = math.pi / 6 + j * math.pi / 3
            ##* en el frame 2 (pico del ataque) el hexagono se expande
            radius = 16 + (8 if i == 2 else 0)
            px = cx + math.cos(angle) * radius
            py = cy + math.sin(angle) * radius
            points.append((px, py))

        ##* color cambia a magenta durante el ataque
        fill_color = (200, 0, 140) if i == 2 else (160, 0, 100)
        border_color = (255, 0, 180) if i == 2 else (200, 0, 140)

        pygame.draw.polygon(surface, fill_color, points)
        pygame.draw.polygon(surface, border_color, points, 2)

        ##* rayos de energia 
        if i == 2:
            for j in range(6):
                angle = j * math.pi / 3
                ex = cx + math.cos(angle) * 26
                ey = cy + math.sin(angle) * 26
                pygame.draw.line(surface, (255, 100, 200), (cx, cy), (int(ex), int(ey)), 2)

        pygame.draw.circle(surface, (255, 200, 255), (cx, cy), 5)

        frames["attack"].append(surface)

    return frames
    
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frames = create_player_frames()

        ##* estado actual 
        self.state = "idle"

        ##* control en la animacion
        self.current_frame = 0
        self.frame_timer = 0

        ##* velocidad de animacion
        self.frame_speeds = {
            "idle": 0.12,
            "move": 0.08,
            "attack": 0.07,
        }

        ##* velocidad de moviemiento 
        self.speed = 200

    def set_state(self, new_state):
        ##! esto cambie el estado solo si es diferente al actual
        if new_state != self.state:
            self.state = new_state
            self.current_frame = 0   ##* reinicia la animacion desde el frame 0
            self.frame_timer = 0
    
    def update(self, dt, keys):
        ##* movimiento con teclas
        moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed * dt
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed * dt
            moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed * dt
            moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed * dt
            moving = True

        ##* cambio de estado conforme a la accion 
        if keys[pygame.K_SPACE]:
            self.set_state("attack")
        elif moving:
            self.set_state("move")
        else:
            self.set_state("idle")

        ##* avance de los frames
        self.frame_timer += dt
        speed = self.frame_speeds[self.state]

        if self.frame_timer >= speed: 
            self.frame_timer = 0
            total_frames = len(self.frames[self.state])
            self.current_frame = (self.current_frame + 1) % total_frames

            ##* si el ataque termina vuelve a idle 
            if self.state == "attack" and self.current_frame == 0:
                self.set_state("idle")
    
    def draw(self, surface):
        frame = self.frames[self.state][self.current_frame]

        ##* centra el sprite en la posicion del player
        frame_w = frame.get_width()
        frame_h = frame.get_height()
        draw_x = int(self.x) - frame_w // 2
        draw_y = int(self.y) - frame_h // 2

        surface.blit(frame, (draw_x, draw_y))