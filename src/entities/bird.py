import math
import random


class Bird:
    def __init__(self, zone_index: int):
        self.zone_index = zone_index
        self.cam_y_frac = random.uniform(0.06, 0.30)
        if random.random() < 0.5:
            self.cam_x = -0.12
            self.cam_vx = random.uniform(0.12, 0.30)
            self.facing_right = True
        else:
            self.cam_x = 1.12
            self.cam_vx = -random.uniform(0.12, 0.30)
            self.facing_right = False
        self.wing_phase: float = random.uniform(0, math.tau)

    def update(self, dt: float) -> bool:
        """Move bird and advance wing animation. Returns True when off-screen."""
        self.cam_x += self.cam_vx * dt
        self.wing_phase = (self.wing_phase + 8.0 * dt) % math.tau
        return self.cam_x < -0.2 or self.cam_x > 1.2
