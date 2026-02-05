#!/usr/bin/env python3
"""
Calculate average impact factor and h-index for top 25 journals in each category.
"""

import json
from pathlib import Path


def calculate_category_averages(json_file='journals_by_category.json', top_n=25):
    """
    Calculate average metrics for top N journals in each category.
    
    Args:
        json_file: Path to the journals database JSON
        top_n: Number of top journals to include in averages
    """
    if not Path(json_file).exists():
        print(f"Error: {json_file} not found!")
        print("Please run download_scimago.py first to generate the database.")
        return
    
    # Load the database
    with open(json_file, 'r', encoding='utf-8') as f:
        journals_by_category = json.load(f)
    
    print("\n" + "=" * 80)
    print("AVERAGE METRICS FOR TOP 25 JOURNALS BY CATEGORY")
    print("=" * 80)
    print("\nBased on SCImago Journal Rankings 2024")
    print("-" * 80)
    
    results = {}
    
    for category, journals in journals_by_category.items():
        # Take top N journals
        top_journals = journals[:top_n]
        
        if not top_journals:
            continue
        
        # Calculate averages
        avg_h_index = sum(j['h_index'] for j in top_journals) / len(top_journals)
        avg_sjr = sum(j['sjr'] for j in top_journals) / len(top_journals)
        avg_impact_factor = sum(j['impact_factor'] for j in top_journals) / len(top_journals)
        
        results[category] = {
            'avg_h_index': round(avg_h_index, 1),
            'avg_sjr': round(avg_sjr, 3),
            'avg_impact_factor': round(avg_impact_factor, 2),
            'num_journals': len(top_journals)
        }
        
        print(f"\n{category}")
        print(f"  Number of journals analyzed: {len(top_journals)}")
        print(f"  Average h-index: {avg_h_index:.1f}")
        print(f"  Average Impact Factor: {avg_impact_factor:.2f}")
        print(f"  Average SJR Score: {avg_sjr:.3f}")
    
    print("\n" + "=" * 80)
    print("SUMMARY COMPARISON")
    print("=" * 80)
    
    # Sort by h-index
    sorted_by_h = sorted(results.items(), key=lambda x: x[1]['avg_h_index'], reverse=True)
    
    print("\nRanked by Average h-index:")
    print("-" * 80)
    for i, (cat, metrics) in enumerate(sorted_by_h, 1):
        print(f"{i}. {cat}")
        print(f"   h-index: {metrics['avg_h_index']:.1f}, IF: {metrics['avg_impact_factor']:.2f}, SJR: {metrics['avg_sjr']:.3f}")
    
    # Sort by Impact Factor
    sorted_by_if = sorted(results.items(), key=lambda x: x[1]['avg_impact_factor'], reverse=True)
    
    print("\nRanked by Average Impact Factor:")
    print("-" * 80)
    for i, (cat, metrics) in enumerate(sorted_by_if, 1):
        print(f"{i}. {cat}")
        print(f"   IF: {metrics['avg_impact_factor']:.2f}, h-index: {metrics['avg_h_index']:.1f}, SJR: {metrics['avg_sjr']:.3f}")
    
    # Sort by SJR
    sorted_by_sjr = sorted(results.items(), key=lambda x: x[1]['avg_sjr'], reverse=True)
    
    print("\nRanked by Average SJR Score:")
    print("-" * 80)
    for i, (cat, metrics) in enumerate(sorted_by_sjr, 1):
        print(f"{i}. {cat}")
        print(f"   SJR: {metrics['avg_sjr']:.3f}, IF: {metrics['avg_impact_factor']:.2f}, h-index: {metrics['avg_h_index']:.1f}")
    
    print("\n" + "=" * 80)
    
    # Save results
    output_file = 'category_averages.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    calculate_category_averages(top_n=25)
