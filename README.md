# quick-convert

A tiny, dependency-free command-line tool for fast unit conversions:
temperature, length, weight, volume/cooking, speed, and data sizes. It works
out what kind of conversion you want from the unit you type.

## Requirements

- Python 3 (no third-party packages needed)

## Usage

```bash
qconvert 72f            # 72F = 22.2C
qconvert 5ft            # 5 ft = 1.52 m = 152.4 cm
qconvert 180cm          # 180 cm = 70.87 in = 5 ft 10.9 in
qconvert 150lb          # 150 lb = 68.04 kg
qconvert 2 cups         # 2 cups = 473.2 ml = 32 tbsp = 16 fl oz
qconvert 65mph          # 65 mph = 104.6 kph
qconvert 4.7GB          # 4.7 GB = 4.38 GiB
qconvert 72f 5ft 150lb  # several values at once, one line each
qconvert weight 12oz    # naming the category is optional
qconvert --help         # list every supported unit
```

Run `qconvert` with no arguments for an interactive prompt.

Supported units (case doesn't matter, and a space before the unit is fine):

| Category | Units |
| --- | --- |
| temp | `f`, `c` |
| length | `in`, `ft`, `yd`, `mi`, `mm`, `cm`, `m`, `km` |
| weight | `oz`, `lb`, `g`, `kg` |
| volume | `tsp`, `tbsp`, `fl oz`, `cup`, `pt`, `qt`, `gal`, `ml`, `l` (US measures) |
| speed | `mph`, `kph` (or `km/h`) |
| data | `B`, `KB`, `MB`, `GB`, `TB` (1000-based) and `KiB`, `MiB`, `GiB`, `TiB` (1024-based) |

Common spellings work too (`feet`, `lbs`, `cups`, `tablespoons`, ...). `oz` is
weight; use `fl oz` for volume. `m` is meters; use `mi` for miles.

Data sizes: drives are sold in 1000-based GB, but Windows reports 1024-based
units while labelling them "GB". That's why a "1 TB" drive shows up as about
931 GB in Explorer: `qconvert 1TB` gives `1 TB = 931.3 GiB`.

If you run `qconvert.py` directly instead of installing the command, use
`python qconvert.py ...` in place of `qconvert ...`.

## Installing it as a plain `qconvert` command

Clone the repo, then put this folder on your `PATH`.

The command is named `qconvert`, not `convert` — Windows ships a built-in
`System32\convert.exe` (FAT-to-NTFS disk conversion) that would otherwise
shadow a plain `convert` on PATH.

**macOS / Linux:**

```bash
git clone https://github.com/QuietRelay/quick-convert.git
chmod +x quick-convert/qconvert
echo 'export PATH="$PATH:'"$(pwd)"'/quick-convert"' >> ~/.zshrc   # or ~/.bashrc
```

**Windows (PowerShell or cmd):**

```powershell
git clone https://github.com/QuietRelay/quick-convert.git
[Environment]::SetEnvironmentVariable('PATH', "$env:PATH;$(Resolve-Path .\quick-convert)", 'User')
```

> Avoid `setx` for editing `PATH` on Windows — it silently truncates the
> value at 1024 characters, which will corrupt the rest of your PATH if it's
> already long. `[Environment]::SetEnvironmentVariable` has no such limit.

Open a new terminal afterward, then run:

```bash
qconvert temp 72f
```

## Adding a unit

In `qconvert.py`:

1. Add it to `UNITS` with its category and its size in that category's base
   unit (meters, grams, milliliters, km/h, or bytes).
2. Add any other spellings to `ALIASES`.
3. Say what it should convert to in `TARGETS`.

## Running the tests

```bash
python -m unittest
```

## License

No license file yet — all rights reserved by default. Add a `LICENSE` file
if you want to permit reuse.
