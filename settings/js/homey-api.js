(function (ui) {
  let homeyInstance = null;

  function extractErrorMessage(error) {
    if (error && error.message) return error.message;
    if (typeof error === "string") return error;
    return "";
  }

  ui.setApiHomey = function (homey) {
    homeyInstance = homey;
  };

  ui.callApi = function (method, path, body) {
    return new Promise(function (resolve, reject) {
      homeyInstance.api(method, path, body, function (error, result) {
        if (error) {
          reject(error);
        } else {
          resolve(result);
        }
      });
    });
  };

  ui.describeError = function (error) {
    const message = extractErrorMessage(error);
    if (ui.hasTranslation("errors." + message)) {
      return ui.translate("errors." + message);
    }
    return message || ui.translate("toast.error");
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
