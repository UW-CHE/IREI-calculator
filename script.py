import requests
from category_keywords import CATEGORY_KEYWORDS, DEFAULT_CATEGORY
import json
import pandas as pd
import re


def _build_scimago_index(f='scimagojr 2024.csv') -> dict:
    """Build a dict mapping bare ISSNs (no hyphens) to Scimago row data."""
    try:
        df = pd.read_csv(f, delimiter=';')
    except FileNotFoundError:
        return {}
    index = {}
    for _, row in df.iterrows():
        raw_issns = str(row.get('Issn', ''))
        for issn in raw_issns.split(','):
            issn = issn.strip().replace('-', '')
            if issn:
                index[issn] = row
    return index

_SCIMAGO_INDEX = _build_scimago_index()


def _build_clarivate_index(f='curated_journals_by_category.json') -> dict:
    """Build a dict mapping normalised journal name → clarivate_if and openalex_id."""
    try:
        with open(f, encoding='utf-8') as fh:
            db = json.load(fh)
    except FileNotFoundError:
        return {}
    index = {}
    for journals in db.values():
        for j in journals:
            key = j['name'].lower().strip()
            index[key] = {
                'clarivate_if': j.get('clarivate_if'),
                'openalex_id': j.get('openalex_id', ''),
            }
    return index

_CLARIVATE_INDEX = _build_clarivate_index()


def _clarivate_lookup(openalex_id: str, journal_name: str) -> float | None:
    """Return clarivate_if for the journal, or None if not in the curated DB."""
    if openalex_id:
        for entry in _CLARIVATE_INDEX.values():
            if entry['openalex_id'] == openalex_id:
                return entry['clarivate_if']
    return _CLARIVATE_INDEX.get(journal_name.lower().strip(), {}).get('clarivate_if')


def _scimago_lookup(issn: str) -> dict | None:
    """Return Scimago row for the given ISSN (with or without hyphens), or None."""
    bare = issn.replace('-', '')
    row = _SCIMAGO_INDEX.get(bare)
    if row is None:
        return None
    return {
        'scimago_quartile': row.get('SJR Best Quartile'),
        'scimago_sjr': row.get('SJR'),
        'scimago_h_index': row.get('H index'),
    }


def scimago_csv_to_db(f='scimagojr 2024.csv'):
    df = pd.read_csv(f, delimiter=';')
    db = {}
    for index, (categories, areas) in enumerate(zip(df['Categories'], df['Areas'])):
        for area in areas.split(';'):
            area = area.strip()
            if area not in db.keys():
                db[area] = dict()
            else:
                for category in categories.split(';'):
                    category = category.strip()
                    match = re.match(r'^(.+?)\s*\(([^)]+)\)$', category)
                    if match:
                        category, quartile = match.group(1).strip(), match.group(2).strip()
                    else:
                        quartile = 'None'
                    if category not in db[area].keys():
                        db[area][category] = {}
                    if quartile not in db[area][category].keys():
                        db[area][category][quartile] = []
                    db[area][category][quartile].append(index)
    json.dump(db, open('scimago_db.json', 'w'))


def categorize_journal(
    journal_name: str,
    journal_topics: list,
    article_topics: list = None,
    article_keywords: list = None,
) -> str:
    """
    Categorize a journal into research areas using a three-stage cascade.

    Stage 1 – Journal name (decisive).
        Each matching keyword adds 20 points.  If any category scores ≥ 20
        the winner is returned immediately; article content is never consulted.
        This ensures multidisciplinary journals like Scientific Reports and
        specialized ones like Nature Biotechnology are not overridden by the
        topic of the specific article being looked up.

    Stage 2 – Journal-level topics (secondary identity signal).
        Used only when the journal name gave no clear match.  If the leading
        category reaches ≥ 3 topic hits the winner is returned, still without
        consulting article content.

    Stage 3 – Article topics / keywords (last resort).
        Only reached when the journal's own identity signals are ambiguous
        (e.g. very new journals with no distinctive name or few topics).
    """
    journal_name_lower = journal_name.lower()

    # ── Stage 1: journal name ────────────────────────────────────────────────
    name_scores: dict[str, float] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        name_scores[category] = sum(
            20 for kw in keywords if kw in journal_name_lower
        )

    max_name = max(name_scores.values())
    if max_name >= 20:
        return max(name_scores, key=name_scores.get)

    # ── Stage 2: journal-level topics ───────────────────────────────────────
    topic_scores: dict[str, float] = {cat: 0.0 for cat in CATEGORY_KEYWORDS}
    for category, keywords in CATEGORY_KEYWORDS.items():
        for topic in journal_topics[:10]:
            topic_name = topic.get('display_name', '').lower()
            for kw in keywords:
                if kw in topic_name:
                    topic_scores[category] += 1
                    break

    max_topic = max(topic_scores.values())
    if max_topic >= 3:
        combined = {cat: name_scores[cat] + topic_scores[cat] for cat in name_scores}
        return max(combined, key=combined.get)

    # ── Stage 3: article content (ambiguous journal identity) ────────────────
    article_scores: dict[str, float] = {
        cat: name_scores[cat] + topic_scores[cat] for cat in name_scores
    }
    for category, keywords in CATEGORY_KEYWORDS.items():
        if article_topics:
            for topic in article_topics[:5]:
                topic_name = topic.get('display_name', '').lower()
                for kw in keywords:
                    if kw in topic_name:
                        article_scores[category] += 0.5
                        break
        if article_keywords:
            for kw_entry in article_keywords[:15]:
                kw_name = kw_entry.get('display_name', '').lower()
                for kw in keywords:
                    if kw in kw_name:
                        article_scores[category] += 0.3
                        break

    max_article = max(article_scores.values())
    if max_article > 0:
        return max(article_scores, key=article_scores.get)
    return DEFAULT_CATEGORY


