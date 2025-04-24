function formatNumber(input) {
    let value = input.value.replace(/\D/g, '');
    if (value) {
        value = parseInt(value).toLocaleString('en-US');
    }
    input.value = value;
}

function parseFormattedNumber(formattedNumber) {
    return parseInt(formattedNumber.replace(/\D/g, '')) || 0;
}

function calculateQarz() {
    const totalAmount = parseFormattedNumber(document.getElementById('id_summasi').value);
    const cash = parseFormattedNumber(document.getElementById('naqd').value);
    const bankAccount = parseFormattedNumber(document.getElementById('bank_schot').value);
    
    if (totalAmount === 0 || isNaN(totalAmount)) {
        document.getElementById('karta').value = '';
        return;
    }
    
    const totalPayments = cash + bankAccount;
    if (totalPayments > totalAmount) {
        showToast("To'lovlar umumiy summadan oshib ketdi!", "error");
            document.getElementById('naqd').value = '0';
            document.getElementById('bank_schot').value = '0';
        document.getElementById('karta').value = '';
        return;
    }
    
    const debt = totalAmount - totalPayments;
    document.getElementById('karta').value = debt.toLocaleString('en-US');
}

function updateGpsOptions() {
    const gpsSelects = document.querySelectorAll('.gps-select');
    const selectedValues = Array.from(gpsSelects)
        .map(select => select.value)
        .filter(value => value !== '');
    
    gpsSelects.forEach(select => {
        const currentValue = select.value;
        Array.from(select.options).forEach(option => {
            if (option.value === '') return; // Skip placeholder option
            if (option.value === currentValue) {
                option.disabled = false;
    } else {
                option.disabled = selectedValues.includes(option.value);
            }
        });
        
        // Refresh Select2 to reflect changes
        $(select).trigger('change.select2');
    });
}

function addGpsField() {
    const container = document.querySelector('.gps-fields');
    const newField = document.createElement('div');
    newField.className = 'gps-field card bg-base-200';
    newField.style.opacity = '0';
    newField.style.transform = 'translateY(20px)';
    
    // Get all already selected GPS values to exclude them
    const gpsSelects = document.querySelectorAll('.gps-select');
    const selectedValues = Array.from(gpsSelects)
        .map(select => select.value)
        .filter(value => value !== '');
    
    // Get available options from first select (excluding already selected ones)
    const firstSelect = document.querySelector('.gps-select');
    let optionsHTML = '<option value="">GPS tanlang</option>';
    
    if (firstSelect) {
        Array.from(firstSelect.options)
            .filter(option => option.value !== '' && !selectedValues.includes(option.value))
            .forEach(option => {
                optionsHTML += `<option value="${option.value}">${option.textContent}</option>`;
            });
    }
    
    newField.innerHTML = `
        <div class="card-body">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="form-control">
                    <label class="label">
                        <span class="label-text font-medium">GPS ID</span>
                    </label>
                    <div class="input-group">
                        <span class="btn btn-square btn-ghost">
                            <i class="fas fa-satellite text-gray-400"></i>
                        </span>
                        <select name="gps_id" class="gps-select select-bordered w-full" required onchange="updateGpsOptions()">
                            ${optionsHTML}
                        </select>
                    </div>
                </div>
                <div class="form-control">
                    <label class="label">
                        <span class="label-text font-medium">SIM karta</span>
                    </label>
                    <div class="input-group">
                        <span class="btn btn-square btn-ghost">
                            <i class="fas fa-sim-card text-gray-400"></i>
                        </span>
                        <input type="text" name="sim_karta" class="input input-bordered w-full" required>
                    </div>
                </div>
                <div class="form-control">
                    <label class="label">
                        <span class="label-text font-medium">Mashina turi</span>
                    </label>
                    <div class="input-group">
                        <span class="btn btn-square btn-ghost">
                            <i class="fas fa-car text-gray-400"></i>
                        </span>
                        <input type="text" name="mashina_turi" class="input input-bordered w-full" required placeholder="Masalan: Cobalt">
                    </div>
                </div>
                <div class="form-control">
                    <label class="label">
                        <span class="label-text font-medium">Davlat raqami</span>
                    </label>
                    <div class="input-group">
                        <span class="btn btn-square btn-ghost">
                            <i class="fas fa-hashtag text-gray-400"></i>
                        </span>
                        <input type="text" name="davlat_raqami" class="input input-bordered w-full" required placeholder="Masalan: 01A777AA">
                    </div>
                </div>
            </div>
            <div class="card-actions justify-end mt-4">
                <button type="button" onclick="removeGpsField(this)" class="btn btn-error gap-2">
                    <i class="fas fa-trash-alt"></i>
                    O'chirish
                </button>
            </div>
        </div>
    `;
    
    container.appendChild(newField);
    
    // Initialize Select2 for the new field
    $(newField).find('.gps-select').select2({
        theme: 'bootstrap-5',
        width: '100%',
        placeholder: 'GPS tanlang',
        allowClear: true,
        language: {
            noResults: function() {
                return "Natija topilmadi";
            },
            searching: function() {
                return "Qidirilmoqda...";
            }
        }
    });
    
    // Animate the new field
    setTimeout(() => {
        newField.style.transition = 'all 0.3s ease-out';
        newField.style.opacity = '1';
        newField.style.transform = 'translateY(0)';
    }, 10);
    
    updateGpsOptions();
}

function removeGpsField(button) {
    const field = button.closest('.gps-field');
    field.style.transition = 'all 0.3s ease-out';
    field.style.opacity = '0';
    field.style.transform = 'translateY(-20px)';
    
    setTimeout(() => {
        // Destroy Select2 before removing the element
        $(field).find('.gps-select').select2('destroy');
        field.remove();
        updateGpsOptions();
    }, 300);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Format number inputs
    const numberInputs = document.querySelectorAll('input[type="text"]');
    numberInputs.forEach(input => {
        if (input.id !== 'karta') { // Skip readonly debt field
            formatNumber(input);
        }
    });
    
    // Set up event listeners
    document.querySelector('form').addEventListener('submit', function(e) {
        const gpsFields = document.querySelectorAll('.gps-field');
        if (gpsFields.length === 0) {
            e.preventDefault();
            showToast("Kamida bitta GPS qurilma qo'shishingiz kerak!", "error");
            return;
        }
        
        // Validate GPS selections
        let hasValidGps = false;
        gpsFields.forEach(field => {
            const select = field.querySelector('.gps-select');
            if (select.value) {
                hasValidGps = true;
            }
        });
        
        if (!hasValidGps) {
            e.preventDefault();
            showToast("Kamida bitta GPS qurilmani tanlashingiz kerak!", "error");
            return;
        }
    });
    
    // Initial calculations
    calculateQarz();
    updateGpsOptions();
});

