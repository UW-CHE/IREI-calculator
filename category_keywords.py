"""
Shared category keywords for journal categorization.
Used by both script.py and download_scimago.py to ensure consistent categorization.
"""

CATEGORY_KEYWORDS = {
    'Biotechnology and Biomedical Engineering': [
        'biotechnology', 'biotech', 'biomedical', 'biomaterial', 'tissue engineering',
        'biomechanics', 'bioengineering', 'medicine', 'pharmaceutical', 'drug',
        'clinical', 'medical', 'health', 'biomed', 'biosensor', 'protein', 'cell',
        'gene', 'therapeutic', 'diagnostic', 'biochemical', 'molecular biology',
        'biology', 'genetics', 'immunology', 'microbiology', 'pharmacology',
        'biophysics', 'bioprocess'
    ],
    'Electrochemical Engineering': [
        'electrochemistry', 'electrochemical', 'electrochimica', 'battery', 'batteries',
        'fuel cell', 'corrosion', 'electrocatalysis', 'electrode', 'electrolysis',
        'electrodeposition', 'voltammetry', 'redox', 'ionic', 'supercapacitor',
        'electroanal', 'electroanalytical', 'power sources', 'vanadium', 'lithium',
        'flow battery', 'energy storage', 'energy technology', 'energy materials',
        'energy &', 'energy engineering', 'fuel technology', 'power technology',
        'electrochemical energy'
    ],
    'Nanotechnology for Advanced Materials': [
        'nano', 'nanomaterial', 'nanotechnology', 'nanoparticle', 'nanostructure',
        'nanoscale', 'quantum', 'quantum dot', 'carbon nanotube', 'graphene',
        'thin film', 'nanocomposite', 'metamaterial', 'advanced material',
        '2d material', 'ceramics', 'composite', 'materials science',
        'materials chemistry'
    ],
    'Process Systems Engineering': [
        'chemical engineering', 'process engineering', 'industrial chemistry',
        'process control', 'process system', 'process design', 'optimization',
        'simulation', 'modeling', 'systems engineering', 'process safety',
        'industrial', 'manufacturing', 'automation', 'operations research',
        'supply chain', 'process intensification', 'plant design', 'unit operations',
        'industrial & engineering'
    ],
    'Soft Matter & Polymer Engineering': [
        'polymer', 'polymers', 'rheology', 'soft matter', 'colloid', 'gel',
        'emulsion', 'macromolecule', 'plastic', 'rubber', 'elastomer',
        'polymerization', 'copolymer', 'thermoplastic', 'thermoplastics', 'resin',
        'foam', 'viscoelastic', 'self-assembly', 'complex fluid', 'macromolecular'
    ],
    'Sustainable Reaction Engineering': [
        'sustainable', 'green chemistry', 'renewable', 'biofuel', 'biomass',
        'catalysis', 'reaction engineering', 'environmental', 'carbon capture',
        'waste', 'recycling', 'circular economy', 'clean energy', 'solar',
        'hydrogen', 'sustainability', 'photovoltaic', 'renewable energy', 'co2',
        'emission', 'climate'
    ],
    # Multidisciplinary journals are identified primarily by exact phrases in
    # their titles.  Multi-word phrases prevent false matches on partial words.
    # 'nature' is a standalone word because "Nature" (journal) has no other
    # distinguishing term; specific sub-brands like "Nature Biotechnology"
    # still win because their field keyword scores are twice as high.
    'Multidisciplinary & Core Engineering': [
        'multidisciplinary', 'interdisciplinary', 'nature',
        'scientific reports', 'nature communications', 'science advances',
        'pnas nexus', 'rsc advances', 'acs omega', 'acs central science',
        'communications chemistry', 'cell reports physical', 'iscience',
        'national science review', 'one earth', 'ccs chemistry',
        'aggregate', 'plos one', 'heliyon', 'royal society open science',
    ]
}

# All categories list for convenience
CATEGORIES = list(CATEGORY_KEYWORDS.keys())
DEFAULT_CATEGORY = 'Multidisciplinary & Core Engineering'
