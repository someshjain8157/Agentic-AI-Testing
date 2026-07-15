from app.observability import (
    audit_payload,
    hash_text,
    safe_preview,
)


def test_safe_preview_redacts_sensitive_patterns():
    text = "Email me at student@example.com or +1 (555) 123-4567 about the lesson plan."

    preview = safe_preview(text, max_length=120)

    assert "[REDACTED_EMAIL]" in preview
    assert "[REDACTED_PHONE]" in preview


def test_hash_text_is_deterministic():
    assert hash_text("hello world") == hash_text("hello world")


def test_audit_payload_defaults_to_metadata_only():
    payload = audit_payload(
        request_id="req-123",
        question="Explain photosynthesis",
        subject="SCIENCE",
        request_type="normal",
        model="phi3:mini",
        citations=[{"subject": "SCIENCE", "chapter": "chapter1", "page": 12}],
        answer="Plants use sunlight.",
    )

    assert payload["request_id"] == "req-123"
    assert payload["question_hash"]
    assert payload["answer_hash"]
    assert payload["citation_count"] == 1
    assert "question" not in payload
    assert "answer" not in payload
