import pathlib

import pytest

from buildgen.generator import BuildManifest, BuildScriptGenerator

MANIFEST_YAML = """
project:
  name: sample-project
  version: "2.3.1"

steps:
  configure:
    unix: ["./configure --prefix=/usr/local"]
    windows: ["cmake -G \\"NMake Makefiles\\" ."]
  build:
    unix: ["make -j4"]
    windows: ["nmake"]
  test:
    unix: ["make test"]
    windows: ["nmake test"]
"""


@pytest.fixture()
def manifest(tmp_path: pathlib.Path) -> BuildManifest:
    manifest_path = tmp_path / "build.yaml"
    manifest_path.write_text(MANIFEST_YAML)
    return BuildManifest.from_yaml(manifest_path)


def test_parses_project_metadata(manifest: BuildManifest):
    assert manifest.name == "sample-project"
    assert manifest.version == "2.3.1"


def test_commands_for_returns_expected_list(manifest: BuildManifest):
    assert manifest.commands_for("build", "unix") == ["make -j4"]
    assert manifest.commands_for("build", "windows") == ["nmake"]


def test_commands_for_missing_step_is_empty(manifest: BuildManifest):
    assert manifest.commands_for("install", "unix") == []


def test_missing_project_name_raises(tmp_path: pathlib.Path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("project:\n  version: '1.0'\n")
    with pytest.raises(ValueError):
        BuildManifest.from_yaml(bad)


def test_render_makefile_contains_unix_commands(manifest: BuildManifest):
    generator = BuildScriptGenerator(manifest)
    makefile = generator.render_makefile()
    assert "./configure --prefix=/usr/local" in makefile
    assert "make -j4" in makefile
    assert "nmake" not in makefile  # windows-only command must not leak in


def test_render_build_bat_contains_windows_commands(manifest: BuildManifest):
    generator = BuildScriptGenerator(manifest)
    build_bat = generator.render_build_bat()
    assert "nmake" in build_bat
    assert "nmake test" in build_bat
    assert "./configure" not in build_bat  # unix-only command must not leak in


def test_write_creates_expected_files(manifest: BuildManifest, tmp_path: pathlib.Path):
    out_dir = tmp_path / "out"
    generator = BuildScriptGenerator(manifest)
    written = generator.write(out_dir)

    makefile_path = out_dir / "Makefile"
    build_bat_path = out_dir / "mswin32" / "Build.bat"

    assert makefile_path in written
    assert build_bat_path in written
    assert makefile_path.exists()
    assert build_bat_path.exists()

    # Build.bat should use CRLF line endings.
    raw = build_bat_path.read_bytes()
    assert b"\r\n" in raw


def test_write_is_idempotent(manifest: BuildManifest, tmp_path: pathlib.Path):
    out_dir = tmp_path / "out"
    generator = BuildScriptGenerator(manifest)
    first = generator.write(out_dir)
    second = generator.write(out_dir)
    assert [p.read_text(errors="ignore") for p in first] == [
        p.read_text(errors="ignore") for p in second
    ]
