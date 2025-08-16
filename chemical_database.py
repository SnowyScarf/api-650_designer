


class ChemicalDatabase:
    """Database of chemical properties for storage tank design."""

    def __init__(self):
        """Initialize the chemical database with predefined chemicals."""
        self.chemicals = {
            'ethyl_acetate': {
                'name': 'Ethyl Acetate',
                'formula': 'C4H8O2',
                'density': 902,  # kg/m³
                'boiling_point': 77.1,  # °C
                'corrosivity': 'Low',
                'recommended_material': 'SS304/SS316',
                'corrosion_allowance': 0.5,  # mm
                'category': 'Ester'
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
            'water': {
                'name': 'Water (Process)',
                'formula': 'H2O',
                'density': 1000,  # kg/m³
                'boiling_point': 100,  # °C
                'corrosivity': 'Low',
                'recommended_material': 'Carbon Steel',
                'corrosion_allowance': 1.5,  # mm
                'category': 'Inorganic'
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