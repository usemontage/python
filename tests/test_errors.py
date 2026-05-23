from montageai.errors import MontageApiError, MontageAuthError, MontageRateLimitError


def test_api_error() -> None:
    err = MontageApiError(message="Not found", status=404, code="not_found")
    assert err.status == 404
    assert err.code == "not_found"
    assert "Not found" in str(err)


def test_auth_error_is_api_error() -> None:
    err = MontageAuthError()
    assert isinstance(err, MontageApiError)
    assert err.status == 401


def test_rate_limit_error() -> None:
    err = MontageRateLimitError(retry_after=30)
    assert isinstance(err, MontageApiError)
    assert err.status == 429
    assert err.retry_after == 30

