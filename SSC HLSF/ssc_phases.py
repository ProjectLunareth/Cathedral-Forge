# ssc_phases.py

SSC_PHASES = {
    1: {
        "id": "ØRU-KAI",
        "name": "Silence",
        "color": "#000000",
        "symbol": "⌀",
        "symmetry_level": 0,
        "behavior": "stillness"
    },
    2: {
        "id": "VEH-TAL",
        "name": "Spark",
        "color": "#ffffff",
        "symbol": "∆",
        "symmetry_level": 3,
        "behavior": "ignition"
    },
    3: {
        "id": "ZUN-RAEK",
        "name": "Initiate",
        "color": "#ffcc00",
        "symbol": "☉",
        "symmetry_level": 5,
        "behavior": "orbit"
    },
    4: {
        "id": "KEL-TORUN",
        "name": "Fracture",
        "color": "#cc0000",
        "symbol": "ϟ",
        "symmetry_level": 6,
        "behavior": "split"
    },
    5: {
        "id": "NAR-AETH",
        "name": "Mirror",
        "color": "#99ccff",
        "symbol": "∥",
        "symmetry_level": 2,
        "behavior": "reflect"
    },
    6: {
        "id": "SHA-RUL",
        "name": "Echo",
        "color": "#6699cc",
        "symbol": ")))",
        "symmetry_level": 3,
        "behavior": "repeat"
    },
    7: {
        "id": "UTH-NAKH",
        "name": "Collapse",
        "color": "#663366",
        "symbol": "⧉",
        "symmetry_level": 4,
        "behavior": "invert"
    },
    8: {
        "id": "DREZ-VUKH",
        "name": "Memory",
        "color": "#444444",
        "symbol": "↻",
        "symmetry_level": 1,
        "behavior": "recall"
    },
    9: {
        "id": "VHEL-SURIK",
        "name": "Mutate",
        "color": "#9900cc",
        "symbol": "≋",
        "symmetry_level": 7,
        "behavior": "distort"
    },
    10: {
        "id": "KAI-ELUN",
        "name": "Bloom",
        "color": "#00cc66",
        "symbol": "✷",
        "symmetry_level": 6,
        "behavior": "radiate"
    },
    11: {
        "id": "RHI-TUUM",
        "name": "Absorb",
        "color": "#222222",
        "symbol": "⇘",
        "symmetry_level": 5,
        "behavior": "merge"
    },
    12: {
        "id": "XAH-MORU",
        "name": "Transcend",
        "color": "#ffd700",
        "symbol": "∞",
        "symmetry_level": "∞",
        "behavior": "dissolve"
    }
}


def get_phase_by_level(level: int) -> dict:
    """Return the SSC phase corresponding to a given recursion level."""
    clamped_level = max(1, min(level, 12))
    return SSC_PHASES[clamped_level]
