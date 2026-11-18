(function (ui) {
  ui.menu = {
    setSubtitle: function (elementId, text) {
      document.getElementById(elementId).textContent = text;
    },
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
