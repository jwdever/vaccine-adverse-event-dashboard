
import streamlit as st
import pandas as pd
import altair as alt
import pickle
import datetime
import json

def app():
    
    with open('data/ts_data.json', 'r') as f:
        ts_data = json.load(f)
    column_keys = {'vaers':{'time':'RECVDATE', 'age':'AGE_YRS'}, 'ev':{'time':'Report Date', 'age': 'Age_approx'}}

        
    def get_age_graph(ts_data, source = 'vaers'):
        if 'vaers' in source:
            source_type = 'vaers'
        else:
            source_type = 'ev'
        time_key = column_keys[source_type]['time']+':T'
        age_key = column_keys[source_type]['age']+':Q'
        data = pd.read_json(ts_data['age'][source])
        chart = alt.Chart(data).mark_line().encode(
        x=alt.X(time_key, title = 'Date', axis=alt.Axis(format='%b %Y')),
        y=alt.Y(age_key, title = 'Mean patient Age (years)', stack=None, scale = alt.Scale(zero = False))
        )
        return chart  
    def get_agg_chart(ts_data, source = 'vaers', option = 'sex', option_title = 'Sex', vertical = False, sort = None):
        data = pd.read_json(ts_data['agg'][source][option]).reset_index()
        chart = alt.Chart(data).mark_bar().encode(
        y=alt.Y('index:N', title = option_title, sort = sort),
        x=alt.X('percent:Q', title = 'Percent', stack=None, axis=alt.Axis(format='%')), tooltip = alt.Tooltip('percent', format = '%'), color=alt.Color("index:N", title = 'Report Type', legend = None)
        )
        return chart  
    
    def get_agg_chart1(ts_data, source = 'vaers', option = 'sex', option_title = 'Sex', vertical = False, sort = None):
        data = pd.read_json(ts_data['agg'][source][option]).reset_index()
        chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('index:N', title = option_title, sort = sort),
        y=alt.Y('percent:Q', title = 'Percent', stack=None, axis=alt.Axis(format='%')), tooltip = alt.Tooltip('percent', format = '%'), color=alt.Color("index:N", title = 'Report Type', legend = None)
        )
        return chart 
    selection_dict = {'VAERS': 'vaers', 'Covid vaccine reports (VAERS)':'cv_vaers', 'EudraVigilance': 'ev', 'Covid vaccine reports (EudraVigilance)':'cv_ev'}

    category_dict = {'All reports':['vaers','ev'], 'Covid vaccine reports':['cv_vaers', 'cv_ev'], 'Myocarditis/pericarditis (Covid vaccine reports)':['cv_vaers_cardiac', 'cv_ev_cardiac'], 'Serious reaction reports':['vaers_serious', 'ev_serious']}
    
    st.header('Patient Age and Sex by Source')
    form = st.form("demographics")
    form.markdown('Select a report category to plot the average patient age (per two week window) and the percentages for patient sex for VAERS and EudraVigilance**.')
    
    category = form.selectbox('Select report category', list(category_dict.keys()))
    submit = form.form_submit_button('Submit')
    
    c1, c2 = form.columns(2)
    
    with c1:
        
        chart1 = get_age_graph(ts_data, category_dict[category][0]).properties(title = ['VAERS', f'{category}', 'Mean age'])
        chart2 = get_agg_chart(ts_data, category_dict[category][0], 'sex', 'Sex').properties(title = [f'VAERS', f'{category}', 'Patient sex'])
        st.altair_chart(chart1)
        st.altair_chart(chart2)
    with c2:
        chart9 = get_age_graph(ts_data, category_dict[category][1]).properties(title = ['EudraVigilance', f'{category}', 'Mean age'])
        chart10 = get_agg_chart(ts_data, category_dict[category][1], 'sex', 'Sex').properties(title = ['EudraVigilance', f'{category}', 'Patient sex'])
        st.altair_chart(chart9)
        st.altair_chart(chart10)
    with form.expander('** Note on EudraVigilance age data'):
        st.caption('The EudraVigilance source data only includes patient age groups, not exact ages. These age groups are "More than 85 years", "65-85 years", "18-64 years", "3-11 years", "2 months - 2 years", and "0-1 month". For the plots above, we chose representative ages of 86, 75, 43, 14, 7, and 0.05, respectively, to represent each age group when computing averages. Since these choices are fairly arbitrary and a rough approximation of the data, the age averages plotted for EudraVigilance may not be representative of the actual values.')
    
    
    
    vaers_reportable_events = '[VAERS table of reportable events](https://vaers.hhs.gov/docs/VAERS_Table_of_Reportable_Events_Following_Vaccination.pdf)'
    vaers_guidelines = '[VAERS reporting guidelines](https://vaers.hhs.gov/reportevent.html)' 
    vaers_guidelines_archived = '[VAERS reporting guidelines archived page (from October 29, 2021)](https://web.archive.org/web/20211029034155/https://vaers.hhs.gov/reportevent.html)'
    vaers_advisory_guide = '[VAERS advisory guide](https://wonder.cdc.gov/wonder/help/vaers/VAERS%20Advisory%20Guide.htm)'
    ev_reporting = '[reporting requirements](https://www.ema.europa.eu/en/human-regulatory/research-development/pharmacovigilance/eudravigilance/eudravigilance-electronic-reporting('
    st.subheader("Data Source Comparison")

    
    st.markdown("We see notable difference in the mean patient age for VAERS and EudraVigilance reports in the plots above. For all VAERS reports, we see that there is an overall trend of increase in average age over time, with a further jump in average age for Covid vaccine reports. The overall trend of an increase in age for VAERS is likely due to a long term trend of increased adult vaccination.")
    st.markdown("On the other hand, for EudraVigilance, we see a baseline age larger than past VAERS reports with a sharp decrease in mean age with the influx of Covid vaccine reports. Similar trends hold for serious reactions. The vast majority of VAERS and EudraVigilance reports are currently, and for most of 2021 as may be seen in the plot below, related to Covid vaccines, with more than 95% of VAERS reports and around 80% of EudraVigilance reports Covid vaccine related.") 
    
    a = pd.read_json(ts_data['percentages']['cv_vaers']).rename(columns = {'RECVDATE':'Report Date'})
    a['Source'] = 'VAERS'
    b = pd.read_json(ts_data['percentages']['cv_ev'])
    b['Source'] = 'EudraVigilance'
   
    data = pd.concat([a, b])

    chart = alt.Chart(data).mark_line(strokeWidth = 4).encode(
        x=alt.X('Report Date:T', title = 'Date', axis=alt.Axis(format='%b %Y')),
        y=alt.Y("percent:Q", title = f'Percent', stack=None, axis=alt.Axis(format='%')),
        tooltip = alt.Tooltip('percent', format = '%'), color=alt.Color("Source:N", title = 'Source type')
        ).properties(width = 500, height = 200, title =  'Percent of total reports related to Covid vaccines')
    st.altair_chart(chart)  
        
    st.markdown("A large portion of past EudraVigilance reports are related to prescribed pharmaceutical drug reactions and many of the reactions are among the elderly and terminally ill patients. The influx of vaccine reports due to mass vaccination has led to a lowering of the mean age and a reduction in the percentage of reports relating to serious reactions.")

    st.subheader("VAERS")
    st.markdown("""Reports to VAERS are voluntary (although there are some listed reporting requirements for healthcare professionals) and anyone can submit a report, on behalf of themselves or someone they know that experienced an adverse reaction. Some reports are submitted by healthcare professionals, healtcare administrators, vaccine administrators, or manufacturers in response to being notified of an adverse event. Although VAERS does not record whether the source is a healthcare professional or other administrator or if the source is the a private individual submiting a report on their own behalf or someone they know, it seems that a large percentage of domestic reports are from non-professional individual sources that are reporting voluntarily. Due to the varying nature of the type of reports, it is difficult to estimate what percentage of reports for each reaction type that occur are actually recorded. While currently (November 21, 2021) there is a disclaimer on the """ +vaers_guidelines + """ mentioning reporting requirments for Covid vaccines, this addition is recent. As can be seen from this """ +vaers_guidelines_archived+ """, any reporting requirements for Covid vaccines were not mentioned as of October 29, 2021. By that point a large proportion of the adult population had already received a Covid vaccine. Moreover, any requirements for reporting for Covid vaccines are not mentioned in the """ + vaers_reportable_events +""" (as of November 21, 2021). There also does not seem to be any indication that reporting requirements are enforced when applicable.""", unsafe_allow_html = True)
    
    st.markdown("""In the VAERS data, there also seems to be a distinction in the report types and character between domestic and "foreign" reports (labeled FR for the state in the VAERS data) reports. In the """+ vaers_advisory_guide +""", it is mentioned that "*VAERS occasionally receives case reports from US manufacturers that were reported to their foreign subsidiaries. Under FDA regulations, if a manufacturer is notified of a foreign case report that describes an event that is both serious and unexpected (in other words, it does not appear in the product labeling), they are required to submit it to VAERS.*\"""", unsafe_allow_html = True)
                
    
    st.markdown("""As a result, since many of the foreign VAERS reports come from mandatory reports from vaccine manufacturers that receive notification of an adverse even report, the foreign reports are more likely to come from professional sources (as they are entered by employees or administrators) and include an increased percentage of severe reactions. While VAERS does not include indication of the source type of a report, an examination of the report text in the source data gives hints at patterns between the report types of profesional reports and reports from private individuals. Professional reports (i.e. reports by healthcare providers, administrators, vaccine manufacturers, vaccine administrators, etc.). These types of reports often begin with something like "This is a voluntary report by". They also often call the report of the events that occur a "narrative". Many of the medical professional reports also refer to the person experiencing an adverse event as the "patient" or abbreviated "pt". Searching for reports containing these terms, while not a definitive classification, can give us some clues as to what percentage of VAERS reports are submitted by professional (whether medical or administrative) sources.""") 
    
    d1, d2 = st.columns(2)
    with d1:
        st.altair_chart(get_agg_chart(ts_data, 'vaers', 'qual_0', option_title = 'Source type').properties(title = ['VAERS', 'Percent of reports mentioning', '"voluntary"', 'by source type']))
            
    with d2:
        st.altair_chart(get_agg_chart(ts_data, 'vaers', 'qual_1', option_title = 'Source type').properties(title = ['VAERS', 'Percent of reports mentioning', '"voluntary", "narrative", "patient", or "pt"', 'by source type']))
        
    st.markdown("From the above charts, we see much larger percentages of foreign reports including these terms, indicating a likely larger percentage of professional reports.")
    
    st.markdown("""For foreign reports, we also see a larger percentage of the reports for severe reactions. This is not suprising, since many of the foreign reports are submitted as a result of a notification of an adverse event to a foreign subsidiary of a US vaccine manufacturer. The chart below shows the percentage of serious reations (defined by a report of one of the following: hospitilization, prolonged existing hospitilization, disability, life-threatening reaction, congenital anomaly, or death) for each source type.""")
    
    st.altair_chart(get_agg_chart(ts_data, 'source_compare', 'serious_compare', option_title = 'Source type', sort = '-x').properties(title = ['Percent serious reactions', 'by source type']))    
    
    
    st.subheader("EudraVigilance")
    
    st.markdown("""Additionally, there is a larger percentage of serious reaction reports among EudraVigilance (especially past) reports. EudraVigilance accepts reports for all types of drugs, not only vaccines. Many of these drugs are used predominately by the elderly and those with life-threatening or chronic ilnesses and medical conditions. For example, among the most commonly occuring drugs in reports prior to March 1, 2020, are Revlimid, Eliquis, Enbrel, Xareleto, Humira, Lyrica, Taxotere, Keytruda, Pradaxa, and Tecfidera. Many of these drugs are for cancer (Revlimid, Taxotere, Keytruda) or blood clotting (Xareleto, Eliquis, Pradaxa), and sever autoimmune disorders such as rheumatoid arthritis (Enbrel, Humira), and many have severe side effects. As such, due to the types of reports received and larger mean patient age (due to reports from pharmaceutical drugs more often used in the elderly as opposed to only vaccination reports for VAERS), we see a larger percentage of severe reactions. The chart above shows the percentages of severe reaction for each source type. We see the largest percentage of severe reaction for foreign VAERS reports, for reasons due to such reports coming primarily from vaccine manufacturers in response to notifications of adverse events, with the the second largest for past EudraVigilance reports. The more recent EudraVigilance reports show a decreased percentage of severe reactions due to them being dominated by reports for Covid vaccines, changing the average age and types of reports that are received. The lowest percentage is for EudraVigilance covid vaccine reports. This may in part be due to more stringent reporting requirements for adverse events for EudraVigilance when compared to VAERS. EudraVigilance has """+ev_reporting+""" for clinical trials and marketing authorization holders to report suspected serious adverse reactions. Moreover, reporting requirements may also be instituted by EU member state regulatory authorities. These reporting requirements, together with the more standardized EudraVigilance reporting system, may lead to greater frequency of reporting among medical professionals and administrators. For Covid vaccines, the increased reporting for more subtle reactions may lower the overall percentage of serious reactions.""")
    
    st.markdown("While certain member states may allow voluntary public reporting through local portals, there does not seem to be a way to directly submit public reports to EudraVigilance. Because of this, most reports may be from either medical professionals or non-medical adminstrators or other mediators that process and submit public reports. This means that there is likely a much higher percentage of professional rerports to EudraVigilance than to VAERS. The chart below shows the percentages of reports submitted by healthcare professionals. While these percentages are not available for VAERS data, it seems likely that there is a larger percentage of healthcare professional reporting for EudraVigilance than for VAERS.")
    
    
    st.altair_chart(get_agg_chart(ts_data, 'ev', 'qual', option_title = 'Report type').properties(title = ['EudraVigilance', 'percent reports by type']))    

    
    
    
    
