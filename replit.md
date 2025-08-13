# Acetic Acid Storage Tank Design Tool

## Overview

This is a professional Flask web application that automates the design of atmospheric storage tanks for concentrated acetic acid following API 650 standards. The application has been enhanced with advanced features including custom branding, multi-chemical database, case comparison, interactive PFD, multiple export formats, dark/light theme toggle, and live unit conversion tools. It serves as a comprehensive engineering calculator that takes process parameters and calculates optimal tank specifications using API 650 One-Foot Method.

## Recent Major Enhancements (August 2025)

### Custom Branding System
- Logo upload functionality for company/college branding
- Custom company name integration in all reports
- Professional branded PDF and Excel exports

### Chemical Database Expansion
- 11 pre-defined chemicals with complete properties
- Automatic property updates based on chemical selection
- Corrosivity ratings and material recommendations
- Support for acetic acid, sulfuric acid, methanol, benzene, and more

### Case Comparison Feature
- Save multiple calculation cases for side-by-side comparison
- Percentage difference calculations between cases
- Session-based storage for comparison data
- Professional comparison tables and analysis

### Interactive Process Flow Diagram
- SVG-based interactive PFD with hover tooltips
- Equipment specifications and safety device details
- Visual tank representations with design dimensions
- Professional engineering symbols and legends

### Enhanced Export Capabilities
- CSV export for data analysis
- Enhanced Excel reports with multiple sheets
- PDF reports with embedded logos and static chart images
- Professional formatting with company branding

### User Experience Improvements
- Professional dark theme design
- Live unit conversion sidebar (volume, mass, temperature, pressure)
- Auto-save form data in browser local storage
- Enhanced responsive design and animations

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: HTML5, CSS3, Bootstrap 5 for responsive design with dark theme support
- **Interactivity**: Vanilla JavaScript for form validation, real-time input feedback, and UI enhancements
- **Visualization**: Plotly.js for interactive charts showing design parameter relationships
- **Icons**: Font Awesome for professional iconography
- **Responsive Design**: Mobile-friendly layout with Bootstrap grid system

### Backend Architecture
- **Framework**: Flask (Python 3.11) with modular structure and session management
- **Design Pattern**: MVC pattern with separate calculation and database modules
- **Core Components**:
  - `app.py`: Enhanced Flask application with 15+ routes for full functionality
  - `calculations.py`: TankDesignCalculator class implementing API 650 engineering calculations
  - `chemical_database.py`: ChemicalDatabase class with 11 predefined chemicals
  - `main.py`: Application entry point
- **Template Engine**: Jinja2 with inheritance-based template structure
- **Session Management**: Flask sessions for case comparison, branding, and theme preferences
- **File Upload**: Secure logo upload with validation and storage

### Calculation Engine
- **Standards Compliance**: API 650 One-Foot Method for shell thickness calculations
- **Material Specifications**: SS316L stainless steel with corrosion resistance properties
- **Engineering Features**: 
  - Tank volume optimization based on D:H ratio (1:1.7)
  - Standard plate thickness rounding
  - Multi-tank configuration support
  - Bund volume calculations (110% of largest tank)

### Data Processing and Export
- **Excel Export**: pandas + openpyxl for structured multi-sheet reports with branding
- **PDF Generation**: reportlab for professional engineering reports with logos and charts
- **CSV Export**: Simple comma-separated format for data analysis
- **Data Validation**: Enhanced client-side and server-side input validation
- **Case Management**: Session-based storage and comparison of multiple design cases

### User Interface Design
- **Theme**: Professional dark theme with engineering aesthetics
- **Navigation**: Enhanced Bootstrap navbar with PFD and comparison links
- **Forms**: Chemical selection dropdown with auto-property updates
- **Results Display**: Enhanced tabular data with case saving and comparison features
- **Interactive Elements**: Process Flow Diagram with hover tooltips and equipment details
- **Unit Converter**: Always-available sidebar for live unit conversions
- **Animations**: Smooth transitions and hover effects throughout the application

## External Dependencies

### Python Libraries
- **Flask**: Core web framework for routing and templating
- **pandas**: Data manipulation and Excel export functionality
- **openpyxl**: Excel file generation for engineering reports
- **reportlab**: PDF generation for professional documentation
- **logging**: Application logging and debugging

### Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme variant from replit CDN
- **Plotly.js**: Interactive charting library for data visualization
- **Font Awesome**: Icon library for professional UI elements

### Runtime Environment
- **Python 3.11+**: Required runtime environment
- **Flask Development Server**: Built-in server for development and testing
- **Environment Variables**: SESSION_SECRET for Flask session management

### Engineering Standards
- **API 650**: Welded Tanks for Oil Storage standard for calculations
- **Material Standards**: SS316L stainless steel specifications for corrosion resistance
- **Safety Factors**: Industry-standard design margins and safety considerations