import random


class TrashBag:
    # Placed at ground level matching raccoon height in the camera feed (cam_y_frac = 0.65).
    CAM_Y_FRAC = 0.65

    def __init__(self, zone_index: int):
        self.zone_index = zone_index
        self.cam_x = random.uniform(0.15, 0.85)
        self.cam_y_frac = self.CAM_Y_FRAC
