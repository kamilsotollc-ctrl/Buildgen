"""buildgen: generate platform-specific build scripts from one manifest.

Public API:
    BuildManifest          - parsed representation of a build.yaml manifest
    BuildScriptGenerator   - renders and writes Makefile / mswin32/Build.bat
"""

from .generator import BuildManifest, BuildScriptGenerator

__version__ = "0.1.0"
__all__ = ["BuildManifest", "BuildScriptGenerator", "__version__"]
