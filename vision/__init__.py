"""Vision pipeline: turn a screenshot of a real match-3 board (Royal Kingdom)
into the engine's board alphabet, ask a trained policy for a move, and express
that move as a screen gesture.

The loop is capture -> read -> decide -> execute, each behind a small
interface so backends swap freely:

    capture:  FileCapture (manual screenshots) | AdbCapture (android device)
    read:     AutoBoardReader (real screenshots, detect_grid + classify)
              | BoardReader (synth-rendered frames for the sim/tests)
    decide:   PolicyAgent wrapping a train.py checkpoint
    execute:  SuggestExecutor (print for a human) | AdbExecutor (input swipe)

scripts/play_live.py wires the loop; scripts/slice_cells.py dumps per-cell
crops for debugging classification.
"""
from vision.geometry import GridGeometry
from vision.palette import Palette, UnknownCellError, synth_palette
from vision.reader import AutoBoardReader, BoardReader
from vision.agent import PolicyAgent
from vision.capture import FileCapture, AdbCapture
from vision.executor import SuggestExecutor, AdbExecutor
from vision.synth import render_board, synth_geometry

__all__ = [
    "GridGeometry", "Palette", "UnknownCellError", "synth_palette",
    "AutoBoardReader", "BoardReader", "PolicyAgent",
    "FileCapture", "AdbCapture", "SuggestExecutor", "AdbExecutor",
    "render_board", "synth_geometry",
]
