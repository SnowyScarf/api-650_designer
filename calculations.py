"""
Generic Storage Tank Design Calculations
Based on API 650 Standard for Welded Tanks for Oil Storage
"""
import math
import logging


class TankDesignCalculator:
    """
    Calculator for generic storage tank design following API 650 standards.
    """

    # Standard plate thicknesses (mm) - API 650 Appendix A
    STANDARD_THICKNESSES = [5, 6, 8, 10, 12, 16, 19, 22, 25, 28, 32, 38, 44, 50]

    # --- MODIFICATION START ---
    # The __init__ method is now generic. It requires a density and accepts an optional chemical_name.
    def __init__(self, production_rate, holding_period, density=1000.0, chemical_name="Liquid",
                 max_fill_fraction=0.85, corrosion_allowance=1.5, num_tanks=2, design_margin=0.10):
        """
        Initialize tank design calculator.

        Args:
            production_rate (float): Production rate in TPD (tonnes per day)
            holding_period (float): Storage period in days
            density (float): Liquid density in kg/m³
            chemical_name (str): Name of the chemical being stored
            max_fill_fraction (float): Maximum fill fraction (default: 0.85)
            corrosion_allowance (float): Corrosion allowance in mm (default: 1.5)
            num_tanks (int): Number of storage tanks (default: 2)
            design_margin (float): Design margin as a fraction (e.g., 0.10 for 10%)
        """
        self.production_rate = production_rate  # TPD
        self.holding_period = holding_period  # days
        self.density = density  # kg/m³
        self.chemical_name = chemical_name
        self.max_fill_fraction = max_fill_fraction
        self.corrosion_allowance = corrosion_allowance  # mm
        self.num_tanks = num_tanks
        self.design_margin = design_margin  # e.g., 0.10 for 10%

        # Allowable stress values are fixed internally for SS316L.
        self.allowable_stress_design = 138.0  # MPa for SS316L
        self.allowable_stress_test = 207.0  # MPa for SS316L

        # Conversion factors
        self.gravity = 9.81  # m/s²

        logging.info(f"Tank calculator initialized for {production_rate} TPD of {chemical_name}, {holding_period} days storage with a {design_margin*100}% margin.")

    def calculate_storage_volume(self):
        """
        Calculate total storage volume required.

        Returns:
            dict: Storage volume calculations
        """
        # Apply the design margin to the production rate
        adjusted_production_rate = self.production_rate * (1 + self.design_margin)

        # Total mass to be stored (tonnes)
        total_mass = adjusted_production_rate * self.holding_period

        # Total volume required (m³)
        total_volume = (total_mass * 1000) / self.density  # Convert tonnes to kg

        # Geometric volume (accounting for fill fraction)
        geometric_volume = total_volume / self.max_fill_fraction

        # Volume per tank
        volume_per_tank = geometric_volume / self.num_tanks

        return {
            'total_mass': total_mass,
            'total_volume': total_volume,
            'geometric_volume': geometric_volume,
            'volume_per_tank': volume_per_tank
        }

    def optimize_tank_dimensions(self, volume_per_tank):
        """
        Optimize tank dimensions for given volume using D:H ratio of 1:1.7.

        Args:
            volume_per_tank (float): Volume per tank in m³

        Returns:
            dict: Optimized dimensions
        """
        # Optimal H/D ratio for storage tanks
        dh_ratio = 1.7

        # Formula for cylinder volume: V = π * D³/4 * (H/D)
        # Solving for D: D = (4V / (π * dh_ratio))^(1/3)
        diameter = (4 * volume_per_tank / (math.pi * dh_ratio)) ** (1 / 3)
        height = dh_ratio * diameter

        # Round to practical values
        diameter = round(diameter, 1)
        height = round(height, 1)

        # Recalculate actual volume with rounded dimensions
        actual_volume = math.pi * (diameter ** 2) / 4 * height

        return {
            'diameter': diameter,
            'height': height,
            'actual_volume': actual_volume,
            'dh_ratio': height / diameter if diameter > 0 else 0
        }

    def calculate_shell_thickness(self, diameter, height):
        """
        Calculate shell thickness using API 650 One-Foot Method.

        Args:
            diameter (float): Tank diameter in meters
            height (float): Tank height in meters

        Returns:
            dict: Shell thickness calculations
        """
        # Convert metric inputs to imperial units for API 650 formulas
        diameter_ft = diameter * 3.28084
        # H is the design liquid level, which is the height of the tank shell
        height_ft = height * 3.28084

        # Specific gravity of the liquid (relative to water)
        specific_gravity = self.density / 1000

        # Convert allowable stress from MPa to psi for the formula
        sd_psi = self.allowable_stress_design * 145.038
        st_psi = self.allowable_stress_test * 145.038

        # Ensure height is sufficient for the (H-1) calculation
        if height_ft <= 1:
            # Handle cases for very short tanks where H-1 would be zero or negative
            td_inches = 0
            tt_inches = 0
        else:
            # Correct formula per API 650 Sec. 5.6.3.2: td = (2.6 * D * (H - 1) * G) / Sd
            td_inches = (2.6 * diameter_ft * (height_ft - 1) * specific_gravity) / sd_psi

            # Calculate thickness for hydrostatic test condition
            # tt = (2.6 * D * (H - 1)) / St
            tt_inches = (2.6 * diameter_ft * (height_ft - 1)) / st_psi

        # The required thickness before corrosion allowance is the larger of the two
        required_thickness_inches = max(td_inches, tt_inches)

        # Add the corrosion allowance (converted from mm to inches)
        total_required_thickness_inches = required_thickness_inches + (self.corrosion_allowance / 25.4)

        # API 650 also specifies an absolute minimum thickness based on diameter.
        # For tanks with diameter < 50 ft (~15.2m), the minimum is 3/16" (0.1875 inches).
        min_api_thickness_inches = 0.1875

        # The final required thickness is the greater of the calculated value and the API minimum
        final_thickness_inches = max(total_required_thickness_inches, min_api_thickness_inches)

        # Convert the final required thickness to mm for output
        required_thickness_mm = final_thickness_inches * 25.4

        # Select the next available standard plate size
        shell_thickness = self._round_to_standard_thickness(required_thickness_mm)

        return {
            'required_thickness': round(required_thickness_mm, 2),
            'shell_thickness': shell_thickness,
            'design_thickness_mm': round(td_inches * 25.4, 2),
            'test_thickness_mm': round(tt_inches * 25.4, 2)
        }

    def calculate_bottom_thickness(self):
        """
        Calculate bottom plate thickness per API 650.

        Returns:
            float: Bottom thickness in mm
        """
        # API 650 minimum bottom thickness + corrosion allowance
        min_bottom = 6  # mm minimum per API 650 Sec. 5.4.1
        return min_bottom + self.corrosion_allowance

    def calculate_roof_thickness(self):
        """
        Calculate roof plate thickness for atmospheric tank.

        Returns:
            float: Roof thickness in mm
        """
        # API 650 minimum roof thickness + corrosion allowance
        min_roof = 5  # mm minimum per API 650 Sec. 5.10.2.2
        return min_roof + self.corrosion_allowance

    def calculate_bund_volume(self, tank_volume):
        """
        Calculate bund (containment) volume.

        Args:
            tank_volume (float): Individual tank volume in m³

        Returns:
            float: Required bund volume in m³
        """
        # Typically 110% of largest tank capacity
        return tank_volume * 1.1

    def _round_to_standard_thickness(self, thickness):
        """
        Round thickness up to next standard plate thickness.

        Args:
            thickness (float): Required thickness in mm

        Returns:
            float: Standard thickness in mm
        """
        for std_thickness in self.STANDARD_THICKNESSES:
            if std_thickness >= thickness:
                return std_thickness

        # If larger than standard, return next multiple of 6mm
        return math.ceil(thickness / 6) * 6

    def calculate_tank_design(self):
        """
        Perform complete tank design calculation.

        Returns:
            dict: Complete design results
        """
        # Calculate storage volumes
        volume_data = self.calculate_storage_volume()

        # Optimize dimensions
        dimensions = self.optimize_tank_dimensions(volume_data['volume_per_tank'])

        # Calculate thicknesses
        shell_data = self.calculate_shell_thickness(dimensions['diameter'], dimensions['height'])
        bottom_thickness = self.calculate_bottom_thickness()
        roof_thickness = self.calculate_roof_thickness()

        # Calculate bund volume
        bund_volume = self.calculate_bund_volume(dimensions['actual_volume'])

        # Compile results
        results = {
            'storage': volume_data,
            'dimensions': dimensions,
            'shell': shell_data,
            'bottom_thickness': bottom_thickness,
            'roof_thickness': roof_thickness,
            'bund_volume': bund_volume,
            'tank_specifications': []
        }

        # Create tank specification table
        for i in range(self.num_tanks):
            # --- MODIFICATION START ---
            # The chemical name is now taken from the instance variable.
            tank_spec = {
                'tank_no': i + 1,
                'chemical': self.chemical_name,
                'capacity': round(dimensions['actual_volume'], 1),
                'diameter': dimensions['diameter'],
                'height': dimensions['height'],
                'shell_thickness': shell_data['shell_thickness'],
                'bottom_thickness': bottom_thickness,
                'roof_thickness': roof_thickness
            }
            # --- MODIFICATION END ---
            results['tank_specifications'].append(tank_spec)

        logging.info(
            f"Tank design completed: {self.num_tanks} tanks, {dimensions['diameter']}m × {dimensions['height']}m")

        return results

    def generate_thickness_chart_data(self):
        """
        Generate data for shell thickness vs height chart.

        Returns:
            dict: Chart data for Plotly.js
        """
        volume_data = self.calculate_storage_volume()
        volume_per_tank = volume_data['volume_per_tank']

        # Generate height range (keeping diameter constant based on volume)
        base_dimensions = self.optimize_tank_dimensions(volume_per_tank)

        heights = []
        thicknesses = []

        # Vary height from 50% to 150% of optimal
        for height_factor in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]:
            height = base_dimensions['height'] * height_factor
            if height == 0: continue
            # Adjust diameter to maintain volume
            diameter = math.sqrt(4 * volume_per_tank / (math.pi * height))

            shell_data = self.calculate_shell_thickness(diameter, height)

            heights.append(round(height, 1))
            thicknesses.append(shell_data['shell_thickness'])

        return {
            'heights': heights,
            'thicknesses': thicknesses,
            'title': 'Shell Thickness vs Tank Height',
            'x_title': 'Tank Height (m)',
            'y_title': 'Shell Thickness (mm)'
        }
