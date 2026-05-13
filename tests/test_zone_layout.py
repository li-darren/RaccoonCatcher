from src.systems.zone_layout import camera_grid_rects, yard_rect_bounds


PAD, FEED_W, FEED_H, HUD_H = 10, 320, 240, 50


class TestCameraGridRects:
    def setup_method(self):
        self.rects = camera_grid_rects(PAD, FEED_W, FEED_H, HUD_H)

    def test_returns_four_rects(self):
        assert len(self.rects) == 4

    def test_all_rects_have_correct_dimensions(self):
        for r in self.rects:
            assert r[2] == FEED_W
            assert r[3] == FEED_H

    def test_row_0_col_0_position(self):
        x, y, w, h = self.rects[0]
        assert x == PAD
        assert y == HUD_H + PAD

    def test_row_0_col_1_position(self):
        x, y, w, h = self.rects[1]
        assert x == PAD + FEED_W + PAD
        assert y == HUD_H + PAD

    def test_row_1_col_0_position(self):
        x, y, w, h = self.rects[2]
        assert x == PAD
        assert y == HUD_H + PAD + FEED_H + PAD

    def test_row_1_col_1_position(self):
        x, y, w, h = self.rects[3]
        assert x == PAD + FEED_W + PAD
        assert y == HUD_H + PAD + FEED_H + PAD

    def test_same_row_rects_share_y(self):
        assert self.rects[0][1] == self.rects[1][1]
        assert self.rects[2][1] == self.rects[3][1]

    def test_same_col_rects_share_x(self):
        assert self.rects[0][0] == self.rects[2][0]
        assert self.rects[1][0] == self.rects[3][0]

    def test_rects_are_tuples_of_four(self):
        for r in self.rects:
            assert len(r) == 4


class TestYardRectBounds:
    def test_left_is_zero(self):
        left, top, w, h = yard_rect_bounds(800, 600, HUD_H)
        assert left == 0

    def test_top_equals_hud_height(self):
        left, top, w, h = yard_rect_bounds(800, 600, HUD_H)
        assert top == HUD_H

    def test_width_equals_screen_width(self):
        left, top, w, h = yard_rect_bounds(800, 600, HUD_H)
        assert w == 800

    def test_height_is_screen_minus_hud(self):
        left, top, w, h = yard_rect_bounds(800, 600, HUD_H)
        assert h == 550

    def test_zero_hud(self):
        left, top, w, h = yard_rect_bounds(1280, 720, 0)
        assert top == 0
        assert h == 720