def get_journal_metrics(doi: str) -> dict:
    """
    Get comprehensive journal metrics for a given DOI.
    
    Args:
        doi: The DOI of the article
        
    Returns:
        Dictionary containing journal metrics including:
        - journal_name: Name of the journal
        - issn: ISSN of the journal
        - category: Research area category (7 categories)
        - impact_factor: Calculated 2-year impact factor
        - h_index: h-index (Eigenfactor alternative - measures cumulative impact)
        - i10_index: i10-index (papers with >=10 citations)
        - papers_count: Total number of papers published
        - cited_by_count: Total citations received
        - citations_per_paper: Average citations per paper (all-time)
        - mean_citedness_2y: Average citations per paper in last 2 years
        - publication_growth_rate: Growth rate comparing recent 5 years vs previous 5 years
        - publisher: Publisher/host organization
        - country: Country code
        - oa_works_count: Number of open access papers
        - apc_usd: Article processing charge in USD
        - counts_by_year: Yearly publication and citation data
    """
    # Step 1: Get article-specific data from OpenAlex
    article_topics = []
    article_keywords = []
    try:
        article_url = f"https://api.openalex.org/works/doi:{doi}"
        response = requests.get(article_url)
        response.raise_for_status()
        article_data = response.json()
        article_topics = article_data.get('topics', [])
        article_keywords = article_data.get('keywords', [])
    except Exception:
        # If article data fails, continue without it
        pass
    
    # Step 2: Get journal information from DOI via CrossRef
    crossref_url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(crossref_url)
        response.raise_for_status()
        crossref_data = response.json()['message']
        
        # Extract ISSN (prefer electronic ISSN, fall back to print ISSN)
        issn_list = crossref_data.get('ISSN', [])
        if not issn_list:
            return {"error": "No ISSN found for this DOI"}
        
        issn = issn_list[0]
        journal_name = crossref_data.get('container-title', ['Unknown'])[0]
        
    except Exception as e:
        return {"error": f"Failed to fetch CrossRef data: {str(e)}"}
    
    # Step 3: Get journal metrics from OpenAlex using ISSN
    openalex_url = f"https://api.openalex.org/sources/issn:{issn}"
    try:
        response = requests.get(openalex_url)
        response.raise_for_status()
        openalex_data = response.json()
        
        # Extract metrics
        summary_stats = openalex_data.get('summary_stats', {})
        counts_by_year = openalex_data.get('counts_by_year', [])
        journal_topics = openalex_data.get('topics', [])
        
        # Categorize the journal using article and journal data
        category = categorize_journal(journal_name, journal_topics, article_topics, article_keywords)
        
        # Calculate publication growth rate
        counts_10y = counts_by_year[:10] if len(counts_by_year) >= 10 else counts_by_year
        if len(counts_10y) >= 5:
            recent_5yr = sum(c['works_count'] for c in counts_10y[:5]) / 5
            older_5yr = sum(c['works_count'] for c in counts_10y[5:10]) / 5 if len(counts_10y) >= 10 else recent_5yr
            growth_rate = round(((recent_5yr - older_5yr) / older_5yr * 100), 1) if older_5yr > 0 else 0
        else:
            growth_rate = 0
        
        # Calculate overall citation rate
        total_works = openalex_data.get('works_count', 0)
        total_citations = openalex_data.get('cited_by_count', 0)
        citations_per_paper = round(total_citations / total_works, 1) if total_works > 0 else 0
        
        # Calculate Impact Factor (most recent available)
        # IF = citations in year X to papers from years X-1 and X-2 / papers published in X-1 and X-2
        impact_factor = 0
        if len(counts_by_year) >= 3:
            # Get most recent complete year (index 1, as index 0 is current partial year)
            year_x = counts_by_year[1]
            year_x_minus_1 = counts_by_year[2]
            year_x_minus_2 = counts_by_year[3] if len(counts_by_year) > 3 else {'works_count': 0, 'cited_by_count': 0}
            
            # Papers published in the 2-year window
            papers_2y = year_x_minus_1['works_count'] + year_x_minus_2['works_count']
            
            # Citations received in year X to those papers
            # Note: OpenAlex doesn't provide this exact breakdown, so we use mean_citedness as proxy
            # For a more accurate IF, we'd need journal-specific citation data by publication year
            citations_to_2y_papers = summary_stats.get('2yr_mean_citedness', 0) * papers_2y
            
            impact_factor = round(citations_to_2y_papers / papers_2y, 2) if papers_2y > 0 else 0
        
        oa_id = openalex_data.get('id', '')
        metrics = {
            'journal_name': journal_name,
            'issn': issn,
            'category': category,
            'openalex_id': oa_id,
            'clarivate_if': _clarivate_lookup(oa_id, journal_name),
            'publisher': openalex_data.get('host_organization_name', 'Unknown'),
            'country': openalex_data.get('country_code', 'Unknown'),
            
            # Citation metrics (Eigenfactor alternatives)
            'h_index': summary_stats.get('h_index', 0),
            'i10_index': summary_stats.get('i10_index', 0),
            'impact_factor': impact_factor,
            'mean_citedness_2y': round(summary_stats.get('2yr_mean_citedness', 0), 2),
            'citations_per_paper': citations_per_paper,
            
            # Volume metrics
            'papers_count': total_works,
            'cited_by_count': total_citations,
            'oa_works_count': openalex_data.get('oa_works_count', 0),
            
            # Growth metrics
            'publication_growth_rate': growth_rate,
            
            # Open access info
            'apc_usd': openalex_data.get('apc_usd', 0),
            'is_oa': openalex_data.get('is_oa', False),
            
            # Year-by-year data
            'counts_by_year': counts_by_year[:5],  # Last 5 years

            # Scimago rankings
            **(_scimago_lookup(issn) or {'scimago_quartile': None, 'scimago_sjr': None, 'scimago_h_index': None})
        }

        return metrics
        
    except Exception as e:
        return {"error": f"Failed to fetch OpenAlex data: {str(e)}", "journal_name": journal_name, "issn": issn}


