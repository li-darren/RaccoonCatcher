"""Pure fade-alpha computation for TransitionState — no pygame dependency."""


def compute_fade_alpha(elapsed_ms: float, phase: str, half_duration_ms: float) -> int:
    """Return overlay alpha (0–255) given elapsed time and current phase."""
    if phase == "fade_out":
        return min(int(255 * elapsed_ms / half_duration_ms), 255)
    return max(int(255 * (1.0 - elapsed_ms / half_duration_ms)), 0)
