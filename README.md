# quick-convert

A tiny, dependency-free command-line tool for fast unit conversions. Started
with temperature (F/C/K) because constantly converting between Fahrenheit
and Celsius gets old fast. Built to grow — more converters can be added as
subcommands over time.

## Requirements

- Python 3 (no third-party packages needed)

## Usage

```bash
python convert.py temp 72f      # 72 Fahrenheit -> Celsius and Kelvin
python convert.py temp 22c      # 22 Celsius -> Fahrenheit and Kelvin
python convert.py temp 300k     # 300 Kelvin -> Celsius and Fahrenheit
python convert.py 72f           # shorthand: "temp" is assumed for now
```

Interactive mode (no arguments):

```bash
python convert.py
```

## Installing it as a plain `convert` command

Clone the repo, then put this folder on your `PATH`.

**macOS / Linux:**

```bash
git clone https://github.com/QuietRelay/quick-convert.git
chmod +x quick-convert/convert
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
convert temp 72f
```

## Adding a new converter

Add a `run_<name>(raw: str)` function and register it in the `CONVERTERS`
dict in `convert.py`. It'll automatically become available as
`convert <name> <value>`.

## License

No license file yet — all rights reserved by default. Add a `LICENSE` file
if you want to permit reuse.
