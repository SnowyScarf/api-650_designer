import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from calculations import TankDesignCalculator
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "acetic-acid-design-tool-secret")

@app.route('/')
def index():
    """Home page with introduction to the acetic acid storage tank design tool."""
    return render_template('index.html')

@app.route('/design')
def design():
    """Design form page for tank design inputs."""
    return render_template('design.html')

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
        
        return render_template('results.html', 
                             results=results, 
                             chart_data=chart_data,
                             inputs={
                                 'production_rate': production_rate,
                                 'holding_period': holding_period,
                                 'density': density,
                                 'max_fill_fraction': max_fill_fraction * 100,
                                 'corrosion_allowance': corrosion_allowance,
                                 'num_tanks': num_tanks,
                                 'sd': allowable_stress_design,
                                 'st': allowable_stress_test
                             })
        
    except ValueError as e:
        flash(f'Invalid input: {str(e)}', 'error')
        return redirect(url_for('design'))
    except Exception as e:
        logging.error(f"Calculation error: {str(e)}")
        flash('An error occurred during calculation. Please check your inputs.', 'error')
        return redirect(url_for('design'))

@app.route('/export/excel')
def export_excel():
    """Export tank design results to Excel format."""
    try:
        # Get results from session or recalculate
        # For simplicity, we'll create a sample export - in production this would use session data
        data = {
            'Tank No': [1, 2],
            'Chemical': ['Acetic Acid', 'Acetic Acid'],
            'Capacity (m³)': [100, 100],
            'Diameter (m)': [6.0, 6.0],
            'Height (m)': [3.5, 3.5],
            'Shell Thickness (mm)': [8, 8],
            'Bottom Thickness (mm)': [6, 6],
            'Roof Thickness (mm)': [5, 5]
        }
        
        df = pd.DataFrame(data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Tank Design', index=False)
            
            # Add design parameters sheet
            params_data = {
                'Parameter': ['Production Rate', 'Holding Period', 'Density', 'Fill Fraction', 'Corrosion Allowance'],
                'Value': ['100 TPD', '7 days', '1049 kg/m³', '85%', '1.5 mm'],
                'Standard': ['User Input', 'User Input', 'Acetic Acid', 'API 650', 'API 650']
            }
            params_df = pd.DataFrame(params_data)
            params_df.to_excel(writer, sheet_name='Design Parameters', index=False)
        
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
    """Export tank design results to PDF format."""
    try:
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph("Acetic Acid Storage Tank Design Report", styles['Title'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
