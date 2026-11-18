import base36
from homeykit.homekit import setup_uri

BRIDGE_CATEGORY = 2


def test_parse_pincode_digits_ignores_dashes():
    assert setup_uri.parse_pincode_digits(b"031-45-154") == 3145154


def test_payload_contains_category_flag_and_pincode():
    payload = setup_uri.build_setup_payload(BRIDGE_CATEGORY, b"031-45-154")
    assert payload & 0x7FFFFFF == 3145154
    assert (payload >> 27) & 0xF == setup_uri.HOMEKIT_IP_PAIRING_FLAG
    assert payload >> 31 == BRIDGE_CATEGORY


def test_uri_has_prefix_padded_payload_and_setup_id():
    uri = setup_uri.build_setup_uri(BRIDGE_CATEGORY, b"031-45-154", "AB12")
    assert uri.startswith("X-HM://")
    assert uri.endswith("AB12")
    encoded = uri.removeprefix("X-HM://").removesuffix("AB12")
    assert len(encoded) == setup_uri.SETUP_PAYLOAD_LENGTH
    assert base36.loads(encoded) == setup_uri.build_setup_payload(
        BRIDGE_CATEGORY, b"031-45-154"
    )


def test_qr_code_is_an_inline_svg():
    svg = setup_uri.build_qr_code_svg("X-HM://0023ISYE5AB12")
    assert svg.startswith("<svg")
