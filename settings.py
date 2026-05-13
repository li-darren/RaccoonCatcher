# Window
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "RaccoonCatcher"

HUD_BAR_H = 60

# Colors (R, G, B)
COL_BG = (5, 8, 18)
COL_CCTV_BORDER = (0, 200, 0)
COL_WHITE = (255, 255, 255)
COL_BLACK = (0, 0, 0)
COL_GOLD = (255, 215, 0)
COL_TEXT = (220, 220, 220)
COL_VIEWFINDER = (200, 200, 200)
COL_VIEWFINDER_HIT = (0, 255, 80)

# Zones
NUM_ZONES = 4
ZONE_NAMES = ["Front Yard", "Back Yard", "Side Gate", "Garden Shed"]

# Camera grid — 2x2 layout below the HUD bar
CAMERA_PAD = 20
CAMERA_FEED_W = (SCREEN_WIDTH - CAMERA_PAD * 3) // 2    # 610
CAMERA_FEED_H = (SCREEN_HEIGHT - HUD_BAR_H - CAMERA_PAD * 3) // 2  # 300

# Raccoon sizes: radius (px), points, wariness (0–1), move_range (seconds between zone hops)
# Smaller raccoons are harder to catch and worth more points.
RACCOON_SIZES = {
    "small":  {"radius": 6,  "points": 100, "wariness": 0.85, "move_range": (4.0, 8.0)},
    "medium": {"radius": 10, "points": 50,  "wariness": 0.60, "move_range": (6.0, 12.0)},
    "large":  {"radius": 15, "points": 25,  "wariness": 0.35, "move_range": (8.0, 16.0)},
    "xl":     {"radius": 20, "points": 10,  "wariness": 0.15, "move_range": (12.0, 24.0)},
}

# Viewfinder
VIEWFINDER_SIZE = 80   # outer decorative border (px)
HIT_ZONE_SIZE = 40     # inner capture hot-spot (px)

# Timing
YARD_PHOTO_TIME_SEC = 6.0
TRANSITION_DURATION_MS = 800
RESULT_DISPLAY_SEC = 2.5
SHUTTER_FLASH_MS = 250
