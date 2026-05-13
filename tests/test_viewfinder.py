import os
import sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pygame
pygame.init()

from unittest.mock import patch
from src.entities.viewfinder import Viewfinder
from settings import HIT_ZONE_SIZE

_HALF = HIT_ZONE_SIZE // 2  # 20 with default HIT_ZONE_SIZE=40


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_initial_is_hit_false():
    v = Viewfinder()
    assert v.is_hit is False


def test_initial_hit_size():
    v = Viewfinder()
    assert v.hit_size == HIT_ZONE_SIZE


# ---------------------------------------------------------------------------
# hit_test — pure geometry
# ---------------------------------------------------------------------------

def test_hit_test_exact_center():
    v = Viewfinder()
    v.pos = (100, 200)
    assert v.hit_test((100, 200)) is True


def test_hit_test_within_box():
    v = Viewfinder()
    v.pos = (100, 200)
    assert v.hit_test((100 + _HALF - 1, 200 + _HALF - 1)) is True


def test_hit_test_at_boundary():
    v = Viewfinder()
    v.pos = (100, 200)
    assert v.hit_test((100 + _HALF, 200)) is True
    assert v.hit_test((100 - _HALF, 200)) is True
    assert v.hit_test((100, 200 + _HALF)) is True
    assert v.hit_test((100, 200 - _HALF)) is True


def test_hit_test_just_outside_x():
    v = Viewfinder()
    v.pos = (100, 200)
    assert v.hit_test((100 + _HALF + 1, 200)) is False


def test_hit_test_just_outside_y():
    v = Viewfinder()
    v.pos = (100, 200)
    assert v.hit_test((100, 200 + _HALF + 1)) is False


def test_hit_test_x_miss_y_ok():
    v = Viewfinder()
    v.pos = (100, 200)
    assert v.hit_test((100 + _HALF + 5, 200)) is False


def test_hit_test_x_ok_y_miss():
    v = Viewfinder()
    v.pos = (100, 200)
    assert v.hit_test((100, 200 - _HALF - 5)) is False


def test_hit_test_far_away():
    v = Viewfinder()
    v.pos = (0, 0)
    assert v.hit_test((640, 360)) is False


# ---------------------------------------------------------------------------
# update — is_hit derived from hit_test
# ---------------------------------------------------------------------------

def test_update_sets_is_hit_when_raccoon_at_cursor():
    v = Viewfinder()
    cursor = (300, 400)
    with patch("pygame.mouse.get_pos", return_value=cursor):
        v.update([cursor])
    assert v.is_hit is True


def test_update_clears_is_hit_when_raccoon_far():
    v = Viewfinder()
    cursor = (300, 400)
    far = (600, 600)
    with patch("pygame.mouse.get_pos", return_value=cursor):
        v.update([far])
    assert v.is_hit is False


def test_update_no_raccoons_clears_is_hit():
    v = Viewfinder()
    v.is_hit = True
    with patch("pygame.mouse.get_pos", return_value=(300, 400)):
        v.update(None)
    assert v.is_hit is False


def test_update_empty_list_clears_is_hit():
    v = Viewfinder()
    v.is_hit = True
    with patch("pygame.mouse.get_pos", return_value=(300, 400)):
        v.update([])
    assert v.is_hit is False


def test_update_any_raccoon_in_zone_sets_is_hit():
    v = Viewfinder()
    cursor = (300, 400)
    far = (600, 600)
    with patch("pygame.mouse.get_pos", return_value=cursor):
        v.update([far, cursor])  # second one is in the zone
    assert v.is_hit is True


def test_update_sets_pos_from_mouse():
    v = Viewfinder()
    with patch("pygame.mouse.get_pos", return_value=(123, 456)):
        v.update(None)
    assert v.pos == (123, 456)
