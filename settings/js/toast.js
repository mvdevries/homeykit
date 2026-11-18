(function (ui) {
  const SAVED_DURATION_MILLISECONDS = 1800;
  const ERROR_DURATION_MILLISECONDS = 3500;

  const toastElement = document.getElementById("toast");
  let hideTimer = null;

  function show(text, kind, durationMilliseconds) {
    clearTimeout(hideTimer);
    toastElement.textContent = text;
    toastElement.className = "toast " + kind;
    toastElement.hidden = false;
    if (durationMilliseconds) {
      hideTimer = setTimeout(function () {
        toastElement.hidden = true;
      }, durationMilliseconds);
    }
  }

  ui.toast = {
    showSaving: function () {
      show(ui.translate("toast.saving"), "saving", 0);
    },
    showSaved: function (text) {
      show(text || ui.translate("toast.saved"), "saved", SAVED_DURATION_MILLISECONDS);
    },
    showError: function (text) {
      show(text, "error", ERROR_DURATION_MILLISECONDS);
    },
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
