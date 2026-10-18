# Image rotation, by hand

Coursework for CSC 340 (Computer Vision), spring 2025. It turns a picture by an angle theta again
and again until it is upright, and measures what all those turns cost: how far the pixels end up
from where they began, and how much the colours change. The rotation is a 2 × 2 matrix
multiplication written out by hand; OpenCV only loads, shows and saves the images.

**Live walkthrough:** https://dimitri-montgomery-site.pages.dev/vision/image-rotation/ turns a
drawn test card in the browser, with the first version beside the revised one.

## What is here

| File | What it is |
|---|---|
| `Image_Rotation.py` | The rotation, the error measures, and a drawn test card |
| `test_rotation.py` | Checks it on the test card, where the right answer is known |

## How it works

The picture is centred on a black square canvas as wide as its diagonal, so no turn can push it
off the edge. Each turn runs backwards: every pixel of the turned picture multiplies its position
(relative to the centre) by the rotation matrix to find the point it came from, rounds that to the
nearest pixel, and takes its colour. Working backwards means no pixel is left empty. After
360 / theta turns the picture is upright again, and three errors are measured over the picture:

- **Rounding error:** how far each lookup's exact point was from the pixel it used, on average.
- **Displacement error:** how far each pixel ends up from the pixel its colour came from, found by
  following every lookup through every turn.
- **Colour error:** the mean distance between each pixel's start and end colours, treating
  (blue, green, red) as a point.

### What changed on 2026-10-18

- **It turns all the way round.** `cycles = 180 // theta` gave 4 turns of 45 degrees, so the
  final picture was upside down, and the colour error mostly measured that.
- **It rounds instead of truncating.** `int()` drops the fraction, so every lookup leaned half a
  pixel toward the top left. Even 90-degree turns slipped, because cos 90° comes out as 6e-17,
  not 0.
- **Displacement is measured.** It used to be the rounding error times the number of turns.
- **Nothing is cropped.** The canvas was 1.8 times the picture, which cut the corners off wide
  pictures: a 2:1 picture lost 10% of itself at 90 degrees, a 3:1 picture 40%.
- **The whole picture counts.** The copy onto the canvas skipped the outermost row and column,
  and the colour error was averaged over the whole canvas, mostly black border.
- **Any angle that divides 360**, with `--theta`; `--truncate` brings back the old lookups for
  comparison.

Measured on the drawn test card (120 × 90), all the way round in 45-degree steps, averaged over
the picture:

| | Displacement | Pixels holding another pixel's colour | Colour error |
|---|---|---|---|
| Truncated, as before | 0.79 px | 55% | 14.1 |
| Rounded, now | 0.17 px | 17% | 3.2 |

As first written, stopping at 180 degrees, the colour error over the picture was 95.7. In
90-degree steps every pixel now lands exactly where it began.

## Limits

Rounding to the nearest pixel is the simplest lookup. Blending the four nearest pixels (bilinear
interpolation) would keep edges smoother at the cost of some blur; it is not built.

## Run

```bash
pip install opencv-python numpy pytest
python -m pytest test_rotation.py                     # no images needed
python Image_Rotation.py --drawn --no-show            # the drawn test card
python Image_Rotation.py photo.png --theta 30
```

It prints the three errors and saves the final picture as `assign1_RotIMG.png`.