def get_paper_metrics(doi: str) -> dict:
    """
    Get comprehensive bibliographic and citation information for a paper given its DOI.
    
    Args:
        doi: The DOI of the paper
        
    Returns:
        Dictionary containing paper information including:
        - title: Paper title
        - authors: List of authors with affiliations
        - publication_date: Publication date
        - publication_year: Publication year
        - journal: Journal name
        - doi: Paper DOI
        - openalex_id: OpenAlex identifier
        - abstract: Abstract text (if available)
        - keywords: List of keywords
        - topics: List of research topics with scores
        - cited_by_count: Number of citations received
        - references_count: Number of references cited
        - is_open_access: Open access status
        - open_access_url: URL to OA version (if available)
        - pdf_url: Direct PDF URL (if available)
        - publisher: Publisher name
        - type: Publication type (e.g., journal-article, book-chapter)
        - language: Language code
        - counts_by_year: Citations received by year
        - related_works: List of related papers
        - concepts: List of concepts/fields
        - sustainable_development_goals: Related SDGs
        - mesh_terms: Medical Subject Headings (if applicable)
    """
    # Get article data from OpenAlex
    openalex_url = f"https://api.openalex.org/works/doi:{doi}"
    try:
        response = requests.get(openalex_url)
        response.raise_for_status()
        data = response.json()
        
        # Extract authors with affiliations
        authors = []
        for authorship in data.get('authorships', []):
            author_info = {
                'name': authorship.get('author', {}).get('display_name', 'Unknown'),
                'orcid': authorship.get('author', {}).get('orcid'),
                'position': authorship.get('author_position'),
                'affiliations': [
                    {
                        'institution': inst.get('display_name'),
                        'country': inst.get('country_code'),
                        'type': inst.get('type')
                    }
                    for inst in authorship.get('institutions', [])
                ]
            }
            authors.append(author_info)
        
        # Extract topics with scores
        topics = []
        for topic in data.get('topics', []):
            subfield = topic.get('subfield')
            field = topic.get('field')
            domain = topic.get('domain')
            topics.append({
                'name': topic.get('display_name'),
                'score': round(topic.get('score', 0), 3),
                'subfield': subfield.get('display_name') if isinstance(subfield, dict) else subfield,
                'field': field.get('display_name') if isinstance(field, dict) else field,
                'domain': domain.get('display_name') if isinstance(domain, dict) else domain
            })
        
        # Extract keywords
        keywords = [kw.get('display_name') for kw in data.get('keywords', [])]
        
        # Extract concepts (broader classification)
        concepts = [
            {
                'name': concept.get('display_name'),
                'score': round(concept.get('score', 0), 3),
                'level': concept.get('level', 0)
            }
            for concept in data.get('concepts', [])
        ]
        
        # Extract Open Access information
        oa_info = data.get('open_access') or {}
        best_oa_location = data.get('best_oa_location') or {}
        
        # Extract biblio info
        biblio = data.get('biblio') or {}
        
        # Extract location (journal/venue info)
        location = data.get('primary_location') or {}
        source = location.get('source') if isinstance(location, dict) else {}
        if not isinstance(source, dict):
            source = {}
        
        # Extract SDGs
        sdgs = [
            {
                'id': sdg.get('id'),
                'display_name': sdg.get('display_name'),
                'score': round(sdg.get('score', 0), 3)
            }
            for sdg in data.get('sustainable_development_goals', [])
        ]
        
        # Extract MeSH terms
        mesh_terms = [
            {
                'descriptor_ui': mesh.get('descriptor_ui'),
                'descriptor_name': mesh.get('descriptor_name'),
                'is_major_topic': mesh.get('is_major_topic', False)
            }
            for mesh in data.get('mesh', [])
        ]
        
        # Extract related works (most similar papers) - already a list of strings
        related_works = data.get('related_works', [])
        
        paper_info = {
            # Basic bibliographic info
            'title': data.get('title', 'Unknown'),
            'doi': data.get('doi'),
            'openalex_id': data.get('id'),
            'publication_date': data.get('publication_date'),
            'publication_year': data.get('publication_year'),
            'type': data.get('type'),
            'language': data.get('language'),
            
            # Journal/venue info
            'journal': source.get('display_name', 'Unknown') if source else 'Unknown',
            'journal_issn': source.get('issn_l') if source else None,
            'journal_issn_list': source.get('issn') if source else None,
            'publisher': source.get('host_organization_name') if source else None,
            'volume': biblio.get('volume'),
            'issue': biblio.get('issue'),
            'first_page': biblio.get('first_page'),
            'last_page': biblio.get('last_page'),
            
            # Authors
            'authors': authors,
            'first_author': authors[0]['name'] if authors else 'Unknown',
            'last_author': authors[-1]['name'] if len(authors) > 1 else None,
            'author_count': len(authors),
            
            # Abstract and keywords
            'abstract': data.get('abstract'),
            'keywords': keywords,
            
            # Research classification
            'topics': topics,
            'concepts': concepts,
            'mesh_terms': mesh_terms,
            'sustainable_development_goals': sdgs,
            
            # Citation metrics
            'cited_by_count': data.get('cited_by_count', 0),
            'references_count': data.get('referenced_works_count', 0),
            'counts_by_year': data.get('counts_by_year', []),
            'citation_normalized_percentile': (data.get('cited_by_percentile_year') or {}).get('min'),
            
            # Open Access
            'is_open_access': oa_info.get('is_oa', False),
            'oa_status': oa_info.get('oa_status'),
            'open_access_url': oa_info.get('oa_url'),
            'pdf_url': best_oa_location.get('pdf_url'),
            'landing_page_url': best_oa_location.get('landing_page_url'),
            
            # Related works
            'related_works': related_works,
            
            # URLs
            'openalex_url': f"https://openalex.org/{data.get('id', '').split('/')[-1]}" if data.get('id') else None,
            'doi_url': f"https://doi.org/{doi}"
        }
        
        return paper_info
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"Paper not found for DOI: {doi}"}
        else:
            return {"error": f"HTTP error occurred: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to fetch paper data: {str(e)}"}


