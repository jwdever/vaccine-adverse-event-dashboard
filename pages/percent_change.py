
import streamlit as st
import pandas as pd
import altair as alt
import pickle
import datetime
import json

from pages import symptom_graph


def top_changes_c(dist_c, control_key, compare_key, num_changes = None, cutoff_freq = 0, percentages = False, normalize_by_reports = True):
    """Finds percent increase in relative frequencies from control distribution to compare distribution and returns the result for the top num_changes results. Use normalize_by_reports = False to normalize by total number of symptoms, rather than number of reports."""
    all_changes=[]
    factor = 1
    idx_0, idx_1 = dist_c['keys'][control_key], dist_c['keys'][compare_key]
    if percentages:
        factor = 100
    for layer in [x for x in dist_c.keys() if x not in ['norm', 'keys']]:
        per_changes = []
        if normalize_by_reports:
            n1, n2 = dist_c['norm'][idx_0], dist_c['norm'][idx_1]
        else:
            n1 = sum([x[idx_0] for x in dist_c[layer].values()]) 
            n2 = sum([x[idx_1] for x in dist_c[layer].values()]) 
        cutoff = min([k for k in range(100) if k/n1 > cutoff_freq])
        for x in dist_c[layer].keys():
            a = dist_c[layer][x][idx_0] 
            b = dist_c[layer][x][idx_1] 
            if a >= cutoff:
                change=factor*((b/n2)-(a/n1))/((a/n1))
                per_changes.append((x,change))
        if num_changes:
            all_changes.append(sorted(per_changes,key=lambda x: x[1], reverse=True)[:num_changes])
        else:
            all_changes.append(sorted(per_changes,key=lambda x: x[1], reverse=True))
    return all_changes  

def get_data_c(source, control_key, compare_key, layer_key, num_changes = None, cutoff_freq = 0, percentages = False, normalize_by_reports = True):
    return pd.DataFrame(top_changes_c(source, control_key, compare_key, num_changes, cutoff_freq, percentages, normalize_by_reports)[int(layer_key)], columns = ['Symptom', 'Percent'])


