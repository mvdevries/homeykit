(function (ui) {
  const PINCODE_DIGIT_COUNT = 8;

  const currentPincode = document.getElementById("pincode-current");
  const pincodeInput = document.getElementById("pincode-input");

  function formatPincodeInput(text) {
    const digits = text.replace(/\D/g, "").slice(0, PINCODE_DIGIT_COUNT);
    const groups = [digits.slice(0, 3), digits.slice(3, 5), digits.slice(5, 8)];
    return groups
      .filter(function (group) {
        return group.length > 0;
      })
      .join("-");
  }

  function updateMenuSubtitle(settings) {
    ui.menu.setSubtitle("menu-pincode-subtitle", settings.pincode || "");
  }

  function fillFromSettings() {
    const settings = ui.settingsState.get();
    if (!settings) return;
    currentPincode.textContent = settings.pincode || "";
    pincodeInput.value = "";
    pincodeInput.placeholder = ui.translate("pincode.placeholder");
  }

  async function savePincode(pincode) {
    ui.toast.showSaving();
    try {
      ui.settingsState.set(await ui.callApi("PUT", "/settings/pincode", { pincode: pincode }));
      fillFromSettings();
      ui.toast.showSaved(ui.translate("pincode.updated"));
      ui.pairingPage.refresh();
    } catch (error) {
      ui.toast.showError(ui.describeError(error));
    }
  }

  ui.pincodePage = {
    start: function () {
      ui.settingsState.onChange(updateMenuSubtitle);
      ui.settingsState.onChange(fillFromSettings);
      pincodeInput.addEventListener("input", function () {
        pincodeInput.value = formatPincodeInput(pincodeInput.value);
      });
      ui.activateOnClickOrKey(document.getElementById("pincode-save"), function () {
        savePincode(pincodeInput.value);
      });
      ui.activateOnClickOrKey(document.getElementById("pincode-random"), function () {
        savePincode(null);
      });
    },
    onShow: fillFromSettings,
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
