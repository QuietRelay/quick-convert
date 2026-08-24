#!/usr/bin/env python3
"""
convert.py - Quick unit conversions from the terminal.

Usage:
    python convert.py temp 72f          # 72 Fahrenheit -> Celsius
    python convert.py temp 22c          # 22 Celsius -> Fahrenheit
    python convert.py temp 300k         # 300 Kelvin -> Celsius and Fahrenheit
    python convert.py 72f               # shorthand: temp is assumed
    python convert.py                   # interactive prompt

Works identically in Windows cmd.exe, PowerShell, and macOS/Linux terminals
since it only relies on the Python standard library (no dependencies).

New converters can be added as additional subcommands (see CONVERTERS below)
without touching the existing temp logic.
"""

import re
import sys

UNIT_NAMES = {"c": "C", "f": "F", "k": "K"}


def parse_value_unit(raw: str):
    """Parse a string like '72f', '72 F', or '-40c' into (value, unit)."""
    match = re.match(r"^\s*(-?\d+(?:\.\d+)?)\s*([a-zA-Z])\s*$", raw)
    if not match:
        return None
    value = float(match.group(1))
    unit = match.group(2).lower()
    if unit not in UNIT_NAMES:
        return None
    return value, unit


def convert_temp(value: float, unit: str) -> dict:
    """Convert a temperature to the other two common scales."""
    if unit == "f":
        c = (value - 32) * 5 / 9
    elif unit == "c":
        c = value
    elif unit == "k":
        c = value - 273.15
    else:
        raise ValueError(f"Unknown temperature unit: {unit}")

    f = c * 9 / 5 + 32
    k = c + 273.15
    return {"c": c, "f": f, "k": k}


def run_temp(raw: str) -> None:
    parsed = parse_value_unit(raw)
    if not parsed:
        print(f"Couldn't parse '{raw}'. Expected a number plus C, F, or K, e.g. 72f or -40c.")
        return

    value, unit = parsed
    results = convert_temp(value, unit)

    others = [f"{results[u]:.1f}{UNIT_NAMES[u]}" for u in ("c", "f", "k") if u != unit]
    print(f"{value:g}{UNIT_NAMES[unit]} = {' = '.join(others)}")


# Map of subcommand name -> handler function. Add new converters here.
CONVERTERS = {
    "temp": run_temp,
}


def main() -> None:
    args = sys.argv[1:]

    if not args:
        print("Quick Convert")
        print("Enter a value like '72f' or '22c' (temperature). Type 'q' to quit.\n")
        while True:
            try:
                raw = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not raw or raw.lower() in ("q", "quit", "exit"):
                break
            run_temp(raw)
        return

    first, rest = args[0], args[1:]

    if first.lower() in CONVERTERS:
        handler = CONVERTERS[first.lower()]
        for raw in rest:
            handler(raw)
        return

    # Shorthand: no subcommand given, assume temperature (the only converter so far).
    for raw in args:
        run_temp(raw)


if __name__ == "__main__":
    main()
