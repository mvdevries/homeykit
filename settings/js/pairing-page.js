(function (ui) {
  const REFRESH_INTERVAL_MILLISECONDS = 5000;

  const startMessage = document.getElementById("start-message");
  const pairingSection = document.getElementById("pairing-section");
  const pairedBadge = document.getElementById("paired-badge");
  const alreadyPairedText = document.getElementById("already-paired-text");
  const pairingSteps = document.getElementById("pairing-steps");
  const qrCode = document.getElementById("qr-code");
  const pincodeDisplay = document.getElementById("pincode-display");

  function showMessage(text) {
    startMessage.textContent = text;
    startMessage.hidden = false;
    pairingSection.hidden = true;
  }

  function showPairingSection() {
    startMessage.hidden = true;
    pairingSection.hidden = false;
  }

  function showPairingState(isPaired) {
    pairedBadge.hidden = !isPaired;
    alreadyPairedText.hidden = !isPaired;
    pairingSteps.hidden = isPaired;
  }

  function showPairingInfo(pairingInfo) {
    qrCode.innerHTML = pairingInfo.qr_svg;
    pincodeDisplay.textContent = pairingInfo.pincode;
    showPairingState(pairingInfo.paired);
    showPairingSection();
  }

  function describeNotStarted(pairingInfo) {
    const secondsUntilStart = pairingInfo.seconds_until_start;
    if (secondsUntilStart === null || secondsUntilStart === undefined) {
      return ui.translate("pairing.notStarted");
    }
    return ui.translate("pairing.startsIn", { seconds: secondsUntilStart });
  }

  function showPairingInfoOrNotStarted(pairingInfo) {
    if (pairingInfo.available) {
      showPairingInfo(pairingInfo);
    } else {
      showMessage(describeNotStarted(pairingInfo));
    }
  }

  async function refreshPairingInfo() {
    try {
      showPairingInfoOrNotStarted(await ui.callApi("GET", "/pairing", null));
    } catch (error) {
      showMessage(ui.translate("pairing.loadFailed"));
    }
  }

  ui.pairingPage = {
    refresh: refreshPairingInfo,
    start: function () {
      refreshPairingInfo();
      setInterval(refreshPairingInfo, REFRESH_INTERVAL_MILLISECONDS);
    },
  };
})(window.HomeykitUi);
