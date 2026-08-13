"""The POST /api/notes request handler (commandcenter/intake.py).

The contract is narrow and the whole point of it is the failure mode: a request the handler cannot use comes
back as a 400 naming the field to fix. It never comes back as a 500, and it never raises — a raise IS the
500, and a 500 tells the caller "our fault, retry", which is wrong twice over for a malformed request.
"""
from commandcenter.intake import MAX_NOTE, handle_note


def test_a_normal_note_is_accepted():
    status, body = handle_note({"ticket_id": "TCK-4471", "notes": "customer called back"})
    assert status == 201
    assert body["ticket_id"] == "TCK-4471"
    assert body["notes"] == "customer called back"


def test_an_omitted_note_is_accepted_as_empty():
    status, body = handle_note({"ticket_id": "TCK-4471"})
    assert (status, body["notes"]) == (201, "")


def test_an_explicit_json_null_note_is_accepted_as_empty():
    """Every form binding sends `null` for an empty text box — it means the same as omitting the key."""
    status, body = handle_note({"ticket_id": "TCK-4471", "notes": None})
    assert (status, body["notes"]) == (201, "")


def test_surrounding_whitespace_is_trimmed():
    status, body = handle_note({"ticket_id": "TCK-4471", "notes": "  spaced  "})
    assert (status, body["notes"]) == (201, "spaced")


def test_a_missing_ticket_id_is_a_400():
    status, body = handle_note({"notes": "orphan note"})
    assert status == 400
    assert "ticket_id" in body["error"]


def test_a_missing_ticket_id_with_a_null_note_is_still_a_400():
    """The two bad things arrive together in the wild. The answer is still the client-facing 400."""
    status, body = handle_note({"notes": None})
    assert status == 400
    assert "ticket_id" in body["error"]


def test_an_over_long_note_is_a_400():
    status, body = handle_note({"ticket_id": "TCK-4471", "notes": "x" * (MAX_NOTE + 1)})
    assert status == 400
    assert str(MAX_NOTE) in body["error"]


def test_the_handler_never_raises_on_any_of_these_bodies():
    """The single property that matters: nothing a client can send turns into a 500."""
    for payload in ({}, {"notes": None}, {"ticket_id": None, "notes": None},
                    {"ticket_id": "TCK-1", "notes": None}, {"ticket_id": "TCK-1"}):
        status, _ = handle_note(payload)
        assert status in (201, 400)
