"""
Acetic Acid Storage Tank Design Calculations
Based on API 650 Standard for Welded Tanks for Oil Storage
"""
import math
import logging

class TankDesignCalculator:
    """
    Calculator for acetic acid storage tank design following API 650 standards.
    """
    
    # Standard plate thicknesses (mm) - API 650 Appendix A
    STANDARD_THICKNESSES = [5, 6, 8, 10, 12, 16, 19, 22, 25, 28, 32, 38, 44, 50]
    
    def __init__(self, production_rate, holding_period, density=1049, 
                 max_fill_fraction=0.85, corrosion_allowance=1.5, num_tanks=2,
                 allowable_stress_design=138, allowable_stress_test=207):
        """
        Initialize tank design calculator.
        
        Args:
            production_rate (float): Production rate in TPD (tonnes per day)
            holding_period (float): Storage period in days
            density (float): Liquid density in kg/m³ (default: 1049 for acetic acid)
            max_fill_fraction (float): Maximum fill fraction (default: 0.85)
            corrosion_allowance (float): Corrosion allowance in mm (default: 1.5)
            num_tanks (int): Number of storage tanks (default: 2)
            allowable_stress_design (float): Design stress in MPa (default: 138 for SS316L)
            allowable_stress_test (float): Test stress in MPa (default: 207 for SS316L)
        """
        self.production_rate = production_rate  # TPD
        self.holding_period = holding_period    # days
        self.density = density                  # kg/m³
        self.max_fill_fraction = max_fill_fraction
        self.corrosion_allowance = corrosion_allowance  # mm
        self.num_tanks = num_tanks
        self.allowable_stress_design = allowable_stress_design  # MPa
        self.allowable_stress_test = allowable_stress_test      # MPa
        
        # Conversion factors
        self.gravity = 9.81  # m/s²
        
        logging.info(f"Tank calculator initialized for {production_rate} TPD, {holding_period} days storage")
    
    def calculate_storage_volume(self):
        """
        Calculate total storage volume required.
        
        Returns:
            dict: Storage volume calculations
        """
        # Total mass to be stored (tonnes)
        total_mass = self.production_rate * self.holding_period
        
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
        # Optimal D:H ratio for storage tanks (API 650 recommendation)
        dh_ratio = 1.7  # H/D ratio
        
        # For cylindrical tank: V = π * D²/4 * H
        # With H = dh_ratio * D: V = π * D²/4 * dh_ratio * D = π * D³ * dh_ratio / 4
        # Solving for D: D = (4V / (π * dh_ratio))^(1/3)
        
        diameter = (4 * volume_per_tank / (math.pi * dh_ratio)) ** (1/3)
        height = dh_ratio * diameter
        
        # Round to practical values
        diameter = round(diameter, 1)
        height = round(height, 1)
        
        # Recalculate actual volume
        actual_volume = math.pi * (diameter ** 2) / 4 * height
        
        return {
            'diameter': diameter,
            'height': height,
            'actual_volume': actual_volume,
            'dh_ratio': height / diameter
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
        # Convert to feet for API 650 formulas
        diameter_ft = diameter * 3.28084
        height_ft = height * 3.28084
        
        # Specific gravity (relative to water)
        specific_gravity = self.density / 1000
        
        # Design condition thickness (API 650 Eq. 5.6.3.2-1)
        # td = (Sd × 4.9 × D × (H - 0.3) × G) + CA
        # Note: Using metric conversion and proper units
        
        # Design stress in API units (psi) - convert from MPa
        sd_psi = self.allowable_stress_design * 145.038
        st_psi = self.allowable_stress_test * 145.038
        
        # Design thickness (inches)
        td_inches = (sd_psi * 4.9 * diameter_ft * (height_ft - 0.3) * specific_gravity) / 1000000
        
        # Test condition thickness (inches)
        tt_inches = (st_psi * 4.9 * diameter_ft * (height_ft - 0.3)) / 1000000
        
        # Take maximum and add corrosion allowance
        required_thickness_inches = max(td_inches, tt_inches) + (self.corrosion_allowance / 25.4)
        
        # Convert to mm
        required_thickness_mm = required_thickness_inches * 25.4
        
        # Round up to next standard thickness
        shell_thickness = self._round_to_standard_thickness(required_thickness_mm)
        
        return {
            'required_thickness': round(required_thickness_mm, 2),
            'shell_thickness': shell_thickness,
            'design_thickness': round(td_inches * 25.4, 2),
            'test_thickness': round(tt_inches * 25.4, 2)
        }
    
    def calculate_bottom_thickness(self):
        """
        Calculate bottom plate thickness per API 650.
        
        Returns:
            float: Bottom thickness in mm
        """
        # API 650 minimum bottom thickness + corrosion allowance
        min_bottom = 6  # mm minimum per API 650
        return min_bottom + self.corrosion_allowance
    
    def calculate_roof_thickness(self):
        """
        Calculate roof plate thickness for atmospheric tank.
        
        Returns:
            float: Roof thickness in mm
        """
        # API 650 minimum roof thickness + corrosion allowance
        min_roof = 5  # mm minimum per API 650
        return min_roof + self.corrosion_allowance
    
    def calculate_bund_volume(self, tank_volume):
        """
        Calculate bund (containment) volume.
        
        Args:
            tank_volume (float): Individual tank volume in m³
            
        Returns:
            float: Required bund volume in m³
        """
        # 110% of largest tank capacity
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
            tank_spec = {
                'tank_no': i + 1,
                'chemical': 'Acetic Acid',
                'capacity': round(dimensions['actual_volume'], 1),
                'diameter': dimensions['diameter'],
                'height': dimensions['height'],
                'shell_thickness': shell_data['shell_thickness'],
                'bottom_thickness': bottom_thickness,
                'roof_thickness': roof_thickness
            }
            results['tank_specifications'].append(tank_spec)
        
        logging.info(f"Tank design completed: {self.num_tanks} tanks, {dimensions['diameter']}m × {dimensions['height']}m")
        
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
        base_diameter = base_dimensions['diameter']
        
        heights = []
        thicknesses = []
        
        # Vary height from 50% to 150% of optimal
        for height_factor in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]:
            height = base_dimensions['height'] * height_factor
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
