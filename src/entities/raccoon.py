import random
from settings import RACCOON_SIZES, NUM_ZONES


class Raccoon:
    def __init__(self, size: str, zone_index: int,
                 wariness_scale: float = 1.0, speed_scale: float = 1.0):
        self.size = size
        cfg = RACCOON_SIZES[size]
        self.radius: int = cfg["radius"]
        self.points: int = cfg["points"]
        self.wariness: float = min(cfg["wariness"] * wariness_scale, 0.97)

        lo, hi = cfg["move_range"]
        lo = max(lo * speed_scale, 1.0)
        hi = max(hi * speed_scale, 2.0)
        self.move_range = (lo, hi)

        self.zone_index: int = zone_index
        self.move_timer: float = random.uniform(*self.move_range)
        self.yard_pos: list = [0, 0]

        # Camera lateral wandering (normalized: 0=left edge, 1=right edge).
        # 85% chance: spawn off-screen and walk slowly into view (~5-16 s).
        if random.random() < 0.85:
            if random.random() < 0.5:
                self.cam_x = random.uniform(-0.25, -0.05)
                self.cam_vx = random.uniform(0.015, 0.04)   # rightward slow entry
            else:
                self.cam_x = random.uniform(1.05, 1.25)
                self.cam_vx = -random.uniform(0.015, 0.04)  # leftward slow entry
            self._entering = True
        else:
            self.cam_x = random.uniform(0.2, 0.8)
            self.cam_vx = random.choice([-1, 1]) * random.uniform(0.025, 0.07)
            self._entering = False
        self.facing_right: bool = self.cam_vx >= 0
        self._dir_timer: float = random.uniform(3.0, 9.0)

        # Zone-hop animation state
        self._hopping: bool = False
        self._hop_target_zone: int = -1

        # Yard lateral speed (pixels/sec); direction set again in set_yard_position
        self.yard_vx: float = random.choice([-1, 1]) * random.uniform(25, 70)

    @property
    def is_camera_visible(self) -> bool:
        """True when the raccoon is within the camera feed's visible area."""
        return 0.0 <= self.cam_x <= 1.0

    def update(self, dt: float) -> bool:
        """Tick zone-hop timer. Zone change is animated via update_wander."""
        # Don't allow zone hops while the raccoon is still walking on-screen.
        if not self._entering:
            self.move_timer -= dt
            if self.move_timer <= 0 and not self._hopping:
                available = [z for z in range(NUM_ZONES) if z != self.zone_index]
                self._hop_target_zone = random.choice(available)
                self._hopping = True
                self.move_timer = random.uniform(*self.move_range)
        return False

    def update_wander(self, dt: float):
        """Tick lateral wandering for the camera view."""
        if self._hopping:
            # Walk off-screen at full speed in the current travel direction
            self.cam_vx = 0.08 if self.facing_right else -0.08
            self.cam_x += self.cam_vx * dt
            # Once fully off-screen, commit the zone change and enter from opposite edge
            if self.cam_x > 1.2:
                self.zone_index = self._hop_target_zone
                self._hopping = False
                self._hop_target_zone = -1
                self.cam_x = -0.15
                self.cam_vx = 0.05
                self.facing_right = True
                self._entering = True
            elif self.cam_x < -0.2:
                self.zone_index = self._hop_target_zone
                self._hopping = False
                self._hop_target_zone = -1
                self.cam_x = 1.15
                self.cam_vx = -0.05
                self.facing_right = False
                self._entering = True
            return

        self.cam_x += self.cam_vx * dt

        if self._entering:
            # Walk straight in; once fully on-screen switch to normal wander speed
            if 0.0 <= self.cam_x <= 1.0:
                self._entering = False
                speed = random.uniform(0.025, 0.07)
                self.cam_vx = speed if self.cam_vx >= 0 else -speed
            return

        # Normal bounce and direction-change logic
        if self.cam_x < 0.05:
            self.cam_vx = abs(self.cam_vx)
            self.facing_right = True
        elif self.cam_x > 0.95:
            self.cam_vx = -abs(self.cam_vx)
            self.facing_right = False

        self._dir_timer -= dt
        if self._dir_timer <= 0:
            if random.random() < 0.35:
                self.cam_vx = -self.cam_vx
                self.facing_right = self.cam_vx >= 0
            self._dir_timer = random.uniform(3.0, 9.0)

    def set_yard_position(self, yard_rect):
        margin = self.radius + 20
        x = random.randint(yard_rect.left + margin, yard_rect.right - margin)
        # Keep raccoons in the foreground (lower ~38% of the scene) so they
        # appear below all zone props (fences, shed, gate, garden).
        foreground_top = yard_rect.top + int(yard_rect.height * 0.62)
        foreground_bot = yard_rect.bottom - margin - 40
        y = random.randint(foreground_top, max(foreground_top, foreground_bot))
        self.yard_pos = [x, y]
        self.yard_vx = random.choice([-1, 1]) * random.uniform(25, 70)
        self.facing_right = self.yard_vx >= 0

    def set_yard_position_from_camera(self, yard_rect, transition_sec: float = 0.8):
        """Place the raccoon at a yard position consistent with where it was on camera,
        drifted by the travel time during transition."""
        margin = self.radius + 20
        usable_w = yard_rect.width - 2 * margin
        x = yard_rect.left + margin + self.cam_x * usable_w
        # Continue moving in the same direction as on camera
        speed = random.uniform(25, 70)
        self.yard_vx = speed if self.cam_vx >= 0 else -speed
        self.facing_right = self.yard_vx >= 0
        x += self.yard_vx * transition_sec
        self.yard_pos[0] = max(yard_rect.left + margin,
                               min(x, yard_rect.right - margin))
        # 65% of yard height maps exactly to where the raccoon sits on camera,
        # and falls below all zone props in the foreground grass.
        self.yard_pos[1] = yard_rect.top + int(yard_rect.height * 0.65)

    def flee_probability(self, seconds_in_camera: float) -> float:
        """Chance the raccoon bolts before the player arrives."""
        base = self.wariness * min(seconds_in_camera / 60.0, 1.0)
        return min(base, 0.95)
