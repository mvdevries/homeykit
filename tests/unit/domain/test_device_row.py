from homeykit.domain.device_row import DeviceRow


class TestDeviceRow:
    def test_given_a_row_when_converted_to_a_payload_then_public_field_names_are_used(
        self,
    ):
        row = DeviceRow("id-1", "Lamp", "Kitchen", "light", "icon-1", True, False)

        payload = row.to_payload()

        assert payload == {
            "id": "id-1",
            "name": "Lamp",
            "zone": "Kitchen",
            "device_class": "light",
            "icon_id": "icon-1",
            "supported": True,
            "exposed": False,
        }
