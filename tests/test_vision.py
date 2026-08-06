from pathlib import Path

import numpy as np
import pytest

from engine.board import Board
from engine.levels import get_level
from vision import (AutoBoardReader, BoardReader, GridGeometry, PolicyAgent,
                    UnknownCellError, render_board, synth_palette)
from vision.executor import move_endpoints
from vision.synth import synth_geometry

REAL_SHOT = Path(__file__).resolve().parent.parent / \
    "vision" / "levels" / "level_001.png"


@pytest.fixture
def dealt_grid():
    # a real level-1 deal: candies, boxes, and walls all present
    tmpl = [row.copy() for row in get_level(1)]
    return Board(board_state=tmpl, seed=3, fill_empty=True).grid


@pytest.mark.vision
def test_geometry_cell_center():
    geo = GridGeometry(x0=100, y0=200, cell_w=50, cell_h=50, rows=9, cols=9)
    assert geo.cell_center(0, 0) == (125, 225)
    assert geo.cell_center(8, 8) == (525, 625)


@pytest.mark.vision
def test_palette_classifies_nearest_and_rejects_unknown():
    pal = synth_palette()
    assert pal.classify((225, 55, 65)) == "r"      # near the red swatch
    with pytest.raises(UnknownCellError) as e:
        pal.classify((255, 255, 255), r=2, c=5)    # matches nothing
    assert e.value.r == 2 and e.value.c == 5


@pytest.mark.vision
def test_render_then_read_roundtrips_exactly(dealt_grid):
    geo = synth_geometry(len(dealt_grid), len(dealt_grid[0]))
    img = render_board(dealt_grid, geo)
    assert BoardReader(geo, synth_palette()).read(img) == dealt_grid


@pytest.mark.vision
def test_reader_survives_sprite_noise(dealt_grid):
    # real sprites aren't flat color — jitter every pixel and re-read
    geo = synth_geometry(len(dealt_grid), len(dealt_grid[0]))
    arr = np.asarray(render_board(dealt_grid, geo)).astype(int)
    rng = np.random.default_rng(0)
    noisy = np.clip(arr + rng.integers(-25, 26, arr.shape), 0, 255)
    from PIL import Image
    img = Image.fromarray(noisy.astype(np.uint8))
    assert BoardReader(geo, synth_palette()).read(img) == dealt_grid


@pytest.mark.vision
def test_move_endpoints_map_to_cell_centers():
    geo = GridGeometry(x0=0, y0=0, cell_w=10, cell_h=10, rows=3, cols=3)
    assert move_endpoints(geo, 0, 0, "d") == ((5, 5), (15, 5))
    assert move_endpoints(geo, 0, 0, "s") == ((5, 5), (5, 15))
    start, end = move_endpoints(geo, 1, 1, "x")
    assert start == end == (15, 15)


@pytest.mark.vision
def test_real_screenshot_parses_to_level_one():
    # the actual Royal Kingdom level-1 screenshot: 9x9, top three rows are
    # cubes, the other six are the 54-box wall — exactly our level 1
    from PIL import Image
    reader = AutoBoardReader()
    grid = reader.read(Image.open(REAL_SHOT))
    assert len(grid) == 9 and all(len(row) == 9 for row in grid)
    assert sum(ch == "B" for row in grid for ch in row) == 54
    for row in grid[3:]:
        assert row == ["B"] * 9
    for row in grid[:3]:
        assert all(ch in ("r", "b", "g", "y") for ch in row)
    # geometry landed on the playfield, not the whole screen
    geo = reader.geometry
    assert geo.rows == geo.cols == 9
    with Image.open(REAL_SHOT) as im:
        w, h = im.size
    x, y = geo.cell_center(8, 8)
    assert 0 < x < w and 0 < y < h


@pytest.mark.vision
def test_template_layer_recognizes_harvested_powerup(tmp_path, monkeypatch):
    # the powerup path: a cell crop harvested from the device's own
    # screenshot becomes a template, and that exact sprite then classifies
    # as the powerup instead of falling into a candy hue bucket
    import cv2
    from vision import classify
    from vision.detect_grid import detect

    img = cv2.imread(str(REAL_SHOT))
    x1, y1, x2, y2, rows, cols = detect(img)
    cell_h, cell_w = (y2 - y1) // rows, (x2 - x1) // cols
    crop = img[y1:y1 + cell_h, x1:x1 + cell_w]      # cell (0,0): a clover
    cv2.imwrite(str(tmp_path / "V.png"), crop)

    monkeypatch.setattr(classify, "_TEMPLATE_DIR", str(tmp_path))
    classify.reload_templates()
    try:
        grid = classify.classify_board(img, x1, y1, x2, y2, rows, cols)
        assert grid[0][0] == "V"    # the harvested sprite is recognized
        assert grid[0][2] == "r"    # unrelated sprites still hue-classify
        assert grid[3][0] == "B"
    finally:
        classify.reload_templates()  # don't leak the fake template cache


@pytest.mark.vision
def test_adb_devices_output_parsing():
    from vision.capture import _parse_adb_devices
    out = ("List of devices attached\n"
           "R58M12ABCDE\tdevice\n"
           "emulator-5554\tunauthorized\n")
    assert _parse_adb_devices(out) == {"R58M12ABCDE": "device",
                                       "emulator-5554": "unauthorized"}
    assert _parse_adb_devices("List of devices attached\n") == {}


@pytest.fixture
def checkpoint(tmp_path):
    from rl.policy import PolicyNet, save_checkpoint
    from rl.env import PLANES
    net = PolicyNet((len(PLANES), 9, 9), 9 * 9 * 3)
    path = str(tmp_path / "net.pt")
    save_checkpoint(net, path, level=1, update=0)
    return path


@pytest.mark.vision
def test_agent_picks_a_legal_move_on_the_real_screenshot(checkpoint):
    from PIL import Image
    grid = AutoBoardReader().read(Image.open(REAL_SHOT))
    move = PolicyAgent(checkpoint).pick(grid)
    assert move in Board(board_state=[row.copy() for row in grid]).valid_moves()


@pytest.mark.vision
def test_agent_rejects_wrong_board_shape(checkpoint):
    grid = [["r", "b"], ["g", "y"]]
    with pytest.raises(ValueError, match="2x2"):
        PolicyAgent(checkpoint).pick(grid)


@pytest.mark.vision
def test_full_episode_through_rendered_frames_only(checkpoint):
    # the pipeline self-test the --sim flag runs: every move is chosen from
    # a rendered image, never from engine state
    from rl.env import CandyCrushEnv
    env = CandyCrushEnv(level=1, max_moves=5, seed=0)
    _, info = env.reset()
    geo = synth_geometry(env.rows, env.cols)
    reader = BoardReader(geo, synth_palette())
    agent = PolicyAgent(checkpoint)
    steps = 0
    while True:
        grid = reader.read(render_board(env.game.board.grid, geo))
        assert grid == env.game.board.grid  # vision saw the truth
        move = agent.pick(grid)
        assert move is not None
        _, _, terminated, truncated, info = env.step(env.encode_action(*move))
        steps += 1
        if terminated or truncated:
            break
    assert steps > 0 and info["moves_left"] < 5
