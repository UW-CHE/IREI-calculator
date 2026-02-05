import streamlit as st
import pandas as pd
from script import get_journal_metrics, get_paper_metrics


doi = st.text_input('Enter DOI', value='https://doi.org/10.1038/171737a0')
output = get_journal_metrics(doi)
paper = get_paper_metrics(doi)

item = 'title'
label = item.replace('_', ' ').title()
with st.container(border=True):
    st.markdown(f"### {paper[item]}")

    flex = st.container(horizontal=True, horizontal_alignment="left")
    flex.badge(f"Published: {paper['publication_year']}")
    flex.badge(f"Cited by: {paper['cited_by_count']}")
    flex.badge(f"Percentile: {paper['citation_normalized_percentile']}")
    flex.badge(f"# Authors: {paper['author_count']}")
    flex.badge(f"1st Author: {paper['first_author']}")
# for item in paper['topics']:
#     st.markdown(f"{item['domain']}  \n  -- {item['field']}  \n  ---- {item['subfield']}  \n  ------ {item['name']}")

item = 'journal_name'
label = item.replace('_', ' ').title()
st.metric(label, output[item], border=True)

item = 'category'
label = item.replace('_', ' ').title()
st.metric(label, output[item], border=True)

item = 'publisher'
label = item.replace('_', ' ').title()
st.metric(label, output[item], border=True)

cols = st.columns(3)
item = 'impact_factor'
label = item.replace('_', ' ').title()
cols[0].metric(label, output[item], border=True, height="stretch")

item = 'h_index'
label = item.replace('_', ' ').title()
cols[1].metric(label, output[item], border=True, height="stretch")

data = [output['counts_by_year'][i]['works_count'] for i in range(4, -1, -1)]
cols[2].metric("Pubs in 2025", 
    output['counts_by_year'][0]['works_count'], 
    chart_data=data, 
    chart_type='area',
    border=True,
    delta_color='green',
)

with st.expander("Show Top Journals in Category"):
    import json
    journals = json.load(open('journals_by_category.json'))
    data = []
    for j in journals[output['category']]:
        # st.write(j)
        data.append({
            'Journal': j['name'], 
            'Impact Factor': j['impact_factor'], 
            'H-Index': j['h_index'], 
            'Pubs per Year': j['works_count'],
        })
    df = pd.DataFrame(data)
    st.write(df)


# @st.cache_data
def load_dataframe(file):
    df = pd.read_csv(file, delimiter=';')
    for item in ['Type', 'Sourceid', 'Open Access', 'Open Access Diamond', 'Overton']:
        df.pop(item)
    return df
df = load_dataframe('scimagojr 2024.csv')


# @st.cache_data
def load_database(file):
    return json.load(open(file, 'r'))
db = load_database('scimago_db.json')

with st.expander("Play with Scimago database"):
    area = st.selectbox('Choose Area', sorted(list(db.keys())))
    category = st.selectbox('Choose Category', sorted(list(db[area])))
    quartile = st.selectbox('Choose Quartile', sorted(list(db[area][category])))
    data = df.iloc[db[area][category][quartile]]
    st.write(data)

with st.expander("Filter Scimago database by Area and Category"):
    areas = [
        'Engineering',
        'Chemical Engineering',
        'Materials Science',
        'Chemistry',
        'Energy',
        'Environmental Science',
        'Mathematics',
        'Biochemistry, Genetics and Molecular Biology',
        'Agricultural and Biological Sciences',
        'Pharmacology, Toxicology and Pharmaceutics',
        'Immunology and Microbiology',
        'Computer Science',
        'Earth and Planetary Sciences',
        'Physics and Astronomy',
        'Medicine',
        'Dentistry',
        'Neuroscience',
        'Multidisciplinary',
        'Economics, Econometrics and Finance',
        'Business, Management and Accounting',
        'Psychology',
        'Decision Sciences',
        'Health Professions',
        'Nursing',
        'Veterinary',
        'Social Sciences',
        'Arts and Humanities',
    ]

    state = {}
    cols = st.columns(3)
    selected_areas = []
    with cols[0]:
        for i in range(len(areas)):
            if st.checkbox(areas[i]):
                selected_areas.append(areas[i])

    selected_categories = []
    with cols[1]:
        available_categories = [list(db[area].keys()) for area in selected_areas]
        overlapping_categories = set(available_categories[0])
        if len(available_categories) > 1:
            for cat in available_categories[1:]:
                overlapping_categories.intersection_update(set(cat))
        for cat in overlapping_categories:
            try:
                if st.checkbox(cat):
                    selected_categories.append(cat)
            except:
                pass

    selected_quartiles = []
    with cols[2]:
        for q in ['Q1', 'Q2', 'Q3', 'Q4', 'None']:
            if st.checkbox(q):
                selected_quartiles.append(q)

    new_df = pd.DataFrame()
    for area in selected_areas:
        for category in selected_categories:
            for q in selected_quartiles:
                try:
                    data = df.iloc[db[area][category][q]]
                    new_df = pd.concat((new_df, data))
                except KeyError:
                    pass
    new_df = new_df.drop_duplicates()
    st.write(new_df)
