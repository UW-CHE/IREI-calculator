#!/usr/bin/env python3
"""
Create curated_journals_by_category.json from top_journals_by_hamed.json
Looks up journal metrics from OpenAlex for any journals not in journals_by_category.json
"""

import json
import requests
import time

# Load both files
with open('top_journals_by_hamed.json', 'r') as f:
    hamed_journals = json.load(f)

with open('journals_by_category.json', 'r') as f:
    all_journals = json.load(f)

def normalize_name(name):
    """Normalize journal name for matching"""
    return name.lower().strip().replace('&', 'and').replace('.', '').replace('  ', ' ')

def get_journal_from_openalex(journal_name):
    """Query OpenAlex for journal metrics"""
    try:
        # Search for the journal
        search_url = "https://api.openalex.org/sources"
        params = {
            'search': journal_name,
            'per_page': 5
        }
        
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Find best match
        for source in data.get('results', []):
            source_name = source.get('display_name', '')
            if normalize_name(source_name) == normalize_name(journal_name):
                # Found exact match
                summary_stats = source.get('summary_stats', {})
                return {
                    'name': source.get('display_name'),
                    'issn': source.get('issn_l', 'N/A'),
                    'h_index': summary_stats.get('h_index', 0),
                    'impact_factor': round(summary_stats.get('2yr_mean_citedness', 0), 2),
                    'publisher': source.get('host_organization_name', 'Unknown'),
                    'works_count': source.get('works_count', 0),
                    'cited_by_count': source.get('cited_by_count', 0),
                    'openalex_id': source.get('id', '')
                }
        
        # If no exact match, return first result if close enough
        if data.get('results'):
            source = data['results'][0]
            summary_stats = source.get('summary_stats', {})
            return {
                'name': source.get('display_name'),
                'issn': source.get('issn_l', 'N/A'),
                'h_index': summary_stats.get('h_index', 0),
                'impact_factor': round(summary_stats.get('2yr_mean_citedness', 0), 2),
                'publisher': source.get('host_organization_name', 'Unknown'),
                'works_count': source.get('works_count', 0),
                'cited_by_count': source.get('cited_by_count', 0),
                'openalex_id': source.get('id', '')
            }
        
    except Exception as e:
        print(f"  Error fetching {journal_name}: {e}")
    
    return None

# Build curated database
curated = {}

for category in hamed_journals.keys():
    print(f'\n{category}:')
    curated[category] = []
    
    # Get the list of journal names from hamed's file for this category
    hamed_names = {normalize_name(name): name for name in hamed_journals[category]}
    
    # First, try to find matching journals in journals_by_category
    found_names = set()
    if category in all_journals:
        for journal in all_journals[category]:
            journal_name_normalized = normalize_name(journal['name'])
            
            # Check if this journal is in hamed's list
            if journal_name_normalized in hamed_names:
                curated[category].append(journal)
                found_names.add(journal_name_normalized)
                print(f'  ✓ Found in cache: {journal["name"]}')
    
    # For journals not found, query OpenAlex
    missing_names = set(hamed_names.keys()) - found_names
    for norm_name in missing_names:
        original_name = hamed_names[norm_name]
        print(f'  ⟳ Querying OpenAlex: {original_name}')
        
        journal_data = get_journal_from_openalex(original_name)
        if journal_data:
            curated[category].append(journal_data)
            print(f'    → Added: {journal_data["name"]} (h-index: {journal_data["h_index"]})')
        else:
            print(f'    ✗ Not found')
        
        # Be nice to the API
        time.sleep(0.2)
    
    print(f'  Total: {len(curated[category])} journals')

# Save to new file
with open('curated_journals_by_category.json', 'w') as f:
    json.dump(curated, f, indent=2)

print(f'\n✓ Created curated_journals_by_category.json')

# Show summary
total = sum(len(journals) for journals in curated.values())
print(f'Total journals: {total}')
