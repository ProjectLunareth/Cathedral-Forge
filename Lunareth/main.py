"""
Lunareth – main orchestrator script
Handles top‑level CLI routing, including the new visualisation mode.
"""

import sys
from pathlib import Path

# -------- Optional: pull core engine helpers ------------
# from engine import run_engine                # existing logic
# from config import load_config               # existing logic
# --------------------------------------------------------

# ---- NEW: visualisation entry points -------------------
try:
    # Local import to avoid matplotlib overhead unless needed
    from visualize_lunareth import animate, render_static
except ImportError:
    animate = render_static = None            # graceful fallback
# --------------------------------------------------------

# ---- NEW: memory reset helper --------------------------
try:
    from core.memory_loop_archiver import reset_memory_loop
except (ImportError, ModuleNotFoundError):
    def reset_memory_loop():
        print("[WARN] memory_loop_archiver not found – skipping reset.")
# --------------------------------------------------------


def main() -> None:
    """Entry point for the Lunareth command‑line interface."""
    args = sys.argv[1:]

    # ── VISUALISATION MODE ───────────────────────────────
    if "--visual" in args:
        if render_static is None:
            print("✖  visualize_lunareth.py not available.")
            sys.exit(1)

        if "--static" in args:
            render_static()
        else:
            animate()
        return

    # ── RESET MEMORY STACK (optional flag) ───────────────
    if "--start-fresh" in args:
        reset_memory_loop()
        print("✓ Memory loop reset.")
        # Note: continue on – user may combine with other flags

    # ── PLACEHOLDER FOR OTHER MODES / FLAGS --------------
    if "--help" in args or not args:
        print(
            "Lunareth CLI\n"
            "Usage:\n"
            "  python main.py --visual [--static]     # Launch visualiser\n"
            "  python main.py --start-fresh           # Reset glyph memory\n"
            "  python main.py --help                  # This message\n"
            "... (other existing flags) ..."
        )
        return

    # ---- Existing engine logic could stay here ----------
    # run_engine(args)    # example
    # -----------------------------------------------------

if __name__ == "__main__":
    main()
