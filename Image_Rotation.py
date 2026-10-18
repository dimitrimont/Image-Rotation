"""
Image rotation by hand: turn a picture by theta again and again until it is upright, and measure
what the turns cost.

    canvas  ->  every pixel looks up where it came from (2 x 2 matrix, rounded)  ->  360 / theta turns  ->  errors

CSC 340, spring 2025. The rotation is a 2 x 2 matrix multiplication written out by hand and
applied backwards: each pixel of the turned picture looks up the pixel it came from, so the result
has no holes. OpenCV only loads, shows and saves the images.

Revised 2026-10-18. Measured on the drawn test card in test_rotation.py:

- It turned half way round. `cycles = 180 // theta` gave 4 turns of 45 degrees, so the final
  picture was upside down and the colour error mostly measured that (95.7 over the picture). Now
  it turns 360 / theta times, back to upright.
- It truncated. `int()` drops the fraction, so every lookup leaned half a pixel toward the top
  left, and even 90-degree turns slipped (cos 90 comes out as 6e-17, not 0). Now each lookup is
  rounded to the nearest pixel. All the way round in 45-degree steps, the colour error falls from
  14.1 to 3.2 and pixels end 0.17 px from where they began instead of 0.79.
- The displacement error was the rounding error times the number of turns, not a measurement.
  Now every pixel is followed through every turn, and the distance from where it ends up to where
  it began is averaged.
- The canvas was 1.8 times the picture, which cut the corners off wide pictures (a 2:1 picture
  lost 10% of itself at 90 degrees). Now the canvas is as wide as the picture's diagonal, which
  holds it at any angle.
- The copy onto the canvas skipped the picture's outermost row and column, and the colour error was
  averaged over the whole canvas, mostly black border. Now the whole picture is copied and the
  errors are averaged over the picture.

Usage:
    python Image_Rotation.py photo.png [--theta 30] [--truncate]
    python Image_Rotation.py --drawn                  # the drawn test card
    python Image_Rotation.py                          # asks for a file name, as before
"""

import argparse
import math
import sys

import cv2
import numpy as np


# ── the rotation ──────────────────────────────────────────────────────────────────────────


def matrix_multiply(m, v):
    """A 2 x 2 matrix times a 2-vector, by hand."""
    out = [0.0, 0.0]
    for i in range(2):
        for j in range(2):
            out[i] += m[i][j] * v[j]
    return out


