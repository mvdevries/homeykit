(function (ui) {
  const SAVE_DELAY_MILLISECONDS = 500;
  const ICON_RETRY_DELAY_MILLISECONDS = 4000;
  const MAX_ICON_RETRIES = 6;
  const FILTER_BUTTON_IDS = {
    active: "filter-active",
    inactive: "filter-inactive",
    unsupported: "filter-unsupported",
  };

  const searchInput = document.getElementById("device-search");
  const deviceList = document.getElementById("device-list");
  const deviceSummary = document.getElementById("device-summary");
  let saveTimer = null;

  function buildExposedCountText() {
    return ui.translate("devices.exposedCount", {
      count: ui.devicesState.getExposedDevices().length,
      total: ui.devicesState.getSupportedDevices().length,
    });
  }

  function updateSummaryTexts() {
    const exposedCountText = buildExposedCountText();
    deviceSummary.textContent = exposedCountText;
    const hasExposedDevices = ui.devicesState.getExposedDevices().length > 0;
    ui.menu.setSubtitle(
      "menu-devices-subtitle",
      hasExposedDevices ? exposedCountText : ui.translate("devices.noneExposed"),
    );
  }

  function renderDeviceList() {
    ui.deviceListView.render(deviceList, handleExposedChanged);
    updateSummaryTexts();
  }

  function refreshFilterButtons() {
    Object.keys(FILTER_BUTTON_IDS).forEach(function (filterName) {
      document
        .getElementById(FILTER_BUTTON_IDS[filterName])
        .setAttribute("aria-pressed", String(ui.devicesState.isFilterSelected(filterName)));
    });
  }

  function handleFilterClicked(filterName) {
    ui.devicesState.toggleFilter(filterName);
    refreshFilterButtons();
    renderDeviceList();
  }

  function handleExposedChanged() {
    updateSummaryTexts();
    scheduleSave();
  }

  function scheduleSave() {
    ui.toast.showSaving();
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveExposedDevices, SAVE_DELAY_MILLISECONDS);
  }

  function getExposedDeviceIds() {
    return ui.devicesState.getExposedDevices().map(function (device) {
      return device.id;
    });
  }

  async function saveExposedDevices() {
    await ui.saveWithToast(
      function () {
        return ui.callApi("PUT", "/devices/exposed", {
          exposed_device_ids: getExposedDeviceIds(),
        });
      },
      { errorText: ui.translate("toast.saveFailed"), onError: loadDevices },
    );
  }

  async function loadDevices() {
    try {
      const response = await ui.callApi("GET", "/devices", null);
      ui.devicesState.setDevices(response.devices);
      renderDeviceList();
    } catch (error) {
      ui.menu.setSubtitle("menu-devices-subtitle", ui.translate("devices.loadFailed"));
      ui.toast.showError(ui.translate("devices.loadFailed"));
    }
  }

  function scheduleIconRetry(attemptNumber) {
    if (attemptNumber >= MAX_ICON_RETRIES) return;
    setTimeout(function () {
      loadIcons(attemptNumber + 1);
    }, ICON_RETRY_DELAY_MILLISECONDS);
  }

  async function loadIcons(attemptNumber) {
    try {
      const response = await ui.callApi("GET", "/icons", null);
      ui.devicesState.setIcons(response.icons || {});
      renderDeviceList();
      if (response.missing_count > 0) scheduleIconRetry(attemptNumber);
    } catch (error) {
      scheduleIconRetry(attemptNumber);
    }
  }

  function bindSearch() {
    searchInput.placeholder = ui.translate("devices.search");
    searchInput.addEventListener("input", function () {
      ui.devicesState.setSearchText(searchInput.value);
      renderDeviceList();
    });
  }

  function bindFilterButtons() {
    Object.keys(FILTER_BUTTON_IDS).forEach(function (filterName) {
      ui.activateOnClickOrKey(document.getElementById(FILTER_BUTTON_IDS[filterName]), function () {
        handleFilterClicked(filterName);
      });
    });
  }

  ui.devicesPage = {
    start: function () {
      bindSearch();
      bindFilterButtons();
      refreshFilterButtons();
      loadDevices().then(function () {
        loadIcons(0);
      });
    },
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
