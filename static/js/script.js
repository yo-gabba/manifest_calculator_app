
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