def rotation_matrix(theta):
    a = math.radians(theta)
    return [[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]


def on_canvas(image):
    """The picture centred on a square black canvas as wide as its diagonal, so no turn can push
    it off the edge. Pixels are (b, g, r) tuples in rows of lists. Returns the canvas, its size,
    and where the picture sits on it (top, left)."""
    rows, cols = len(image), len(image[0])
    size = math.ceil(math.hypot(rows, cols)) + 4
    top, left = size // 2 - rows // 2, size // 2 - cols // 2
    canvas = [[(0, 0, 0)] * size for _ in range(size)]
    for i in range(rows):
        for j in range(cols):
            canvas[top + i][left + j] = image[i][j]
    return canvas, size, (top, left)


def lookups(size, theta, truncate=False):
    """For every canvas pixel, the pixel it takes its colour from when the picture turns by theta,
    or None if that is off the canvas; and how far the exact source point was from the pixel
    used, on average. The turn is about the canvas centre, a whole pixel, so turns of 90 degrees
    move every pixel exactly onto another."""
    m, c = rotation_matrix(theta), size // 2
    table, off, n = [], 0.0, 0
    for i in range(size):
        row = []
        for j in range(size):
            x, y = matrix_multiply(m, [j - c, i - c])
            x, y = x + c, y + c
            sx, sy = (int(x), int(y)) if truncate else (round(x), round(y))
            if 0 <= sx < size and 0 <= sy < size:
                row.append((sy, sx))
                off += math.hypot(x - sx, y - sy)
                n += 1
            else:
                row.append(None)
        table.append(row)
    return table, off / n


def turn(canvas, table):
    """One turn: every pixel takes the colour its lookup points to."""
    black = (0, 0, 0)
    return [[canvas[s[0]][s[1]] if s else black for s in row] for row in table]


def rotate(image, theta=45, truncate=False):
    """Turn the picture by theta, 360 / theta times, so it ends upright, and measure the cost.

    Returns the canvas before and after, and a report:
      rounding_px      how far each lookup's exact point was from the pixel it used, on average
      displacement_px  how far each pixel of the picture ends up from the pixel its colour came
                       from, found by following every lookup through every turn
      moved            the share of the picture's pixels whose colour came from somewhere else
      colour_error     the mean distance between start and end colours, (b, g, r) as a point,
                       over the picture
    """
    if theta <= 0 or 360 % theta:
        raise ValueError("theta must divide 360, so the picture comes back upright")
    start, size, (top, left) = on_canvas(image)
    table, rounding = lookups(size, theta, truncate)
    turns = 360 // theta

    canvas = start
    origin = [[(i, j) for j in range(size)] for i in range(size)]
    for _ in range(turns):
        canvas = turn(canvas, table)
        origin = [[origin[s[0]][s[1]] if s else None for s in row] for row in table]

    rows, cols = len(image), len(image[0])
    dist = colour = moved = 0.0
    for i in range(top, top + rows):
        for j in range(left, left + cols):
            o = origin[i][j]
            d = math.hypot(o[0] - i, o[1] - j) if o else float("nan")
            dist += d
            moved += d > 0
            colour += math.dist(start[i][j], canvas[i][j])
    n = rows * cols
    report = {"turns": turns, "rounding_px": rounding, "displacement_px": dist / n, "moved": moved / n, "colour_error": colour / n}
    return start, canvas, report


# ── a picture with a known answer ─────────────────────────────────────────────────────────


def drawn_card(width=120, height=90):
    """A small coloured test card: a grid, two blocks, a disc and a diagonal line."""
    img = np.full((height, width, 3), (235, 230, 225), np.uint8)
    for x in range(0, width, 15):
        cv2.line(img, (x, 0), (x, height - 1), (180, 170, 160), 1)
    for y in range(0, height, 15):
        cv2.line(img, (0, y), (width - 1, y), (180, 170, 160), 1)
    cv2.rectangle(img, (10, 10), (45, 40), (40, 90, 200), -1)
    cv2.rectangle(img, (70, 50), (110, 80), (60, 160, 70), -1)
    cv2.circle(img, (85, 25), 14, (200, 120, 40), -1)
    cv2.line(img, (5, 85), (60, 45), (20, 20, 20), 2)
    return img


def as_pixels(img):
    """An OpenCV image as rows of (b, g, r) tuples, for the loops above."""
    return [[tuple(int(c) for c in px) for px in row] for row in img]


def as_image(canvas):
    return np.array(canvas, np.uint8)


# ── run ───────────────────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Turn a picture all the way round in steps, by hand.")
    parser.add_argument("image", nargs="?", help="an image file; without one, it asks")
    parser.add_argument("--theta", type=int, default=45, help="degrees per turn; must divide 360 (default 45)")
    parser.add_argument("--truncate", action="store_true", help="drop the fraction instead of rounding, as the first version did")
    parser.add_argument("--drawn", action="store_true", help="use the drawn test card")
    parser.add_argument("--no-show", action="store_true", help="save the result without opening a window")
    args = parser.parse_args()

    if args.drawn:
        img = drawn_card()
    else:
        path = args.image or input("Enter image file name (with .png, .jpg, ... at the end): ").strip()
        img = cv2.imread(path)
        if img is None:
            sys.exit(f"Could not load {path}.")

    try:
        _, final, r = rotate(as_pixels(img), args.theta, args.truncate)
    except ValueError as e:
        sys.exit(str(e))
    how = "truncated" if args.truncate else "rounded"
    print(f"{r['turns']} turns of {args.theta} degrees, lookups {how}")
    print(f"Rounding error:     {r['rounding_px']:.3f} px per lookup")
    print(f"Displacement error: {r['displacement_px']:.3f} px; {r['moved']:.0%} of pixels end up holding another pixel's colour")
    print(f"Colour error:       {r['colour_error']:.2f} (mean distance between start and end colours)")

    out = as_image(final)
    cv2.imwrite("assign1_RotIMG.png", out)
    print("Saved assign1_RotIMG.png")
    if not args.no_show:
        cv2.imshow("Rotated", out)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
