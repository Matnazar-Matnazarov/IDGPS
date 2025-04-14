function setTodayDate() {
    const today = new Date();
    const date = today.toISOString().split('T')[0];
    document.getElementById('olingan_sana').value = date;
}

window.onload = function() {
    setTodayDate();  // Olingan sana
};

function filterTable() {
    const searchInput = document.getElementById('search-input').value.toLowerCase();
    const tableRows = document.querySelectorAll('tbody tr');
    
    tableRows.forEach(row => {
        const gpsCell = row.querySelector('td:first-child').textContent.toLowerCase();
        const personCell = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        const dateCell = row.querySelector('td:nth-child(5)').textContent.toLowerCase();
        
        if (gpsCell.includes(searchInput) || 
            dateCell.includes(searchInput) || 
            personCell.includes(searchInput)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

//  GPS qo'shish
    let gpsCount = 1;
    function addGpsField() {
        gpsCount++;
        const container = document.getElementById('gps-container');
        const newField = document.createElement('div');
        newField.className = 'mb-4 flex items-center gap-2';
        newField.innerHTML = `
            <div class="flex-grow">
                <label for="gps_id_${gpsCount}" class="block text-gray-700 font-medium mb-2">GPS ID ${gpsCount}</label>
                <input type="text" name="gps_id_${gpsCount}" id="gps_id_${gpsCount}" class="w-full p-2 border border-gray-300 rounded-lg">
            </div>
            <button type="button" onclick="removeGpsField(this)" class="h-10 mt-8 px-3 bg-red-500 text-white rounded-lg hover:bg-red-600">
                -
            </button>
        `;
        container.appendChild(newField);
    }

    function removeGpsField(button) {
        button.parentElement.remove();
    }
