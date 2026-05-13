import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.entities.trash_bag import TrashBag


def test_cam_x_in_valid_range():
    for _ in range(50):
        bag = TrashBag(zone_index=0)
        assert 0.15 <= bag.cam_x <= 0.85


def test_cam_y_frac_matches_raccoon_level():
    bag = TrashBag(zone_index=0)
    assert bag.cam_y_frac == TrashBag.CAM_Y_FRAC


def test_zone_index_assigned():
    for i in range(4):
        bag = TrashBag(zone_index=i)
        assert bag.zone_index == i


def test_cam_y_frac_constant():
    # Multiple instances share the same ground level
    bags = [TrashBag(zone_index=i) for i in range(4)]
    assert all(b.cam_y_frac == bags[0].cam_y_frac for b in bags)
