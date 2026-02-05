#!/usr/bin/env python3
"""
Download and process SCImago Journal Rankings data.
Categorizes journals into research areas and creates a local database.
"""

import requests
import csv
import json
from pathlib import Path
from category_keywords import CATEGORY_KEYWORDS, CATEGORIES, DEFAULT_CATEGORY


def download_scimago_data(output_file='scimago_journals.csv'):
    """
    Download the SCImago journal rankings CSV file.
    
    Note: SCImago provides their data through their website.
    You'll need to download it manually from:
    https://www.scimagojr.com/journalrank.php
    
    Click "Download data" button to get the CSV file.
    """
    print("=" * 80)
    print("SCIMAGO JOURNAL RANKINGS DOWNLOAD")
    print("=" * 80)
    print("\nTo get the SCImago data:")
    print("1. Visit: https://www.scimagojr.com/journalrank.php")
    print("2. Click 'Download data' button (free, no registration required)")
    print("3. Save the CSV file as 'scimagojr.csv' in this directory")
    print("\nOnce downloaded, run: python process_scimago.py")
    print("=" * 80)


def categorize_journal_scimago(journal_name, categories_str, areas_str):
    """
    Categorize a journal based on SCImago categories and subject areas.
    Can return multiple categories for a journal.
    
    Args:
        journal_name: Name of the journal
        categories_str: Semicolon-separated category string from SCImago
        areas_str: Semicolon-separated area string from SCImago
        
    Returns:
        List of category names (can be multiple)
    """
    # Combine text for searching
    text = f"{journal_name} {categories_str} {areas_str}".lower()
    
    # Score each category
    category_scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        
        # Journal name gets highest weight
        journal_lower = journal_name.lower()
        for keyword in keywords:
            if keyword in journal_lower:
                score += 5  # High weight for journal name match
        
        # Categories and areas from SCImago
        for keyword in keywords:
            if keyword in text:
                score += 1
        
        category_scores[category] = score
    
    # Return all categories with score > 0 (allows multiple categories)
    matched_categories = [cat for cat, score in category_scores.items() if score > 0]
    
    # If no matches, return Multidisciplinary
    if not matched_categories:
        return [DEFAULT_CATEGORY]
    
    return matched_categories


