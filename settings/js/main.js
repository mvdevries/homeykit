window.onHomeyReady = function (homey) {
  const ui = window.HomeykitUi;
  ui.setHomey(homey);
  ui.setApiHomey(homey);
  ui.translateStaticElements();
  ui.router.registerPage("", "page-start");
  ui.router.registerPage("#devices", "page-devices");
  ui.devicesPage.start();
  ui.pairingPage.start();
  ui.router.start();
  homey.ready();
};
