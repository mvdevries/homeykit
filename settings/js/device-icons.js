(function (ui) {
  const FALLBACK_ICON_PATHS = {
    light: '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
    socket: '<path d="M12 22v-5M9 8V2M15 8V2M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8z"/>',
    thermostat: '<path d="M14 4v10.5a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0z"/>',
    sensor: '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    speaker: '<rect x="4" y="2" width="16" height="20" rx="2"/><circle cx="12" cy="14" r="4"/><path d="M12 6h.01"/>',
    tv: '<rect x="2" y="7" width="20" height="15" rx="2"/><path d="m17 2-5 5-5-5"/>',
    remote: '<rect x="7" y="2" width="10" height="20" rx="3"/><circle cx="12" cy="8" r="1.5"/><path d="M12 14h.01M12 18h.01"/>',
    networkrouter: '<rect x="2" y="14" width="20" height="8" rx="2"/><path d="M6 18h.01M10 18h.01M15 10v4M17.8 7.2a4 4 0 0 0-5.6 0M20.7 4.3a8 8 0 0 0-11.4 0"/>',
    toggle: '<rect x="2" y="6" width="20" height="12" rx="6"/><circle cx="16" cy="12" r="2"/>',
    generic: '<path d="M21 8l-9-5-9 5v8l9 5 9-5V8z"/><path d="M3.3 7 12 12l8.7-5M12 22V12"/>',
  };
  const TOGGLE_DEVICE_CLASSES = ["other", "switch"];

  function pickFallbackPath(deviceClass) {
    if (TOGGLE_DEVICE_CLASSES.indexOf(deviceClass) !== -1) return FALLBACK_ICON_PATHS.toggle;
    return FALLBACK_ICON_PATHS[deviceClass] || FALLBACK_ICON_PATHS.generic;
  }

  function createFallbackSvgMarkup(deviceClass) {
    return (
      '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" ' +
      'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      pickFallbackPath(deviceClass) +
      "</svg>"
    );
  }

  function createMaskedIcon(dataUri) {
    const mask = document.createElement("span");
    mask.className = "device-icon-mask";
    mask.style.setProperty("--icon-image", 'url("' + dataUri + '")');
    return mask;
  }

  ui.createDeviceIcon = function (device, iconsById) {
    const iconElement = document.createElement("span");
    iconElement.className = "device-icon";
    const dataUri = device.icon_id ? iconsById[device.icon_id] : null;
    if (dataUri) {
      iconElement.append(createMaskedIcon(dataUri));
    } else {
      iconElement.innerHTML = createFallbackSvgMarkup(device.device_class);
    }
    return iconElement;
  };
})((window.HomeykitUi = window.HomeykitUi || {}));
