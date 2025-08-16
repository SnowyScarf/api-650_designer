import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from calculations import TankDesignCalculator
from chemical_database import ChemicalDatabase
import io
import csv
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "a-very-secret-key")

# Initialize chemical database
chemical_db = ChemicalDatabase()


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/design')
def design():
    """Design form page."""
    chemicals = chemical_db.get_chemical_list()
    return render_template('design.html', chemicals=chemicals)


@app.route('/sds')
def sds():
    """Safety Data Sheet page."""
    return render_template('sds.html')


@app.route('/get_chemical_properties/<chemical_id>')
def get_chemical_properties(chemical_id):
    """API endpoint to get chemical properties."""
    chemical = chemical_db.get_chemical(chemical_id)
    if chemical:
        return jsonify(chemical)
    return jsonify({'error': 'Chemical not found'}), 404


@app.route('/save_case', methods=['POST'])
def save_case():
    """Save a calculation case for comparison."""
    case_name = request.form.get('case_name', 'Case 1')
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
    return redirect(url_for('results_page'))


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
        production_rate = float(request.form.get('production_rate', 0))
        holding_period = float(request.form.get('holding_period', 0))
        density = float(request.form.get('density', 1000))
        max_fill_fraction = float(request.form.get('max_fill_fraction', 85)) / 100.0
        corrosion_allowance = float(request.form.get('corrosion_allowance', 1.5))
        num_tanks = int(request.form.get('num_tanks', 2))
        design_margin = float(request.form.get('design_margin', 10)) / 100.0
        
        chemical_id = request.form.get('chemical_name')
        chemical_display_name = 'Custom Liquid'
        if chemical_id:
            chemical_properties = chemical_db.get_chemical(chemical_id)
            if chemical_properties:
                chemical_display_name = chemical_properties.get('name', chemical_id)

        if production_rate <= 0 or holding_period <= 0:
            flash('Production rate and holding period must be positive.', 'error')
            return redirect(url_for('design'))

        calculator = TankDesignCalculator(
            production_rate=production_rate, holding_period=holding_period, density=density,
            chemical_name=chemical_display_name, max_fill_fraction=max_fill_fraction,
            corrosion_allowance=corrosion_allowance, num_tanks=num_tanks, design_margin=design_margin
        )
        results = calculator.calculate_tank_design()
        chart_data = calculator.generate_thickness_chart_data()
        
        session['chart_data'] = chart_data
        session['current_results'] = results
        session['current_inputs'] = {
            'production_rate': production_rate, 'holding_period': holding_period, 'density': density,
            'chemical_name': chemical_display_name, 'max_fill_fraction': max_fill_fraction * 100,
            'corrosion_allowance': corrosion_allowance, 'num_tanks': num_tanks,
            'design_margin': design_margin * 100
        }
        session.modified = True
        return redirect(url_for('results_page'))

    except Exception as e:
        logging.error(f"Calculation error: {str(e)}")
        flash('An error occurred during calculation. Please check your inputs.', 'error')
        return redirect(url_for('design'))

@app.route('/results')
def results_page():
    """Displays the results of the calculation."""
    if 'current_results' not in session:
        flash('No results to display. Please run a calculation first.', 'error')
        return redirect(url_for('design'))
    return render_template('results.html', results=session['current_results'],
                           chart_data=session['chart_data'], inputs=session['current_inputs'])


@app.route('/export/csv')
def export_csv():
    """Export tank design results to CSV format."""
    if 'current_results' not in session:
        flash('No results to export.', 'error')
        return redirect(url_for('design'))

    results = session['current_results']
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Tank Specifications'])
    headers = results.get('tank_specifications', [{}])[0].keys()
    writer.writerow(headers)
    for tank in results.get('tank_specifications', []):
        writer.writerow(tank.values())
    csv_data = output.getvalue().encode('utf-8')
    return send_file(io.BytesIO(csv_data), as_attachment=True,
                     download_name='tank_design_results.csv', mimetype='text/csv')


@app.route('/clear_cases', methods=['POST'])
def clear_cases():
    """Clear all saved cases."""
    session.pop('saved_cases', None)
    flash('All saved cases cleared!', 'success')
    return redirect(url_for('design'))

# --- MODIFICATION START ---
# The export_pdf function has been fully restored.
@app.route('/export/pdf')
def export_pdf():
    """Export tank design results to PDF format."""
    try:
        results = session.get('current_results')
        inputs = session.get('current_inputs')

        if not results or not inputs:
            flash('No calculation results to export.', 'error')
            return redirect(url_for('results_page'))

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Storage Tank Design Report", styles['Title']))
        elements.append(Spacer(1, 20))

        # Design parameters table
        param_data = [
            ['Parameter', 'Value', 'Standard/Source'],
            ['Production Rate', f"{inputs.get('production_rate', '')} TPD", 'User Input'],
            ['Holding Period', f"{inputs.get('holding_period', '')} days", 'User Input'],
            ['Density', f"{inputs.get('density', '')} kg/m³", 'Chemical Property'],
            ['Fill Fraction', f"{inputs.get('max_fill_fraction', '')} %", 'API 650 Rec.'],
            ['Design Margin', f"{inputs.get('design_margin', '')} %", 'User Input'],
            ['Corrosion Allowance', f"{inputs.get('corrosion_allowance', '')} mm", 'Project Basis'],
            ['Material', 'SS316L', 'Corrosion Resistance']
        ]
        param_table = Table(param_data)
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(Paragraph("Design Parameters", styles['Heading2']))
        elements.append(param_table)
        elements.append(Spacer(1, 20))

        # Tank specifications table
        tank_data = [['Tank No', 'Chemical', 'Capacity (m³)', 'Diameter (m)', 'Height (m)', 'Shell Thickness (mm)']]
        for tank in results.get('tank_specifications', []):
            tank_data.append([
                tank.get('tank_no', ''),
                tank.get('chemical', ''),
                f"{tank.get('capacity', 0):.1f}",
                f"{tank.get('diameter', 0):.1f}",
                f"{tank.get('height', 0):.1f}",
                tank.get('shell_thickness', '')
            ])
        tank_table = Table(tank_data)
        tank_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(Paragraph("Tank Specifications", styles['Heading2']))
        elements.append(tank_table)
        elements.append(Spacer(1, 20))

        elements.append(Paragraph("Design based on API 650 Standard.", styles['Normal']))

        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer, as_attachment=True,
            download_name='tank_design.pdf', mimetype='application/pdf'
        )

    except Exception as e:
        logging.error(f"PDF export error: {str(e)}")
        flash('Error generating PDF file.', 'error')
        return redirect(url_for('results_page'))
# --- MODIFICATION END ---

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
