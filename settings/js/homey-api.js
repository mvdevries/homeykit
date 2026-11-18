(function (ui) {
  let homeyInstance = null;

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
})((window.HomeykitUi = window.HomeykitUi || {}));
