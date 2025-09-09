
document.addEventListener('DOMContentLoaded', () => {
    const zipInput = document.querySelector('input[name="zip_code"]');
    const milesInput = document.querySelector('input[name="miles"]');
    const zoneInput = document.querySelector('input[name="zone"]');

    zipInput.addEventListener('blur', async () => {
        const zip = zipInput.value.trim();
        if (zip) {
            const response = await fetch(`/zip_lookup/${zip}`);
            const data = await response.json();

            if (data.miles && data.zone) {
                milesInput.value = data.miles;
                zoneInput.value = data.zone;
                milesInput.readOnly = true;
                zoneInput.readOnly = true;

                // Flash message
                const flash = document.createElement('div');
                flash.textContent = 'Miles and zone auto-filled from database';
                flash.className = 'flash-message';
                zipInput.parentElement.insertBefore(flash, zipInput.nextSibling);

                // Remove flash after 3 seconds
                setTimeout(() => flash.remove(), 3000);
            } else {
                milesInput.value = '';
                zoneInput.value = '';
                milesInput.readOnly = false;
                zoneInput.readOnly = false;
            }
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
  const zipInput = document.getElementById("stop-zip");
  const milesInput = document.getElementById("stop-miles");
  const palletsInput = document.getElementById("stop-pallets");
  const palletSpacesInput = document.getElementById("stop-pallet-spaces");
  const accessorialsInput = document.getElementById("stop-accessorials");

  const previewTotal = document.getElementById("preview-total");
  const previewRate = document.getElementById("preview-rate");
  const previewZone = document.getElementById("preview-zone");

  // Mirror your backend rate tables
  const STOP_RATES = {
    A: 11.11, B: 12.37, C: 13.38, D: 14.39,
    E: 17.42, F: 19.44, G: 21.46, H: 23.48,
    I: 25.50, J: 27.52
  };

  const PALLET_RATES = {
    A: 9.09, B: 9.34, C: 9.34, D: 9.34,
    E: 11.36, F: 11.36, G: 11.36, H: 11.36,
    I: 11.36, J: 11.36
  };

  const ACCESSORIAL_RATES = {
    Liftgate: 20.0,
    Residential: 15.0,
    "Inside Delivery": 25.0
  };

  // Watch zip input for lookup
  zipInput.addEventListener("blur", function () {
    const zip = zipInput.value.trim();
    if (!zip) return;

    fetch(`/zip_lookup/${zip}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.miles) {
          milesInput.value = data.miles;
          previewZone.textContent = data.zone || "-";
          updatePreview();
        }
      })
      .catch((err) => console.error("ZIP lookup failed", err));
  });

  // Update preview on input changes
  [milesInput, palletsInput, palletSpacesInput, accessorialsInput].forEach((el) => {
    el.addEventListener("input", updatePreview);
  });

  function updatePreview() {
    const miles = parseFloat(milesInput.value) || 0;
    const palletSpaces = parseFloat(palletSpacesInput.value) || 0;
    const accessorials = accessorialsInput.value.toLowerCase();

    // Determine zone from miles
    let zone = previewZone.textContent !== "-" ? previewZone.textContent : getZone(miles);
    if (!zone) {
      previewZone.textContent = "-";
      previewRate.textContent = "0.00";
      previewTotal.textContent = "0.00";
      return;
    }

    const freightTotal = (STOP_RATES[zone] || 0) + (PALLET_RATES[zone] || 0) * palletSpaces;

    let accessorialTotal = 0;
    for (const [key, val] of Object.entries(ACCESSORIAL_RATES)) {
      if (accessorials.includes(key.toLowerCase())) {
        accessorialTotal += val;
      }
    }

    const total = freightTotal + accessorialTotal;

    previewZone.textContent = zone;
    previewRate.textContent = freightTotal.toFixed(2);
    previewTotal.textContent = total.toFixed(2);
  }

  // Helper: match backend zone ranges
  function getZone(miles) {
    if (miles >= 0 && miles <= 20) return "A";
    if (miles <= 30) return "B";
    if (miles <= 40) return "C";
    if (miles <= 60) return "D";
    if (miles <= 80) return "E";
    if (miles <= 100) return "F";
    if (miles <= 120) return "G";
    if (miles <= 140) return "H";
    if (miles <= 160) return "I";
    if (miles <= 500) return "J";
    return null;
  }
});
