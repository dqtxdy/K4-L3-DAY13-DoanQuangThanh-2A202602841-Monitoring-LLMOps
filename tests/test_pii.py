from app.pii import scrub_text, scrub_value


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_cccd_and_payment_card_without_breaking_normal_text() -> None:
    out = scrub_text("CCCD 012345678901; card 4111 1111 1111 1111; order 12345")
    assert "012345678901" not in out
    assert "4111 1111 1111 1111" not in out
    assert "REDACTED_CCCD" in out
    assert "REDACTED_CREDIT_CARD" in out
    assert "order 12345" in out


def test_scrub_nested_structured_values() -> None:
    value = {"context": [{"email": "nested@example.com"}], "message": "Call 0901234567"}
    redacted = scrub_value(value)
    assert "nested@example.com" not in str(redacted)
    assert "0901234567" not in str(redacted)
    assert "REDACTED_EMAIL" in str(redacted)
    assert "REDACTED_PHONE_VN" in str(redacted)
