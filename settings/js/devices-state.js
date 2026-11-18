(function (ui) {
  const FILTER_RULES = {
    active: function (device) {
      return device.supported && device.exposed;
    },
    inactive: function (device) {
      return device.supported && !device.exposed;
    },
    unsupported: function (device) {
      return !device.supported;
    },
  };

  const filterStates = { active: true, inactive: true, unsupported: false };
  let devices = [];
  let iconsById = {};
  let searchText = "";

  function getSelectedFilterNames() {
    return Object.keys(filterStates).filter(function (name) {
      return filterStates[name];
    });
  }

  function matchesAnySelectedFilter(device) {
    return getSelectedFilterNames().some(function (name) {
      return FILTER_RULES[name](device);
    });
  }

  function getZoneDisplayText(device) {
    return device.zone || ui.translate("devices.noZone");
  }

  function matchesSearchText(device) {
    const term = searchText.trim().toLowerCase();
    if (!term) return true;
    return (
      device.name.toLowerCase().includes(term) ||
      getZoneDisplayText(device).toLowerCase().includes(term)
    );
  }

  ui.devicesState = {
    setDevices: function (newDevices) {
      devices = newDevices;
    },
    setIcons: function (newIcons) {
      iconsById = newIcons;
    },
    getIcons: function () {
      return iconsById;
    },
    setSearchText: function (text) {
      searchText = text;
    },
    toggleFilter: function (name) {
      filterStates[name] = !filterStates[name];
    },
    isFilterSelected: function (name) {
      return filterStates[name];
    },
    hasSelectedFilters: function () {
      return getSelectedFilterNames().length > 0;
    },
    getZoneDisplayText: getZoneDisplayText,
    getVisibleDevices: function () {
      return devices.filter(function (device) {
        return matchesSearchText(device) && matchesAnySelectedFilter(device);
      });
    },
    getSupportedDevices: function () {
      return devices.filter(function (device) {
        return device.supported;
      });
    },
    getExposedDevices: function () {
      return devices.filter(function (device) {
        return device.supported && device.exposed;
      });
    },
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
