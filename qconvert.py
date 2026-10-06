#!/usr/bin/env python3
"""
qconvert.py - Quick unit conversions from the terminal.

Usage:
    qconvert 72f                 # temperature: 72F = 22.2C
    qconvert 5ft                 # length:      5 ft = 1.52 m = 152.4 cm
    qconvert 150lb               # weight:      150 lb = 68.04 kg
    qconvert 4.7GB               # data size:   4.7 GB = 4.38 GiB
    qconvert 2 cups              # volume:      2 cups = 473.2 ml = 32 tbsp = 16 fl oz
    qconvert 65mph               # speed:       65 mph = 104.6 kph
    qconvert 72f 5ft 150lb       # several values at once
    qconvert weight 12oz         # optional category name (temp, length, ...)
    qconvert                     # interactive prompt
    qconvert --help              # list every supported unit

The category is worked out from the unit, so naming it is optional.

Works identically in Windows cmd.exe, PowerShell, and macOS/Linux terminals
since it only relies on the Python standard library (no dependencies).

Named "qconvert" (not "convert") because Windows ships a built-in
System32\\convert.exe (FAT->NTFS disk conversion) that would otherwise
shadow this command on PATH.

To add a unit, add it to UNITS (and its spellings to ALIASES), then say what
it should convert to in TARGETS.
"""

import math
import re
import sys

# Canonical unit -> (category, size in the category's base unit, display name).
# Base units: length = meter, weight = gram, volume = milliliter,
# speed = km/h, data = byte. Temperature isn't a simple multiple, so its
# factor is unused and it's handled in convert().
UNITS = {
    # Length
    "in": ("length", 0.0254, "in"),
    "ft": ("length", 0.3048, "ft"),
    "yd": ("length", 0.9144, "yd"),
    "mi": ("length", 1609.344, "mi"),
    "mm": ("length", 0.001, "mm"),
    "cm": ("length", 0.01, "cm"),
    "m": ("length", 1.0, "m"),
    "km": ("length", 1000.0, "km"),
    # Weight
    "oz": ("weight", 28.349523125, "oz"),
    "lb": ("weight", 453.59237, "lb"),
    "g": ("weight", 1.0, "g"),
    "kg": ("weight", 1000.0, "kg"),
    # Volume / cooking (US customary measures)
    "tsp": ("volume", 4.92892159375, "tsp"),
    "tbsp": ("volume", 14.78676478125, "tbsp"),
    "floz": ("volume", 29.5735295625, "fl oz"),
    "cup": ("volume", 236.5882365, "cup"),
    "pt": ("volume", 473.176473, "pt"),
    "qt": ("volume", 946.352946, "qt"),
    "gal": ("volume", 3785.411784, "gal"),
    "ml": ("volume", 1.0, "ml"),
    "l": ("volume", 1000.0, "L"),
    # Speed
    "mph": ("speed", 1.609344, "mph"),
    "kph": ("speed", 1.0, "kph"),
    # Data size: KB/MB/GB/TB are powers of 1000 (what drive makers and most
    # websites use); KiB/MiB/GiB/TiB are powers of 1024 (what Windows shows,
    # even though it labels them "GB").
    "b": ("data", 1, "B"),
    "kb": ("data", 1000**1, "KB"),
    "mb": ("data", 1000**2, "MB"),
    "gb": ("data", 1000**3, "GB"),
    "tb": ("data", 1000**4, "TB"),
    "kib": ("data", 1024**1, "KiB"),
    "mib": ("data", 1024**2, "MiB"),
    "gib": ("data", 1024**3, "GiB"),
    "tib": ("data", 1024**4, "TiB"),
    # Temperature
    "f": ("temp", None, "F"),
    "c": ("temp", None, "C"),
}

# Extra spellings people type -> canonical unit. Matching ignores case,
# spaces, and periods, so "fl oz", "Fl. Oz." and "FLOZ" are all the same.
ALIASES = {
    "inch": "in", "inches": "in",
    "foot": "ft", "feet": "ft",
    "yard": "yd", "yards": "yd", "yds": "yd",
    "mile": "mi", "miles": "mi",
    "millimeter": "mm", "millimeters": "mm", "millimetre": "mm", "millimetres": "mm",
    "centimeter": "cm", "centimeters": "cm", "centimetre": "cm", "centimetres": "cm",
    "meter": "m", "meters": "m", "metre": "m", "metres": "m",
    "kilometer": "km", "kilometers": "km", "kilometre": "km", "kilometres": "km",
    "ounce": "oz", "ounces": "oz",
    "lbs": "lb", "pound": "lb", "pounds": "lb",
    "gram": "g", "grams": "g",
    "kgs": "kg", "kilo": "kg", "kilos": "kg", "kilogram": "kg", "kilograms": "kg",
    "teaspoon": "tsp", "teaspoons": "tsp",
    "tbs": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
    "fluidounce": "floz", "fluidounces": "floz",
    "cups": "cup",
    "pint": "pt", "pints": "pt",
    "quart": "qt", "quarts": "qt",
    "gallon": "gal", "gallons": "gal",
    "milliliter": "ml", "milliliters": "ml", "millilitre": "ml", "millilitres": "ml",
    "liter": "l", "liters": "l", "litre": "l", "litres": "l",
    "kmh": "kph", "km/h": "kph", "kmph": "kph", "km/hr": "kph",
    "byte": "b", "bytes": "b",
    "°f": "f", "fahrenheit": "f",
    "°c": "c", "celsius": "c",
}

