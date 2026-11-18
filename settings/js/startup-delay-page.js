(function (ui) {
  const MIN_DELAY_SECONDS = 1;
  const MAX_DELAY_SECONDS = 600;
  const SAVE_DELAY_MILLISECONDS = 800;

  const delayRow = document.getElementById("startup-delay-row");
  const secondsInput = document.getElementById("startup-delay-seconds");
  let enabledSwitch = null;
  let saveTimer = null;

  function describeDelay(settings) {
    if (!settings.startup_delay_enabled) return ui.translate("start.immediate");
    return ui.translate("start.waits", { seconds: settings.startup_delay_seconds });
  }

  function updateMenuSubtitle(settings) {
    ui.menu.setSubtitle("menu-startup-subtitle", describeDelay(settings));
  }

  function fillFromSettings() {
    const settings = ui.settingsState.get();
    if (!settings) return;
    ui.setSwitchChecked(enabledSwitch, settings.startup_delay_enabled);
    secondsInput.value = settings.startup_delay_seconds;
    delayRow.hidden = !settings.startup_delay_enabled;
  }

  function isValidDelay(seconds) {
    return Number.isInteger(seconds) && seconds >= MIN_DELAY_SECONDS && seconds <= MAX_DELAY_SECONDS;
  }

  async function saveStartupDelay() {
    const seconds = Number(secondsInput.value);
    if (!isValidDelay(seconds)) {
      ui.toast.showError(ui.translate("startup.invalid"));
      return;
    }
    ui.toast.showSaving();
    try {
      const body = { enabled: ui.isSwitchChecked(enabledSwitch), seconds: seconds };
      ui.settingsState.set(await ui.callApi("PUT", "/settings/startup-delay", body));
      ui.toast.showSaved();
    } catch (error) {
      ui.toast.showError(ui.describeError(error));
    }
  }

  function scheduleSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveStartupDelay, SAVE_DELAY_MILLISECONDS);
  }

  function createEnabledSwitch() {
    return ui.createSwitch({
      label: ui.translate("startup.wait"),
      checked: false,
      onToggle: function (isEnabled) {
        delayRow.hidden = !isEnabled;
        saveStartupDelay();
      },
    });
  }

  ui.startupDelayPage = {
    start: function () {
      enabledSwitch = createEnabledSwitch();
      document.getElementById("startup-delay-switch-slot").append(enabledSwitch);
      secondsInput.addEventListener("input", scheduleSave);
      ui.settingsState.onChange(updateMenuSubtitle);
      ui.settingsState.onChange(fillFromSettings);
    },
    onShow: fillFromSettings,
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
