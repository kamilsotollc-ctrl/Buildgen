# LinkedIn post draft

---

**Option A — short, punchy**

Cross-platform build tooling has a recurring problem: your Makefile and your
Windows build script drift apart. Someone updates the Linux build steps,
forgets Windows, and the Windows build quietly breaks.

I built **buildgen** to fix that: one YAML manifest → a real Makefile *and* a
real `mswin32/Build.bat`, generated together, every time. No drift possible,
because there's only one source of truth.

The repo's CI actually proves it works — it regenerates the scripts and runs
them for real on Linux, macOS, and Windows runners on every push.

🔗 [link to repo]

#buildautomation #devtools #python #softwareengineering #opensource

---

**Option B — a bit more technical detail, good if your audience is engineers**

Most cross-platform native projects hand-maintain two build systems: a
Makefile for Unix and a batch script / nmake file for Windows. They inevitably
fall out of sync.

I built **buildgen**, a small Python CLI that generates both from a single
declarative manifest:

```yaml
steps:
  build:
    unix: ["make -j4"]
    windows: ["nmake"]
```

→ `buildgen build.yaml` produces a working `Makefile` and `mswin32/Build.bat`
with matching configure/build/test/install targets, fail-fast error handling
on both platforms, and zero duplication of intent.

What I'm most proud of isn't the generator itself — it's the CI. The example
project isn't just unit-tested in isolation; the GitHub Actions workflow
regenerates the build scripts and actually runs `make` on Linux/macOS and
`Build.bat` on Windows on every commit. If the generated scripts ever broke on
a real platform, CI would catch it immediately.

Built with Python, Jinja2, and a healthy respect for how much pain Windows
batch scripting can cause. 😄

🔗 [link to repo]

#buildautomation #devtools #python #ci #softwareengineering

---

## Notes for you before posting

1. Push this to a public GitHub repo, then swap in the real link.
2. The CI badge is genuinely meaningful here — once you push, GitHub Actions
   will run the matrix (Ubuntu/macOS/Windows) automatically. Consider adding
   a badge to the top of README.md once it's green:
   `![CI](https://github.com/<you>/buildgen/actions/workflows/ci.yml/badge.svg)`
3. If you want a screenshot for the post, a good one is the green CI checks
   showing all three OSes passing — that's the visual proof of the "actually
   works cross-platform" claim.
