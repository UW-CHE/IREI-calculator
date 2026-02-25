import json
import streamlit as st
import pandas as pd
from script import get_journal_metrics, get_paper_metrics

def reset_state():
    st.session_state.clear()


def calc_authorship():
    author = state['author']
    pos = [item['position'] for item in paper['authors'] if item['name'] == author]
    return pos[0]

def category_journals_to_df(category_journals):
    data = []
    for rank, j in enumerate(category_journals, 1):
        data.append({
            'Rank': rank,
            'Journal': j['name'],
            'Impact Factor': j['impact_factor'],
            'H-Index': j['h_index'],
            'Pubs / Year': j['works_count'],
            'Publisher': j.get('publisher', ''),
        })
    df = pd.DataFrame(data)
    return df


# Style
css = """
div[class*="st-key-blue_"] {
    background: rgba(100, 100, 200, 0.1);
}
"""
st.html(f"<style>{css}</style>")
state = st.session_state

st.set_page_config(layout="wide")
doi = st.text_input('Enter DOI', value='https://doi.org/10.1038/171737a0', on_change=reset_state)
journal = get_journal_metrics(doi)
paper = get_paper_metrics(doi)

cols = st.columns(2)
with cols[0].container(border=True, key="blue_left"):
    st.markdown(f"**Title: {paper['title']}**")
    flex = st.container(horizontal=True, horizontal_alignment="left")
    flex.badge(f"Published: {paper['publication_year']}")
    flex.badge(f"Cited by: {paper['cited_by_count']}")
    flex.badge(f"Percentile: {paper['citation_normalized_percentile']}")
    flex.badge(f"# Authors: {paper['author_count']}")
    st.radio(
        label='Select Author', 
        options=[item['name'] for item in paper['authors']],
        key='author'
    )
    with st.expander(label='Show all paper metrics'):
        st.write(paper) 

@st.cache_data
def load_journal_db():
    return json.load(open('curated_journals_by_category.json'))

journal_db = load_journal_db()
category = journal['category']
category_journals = journal_db.get(category, [])
df = category_journals_to_df(category_journals)

with cols[1].container(border=True, key="blue_right"):
    st.markdown(f"**Journal: {journal['journal_name']}**")
    flex = st.container(horizontal=True, horizontal_alignment="left")
    flex.badge(f"Impact Factor: {journal['impact_factor']}")
    flex.badge(f"H-Index: {journal['h_index']}")
    flex.badge(f"Quartile: {journal['scimago_quartile']}")
    flex.badge(f"Pubs Last Year: {journal['counts_by_year'][1]['works_count']}")
    flex.badge(f"Publisher: {journal['publisher']}")
    flex.badge(f"Category: {journal['category']}")

    if not category_journals:
        st.warning(f"No journal data found for category: {category}")
    else:
        # Summary badges
        flex2 = st.container(horizontal=True)
        flex2.badge(f"Average H-Index in Category: {df['H-Index'].mean()}")
        flex2.badge(f"Average Impact Factor in Category: {df['Impact Factor'].mean()}")
                
        authorship = calc_authorship()
        if authorship == 'first':
            A = 1.0
        elif authorship == 'middle':
            A = 0.2
        elif authorship == 'last':
            A = 0.5
        IREI = \
            (journal['impact_factor']/df['Impact Factor'].mean() +
            journal['h_index']/df['H-Index'].mean())*A
        st.metric(label="IREI", value=f"{round(IREI, 3)}", border=True)

    with st.expander(label="Show all journal metrics", expanded=False):
        st.write(journal)

with st.expander("Journal Ranking in Category", expanded=True):
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )
