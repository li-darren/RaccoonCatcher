from src.states.result_logic import decide_next_state


class TestDecideNextState:
    def test_timer_out_returns_game_over(self):
        state, kwargs = decide_next_state(timer_remaining=0, score=50,
                                          score_target=100, zone_index=2)
        assert state == "game_over"
        assert kwargs == {}

    def test_negative_timer_returns_game_over(self):
        state, kwargs = decide_next_state(-1, 0, 100, 0)
        assert state == "game_over"

    def test_score_reached_returns_level_complete(self):
        state, kwargs = decide_next_state(timer_remaining=30, score=100,
                                          score_target=100, zone_index=1)
        assert state == "level_complete"
        assert kwargs == {}

    def test_score_exceeded_returns_level_complete(self):
        state, kwargs = decide_next_state(30, 200, 100, 3)
        assert state == "level_complete"

    def test_normal_advance_returns_camera_with_exclude_zone(self):
        state, kwargs = decide_next_state(timer_remaining=30, score=50,
                                          score_target=100, zone_index=2)
        assert state == "camera"
        assert kwargs == {"exclude_zone": 2}

    def test_exclude_zone_matches_zone_index(self):
        for zone in range(4):
            state, kwargs = decide_next_state(30, 0, 100, zone)
            assert kwargs.get("exclude_zone") == zone

    def test_game_over_takes_priority_over_score(self):
        # timer at zero even if score is huge → game over
        state, _ = decide_next_state(0, 9999, 100, 0)
        assert state == "game_over"
