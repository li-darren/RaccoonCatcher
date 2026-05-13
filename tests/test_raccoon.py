import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.entities.raccoon import Raccoon
from settings import RACCOON_SIZES, NUM_ZONES


class FakeRect:
    """Minimal stand-in for pygame.Rect used in yard position tests."""
    def __init__(self, left, top, width, height):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.right = left + width
        self.bottom = top + height


YARD = FakeRect(0, 60, 1280, 660)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_size_attributes_match_settings():
    for size in ("small", "medium", "large", "xl"):
        r = Raccoon(size, zone_index=0)
        cfg = RACCOON_SIZES[size]
        assert r.radius == cfg["radius"]
        assert r.points == cfg["points"]


def test_wariness_scale_applied():
    r = Raccoon("medium", zone_index=0, wariness_scale=2.0)
    base = RACCOON_SIZES["medium"]["wariness"]
    assert r.wariness == min(base * 2.0, 0.97)


def test_wariness_capped_at_97_percent():
    r = Raccoon("small", zone_index=0, wariness_scale=100.0)
    assert r.wariness == 0.97


def test_zone_index_assigned():
    for i in range(NUM_ZONES):
        r = Raccoon("medium", zone_index=i)
        assert r.zone_index == i


# ---------------------------------------------------------------------------
# is_camera_visible
# ---------------------------------------------------------------------------

def test_visible_when_cam_x_in_range():
    r = Raccoon("medium", zone_index=0)
    r.cam_x = 0.5
    assert r.is_camera_visible is True


def test_visible_at_left_boundary():
    r = Raccoon("medium", zone_index=0)
    r.cam_x = 0.0
    assert r.is_camera_visible is True


def test_visible_at_right_boundary():
    r = Raccoon("medium", zone_index=0)
    r.cam_x = 1.0
    assert r.is_camera_visible is True


def test_not_visible_left_of_frame():
    r = Raccoon("medium", zone_index=0)
    r.cam_x = -0.1
    assert r.is_camera_visible is False


def test_not_visible_right_of_frame():
    r = Raccoon("medium", zone_index=0)
    r.cam_x = 1.1
    assert r.is_camera_visible is False


# ---------------------------------------------------------------------------
# update — zone-hop timer
# ---------------------------------------------------------------------------

def test_update_decrements_timer():
    r = Raccoon("medium", zone_index=0)
    r._entering = False
    r._hopping = False
    r.move_timer = 5.0
    r.update(1.0)
    assert r.move_timer == 4.0


def test_update_triggers_hop_when_timer_expires():
    r = Raccoon("medium", zone_index=0)
    r._entering = False
    r._hopping = False
    r.move_timer = 0.1
    r.update(0.5)
    assert r._hopping is True
    assert r._hop_target_zone != r.zone_index


def test_update_hop_target_is_different_zone():
    r = Raccoon("medium", zone_index=2)
    r._entering = False
    r._hopping = False
    r.move_timer = 0.01
    r.update(1.0)
    assert r._hop_target_zone != 2


def test_update_does_not_decrement_while_entering():
    r = Raccoon("medium", zone_index=0)
    r._entering = True
    r.move_timer = 5.0
    r.update(1.0)
    assert r.move_timer == 5.0


def test_update_does_not_retrigger_hop_while_hopping():
    r = Raccoon("medium", zone_index=0)
    r._entering = False
    r._hopping = True
    r._hop_target_zone = 1
    r.move_timer = -1.0
    r.update(1.0)
    assert r._hop_target_zone == 1  # unchanged


def test_update_always_returns_false():
    r = Raccoon("small", zone_index=0)
    assert r.update(0.1) is False


# ---------------------------------------------------------------------------
# update_wander — entering state
# ---------------------------------------------------------------------------

def test_update_wander_entering_moves_toward_frame():
    r = Raccoon("medium", zone_index=0)
    r._entering = True
    r._hopping = False
    r.cam_x = -0.1
    r.cam_vx = 0.03
    r.update_wander(1.0)
    assert r.cam_x > -0.1


def test_update_wander_clears_entering_once_visible():
    r = Raccoon("medium", zone_index=0)
    r._entering = True
    r._hopping = False
    r.cam_x = 0.0
    r.cam_vx = 0.05
    r.update_wander(0.1)
    assert r._entering is False
    assert r.is_camera_visible


# ---------------------------------------------------------------------------
# update_wander — normal bounce
# ---------------------------------------------------------------------------

