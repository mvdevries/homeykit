(function (ui) {
  const KNOWN_ERROR_CODES = [
    "bridge_name_too_long",
    "startup_delay_out_of_range",
    "pincode_invalid_format",
    "pincode_too_simple",
  ];

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
    if (KNOWN_ERROR_CODES.indexOf(message) !== -1) {
      return ui.translate("errors." + message);
    }
    return message || ui.translate("toast.error");
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
