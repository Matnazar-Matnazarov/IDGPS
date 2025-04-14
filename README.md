# ID_GPS - GPS Monitoring and Management System

## Overview
ID_GPS is a comprehensive GPS device management system designed for businesses that sell, monitor, and maintain GPS tracking devices. This enterprise-grade application streamlines inventory management, sales tracking, client subscription management, and financial reporting within a single unified platform.

## Key Features

### 📊 Dashboard and Analytics
- Interactive statistical dashboard with real-time key metrics visualization
- Monthly and annual performance tracking with dynamic charts
- Subscriber growth analytics and payment success rate monitoring
- Financial analytics including revenue trends, GPS penetration rate, and payment ratios

### 📦 Inventory Management (Sklad)
- Complete lifecycle tracking of GPS devices from acquisition to sales
- Efficient bulk import/export functionality via Excel templates
- Status tracking with filterable views by sold/unsold status
- Detailed device history with acquisition information

### 👥 Client Management (Mijozlar)
- Comprehensive client profile management with contact details
- Multi-device assignment capabilities and subscription tracking
- Integrated SIM card management and vehicle information
- User-friendly filtering and search functionality

### 💰 Financial Operations
- Detailed expense tracking and categorization (Rasxod)
- Revenue tracking with multiple payment method support (cash, card, bank transfer)
- Monthly subscription management and payment verification
- Comprehensive accounting reports and financial summaries (Bugalteriya)

### 👤 User Management
- Role-based access control with customizable permissions
- Staff profiles and activity tracking
- Secure authentication system with password encryption

### 📝 Additional Tools
- Task and note management system with reminders
- Sales performance tracking by staff member
- Technician (master) assignment and payment tracking

## Technology Stack

### Backend
- **Framework**: Django 5.x
- **Database**: Django ORM (supports PostgreSQL, MySQL, SQLite)
- **Data Processing**: Pandas, OpenPyXL for Excel operations

### Frontend
- **CSS Framework**: Tailwind CSS with DaisyUI components
- **JavaScript**: Alpine.js for reactive components
- **Charts**: Chart.js for data visualization
- **UI Components**: Select2 for enhanced dropdowns, FontAwesome for icons
- **Responsive Design**: Mobile-first approach with adaptive layouts

### User Experience
- Dark/light mode support
- Responsive sidebar navigation
- Interactive toast notifications
- Animated UI transitions
- Form validation and error handling

## Installation and Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/Matnazar-Matnazarov/IDGPS.git
   cd ID_GPS
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database in `settings.py`

5. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create an administrator account:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the application at http://127.0.0.1:8000

## Project Structure

```
ID_GPS/
├── IDGPS/                # Main application package
│   ├── models.py         # Database models (Users, GPS devices, Sales, etc.)
│   ├── forms.py          # Form definitions for data entry
│   ├── views/            # Application views organized by function
│   │   ├── umumiy.py     # General views including statistics
│   │   └── ...           # Other view modules
│   └── ...               # Other application components
├── templates/            # HTML templates with Tailwind/DaisyUI styling
│   ├── base.html         # Base template with navigation and layout
│   ├── statistika.jinja  # Statistics and dashboard template
│   ├── rasxod.html       # Expense management template
│   ├── sklad.html        # Inventory management template
│   └── ...               # Other templates
├── static/               # Static files (CSS, JS, images)
├── manage.py             # Django management script
└── requirements.txt      # Project dependencies
```

## Application Modules

1. **Statistika**: Dashboard with key performance indicators and financial analytics
2. **Mijozlar**: Client information management and device assignments
3. **Sklad**: GPS device inventory tracking and management
4. **Eslatmalar**: Task and note management system
5. **Rasxod**: Business expense recording and tracking
6. **Sotuv**: Device sales and subscription management
7. **Bugalteriya**: Financial reporting and payment tracking
8. **Hodim**: Staff management and access control (admin only)

## Usage Guide

After installation, log in using your administrator credentials:

1. **Dashboard (Statistika)**: Access the main dashboard to view KPIs, statistics, and performance charts
2. **Add Inventory**: Use the Sklad module to add new GPS devices either individually or via Excel import
3. **Manage Sales**: Record new sales through the Sotuv module, assigning devices to clients
4. **Track Finances**: Monitor expenses in Rasxod and manage payments in Bugalteriya
5. **Generate Reports**: Use the reporting features to analyze business performance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue to suggest improvements or report bugs.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For support, feature requests, or questions:
- Email: [your-email@example.com](mailto:your-email@example.com)
- Issues: [GitHub Issues](https://github.com/Matnazar-Matnazarov/IDGPS/issues)