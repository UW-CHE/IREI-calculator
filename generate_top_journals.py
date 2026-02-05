#!/usr/bin/env python3
"""
Script to generate a list of top 25 journals in each research category.
Rankings based on h-index and impact factor.
"""

from script import save_top_journals_to_file

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("GENERATING TOP 25 JOURNALS BY RESEARCH CATEGORY")
    print("=" * 80)
    print("\nThis will query OpenAlex for journals in each category.")
    print("The process may take 1-2 minutes...\n")
    
    filename = save_top_journals_to_file('top_journals_by_category.txt')
    
    print(f"\n✓ Complete! Check the file: {filename}")
