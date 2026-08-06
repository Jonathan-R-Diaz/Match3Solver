"""Color swatches for rendered boards. Real Royal Kingdom screenshots are
classified by hue in classify.py — this palette only serves synth.py's flat
tiles (the sim loop and the tests)."""
import numpy as np


class UnknownCellError(Exception):
    """A cell's color matched nothing in the palette. Carries enough context
    to debug the frame instead of guessing."""

    def __init__(self, r, c, rgb, best_symbol, best_dist):
        self.r, self.c, self.rgb = r, c, tuple(int(v) for v in rgb)
        self.best_symbol, self.best_dist = best_symbol, best_dist
        super().__init__(
            f"cell ({r},{c}) color rgb{self.rgb} matched nothing — closest "
            f"was {best_symbol!r} at distance {best_dist:.0f}")


class Palette:
    """Maps engine symbols to reference RGB swatches. Classification is
    nearest-swatch in RGB space, rejected past max_dist."""

    def __init__(self, swatches, max_dist=60.0):
        # swatches: {symbol: (r, g, b)}
        self.swatches = {sym: tuple(float(v) for v in rgb)
                         for sym, rgb in swatches.items()}
        self.max_dist = max_dist

    def nearest(self, rgb):
        """(symbol, distance) of the closest swatch to an RGB triple."""
        rgb = np.asarray(rgb, dtype=float)
        best_sym, best_dist = None, float("inf")
        for sym, swatch in self.swatches.items():
            dist = float(np.linalg.norm(rgb - np.asarray(swatch)))
            if dist < best_dist:
                best_sym, best_dist = sym, dist
        return best_sym, best_dist

    def classify(self, rgb, r=0, c=0):
        """Symbol for an RGB triple; raises UnknownCellError past max_dist."""
        sym, dist = self.nearest(rgb)
        if sym is None or dist > self.max_dist:
            raise UnknownCellError(r, c, rgb, sym, dist)
        return sym


# Distinct flat colors for synth.py's renderer, one per engine symbol.
SYNTH_SWATCHES = {
    "r": (220, 60, 60),
    "b": (60, 110, 220),
    "g": (70, 190, 90),
    "y": (240, 200, 60),
    "5": (160, 60, 200),   # light ball
    "V": (230, 140, 50),   # vertical rocket
    "H": (50, 200, 200),   # horizontal rocket
    "T": (140, 90, 40),    # TNT
    "S": (250, 120, 180),  # propeller
    "B": (120, 120, 120),  # box obstacle
    "#": (40, 40, 40),     # wall
    " ": (15, 15, 15),     # empty
}


def synth_palette():
    return Palette(dict(SYNTH_SWATCHES))
