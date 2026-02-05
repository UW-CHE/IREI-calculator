# DOI Checker - Journal Metrics and Categorization

This tool provides comprehensive journal metrics and categorization for academic papers using their DOI.

## Features

1. **Get Journal Metrics from DOI** - Extract comprehensive metrics for any journal
2. **Automatic Categorization** - Categorize journals into 7 research areas
3. **Top Journals Database** - Generate lists of top 25 journals in each category

## Research Categories

1. Biotechnology and Biomedical Engineering
2. Electrochemical Engineering
3. Nanotechnology for Advanced Materials
4. Process Systems Engineering
5. Soft Matter & Polymer Engineering
6. Sustainable Reaction Engineering
7. Multidisciplinary & Core Engineering

## Usage

### Get Metrics for a Single Journal

```python
from script import get_journal_metrics

doi = "10.1016/j.electacta.2025.147532"
metrics = get_journal_metrics(doi)

print(f"Journal: {metrics['journal_name']}")
print(f"Category: {metrics['category']}")
print(f"Impact Factor: {metrics['impact_factor']}")
print(f"h-index: {metrics['h_index']}")
```

### Generate Top Journals List

Run the script to generate a comprehensive list:

```bash
python generate_top_journals.py
```

This creates `top_journals_by_category.txt` with the top 25 journals in each category.

### Available Metrics

The `get_journal_metrics()` function returns:

- `journal_name`: Name of the journal
- `category`: Research area classification
- `issn`: International Standard Serial Number
- `impact_factor`: 2-year impact factor
- `h_index`: h-index (cumulative impact measure)
- `i10_index`: Number of papers with ≥10 citations
- `mean_citedness_2y`: Average citations per paper (2-year window)
- `citations_per_paper`: Overall citation rate
- `papers_count`: Total papers published
- `cited_by_count`: Total citations received
- `publication_growth_rate`: Growth trend (5-year comparison)
- `publisher`: Publisher name
- `country`: Country code
- `oa_works_count`: Open access paper count
- `apc_usd`: Article processing charge (USD)
- `counts_by_year`: Yearly publication/citation data

## Data Sources

- **CrossRef API**: DOI metadata and journal information
- **OpenAlex**: Comprehensive journal metrics, topics, and classifications

## Notes

- Impact Factor and mean_citedness_2y use the same metric (2-year citation average)
- h-index serves as an open alternative to Eigenfactor for measuring journal impact
- Categorization uses weighted scoring: journal name (10x) > article topics (2x) > article keywords (1.5x) > journal topics (1x)
