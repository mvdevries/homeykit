(function (ui) {
  const pagesByHash = {};

  function getCurrentHash() {
    const hash = window.location.hash;
    return pagesByHash[hash] ? hash : "";
  }

  function showOnlyPage(currentHash) {
    Object.keys(pagesByHash).forEach(function (hash) {
      document.getElementById(pagesByHash[hash].elementId).hidden = hash !== currentHash;
    });
  }

  function notifyPageShown(currentHash) {
    const onShow = pagesByHash[currentHash].onShow;
    if (onShow) onShow();
  }

  function showCurrentPage() {
    const currentHash = getCurrentHash();
    showOnlyPage(currentHash);
    window.scrollTo(0, 0);
    notifyPageShown(currentHash);
  }

  ui.router = {
    registerPage: function (hash, elementId, onShow) {
      pagesByHash[hash] = { elementId: elementId, onShow: onShow };
    },
    start: function () {
      window.addEventListener("hashchange", showCurrentPage);
      showCurrentPage();
    },
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
