from ...domain.homey_device import HomeyDevice
from .service_profiles import is_device_supported


class HomeKitDeviceSupport:
    def is_supported(self, device: HomeyDevice) -> bool:
        return is_device_supported(device)
