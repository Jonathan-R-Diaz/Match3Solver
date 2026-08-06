"""Turn an engine move (r, c, d) into something that happens on screen."""
import subprocess

# Human-facing names for the canonical move set.
DESCRIBE = {
    "s": "swap DOWN with the cell below",
    "d": "swap RIGHT with the cell beside",
    "x": "TAP to fire the powerup",
}


def move_endpoints(geometry, r, c, d):
    """Pixel start/end of the gesture. Taps return start == end."""
    x0, y0 = geometry.cell_center(r, c)
    if d == "s":
        x1, y1 = geometry.cell_center(r + 1, c)
    elif d == "d":
        x1, y1 = geometry.cell_center(r, c + 1)
    else:
        x1, y1 = x0, y0
    return (x0, y0), (x1, y1)


class SuggestExecutor:
    """Manual mode: print the move for a human to perform on the device."""

    def __init__(self, geometry):
        self.geometry = geometry

    def execute(self, r, c, d):
        (x0, y0), (x1, y1) = move_endpoints(self.geometry, r, c, d)
        at = f"({r},{c}) — screen ~({x0:.0f},{y0:.0f})"
        print(f">>> {DESCRIBE[d]} at {at}")


class AdbExecutor:
    """Android device over adb: `input swipe` for swaps, `input tap` for
    powerup fires."""

    def __init__(self, geometry, serial=None, swipe_ms=150):
        self.geometry = geometry
        self.base = ["adb"] + (["-s", serial] if serial else [])
        self.swipe_ms = swipe_ms

    def execute(self, r, c, d):
        (x0, y0), (x1, y1) = move_endpoints(self.geometry, r, c, d)
        if d == "x":
            cmd = ["shell", "input", "tap", f"{x0:.0f}", f"{y0:.0f}"]
        else:
            cmd = ["shell", "input", "swipe", f"{x0:.0f}", f"{y0:.0f}",
                   f"{x1:.0f}", f"{y1:.0f}", str(self.swipe_ms)]
        subprocess.run(self.base + cmd, check=True)
