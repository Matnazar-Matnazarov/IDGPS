// Payment status update functionality
document.addEventListener('DOMContentLoaded', function() {
    const yearSelect = document.getElementById('year-select');
    const paymentButtons = document.querySelectorAll('.payment-btn');
    
    // Handle year selection change
    if (yearSelect) {
        yearSelect.addEventListener('change', function() {
            window.location.href = `/bugalteriya/?year=${this.value}`;
        });
    }
    
    // Handle payment button clicks
    paymentButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const clientId = this.dataset.clientId;
            const month = this.dataset.month;
            const year = this.dataset.year;
            
            try {
                const response = await fetch(`/api/update-payment-status/${clientId}/${month}/${year}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    // Update button appearance based on new status
                    this.textContent = data.new_status === 'paid' ? 'To\'langan' : 
                                      data.new_status === 'pending' ? 'Kutilmoqda' : 'To\'lanmagan';
                    
                    if (data.new_status === 'paid') {
                        this.classList.remove('bg-red-100', 'text-red-800', 'bg-yellow-100', 'text-yellow-800');
                        this.classList.add('bg-green-100', 'text-green-800');
                    } else if (data.new_status === 'pending') {
                        this.classList.remove('bg-red-100', 'text-red-800', 'bg-green-100', 'text-green-800');
                        this.classList.add('bg-yellow-100', 'text-yellow-800');
                    } else {
                        this.classList.remove('bg-green-100', 'text-green-800', 'bg-yellow-100', 'text-yellow-800');
                        this.classList.add('bg-red-100', 'text-red-800');
                    }
                    
                    // Show success message
                    showAlert('success', data.message || 'To\'lov holati yangilandi');
                } else {
                    const errorData = await response.json();
                    showAlert('error', errorData.error || 'Xatolik yuz berdi');
                }
            } catch (error) {
                console.error('Error:', error);
                showAlert('error', 'Xatolik yuz berdi');
            }
        });
    });
});

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Helper function to show alerts
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`;
    alertDiv.textContent = message;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}