# Optional category names accepted as the first word, e.g. "qconvert len 5ft".
CATEGORIES = {
    "temp": "temp", "temperature": "temp",
    "length": "length", "len": "length", "distance": "length",
    "weight": "weight", "mass": "weight",
    "volume": "volume", "vol": "volume", "cooking": "volume", "cook": "volume",
    "speed": "speed",
    "data": "data", "size": "data",
}

EXAMPLES = {
    "temp": "72f", "length": "5ft", "weight": "150lb",
    "volume": "2cups", "speed": "65mph", "data": "4.7GB",
}


def _ml_targets(ml: float) -> list:
    # Spoon measures for small amounts, fluid ounces and cups for bigger ones.
    return ["tsp", "tbsp"] if abs(ml) < 60 else ["floz", "cup"]


def _with_ft_in(main_target: str):
    def targets(meters: float) -> list:
        # A "5 ft 10.9 in" breakdown is only useful from about a foot up.
        return [main_target] + (["ftin"] if abs(meters) >= 0.3048 else [])
    return targets


# What each unit converts to. Either a list of canonical units, or a function
# of the value in base units that returns one. Data sizes use _data_targets().
TARGETS = {
    "in": ["cm"], "ft": ["m", "cm"], "yd": ["m"], "mi": ["km"],
    "mm": ["in"], "cm": _with_ft_in("in"), "m": _with_ft_in("ft"), "km": ["mi"],
    "oz": ["g"], "lb": ["kg"], "g": ["oz"], "kg": ["lb"],
    "tsp": ["ml", "tbsp"], "tbsp": ["ml", "tsp"], "floz": ["ml", "tbsp"],
    "cup": ["ml", "tbsp", "floz"], "pt": ["ml", "cup"], "qt": ["l", "cup"],
    "gal": ["l", "qt"], "ml": _ml_targets, "l": ["qt", "gal"],
    "mph": ["kph"], "kph": ["mph"],
    "f": ["c"], "c": ["f"],
}

DECIMAL_DATA = ["b", "kb", "mb", "gb", "tb"]
BINARY_DATA = ["b", "kib", "mib", "gib", "tib"]


def _best_data_unit(num_bytes: float, units: list) -> str:
    """Largest unit in the list that keeps the number at 1 or more."""
    best = units[0]
    for u in units:
        if abs(num_bytes) >= UNITS[u][1]:
            best = u
    return best


def _data_targets(unit: str, num_bytes: float) -> list:
    # Best fit in the same system first (1500 MB -> 1.5 GB), then the other
    # system (-> 1.4 GiB). Plain bytes get the best fit in each system.
    if unit in DECIMAL_DATA:
        systems = [DECIMAL_DATA, BINARY_DATA]
    else:
        systems = [BINARY_DATA, DECIMAL_DATA]
    targets = []
    for units in systems:
        u = _best_data_unit(num_bytes, units)
        if u != unit and u not in targets:
            targets.append(u)
    return targets


def normalize_unit(raw: str):
    """Turn whatever the user typed ('Fl. Oz.', 'lbs', 'GiB') into a canonical unit, or None."""
    key = re.sub(r"[\s.]", "", raw.lower())
    if key in UNITS:
        return key
    return ALIASES.get(key)


VALUE_RE = re.compile(r"^\s*([-+]?(?:\d[\d,]*)?\.?\d+)\s*(\D*?)\s*$")


def parse_value_unit(raw: str):
    """Parse '72f', '5 ft', '2 cups', or '-40c' into (value, canonical unit).

    Raises ValueError with a message for the user if it can't.
    """
    match = VALUE_RE.match(raw)
    if not match:
        raise ValueError(f"Couldn't parse '{raw.strip()}'. Expected a number and a unit, e.g. 72f, 5ft, 150lb.")
    value = float(match.group(1).replace(",", ""))
    unit_text = match.group(2)
    if not unit_text:
        raise ValueError(f"'{raw.strip()}' is missing a unit, e.g. {match.group(1)}f or {match.group(1)}ft.")
    unit = normalize_unit(unit_text)
    if unit is None:
        raise ValueError(f"Unknown unit '{unit_text}'. Run 'qconvert --help' to see supported units.")
    return value, unit