def get_top_journals_by_category(top_n: int = 25) -> dict:
    """
    Get top N journals for each research category based on h-index and impact factor.
    
    Args:
        top_n: Number of top journals to retrieve per category (default: 25)
        
    Returns:
        Dictionary with category names as keys and lists of journal info as values
    """
    import time
    
    results = {}
    
    for category, query_terms in CATEGORY_KEYWORDS.items():
        print(f"\nSearching for top journals in: {category}")
        print("-" * 70)
        
        all_journals = []
        
        # Search for journals using each query term
        for query in query_terms[:2]:  # Use first 2 query terms to limit API calls
            try:
                # Search OpenAlex for sources (journals) related to the topic
                search_url = f"https://api.openalex.org/sources"
                params = {
                    'filter': f'type:journal',
                    'search': query,
                    'per_page': 50,
                    'sort': 'cited_by_count:desc'
                }
                
                response = requests.get(search_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                for source in data.get('results', []):
                    summary_stats = source.get('summary_stats', {})
                    h_index = summary_stats.get('h_index', 0)
                    mean_citedness = summary_stats.get('2yr_mean_citedness', 0)
                    
                    # Only include journals with reasonable metrics
                    if h_index > 0 and mean_citedness > 0:
                        journal_info = {
                            'name': source.get('display_name', 'Unknown'),
                            'issn': source.get('issn_l', 'N/A'),
                            'h_index': h_index,
                            'impact_factor': round(mean_citedness, 2),
                            'publisher': source.get('host_organization_name', 'Unknown'),
                            'works_count': source.get('works_count', 0),
                            'cited_by_count': source.get('cited_by_count', 0),
                            'openalex_id': source.get('id', '')
                        }
                        
                        # Check if journal already in list (avoid duplicates)
                        if not any(j['name'] == journal_info['name'] for j in all_journals):
                            all_journals.append(journal_info)
                
                # Be respectful to the API
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  Error searching for '{query}': {str(e)}")
                continue
        
        # Sort by combined score (h_index + impact_factor weighted)
        all_journals.sort(key=lambda x: (x['impact_factor'] * 10), reverse=True)
        
        # Take top N
        results[category] = all_journals[:top_n]
        print(f"  Found {len(results[category])} journals")
    
    return results


def save_top_journals_to_file(filename: str = 'top_journals_by_category.txt', top_n=25):
    """
    Get top journals and save them to a text file.
    
    Args:
        filename: Output filename
    """
    print("Fetching top journals by category...")
    print("=" * 70)
    
    top_journals = get_top_journals_by_category(top_n=top_n)
    
    with open(filename, 'w') as f:
        f.write("TOP 25 JOURNALS BY RESEARCH CATEGORY\n")
        f.write("=" * 80 + "\n")
        f.write("Ranked by combined h-index and impact factor\n")
        f.write("=" * 80 + "\n\n")
        
        for category, journals in top_journals.items():
            f.write(f"\n{category.upper()}\n")
            f.write("-" * 80 + "\n\n")
            
            for i, journal in enumerate(journals, 1):
                f.write(f"{i:2d}. {journal['name']}\n")
                f.write(f"    ISSN: {journal['issn']}\n")
                f.write(f"    Publisher: {journal['publisher']}\n")
                f.write(f"    h-index: {journal['h_index']}\n")
                f.write(f"    Impact Factor: {journal['impact_factor']}\n")
                f.write(f"    Total Papers: {journal['works_count']:,}\n")
                f.write(f"    Total Citations: {journal['cited_by_count']:,}\n")
                f.write("\n")
            
            f.write("\n")
    
    print(f"\n✓ Results saved to: {filename}")
    return filename


# Example usage
if __name__ == "__main__":
    # Test with different journals
    test_dois = [
        "10.3390/polym14112143",  # Polymers journal - should be Soft Matter
        "10.1016/j.electacta.2025.147532",  # Electrochimica Acta
        "10.1038/nbt.3121",  # Nature Biotechnology
        "10.1021/acsnano.5b00184",  # ACS Nano
    ]
    
    print("TESTING JOURNAL CATEGORIZATION")
    print("=" * 70)
    for doi in test_dois:
        metrics = get_journal_metrics(doi)
        
        print(f"\nDOI: {doi}")
        print("-" * 70)
        
        if 'error' in metrics:
            print(f"Error: {metrics['error']}")
        else:
            print(f"Journal: {metrics['journal_name']}")
            print(f"Category: {metrics['category']}")
            print(f"Impact Factor: {metrics['impact_factor']}")
    
    print("\n\n")
    
    import json
    journals_by_category = get_top_journals_by_category(top_n=50)
    with open('journals_by_category.json', 'w', encoding='utf-8') as f:
        json.dump(journals_by_category, f, indent=2, ensure_ascii=False)
    # save_top_journals_to_file('top_journals_by_category.txt', top_n=25)