(function (ui) {
  let homeyInstance = null;

  ui.setHomey = function (homey) {
    homeyInstance = homey;
  };

  ui.translate = function (key, tokens) {
    return homeyInstance.__("settings." + key, tokens);
  };

  ui.hasTranslation = function (key) {
    const fullKey = "settings." + key;
    const text = homeyInstance.__(fullKey);
    return typeof text === "string" && text !== "" && text !== fullKey;
  };

  ui.translateStaticElements = function () {
    document.querySelectorAll("[data-i18n]").forEach(function (element) {
      element.textContent = homeyInstance.__(element.getAttribute("data-i18n"));
    });
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
