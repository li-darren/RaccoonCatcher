import math
import random

_LEAF_COLORS = [
    (40, 120, 30),
    (80, 150, 20),
    (140, 100, 20),
    (160, 80, 10),
    (100, 140, 30),
]


class Leaf:
    def __init__(self, zone_index: int):
        self.zone_index = zone_index
        self.cam_x = random.uniform(0.02, 0.98)
        self.cam_y_frac = random.uniform(-0.05, 0.0)
        self.cam_vy = random.uniform(0.05, 0.14)
        self.drift_amp = random.uniform(0.005, 0.020)
        self.drift_freq = random.uniform(1.5, 3.5)
        self.drift_phase: float = random.uniform(0, math.tau)
        self.rotation: float = random.uniform(0, 360)
        self.rot_speed: float = random.uniform(-180, 180)
        self.color = random.choice(_LEAF_COLORS)

    def update(self, dt: float) -> bool:
        """Fall and drift. Returns True when below the frame."""
        self.cam_y_frac += self.cam_vy * dt
        self.drift_phase = (self.drift_phase + self.drift_freq * dt) % math.tau
        self.cam_x += self.drift_amp * math.sin(self.drift_phase) * dt
        self.rotation = (self.rotation + self.rot_speed * dt) % 360
        return self.cam_y_frac > 1.1
