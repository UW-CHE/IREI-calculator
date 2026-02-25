"""
One-time script: clean JCRImpactFactors2025.xlsx and produce jcr_if.csv.

Output columns: issn, eissn, journal_name, jif_2024, jif_quartile
ISSN values are stored bare (no hyphens) for fast lookup.

Run once:  python build_jcr_lookup.py
"""

import pandas as pd

SRC = 'JCRImpactFactors2025.xlsx'
DST = 'jcr_if.csv'

df = pd.read_excel(SRC, dtype={'ISSN': str, 'eISSN': str})

# Drop exact duplicate rows
before = len(df)
df = df.drop_duplicates()
print(f"Exact duplicates removed: {before - len(df)}")

# Normalise ISSN columns: strip hyphens, treat 'nan' / NaN as empty string
for col in ('ISSN', 'eISSN'):
    df[col] = df[col].fillna('').str.replace('-', '', regex=False).str.strip()
    df[col] = df[col].apply(lambda v: '' if v.lower() == 'nan' else v)

# Ensure JIF 2024 is numeric
df['JIF 2024'] = pd.to_numeric(df['JIF 2024'], errors='coerce')

# For the rare ISSN collision (different journals sharing a print ISSN),
# keep the row with the higher JIF so neither entry is silently lost.
df = df.sort_values('JIF 2024', ascending=False)
df = df.drop_duplicates(subset='ISSN', keep='first')

# Rename and keep only the columns the app needs
out = df.rename(columns={
    'Journal Name': 'journal_name',
    'ISSN':         'issn',
    'eISSN':        'eissn',
    'JIF 2024':     'jif_2024',
    'JIF Quartile': 'jif_quartile',
})[['issn', 'eissn', 'journal_name', 'jif_2024', 'jif_quartile']]

out = out.sort_values('jif_2024', ascending=False).reset_index(drop=True)

out.to_csv(DST, index=False)
print(f"Wrote {len(out):,} journals to {DST}")
print(f"Sample:\n{out.head(5).to_string(index=False)}")
