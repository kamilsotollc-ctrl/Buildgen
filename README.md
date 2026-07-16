# buildgen

**One build manifest. Two real build scripts. Zero drift.**

`buildgen` reads a single declarative `build.yaml` and generates both a Unix `Makefile`
and a Windows `mswin32/Build.bat` from it — so your `configure` / `build` / `test` /
`install` steps never fall out of sync between platforms.

```
build.yaml  ──buildgen──>  Makefile              (macOS / Linux / BSD)
                     └───>  mswin32/Build.bat     (Windows)
```

## Why

Cross-platform C, C++, and native-extension projects have solved this problem
forever by hand-maintaining a `Makefile` *and* a separate Windows batch/nmake
script side by side. They drift. Someone adds a step on Linux, forgets Windows,
and the Windows build silently breaks. `buildgen` makes the manifest the single
source of truth and generates both scripts from it every time.

## Install

```bash
git clone https://github.com/<you>/buildgen.git
cd buildgen
pip install -e .
```

## Quick start

Write a `build.yaml`:

```yaml
project:
  name: my-app
  version: "1.0.0"

steps:
  configure:
    unix: ["./configure --prefix=/usr/local"]
    windows: ["cmake -G \"NMake Makefiles\" ."]
  build:
    unix: ["make -j4"]
    windows: ["nmake"]
  test:
    unix: ["make test"]
    windows: ["nmake test"]
  install:
    unix: ["make install"]
    windows: ["nmake install"]
```

Generate the platform build scripts:

```bash
buildgen build.yaml
```

This writes:

```
Makefile
mswin32/Build.bat
```

Then build the same way on either platform:

```bash
# Unix
make configure && make build && make test

# Windows
mswin32\Build.bat configure
mswin32\Build.bat build
mswin32\Build.bat test
```

Or run everything in one shot: `make` / `mswin32\Build.bat` (defaults to `all`,
which runs `configure` then `build`).

## Working example

[`examples/example_project`](examples/example_project) is a complete, runnable
example — a tiny Python "build" that writes an artifact and a pytest test that
verifies it. It's regenerated and actually executed on every CI run, on
**Linux, macOS, and Windows**, so the badge above isn't just testing the
generator in isolation — it's proof the generated scripts really build
something on every target platform.

Try it yourself:

```bash
buildgen examples/example_project/build.yaml -o examples/example_project
cd examples/example_project
make configure && make build && make test      # Unix
:: or on Windows:
mswin32\Build.bat configure && mswin32\Build.bat build && mswin32\Build.bat test
```

## How it works

- `src/buildgen/generator.py` — parses the YAML manifest into a `BuildManifest`
  and renders it through Jinja2 templates into real scripts.
- `src/buildgen/templates/Makefile.j2` — Unix Makefile template with
  `configure` / `build` / `test` / `install` phony targets.
- `src/buildgen/templates/Build.bat.j2` — Windows batch template using
  labeled subroutines (`call :build`, `errorlevel` checks) so failures stop
  the build instead of silently continuing, just like `make`'s default
  fail-fast behavior.
- `src/buildgen/cli.py` — the `buildgen` command.

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Project layout

```
buildgen/
├── src/buildgen/
│   ├── cli.py
│   ├── generator.py
│   └── templates/
│       ├── Makefile.j2
│       └── Build.bat.j2
├── examples/example_project/
│   ├── build.yaml
│   ├── build_hello.py
│   └── test_hello.py
├── tests/
│   └── test_generator.py
└── .github/workflows/ci.yml
```

## License

MIT — see [LICENSE](LICENSE).
