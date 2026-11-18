from homey import app

from .services.service_container import ServiceContainer, build_service_container
from .storage.legacy_settings_migration import LegacySettingsMigration


class App(app.App):
    services: ServiceContainer | None = None

    async def on_init(self) -> None:
        await LegacySettingsMigration(self.homey.settings).migrate_all_legacy_keys()
        self.services = build_service_container(
            settings=self.homey.settings,
            token_source=self.homey.api,
            log=self.log,
        )
        self.services.address_watchdog.start()
        await self.services.bridge_supervisor.start()

    async def on_uninit(self) -> None:
        if self.services is None:
            return
        await self.services.address_watchdog.stop()
        await self.services.bridge_supervisor.shutdown()
        await self.services.close_connections()
        self.services = None


homey_export = App
