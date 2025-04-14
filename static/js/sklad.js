// Variables
let sortDirection = 'desc'; // Start with newest first
let sortField = 'date'; // Default sort by date
let gpsCount = 1;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Set today's date by default
    setTodayDate();
    
    // Format numeric inputs
    const summaInput = document.getElementById('id_summa_prixod');
    if (summaInput) {
        summaInput.addEventListener('input', function() {
            formatNumber(this);
        });
    }
    
    // Handle form submission to clean up formatted numbers
    const form = document.getElementById('sklad-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const summaInput = document.getElementById('id_summa_prixod');
            if (summaInput && summaInput.value) {
                // Remove commas before submitting
                summaInput.value = summaInput.value.replace(/,/g, '');
            }
        });
    }
    
    // Search functionality
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterTable();
        });
    }
    
    // Status filters
    const statusFilters = document.querySelectorAll('.status-filter');
    statusFilters.forEach(filter => {
        filter.addEventListener('click', function(e) {
            e.preventDefault();
            filterByStatus(this.dataset.filter);
            
            // Update filter button text
            const filterText = this.textContent.trim();
            const filterButton = document.getElementById('status-filter-button');
            if (filterButton) {
                filterButton.innerHTML = `<i class="fas fa-filter mr-2"></i> <span>${filterText}</span>`;
                filterButton.classList.add('btn-active');
            }
            
            // Force close the dropdown (DaisyUI specific)
            document.activeElement.blur();
        });
    });
    
    // Date filters
    const dateFilters = document.querySelectorAll('.date-filter');
    dateFilters.forEach(filter => {
        filter.addEventListener('click', function(e) {
            e.preventDefault();
            filterByDate(this.dataset.filter);
            
            // Update filter button text
            const filterText = this.textContent.trim();
            const filterButton = document.getElementById('date-filter-button');
            if (filterButton) {
                filterButton.innerHTML = `<i class="fas fa-calendar-alt mr-2"></i> <span>${filterText}</span>`;
                filterButton.classList.add('btn-active');
            }
            
            // Force close the dropdown (DaisyUI specific)
            document.activeElement.blur();
        });
    });
    
    // Calculate initial stats
    calculateStats();
});

// Set today's date
function setTodayDate() {
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('id_olingan_sana');
    if (dateInput) {
        dateInput.value = today;
    }
}

// Format number with commas
function formatNumber(input) {
    // Save cursor position
    const cursorPos = input.selectionStart;
    const oldLength = input.value.length;
    
    // Remove non-numeric characters
    let value = input.value.replace(/\D/g, '');
    
    // Format with commas
    if (value) {
        value = parseInt(value, 10).toLocaleString('en-US');
    }
    
    input.value = value;
    
    // Restore cursor position
    const newLength = input.value.length;
    const newCursorPos = cursorPos + (newLength - oldLength);
    if (newCursorPos >= 0) {
        input.setSelectionRange(newCursorPos, newCursorPos);
    }
}

// Parse formatted number
function parseFormattedNumber(formattedNumber) {
    return parseInt(formattedNumber.replace(/,/g, ''), 10) || 0;
}

// Filter table by search input
function filterTable() {
    const searchInput = document.getElementById('search-input').value.toLowerCase();
    const tableRows = document.querySelectorAll('#sklad-table-body tr:not([colspan])');
    let hasVisibleRows = false;
    
    tableRows.forEach(row => {
        const gpsId = row.dataset.id ? row.dataset.id.toLowerCase() : '';
        const personName = row.dataset.person ? row.dataset.person.toLowerCase() : '';
        const phoneCell = row.querySelector('td:nth-child(3) a')?.textContent.toLowerCase() || '';
        const dateCell = row.querySelector('.badge')?.textContent.toLowerCase() || '';
        
        if (gpsId.includes(searchInput) || 
            personName.includes(searchInput) || 
            phoneCell.includes(searchInput) ||
            dateCell.includes(searchInput)) {
            row.style.display = '';
            hasVisibleRows = true;
        } else {
            row.style.display = 'none';
        }
    });
    
    // Show/hide empty message
    const emptyRow = document.querySelector('#sklad-table-body tr[colspan]');
    if (emptyRow) {
        emptyRow.style.display = hasVisibleRows ? 'none' : '';
    }
    
    // Update counters
    calculateStats();
}

// Set sort field
function setSortField(field) {
    const oldField = sortField;
    sortField = field;
    
    // If clicking the same field, toggle direction
    if (oldField === field) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        // For new field, start with descending (newest/largest first)
        sortDirection = 'desc';
    }
    
    sortTable();
}

