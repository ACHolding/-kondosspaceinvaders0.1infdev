#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AC'S SPACE INVADERS PC PORT - YOUR TAKE 0.1
(C) 1999-2026 A.C Holdings / Team Flames

Single file. Python 3.10+. pygame-ce (or pygame) only.
FILES = OFF (no disk I/O, no assets). AUDIO FILES = OFF (procedural SFX only).
All sprites, fonts and sound effects are generated procedurally in code.

RUN:  python3 space4k.py
      (needs: pip install pygame-ce)
"""

import array
import math
import random
import sys

try:
    import pygame
except ImportError:  # pragma: no cover
    sys.stderr.write(
        "\n  AC'S SPACE INVADERS needs pygame-ce (or pygame).\n"
        "  Install it with:   python3 -m pip install pygame-ce\n"
        "  Then run:          python3 space4k.py\n\n"
    )
    raise SystemExit(2)

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

TITLE = "AC'S SPACE INVADERS PC PORT - YOUR TAKE 0.1"
COPYRIGHT = "(C) 1999-2026 A.C HOLDINGS"
COPYRIGHT_FULL = "(C) 1999-2026 A.C HOLDINGS / TEAM FLAMES"
VERSION = "0.1"

# FILES = OFF: never read/write assets, saves, or logs.
FILES_OFF = True
# AUDIO FILES = OFF: never load .wav/.ogg/.mp3; SFX are synthesised in RAM.
AUDIO_FILES_OFF = True

# Native arcade-style logical resolution (Taito cabinet was 224x256 rotated).
LW, LH = 224, 256

FPS = 60
DT = 1.0 / 60.0  # fixed timestep

SR = 22050  # audio sample rate

# Retro palette: green / white / black
BLACK = (0, 0, 0)
WHITE = (236, 236, 236)
GREEN = (32, 240, 80)
DGREEN = (16, 128, 44)
GREY = (128, 132, 128)

# States
S_MENU = "MENU"
S_PLAYING = "PLAYING"
S_HELP = "HELP"
S_ABOUT = "ABOUT"
S_CONTROLS = "CONTROLS"
S_SETTINGS = "SETTINGS"
S_EXIT = "EXIT"

# Playfield geometry (logical pixels)
HUD_H = 16
GROUND_Y = 232
PLAYER_Y = 216
BUNKER_Y = 194
INVASION_Y = 202
FIELD_LEFT = 8
FIELD_RIGHT = LW - 8

# Classic UFO score table, indexed by (player shots fired) % 15.
# The 23rd shot lands on index 8 -> 300 points, exactly like the arcade.
UFO_TABLE = (100, 50, 50, 100, 150, 100, 100, 50, 300, 100, 100, 100, 50, 150, 100)

ALIEN_POINTS = (30, 20, 20, 10, 10)  # per row, top row first
EXTRA_LIFE_AT = 1500


# ---------------------------------------------------------------------------
# 5x7 BITMAP FONT (procedural, no font files)
# ---------------------------------------------------------------------------

GLYPHS = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x19, 0x15, 0x13, 0x13, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "_": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x14, 0x00, 0x00, 0x00, 0x00),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "\\": (0x10, 0x08, 0x08, 0x04, 0x02, 0x02, 0x01),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "*": (0x00, 0x0A, 0x04, 0x1F, 0x04, 0x0A, 0x00),
    "%": (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    "#": (0x0A, 0x1F, 0x0A, 0x0A, 0x1F, 0x0A, 0x00),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x17, 0x10, 0x0E),
    "^": (0x04, 0x0A, 0x11, 0x00, 0x00, 0x00, 0x00),
}

GW, GH = 5, 7  # glyph cell
CW = GW + 1    # advance


def _rgb(color):
    """Normalise a colour to an opaque (R, G, B) tuple."""
    if len(color) >= 3:
        return (int(color[0]), int(color[1]), int(color[2]))
    return (255, 255, 255)


def _make_keyed(size, color_pixel_callback):
    """Opaque software surface with black colorkey (reliable on all backends)."""
    s = pygame.Surface(size)
    s.fill((0, 0, 0))
    color_pixel_callback(s)
    s.set_colorkey((0, 0, 0))
    try:
        return s.convert()
    except pygame.error:
        return s


class BitmapFont:
    """Procedural 5x7 pixel font with a surface cache."""

    def __init__(self):
        self._cache = {}

    def _glyph(self, ch, color):
        color = _rgb(color)
        key = (ch, color)
        s = self._cache.get(key)
        if s is None:
            rows = GLYPHS.get(ch, GLYPHS["?"])

            def paint(surf):
                for y, bits in enumerate(rows):
                    for x in range(GW):
                        if bits & (0x10 >> x):
                            surf.set_at((x, y), color)

            s = _make_keyed((GW, GH), paint)
            self._cache[key] = s
        return s

    @staticmethod
    def width(text, scale=1):
        return (len(text) * CW - 1) * scale if text else 0

    def draw(self, surf, text, x, y, color=WHITE, scale=1, center=False):
        text = "".join(ch if ch in GLYPHS or ch == " " else "?"
                       for ch in text.upper())
        if center:
            x = int(x - self.width(text, scale) / 2)
        cx = int(x)
        for ch in text:
            if ch != " ":
                g = self._glyph(ch, color)
                if scale != 1:
                    g = pygame.transform.scale(g, (GW * scale, GH * scale))
                surf.blit(g, (cx, int(y)))
            cx += CW * scale
        return cx


FONT = BitmapFont()


# ---------------------------------------------------------------------------
# PROCEDURAL SPRITES
# ---------------------------------------------------------------------------

def make_sprite(rows, color):
    """Build a Surface from a list of strings ('#' = pixel)."""
    color = _rgb(color)
    h = len(rows)
    w = max(len(r) for r in rows)

    def paint(surf):
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == "#":
                    surf.set_at((x, y), color)

    return _make_keyed((w, h), paint)


SQUID_A = [
    "...##...",
    "..####..",
    ".######.",
    "##.##.##",
    "########",
    "..#..#..",
    ".#.##.#.",
    "#.#..#.#",
]
SQUID_B = [
    "...##...",
    "..####..",
    ".######.",
    "##.##.##",
    "########",
    ".#.##.#.",
    "#......#",
    ".#....#.",
]
CRAB_A = [
    "..#.....#..",
    "...#...#...",
    "..#######..",
    ".##.###.##.",
    "###########",
    "#.#######.#",
    "#.#.....#.#",
    "...##.##...",
]
CRAB_B = [
    "..#.....#..",
    "#..#...#..#",
    "#.#######.#",
    "###.###.###",
    "###########",
    ".#########.",
    "..#.....#..",
    ".#.......#.",
]
OCTO_A = [
    "....####....",
    ".##########.",
    "############",
    "###..##..###",
    "############",
    "...##..##...",
    "..##.##.##..",
    "##........##",
]
OCTO_B = [
    "....####....",
    ".##########.",
    "############",
    "###..##..###",
    "############",
    "..###..###..",
    ".##..##..##.",
    "..##....##..",
]
CANNON = [
    "......#......",
    ".....###.....",
    ".....###.....",
    ".###########.",
    "#############",
    "#############",
    "#############",
    "#############",
]
UFO_SPR = [
    ".....######.....",
    "...##########...",
    "..############..",
    ".##.##.##.##.##.",
    "################",
    "..###..##..###..",
    "...#........#...",
]
ALIEN_BOOM = [
    "...#.....#...",
    "#...#...#...#",
    ".#..#####..#.",
    "..###.#.###..",
    ".###########.",
    "##.#######.##",
    "#.#.......#.#",
    "...##...##...",
]
PLAYER_BOOM_A = [
    "..#...#...#..",
    "#..#.#.#.#..#",
    ".#.#######.#.",
    "#.#########.#",
    "..#########..",
    ".###.###.###.",
    "##.#.###.#.##",
    "#.#..#.#..#.#",
]
PLAYER_BOOM_B = [
    "#..#..#..#..#",
    "..#.#.#.#.#..",
    "#.#.#####.#.#",
    ".#########.#.",
    "#.#######..#.",
    ".##.#.#.###..",
    "#.#..###..#.#",
    "..#.#...#.#..",
]
# Alien projectile animations (3x7)
BOMB_SQUIGGLY = (
    [".#.", "..#", ".#.", "#..", ".#.", "..#", ".#."],
    [".#.", "#..", ".#.", "..#", ".#.", "#..", ".#."],
)
BOMB_PLUNGER = (
    ["###", ".#.", ".#.", ".#.", "###", ".#.", ".#."],
    [".#.", ".#.", "###", ".#.", ".#.", ".#.", "###"],
)
BOMB_ROLLING = (
    [".#.", ".#.", "#.#", ".#.", ".#.", "#.#", ".#."],
    ["#.#", ".#.", ".#.", "#.#", ".#.", ".#.", "#.#"],
)


class SpriteBank:
    """All sprite surfaces, generated once at boot."""

    def __init__(self):
        self.alien = [
            (make_sprite(SQUID_A, WHITE), make_sprite(SQUID_B, WHITE)),
            (make_sprite(CRAB_A, WHITE), make_sprite(CRAB_B, WHITE)),
            (make_sprite(CRAB_A, WHITE), make_sprite(CRAB_B, WHITE)),
            (make_sprite(OCTO_A, WHITE), make_sprite(OCTO_B, WHITE)),
            (make_sprite(OCTO_A, WHITE), make_sprite(OCTO_B, WHITE)),
        ]
        self.cannon = make_sprite(CANNON, GREEN)
        self.ufo = make_sprite(UFO_SPR, GREEN)
        self.alien_boom = make_sprite(ALIEN_BOOM, WHITE)
        self.player_boom = (
            make_sprite(PLAYER_BOOM_A, GREEN),
            make_sprite(PLAYER_BOOM_B, GREEN),
        )
        self.bombs = [
            tuple(make_sprite(f, WHITE) for f in BOMB_SQUIGGLY),
            tuple(make_sprite(f, WHITE) for f in BOMB_PLUNGER),
            tuple(make_sprite(f, WHITE) for f in BOMB_ROLLING),
        ]
        # menu icons scaled x2
        self.icon = [pygame.transform.scale2x(self.alien[i][0]) for i in (0, 1, 3)]
        self.icon_ufo = pygame.transform.scale2x(self.ufo)


# ---------------------------------------------------------------------------
# ATARI SOUND ENGINE - procedural square waves / noise, no audio files
# ---------------------------------------------------------------------------

class AtariSoundEngine:
    """Generates every SFX in code and feeds pygame.mixer.Sound(buffer=...).

    AUDIO_FILES_OFF means this engine never opens a path on disk -- every
    sample is a procedural square wave / noise burst built into a PCM buffer.
    """

    def __init__(self):
        self.ok = False
        self.enabled = True
        self.volume = 0.7
        self.channels = 1
        self.from_file = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SR, size=-16, channels=1, buffer=512)
            init = pygame.mixer.get_init()
            if not init:
                raise RuntimeError("mixer not initialised")
            self.channels = init[2]
            pygame.mixer.set_num_channels(16)
            self.ok = True
        except Exception:
            self.ok = False
            return

        self.ch_shoot = pygame.mixer.Channel(0)
        self.ch_march = pygame.mixer.Channel(1)
        self.ch_ufo = pygame.mixer.Channel(2)
        self.ch_boom = pygame.mixer.Channel(3)
        self.ch_extra = pygame.mixer.Channel(4)

        self.snd = {}
        self._build()
        self._ufo_playing = False
        self.march_step = 0
        # Policy guard: we only ever construct Sounds from raw PCM buffers.
        self.from_file = False
        if not AUDIO_FILES_OFF:
            # Reserved -- default stays procedural.
            pass

    # -- waveform primitives -------------------------------------------------

    @staticmethod
    def _buf(n):
        return array.array("h", bytes(2 * n))

    def _square(self, dur, f0, f1=None, vol=0.5, duty=0.5, env="flat", steps=0):
        """Square wave with optional linear/stepped frequency sweep."""
        n = max(1, int(SR * dur))
        buf = self._buf(n)
        phase = 0.0
        f1 = f0 if f1 is None else f1
        for i in range(n):
            u = i / n
            if steps:
                q = math.floor(u * steps) / max(1, steps - 1)
                f = f0 + (f1 - f0) * min(1.0, q)
            else:
                f = f0 + (f1 - f0) * u
            phase += f / SR
            s = 1.0 if (phase % 1.0) < duty else -1.0
            a = self._env(env, u)
            buf[i] = int(max(-1.0, min(1.0, s * vol * a)) * 32000)
        return buf

    def _noise(self, dur, vol=0.5, hold=2, env="decay", lp=0.0, hold_end=None):
        """Sample-and-hold noise; `hold` sets the grain (pitch) of the burst."""
        n = max(1, int(SR * dur))
        buf = self._buf(n)
        val = 0.0
        prev = 0.0
        cnt = 0
        h0 = max(1, hold)
        h1 = h0 if hold_end is None else max(1, hold_end)
        for i in range(n):
            u = i / n
            h = int(h0 + (h1 - h0) * u)
            if cnt <= 0:
                val = random.uniform(-1.0, 1.0)
                cnt = max(1, h)
            cnt -= 1
            s = val
            if lp > 0.0:
                prev = prev + (s - prev) * (1.0 - lp)
                s = prev
            a = self._env(env, u)
            buf[i] = int(max(-1.0, min(1.0, s * vol * a)) * 32000)
        return buf

    @staticmethod
    def _env(kind, u):
        if kind == "flat":
            return 1.0
        if kind == "decay":
            return (1.0 - u) ** 1.6
        if kind == "hdecay":
            return (1.0 - u) ** 3.0
        if kind == "pluck":
            return 1.0 if u < 0.06 else (1.0 - (u - 0.06) / 0.94) ** 1.2
        if kind == "swell":
            return math.sin(math.pi * u)
        return 1.0

    @staticmethod
    def _mix(a, b, ga=1.0, gb=1.0):
        n = max(len(a), len(b))
        out = array.array("h", bytes(2 * n))
        for i in range(n):
            v = 0.0
            if i < len(a):
                v += a[i] * ga
            if i < len(b):
                v += b[i] * gb
            out[i] = int(max(-32000, min(32000, v)))
        return out

    @staticmethod
    def _cat(*bufs):
        out = array.array("h")
        for b in bufs:
            out.extend(b)
        return out

    def _sound(self, buf):
        # Always pass raw PCM bytes -- never a filename (AUDIO_FILES_OFF).
        if self.channels == 2:
            st = array.array("h", bytes(4 * len(buf)))
            for i, v in enumerate(buf):
                st[2 * i] = v
                st[2 * i + 1] = v
            buf = st
        return pygame.mixer.Sound(buffer=buf.tobytes())

    # -- SFX bank ------------------------------------------------------------

    def _build(self):
        s = self.snd
        # Player cannon shot: short descending square-wave pulse
        s["shoot"] = self._sound(
            self._square(0.22, 1400, 260, vol=0.42, duty=0.5, env="pluck", steps=18)
        )
        # Alien march: 4 descending bass square tones (the classic heartbeat)
        for i, f in enumerate((116, 104, 92, 82)):
            s["march%d" % i] = self._sound(
                self._square(0.11, f, f * 0.92, vol=0.55, duty=0.5, env="decay")
            )
        # Alien explosion: bright noise burst + tiny square spike
        s["alien_boom"] = self._sound(
            self._mix(
                self._noise(0.32, vol=0.55, hold=2, hold_end=9, env="decay"),
                self._square(0.10, 620, 180, vol=0.25, env="hdecay"),
                1.0, 1.0,
            )
        )
        # Player explosion: longer, lower-frequency noise burst
        s["player_boom"] = self._sound(
            self._mix(
                self._noise(0.95, vol=0.62, hold=7, hold_end=26, env="decay", lp=0.55),
                self._square(0.55, 150, 42, vol=0.30, duty=0.35, env="decay"),
                1.0, 1.0,
            )
        )
        # UFO hum: continuous rising/falling frequency, looped
        s["ufo"] = self._sound(self._ufo_loop())
        # UFO explosion: sharp noise crack + square-wave spike
        s["ufo_boom"] = self._sound(
            self._mix(
                self._noise(0.55, vol=0.6, hold=1, hold_end=14, env="decay"),
                self._cat(
                    self._square(0.09, 900, 1500, vol=0.35, duty=0.25, env="flat"),
                    self._square(0.30, 1500, 120, vol=0.35, duty=0.25, env="decay"),
                ),
                1.0, 1.0,
            )
        )
        # Extras
        s["extra_life"] = self._sound(
            self._cat(
                self._square(0.09, 523, 523, vol=0.35, env="flat"),
                self._square(0.09, 659, 659, vol=0.35, env="flat"),
                self._square(0.09, 784, 784, vol=0.35, env="flat"),
                self._square(0.18, 1046, 1046, vol=0.35, env="decay"),
            )
        )
        s["menu_move"] = self._sound(
            self._square(0.05, 880, 880, vol=0.28, duty=0.25, env="decay")
        )
        s["menu_ok"] = self._sound(
            self._cat(
                self._square(0.06, 660, 660, vol=0.32, duty=0.5, env="flat"),
                self._square(0.10, 1320, 1320, vol=0.32, duty=0.5, env="decay"),
            )
        )
        s["wave"] = self._sound(
            self._square(0.45, 180, 900, vol=0.30, duty=0.5, env="swell", steps=12)
        )
        s["gameover"] = self._sound(
            self._cat(
                self._square(0.20, 300, 260, vol=0.35, env="flat"),
                self._square(0.20, 240, 200, vol=0.35, env="flat"),
                self._square(0.55, 180, 60, vol=0.38, env="decay"),
            )
        )

    def _ufo_loop(self):
        dur = 0.60
        n = int(SR * dur)
        buf = self._buf(n)
        phase = 0.0
        for i in range(n):
            t = i / SR
            f = 430.0 + 190.0 * math.sin(2.0 * math.pi * t / dur)
            phase += f / SR
            v = 1.0 if (phase % 1.0) < 0.5 else -1.0
            buf[i] = int(v * 0.26 * 32000)
        return buf

    # -- playback ------------------------------------------------------------

    def _play(self, ch, name, loops=0):
        if not self.ok or not self.enabled:
            return
        snd = self.snd.get(name)
        if snd is None:
            return
        snd.set_volume(self.volume)
        try:
            ch.play(snd, loops=loops)
        except pygame.error:
            pass

    def shoot(self):
        self._play(self.ch_shoot, "shoot")

    def march(self):
        self._play(self.ch_march, "march%d" % self.march_step)
        self.march_step = (self.march_step + 1) % 4

    def reset_march(self):
        self.march_step = 0

    def alien_boom(self):
        self._play(self.ch_boom, "alien_boom")

    def player_boom(self):
        self._play(self.ch_boom, "player_boom")

    def ufo_boom(self):
        self.ufo_stop()
        self._play(self.ch_boom, "ufo_boom")

    def ufo_start(self):
        if not self.ok or not self.enabled or self._ufo_playing:
            return
        self._play(self.ch_ufo, "ufo", loops=-1)
        self._ufo_playing = True

    def ufo_stop(self):
        if self.ok and self._ufo_playing:
            self.ch_ufo.stop()
        self._ufo_playing = False

    def extra_life(self):
        self._play(self.ch_extra, "extra_life")

    def wave_clear(self):
        self._play(self.ch_extra, "wave")

    def game_over(self):
        self.ufo_stop()
        self._play(self.ch_extra, "gameover")

    def ui_move(self):
        self._play(self.ch_extra, "menu_move")

    def ui_ok(self):
        self._play(self.ch_extra, "menu_ok")

    def stop_all(self):
        if self.ok:
            pygame.mixer.stop()
        self._ufo_playing = False

    def set_enabled(self, on):
        self.enabled = bool(on)
        if not self.enabled:
            self.stop_all()

    def set_volume(self, v):
        self.volume = max(0.0, min(1.0, v))
        if self.ok and self._ufo_playing:
            self.snd["ufo"].set_volume(self.volume)


# ---------------------------------------------------------------------------
# ENTITIES
# ---------------------------------------------------------------------------

class Bullet:
    """Player shot or alien bomb."""

    def __init__(self, x, y, vy, frames=None, w=1, h=4, color=WHITE):
        self.x = float(x)
        self.y = float(y)
        self.vy = float(vy)
        self.frames = frames
        self.w = frames[0].get_width() if frames else w
        self.h = frames[0].get_height() if frames else h
        self.color = color
        self.alive = True
        self.anim = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt):
        self.y += self.vy * dt
        self.anim += dt
        if self.y + self.h < HUD_H or self.y > GROUND_Y:
            self.alive = False

    def draw(self, surf):
        if self.frames:
            f = self.frames[int(self.anim * 12) % len(self.frames)]
            surf.blit(f, (int(self.x), int(self.y)))
        else:
            pygame.draw.rect(surf, self.color, self.rect)


class Player:
    """The laser cannon at the bottom of the field."""

    SPEED = 60.0  # logical px/sec (1 px per frame, arcade accurate)

    def __init__(self, sprites, snd):
        self.spr = sprites
        self.snd = snd
        self.w = sprites.cannon.get_width()
        self.h = sprites.cannon.get_height()
        self.x = float(FIELD_LEFT + 8)
        self.y = float(PLAYER_Y)
        self.bullet = None
        self.shots_fired = 0
        self.dying = 0.0
        self.boom_frame = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def reset_position(self):
        self.x = float(FIELD_LEFT + 8)
        self.bullet = None
        self.dying = 0.0

    def update(self, dt, keys, freeze):
        if self.dying > 0.0:
            self.dying = max(0.0, self.dying - dt)
            self.boom_frame = int(self.dying * 12) % 2
            return
        if freeze:
            return
        vx = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx += 1.0
        self.x += vx * self.SPEED * dt
        self.x = max(FIELD_LEFT, min(FIELD_RIGHT - self.w, self.x))

    def fire(self):
        # Classic rule: exactly one player shot in flight at any time.
        if self.dying > 0.0 or self.bullet is not None:
            return None
        self.shots_fired += 1
        self.bullet = Bullet(self.x + self.w // 2, self.y - 4, -240.0, w=1, h=4)
        self.snd.shoot()
        return self.bullet

    def kill(self):
        self.dying = 1.6
        self.bullet = None
        self.snd.player_boom()

    def draw(self, surf):
        if self.dying > 0.0:
            surf.blit(self.spr.player_boom[self.boom_frame], (int(self.x), int(self.y)))
        else:
            surf.blit(self.spr.cannon, (int(self.x), int(self.y)))


class Alien:
    """One invader in the formation grid."""

    __slots__ = ("row", "col", "kind", "alive", "ox", "w", "h", "boom")

    def __init__(self, row, col, cell_w):
        self.row = row
        self.col = col
        self.kind = row
        self.alive = True
        self.boom = 0.0
        self.w = 0
        self.h = 8
        self.ox = 0
        self.cell(cell_w)

    def cell(self, cell_w):
        widths = (8, 11, 11, 12, 12)
        self.w = widths[self.kind]
        self.ox = col_off = (cell_w - self.w) // 2
        return col_off

    def rect(self, gx, gy, cw, ch):
        return pygame.Rect(
            int(gx + self.col * cw + self.ox),
            int(gy + self.row * ch),
            self.w,
            self.h,
        )


class AlienGrid:
    """11x5 formation with classic stepped movement and accelerating pace."""

    COLS = 11
    ROWS = 5
    CELL_W = 16
    CELL_H = 16
    STEP_X = 2.0
    DROP_Y = 8.0

    def __init__(self, wave, sprites, snd, speed_mult):
        self.spr = sprites
        self.snd = snd
        self.wave = wave
        self.speed_mult = speed_mult
        self.aliens = [
            [Alien(r, c, self.CELL_W) for c in range(self.COLS)] for r in range(self.ROWS)
        ]
        self.x = float(FIELD_LEFT + 16)
        self.y = float(40 + min(wave - 1, 7) * 8)
        self.dir = 1.0
        self.frame = 0
        self.step_timer = 0.0
        self.pending_drop = False
        self.alive_count = self.COLS * self.ROWS
        self.landed = False
        self.booms = []  # [x, y, timer]

    # -- helpers -------------------------------------------------------------

    def iter_alive(self):
        for row in self.aliens:
            for a in row:
                if a.alive:
                    yield a

    def step_interval(self):
        # Arcade behaviour: the whole formation advances once every
        # `alive_count` frames, so it accelerates as invaders die.
        base = self.alive_count / 60.0
        return max(0.012, base / self.speed_mult)

    def bounds(self):
        left = 9999.0
        right = -9999.0
        any_alive = False
        for a in self.iter_alive():
            any_alive = True
            lx = self.x + a.col * self.CELL_W + a.ox
            if lx < left:
                left = lx
            if lx + a.w > right:
                right = lx + a.w
        if not any_alive:
            return self.x, self.x
        return left, right

    def bottom(self):
        b = 0.0
        for a in self.iter_alive():
            v = self.y + a.row * self.CELL_H + a.h
            if v > b:
                b = v
        return b

    def bottom_aliens(self):
        """Lowest living alien of each occupied column (they do the shooting)."""
        out = []
        for c in range(self.COLS):
            for r in range(self.ROWS - 1, -1, -1):
                a = self.aliens[r][c]
                if a.alive:
                    out.append(a)
                    break
        return out

    # -- update --------------------------------------------------------------

    def update(self, dt):
        for b in self.booms:
            b[2] -= dt
        self.booms = [b for b in self.booms if b[2] > 0.0]

        if self.alive_count <= 0:
            return

        self.step_timer += dt
        interval = self.step_interval()
        while self.step_timer >= interval:
            self.step_timer -= interval
            self._step()
            interval = self.step_interval()

    def _step(self):
        if self.alive_count <= 0:
            return
        if self.pending_drop:
            self.y += self.DROP_Y
            self.dir = -self.dir
            self.pending_drop = False
        else:
            self.x += self.STEP_X * self.dir
            left, right = self.bounds()
            if right >= FIELD_RIGHT or left <= FIELD_LEFT:
                self.pending_drop = True
        self.frame ^= 1
        self.snd.march()
        if self.bottom() >= INVASION_Y:
            self.landed = True

    def kill(self, alien):
        alien.alive = False
        self.alive_count -= 1
        r = alien.rect(self.x, self.y, self.CELL_W, self.CELL_H)
        self.booms.append([r.centerx, r.centery, 0.28])
        self.snd.alien_boom()
        return ALIEN_POINTS[alien.kind]

    def hit_test(self, rect):
        for a in self.iter_alive():
            if a.rect(self.x, self.y, self.CELL_W, self.CELL_H).colliderect(rect):
                return a
        return None

    def draw(self, surf):
        f = self.frame
        for a in self.iter_alive():
            spr = self.spr.alien[a.kind][f]
            surf.blit(
                spr,
                (
                    int(self.x + a.col * self.CELL_W + a.ox),
                    int(self.y + a.row * self.CELL_H),
                ),
            )
        boom = self.spr.alien_boom
        bw, bh = boom.get_width() // 2, boom.get_height() // 2
        for bx, by, _t in self.booms:
            surf.blit(boom, (int(bx - bw), int(by - bh)))


class UFO:
    """Mystery ship that drifts across the top of the field."""

    SPEED = 32.0

    def __init__(self, sprites, snd):
        self.spr = sprites
        self.snd = snd
        self.active = False
        self.x = 0.0
        self.y = 26.0
        self.dir = 1.0
        self.timer = random.uniform(18.0, 26.0)
        self.w = sprites.ufo.get_width()
        self.h = sprites.ufo.get_height()
        self.score_pop = None  # [value, x, timer]

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def reset(self):
        if self.active:
            self.snd.ufo_stop()
        self.active = False
        self.timer = random.uniform(18.0, 26.0)
        self.score_pop = None

    def update(self, dt, aliens_left, allow):
        if self.score_pop:
            self.score_pop[2] -= dt
            if self.score_pop[2] <= 0.0:
                self.score_pop = None

        if not self.active:
            if not allow:
                return
            self.timer -= dt
            if self.timer <= 0.0 and aliens_left > 7:
                self.launch()
            return

        self.x += self.SPEED * self.dir * dt
        if self.dir > 0 and self.x > FIELD_RIGHT:
            self.despawn()
        elif self.dir < 0 and self.x + self.w < FIELD_LEFT:
            self.despawn()

    def launch(self):
        self.active = True
        self.dir = random.choice((1.0, -1.0))
        self.x = float(FIELD_LEFT - self.w) if self.dir > 0 else float(FIELD_RIGHT)
        self.snd.ufo_start()

    def despawn(self):
        self.active = False
        self.snd.ufo_stop()
        self.timer = random.uniform(18.0, 28.0)

    def hit(self, shots_fired):
        value = UFO_TABLE[shots_fired % 15]
        self.active = False
        self.snd.ufo_boom()
        self.timer = random.uniform(18.0, 28.0)
        self.score_pop = [value, self.x + self.w / 2, 1.2]
        return value

    def draw(self, surf):
        if self.active:
            surf.blit(self.spr.ufo, (int(self.x), int(self.y)))
        if self.score_pop:
            FONT.draw(
                surf, str(self.score_pop[0]), self.score_pop[1], self.y, GREEN, 1, True
            )


class Bunker:
    """Destructible shield, pixel grid generated procedurally."""

    W, H = 22, 16

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.grid = [[0] * self.W for _ in range(self.H)]
        self.surf = pygame.Surface((self.W, self.H))
        self.surf.set_colorkey((0, 0, 0))
        self.build()

    def build(self):
        for y in range(self.H):
            for x in range(self.W):
                on = 1
                if y < 4 and (x < 4 - y or x > 17 + y):
                    on = 0
                if y >= 11:
                    half = 3.0 + (y - 11) * 0.9
                    if abs(x - 10.5) < half:
                        on = 0
                self.grid[y][x] = on
        self.redraw()

    def redraw(self):
        self.surf.fill((0, 0, 0))
        for y in range(self.H):
            row = self.grid[y]
            for x in range(self.W):
                if row[x]:
                    self.surf.set_at((x, y), GREEN)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    def collide(self, rect):
        if not self.rect.colliderect(rect):
            return False
        lx0 = max(0, rect.left - self.x)
        lx1 = min(self.W, rect.right - self.x)
        ly0 = max(0, rect.top - self.y)
        ly1 = min(self.H, rect.bottom - self.y)
        for y in range(ly0, ly1):
            row = self.grid[y]
            for x in range(lx0, lx1):
                if row[x]:
                    return (x, y)
        return False

    def blast(self, cx, cy, radius=3, up=True):
        r2 = radius * radius
        for y in range(max(0, cy - radius), min(self.H, cy + radius + 1)):
            dy = y - cy
            if up and dy > 1:
                continue
            if not up and dy < -1:
                continue
            for x in range(max(0, cx - radius), min(self.W, cx + radius + 1)):
                dx = x - cx
                if dx * dx + dy * dy <= r2 + random.randint(0, 2):
                    self.grid[y][x] = 0
        self.redraw()

    def erase_band(self, top):
        """Aliens marching over a shield scrub it away."""
        changed = False
        ly = top - self.y
        for y in range(max(0, ly), min(self.H, ly + self.H)):
            row = self.grid[y]
            for x in range(self.W):
                if row[x]:
                    row[x] = 0
                    changed = True
        if changed:
            self.redraw()

    def draw(self, surf):
        surf.blit(self.surf, (self.x, self.y))


# ---------------------------------------------------------------------------
# MENU SYSTEM
# ---------------------------------------------------------------------------

class MenuSystem:
    """Menu, Help, About, Controls and Settings screens + navigation."""

    MAIN_ITEMS = (
        ("PLAY GAME", "play"),
        ("CONTROLS", S_CONTROLS),
        ("SETTINGS", S_SETTINGS),
        ("HELP", S_HELP),
        ("ABOUT", S_ABOUT),
        ("EXIT", S_EXIT),
    )

    HELP_TEXT = (
        "OBJECTIVE",
        "",
        "  DESTROY ALL 55 INVADERS",
        "  BEFORE THEY REACH YOU.",
        "  EACH WAVE STARTS LOWER.",
        "",
        "RULES OF ENGAGEMENT",
        "",
        "  ONLY ONE SHOT IN FLIGHT.",
        "  SWARM SPEEDS UP AS IT THINS.",
        "  THE LAST INVADER IS FAST.",
        "  SHIELDS ERODE BOTH WAYS.",
        "",
        "SCORING",
        "",
        "  TOP SQUID . . . . 30 PTS",
        "  MIDDLE CRABS . . 20 PTS",
        "  BOTTOM OCTOPI . . 10 PTS",
        "  MYSTERY UFO  50-300 PTS",
        "  EXTRA CANNON AT 1500",
        "",
        "  UFO USES THE ARCADE TABLE.",
        "  YOUR 23RD SHOT = 300 PTS.",
    )

    ABOUT_TEXT = (
        "AC'S SPACE INVADERS PC PORT",
        "YOUR TAKE 0.1",
        "",
        "  A SINGLE-FILE TRIBUTE TO THE",
        "  1978 ARCADE CLASSIC.",
        "",
        "  ENGINE . . PYGAME, 60 FPS",
        "  RESOLUTION  224 X 256",
        "  ASSETS . . NONE (PROCEDURAL)",
        "  FILES . . . OFF",
        "  AUDIO FILES  OFF (DSP BEEPS)",
        "",
        "  EVERY SPRITE, GLYPH AND SFX",
        "  IS BUILT FROM ARRAYS AT BOOT.",
        "  NOTHING IS LOADED OR WRITTEN.",
        "",
        COPYRIGHT,
        "TEAM FLAMES",
    )

    CONTROLS_TEXT = (
        "IN GAME",
        "",
        "  LEFT / A . . . . MOVE LEFT",
        "  RIGHT / D . . . MOVE RIGHT",
        "  SPACE . . . . . . FIRE",
        "  P . . . . . . . . PAUSE",
        "  ESC . . . . . . . TO MENU",
        "",
        "MENUS",
        "",
        "  UP / DOWN . . . SELECT",
        "  LEFT / RIGHT . CHANGE",
        "  ENTER . . . . . CONFIRM",
        "  ESC . . . . . . BACK",
        "",
        "GLOBAL",
        "",
        "  F11 . . . . FULLSCREEN",
        "  M . . . . . MUTE / UNMUTE",
    )

    def __init__(self, game):
        self.game = game
        self.index = 0
        self.set_index = 0
        self.blink = 0.0
        self.demo_t = 0.0

    # -- input ---------------------------------------------------------------

    def key(self, state, key):
        g = self.game
        if state == S_MENU:
            return self._key_main(key)
        if state == S_SETTINGS:
            return self._key_settings(key)
        if key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER,
                   pygame.K_SPACE, pygame.K_BACKSPACE):
            g.snd.ui_ok()
            return S_MENU
        return state

    def _key_main(self, key):
        g = self.game
        n = len(self.MAIN_ITEMS)
        if key in (pygame.K_UP, pygame.K_w):
            self.index = (self.index - 1) % n
            g.snd.ui_move()
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.index = (self.index + 1) % n
            g.snd.ui_move()
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            g.snd.ui_ok()
            target = self.MAIN_ITEMS[self.index][1]
            if target == "play":
                g.start_game()
                return S_PLAYING
            if target == S_SETTINGS:
                self.set_index = 0
            return target
        elif key == pygame.K_ESCAPE:
            return S_EXIT
        return S_MENU

    def _key_settings(self, key):
        g = self.game
        items = g.settings_items()
        n = len(items)
        if key in (pygame.K_UP, pygame.K_w):
            self.set_index = (self.set_index - 1) % n
            g.snd.ui_move()
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.set_index = (self.set_index + 1) % n
            g.snd.ui_move()
        elif key in (pygame.K_LEFT, pygame.K_a):
            g.settings_adjust(items[self.set_index][0], -1)
            g.snd.ui_move()
        elif key in (pygame.K_RIGHT, pygame.K_d):
            g.settings_adjust(items[self.set_index][0], +1)
            g.snd.ui_move()
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            key_name = items[self.set_index][0]
            if key_name == "back":
                g.snd.ui_ok()
                return S_MENU
            g.settings_adjust(key_name, +1)
            g.snd.ui_ok()
        elif key == pygame.K_ESCAPE:
            g.snd.ui_ok()
            return S_MENU
        return S_SETTINGS

    # -- drawing -------------------------------------------------------------

    def update(self, dt):
        self.blink += dt
        self.demo_t += dt

    def draw(self, surf, state):
        if state == S_MENU:
            self._draw_main(surf)
        elif state == S_HELP:
            self._draw_page(surf, "HELP", self.HELP_TEXT)
        elif state == S_ABOUT:
            self._draw_page(surf, "ABOUT", self.ABOUT_TEXT)
        elif state == S_CONTROLS:
            self._draw_page(surf, "CONTROLS", self.CONTROLS_TEXT)
        elif state == S_SETTINGS:
            self._draw_settings(surf)

    def _header(self, surf, text):
        FONT.draw(surf, text, LW // 2, 8, GREEN, 2, True)
        pygame.draw.line(surf, DGREEN, (8, 26), (LW - 8, 26))

    def _footer(self, surf, text="ESC - BACK"):
        pygame.draw.line(surf, DGREEN, (8, GROUND_Y), (LW - 8, GROUND_Y))
        FONT.draw(surf, text, LW // 2, GROUND_Y + 8, GREY, 1, True)

    def _draw_main(self, surf):
        FONT.draw(surf, "AC'S", LW // 2, 14, GREEN, 2, True)
        FONT.draw(surf, "SPACE INVADERS", LW // 2, 30, WHITE, 2, True)
        FONT.draw(surf, "PC PORT - YOUR TAKE 0.1", LW // 2, 48, GREEN, 1, True)

        # marching demo invader row
        sp = self.game.spr
        wob = int(math.sin(self.demo_t * 2.0) * 10)
        frame = int(self.demo_t * 2.0) % 2
        for i in range(6):
            spr = sp.alien[(0, 1, 3)[i % 3]][frame]
            surf.blit(spr, (36 + i * 26 + wob, 62))

        y = 88
        for i, (label, _t) in enumerate(self.MAIN_ITEMS):
            sel = i == self.index
            col = WHITE if sel else GREY
            if sel and (self.blink % 0.6) < 0.4:
                FONT.draw(surf, ">", LW // 2 - FONT.width(label) // 2 - 12, y, GREEN)
            FONT.draw(surf, label, LW // 2, y, col, 1, True)
            y += 14

        # score advance table
        FONT.draw(surf, "* SCORE ADVANCE TABLE *", LW // 2, 178, GREEN, 1, True)
        rows = (
            (self.game.spr.ufo, "= ? MYSTERY"),
            (self.game.spr.alien[0][0], "= 30 POINTS"),
            (self.game.spr.alien[1][0], "= 20 POINTS"),
            (self.game.spr.alien[3][0], "= 10 POINTS"),
        )
        yy = 190
        for spr, text in rows:
            surf.blit(spr, (56, yy))
            FONT.draw(surf, text, 82, yy + 1, WHITE)
            yy += 11

        hi = self.game.high_score
        FONT.draw(surf, "HI-SCORE %04d" % hi, LW // 2, GROUND_Y + 6, GREEN, 1, True)
        FONT.draw(surf, COPYRIGHT, LW // 2, GROUND_Y + 16, GREY, 1, True)

    def _draw_page(self, surf, title, lines):
        self._header(surf, title)
        y = 34
        for ln in lines:
            col = GREEN if ln and not ln.startswith(" ") else WHITE
            FONT.draw(surf, ln, 12, y, col)
            y += 8
        self._footer(surf)

    def _draw_settings(self, surf):
        g = self.game
        self._header(surf, "SETTINGS")
        items = g.settings_items()
        y = 44
        for i, (key_name, label, value) in enumerate(items):
            sel = i == self.set_index
            col = WHITE if sel else GREY
            if sel and (self.blink % 0.6) < 0.4:
                FONT.draw(surf, ">", 12, y, GREEN)
            FONT.draw(surf, label, 22, y, col)
            if value is not None:
                txt = "< %s >" % value if sel else "  %s" % value
                FONT.draw(surf, txt, LW - 14 - FONT.width(txt), y,
                          GREEN if sel else GREY)
            y += 13
        FONT.draw(surf, "LEFT/RIGHT CHANGES A VALUE", LW // 2, 196, GREY, 1, True)
        FONT.draw(surf, "SETTINGS ARE NOT SAVED", LW // 2, 206, GREY, 1, True)
        FONT.draw(surf, "FILES=OFF  AUDIO FILES=OFF", LW // 2, 216, DGREEN, 1, True)
        self._footer(surf)


# ---------------------------------------------------------------------------
# GAME
# ---------------------------------------------------------------------------

class Game:
    """Top level application: state machine, fixed timestep loop, rendering."""

    SPEED_NAMES = ("CLASSIC", "FAST", "TURBO")
    SPEED_MULTS = (1.0, 1.7, 2.6)

    def __init__(self):
        self.scale = 3
        self.fullscreen = False
        self.screen = None
        self.scanline_overlay = None
        self._set_mode()
        pygame.display.set_caption(TITLE)
        self.frame_surf = pygame.Surface((LW, LH))
        try:
            self.frame_surf = self.frame_surf.convert()
        except pygame.error:
            pass

        self.spr = SpriteBank()
        self.snd = AtariSoundEngine()
        self.menu = MenuSystem(self)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = S_MENU
        self.accum = 0.0
        self.time = 0.0

        # settings
        self.opt_sound = True
        self.opt_volume = 7
        self.opt_lives = 3
        self.opt_speed = 0
        self.opt_scanlines = False  # off by default; SRCALPHA overlays blanked some Macs
        self.opt_starfield = True
        self.snd.set_volume(self.opt_volume / 10.0)

        self.high_score = 0
        self.stars = [
            (random.randrange(LW), random.randrange(HUD_H, GROUND_Y),
             random.choice((DGREEN, GREY)), random.uniform(1.5, 5.0))
            for _ in range(38)
        ]

        # runtime game objects
        self.player = None
        self.grid = None
        self.ufo = None
        self.bunkers = []
        self.bombs = []
        self.reset_game_vars()

    # -- display -------------------------------------------------------------

    def _set_mode(self):
        """Open a window. Prefer SCALED so macOS/Retina actually shows pixels."""
        wanted = (LW * self.scale, LH * self.scale)
        scaled = getattr(pygame, "SCALED", 0)
        errors = []
        attempts = []
        if self.fullscreen:
            if scaled:
                attempts.append(((0, 0), pygame.FULLSCREEN | scaled))
            attempts.append(((0, 0), pygame.FULLSCREEN))
        if scaled:
            attempts.append((wanted, scaled))
        attempts.append((wanted, 0))
        attempts.append(((LW * 2, LH * 2), scaled or 0))
        attempts.append((wanted, getattr(pygame, "RESIZABLE", 0)))

        self.screen = None
        for size, flags in attempts:
            try:
                self.screen = pygame.display.set_mode(size, flags)
                if size[0] and size[0] < LW * self.scale:
                    self.scale = max(1, size[0] // LW)
                break
            except pygame.error as exc:
                errors.append(str(exc))
        if self.screen is None:
            raise pygame.error(
                "could not open a display: " + (errors[-1] if errors else "unknown")
            )
        self.scanline_overlay = None
        # Warm the event queue -- some macOS builds stay black until pumped.
        pygame.event.pump()

    def _overlay(self):
        """Scanline veil using surface alpha (not per-pixel SRCALPHA)."""
        if self.scanline_overlay is None:
            w, h = self.screen.get_size()
            step = max(2, h // LH)
            ov = pygame.Surface((w, h))
            ov.fill((0, 0, 0))
            ov.set_colorkey((1, 0, 0))  # unused; we punch holes below
            # Build an opaque black sheet, then punch transparent gaps so only
            # every Nth row darkens the image via set_alpha.
            ov.fill((1, 0, 0))  # colorkey = fully transparent
            for y in range(0, h, step):
                pygame.draw.line(ov, (0, 0, 0), (0, y), (w, y))
            ov.set_alpha(90)
            self.scanline_overlay = ov
        return self.scanline_overlay

    # -- settings ------------------------------------------------------------

    def settings_items(self):
        return [
            ("sound", "SOUND", "ON" if self.opt_sound else "OFF"),
            ("volume", "VOLUME", "%d" % self.opt_volume),
            ("lives", "CANNONS", "%d" % self.opt_lives),
            ("speed", "PACE", self.SPEED_NAMES[self.opt_speed]),
            ("scanlines", "SCANLINES", "ON" if self.opt_scanlines else "OFF"),
            ("starfield", "STARFIELD", "ON" if self.opt_starfield else "OFF"),
            ("scale", "WINDOW", "%dX" % self.scale),
            ("reset", "RESET HI-SCORE", "%04d" % self.high_score),
            ("back", "BACK TO MENU", None),
        ]

    def settings_adjust(self, key_name, d):
        if key_name == "sound":
            self.opt_sound = not self.opt_sound
            self.snd.set_enabled(self.opt_sound)
        elif key_name == "volume":
            self.opt_volume = max(0, min(10, self.opt_volume + d))
            self.snd.set_volume(self.opt_volume / 10.0)
        elif key_name == "lives":
            self.opt_lives = max(1, min(5, self.opt_lives + d))
        elif key_name == "speed":
            self.opt_speed = (self.opt_speed + d) % len(self.SPEED_NAMES)
        elif key_name == "scanlines":
            self.opt_scanlines = not self.opt_scanlines
        elif key_name == "starfield":
            self.opt_starfield = not self.opt_starfield
        elif key_name == "scale":
            self.scale = max(2, min(5, self.scale + d))
            if not self.fullscreen:
                self._set_mode()
        elif key_name == "reset":
            self.high_score = 0

    @property
    def speed_mult(self):
        return self.SPEED_MULTS[self.opt_speed]

    # -- game lifecycle ------------------------------------------------------

    def reset_game_vars(self):
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.paused = False
        self.game_over = False
        self.game_over_t = 0.0
        self.wave_clear_t = 0.0
        self.respawn_t = 0.0
        self.extra_awarded = False
        self.bomb_timer = 0.0
        self.bombs = []

    def start_game(self):
        self.reset_game_vars()
        self.lives = self.opt_lives
        self.snd.stop_all()
        self.snd.reset_march()
        self.player = Player(self.spr, self.snd)
        self.ufo = UFO(self.spr, self.snd)
        self.spawn_wave(1)

    def spawn_wave(self, wave):
        self.wave = wave
        self.grid = AlienGrid(wave, self.spr, self.snd, self.speed_mult)
        self.bombs = []
        self.bomb_timer = self.bomb_interval()
        self.snd.reset_march()
        if self.ufo:
            self.ufo.reset()
        if self.player:
            self.player.reset_position()
        # Arcade rebuilds the shields every wave.
        self.build_bunkers()

    def build_bunkers(self):
        self.bunkers = []
        gap = (LW - 4 * Bunker.W) // 5
        x = gap
        for _ in range(4):
            self.bunkers.append(Bunker(x, BUNKER_Y))
            x += Bunker.W + gap

    def bomb_interval(self):
        alive = self.grid.alive_count if self.grid else 55
        base = 1.45 - 0.07 * min(self.wave - 1, 9)
        base *= 0.40 + 0.60 * (alive / 55.0)
        return max(0.22, base / self.speed_mult) * random.uniform(0.7, 1.35)

    def add_score(self, pts):
        self.score += pts
        if self.score > self.high_score:
            self.high_score = self.score
        if not self.extra_awarded and self.score >= EXTRA_LIFE_AT:
            self.extra_awarded = True
            self.lives += 1
            self.snd.extra_life()

    # -- main loop -----------------------------------------------------------

    def run(self):
        while self.running:
            ms = self.clock.tick(FPS)
            self.accum = min(self.accum + ms / 1000.0, 0.25)
            self.handle_events()
            while self.accum >= DT:
                self.update(DT)
                self.accum -= DT
            self.render()
        self.snd.stop_all()

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.state = S_EXIT
            elif ev.type == pygame.KEYDOWN:
                self.on_key(ev.key)
        if self.state == S_EXIT:
            self.running = False

    def on_key(self, key):
        if key == pygame.K_F11:
            self.fullscreen = not self.fullscreen
            self._set_mode()
            return
        if key == pygame.K_m:
            self.opt_sound = not self.opt_sound
            self.snd.set_enabled(self.opt_sound)
            return

        if self.state == S_PLAYING:
            self.on_key_playing(key)
        else:
            self.state = self.menu.key(self.state, key)
            if self.state == S_EXIT:
                self.running = False

    def on_key_playing(self, key):
        if self.player is None:
            return
        if key == pygame.K_ESCAPE:
            self.snd.stop_all()
            self.state = S_MENU
            return
        if key == pygame.K_p and not self.game_over:
            self.paused = not self.paused
            if self.paused:
                self.snd.ufo_stop()
            return
        if self.game_over:
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.snd.stop_all()
                self.state = S_MENU
            return
        if self.paused:
            return
        if key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w, pygame.K_LCTRL,
                   pygame.K_RCTRL, pygame.K_z):
            if self.respawn_t <= 0.0 and self.wave_clear_t <= 0.0:
                self.player.fire()

    # -- update --------------------------------------------------------------

    def update(self, dt):
        self.time += dt
        if self.state == S_PLAYING:
            self.update_play(dt)
        else:
            self.menu.update(dt)

    def update_play(self, dt):
        if self.paused or self.player is None or self.grid is None:
            return

        if self.game_over:
            self.game_over_t += dt
            self.player.update(dt, pygame.key.get_pressed(), True)
            self.grid.update(0.0)
            return

        if self.wave_clear_t > 0.0:
            self.wave_clear_t -= dt
            if self.wave_clear_t <= 0.0:
                self.spawn_wave(self.wave + 1)
            return

        freeze = self.respawn_t > 0.0
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, freeze)

        if freeze:
            self.respawn_t -= dt
            self.grid.update(0.0)  # only tick explosion timers
            if self.respawn_t <= 0.0:
                if self.lives <= 0:
                    self.trigger_game_over()
                else:
                    self.player.reset_position()
                    self.bombs = []
            return

        self.grid.update(dt)
        self.ufo.update(dt, self.grid.alive_count, True)
        self.update_bullets(dt)
        self.update_bombs(dt)
        self.alien_bunker_scrub()

        if self.grid.alive_count <= 0:
            self.wave_clear_t = 1.6
            self.snd.ufo_stop()
            self.snd.wave_clear()
            return

        if self.grid.landed:
            self.lives = 0
            self.player.kill()
            self.respawn_t = 1.8
            return

    def update_bullets(self, dt):
        b = self.player.bullet
        if b is None:
            return
        b.update(dt)

        # UFO
        if b.alive and self.ufo.active and self.ufo.rect.colliderect(b.rect):
            self.add_score(self.ufo.hit(self.player.shots_fired))
            b.alive = False

        # aliens
        if b.alive:
            a = self.grid.hit_test(b.rect)
            if a is not None:
                self.add_score(self.grid.kill(a))
                b.alive = False

        # bunkers
        if b.alive:
            for bu in self.bunkers:
                hit = bu.collide(b.rect)
                if hit:
                    bu.blast(hit[0], hit[1], 3, up=False)
                    b.alive = False
                    break

        # ceiling
        if b.alive and b.y <= HUD_H + 2:
            b.alive = False

        if not b.alive:
            self.player.bullet = None

    def update_bombs(self, dt):
        # spawn
        self.bomb_timer -= dt
        if self.bomb_timer <= 0.0 and len(self.bombs) < 3:
            self.bomb_timer = self.bomb_interval()
            shooters = self.grid.bottom_aliens()
            if shooters:
                a = random.choice(shooters)
                r = a.rect(self.grid.x, self.grid.y, self.grid.CELL_W, self.grid.CELL_H)
                kind = random.randrange(3)
                spd = (72.0 if kind == 2 else 60.0) * (0.85 + 0.30 * self.speed_mult)
                self.bombs.append(
                    Bullet(r.centerx - 1, r.bottom, spd, frames=self.spr.bombs[kind])
                )

        for b in self.bombs:
            b.update(dt)
            if not b.alive:
                continue
            # player shot cancels a bomb sometimes (classic behaviour)
            pb = self.player.bullet
            if pb is not None and pb.rect.colliderect(b.rect):
                b.alive = False
                pb.alive = False
                self.player.bullet = None
                continue
            for bu in self.bunkers:
                hit = bu.collide(b.rect)
                if hit:
                    bu.blast(hit[0], hit[1], 3, up=True)
                    b.alive = False
                    break
            if not b.alive:
                continue
            if self.player.dying <= 0.0 and self.player.rect.colliderect(b.rect):
                b.alive = False
                self.lives -= 1
                self.player.kill()
                self.respawn_t = 1.8
            elif b.y >= GROUND_Y - 2:
                b.alive = False

        self.bombs = [b for b in self.bombs if b.alive]

    def alien_bunker_scrub(self):
        bottom = self.grid.bottom()
        if bottom < BUNKER_Y:
            return
        for a in self.grid.iter_alive():
            r = a.rect(self.grid.x, self.grid.y, self.grid.CELL_W, self.grid.CELL_H)
            for bu in self.bunkers:
                if bu.rect.colliderect(r):
                    bu.erase_band(r.top)

    def trigger_game_over(self):
        self.game_over = True
        self.game_over_t = 0.0
        self.snd.game_over()

    # -- render --------------------------------------------------------------

    def render(self):
        surf = self.frame_surf
        surf.fill(BLACK)

        if self.state == S_PLAYING:
            self.draw_play(surf)
        else:
            if self.opt_starfield:
                self.draw_stars(surf)
            self.menu.draw(surf, self.state)

        # Scale straight onto the display surface.  An intermediate scaled
        # Surface can come back blank on some macOS / Retina pygame builds.
        size = self.screen.get_size()
        if size == (LW, LH):
            self.screen.blit(surf, (0, 0))
        else:
            pygame.transform.scale(surf, size, self.screen)

        if self.opt_scanlines:
            self.screen.blit(self._overlay(), (0, 0))
        pygame.display.flip()

    def draw_stars(self, surf):
        for x, y, col, spd in self.stars:
            yy = HUD_H + int((y - HUD_H + self.time * spd * 4) % (GROUND_Y - HUD_H))
            if 0 <= x < LW and 0 <= yy < LH:
                surf.set_at((x, yy), col)

    def draw_play(self, surf):
        if self.player is None or self.grid is None:
            FONT.draw(surf, "LOADING...", LW // 2, LH // 2, GREEN, 2, True)
            return

        if self.opt_starfield:
            self.draw_stars(surf)

        # HUD
        FONT.draw(surf, "SCORE", 8, 2, GREEN)
        FONT.draw(surf, "%04d" % self.score, 8, 10, WHITE)
        FONT.draw(surf, "HI-SCORE", LW // 2, 2, GREEN, 1, True)
        FONT.draw(surf, "%04d" % self.high_score, LW // 2, 10, WHITE, 1, True)
        FONT.draw(surf, "WAVE", LW - 8 - FONT.width("WAVE"), 2, GREEN)
        FONT.draw(surf, "%02d" % self.wave, LW - 8 - FONT.width("00"), 10, WHITE)

        for bu in self.bunkers:
            bu.draw(surf)

        self.grid.draw(surf)
        self.ufo.draw(surf)

        if self.player.bullet:
            self.player.bullet.draw(surf)
        for b in self.bombs:
            b.draw(surf)

        if not (self.respawn_t > 0.0 and self.player.dying <= 0.0):
            self.player.draw(surf)

        pygame.draw.line(surf, GREEN, (0, GROUND_Y), (LW, GROUND_Y))

        # lives + credits
        FONT.draw(surf, "%d" % self.lives, 8, GROUND_Y + 6, WHITE)
        x = 18
        small = pygame.transform.scale(
            self.spr.cannon,
            (self.spr.cannon.get_width(), self.spr.cannon.get_height()),
        )
        for _ in range(max(0, self.lives - 1)):
            surf.blit(small, (x, GROUND_Y + 5))
            x += small.get_width() + 3
        FONT.draw(surf, "CREDIT 01", LW - 8 - FONT.width("CREDIT 01"),
                  GROUND_Y + 6, GREEN)

        if self.paused:
            self.banner(surf, "PAUSED", "PRESS P TO RESUME")
        elif self.game_over:
            self.banner(surf, "GAME OVER", "PRESS ENTER FOR MENU")
        elif self.wave_clear_t > 0.0:
            self.banner(surf, "WAVE %d CLEAR" % self.wave, "GET READY")

    def banner(self, surf, title, sub):
        box = pygame.Rect(16, 96, LW - 32, 44)
        pygame.draw.rect(surf, BLACK, box)
        pygame.draw.rect(surf, GREEN, box, 1)
        FONT.draw(surf, title, LW // 2, box.y + 8, WHITE, 2, True)
        FONT.draw(surf, sub, LW // 2, box.y + 28, GREEN, 1, True)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    try:
        pygame.mixer.pre_init(SR, -16, 1, 512)
        pygame.init()
        if not pygame.display.get_init():
            pygame.display.init()
    except Exception as exc:  # pragma: no cover
        sys.stderr.write("  failed to initialise pygame: %s\n" % exc)
        return 1

    random.seed()
    try:
        game = Game()
    except pygame.error as exc:
        sys.stderr.write(
            "\n  Could not open a game window: %s\n"
            "  If you launched from the Finder, try Terminal instead:\n"
            "    cd \"%s\"\n"
            "    python3 space4k.py\n\n"
            % (exc, sys.path[0] or ".")
        )
        pygame.quit()
        return 1

    try:
        game.run()
    except KeyboardInterrupt:
        pass
    finally:
        try:
            pygame.quit()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
