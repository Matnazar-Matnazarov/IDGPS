// Show toast message
function showToast(message, type = "info") {
    // Check if toast function exists
    if (window.Toastify) {
        Toastify({
            text: message,
            duration: 3000,
            close: true,
            gravity: "top",
            position: "center",
            backgroundColor: type === "error" ? "#F87272" : "#36D399",
            stopOnFocus: true
        }).showToast();
    } else {
        // Fallback to alert
        alert(message);
    }
}

// Format GPS option for Select2
function formatGpsOption(gps) {
    if (!gps.id) return gps.text;
    return '<div class="flex items-center gap-2">' +
           '<i class="fas fa-satellite text-primary"></i>' +
           '<span>' + gps.text + '</span>' +
           '</div>';
}

function formatNumber(input) {
    if (!input) return;
    let value = input.value.replace(/\D/g, '');
    if (value) {
        value = parseInt(value).toLocaleString('en-US');
    }
    input.value = value;
}

function parseFormattedNumber(formattedNumber) {
    if (!formattedNumber) return 0;
    return parseInt(formattedNumber.replace(/\D/g, '')) || 0;
}

function calculateQarz() {
    try {
        const summasi = document.getElementById('id_summasi');
        const naqd = document.getElementById('id_naqd');
        const bank_schot = document.getElementById('id_bank_schot');
        const karta = document.getElementById('id_karta');
        
        if (!summasi || !naqd || !bank_schot || !karta) {
            console.error('Required fields not found for calculateQarz');
            console.log('Looking for: id_summasi, id_naqd, id_bank_schot, id_karta');
            return;
        }
        
        const totalAmount = parseFormattedNumber(summasi.value);
        const cash = parseFormattedNumber(naqd.value);
        const bankAccount = parseFormattedNumber(bank_schot.value);
        
        if (totalAmount === 0 || isNaN(totalAmount)) {
            karta.value = '';
            return;
        }
        
        const totalPayments = cash + bankAccount;
        if (totalPayments > totalAmount) {
            showToast("To'lovlar umumiy summadan oshib ketdi!", "error");
            naqd.value = '0';
            bank_schot.value = '0';
            karta.value = '';
            return;
        }
        
        const debt = totalAmount - totalPayments;
        karta.value = debt.toLocaleString('en-US');
    } catch (error) {
        console.error('Error in calculateQarz:', error);
    }
}

// Flag to prevent recursive updating
let isUpdatingGpsOptions = false;

function updateGpsOptions() {
    try {
        // Prevent recursive updates
        if (isUpdatingGpsOptions) {
            return;
        }
        
        isUpdatingGpsOptions = true;
        
        const gpsSelects = document.querySelectorAll('.gps-select');
        if (!gpsSelects || gpsSelects.length === 0) {
            isUpdatingGpsOptions = false;
            return;
        }
        
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
        });
        
        // Manually update the UI without triggering change event
        if (window.jQuery) {
            $('.gps-select').each(function() {
                if ($(this).data('select2')) {
                    // Update UI without triggering events
                    $(this).select2('destroy');
                    $(this).select2({
                        theme: 'bootstrap-5',
                        width: '100%',
                        placeholder: 'GPS tanlang',
                        allowClear: false,
                        templateResult: formatGpsOption,
                        templateSelection: formatGpsOption,
                        escapeMarkup: function(m) { return m; }
                    });
                }
            });
        }
        
        isUpdatingGpsOptions = false;
    } catch (error) {
        isUpdatingGpsOptions = false;
        console.error('Error in updateGpsOptions:', error);
    }
}

