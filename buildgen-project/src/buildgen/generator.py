"""Core generation logic for buildgen.

A build.yaml manifest declares, per build phase (configure/build/test/install),
the shell commands to run on Unix-like systems and on Windows. This module
turns that single source of truth into two real, runnable build scripts:

    Makefile            - for macOS / Linux / BSD (make configure|build|test|install)
    mswin32/Build.bat   - for Windows (Build.bat configure|build|test|install)

The mswin32/ subdirectory convention mirrors how several long-lived
cross-platform C/Perl-style projects keep their Windows build entry point
separate from the Unix Makefile at the project root.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass, field
from typing import Dict, List

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = pathlib.Path(__file__).parent / "templates"

STEP_NAMES = ("configure", "build", "test", "install")


@dataclass
class BuildManifest:
    """Parsed representation of a build.yaml manifest."""

    name: str
    version: str
    steps: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: pathlib.Path) -> "BuildManifest":
        data = yaml.safe_load(path.read_text()) or {}
        project = data.get("project", {})
        steps = data.get("steps", {})

        if "name" not in project:
            raise ValueError(f"manifest {path} is missing required 'project.name'")

        return cls(
            name=str(project["name"]),
            version=str(project.get("version", "0.0.0")),
            steps=steps,
        )

    def commands_for(self, step: str, platform: str) -> List[str]:
        """Return the ordered command list for a given step + platform.

        platform is either "unix" or "windows". Missing steps/platforms
        simply produce an empty (no-op) list rather than raising, so a
        manifest only needs to declare the phases it actually uses.
        """
        return list(self.steps.get(step, {}).get(platform, []))


class BuildScriptGenerator:
    """Renders a BuildManifest into real, runnable build scripts."""

    def __init__(self, manifest: BuildManifest):
        self.manifest = manifest
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(disabled_extensions=("j2",)),
        )

    def _context(self, platform: str) -> dict:
        return {step: self.manifest.commands_for(step, platform) for step in STEP_NAMES}

    def render_makefile(self) -> str:
        template = self.env.get_template("Makefile.j2")
        return template.render(**self._context("unix"))

    def render_build_bat(self) -> str:
        template = self.env.get_template("Build.bat.j2")
        return template.render(**self._context("windows"))

    def write(self, output_dir: pathlib.Path) -> List[pathlib.Path]:
        """Write Makefile and mswin32/Build.bat under output_dir.

        Returns the list of paths that were written.
        """
        output_dir = pathlib.Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        written: List[pathlib.Path] = []

        makefile_path = output_dir / "Makefile"
        makefile_path.write_text(self.render_makefile(), newline="\n")
        written.append(makefile_path)

        win_dir = output_dir / "mswin32"
        win_dir.mkdir(exist_ok=True)
        build_bat_path = win_dir / "Build.bat"
        # Windows batch files are happiest with CRLF line endings.
        build_bat_path.write_text(self.render_build_bat().replace("\n", "\r\n"))
        written.append(build_bat_path)

        return written
