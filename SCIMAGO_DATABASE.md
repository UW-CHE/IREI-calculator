# Journal Database from SCImago Rankings

## Overview

Successfully processed **22,575 journals** from SCImago Journal Rankings 2024 and categorized them into 7 research areas.

## Database Files

1. **journals_by_category.json** - Machine-readable JSON database
   - Top 50 journals per category
   - Includes: name, ISSN, SJR score, h-index, publisher, country, categories

2. **top_journals_scimago.txt** - Human-readable text report
   - Formatted list of top journals by category
   - Easy to browse and reference

## Categories and Journal Counts

All categories contain **50 top-ranked journals**:

- ✓ Biotechnology and Biomedical Engineering: 50 journals
- ✓ Electrochemical Engineering: 50 journals  
- ✓ Nanotechnology for Advanced Materials: 50 journals
- ✓ Process Systems Engineering: 50 journals
- ✓ Soft Matter & Polymer Engineering: 50 journals
- ✓ Sustainable Reaction Engineering: 50 journals
- ✓ Multidisciplinary & Core Engineering: 50 journals

**Total: 350 curated journals**

## Ranking Methodology

Journals ranked by combined score:
- SJR Score (weighted higher for prestige)
- h-index (weighted for cumulative impact)
- Minimum threshold: h-index > 10 and SJR > 0

## Sample Top Journals by Category

### Biotechnology and Biomedical Engineering
1. Ca-A Cancer Journal for Clinicians (SJR: 145.004, h-index: 223)
2. Nature Reviews Molecular Cell Biology (SJR: 37.353, h-index: 531)
3. Cell (SJR: 22.612, h-index: 925)

### Electrochemical Engineering
1. Advanced Energy Materials (SJR: 7.776, h-index: 320)
2. Energy and Environmental Science (SJR: 7.632, h-index: 408)
3. Nano Energy (SJR: 5.182, h-index: 288)

### Soft Matter & Polymer Engineering
1. Progress in Polymer Science (SJR: 6.089, h-index: 346)
2. Acta Materialia (SJR: 2.972, h-index: 381)
3. Accounts of Materials Research (SJR: 4.358, h-index: 51)

## Usage

### Load JSON database in Python:
```python
import json

with open('journals_by_category.json', 'r') as f:
    journals = json.load(f)

# Get biotechnology journals
biotech_journals = journals['Biotechnology and Biomedical Engineering']

# Access journal data
for journal in biotech_journals[:5]:
    print(f"{journal['name']}: SJR={journal['sjr']}, h-index={journal['h_index']}")
```

### Query by category:
```python
# Find journals by country
us_journals = [j for j in biotech_journals if j['country'] == 'United States']

# Sort by h-index
sorted_journals = sorted(biotech_journals, key=lambda x: x['h_index'], reverse=True)

# Filter by SJR threshold
high_impact = [j for j in biotech_journals if j['sjr'] > 5.0]
```

## Data Source

- **Source**: SCImago Journal & Country Rank (SJR)
- **Year**: 2024 edition
- **Website**: https://www.scimagojr.com
- **Update Frequency**: Annual
- **License**: Free to use for research and analysis

## Regenerating the Database

To update with a newer SCImago file:

1. Download latest data from https://www.scimagojr.com/journalrank.php
2. Save as `scimagojr 2024.csv` (or update year)
3. Run: `python process_scimago_data.py`

The script will automatically process the file and regenerate both JSON and text outputs.

## Advantages Over OpenAlex Query Method

✓ **No API calls** - Instant access, no network delays  
✓ **Consistent data** - Same dataset for all queries  
✓ **Offline use** - Works without internet connection  
✓ **Curated rankings** - Pre-filtered and categorized  
✓ **Comprehensive** - 22,575 journals processed  
✓ **Authoritative** - SCImago is widely recognized in academia
