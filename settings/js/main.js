window.onHomeyReady = function (homey) {
  const ui = window.HomeykitUi;
  ui.setHomey(homey);
  ui.setApiHomey(homey);
  ui.translateStaticElements();
  ui.router.registerPage("", "page-start");
  ui.router.registerPage("#devices", "page-devices");
  ui.router.registerPage("#name", "page-name", ui.bridgeNamePage.onShow);
  ui.router.registerPage("#pincode", "page-pincode", ui.pincodePage.onShow);
  ui.router.registerPage("#startup", "page-startup", ui.startupDelayPage.onShow);
  ui.devicesPage.start();
  ui.bridgeNamePage.start();
  ui.pincodePage.start();
  ui.startupDelayPage.start();
  ui.pairingPage.start();
  ui.router.start();
  ui.settingsState.load();
  homey.ready();
};
