# Acetic Acid Storage Tank Design Tool

## Overview

This is a professional Flask web application that automates the design of atmospheric storage tanks for concentrated acetic acid following API 650 standards. The application implements engineering calculations for tank design, provides interactive visualizations, and generates professional reports. It serves as an engineering calculator that takes process parameters (production rate, holding period) and calculates optimal tank specifications including dimensions, shell thickness, and material requirements using the API 650 One-Foot Method.

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
- **Framework**: Flask (Python 3.11) with modular structure
- **Design Pattern**: MVC pattern with separate calculation module
- **Core Components**:
  - `app.py`: Main Flask application with routes for home, design form, and calculations
  - `calculations.py`: TankDesignCalculator class implementing API 650 engineering calculations
  - `main.py`: Application entry point
- **Template Engine**: Jinja2 with inheritance-based template structure

### Calculation Engine
- **Standards Compliance**: API 650 One-Foot Method for shell thickness calculations
- **Material Specifications**: SS316L stainless steel with corrosion resistance properties
- **Engineering Features**: 
  - Tank volume optimization based on D:H ratio (1:1.7)
  - Standard plate thickness rounding
  - Multi-tank configuration support
  - Bund volume calculations (110% of largest tank)

### Data Processing and Export
- **Excel Export**: pandas + openpyxl for structured data export
- **PDF Generation**: reportlab for professional engineering reports
- **Data Validation**: Client-side and server-side input validation with Flask's request handling

### User Interface Design
- **Theme**: Dark theme with professional engineering aesthetics
- **Navigation**: Bootstrap navbar with responsive collapse
- **Forms**: Progressive enhancement with validation feedback
- **Results Display**: Tabular data presentation with visual emphasis on key metrics

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