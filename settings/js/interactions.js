(function (ui) {
  const ACTIVATION_KEYS = ["Enter", " "];

  function isActivationKey(event) {
    return ACTIVATION_KEYS.indexOf(event.key) !== -1;
  }

  ui.activateOnClickOrKey = function (element, action) {
    element.addEventListener("click", action);
    element.addEventListener("keydown", function (event) {
      if (isActivationKey(event)) {
        event.preventDefault();
        action();
      }
    });
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
