from homey import app

from .services.service_container import ServiceContainer, build_service_container


class App(app.App):
    services: ServiceContainer | None = None

    async def on_init(self) -> None:
        self.services = build_service_container(
            settings=self.homey.settings, log=self.log
        )
        await self.services.bridge_supervisor.start()

    async def on_uninit(self) -> None:
        if self.services is None:
            return
        await self.services.bridge_supervisor.shutdown()
        self.services = None


homey_export = App
