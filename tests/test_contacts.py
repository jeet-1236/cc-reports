"""The CRM contact-intake validation rule (commandcenter/contacts.py).

`validate_contact` returns the list of fields that failed, so `[]` means "saved". The cases below are the
book of record the CRM actually holds: domestic US numbers alongside international ones, and names carrying
the apostrophes, hyphens and accents that real customer names carry.
"""
from commandcenter.contacts import validate_contact


def test_a_plain_us_contact_is_accepted():
    assert validate_contact({"name": "Dana White", "phone": "555-018-2231"}) == []


def test_an_international_number_is_accepted():
    """E.164 with a country code and spaces — how the CRM stores every non-US number."""
    assert validate_contact({"name": "Siobhan Brennan", "phone": "+44 20 7946 0958"}) == []


def test_a_name_with_an_apostrophe_or_hyphen_is_accepted():
    assert validate_contact({"name": "Siobhán O'Brien", "phone": "+353 1 437 2100"}) == []
    assert validate_contact({"name": "Anne-Marie Dubois", "phone": "+33 1 42 68 53 00"}) == []


def test_an_accented_name_is_accepted():
    assert validate_contact({"name": "José Álvarez", "phone": "(212) 555-0147"}) == []


def test_a_missing_name_is_rejected():
    assert validate_contact({"name": "", "phone": "555-018-2231"}) == ["name"]


def test_a_name_containing_digits_is_rejected():
    assert validate_contact({"name": "R2D2", "phone": "555-018-2231"}) == ["name"]


def test_a_number_that_is_too_short_is_rejected():
    assert validate_contact({"name": "Dana White", "phone": "12345"}) == ["phone"]


def test_text_in_the_phone_field_is_rejected():
    assert validate_contact({"name": "Dana White", "phone": "call the switchboard"}) == ["phone"]


def test_both_bad_fields_are_reported_together():
    """The form marks every bad field at once — a rep should not have to submit twice to find both."""
    assert validate_contact({"name": "", "phone": ""}) == ["name", "phone"]
