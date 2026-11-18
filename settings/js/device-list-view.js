(function (ui) {
  function createEmptyState(title, text) {
    const emptyState = document.createElement("div");
    emptyState.className = "empty-state";
    const titleElement = document.createElement("p");
    titleElement.className = "empty-title";
    titleElement.textContent = title;
    const textElement = document.createElement("p");
    textElement.className = "empty-text";
    textElement.textContent = text;
    emptyState.append(titleElement, textElement);
    return emptyState;
  }

  function buildRowClassName(device) {
    const classNames = ["device-row"];
    if (!device.supported) classNames.push("unsupported");
    if (device.exposed) classNames.push("exposed");
    return classNames.join(" ");
  }

  function buildZoneText(device) {
    const zoneText = ui.devicesState.getZoneDisplayText(device);
    if (device.supported) return zoneText;
    return zoneText + " · " + ui.translate("devices.unsupported");
  }

  function createDeviceText(device) {
    const textElement = document.createElement("span");
    textElement.className = "device-text";
    const nameElement = document.createElement("span");
    nameElement.className = "device-name";
    nameElement.textContent = device.name;
    const zoneElement = document.createElement("span");
    zoneElement.className = "device-zone";
    zoneElement.textContent = buildZoneText(device);
    textElement.append(nameElement, zoneElement);
    return textElement;
  }

  function createExposureSwitch(device, rowElement, onExposedChanged) {
    return ui.createSwitch({
      label: device.name,
      checked: device.exposed,
      disabled: !device.supported,
      onToggle: function (isExposed) {
        device.exposed = isExposed;
        rowElement.classList.toggle("exposed", isExposed);
        onExposedChanged();
      },
    });
  }

  function createDeviceRow(device, onExposedChanged) {
    const rowElement = document.createElement("div");
    rowElement.className = buildRowClassName(device);
    rowElement.append(
      ui.createDeviceIcon(device, ui.devicesState.getIcons()),
      createDeviceText(device),
      createExposureSwitch(device, rowElement, onExposedChanged),
    );
    return rowElement;
  }

  function createNoFilterState() {
    return createEmptyState(
      ui.translate("devices.noFilterTitle"),
      ui.translate("devices.noFilterText"),
    );
  }

  function createNoResultsState() {
    return createEmptyState(
      ui.translate("devices.noResultsTitle"),
      ui.translate("devices.noResultsText"),
    );
  }

  ui.deviceListView = {
    render: function (listElement, onExposedChanged) {
      listElement.replaceChildren();
      if (!ui.devicesState.hasSelectedFilters()) {
        listElement.append(createNoFilterState());
        return;
      }
      const visibleDevices = ui.devicesState.getVisibleDevices();
      if (visibleDevices.length === 0) {
        listElement.append(createNoResultsState());
        return;
      }
      visibleDevices.forEach(function (device) {
        listElement.append(createDeviceRow(device, onExposedChanged));
      });
    },
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