def process_scimago_file(input_file='scimagojr.csv', output_file='journals_by_category.json', top_n=50):
    """
    Process the SCImago CSV file and categorize journals.
    
    Args:
        input_file: Path to downloaded SCImago CSV
        output_file: Path to output JSON file
    """
    print("\n" + "=" * 80)
    print("PROCESSING SCIMAGO JOURNAL DATA")
    print("=" * 80)
    
    if not Path(input_file).exists():
        print(f"\n❌ Error: {input_file} not found!")
        print("\nPlease download the SCImago data first:")
        print("1. Visit: https://www.scimagojr.com/journalrank.php")
        print("2. Click 'Download data' button")
        print("3. Save as 'scimagojr.csv' in this directory")
        return None
    
    print(f"\n📂 Reading {input_file}...")
    
    # Read the CSV file
    journals_by_category = {category: [] for category in CATEGORIES}
    journals_by_category[DEFAULT_CATEGORY] = []
    
    processed_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            try:
                # Extract relevant fields (2024 format)
                journal_name = row.get('Title', '')
                issn = row.get('Issn', '')
                sjr_str = row.get('SJR', '0')
                # Handle European decimal format (comma instead of period)
                sjr_str = sjr_str.replace(',', '.')
                sjr = float(sjr_str or 0)
                h_index = int(row.get('H index', 0) or 0)
                
                # Get impact factor (Citations per Doc in 2 years)
                impact_factor_str = row.get('Citations / Doc. (2years)', '0')
                impact_factor_str = impact_factor_str.replace(',', '.')
                impact_factor = float(impact_factor_str or 0)
                
                total_docs = int(row.get('Total Docs. (2024)', 0) or 0)
                total_refs = int(row.get('Total Refs.', 0) or 0)
                country = row.get('Country', '')
                publisher = row.get('Publisher', '')
                categories = row.get('Categories', '')
                areas = row.get('Areas', '')
                
                # Only include journals with reasonable metrics
                if h_index > 10 and sjr > 0:
                    categories = categorize_journal_scimago(journal_name, categories, areas)
                    
                    journal_info = {
                        'name': journal_name,
                        'issn': issn,
                        'sjr': round(sjr, 3),
                        'h_index': h_index,
                        'impact_factor': round(impact_factor, 2),
                        'total_docs': total_docs,
                        'total_refs': total_refs,
                        'country': country,
                        'publisher': publisher,
                        'categories': categories,
                        'areas': areas
                    }
                    
                    # Add to all matched categories
                    for category in categories:
                        journals_by_category[category].append(journal_info)
                    
                    processed_count += 1
                    
                    if processed_count % 1000 == 0:
                        print(f"  Processed {processed_count} journals...")
                        
            except Exception as e:
                continue
    
    print(f"\n✓ Processed {processed_count} journals")
    
    # Sort journals within each category by combined score (SJR + h_index)
    for category in journals_by_category:
        journals_by_category[category].sort(
            key=lambda x: (x['h_index'] * 0.5 + x['sjr'] * 100),
            reverse=True
        )
        # Keep top 50 per category
        journals_by_category[category] = journals_by_category[category][:top_n]
    
    # Print summary
    print("\n" + "-" * 80)
    print("JOURNALS BY CATEGORY (Top 50 each):")
    print("-" * 80)
    for category, journals in journals_by_category.items():
        print(f"  {category}: {len(journals)} journals")
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(journals_by_category, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved to: {output_file}")
    print("=" * 80)
    
    return journals_by_category


def create_text_report(json_file='journals_by_category.json', output_file='top_journals_scimago.txt'):
    """
    Create a human-readable text report from the JSON data.
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("TOP JOURNALS BY RESEARCH CATEGORY (SCImago Rankings)\n")
        f.write("=" * 80 + "\n")
        f.write("Data source: SCImago Journal & Country Rank\n")
        f.write("Ranked by combined SJR score and h-index\n")
        f.write("=" * 80 + "\n\n")
        
        for category, journals in data.items():
            f.write(f"\n{category.upper()}\n")
            f.write("-" * 80 + "\n\n")
            
            for i, journal in enumerate(journals, 1):
                f.write(f"{i:2d}. {journal['name']}\n")
                f.write(f"    ISSN: {journal['issn']}\n")
                f.write(f"    Publisher: {journal['publisher']}\n")
                f.write(f"    Country: {journal['country']}\n")
                f.write(f"    Impact Factor (2yr): {journal['impact_factor']}\n")
                f.write(f"    SJR Score: {journal['sjr']}\n")
                f.write(f"    h-index: {journal['h_index']}\n")
                f.write(f"    Total Documents: {journal['total_docs']:,}\n")
                f.write("\n")
            
            f.write("\n")
    
    print(f"✓ Text report saved to: {output_file}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("SCIMAGO JOURNAL DATABASE BUILDER")
    print("=" * 80)
    print("\nThis tool will create a local database of top journals by category")
    print("using SCImago Journal Rankings data.\n")
    
    # Check for file with different possible names
    possible_files = ['scimagojr 2024.csv', 'scimagojr.csv', 'scimagojr 2023.csv']
    input_file = None
    
    for filename in possible_files:
        if Path(filename).exists():
            input_file = filename
            break
    
    if not input_file:
        download_scimago_data()
    else:
        print(f"✓ Found {input_file}")
        result = process_scimago_file(input_file, 'journals_by_category.json', top_n=100)
        
        if result:
            create_text_report('journals_by_category.json', 'top_journals_scimago.txt')
            print("\n✓ Done! You can now use the journals_by_category.json file")
            print("  or view top_journals_scimago.txt for a readable report.")
