(function (ui) {
  const nameInput = document.getElementById("bridge-name-input");
  const defaultNameText = document.getElementById("bridge-name-default");

  function updateMenuSubtitle(settings) {
    ui.menu.setSubtitle("menu-name-subtitle", settings.bridge_name);
  }

  function fillFromSettings() {
    const settings = ui.settingsState.get();
    if (!settings) return;
    nameInput.value = settings.bridge_name;
    defaultNameText.textContent = ui.translate("bridgeName.default", {
      name: settings.default_bridge_name,
    });
  }

  async function saveBridgeName(bridgeName) {
    ui.toast.showSaving();
    try {
      ui.settingsState.set(
        await ui.callApi("PUT", "/settings/bridge-name", { bridge_name: bridgeName }),
      );
      fillFromSettings();
      ui.toast.showSaved();
      ui.pairingPage.refresh();
    } catch (error) {
      ui.toast.showError(ui.describeError(error));
    }
  }

  ui.bridgeNamePage = {
    start: function () {
      nameInput.placeholder = ui.translate("bridgeName.placeholder");
      ui.settingsState.onChange(updateMenuSubtitle);
      ui.settingsState.onChange(fillFromSettings);
      ui.activateOnClickOrKey(document.getElementById("bridge-name-save"), function () {
        saveBridgeName(nameInput.value);
      });
      ui.activateOnClickOrKey(document.getElementById("bridge-name-restore"), function () {
        saveBridgeName(null);
      });
    },
    onShow: fillFromSettings,
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
