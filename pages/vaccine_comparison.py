
import datetime
import pandas as pd
import altair as alt
import streamlit as st
import datetime as dt
import json

def app():
    with open('data/ts_data.json', 'r') as f:
        ts_data = json.load(f)
        
    source_keys = ['vaers', 'ev']
    condition_keys = ['died', 'serious', 'cardiac', 'menstrual', 'embolism']    
    died_values_vaers = ['pf_vaers_died', 'mod_vaers_died', 'jj_vaers_died']
    serious_values_vaers = ['pf_vaers_serious', 'mod_vaers_serious', 'jj_vaers_serious']
    cardiac_values_vaers = ['pf_vaers_cardiac', 'mod_vaers_cardiac', 'jj_vaers_cardiac']
    menstrual_values_vaers = ['pf_vaers_menstrual', 'mod_vaers_menstrual', 'jj_vaers_menstrual']
    embolism_values_vaers = ['pf_vaers_embolism', 'mod_vaers_embolism', 'jj_vaers_embolism']
    condition_values_vaers = [died_values_vaers, serious_values_vaers, cardiac_values_vaers, menstrual_values_vaers, embolism_values_vaers]
    died_values_ev = ['pf_ev_died', 'mod_ev_died', 'jj_ev_died', 'az_ev_died']
    serious_values_ev = ['pf_ev_serious', 'mod_ev_serious', 'jj_ev_serious', 'az_ev_serious']
    cardiac_values_ev = ['pf_ev_cardiac', 'mod_ev_cardiac', 'jj_ev_cardiac', 'az_ev_cardiac']
    menstrual_values_ev = ['pf_ev_menstrual', 'mod_ev_menstrual', 'jj_ev_menstrual', 'az_ev_embolism']
    embolism_values_ev = ['pf_ev_embolism', 'mod_ev_embolism', 'jj_ev_embolism', 'az_ev_embolism']
    condition_values_ev = [died_values_ev, serious_values_ev, cardiac_values_ev, menstrual_values_ev, embolism_values_ev]
    condition_vaers = dict(zip(condition_keys, condition_values_vaers))
    condition_ev = dict(zip(condition_keys, condition_values_ev))
    source_condition = dict(zip(source_keys, [condition_vaers, condition_ev]))

    vax_labels = {'pf':'Pfizer', 'mo':'Moderna', 'jj':'Janssen', 'az':'AstraZeneca'}

    cond_dict = {'died': 'death', 'serious':'serious reactions', 'cardiac': 'myocarditis and pericarditis', 'menstrual':'menstrual disorders', 'embolism': 'embolism and thrombosis', 'Death':'died', 'Serious reactions': 'serious', 'Myocarditis and pericarditis': 'cardiac', 'Menstrual and uterine bleeding disorders': 'menstrual', 'Embolism and thrombosis':'embolism'}

    def get_comparison_plots(ts_data, source_type = 'vaers', condition = 'died', excl_jj_ev = False):
        if source_type == 'vaers':
            key = 'RECVDATE'
        else:
            key = 'Report Date'
        time_key = key + ':T'
        data = dict()
        labels = source_condition[source_type][condition]
        if excl_jj_ev and (source_type == 'ev'):
            labels = [label for label in labels if label[:2]!='jj']
        for label in labels:
            data[label] = pd.read_json(ts_data['percentages'][label])
            data[label]['Vtype'] = vax_labels[label[0:2]]
        data = pd.concat(data.values())
        chart = alt.Chart(data).mark_line().encode(
        x=alt.X(time_key, title = 'Date'),
        y=alt.Y("percent:Q", title = f'Reports of {cond_dict[condition]}', stack=None, axis=alt.Axis(format='%')),
        color=alt.Color("Vtype:N", title = 'Vaccine type')
        )
        return chart  
    
    def get_agg_chart(ts_data, source = 'vaers', option = 'sex', option_title = 'Sex'):
        data = pd.read_json(ts_data['agg'][source][option]).reset_index()
        chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('index:N', title = option_title),
        y=alt.Y('percent:Q', title = None, axis=alt.Axis(format='%')), tooltip = alt.Tooltip('percent', format = '%'), color=alt.Color("index:N", title = 'Report Type', legend = None)
        )
        return chart  

    st.markdown("The charts below show the percent of reactions for each type of vaccine for each of the following categories: embolism and thrombosis, myocarditis and pericarditis, menstrual and uterine beleeding disorders, serious reactions, and death. The percentages are computed by dividing the number of reports including the given reaction by the total number of reports for that vaccine or report type. Embolism and thrombosis, myocarditis, pericarditis, and menstrual cycle and uterine bleeding disroders are each MedDRA layer 1 terms. The number of reports for each type are computed by counting the number of reports with terms with layer 1 subclasses of each type. For myocarditis and pericarditis, reports that include layer 1 subterms that are either myocarditis or pericarditis are counted for a given vaccine or report type. The time series graphs are calculated by taking the percentages for each two week window.")

    
    st.markdown("Select a reaction type from the selection below. The plots on the left and right are of VAERS and EudraVigilance data, respectively.")
    condition = st.selectbox('Select condition for comparison', ['Myocarditis and pericarditis', 'Embolism and thrombosis', 'Menstrual and uterine bleeding disorders', 'Serious reactions', 'Death'])
    
    
    st.subheader(f"Percent of reports for each vaccine type including {condition.lower()} per two week period")
    c1, c2 = st.columns(2)
    st.subheader(f"Percent of reports for each report type including {condition.lower()}")
    d1, d2 = st.columns(2)
    with c1:
        st.subheader("VAERS")
        st.altair_chart(get_comparison_plots(ts_data, 'vaers', cond_dict[condition])
                        .properties(title = f"Percent {condition.lower()} (VAERS)") ,use_container_width = True)
    with d1:
        st.altair_chart(get_agg_chart(ts_data, 'cv_vaers', cond_dict[condition], 'Report type')
                        .properties(title = f"Percent {condition.lower()} (VAERS)"), use_container_width = True)
        
    with c2:  
        st.subheader("EudraVigilance")
        st.altair_chart(get_comparison_plots(ts_data, 'ev', cond_dict[condition])
                        .properties(title = f"Percent {condition.lower()} (EudraVigilance)"), use_container_width = True)
        
    with d2:
        st.altair_chart(get_agg_chart(ts_data, 'cv_ev', cond_dict[condition], 'Report type')
                        .properties(title = f"Percent {condition.lower()} (EudraVigilance)"), use_container_width = True)

    st.subheader('Discussion')
    
    st.markdown('For myocarditis/pericarditis, we see significantly larger frequency percentages among all of the Covid vaccine compared to the control groups. This is especially true for the mRNA type vaccines, Pfizer and Moderna. A notable exception appears to be the AstraZeneca vaccine when compared the control groups in the EudraVigilance data.')
    
    st.markdown('For embolism and thrombosis, we see much more significant increases among all Covid vaccine types when compared to the control groups. The increase is especially notable when compared to influenza vaccines, where the percentages are more than 10 times (in some cases more than 30 times) larger than the percentage for reporting among influenza vaccines.  The viral vector vaccines, Janssen and AstraZeneca, show a slightly larger increase when compared to other vaccines in the VAERS and EudraVigilance source data, respectively.')
    
    st.markdown('For menstrual cycle and uterine bleeding disorders, we again see large increases in percentage among all Covid vaccine types when compared to control data. The Pfizer vaccine shows the largest percent increase for both source data types.')
    
    st.markdown('For serious reactions, except possibly for Pfizer in the VAERS data, there does not seem to be a notable increase when compared to control data for either source. The EudraVigilance data shows decreases in serious reaction percentages among all Covid vaccine types. This is likely due to the change in the types of reports that these systems are receiving. Both VAERS and EudraVigilance have recent reports dominated almost entirely by Covid vaccines. Unlike VAERS, EudraVigilance receives reports for a wide variety of drugs, including medications for serious and terminal illness, that may have extreme side effects. Also, for EudraVigilance, as may be seen from the "Demographics/Source Data Comparison" page, the average age of patient reports has lowered after the start of widespread Covid vaccination. This may have the effect of lowering percentages of severe reactions due to patients being on average younger.')
    
    st.markdown('For death, the VAERS data shows increases among the Covid vaccines when compared to the control group. On the other hand, the percentages for Covid vaccines, among the EudraVigilance data, are comparable to percentages for influenza vaccines and show a decrease when compared to past data. Again, this may be partly attributed to the change in the character of reports for EudraVigilance after the introduction of Covid vaccines.')
    
    
    st.markdown('For myocarditis/pericarditis, embolism and thrombosis, and menstrual and uterine bleeding disorders, in the time series plots showing a two week average percentages, we see unusually low values for the beginning months of 2021 when compared to later months. This may be due to several factors. First, an increase in awareness of these types of side effects may have led to increased report frequency and clinical suspicion. Second, in the US and most European countries, Covid vaccinations began among the elderly, especialy in care facilities. In such settings and among the elderly, there may be less clinical suspicion of such side effects or lower prevalence of reporting. Also, decreased functionality of the medical system during those months may have led to fewer diagnoses of such symptoms.') 
    