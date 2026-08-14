"""Board item definitions.

Every board cell is a single character (`"r"`, `"T"`, `"B"`, `" "`, `"#"`, ...).
`Item` wraps each character in a `str` subclass carrying metadata (kind,
color, cracking chain, RL weight, ...), while remaining interchangeable with
the raw character for ==, in, hashing, and dict keys — so existing code and
tests that compare grid cells against string literals keep working unchanged.

Category containers (CANDIES, POWERUPS, ROCKETS, OBSTACLES, OBSTACLE_HP,
UNMATCHABLE) are derived from the registry rather than hand-listed, so adding
a new item is a single `_make()` call below — no other constant needs
updating to pick it up.
"""
from typing import Optional


class Item(str):
    """A board cell symbol with attached metadata. Instances are interned
    per-symbol (Item("r") is Item("r")) and behave exactly like the raw
    character they wrap for ==, in, hashing, dict keys, and f-strings."""

    _registry: dict = {}

    # class-level defaults so an unrecognized character (parse() falls
    # through to a bare Item) reports as an inert "unknown" item instead of
    # raising AttributeError from incidental access (e.g. repr, validate()).
    kind: str = "unknown"
    color: Optional[str] = None
    hp: int = 0
    cracks_into: Optional[str] = None
    hard_only: bool = False
    weight: float = 0.0
    is_rocket: bool = False
    combo_group: Optional[str] = None
    matchable: bool = False

    def __new__(cls, ch: str):
        existing = cls._registry.get(ch)
        if existing is not None:
            return existing
        return super().__new__(cls, ch)

    def __repr__(self):
        return f"Item({str.__repr__(self)}, kind={self.kind!r})"


def _make(ch, kind, *, color=None, hp=1, cracks_into=None, hard_only=False,
          weight=0.0, is_rocket=False, combo_group=None, matchable=False):
    item = Item(ch)
    item.kind = kind
    item.color = color
    item.hp = hp
    item.cracks_into = cracks_into
    item.hard_only = hard_only
    item.weight = weight
    item.is_rocket = is_rocket
    item.combo_group = combo_group
    item.matchable = matchable
    Item._registry[ch] = item
    return item


EMPTY = _make(" ", "empty")
WALL = _make("#", "wall", color="\x1b[90m")

RED = _make("r", "candy", color="\x1b[31m", matchable=True)
GREEN = _make("g", "candy", color="\x1b[32m", matchable=True)
YELLOW = _make("y", "candy", color="\x1b[33m", matchable=True)
BLUE = _make("b", "candy", color="\x1b[34m", matchable=True)

ELECTRO_BALL = _make("5", "powerup", color="\x1b[97m", weight=3.0, combo_group="eb")
ROCKET_V = _make("V", "powerup", color="\x1b[96m", weight=1.0, is_rocket=True, combo_group="rocket")
ROCKET_H = _make("H", "powerup", color="\x1b[96m", weight=1.0, is_rocket=True, combo_group="rocket")
TNT = _make("T", "powerup", color="\x1b[91m", weight=2.0, combo_group="tnt")
SPINNER = _make("S", "powerup", color="\x1b[95m", weight=2.0, combo_group="spinner")

BOX = _make("B", "obstacle", color="\x1b[37m", hp=1, cracks_into=None)
CRATE = _make("C", "obstacle", color="\x1b[33;2m", hp=2, cracks_into="B")


def _by_kind(kind):
    return frozenset(i for i in Item._registry.values() if i.kind == kind)


CANDIES = [RED, BLUE, GREEN, YELLOW]
POWERUPS = _by_kind("powerup")
ROCKETS = frozenset(i for i in POWERUPS if i.is_rocket)
OBSTACLES = _by_kind("obstacle")
OBSTACLE_HP = {i: i.hp for i in OBSTACLES}
UNMATCHABLE = frozenset({EMPTY, WALL}) | OBSTACLES | POWERUPS


def parse(ch: str) -> Item:
    """Look up the canonical Item for a raw character, used at every board
    construction boundary (Board.__init__, levels, vision output)."""
    return Item._registry.get(ch, Item(ch))
