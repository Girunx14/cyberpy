#  CyberPy

> Videojuego futurista controlado con gestos de la mano en tiempo real.  
> Construido con Python, Pygame, OpenCV y MediaPipe.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python) ![Pygame](https://img.shields.io/badge/Pygame-2.6-green?style=flat-square) ![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-orange?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

##  ¿Qué es?

CyberPy es un videojuego de defensa donde controlas un hacker digital que debe destruir oleadas de virus usando **gestos de la mano** detectados por la cámara web en tiempo real.

Desarrollado como proyecto para feria de ciencias universitaria con el objetivo de demostrar que Python permite crear experiencias interactivas impresionantes combinando visión por computadora y desarrollo de videojuegos.

---

## Controles

### Gestos (cámara)

|Gesto|Acción|
|---|---|
|Mano abierta moviéndose|Mover jugador|
|Solo índice levantado|Disparar al enemigo más cercano|
|Puño cerrado|Modo defensa (idle)|
|Mano abierta estática|Iniciar juego desde el menú|

### Teclado (respaldo)

|Tecla|Acción|
|---|---|
|`WASD` / Flechas|Mover jugador|
|`Espacio`|Disparar al enemigo más cercano|
|`Click izquierdo`|Disparar hacia el cursor|
|`ESC`|Pausar / Reanudar|
|`Enter`|Confirmar en menús|
|`R`|Reiniciar desde Game Over o Victoria|

---

##  Instalación

### Requisitos

- Python 3.8 o superior
- Cámara web
- Sistema operativo: Windows, macOS o Linux

### Pasos

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/cyberpunk-hacker.git
cd cyberpunk-hacker

# 2. Crea y activa el entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

# 3. Instala las dependencias
pip install pygame opencv-python mediapipe numpy

# 4. Ejecuta el juego
python main.py
```

---

##  Estructura del Proyecto

```css
cyberpunk_hacker/
│
├── main.py                  # Punto de entrada
│
├── core/
│   ├── game.py              # Loop principal y orquestación
│   ├── settings.py          # Constantes globales (colores, tamaños, FPS)
│   └── utils.py             # Funciones reutilizables de dibujo
│
├── systems/
│   ├── background.py        # Fondo cyberpunk dinámico (grid, data streams, scanline)
│   ├── particles.py         # Sistema de partículas
│   ├── audio.py             # Audio generado proceduralmente con NumPy
│   ├── hand_controller.py   # Captura y procesamiento de gestos (MediaPipe + threading)
│   └── wave_manager.py      # Lógica de oleadas de enemigos
│
├── entities/
│   ├── player.py            # Jugador con máquina de estados y animaciones
│   ├── enemy.py             # Enemigos (basic, fast, tank) con animaciones
│   └── projectile.py        # Proyectiles con estela visual
│
├── ui/
│   ├── hud.py               # HUD (vida, escudo, score, minimapa, alertas)
│   └── screens.py           # Pantallas de menú, pausa, game over y victoria
│
└── assets/
    ├── sounds/
    ├── images/
    └── fonts/
```

---

## Enemigos

|Tipo|Forma|Velocidad|HP|Puntos|
|---|---|---|---|---|
|Basic|Pentágono rojo|Media|1|100|
|Fast|Triángulo magenta|Alta|1|150|
|Tank|Hexágono oscuro|Baja|3|300|

---

##  Oleadas

|Oleada|Composición|
|---|---|
|1|5 Basic|
|2|4 Basic + 2 Fast|
|3|4 Fast + 1 Tank|
|4|3 Basic + 3 Fast + 2 Tank|
|5|4 Fast + 3 Tank + 4 Basic|

Cada oleada aumenta la velocidad de los enemigos un 15%.

---

##  Tecnologías

|Tecnología|Uso|
|---|---|
|**Pygame**|Motor de juego, renderizado, audio|
|**OpenCV**|Captura de cámara y procesamiento de frames|
|**MediaPipe**|Detección de mano y landmarks en tiempo real|
|**NumPy**|Síntesis de audio procedural|
|**threading**|Captura de cámara en hilo separado para no bloquear el juego|

---

##  Decisiones de Arquitectura

- **Módulos por responsabilidad** — cada carpeta agrupa sistemas con el mismo propósito
- **Delta time** — movimiento independiente del framerate en cualquier hardware
- **Threading para la cámara** — el hilo de captura corre separado del loop del juego para mantener 60fps estables
- **Audio procedural** — los sonidos se generan con NumPy al iniciar, sin archivos externos
- **State machine** — el jugador y el juego tienen estados explícitos (`idle`, `move`, `attack`, `playing`, `paused`, etc.)

---

##  Requisitos del Sistema

|Componente|Mínimo|
|---|---|
|Python|3.8+|
|RAM|4 GB|
|Cámara|Cualquier webcam|
|Iluminación|Buena luz para detección de gestos|
