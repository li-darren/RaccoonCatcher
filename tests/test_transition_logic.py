from src.states.transition_logic import compute_fade_alpha


class TestComputeFadeAlpha:
    # --- fade_out phase ---

    def test_fade_out_start_is_zero(self):
        assert compute_fade_alpha(0, "fade_out", 500) == 0

    def test_fade_out_end_is_255(self):
        assert compute_fade_alpha(500, "fade_out", 500) == 255

    def test_fade_out_midpoint(self):
        alpha = compute_fade_alpha(250, "fade_out", 500)
        assert alpha == 127

    def test_fade_out_clamps_at_255(self):
        assert compute_fade_alpha(1000, "fade_out", 500) == 255

    # --- fade_in phase ---

    def test_fade_in_start_is_255(self):
        assert compute_fade_alpha(0, "fade_in", 500) == 255

    def test_fade_in_end_is_zero(self):
        assert compute_fade_alpha(500, "fade_in", 500) == 0

    def test_fade_in_midpoint(self):
        alpha = compute_fade_alpha(250, "fade_in", 500)
        assert alpha == 127

    def test_fade_in_clamps_at_zero(self):
        assert compute_fade_alpha(1000, "fade_in", 500) == 0

    # --- return type ---

    def test_returns_int(self):
        assert isinstance(compute_fade_alpha(100, "fade_out", 500), int)
