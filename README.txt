Homeykit makes your Homey devices available in Apple HomeKit. It runs a HomeKit bridge inside Homey, so the devices you choose show up in the Home app on your iPhone, iPad and Mac, and you can control them with Siri, widgets and HomeKit automations.

How it works
Homeykit runs completely on your Homey and your local network. Nothing is sent to the cloud. The bridge is paired once with the Home app, after which Homey devices appear as HomeKit accessories. A change in the Home app is sent straight to Homey, and changes made in Homey are passed on to HomeKit within a few seconds.

Getting started
1. Open the settings of this app. The first page shows a QR code and a setup code.
2. In the Home app on your iPhone tap +, choose Add Accessory and scan the QR code (or choose More options and enter the code).
3. Back in the app settings, open Devices and switch on the devices that should be visible in HomeKit.

Supported devices
- Lights: on/off, dimming and color temperature
- Sockets and switches: on/off
- Sensors: temperature, humidity, motion, contact (doors and windows) and water leak

Other device types, such as thermostats, TVs, speakers and buttons, are not supported yet. They are shown as "Not supported" in the device list.

Settings
- Devices: choose which devices are visible in HomeKit. You can search and filter on active, inactive and not supported devices.
- Name: change the name of the bridge, or restore the default name (the name of your Homey). A new name restarts the bridge briefly.
- Pincode: the pairing code is chosen randomly on first start and stays the same afterwards. You can set your own code or generate a new random one. Existing pairings keep working.
- Startup: optionally wait a number of seconds after the app starts before the bridge starts, so Homey can load all devices first. This is off by default.

Good to know
- The Home app only offers pairing when the bridge is not paired yet. To pair again, first remove the bridge from the Home app.
- Control from outside your home network needs a home hub in your Home app (an Apple TV or HomePod).
- If you remove the app from Homey, the pairing and your selection are removed as well, and you need to pair again.
- This is a test version. Please report problems and ideas.