def test_update_wander_bounces_at_left_edge():
    r = Raccoon("medium", zone_index=0)
    r._entering = False
    r._hopping = False
    r.cam_x = 0.04
    r.cam_vx = -0.05
    r._dir_timer = 999.0  # prevent random direction flip
    r.update_wander(0.1)
    assert r.cam_vx > 0
    assert r.facing_right is True


def test_update_wander_bounces_at_right_edge():
    r = Raccoon("medium", zone_index=0)
    r._entering = False
    r._hopping = False
    r.cam_x = 0.96
    r.cam_vx = 0.05
    r._dir_timer = 999.0
    r.update_wander(0.1)
    assert r.cam_vx < 0
    assert r.facing_right is False


# ---------------------------------------------------------------------------
# update_wander — zone hop animation
# ---------------------------------------------------------------------------

def test_update_wander_hop_commits_when_off_right():
    r = Raccoon("medium", zone_index=0)
    r._hopping = True
    r._hop_target_zone = 2
    r.facing_right = True
    r.cam_x = 1.18
    r.update_wander(0.5)  # 1.18 + 0.08*0.5 = 1.22 > 1.2
    assert r.zone_index == 2
    assert r._hopping is False
    assert r._entering is True
    assert r.cam_x < 0  # restarted from left side


def test_update_wander_hop_commits_when_off_left():
    r = Raccoon("medium", zone_index=1)
    r._hopping = True
    r._hop_target_zone = 3
    r.facing_right = False
    r.cam_x = -0.18
    r.update_wander(0.5)  # -0.18 - 0.08*0.5 = -0.22 < -0.2
    assert r.zone_index == 3
    assert r._hopping is False
    assert r._entering is True
    assert r.cam_x > 1  # restarted from right side


# ---------------------------------------------------------------------------
# set_yard_position
# ---------------------------------------------------------------------------

def test_set_yard_position_x_in_bounds():
    r = Raccoon("medium", zone_index=0)
    margin = r.radius + 20
    for _ in range(30):
        r.set_yard_position(YARD)
        assert YARD.left + margin <= r.yard_pos[0] <= YARD.right - margin


def test_set_yard_position_y_in_foreground_band():
    r = Raccoon("medium", zone_index=0)
    foreground_top = YARD.top + int(YARD.height * 0.62)
    foreground_bot = YARD.bottom - (r.radius + 20) - 40
    for _ in range(30):
        r.set_yard_position(YARD)
        assert foreground_top <= r.yard_pos[1] <= foreground_bot


# ---------------------------------------------------------------------------
# set_yard_position_from_camera
# ---------------------------------------------------------------------------

def test_set_yard_position_from_camera_y_mirrors_cam_y():
    r = Raccoon("medium", zone_index=0)
    r.cam_x = 0.5
    r.cam_vx = 0.03
    r.cam_y = 0.68
    r.set_yard_position_from_camera(YARD, transition_sec=0.0)
    # Y should map from cam_y, clamped to the foreground band (>= 62% height)
    foreground_top = YARD.top + int(YARD.height * 0.62)
    assert r.yard_pos[1] >= foreground_top
    expected_y = YARD.top + int(r.cam_y * YARD.height)
    assert r.yard_pos[1] == expected_y


def test_set_yard_position_from_camera_x_left_maps_near_left():
    r = Raccoon("medium", zone_index=0)
    r.cam_x = 0.0
    r.cam_vx = -0.03  # leftward, so yard_vx negative
    r.set_yard_position_from_camera(YARD, transition_sec=0.0)
    # With cam_x=0, x = left + margin + 0 = margin
    margin = r.radius + 20
    # No drift (transition_sec=0), so x = margin, clamped to [margin, right-margin]
    assert r.yard_pos[0] >= YARD.left + margin


def test_set_yard_position_from_camera_x_right_maps_near_right():
    r = Raccoon("medium", zone_index=0)
    r.cam_x = 1.0
    r.cam_vx = 0.03
    r.set_yard_position_from_camera(YARD, transition_sec=0.0)
    margin = r.radius + 20
    expected_x_base = YARD.left + margin + 1.0 * (YARD.width - 2 * margin)
    # Clamped to right-margin
    assert r.yard_pos[0] <= YARD.right - margin


def test_set_yard_position_from_camera_facing_matches_vx():
    r = Raccoon("medium", zone_index=0)
    r.cam_x = 0.5
    r.cam_vx = 0.03  # rightward
    r.set_yard_position_from_camera(YARD, transition_sec=0.0)
    assert r.yard_vx > 0
    assert r.facing_right is True

    r.cam_vx = -0.03  # leftward
    r.set_yard_position_from_camera(YARD, transition_sec=0.0)
    assert r.yard_vx < 0
    assert r.facing_right is False
