from montageai.embed import save_artifact


def test_save_artifact(tmp_path) -> None:  # type: ignore[no-untyped-def]
    out = save_artifact("<html></html>", tmp_path / "artifact.html")
    assert out.read_text(encoding="utf-8") == "<html></html>"

