(function (ui) {
  const changeListeners = [];
  let currentSettings = null;

  function notifyListeners() {
    changeListeners.forEach(function (listener) {
      listener(currentSettings);
    });
  }

  ui.settingsState = {
    get: function () {
      return currentSettings;
    },
    set: function (settings) {
      currentSettings = settings;
      notifyListeners();
    },
    onChange: function (listener) {
      changeListeners.push(listener);
    },
    load: async function () {
      try {
        ui.settingsState.set(await ui.callApi("GET", "/settings", null));
      } catch (error) {
        ui.toast.showError(ui.translate("start.settingsFailed"));
      }
    },
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
