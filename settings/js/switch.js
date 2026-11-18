(function (ui) {
  function isDisabled(switchElement) {
    return switchElement.getAttribute("aria-disabled") === "true";
  }

  ui.isSwitchChecked = function (switchElement) {
    return switchElement.getAttribute("aria-checked") === "true";
  };

  ui.setSwitchChecked = function (switchElement, isChecked) {
    switchElement.setAttribute("aria-checked", String(isChecked));
  };

  function configureSwitchAttributes(switchElement, options) {
    switchElement.setAttribute("role", "switch");
    switchElement.setAttribute("aria-label", options.label);
    switchElement.setAttribute("aria-disabled", String(Boolean(options.disabled)));
    switchElement.tabIndex = options.disabled ? -1 : 0;
    ui.setSwitchChecked(switchElement, Boolean(options.checked));
  }

  function addTrack(switchElement) {
    const track = document.createElement("span");
    track.className = "switch-track";
    switchElement.append(track);
  }

  function toggleAndNotify(switchElement, onToggle) {
    if (isDisabled(switchElement)) return;
    const newValue = !ui.isSwitchChecked(switchElement);
    ui.setSwitchChecked(switchElement, newValue);
    onToggle(newValue);
  }

  ui.createSwitch = function (options) {
    const switchElement = document.createElement("span");
    switchElement.className = "switch";
    configureSwitchAttributes(switchElement, options);
    addTrack(switchElement);
    ui.activateOnClickOrKey(switchElement, function () {
      toggleAndNotify(switchElement, options.onToggle);
    });
    return switchElement;
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
