"""
Chemical Database for Storage Tank Design
Contains properties for various chemicals used in storage tank design.
"""

class ChemicalDatabase:
    """Database of chemical properties for storage tank design."""
    
    def __init__(self):
        """Initialize the chemical database with predefined chemicals."""
        self.chemicals = {
            'acetic_acid': {
                'name': 'Acetic Acid (Concentrated)',
                'formula': 'CH3COOH',
                'density': 1049,  # kg/m³
                'boiling_point': 118.1,  # °C
                'corrosivity': 'High',
                'recommended_material': 'SS316L',
                'corrosion_allowance': 1.5,  # mm
                'category': 'Organic Acid'
            },
            'sulfuric_acid': {
                'name': 'Sulfuric Acid (98%)',
                'formula': 'H2SO4',
                'density': 1840,  # kg/m³
                'boiling_point': 337,  # °C
                'corrosivity': 'Very High',
                'recommended_material': 'SS316L/Hastelloy C',
                'corrosion_allowance': 3.0,  # mm
                'category': 'Inorganic Acid'
            },
            'hydrochloric_acid': {
                'name': 'Hydrochloric Acid (37%)',
                'formula': 'HCl',
                'density': 1190,  # kg/m³
                'boiling_point': 110,  # °C
                'corrosivity': 'Very High',
                'recommended_material': 'HDPE/FRP',
                'corrosion_allowance': 0.0,  # mm (non-metallic)
                'category': 'Inorganic Acid'
            },
            'sodium_hydroxide': {
                'name': 'Sodium Hydroxide (50%)',
                'formula': 'NaOH',
                'density': 1530,  # kg/m³
                'boiling_point': 140,  # °C
                'corrosivity': 'High',
                'recommended_material': 'SS316L',
                'corrosion_allowance': 1.5,  # mm
                'category': 'Caustic'
            },
            'methanol': {
                'name': 'Methanol',
                'formula': 'CH3OH',
                'density': 792,  # kg/m³
                'boiling_point': 64.7,  # °C
                'corrosivity': 'Low',
                'recommended_material': 'SS304/SS316',
                'corrosion_allowance': 0.5,  # mm
                'category': 'Alcohol'
            },
            'ethanol': {
                'name': 'Ethanol (95%)',
                'formula': 'C2H5OH',
                'density': 810,  # kg/m³
                'boiling_point': 78.4,  # °C
                'corrosivity': 'Low',
                'recommended_material': 'SS304/SS316',
                'corrosion_allowance': 0.5,  # mm
                'category': 'Alcohol'
            },
            'ammonia': {
                'name': 'Ammonia (25% aqueous)',
                'formula': 'NH3',
                'density': 910,  # kg/m³
                'boiling_point': 100,  # °C (aqueous solution)
                'corrosivity': 'Medium',
                'recommended_material': 'SS316L',
                'corrosion_allowance': 1.0,  # mm
                'category': 'Base'
            },
            'benzene': {
                'name': 'Benzene',
                'formula': 'C6H6',
                'density': 879,  # kg/m³
                'boiling_point': 80.1,  # °C
                'corrosivity': 'Low',
                'recommended_material': 'Carbon Steel',
                'corrosion_allowance': 1.5,  # mm
                'category': 'Aromatic Hydrocarbon'
            },
            'toluene': {
                'name': 'Toluene',
                'formula': 'C7H8',
                'density': 867,  # kg/m³
                'boiling_point': 110.6,  # °C
                'corrosivity': 'Low',
                'recommended_material': 'Carbon Steel',
                'corrosion_allowance': 1.5,  # mm
                'category': 'Aromatic Hydrocarbon'
            },
            'acetone': {
                'name': 'Acetone',
                'formula': 'C3H6O',
                'density': 784,  # kg/m³
                'boiling_point': 56.0,  # °C
                'corrosivity': 'Low',
                'recommended_material': 'SS304',
                'corrosion_allowance': 0.5,  # mm
                'category': 'Ketone'
            },
            'water': {
                'name': 'Water (Process)',
                'formula': 'H2O',
                'density': 1000,  # kg/m³
                'boiling_point': 100,  # °C
                'corrosivity': 'Low',
                'recommended_material': 'Carbon Steel',
                'corrosion_allowance': 1.5,  # mm
                'category': 'Inorganic'
            }
        }
    
    def get_chemical(self, chemical_id):
        """Get chemical properties by ID."""
        return self.chemicals.get(chemical_id, None)
    
    def get_all_chemicals(self):
        """Get all chemicals in the database."""
        return self.chemicals
    
    def get_chemicals_by_category(self, category):
        """Get chemicals filtered by category."""
        return {k: v for k, v in self.chemicals.items() if v['category'] == category}
    
    def get_chemical_list(self):
        """Get a list of chemicals for dropdown selection."""
        return [(k, v['name']) for k, v in self.chemicals.items()]
    
    def search_chemicals(self, query):
        """Search chemicals by name or formula."""
        query = query.lower()
        results = {}
        for k, v in self.chemicals.items():
            if (query in v['name'].lower() or 
                query in v['formula'].lower() or 
                query in v['category'].lower()):
                results[k] = v
        return results