"""
Resources for the SERPENT application.
"""

import textwrap
from typing import Dict

# --- Themes ---
THEMES: Dict[str, Dict[str, str]] = {
    "Classic (Pastel)": {
        "box": "lightyellow",
        "diamond": "lightblue",
        "oval": "lightgreen",
        "circle": "thistle",
        "parallelogram": "lightcyan",
        "break": "mistyrose",
        "continue": "lightgray",
    },
    "Clean White": {
        "box": "white",
        "diamond": "white",
        "oval": "white",
        "circle": "white",
        "parallelogram": "white",
        "break": "white",
        "continue": "white",
    },
    "Dark Mode": {
        "box": "#444444",
        "diamond": "#555555",
        "oval": "#222222",
        "circle": "#666666",
        "parallelogram": "#333333",
        "break": "#883333",
        "continue": "#333388",
    },
    "Blueberry": {
        "box": "#e3f2fd",
        "diamond": "#bbdefb",
        "oval": "#90caf9",
        "circle": "#64b5f6",
        "parallelogram": "#42a5f5",
        "break": "#ffcdd2",
        "continue": "#e1bee7",
    },
}

# --- Examples ---
EXAMPLES = {
    "ATM Machine (If/Else)": textwrap.dedent(
        """\
        def atm_withdrawal(balance: float, request: float, is_authenticated: bool) -> str:
            if not is_authenticated:
                return "Authentication failed."

            if request <= 0:
                print("Invalid amount.")
                result = "Error: Amount must be positive."
            elif request > balance:
                print("Insufficient funds.")
                result = "Error: Not enough money."
            else:
                balance -= request
                print(f"Dispensing ${request}...")
                result = f"Success. New balance: ${balance}"

            return result
    """
    ),
    "Smart Light (Loop & Condition)": textwrap.dedent(
        """\
        def smart_lighting_system(sensor_readings: list[float], threshold: float):
            for reading in sensor_readings:
                if reading < 0:
                    print("Sensor Error: Negative light level.")
                    continue  # Skip invalid reading

                if reading > threshold:
                    print(f"Bright ({reading} lux): Turning lights OFF.")
                    break  # Sufficient light found, stop checking
                else:
                    print(f"Dim ({reading} lux): Keep lights ON.")

            print("Lighting check complete.")
    """
    ),
    "Server Connection (While Loop)": textwrap.dedent(
        """\
        def connect_to_server(max_retries: int):
            attempt = 0
            connected = False

            while attempt < max_retries and not connected:
                print(f"Connecting... Attempt {attempt + 1}")
                # Simulate connection logic
                if attempt == 2:  # Pretend success on 3rd try
                    connected = True
                else:
                    attempt += 1

            if connected:
                return "Connection Established"
            else:
                return "Connection Failed Service Unavailable"
    """
    ),
    "File Safer (Try/Except/Finally)": textwrap.dedent(
        """\
        def safe_file_reader(filepath: str) -> str:
            file_handle = None
            try:
                print(f"Opening {filepath}...")
                # Simulate opening file (would naturally raise OSError)
                if not filepath:
                    raise ValueError("Empty filepath")
                file_handle = open(filepath, 'r')
                data = file_handle.read()
                return data
            except FileNotFoundError:
                return "Error: File not found."
            except ValueError as e:
                return f"Error: Invalid input - {e}"
            finally:
                if file_handle:
                    print("Closing file handle...")
                    file_handle.close()
                print("Cleanup complete.")
    """
    ),
    "Order Processing (Nested)": textwrap.dedent(
        """\
        def process_orders(orders: list[dict]):
            for order in orders:
                status = order.get("status")

                if status == "cancelled":
                    continue

                if status == "pending":
                    amount = order.get("amount", 0)
                    if amount > 1000:
                        print("Flagging for manual review (High Value)")
                    elif amount < 0:
                        print("Error: Invalid Order")
                        break # Stop critical error
                    else:
                        print("Auto-approving order")
                else:
                    print(f"Skipping order with status: {status}")

            return "Batch Complete"
    """
    ),
}
