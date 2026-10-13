from app.core.rate_limit import RateLimiter


def test_rate_limiter_blocks_after_limit_in_memory() -> None:
    limiter = RateLimiter()
    first = limiter.allow("otp:test:phone", limit=2, window_seconds=60)
    second = limiter.allow("otp:test:phone", limit=2, window_seconds=60)
    third = limiter.allow("otp:test:phone", limit=2, window_seconds=60)

    assert first.allowed is True
    assert second.allowed is True
    assert third.allowed is False
    assert third.count == 3
