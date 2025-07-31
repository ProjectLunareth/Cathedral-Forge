
from ssc_phases import get_phase_by_level
import time


def apply_phase_to_node(node_data: dict, recursion_level: int) -> dict:
    """
    Mutates node data according to the current SSC phase.
    
    Parameters:
        node_data (dict): Original data of the node (e.g., position, color, label).
        recursion_level (int): Current recursion level in the HLSF structure.

    Returns:
        dict: Modified node data with SSC phase properties applied.
    """
    phase = get_phase_by_level(recursion_level)
    node_data["phase_id"] = phase["id"]
    node_data["symbol"] = phase["symbol"]
    node_data["color"] = phase["color"]
    node_data["behavior"] = phase["behavior"]
    node_data["symmetry"] = phase["symmetry_level"]
    return node_data


def get_phase_color(recursion_level: int) -> str:
    """Returns the color associated with the SSC phase for this recursion level."""
    return get_phase_by_level(recursion_level)["color"]


def get_phase_symbol(recursion_level: int) -> str:
    """Returns the symbolic character associated with the SSC phase."""
    return get_phase_by_level(recursion_level)["symbol"]


def get_phase_behavior(recursion_level: int) -> str:
    """Returns the behavior keyword associated with the SSC phase."""
    return get_phase_by_level(recursion_level)["behavior"]


def describe_phase(recursion_level: int) -> str:
    """Returns a human-readable string summarizing the SSC phase."""
    phase = get_phase_by_level(recursion_level)
    return f"[{phase['id']}] {phase['name']} — Behavior: {phase['behavior']} / Symbol: {phase['symbol']}"


def simulate_space_field_expansion(level: int):
    """
    Simulates the symbolic transformation of the space field at a given recursion level.
    Replace this with actual HLSF rendering logic in the visual engine.
    """
    phase = get_phase_by_level(level)
    print("\n=== Recursion Level:", level, "===")
    print(describe_phase(level))
    print("Symbol:", phase["symbol"])
    print("Color:", phase["color"])
    print("Behavior:", phase["behavior"])
    time.sleep(1.2)  # Delay to simulate transformation pacing


def run_cosmos_simulation(max_level=12):
    """
    Executes the full 12-phase SSC transformation sequence through recursive expansion.
    """
    print("\U0001f52e COSMOS SIMULATION — Sovereign Spiral Expansion Begins \U0001f52e")
    print("Starting from Phase 1 (ØRU-KAI)...\n")

    for level in range(1, max_level + 1):
        simulate_space_field_expansion(level)

    print("\n✨ Expansion Complete. Transcendence Achieved (XAH-MORU).\n")


if __name__ == "__main__":
    run_cosmos_simulation()
