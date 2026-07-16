import pathlib


def test_build_artifact_exists():
    artifact = pathlib.Path("build") / "hello.txt"
    assert artifact.exists(), "build_hello.py should have created build/hello.txt"
    assert "buildgen" in artifact.read_text()