// Sort table
function sortTable() {
    const tbody = document.getElementById('sklad-table-body');
    const rows = Array.from(tbody.querySelectorAll('tr:not([style*="display: none"]):not([colspan])'));
    
    // Sort rows
    rows.sort((a, b) => {
        let valueA, valueB;
        
        switch(sortField) {
            case 'id':
                valueA = a.dataset.id || '';
                valueB = b.dataset.id || '';
                return sortDirection === 'asc' 
                    ? valueA.localeCompare(valueB)
                    : valueB.localeCompare(valueA);
                break;
            case 'person':
                valueA = a.dataset.person || '';
                valueB = b.dataset.person || '';
                return sortDirection === 'asc' 
                    ? valueA.localeCompare(valueB)
                    : valueB.localeCompare(valueA);
                break;
            case 'price':
                valueA = parseInt(a.dataset.price || '0', 10);
                valueB = parseInt(b.dataset.price || '0', 10);
                break;
            case 'date':
                valueA = new Date(a.dataset.date || '1970-01-01').getTime();
                valueB = new Date(b.dataset.date || '1970-01-01').getTime();
                break;
            default:
                valueA = 0;
                valueB = 0;
        }
        
        // For numeric values
        if (typeof valueA === 'number') {
            return sortDirection === 'asc' ? valueA - valueB : valueB - valueA;
        }
        
        return 0;
    });
    
    // Remove all rows
    rows.forEach(row => row.remove());
    
    // Append sorted rows
    rows.forEach(row => {
        tbody.appendChild(row);
    });
    
    // Update row numbers and totals
    calculateStats();
}

// Filter by status
function filterByStatus(filter) {
    const rows = document.querySelectorAll('#sklad-table-body tr:not([colspan])');
    let hasVisibleRows = false;
    
    rows.forEach(row => {
        const status = row.dataset.status || '';
        
        if (filter === 'all' || filter === status) {
            row.style.display = '';
            hasVisibleRows = true;
        } else {
            row.style.display = 'none';
        }
    });
    
    // Show/hide empty message
    const emptyRow = document.querySelector('#sklad-table-body tr[colspan]');
    if (emptyRow) {
        emptyRow.style.display = hasVisibleRows ? 'none' : '';
    }
    
    // Update counters
    calculateStats();
}

// Filter by date
function filterByDate(filter) {
    console.log("Filtering by date:", filter);
    const rows = document.querySelectorAll('#sklad-table-body tr:not([colspan])');
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    // Fix week start calculation
    const weekStart = new Date(today);
    // Get current day (0 = Sunday, 1 = Monday, ...)
    const currentDay = today.getDay();
    // Adjust to Monday as first day of week (if today is Sunday, go back 6 days)
    const daysToSubtract = currentDay === 0 ? 6 : currentDay - 1;
    weekStart.setDate(today.getDate() - daysToSubtract);
    console.log("Week starts on:", weekStart.toISOString().split('T')[0]);
    
    const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
    console.log("Month starts on:", monthStart.toISOString().split('T')[0]);
    
    let hasVisibleRows = false;
    
    rows.forEach(row => {
        const dateStr = row.dataset.date;
        console.log("Row date string:", dateStr);
        
        if (!dateStr) {
            row.style.display = 'none';
            return;
        }
        
        // Fix date parsing to handle different formats
        let rowDate;
        if (dateStr.includes('.')) {
            // Handle DD.MM.YYYY format
            const parts = dateStr.split('.');
            rowDate = new Date(parts[2], parts[1] - 1, parts[0]);
        } else {
            // Handle YYYY-MM-DD format
            rowDate = new Date(dateStr);
        }
        
        rowDate.setHours(0, 0, 0, 0);
        console.log("Parsed date:", rowDate.toISOString().split('T')[0]);
        
        let show = false;
        
        switch (filter) {
            case 'all':
                show = true;
                break;
            case 'today':
                show = rowDate.getTime() === today.getTime();
                break;
            case 'week':
                show = rowDate >= weekStart && rowDate <= today;
                break;
            case 'month':
                show = rowDate >= monthStart && rowDate <= today;
                break;
        }
        
        console.log("Show row:", show);
        if (show) {
            row.style.display = '';
            hasVisibleRows = true;
        } else {
            row.style.display = 'none';
        }
    });
    
    // Show/hide empty message
    const emptyRow = document.querySelector('#sklad-table-body tr[colspan]');
    if (emptyRow) {
        emptyRow.style.display = hasVisibleRows ? 'none' : '';
    }
    
    // Update counters
    calculateStats();
}

// Reset all filters
function resetFilters() {
    // Reset search box
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = '';
    }
    
    // Reset status filter button
    const statusFilterButton = document.getElementById('status-filter-button');
    if (statusFilterButton) {
        statusFilterButton.innerHTML = '<i class="fas fa-filter mr-2"></i> <span>Holat bo\'yicha</span>';
        statusFilterButton.classList.remove('btn-active');
    }
    
    // Reset date filter button
    const dateFilterButton = document.getElementById('date-filter-button');
    if (dateFilterButton) {
        dateFilterButton.innerHTML = '<i class="fas fa-calendar-alt mr-2"></i> <span>Sana bo\'yicha</span>';
        dateFilterButton.classList.remove('btn-active');
    }
    
    // Show all rows
    const rows = document.querySelectorAll('#sklad-table-body tr');
    rows.forEach(row => {
        if (!row.querySelector('td[colspan]')) {
            row.style.display = '';
        } else {
            row.style.display = 'none'; // Hide empty message
        }
    });
    
    // Reset sort order
    sortDirection = 'desc';
    sortField = 'date';
    
    // Update stats
    calculateStats();
    
    // Apply a subtle animation to show the reset was successful
    const tableBody = document.getElementById('sklad-table-body');
    if (tableBody) {
        tableBody.classList.add('animate-pulse');
        setTimeout(() => {
            tableBody.classList.remove('animate-pulse');
        }, 500);
    }
}

