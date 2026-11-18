from homey import app


class App(app.App):
    async def on_init(self) -> None:
        self.log("Homeykit initialized")


homey_export = App
