import base36
import segno

HOMEKIT_IP_PAIRING_FLAG = 2
SETUP_URI_PREFIX = "X-HM://"
SETUP_PAYLOAD_LENGTH = 9
QR_CODE_SCALE = 6
QR_CODE_BORDER = 2


def parse_pincode_digits(pincode: bytes) -> int:
    digits_only = pincode.replace(b"-", b"")
    return int(digits_only, 10) & 0x7FFFFFFF


def build_setup_payload(category: int, pincode: bytes) -> int:
    category_bits = (category & 0xFF) << 31
    flag_bits = HOMEKIT_IP_PAIRING_FLAG << 27
    return category_bits | flag_bits | parse_pincode_digits(pincode)


def encode_setup_payload(payload: int) -> str:
    return base36.dumps(payload).upper().rjust(SETUP_PAYLOAD_LENGTH, "0")


def build_setup_uri(category: int, pincode: bytes, setup_id: str) -> str:
    payload = build_setup_payload(category, pincode)
    return SETUP_URI_PREFIX + encode_setup_payload(payload) + setup_id


def build_qr_code_svg(setup_uri: str) -> str:
    qr_code = segno.make(setup_uri, error="m")
    return qr_code.svg_inline(scale=QR_CODE_SCALE, border=QR_CODE_BORDER)