function addGpsField() {
    try {
        const container = document.querySelector('.gps-fields');
        if (!container) {
            console.error('GPS fields container not found');
            return;
        }
        
        const newField = document.createElement('div');
        newField.className = 'gps-field card bg-base-200';
        newField.style.opacity = '0';
        newField.style.transform = 'translateY(20px)';
        
        // Get available GPS options
        let optionsHTML = '<option value="">GPS tanlang</option>';
        
        // Check if there are already GPS selects
        const gpsSelects = document.querySelectorAll('.gps-select');
        const selectedValues = Array.from(gpsSelects)
            .map(select => select.value)
            .filter(value => value !== '');
        
        // Find a select with options to use as a template
        const firstSelect = document.querySelector('.gps-select');
        
        if (firstSelect && firstSelect.options && firstSelect.options.length > 0) {
            // Copy options from existing select
            Array.from(firstSelect.options).forEach(option => {
                if (option.value !== '' && !selectedValues.includes(option.value)) {
                    optionsHTML += `<option value="${option.value}">${option.textContent}</option>`;
                }
            });
        } else {
            // If no existing select with options, try to find available GPSs from a different source
            const mavjudGpslar = document.querySelectorAll('#mavjud_gpslar option');
            if (mavjudGpslar && mavjudGpslar.length > 0) {
                Array.from(mavjudGpslar).forEach(option => {
                    if (option.value !== '' && !selectedValues.includes(option.value)) {
                        optionsHTML += `<option value="${option.value}">${option.textContent}</option>`;
                    }
                });
            } else {
                // Fallback - try to get GPS options from a different field
                const allSelects = document.querySelectorAll('select');
                for (const select of allSelects) {
                    if (select.name === 'gps_id' || select.id === 'id_gps_id' || select.classList.contains('gps-select')) {
                        Array.from(select.options).forEach(option => {
                            if (option.value !== '' && !selectedValues.includes(option.value)) {
                                optionsHTML += `<option value="${option.value}">${option.textContent}</option>`;
                            }
                        });
                        break;
                    }
                }
            }
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
                            <select name="gps_id" class="gps-select select select-bordered w-full" required>
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
        
        // Initialize Select2 if available
        if (window.jQuery && $.fn.select2) {
            const newSelect = newField.querySelector('.gps-select');
            if (newSelect) {
                $(newSelect).select2({
                    theme: 'bootstrap-5',
                    width: '100%',
                    placeholder: 'GPS tanlang',
                    allowClear: false,
                    templateResult: formatGpsOption,
                    templateSelection: formatGpsOption,
                    escapeMarkup: function(m) { return m; }
                });
                
                // After initializing Select2, add change handler
                $(newSelect).on('change', function() {
                    // Update options but in a safe way, without causing infinite loops
                    setTimeout(updateGpsOptions, 10);
                });
                
                // Load options via AJAX if there are no options
                if (newSelect.options.length <= 1) {
                    // Try to fetch available GPS IDs from server
                    $.ajax({
                        url: '/api/available-gps/',  // Check if this endpoint exists
                        type: 'GET',
                        success: function(data) {
                            if (data && data.length > 0) {
                                // Clear existing options
                                $(newSelect).empty().append('<option value="">GPS tanlang</option>');
                                
                                // Add new options
                                data.forEach(function(gps) {
                                    $(newSelect).append(`<option value="${gps.id}">${gps.gps_id}</option>`);
                                });
                                
                                // Refresh Select2
                                $(newSelect).trigger('change');
                            }
                        },
                        error: function() {
                            console.error('Failed to fetch available GPS IDs');
                        }
                    });
                }
            }
        }
        
        // Animate the new field
        setTimeout(() => {
            newField.style.transition = 'all 0.3s ease-out';
            newField.style.opacity = '1';
            newField.style.transform = 'translateY(0)';
        }, 10);
        
        updateGpsOptions();
    } catch (error) {
        console.error('Error in addGpsField:', error);
        showToast('GPS qo\'shishda xatolik yuz berdi', 'error');
    }
}

function removeGpsField(button) {
    try {
        if (!button) return;
        const field = button.closest('.gps-field');
        if (!field) return;
        
        field.style.transition = 'all 0.3s ease-out';
        field.style.opacity = '0';
        field.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            // Destroy Select2 if available
            if (window.jQuery && $.fn.select2) {
                const select = field.querySelector('.gps-select');
                if (select && $(select).data('select2')) {
                    $(select).select2('destroy');
                }
            }
            field.remove();
            
            // Small timeout to update options after the field is removed
            setTimeout(updateGpsOptions, 10);
        }, 300);
    } catch (error) {
        console.error('Error removing GPS field:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    try {
        console.log('Initializing sotish_update.js');
        
        // Safety check if we're on the right page
        const form = document.querySelector('form');
        const gpsFields = document.querySelector('.gps-fields');
        
        // Check for form elements
        const summasi = document.getElementById('id_summasi');
        const naqd = document.getElementById('id_naqd');
        const bank_schot = document.getElementById('id_bank_schot');
        const karta = document.getElementById('id_karta');
        
        // Check other form elements
        const mijoz = document.getElementById('id_mijoz');
        const mijoz_tel_raqam = document.getElementById('id_mijoz_tel_raqam');
        const username = document.getElementById('id_username');
        const password = document.getElementById('id_password');
        const master = document.getElementById('id_master');
        const master_summasi = document.getElementById('id_master_summasi');
        const abonent_tulov = document.getElementById('id_abonent_tulov');
        const sana = document.getElementById('id_sana');
        
        console.log('Found form elements:', {
            form: !!form,
            gpsFields: !!gpsFields,
            summasi: !!summasi,
            naqd: !!naqd,
            bank_schot: !!bank_schot,
            karta: !!karta,
            mijoz: !!mijoz,
            mijoz_tel_raqam: !!mijoz_tel_raqam,
            username: !!username,
            password: !!password,
            master: !!master,
            master_summasi: !!master_summasi,
            abonent_tulov: !!abonent_tulov,
            sana: !!sana
        });
        
        if (!form || !gpsFields) {
            console.log('Not on the GPS form page, skipping initialization');
            return;
        }
        
        // Check for 'require is not defined' error
        if (typeof require !== 'undefined') {
            console.warn('Found "require" function which could cause issues in browser context');
        }
        
        // Make a backup of form values
        const formValues = {};
        if (form) {
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                if (input.name) {
                    formValues[input.name] = input.value;
                }
            });
            console.log('Backed up form values:', formValues);
        }
        
        // Initialize Select2 if available
        if (window.jQuery && $.fn.select2) {
            $('.gps-select').select2({
                theme: 'bootstrap-5',
                width: '100%',
                placeholder: 'GPS tanlang',
                allowClear: false,
                templateResult: formatGpsOption,
                templateSelection: formatGpsOption,
                escapeMarkup: function(m) { return m; }
            });
            
            // Add change handlers after initializing Select2
            $('.gps-select').on('change', function() {
                // Update options in a safe way
                setTimeout(updateGpsOptions, 10);
            });
        } else {
            console.warn('jQuery or Select2 not found');
        }
        
        // Format number inputs
        const numberInputs = document.querySelectorAll('input[type="text"]');
        if (numberInputs && numberInputs.length > 0) {
            numberInputs.forEach(input => {
                if (input && input.id !== 'id_karta' && 
                   (input.id === 'id_summasi' || 
                    input.id === 'id_naqd' || 
                    input.id === 'id_bank_schot' || 
                    input.id === 'id_master_summasi' || 
                    input.id === 'id_abonent_tulov')) {
                    formatNumber(input);
                }
            });
        }
        
        // Restore backup values if inputs are empty
        if (form) {
            setTimeout(() => {
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    if (input.name && !input.value && formValues[input.name]) {
                        input.value = formValues[input.name];
                        console.log(`Restored value for ${input.name}: ${formValues[input.name]}`);
                    }
                });
            }, 500);
        }
        
        // Set up form validation
        if (form) {
            form.addEventListener('submit', function(e) {
                const gpsFields = document.querySelectorAll('.gps-field');
                if (!gpsFields || gpsFields.length === 0) {
                    e.preventDefault();
                    showToast("Kamida bitta GPS qurilma qo'shishingiz kerak!", "error");
                    return;
                }
                
                // Validate GPS selections
                let hasValidGps = false;
                gpsFields.forEach(field => {
                    const select = field.querySelector('.gps-select');
                    if (select && select.value) {
                        hasValidGps = true;
                    }
                });
                
                if (!hasValidGps) {
                    e.preventDefault();
                    showToast("Kamida bitta GPS qurilmani tanlashingiz kerak!", "error");
                    return;
                }
            });
        }
        
        // Initial calculations and updates
        if (summasi && naqd && bank_schot && karta) {
            calculateQarz();
        } else {
            console.warn('Required fields for calculateQarz not found');
        }
        
        // Initialize with a timeout to allow DOM to fully render
        setTimeout(updateGpsOptions, 100);
        
    } catch (error) {
        console.error('Error during initialization:', error);
    }
});

