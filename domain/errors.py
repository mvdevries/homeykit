BRIDGE_NAME_TOO_LONG = "bridge_name_too_long"
STARTUP_DELAY_OUT_OF_RANGE = "startup_delay_out_of_range"
PINCODE_INVALID_FORMAT = "pincode_invalid_format"
PINCODE_TOO_SIMPLE = "pincode_too_simple"


class SettingsValidationError(ValueError):
    def __init__(self, error_code: str) -> None:
        super().__init__(error_code)
        self.error_code = error_code