def app():
    st.header("Percent Changes in Symptom Occurence Compared to Control Group")
    st.markdown("""The graph below plots the largest percent changes in relative frequency (from a control data set to a comparison data set) for symptoms in a given symptom layer. In the dropdown menu below, choose a control data set, a comparison data set, and a symptom layer (corresponding to MedDRA term groupings). Clicking a bar on the graph removes it from the graph. See the "Methodology" page for information about data sources.""")
    
    with st.expander("Terminology"):
        st.markdown(r"""By relative frequency of occurence of a symptom, we mean the ratio of the number of reports that mention the symptom to the total number of reports. For example, say a hypothetical "symptom A" occurs at least once in 5 different reports out of a total of 20,000 reports in the control data set. Then it occurs with relative frequency of 0.00025 or 0.025% in that data set. If also, for example, the same symptom A occurs at least once in 100 reports out of 1,000,000 in a comparison data set, then it occurs with relative frequency of 
0.001 or 0.1% in the comparison data set. The percent change in relative frequency of occurence of symptom A would then be $$\left(100\times \left( \frac{0.1-0.025}{0.025}\right)\right)\%= 300\%$$.""")
        st.markdown(r"""Symptom layers correspond to MedDRA symptom groups. Layer 0 is the System Organ Class, the most general MedDRA terms, while later layers are increasingly specific. To ensure comparison with large enough samples, it is recommended to keep the symptom layer at 2 or below or to increase the control frequency threshold.""")
        st.markdown(r"""The control frequency threshold determines what relative frequency for presence in the control data a symptom needs to exceed in order to be compared. A larger control frequency threshold eliminates terms from comparison that are extremely rare in the control data. A control frequency threshold of 0 means that any term present in the control data is compared.""")
        
    with open('data/dist_c.json', 'r') as f:
         dist = json.load(f)
    
 
    
    control_labels = {'Influenza Vaccines (VAERS)': 'infl_vaers', 'Data prior to 12-1-20 (VAERS)': 'c_vaers',
                      'Data prior to 3-1-20 (VAERS)': 'c_vaers1',
                 'Influenza Vaccines (EudraVigilance)': 'infl_ev', 'Data prior to 12-1-20 (EudraVigilance)': 'c_ev',
                     'Data prior to 3-1-20 (EudraVigilance)': 'c_ev1'}

    
    compare_labels = {'All COVID Vaccines (VAERS)': 'cv_vaers', 'All COVID Vaccines (EudraVigilance)': 'cv_ev', 
                  'Pfizer COVID Vaccine (VAERS)': 'pf_vaers', 'Pfizer COVID Vaccine (EudraVigilance)': 'pf_ev',
                 'Moderna COVID Vaccine (VAERS)': 'mod_vaers', 'Moderna COVID Vaccine (EudraVigilance)': 'mod_ev',
                 'Janssen COVID Vaccine (VAERS)': 'jj_vaers', 'Janssen COVID Vaccine (EudraVigilance)': 'jj_ev',
                 'AstraZeneca COVID Vaccine (EudraVigilance)': 'az_ev'}

    control_labels_d = {'Influenza Vaccines (VAERS)': 'infl_vaers_d', 'Data prior to December 1, 2020 (VAERS)': 'c_vaers_d', 
                        'Data prior to March 1, 2020 (VAERS)': 'c_vaers1_d',
                 'Influenza Vaccines (EudraVigilance)': 'infl_ev', 'Data prior to December 1, 2020 (EudraVigilance)': 'c_ev',
                       'Data prior to March 1, 2020 (EudraVigilance)': 'c_ev1'}

    
    compare_labels_d = {'All COVID Vaccines (VAERS)': 'cv_vaers_d', 'All COVID Vaccines (EudraVigilance)': 'cv_ev', 
                  'Pfizer COVID Vaccine (VAERS)': 'pf_vaers_d', 'Pfizer COVID Vaccine (EudraVigilance)': 'pf_ev',
                 'Moderna COVID Vaccine (VAERS)': 'mod_vaers_d', 'Moderna COVID Vaccine (EudraVigilance)': 'mod_ev',
                 'Janssen COVID Vaccine (VAERS)': 'jj_vaers_d', 'Janssen COVID Vaccine (EudraVigilance)': 'jj_ev',
                 'AstraZeneca COVID Vaccine (EudraVigilance)': 'az_ev'}
   
    group_labels = dict()
    
    cutoff_freqs = dict(zip(['0', '1 report per 10,000', '2 reports per 10,000', '3 reports per 10,000', '4 reports per 10,000'], [0, 1e-5, 2e-5, 3e-5, 4e-5]))

    c1, c2, c3, c4 = st.columns([9,9,4,6])

    with c4:
        incl_foreign = st.checkbox("Include non-domestic VAERS reports.", value = True)
        if incl_foreign:
            group_labels['control'] = control_labels
            group_labels['compare'] = compare_labels
        else:
            group_labels['control'] = control_labels_d
            group_labels['compare'] = compare_labels_d
            
    with c1:
        control_label = st.selectbox("Select control data",
                             options=control_labels.keys())
        
        
    with c2:
        compare_label = st.selectbox("Select comparison data",
                             options=compare_labels.keys())
        st.caption("Percent increases are of the comparison data relative to the control data.")
    with c3:
        symptom_layer = st.radio("Select MedDRA symptom layer",
                 options=[0,1,2,3])
        st.caption("""Increasing layers increases term specificity.""")
    
    with c4:    
        control_freq = st.selectbox("Control frequency threshold.", options = list(cutoff_freqs.keys()), index = 2)
        st.caption("Only terms whose frequency in the control data strictly exceeds the cutoff frequency threshold are included.")
        
    pts = alt.selection_multi(fields=['Percent'], toggle = 'true')

    chart = (alt.Chart(get_data_c(dist, group_labels['control'][control_label], group_labels['compare'][compare_label], symptom_layer, cutoff_freq = cutoff_freqs[control_freq])).add_selection(pts)
         .transform_filter(~pts).transform_calculate(
    order=f"indexof({pts.name}.Percent || [], datum.Percent)",
    ).mark_bar().encode(
    y=alt.Y('Symptom:N', sort = '-x'),
    x=alt.X('Percent', title = 'Percent increase', axis=alt.Axis(format='%')), color = alt.Color('Percent', scale = {"type": "symlog", 'domain': (-15, 15)}, legend = None), tooltip=alt.Tooltip('Percent', format = '%'))
         .transform_window(
    rank="rank(order)"
    ).transform_filter(
    alt.datum.rank <= 15
    ).properties(title = "Percent increase in relative frequency of symptom occurence compared to control group", 
                 height = 500, width = 1000).configure_axisY(labelLimit=600, title = None))

    st.altair_chart(chart, use_container_width = True)

  