// Calculate statistics
function calculateStats() {
    const visibleRows = document.querySelectorAll('#sklad-table-body tr:not([style*="display: none"]):not([colspan])');
    const visibleCount = visibleRows.length;
    
    // Update visible count
    const visibleCountElement = document.getElementById('visible-count');
    if (visibleCountElement) {
        visibleCountElement.textContent = visibleCount;
    }
    
    // Count unsold items
    let unsoldCount = 0;
    visibleRows.forEach(row => {
        if (row.dataset.status === 'unsold') {
            unsoldCount++;
        }
    });
    
    // Update unsold count
    const unsoldCountElement = document.getElementById('unsold-count');
    if (unsoldCountElement) {
        unsoldCountElement.textContent = unsoldCount;
    }
    
    // Calculate total amount
    let totalAmount = 0;
    visibleRows.forEach(row => {
        const price = parseInt(row.dataset.price || '0', 10);
        totalAmount += price;
    });
    
    // Update total amount
    const totalAmountElement = document.getElementById('total-amount');
    if (totalAmountElement) {
        totalAmountElement.textContent = totalAmount.toLocaleString('en-US');
    }
}

// Update file name for Excel import
function updateFileName() {
    const fileInput = document.getElementById('excel_file');
    const fileNameSpan = document.getElementById('file_name');
    
    if (fileInput && fileInput.files.length > 0 && fileNameSpan) {
        fileNameSpan.textContent = fileInput.files[0].name;
    }
}

// Add GPS field
function addGpsField() {
    gpsCount++;
    const container = document.getElementById('gps-container');
    const newField = document.createElement('div');
    newField.className = 'flex items-center gap-2 animate-fade-in';
    newField.innerHTML = `
        <div class="input-group flex-grow">
            <span class="btn btn-square btn-ghost">
                <i class="fas fa-map-marker-alt text-gray-400"></i>
            </span>
            <input type="text" name="gps_id_${gpsCount}" id="gps_id_${gpsCount}" placeholder="GPS ID ${gpsCount}" class="input input-bordered w-full" required>
        </div>
        <button type="button" onclick="removeGpsField(this)" class="btn btn-error btn-square btn-sm">
            <i class="fas fa-times"></i>
        </button>
    `;
    container.appendChild(newField);
    
    // Update GPS count in stats
    const gpsCountElement = document.getElementById('gps-count');
    if (gpsCountElement) {
        gpsCountElement.textContent = gpsCount;
    }
    
    // Focus on the new field
    document.getElementById(`gps_id_${gpsCount}`).focus();
}

// Remove GPS field
function removeGpsField(button) {
    const fieldContainer = button.parentElement;
    fieldContainer.classList.add('animate-fade-out');
    
    // Apply slide-out animation and then remove
    setTimeout(() => {
        fieldContainer.remove();
        gpsCount--;
        
        // Update GPS count in stats
        const gpsCountElement = document.getElementById('gps-count');
        if (gpsCountElement) {
            gpsCountElement.textContent = gpsCount;
        }
    }, 300);
}

// Reset form
function resetForm() {
    const form = document.getElementById('sklad-form');
    if (form) {
        form.reset();
        
        // Reset GPS fields
        const gpsContainer = document.getElementById('gps-container');
        if (gpsContainer) {
            // Keep only the first GPS field
            const allFields = gpsContainer.querySelectorAll('div.flex');
            for (let i = 1; i < allFields.length; i++) {
                allFields[i].remove();
            }
        }
        
        // Reset counter
        gpsCount = 1;
        
        // Update GPS count
        const gpsCountElement = document.getElementById('gps-count');
        if (gpsCountElement) {
            gpsCountElement.textContent = gpsCount;
        }
        
        // Set today's date
        setTodayDate();
        
        // Focus on first field
        document.getElementById('id_gps_id').focus();
    }
}

// Delete confirmation modal
function confirmDelete(id, name) {
    const deleteName = document.getElementById('delete-name');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const deleteModal = document.getElementById('delete-modal');
    
    if (deleteName && confirmDeleteBtn && deleteModal) {
        deleteName.textContent = name;
        confirmDeleteBtn.href = `/sklad/delete/${id}/`;
        deleteModal.classList.add('modal-open');
    }
}

// Close modal
function closeModal() {
    const deleteModal = document.getElementById('delete-modal');
    if (deleteModal) {
        deleteModal.classList.remove('modal-open');
    }
} 