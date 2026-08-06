"""Frame sources. All return PIL Images from grab()."""
import io
import subprocess
import time
from pathlib import Path

from PIL import Image


class FileCapture:
    """Manual loop: the user screenshots the device themselves.

    - Single file: grab() re-reads the same path each time (overwrite it).
    - Directory: grab() blocks until a *new* screenshot appears, then returns
      the newest one — drop files in and the loop advances by itself.
    """

    def __init__(self, path, poll=0.5):
        self.path = Path(path)
        self.poll = poll
        self._last_seen = None

    def _newest(self):
        files = [p for p in self.path.iterdir()
                 if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
        return max(files, key=lambda p: p.stat().st_mtime) if files else None

    def grab(self):
        if not self.path.is_dir():
            return Image.open(self.path).convert("RGB")
        while True:
            newest = self._newest()
            if newest is not None:
                stamp = (newest, newest.stat().st_mtime)
                if stamp != self._last_seen:
                    self._last_seen = stamp
                    time.sleep(0.2)  # let the file finish writing
                    return Image.open(newest).convert("RGB")
            time.sleep(self.poll)


class CaptureError(RuntimeError):
    """Grabbing a frame from the device failed (cable/adb trouble), as
    opposed to a frame that grabbed fine but couldn't be parsed."""


class AdbCapture:
    """Android device over adb: `adb exec-out screencap -p`. No extra Python
    deps and immune to Wayland capture restrictions."""

    def __init__(self, serial=None):
        self.base = ["adb"] + (["-s", serial] if serial else [])

    def grab(self):
        out = subprocess.run(self.base + ["exec-out", "screencap", "-p"],
                             capture_output=True)
        if out.returncode != 0:
            raise CaptureError(out.stderr.decode(errors="replace").strip()
                               or "adb screencap failed")
        try:
            return Image.open(io.BytesIO(out.stdout)).convert("RGB")
        except Exception as e:
            raise CaptureError(f"bad screencap data ({e}) — device "
                               "disconnected mid-capture?")


def _parse_adb_devices(text):
    """`adb devices` output -> {serial: state}."""
    devices = {}
    for line in text.strip().splitlines()[1:]:  # first line is the header
        parts = line.split()
        if len(parts) >= 2:
            devices[parts[0]] = parts[1]
    return devices


_STATE_HINTS = {
    "unauthorized": "accept the USB-debugging prompt on the phone",
    "offline": "replug the cable (or toggle USB debugging off and on)",
}


def wait_for_device(serial=None, poll=2.0):
    """Block until an adb device is ready. Prints what's wrong while waiting
    (nothing plugged in / unauthorized / offline). Returns the serial."""
    announced = None
    while True:
        out = subprocess.run(["adb", "devices"], capture_output=True,
                             text=True)
        devices = _parse_adb_devices(out.stdout)
        if serial is None and len(devices) > 1:
            listing = ", ".join(f"{s} ({st})" for s, st in devices.items())
            raise SystemExit(f"several adb devices: {listing} — pick one "
                             "with --serial")
        pick = serial if serial else next(iter(devices), None)
        state = devices.get(pick)
        if state == "device":
            return pick
        if state is None:
            msg = ("waiting for the phone... plug it in with USB debugging "
                   "enabled (adb devices shows nothing)")
        else:
            hint = _STATE_HINTS.get(state, "unexpected state")
            msg = f"phone is '{state}' — {hint}"
        if msg != announced:
            print(msg)
            announced = msg
        time.sleep(poll)
