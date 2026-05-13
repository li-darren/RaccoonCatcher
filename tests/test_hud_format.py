from src.ui.hud_format import format_timer, timer_color, photo_bar_ratio, photo_bar_color


class TestFormatTimer:
    def test_zero(self):
        assert format_timer(0) == "00:00"

    def test_negative_clamps_to_zero(self):
        assert format_timer(-5) == "00:00"

    def test_one_minute(self):
        assert format_timer(60) == "01:00"

    def test_mixed(self):
        assert format_timer(90) == "01:30"

    def test_large(self):
        assert format_timer(3661) == "61:01"

    def test_fractional_truncated(self):
        assert format_timer(59.9) == "00:59"

    def test_zero_pads_both_fields(self):
        assert format_timer(5) == "00:05"


class TestTimerColor:
    def test_below_30_is_red(self):
        assert timer_color(0) == (255, 70, 70)

    def test_exactly_29_is_red(self):
        assert timer_color(29.9) == (255, 70, 70)

    def test_exactly_30_is_white(self):
        assert timer_color(30) == (220, 220, 220)

    def test_above_30_is_white(self):
        assert timer_color(60) == (220, 220, 220)


class TestPhotoBarRatio:
    def test_full_at_max(self):
        assert photo_bar_ratio(6.0) == 1.0

    def test_half(self):
        assert photo_bar_ratio(3.0) == 0.5

    def test_zero(self):
        assert photo_bar_ratio(0) == 0.0

    def test_negative_clamps_to_zero(self):
        assert photo_bar_ratio(-1) == 0.0

    def test_over_max_exceeds_one(self):
        assert photo_bar_ratio(9.0) == 1.5

    def test_custom_max(self):
        assert photo_bar_ratio(5.0, max_sec=10.0) == 0.5


class TestPhotoBarColor:
    def test_exactly_3_is_red(self):
        assert photo_bar_color(3) == (200, 70, 70)

    def test_below_3_is_red(self):
        assert photo_bar_color(1) == (200, 70, 70)

    def test_above_3_is_green(self):
        assert photo_bar_color(3.1) == (70, 190, 70)

    def test_full_timer_is_green(self):
        assert photo_bar_color(6) == (70, 190, 70)
