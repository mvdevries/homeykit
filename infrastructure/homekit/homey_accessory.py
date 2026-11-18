from collections.abc import Callable
from typing import Any

from pyhap.accessory import Accessory
from pyhap.accessory_driver import AccessoryDriver
from pyhap.characteristic import Characteristic
from pyhap.const import CATEGORY_OTHER
from pyhap.service import Service

from ...application.background_tasks import TaskSet
from ...application.error_logging import run_logging_errors
from ...application.log_function import LogFunction
from ...domain.defaults import ACCESSORY_NAME_MAX_LENGTH
from ...domain.homey_device import HomeyDevice
from ..gateways.homey_devices_gateway import HomeyDevicesGateway
from .service_profiles import CapabilityBinding, ServiceProfile
from .value_conversions import Converter

type CapabilityWrittenCallback = Callable[[str], None]


class HomeyAccessory(Accessory):
    def __init__(
        self,
        *,
        driver: AccessoryDriver,
        device: HomeyDevice,
        profiles: tuple[ServiceProfile, ...],
        devices_gateway: HomeyDevicesGateway,
        accessory_id: int,
        log: LogFunction,
        on_capability_written: CapabilityWrittenCallback,
    ) -> None:
        super().__init__(
            driver, device.name[:ACCESSORY_NAME_MAX_LENGTH], aid=accessory_id
        )
        self.category = self._choose_category(profiles)
        self.homey_device = device
        self._devices_gateway = devices_gateway
        self._log = log
        self._on_capability_written = on_capability_written
        self._characteristics_by_capability: dict[
            str, list[tuple[Characteristic, Converter]]
        ] = {}
        self._pending_writes = TaskSet()
        self._configure_information_service(device)
        self._add_services_from_profiles(profiles)
        self.update_from_device(device)

    @staticmethod
    def _choose_category(profiles: tuple[ServiceProfile, ...]) -> int:
        return profiles[0].category if profiles else CATEGORY_OTHER

    def _configure_information_service(self, device: HomeyDevice) -> None:
        self.set_info_service(
            manufacturer="Homey",
            model=device.effective_class,
            serial_number=device.id,
        )

    def _add_services_from_profiles(self, profiles: tuple[ServiceProfile, ...]) -> None:
        for profile in profiles:
            self._add_service_from_profile(profile)

    def _add_service_from_profile(self, profile: ServiceProfile) -> None:
        service = self.add_preload_service(
            profile.service_name, chars=profile.optional_characteristics
        )
        for binding in profile.bindings:
            self._configure_binding_characteristic(service, binding)

    def _configure_binding_characteristic(
        self, service: Service, binding: CapabilityBinding
    ) -> None:
        setter = self._create_setter(binding) if binding.to_homey else None
        characteristic = service.configure_char(
            binding.characteristic_name,
            properties=binding.characteristic_properties,
            setter_callback=setter,
        )
        self._characteristics_by_capability.setdefault(
            binding.capability_id, []
        ).append((characteristic, binding.to_homekit))

    def _create_setter(self, binding: CapabilityBinding) -> Callable[[Any], None]:
        def set_value_from_homekit(value: Any) -> None:
            self._start_capability_write(binding, value)

        return set_value_from_homekit

    def _start_capability_write(self, binding: CapabilityBinding, value: Any) -> None:
        self._pending_writes.start(self._write_capability(binding, value))

    async def _write_capability(self, binding: CapabilityBinding, value: Any) -> None:
        was_written = await run_logging_errors(
            self._log,
            f"Writing to '{self.homey_device.name}' failed",
            lambda: self._write_to_homey(binding, value),
        )
        if was_written:
            self._on_capability_written(self.homey_device.id)

    async def _write_to_homey(self, binding: CapabilityBinding, value: Any) -> bool:
        assert binding.to_homey is not None
        await self._write_prerequisite_capabilities(binding)
        await self._devices_gateway.set_capability_value(
            self.homey_device.id, binding.capability_id, binding.to_homey(value)
        )
        return True

    async def _write_prerequisite_capabilities(
        self, binding: CapabilityBinding
    ) -> None:
        for capability_id, fixed_value in binding.capabilities_to_set_first:
            if self.homey_device.has_capability(capability_id):
                await self._devices_gateway.set_capability_value(
                    self.homey_device.id, capability_id, fixed_value
                )

    def update_from_device(self, device: HomeyDevice) -> None:
        self.homey_device = device
        for (
            capability_id,
            characteristics,
        ) in self._characteristics_by_capability.items():
            self._update_characteristics_for_capability(
                device, capability_id, characteristics
            )

    def _update_characteristics_for_capability(
        self,
        device: HomeyDevice,
        capability_id: str,
        characteristics: list[tuple[Characteristic, Converter]],
    ) -> None:
        capability = device.capabilities.get(capability_id)
        if capability is None or capability.value is None:
            return
        for characteristic, to_homekit in characteristics:
            self._set_characteristic_value(
                device, capability_id, characteristic, to_homekit(capability.value)
            )

    def _set_characteristic_value(
        self,
        device: HomeyDevice,
        capability_id: str,
        characteristic: Characteristic,
        value: Any,
    ) -> None:
        try:
            characteristic.set_value(value)
        except ValueError as error:
            self._log(
                f"Value of '{device.name}' ({capability_id}) is not usable: {error}"
            )

    async def cancel_pending_writes(self) -> None:
        await self._pending_writes.cancel_all()
