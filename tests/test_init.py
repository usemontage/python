from montageai import Montage, MontageAsync


def test_public_api() -> None:
    mtg = Montage(api_key="mtg_test_sk_xxx")
    assert hasattr(mtg, "generate")
    assert hasattr(mtg, "agenerate")
    assert hasattr(mtg, "stream")
    assert hasattr(mtg, "artifacts")
    assert hasattr(mtg, "adapters")
    assert hasattr(mtg, "components")
    assert hasattr(MontageAsync(api_key="mtg_test_sk_xxx"), "generate")

