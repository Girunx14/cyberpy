import random
from entities.enemy import Enemy


class WaveManager:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.current_wave = 0
        self.total_waves  = 5
        self.enemies = []

        self.wave_active    = False
        self.wave_complete  = False
        self.all_waves_done = False

        self.between_wave_timer    = 0
        self.between_wave_duration = 3.0

        self.spawn_queue    = []
        self.spawn_timer    = 0
        self.spawn_interval = 0.8

        self.start_next_wave()

    def _build_wave(self, wave_number):
        queue = []

        if wave_number == 1:
            queue = [("basic", )] * 5
        elif wave_number == 2:
            queue = [("basic", )] * 4 + [("fast", )] * 2
        elif wave_number == 3:
            queue = [("fast", )] * 4 + [("tank", )] * 1
        elif wave_number == 4:
            queue = [("basic", )] * 3 + [("fast", )] * 3 + [("tank", )] * 2
        elif wave_number == 5:
            queue = [("fast", )] * 4 + [("tank", )] * 3 + [("basic", )] * 4

        speed_multiplier = 1.0 + (wave_number - 1) * 0.15
        return queue, speed_multiplier

    def _spawn_enemy(self, enemy_type, speed_mult):
        side   = random.randint(0, 3)
        margin = 30

        if side == 0:
            x = random.randint(margin, self.screen_w - margin)
            y = -margin
        elif side == 1:
            x = random.randint(margin, self.screen_w - margin)
            y = self.screen_h + margin
        elif side == 2:
            x = -margin
            y = random.randint(margin, self.screen_h - margin)
        else:
            x = self.screen_w + margin
            y = random.randint(margin, self.screen_h - margin)

        enemy = Enemy(x, y, enemy_type)
        enemy.speed *= speed_mult
        self.enemies.append(enemy)

    def start_next_wave(self):
        self.current_wave += 1
        self.wave_active   = True
        self.wave_complete = False

        queue_data, speed_mult = self._build_wave(self.current_wave)
        self.spawn_queue = [(t, speed_mult) for (t,) in queue_data]
        self.spawn_timer = 0

    def get_enemies(self):
        return self.enemies