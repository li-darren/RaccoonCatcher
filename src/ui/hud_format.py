"""Pure formatting helpers for HUD display — no pygame dependency."""


def format_timer(timer_sec: float) -> str:
    """Convert seconds to MM:SS string."""
    total = max(int(timer_sec), 0)
    return f"{total // 60:02d}:{total % 60:02d}"


def timer_color(timer_sec: float) -> tuple:
    """Red when under 30 s, white otherwise."""
    return (255, 70, 70) if timer_sec < 30 else (220, 220, 220)


def photo_bar_ratio(timer_sec: float, max_sec: float = 6.0) -> float:
    """Fill ratio [0, 1] for the photo-countdown bar."""
    return max(timer_sec / max_sec, 0.0)


def photo_bar_color(timer_sec: float) -> tuple:
    """Red when 3 s or under, green otherwise."""
    return (200, 70, 70) if timer_sec <= 3 else (70, 190, 70)
