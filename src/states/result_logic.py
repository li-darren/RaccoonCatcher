"""Pure next-state decision for ResultState — no pygame dependency."""


def decide_next_state(timer_remaining: float, score: int,
                      score_target: int, zone_index: int) -> tuple:
    """Return (state_name, kwargs) for the transition out of the result screen."""
    if timer_remaining <= 0:
        return ("game_over", {})
    if score >= score_target:
        return ("level_complete", {})
    return ("camera", {"exclude_zone": zone_index})
