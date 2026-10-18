"""
Checks the rotation on a drawn test card, where the right answer is known: after turning all the
way round, the card should be back where it started, and turns of 90 degrees move every pixel
exactly onto another.

    python -m pytest test_rotation.py       or       python test_rotation.py
"""

import numpy as np

import Image_Rotation as rot


def card():
    return rot.as_pixels(rot.drawn_card())


def picture_of(canvas, image):
    """The picture's own area on the canvas."""
    rows, cols = len(image), len(image[0])
    size = len(canvas)
    top, left = size // 2 - rows // 2, size // 2 - cols // 2
    return rot.as_image(canvas)[top:top + rows, left:left + cols]


def test_comes_back_upright():
    """The first version stopped at 180 degrees, so its final picture was upside down."""
    img = card()
    start, final, r = rot.rotate(img, 45)
    assert r["turns"] == 8
    assert r["colour_error"] < 5
    assert r["displacement_px"] < 0.25


def test_rounding_beats_truncating():
    """Truncation leans every lookup half a pixel to the top left; rounding does not."""
    img = card()
    _, _, rounded = rot.rotate(img, 45)
    _, _, truncated = rot.rotate(img, 45, truncate=True)
    assert rounded["rounding_px"] < 0.4 < 0.7 < truncated["rounding_px"]
    assert rounded["displacement_px"] < truncated["displacement_px"] / 3
    assert rounded["colour_error"] < truncated["colour_error"] / 3


def test_quarter_turns_are_exact():
    img = card()
    start, final, r = rot.rotate(img, 90)
    assert r["colour_error"] == 0 and r["displacement_px"] == 0
    assert np.array_equal(picture_of(final, img), rot.drawn_card())


def test_one_half_turn_is_upside_down():
    """Two turns of 90 degrees: every pixel lands exactly opposite the centre pixel c."""
    img = card()
    start, size, _ = rot.on_canvas(img)
    table, _ = rot.lookups(size, 90)
    half = rot.turn(rot.turn(start, table), table)
    c = size // 2
    for i in range(size):
        for j in range(size):
            si, sj = 2 * c - i, 2 * c - j
            assert half[i][j] == (start[si][sj] if 0 <= si < size and 0 <= sj < size else (0, 0, 0))


def test_wide_pictures_keep_their_corners():
    """The first version's canvas was 1.8 times the picture: a 3:1 picture lost 40% at 90 degrees."""
    wide = [[(255, 255, 255)] * 180 for _ in range(60)]
    start, size, _ = rot.on_canvas(wide)
    for theta in (45, 90):
        table, _ = rot.lookups(size, theta)
        turned = rot.as_image(rot.turn(start, table))
        white = (turned == 255).all(axis=2).sum()
        assert abs(white - 180 * 60) < 0.02 * 180 * 60
        assert not turned[0].any() and not turned[-1].any() and not turned[:, 0].any() and not turned[:, -1].any()


def test_the_whole_picture_is_copied():
    """The first version skipped the picture's outermost row and column."""
    img = card()
    start, _, _ = rot.on_canvas(img)
    assert np.array_equal(picture_of(start, img), rot.drawn_card())


def test_theta_must_come_back_round():
    try:
        rot.rotate(card(), 50)
    except ValueError:
        return
    raise AssertionError("50 degrees does not divide 360")


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"ok  {name}")