#     def get_counts_graph(ts_data, source = 'vaers', legend = True):
#         time_key = column_keys[source]['time']+':T'
#         data = pd.read_json(ts_data['counts'][source])
#         if legend:
#             chart = alt.Chart(data).mark_area(opacity = 0.5).encode(
#             x=alt.X(time_key, title = 'Date', axis=alt.Axis(format='%b %Y')),
#             y=alt.Y("count:Q", title = 'Reports per week', stack=None), tooltip = 'count',
#             color=alt.Color("Vtype:N", title = 'Report Type')
#             )
#         else:
#             chart = alt.Chart(data).mark_area(opacity = 0.5).encode(
#             x=alt.X(time_key, title = 'Date', axis=alt.Axis(format='%b %Y')),
#             y=alt.Y("count:Q", title = 'Reports per week', stack=None), tooltip = 'count',
#             color=alt.Color("Vtype:N", title = 'Report Type', legend = None)
#             )
#         return chart  
    
#     st.header('Report Counts')
#     st.markdown("The plots below show, for each source, the total reports per week for Covid vaccine (in blue) and non-Covid vaccine (in yellow) reports. The scale of reporting frequency for Covid vaccines dwarfs the scale of reporting for other types of reports.")
#     g1, g2 = st.columns(2)
    
#     with g1:
        
#         st.altair_chart(get_counts_graph(ts_data, 'vaers', legend = True).properties(title = ["VAERS", "Reports per week"]), use_container_width = True)
        
#     with g2:
        
#         st.altair_chart(get_counts_graph(ts_data, 'ev', legend = True).properties(title = ["EudraVigilance", "Reports per week"]), use_container_width = True)
    
#     st.header("Reports by Vaccine Type")
#     st.markdown("The percentages of Covid vaccine reports for each vaccine type are shown below.")
#     h1, h2 = st.columns(2)
    
#     with h1:
        
#         st.altair_chart(get_agg_chart(ts_data, 'cv_vaers', 'vpercentages', 'Vaccine type', sort = '-x')
#                         .properties(title = ["VAERS", "Percent or Covid vaccine reports", "by vaccine type"]), use_container_width = True)
#     with h2:
        
#         st.altair_chart(get_agg_chart(ts_data, 'cv_ev', 'vpercentages', 'Vaccine type', sort = '-x')
#                         .properties(title = ["EudraVigilance", "Percent or Covid vaccine reports", "by vaccine type"]), use_container_width = True)
        
        
#     st.altair_chart(get_agg_chart(ts_data, 'a   
        
        
        
        
    