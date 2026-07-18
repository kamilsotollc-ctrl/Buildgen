"""Stand-in 'compiler' step for the example project.

Writes build/hello.txt, proving the generated Makefile / Build.bat actually
executed real, platform-independent Python -- not just echoed text.
"""

import pathlib

OUTPUT = pathlib.Path("build") / "hello.txt"


def main() -> None:
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text("Hello from buildgen! This file was produced by the generated build script.\n")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
