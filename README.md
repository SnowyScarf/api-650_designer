# Acetic Acid Storage Tank Design Tool

A professional Flask web application for automated design of atmospheric storage tanks for concentrated acetic acid, following API 650 standards.

## Overview

This engineering calculator automates the design process for acetic acid storage tanks by implementing API 650 One-Foot Method calculations. The application provides:

- **Professional Engineering Calculations**: API 650 compliant shell thickness calculations
- **Interactive Visualization**: Real-time charts showing design parameter relationships
- **Export Capabilities**: Professional Excel and PDF reports for documentation
- **Responsive Design**: Modern Bootstrap 5 interface optimized for engineering workflows

## Features

### Core Functionality
- ✅ Production rate and holding period input validation
- ✅ Automated tank volume and dimension optimization
- ✅ API 650 One-Foot Method shell thickness calculations
- ✅ SS316L material property integration
- ✅ Standard plate thickness rounding
- ✅ Bund volume calculations (110% of largest tank)
- ✅ Multi-tank configuration support

### Technical Specifications
- **Material**: SS316L Stainless Steel (corrosion resistant)
- **Design Code**: API 650 - Welded Tanks for Oil Storage
- **Calculation Method**: One-Foot Shell Thickness Method
- **Default Parameters**:
  - Density: 1049 kg/m³ (concentrated acetic acid)
  - Fill Fraction: 85% (API 650 recommendation)
  - Corrosion Allowance: 1.5mm
  - D:H Ratio: Optimized 1:1.7 for storage efficiency

### Interactive Features
- **Real-time Charts**: Plotly.js visualization of shell thickness vs tank height
- **Responsive Design**: Mobile-friendly Bootstrap 5 interface
- **Form Validation**: Client and server-side input validation
- **Export Options**: Excel (.xlsx) and PDF report generation
- **Print Optimization**: Clean printable results layout

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Setup Instructions

1. **Clone or download the application files**
   ```bash
   # Ensure all files are in your project directory
   ls -la
   # Should show: app.py, main.py, calculations.py, templates/, static/, README.md
   ```

2. **Install required packages**
   ```bash
   pip install flask pandas openpyxl reportlab
   ```

3. **Set environment variables**
   ```bash
   # On Linux/macOS
   export SESSION_SECRET="your-secret-key-here"
   
   # On Windows
   set SESSION_SECRET=your-secret-key-here
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`
   - The application will be available on your local network at `http://0.0.0.0:5000`

## Usage Guide

### Step 1: Home Page
- Navigate to the home page for an overview of the tool's capabilities
- Review the acetic acid properties and design standards information
- Click "Start Design" to begin

### Step 2: Design Input
Fill out the design form with your process parameters:

#### Process Parameters
- **Production Rate**: Enter in TPD (tonnes per day)
- **Holding Period**: Storage duration in days
- **Density**: Default 1049 kg/m³ for concentrated acetic acid
- **Fill Fraction**: Default 85% (API 650 recommendation)

#### Design Parameters
- **Corrosion Allowance**: Default 1.5mm for acetic acid service
- **Number of Tanks**: Select 1-4 tanks for redundancy

#### Material Properties (SS316L)
- **Design Stress (Sd)**: Default 138 MPa
- **Test Stress (St)**: Default 207 MPa

### Step 3: View Results
The results page displays:
- **Tank specifications table** with complete dimensions
- **Interactive chart** showing shell thickness vs height relationship
- **Tank diagram** with dimensional annotations
- **Design calculations** breakdown
- **Export options** for documentation

### Step 4: Export Reports
- **Excel Export**: Complete specifications in spreadsheet format
- **PDF Export**: Professional engineering report with calculations
- **Print Option**: Optimized layout for paper documentation

## API 650 Calculations

### Shell Thickness Formula
The application implements the API 650 One-Foot Method:

