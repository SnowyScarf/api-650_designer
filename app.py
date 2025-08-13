import os
import logging
import json
import base64
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from calculations import TankDesignCalculator
from chemical_database import ChemicalDatabase
import pandas as pd
import io
import csv
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
import plotly.graph_objs as go
import plotly.io as pio

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "acetic-acid-design-tool-secret")

# Configure upload folder for logos
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize chemical database
chemical_db = ChemicalDatabase()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page with introduction to the acetic acid storage tank design tool."""
    return render_template('index.html')

@app.route('/upload_logo', methods=['POST'])
def upload_logo():
    """Handle logo upload for custom branding."""
    if 'logo' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['logo']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Store logo path in session
        session['logo_path'] = f"uploads/{filename}"
        session['company_name'] = request.form.get('company_name', 'Engineering Company')
        
        flash('Logo uploaded successfully!', 'success')
        return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files.', 'error')
        return redirect(url_for('index'))

@app.route('/design')
def design():
    """Design form page for tank design inputs."""
    chemicals = chemical_db.get_chemical_list()
    return render_template('design.html', chemicals=chemicals)

@app.route('/pfd')
def pfd():
    """Process Flow Diagram page."""
    return render_template('pfd.html')

@app.route('/get_chemical_properties/<chemical_id>')
def get_chemical_properties(chemical_id):
    """API endpoint to get chemical properties."""
    chemical = chemical_db.get_chemical(chemical_id)
    if chemical:
        return jsonify(chemical)
    else:
        return jsonify({'error': 'Chemical not found'}), 404

@app.route('/save_case', methods=['POST'])
def save_case():
    """Save a calculation case for comparison."""
    case_name = request.form.get('case_name', 'Case 1')
    
    # Store current calculation in session
    if 'current_results' in session:
        if 'saved_cases' not in session:
            session['saved_cases'] = {}
        
        session['saved_cases'][case_name] = {
            'results': session['current_results'],
            'inputs': session.get('current_inputs', {})
        }
        session.modified = True
        
        flash(f'{case_name} saved successfully!', 'success')
    else:
        flash('No calculation results to save.', 'error')
    
    return redirect(url_for('calculate'))

@app.route('/compare_cases')
def compare_cases():
    """Display comparison between saved cases."""
    saved_cases = session.get('saved_cases', {})
    if len(saved_cases) < 2:
        flash('You need at least 2 saved cases to compare.', 'error')
        return redirect(url_for('design'))
    
    return render_template('compare.html', cases=saved_cases)

@app.route('/calculate', methods=['POST'])
def calculate():
    """Process design inputs and calculate tank specifications."""
    try:
        # Extract form data
        production_rate = float(request.form.get('production_rate', 0))
        holding_period = float(request.form.get('holding_period', 0))
        density = float(request.form.get('density', 1049))
        max_fill_fraction = float(request.form.get('max_fill_fraction', 85)) / 100
        corrosion_allowance = float(request.form.get('corrosion_allowance', 1.5))
        num_tanks = int(request.form.get('num_tanks', 2))
        allowable_stress_design = float(request.form.get('sd', 138))  # MPa for SS316L
        allowable_stress_test = float(request.form.get('st', 207))    # MPa for SS316L
        
        # Validate inputs
        if production_rate <= 0 or holding_period <= 0:
            flash('Production rate and holding period must be positive values.', 'error')
            return redirect(url_for('design'))
        
        if num_tanks <= 0:
            flash('Number of tanks must be at least 1.', 'error')
            return redirect(url_for('design'))
        
        # Initialize calculator
        calculator = TankDesignCalculator(
            production_rate=production_rate,
            holding_period=holding_period,
            density=density,
            max_fill_fraction=max_fill_fraction,
            corrosion_allowance=corrosion_allowance,
            num_tanks=num_tanks,
            allowable_stress_design=allowable_stress_design,
            allowable_stress_test=allowable_stress_test
        )
        
        # Perform calculations
        results = calculator.calculate_tank_design()
        
        # Generate chart data for shell thickness vs height
        chart_data = calculator.generate_thickness_chart_data()
        
        # Store results in session for saving/comparison
        session['current_results'] = results
        session['current_inputs'] = {
            'production_rate': production_rate,
            'holding_period': holding_period,
            'density': density,
            'max_fill_fraction': max_fill_fraction * 100,
            'corrosion_allowance': corrosion_allowance,
            'num_tanks': num_tanks,
            'sd': allowable_stress_design,
            'st': allowable_stress_test
        }
        session.modified = True
        
        return render_template('results.html', 
                             results=results, 
                             chart_data=chart_data,
                             inputs=session['current_inputs'])
        
    except ValueError as e:
        flash(f'Invalid input: {str(e)}', 'error')
        return redirect(url_for('design'))
    except Exception as e:
        logging.error(f"Calculation error: {str(e)}")
        flash('An error occurred during calculation. Please check your inputs.', 'error')
        return redirect(url_for('design'))

@app.route('/export/csv')
def export_csv():
    """Export tank design results to CSV format."""
    try:
        # Get results from session
        results = session.get('current_results', {})
        inputs = session.get('current_inputs', {})
        
        if not results:
            flash('No calculation results to export.', 'error')
            return redirect(url_for('design'))
        
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Tank Design Results - CSV Export'])
        writer.writerow(['Company:', session.get('company_name', 'Engineering Company')])
        writer.writerow([])
        
        # Write input parameters
        writer.writerow(['Input Parameters'])
        writer.writerow(['Parameter', 'Value', 'Unit'])
        writer.writerow(['Production Rate', inputs.get('production_rate', ''), 'TPD'])
        writer.writerow(['Holding Period', inputs.get('holding_period', ''), 'days'])
        writer.writerow(['Density', inputs.get('density', ''), 'kg/m³'])
        writer.writerow(['Fill Fraction', inputs.get('max_fill_fraction', ''), '%'])
        writer.writerow([])
        
        # Write tank specifications
        writer.writerow(['Tank Specifications'])
        writer.writerow(['Tank No', 'Chemical', 'Capacity (m³)', 'Diameter (m)', 'Height (m)', 'Shell Thickness (mm)'])
        
        for tank in results.get('tank_specifications', []):
            writer.writerow([
                tank['tank_no'],
                tank['chemical'],
                tank['capacity'],
                tank['diameter'],
                tank['height'],
                tank['shell_thickness']
            ])
        
        # Convert to bytes
        csv_data = output.getvalue().encode('utf-8')
        output.close()
        
        return send_file(
            io.BytesIO(csv_data),
            as_attachment=True,
            download_name='tank_design_results.csv',
            mimetype='text/csv'
        )
        
    except Exception as e:
        logging.error(f"CSV export error: {str(e)}")
        flash('Error generating CSV file.', 'error')
        return redirect(url_for('design'))

@app.route('/export/excel')
def export_excel():
    """Export tank design results to Excel format with custom branding."""
    try:
        # Get results from session
        results = session.get('current_results', {})
        inputs = session.get('current_inputs', {})
        
        if not results:
            flash('No calculation results to export.', 'error')
            return redirect(url_for('design'))
        
        # Create Excel file in memory
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine='openpyxl')
        try:
            # Tank specifications data
            tank_data = []
            for tank in results.get('tank_specifications', []):
                tank_data.append({
                    'Tank No': tank['tank_no'],
                    'Chemical': tank['chemical'],
                    'Capacity (m³)': tank['capacity'],
                    'Diameter (m)': tank['diameter'],
                    'Height (m)': tank['height'],
                    'Shell Thickness (mm)': tank['shell_thickness'],
                    'Bottom Thickness (mm)': tank['bottom_thickness'],
                    'Roof Thickness (mm)': tank['roof_thickness']
                })
            
            df = pd.DataFrame(tank_data)
            df.to_excel(writer, sheet_name='Tank Design', index=False)
            
            # Add design parameters sheet
            params_data = {
                'Parameter': ['Company', 'Production Rate', 'Holding Period', 'Density', 'Fill Fraction', 'Corrosion Allowance', 'Number of Tanks'],
                'Value': [
                    session.get('company_name', 'Engineering Company'),
                    f"{inputs.get('production_rate', '')} TPD",
                    f"{inputs.get('holding_period', '')} days",
                    f"{inputs.get('density', '')} kg/m³",
                    f"{inputs.get('max_fill_fraction', '')}%",
                    f"{inputs.get('corrosion_allowance', '')} mm",
                    f"{inputs.get('num_tanks', '')} tanks"
                ],
                'Standard': ['User Input', 'User Input', 'User Input', 'Chemical Property', 'API 650', 'API 650', 'User Input']
            }
            params_df = pd.DataFrame(params_data)
            params_df.to_excel(writer, sheet_name='Design Parameters', index=False)
            
            # Add calculations sheet
            calc_data = {
                'Calculation': [
                    'Total Storage Volume',
                    'Geometric Volume',
                    'Design Thickness',
                    'Test Thickness',
                    'Required Thickness',
                    'Standard Thickness',
                    'Bund Volume'
                ],
                'Value': [
                    f"{results['storage']['total_volume']:.1f} m³",
                    f"{results['storage']['geometric_volume']:.1f} m³",
                    f"{results['shell']['design_thickness']:.2f} mm",
                    f"{results['shell']['test_thickness']:.2f} mm",
                    f"{results['shell']['required_thickness']:.2f} mm",
                    f"{results['shell']['shell_thickness']} mm",
                    f"{results['bund_volume']:.1f} m³"
                ],
                'Method': [
                    'Mass × Density',
                    'Total Volume ÷ Fill Factor',
                    'API 650 Design Formula',
                    'API 650 Test Formula',
                    'Max(Design, Test) + CA',
                    'Rounded to Standard',
                    '110% of Tank Volume'
                ]
            }
            calc_df = pd.DataFrame(calc_data)
            calc_df.to_excel(writer, sheet_name='Calculations', index=False)
            
        finally:
            writer.close()
        
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name='acetic_acid_tank_design.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logging.error(f"Excel export error: {str(e)}")
        flash('Error generating Excel file.', 'error')
        return redirect(url_for('design'))

@app.route('/export/pdf')
def export_pdf():
    """Export tank design results to PDF format with custom branding and chart."""
    try:
        # Get results from session
        results = session.get('current_results', {})
        inputs = session.get('current_inputs', {})
        
        if not results:
            flash('No calculation results to export.', 'error')
            return redirect(url_for('design'))
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Add logo if available
        logo_path = session.get('logo_path')
        if logo_path and os.path.exists(os.path.join('static', logo_path)):
            try:
                logo = Image(os.path.join('static', logo_path), width=2*inch, height=1*inch)
                elements.append(logo)
                elements.append(Spacer(1, 10))
            except:
                pass  # Skip logo if there's an issue
        
        # Company name and title
        company_name = session.get('company_name', 'Engineering Company')
        company_para = Paragraph(f"<b>{company_name}</b>", styles['Heading1'])
        elements.append(company_para)
        elements.append(Spacer(1, 10))
        
        # Title
        title = Paragraph("Storage Tank Design Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 20))
        
        # Design parameters table
        param_data = [
            ['Parameter', 'Value', 'Standard/Source'],
            ['Production Rate', '100 TPD', 'User Input'],
            ['Holding Period', '7 days', 'User Input'],
            ['Density', '1049 kg/m³', 'Acetic Acid Properties'],
            ['Fill Fraction', '85%', 'API 650 Recommendation'],
            ['Corrosion Allowance', '1.5 mm', 'API 650 for Acetic Acid'],
            ['Material', 'SS316L', 'Corrosion Resistance']
        ]
        
        param_table = Table(param_data)
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(Paragraph("Design Parameters", styles['Heading2']))
        elements.append(param_table)
        elements.append(Spacer(1, 20))
        
        # Tank specifications table
        tank_data = [
            ['Tank No', 'Chemical', 'Capacity (m³)', 'Diameter (m)', 'Height (m)', 'Shell Thickness (mm)'],
            ['1', 'Acetic Acid', '100', '6.0', '3.5', '8'],
            ['2', 'Acetic Acid', '100', '6.0', '3.5', '8']
        ]
        
        tank_table = Table(tank_data)
        tank_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(Paragraph("Tank Specifications", styles['Heading2']))
        elements.append(tank_table)
        elements.append(Spacer(1, 20))
        
        # Footer note
        footer = Paragraph("Design based on API 650 Standard for Welded Tanks for Oil Storage", 
                          styles['Normal'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name='acetic_acid_tank_design.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logging.error(f"PDF export error: {str(e)}")
        flash('Error generating PDF file.', 'error')
        return redirect(url_for('design'))

@app.route('/clear_cases', methods=['POST'])
def clear_cases():
    """Clear all saved cases."""
    session.pop('saved_cases', None)
    session.modified = True
    flash('All saved cases cleared successfully!', 'success')
    return redirect(url_for('design'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
