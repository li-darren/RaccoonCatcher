import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.systems.level_config import LevelConfig, LEVELS


def test_levels_non_empty():
    assert len(LEVELS) > 0


def test_level_nums_match_position():
    for i, level in enumerate(LEVELS):
        assert level.level_num == i + 1


def test_all_score_targets_positive():
    for level in LEVELS:
        assert level.score_target > 0


def test_all_time_limits_positive():
    for level in LEVELS:
        assert level.time_limit_sec > 0


def test_all_raccoon_counts_positive():
    for level in LEVELS:
        assert level.raccoon_count > 0


def test_all_wariness_scales_positive():
    for level in LEVELS:
        assert level.wariness_scale > 0


def test_all_speed_scales_positive():
    for level in LEVELS:
        assert level.speed_scale > 0


def test_score_targets_increase_across_levels():
    targets = [lv.score_target for lv in LEVELS]
    assert targets == sorted(targets)


def test_level_config_is_dataclass():
    lc = LevelConfig(
        level_num=99, score_target=1000, time_limit_sec=120.0,
        raccoon_count=3, wariness_scale=1.5, speed_scale=0.8,
    )
    assert lc.level_num == 99
    assert lc.score_target == 1000
    assert lc.time_limit_sec == 120.0
    assert lc.raccoon_count == 3
    assert lc.wariness_scale == 1.5
    assert lc.speed_scale == 0.8


def test_later_levels_harder_wariness():
    # Wariness should not decrease across levels (raccoons get harder, not easier)
    for i in range(len(LEVELS) - 1):
        assert LEVELS[i + 1].wariness_scale >= LEVELS[i].wariness_scale


def test_later_levels_faster_movement():
    # Lower speed_scale = shorter hop intervals = raccoons move more often
    for i in range(len(LEVELS) - 1):
        assert LEVELS[i + 1].speed_scale <= LEVELS[i].speed_scale
