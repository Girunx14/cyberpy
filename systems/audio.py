import pygame
import numpy as np

SAMPLE_RATE = 44100


def _generate_sound(wave_array):
    audio = (wave_array * 32767).astype(np.int16)
    audio_stereo = np.ascontiguousarray(np.column_stack([audio, audio]))
    return pygame.sndarray.make_sound(audio_stereo)


def create_shoot_sound():
    duration = 0.15
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples)
    freq = np.linspace(800, 200, samples)
    wave = np.sin(2 * np.pi * freq * t)
    wave = wave * np.linspace(1.0, 0.0, samples) * 0.4
    return _generate_sound(wave)


def create_explosion_sound():
    duration = 0.4
    samples = int(SAMPLE_RATE * duration)
    noise = np.random.uniform(-1.0, 1.0, samples)
    wave = noise * np.exp(-8 * np.linspace(0, 1, samples)) * 0.6
    return _generate_sound(wave)


def create_move_sound():
    duration = 0.08
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples)
    wave = np.sin(2 * np.pi * 300 * t) * np.linspace(1.0, 0.0, samples) * 0.15
    return _generate_sound(wave)


def create_bgm():
    duration = 2.0
    samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, samples)
    wave  = np.sin(2 * np.pi * 55  * t) * 0.3
    wave += np.sin(2 * np.pi * 110 * t) * 0.2
    wave += np.sin(2 * np.pi * 165 * t) * 0.1
    wave += np.sin(2 * np.pi * 220 * t) * 0.08
    pulse = (np.sin(2 * np.pi * 2 * t) + 1) / 2
    wave = wave * (0.4 + pulse * 0.6)
    wave = wave / np.max(np.abs(wave)) * 0.5
    return _generate_sound(wave)


class AudioManager:
    def __init__(self):
        pygame.mixer.pre_init(SAMPLE_RATE, -16, 2, 512)
        pygame.mixer.init()
        print("Generando audio...")
        self.sounds = {
            "shoot":     create_shoot_sound(),
            "explosion": create_explosion_sound(),
            "move":      create_move_sound(),
        }
        self.bgm = create_bgm()
        self.bgm_playing = False
        self.move_timer = 0
        self.move_interval = 0.2
        print("Audio listo.")

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def start_bgm(self):
        if not self.bgm_playing:
            self.bgm.play(loops=-1)
            self.bgm_playing = True

    def stop_bgm(self):
        self.bgm.stop()
        self.bgm_playing = False

    def update(self, dt, player_moving):
        if player_moving:
            self.move_timer += dt
            if self.move_timer >= self.move_interval:
                self.move_timer = 0
                self.play("move")
        else:
            self.move_timer = 0