def convert(value: float, unit: str) -> list:
    """Convert a value to its default targets. Returns [(value, unit), ...].

    The special unit "ftin" carries a (feet, inches) tuple as its value.
    """
    category, factor, _ = UNITS[unit]

    if category == "temp":
        if unit == "f":
            return [((value - 32) * 5 / 9, "c")]
        return [(value * 9 / 5 + 32, "f")]

    base = value * factor
    if category == "data":
        targets = _data_targets(unit, base)
    else:
        targets = TARGETS[unit]
        if callable(targets):
            targets = targets(base)

    results = []
    for t in targets:
        if t == "ftin":
            total_in = round(abs(base) / UNITS["in"][1], 1)
            feet, inches = divmod(total_in, 12)
            sign = -1 if base < 0 else 1
            results.append(((sign * int(feet), inches), "ftin"))
        else:
            results.append((base / UNITS[t][1], t))
    return results


def format_number(x: float, decimals=None) -> str:
    """Round to a sensible precision for reading: 104.6, 1.52, 0.0634."""
    if decimals is None:
        ax = abs(x)
        if ax == 0 or ax >= 100:
            decimals = 1
        elif ax >= 1:
            decimals = 2
        else:
            decimals = 2 - math.floor(math.log10(ax))  # three significant figures
    s = f"{x:,.{decimals}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s == "-0":
        s = "0"
    return s


def format_quantity(value, unit: str, is_input: bool = False) -> str:
    if unit == "ftin":
        feet, inches = value
        return f"{feet} ft {format_number(inches, decimals=1)} in"
    category, _, label = UNITS[unit]
    if is_input:
        number = format_number(value, decimals=10)  # show what was typed, untouched
    elif category == "temp":
        number = format_number(value, decimals=1)
    else:
        number = format_number(value)
    if category == "temp":
        return f"{number}{label}"
    if unit == "cup" and number not in ("1", "-1"):
        label = "cups"
    return f"{number} {label}"


def convert_text(raw: str, category=None) -> str:
    """Convert one 'number unit' string to a display line. Raises ValueError."""
    value, unit = parse_value_unit(raw)
    unit_category = UNITS[unit][0]
    if category and unit_category != category:
        raise ValueError(f"'{raw.strip()}' is a {unit_category} unit, not {category}.")
    parts = [format_quantity(value, unit, is_input=True)]
    parts += [format_quantity(v, u) for v, u in convert(value, unit)]
    return " = ".join(parts)


def split_values(text: str) -> list:
    """Split '72f 5 ft 2 fl oz' into ['72f', '5 ft', '2 fl oz'].

    A new value starts wherever a number follows whitespace, so units may
    contain spaces and may be separated from their number.
    """
    text = text.strip()
    if not text:
        return []
    return re.split(r"\s+(?=[-+]?\.?\d)", text)


def run_line(text: str) -> bool:
    """Convert everything on one line of input, printing results. Returns False on any error."""
    words = text.split(None, 1)
    category = None
    if words and words[0].lower() in CATEGORIES:
        category = CATEGORIES[words[0].lower()]
        text = words[1] if len(words) > 1 else ""
        if not text.strip():
            print(f"Give a value to convert after '{words[0]}', e.g. {words[0]} {EXAMPLES[category]}.")
            return False

    ok = True
    for chunk in split_values(text):
        try:
            print(convert_text(chunk, category))
        except ValueError as e:
            print(e)
            ok = False
    return ok


HELP = """\
qconvert - quick unit conversions

Usage:
  qconvert <number><unit> [more values...]   e.g. qconvert 72f 5ft 150lb
  qconvert <category> <number><unit>         category name is optional
  qconvert                                   interactive prompt

Units (case doesn't matter; a space before the unit is fine):
  temp     f, c
  length   in, ft, yd, mi, mm, cm, m, km
  weight   oz, lb, g, kg
  volume   tsp, tbsp, fl oz, cup, pt, qt, gal, ml, l   (US measures)
  speed    mph, kph (or km/h)
  data     B, KB, MB, GB, TB    (1000-based, how drives are sold)
           KiB, MiB, GiB, TiB   (1024-based, what Windows shows as "GB")

Notes: "oz" is weight; use "fl oz" for volume. "m" is meters; use "mi" for miles.
"""


def main() -> None:
    args = sys.argv[1:]

    if args and args[0].lower() in ("-h", "--help", "help", "/?"):
        print(HELP, end="")
        return

    if not args:
        print("Quick Convert")
        print("Enter a value like 72f, 5ft, 150lb, 2 cups, 65mph, or 4.7GB.")
        print("Type 'help' for all units, 'q' to quit.\n")
        while True:
            try:
                raw = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not raw:
                continue
            if raw.lower() in ("q", "quit", "exit"):
                break
            if raw.lower() in ("h", "help", "?"):
                print(HELP)
                continue
            run_line(raw)
        return

    if not run_line(" ".join(args)):
        sys.exit(1)


if __name__ == "__main__":
    main()
