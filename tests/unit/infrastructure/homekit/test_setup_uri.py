import base36
from homeykit.infrastructure.homekit import setup_uri

BRIDGE_CATEGORY = 2
PINCODE = b"031-45-154"


class TestParsePincodeDigits:
    def test_given_a_pincode_with_dashes_when_parsed_then_the_dashes_are_ignored(self):
        digits = setup_uri.parse_pincode_digits(PINCODE)

        assert digits == 3145154


class TestBuildSetupPayload:
    def test_given_a_category_and_pincode_when_built_then_all_parts_are_in_the_payload(
        self,
    ):
        payload = setup_uri.build_setup_payload(BRIDGE_CATEGORY, PINCODE)

        assert payload & 0x7FFFFFF == 3145154
        assert (payload >> 27) & 0xF == setup_uri.HOMEKIT_IP_PAIRING_FLAG
        assert payload >> 31 == BRIDGE_CATEGORY


class TestBuildSetupUri:
    def test_given_a_setup_id_when_built_then_the_uri_has_prefix_payload_and_setup_id(
        self,
    ):
        uri = setup_uri.build_setup_uri(BRIDGE_CATEGORY, PINCODE, "AB12")

        encoded = uri.removeprefix("X-HM://").removesuffix("AB12")
        assert uri.startswith("X-HM://")
        assert uri.endswith("AB12")
        assert len(encoded) == setup_uri.SETUP_PAYLOAD_LENGTH
        assert base36.loads(encoded) == setup_uri.build_setup_payload(
            BRIDGE_CATEGORY, PINCODE
        )


class TestBuildQrCodeSvg:
    def test_given_a_setup_uri_when_rendered_then_an_inline_svg_is_returned(self):
        svg = setup_uri.build_qr_code_svg("X-HM://0023ISYE5AB12")

        assert svg.startswith("<svg")
