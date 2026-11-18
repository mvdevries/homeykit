window.onHomeyReady = function (homey) {
  const ui = window.HomeykitUi;
  ui.setHomey(homey);
  ui.setApiHomey(homey);
  ui.translateStaticElements();
  ui.pairingPage.start();
  homey.ready();
};
