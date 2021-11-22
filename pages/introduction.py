
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
    
    with open('data/ts_data.json', 'r') as f:
        ts_data = json.load(f)
    ev_link = '[EudraVigilance](https://www.ema.europa.eu/en/human-regulatory/research-development/pharmacovigilance/eudravigilance)'
    vaers_link = '[VAERS](https://vaers.hhs.gov/)'
    addreports_link = '[Addreports](https://www.adrreports.eu/en/eudravigilance.html)'
    wonder_link = '[CDC VAERS WONDER](https://wonder.cdc.gov/vaers.html)'                   
    bioportal_link = '[BioPortal](https://bioportal.bioontology.org/)'
    vaers_dl = '[here](https://vaers.hhs.gov/data/datasets.html)'
    meddra_link = '[MedDRA](https://www.meddra.org/)'
    meddra_coding = '[MedDRA - Terminologies & Coding](https://meddra.org/sites/default/files/page/documents_insert/meddra_-_terminologies_coding.pdf)'
    st.markdown("""The purpose of this application is to provide tools for meaningful and accessible analysis of Covid vaccine adverse event data. In particular, we hope to provide tools for the user to identify possible adverse events or commonly reported side effect symptoms of Covid vaccines when compared to control data. The primary tool for this is the "Symptom Comparison" tool, which may be accessed from the navigation menu to the left.""") 
    st.subheader('Data Sources')
    st.markdown("""Data is drawn from  the Vaccine Adverse Event Reporting System (""" + vaers_link + """), a vaccine pharmacovilance reporting system, managed by the US FDA and CDC, as well as """+ev_link+""", (standing for European Union Drug Regulating Authorities Pharmacovigilance), a drug pharmacovigilance system run by the European Medicines Agency (EMA). The VAERS data includes approximately 1.7 million reports dating from July 1990 up to November 5, 2021. EudraVigilance data includes more than 3 million reports, although here we use approximately 2.4 million reports ranging from 2018 up to November 7, 2021. (Select the "Demographics/Source comparison" and "Methodology" pages from the menu on the left for more information about these data sources and methods used to obtain and process the data.)""", unsafe_allow_html = True)
    
    st.markdown("""VAERS allows for public download of the data ("""+vaers_dl+""") and provides limited search and analysis through """+wonder_link+""". EudraVigilance also allows public access to (more limited) report data, although the data (to include all reports) must be downloaded indirectly through the """+addreports_link+""" sytem (See "Methodology" for more information.) . Addreports also provides limited analysis of the data. However, both WONDER and Addreports, as well as most other publicly available tools to analyze adverse event data relating to Covid vaccines, focus on only one source, do not allow comparisons with different parts of the data, and only provide raw numbers of counts of cases (for specific symptoms) without normalization or comparison to a control group.""", unsafe_allow_html = True)
    
    st.subheader('Normalization and Control Groups for Symptom Comparison')
    
    st.markdown("""The charts below show total an overlay of the counts per week of reports submitted to VAERS and EudraVigilance for non-Covid vaccine related reports (in yellow) and Covid vaccine reports (in blue). As can be seen, the scale of the frequency of reports relating to the Covid vaccines is much larger, for either source, than the scale for the frequency of reports related to any other cause.""")
    
    with open('data/ts_data.json', 'r') as f:
        ts_data = json.load(f)
    column_keys = {'vaers':{'time':'RECVDATE', 'age':'AGE_YRS'}, 'ev':{'time':'Report Date', 'age': 'Age_approx'}}


    def get_counts_graph(ts_data, source = 'vaers', legend = True):
        time_key = column_keys[source]['time']+':T'
        data = pd.read_json(ts_data['counts'][source])
        if legend:
            chart = alt.Chart(data).mark_area(opacity = 0.5).encode(
            x=alt.X(time_key, title = 'Date', axis=alt.Axis(format='%b %Y')),
            y=alt.Y("count:Q", title = 'Reports per week', stack=None),
            color=alt.Color("Vtype:N", title = 'Report Type')
            )
        else:
            chart = alt.Chart(data).mark_area(opacity = 0.5).encode(
            x=alt.X(time_key, title = 'Date', axis=alt.Axis(format='%b %Y')),
            y=alt.Y("count:Q", title = 'Reports per week', stack=None),
            color=alt.Color("Vtype:N", title = 'Report Type', legend = None)
            )
        return chart  
    
    
    g1, g2 = st.columns(2)
    
    with g1:
        
        st.altair_chart(get_counts_graph(ts_data, 'vaers', legend = True).properties(title = ["VAERS", "Reports per week"]), use_container_width = True)
        
    with g2:
        
        st.altair_chart(get_counts_graph(ts_data, 'ev', legend = True).properties(title = ["EudraVigilance", "Reports per week"]), use_container_width = True)
    
    st.markdown("""Due to the large increase in scale of the number of reports, we would expect an increased number of reports for a variety of symptoms. Without appropriately normalizing to get a rate of occurence of particular symptoms, it would not be meaningful to look at change in the raw counts of symptom occurence without accounting for the change in scale.""")
    st.markdown("Similarly, among the vaccine types or report types that we will use for comparison, there are differences in scale that would prohibit direct comparison of counts. On the right we see the percentage of reports for each Covid vaccine type for each source.")
        
    
    def get_agg_chart(ts_data, source = 'vaers', option = 'sex', option_title = 'Sex', vertical = False, sort = None):
        data = pd.read_json(ts_data['agg'][source][option]).reset_index()
        chart = alt.Chart(data).mark_bar().encode(
        y=alt.Y('index:N', title = option_title, sort = sort),
        x=alt.X('percent:Q', title = 'Percent', stack=None, axis=alt.Axis(format='%')), tooltip = alt.Tooltip('percent', format = '%'), color=alt.Color("index:N", title = 'Report Type', legend = None)
        )
        return chart  

       
    chart1 = get_agg_chart(ts_data, 'cv_vaers', 'vpercentages', 'Vaccine type', sort = '-x').properties(title = ["VAERS", "Percent or Covid vaccine reports", "by vaccine type"], height = 75)
        
    chart2 = get_agg_chart(ts_data, 'cv_ev', 'vpercentages', 'Vaccine type', sort = '-x').properties(title = ["EudraVigilance", "Percent or Covid vaccine reports", "by vaccine type"], height = 75)
      
    st.altair_chart(chart1|chart2)
    
    st.markdown("We normalize symptom frequencies of reports of a particular type by comparing them to the total number of reports of that type. In other words, we look at the rate of occurence of symptoms with respect to the number of reports.")
    st.markdown("""These report frequency rates for symptoms are still not very meaningful by themselves since, as we do not know how often a particular symptom is actually reported to these systems, we have no way of getting the true rates of occurence. However, we can compare the rates to rates of control groups. For this purpose we use both reports related to influenza vaccines and past reports prior to the introduction fo Covid vaccines.""")
        
    st.subheader('Symptom Terminology')
    st.markdown("""Symptoms are coded in both VAERS and EudraVigilance source data using """+meddra_link+""" (Medical Dictionary for Regulatory Activities) terminology. MedDRA terms are layered by a class structure, where particular terms have subclasses of more specific terms. We call the most general (or highest level) terms layer 0 terms. These are called "System Organ Classes" in MedDRA, and there are 27 of them. Terms such as "Blood and lymphatic system disorders" or "Cardiac disorders" are members of this group. We will call subclasses of layer 0 terms layer 1 terms, and subclasses of layer 1 terms are called layer 2, etc. Layer 3 terms are called "Preferred Terms" in MedDRA terminology. "Arrhythmia" is an example of a layer 3 term. It is a subclass of the layer 2 term "Rate and rhythm disorders NEC", which is a subclass of "Cardiac arrhythmias", which in turn is a subclass of the layer 0 term "Cardiac disorders".  Layer 4 terms, called "Lowest Level Terms" in MedDRA terminology, are the most specific. There are more than 23,000 Preferred Terms (layer 3) and more than 80,000 Lowest Level Terms (layer 4) in the full MedDRA dictionary. The vast majority of terms found in the VAERS and EudraVigilance source data are at layer 3 (i.e. MedDRA Preferred Terms). (See the pdf """ +meddra_coding+""" for more information about MedDRA coding and terminology.)""" , unsafe_allow_html = True)
    
    st.markdown("""In order to identify symptoms that occur at an unusual rate relative to control data, it would be helpful to be able to group similar symptoms for comparison. We do this using MedDRA classes by grouping a symptom with others that share a lower level layer. With this method we can group symptoms for comparison at different levels of generality. For example, say "Arrhythmia" is reported a certain number of times. Since it is a subclass of the layer 2 term "Rate and rhythm disorders NEC", we would also record that same number of occurences for "Rate and rhythm disorders NEC" (and for the layers 1 and 0 terms "Cardiac arrhythmias" and "Cardiac disorders", respectively). Then when calculating relative frequencies, we do so for terms on each symptom layer. To avoid overcounting lower level terms, we only allow at most one of each type of term for each report (See "Methodology" for more information.). Unfortunately, the MedDRA dictionary is not available to the public. In order to construct our connections of classes and subclasses for analysis, we scraped the connections for subclasses only for terms found in the source VAERS and EudraVigilance data from """ +bioportal_link+ """ using the REST API. Using this method we end up with more than 20,000 terms, including more than 18,000 layer 3 terms, along with the relations between classes. See the "MedDRA Symptoms" page to explore the connections between these terms interactively.""")
    
    st.markdown("""For both data sources, similar symptoms are reported with a variety of different terms, many of which may have similar meaning. Only looking at specific terms and ignoring similar terms makes it difficult to notice signals for more general symptoms. As a result, it is difficult to see the significance of the reported numbers in context, much less to find signals about particular symptoms or related groups of symptoms. For our comparison, we use the layer structure of MedDRA terms to compare terms at each symptom layer. Using these methods, in the "Symptom Comparison" page we provide a tool to compare rates (relative frequencies) of symptom occurence for reports relating to covid vaccines to rates of corresponding symptoms for past reports and reports related to influenza vaccines for symptoms at each symptom layer. """)
    
    st.subheader("Results")
    st.markdown("""The Covid vaccines show significantly increased (in some cases increases of several thousand percent at the level of layer 1 terms (MedDRA Highest Level Group Terms)) relative frequencies of reports relating to embolism and thrombosis, myocardial and pericardial disorders (and related cardiac conditions), and mestrual and uterine bleeding disorders compared to relative frequencies of corresponding symptoms in the control groups of influenza vaccines or past data prior to the introduction of Covid vaccines.""")
    st.markdown("""These measurements are not rates of absolute risk, however, since they are only relative to rates of reporting to these surveillance systems with respect to a control group. Also, these rates of increase must be interpreted with caution as rare symptoms for the control group may show large percent increases in the comparison group only because they are particularly rare (or the control group is too small to ensure the sample is represented with proper proporitions) or less likely to be reported within the control group or due to idiosyncratic or time dependent use of terminology in symptom reporting. For example, updates to the MedDRA dictionary may create new terms that would only be used after the update. In order to control for some of these issues, we compare symptoms between lower layers of MedDRA terms. Since the lower level subclass terms are more general, this makes it less likely that we will be comparing a term in the comparison layer to a term that is unusual in the control layer (while another member of the same subclass may be more common, for example). Additionally, in order to avoid comparing extremely rare symptom in the control group, we provide a control frequency threshold on the "Symptom comparison" page, where particularly rare symptoms in the control group are not compared at all.""")
    st.markdown("However, at even low symptom layers and with increased control frequency threshold (it should not be too high as well in order to not exclude rare but significant symptoms), many of the same types of symptoms relating to embolism and thrombosis, abnormal menstrual issues (many of the pulmonary vascular disorder conditions and menstrual cycle and uterine bleeding disroder conditions), and cardiac conditions (especially myocardial and pericardial disorders) persist among the largest percent increases for each layer. Moreover, the past reports for EudraVigilance include a higher proportion of severe type reactions as the data includes reports not only for vaccines, but all types of drugs including drugs for sever and terminal illness. The same type of symptoms still show increases when comparing the Covid EudraVigilance vaccine data to past EudraVigilance reports. Also, the sampe type of increases persist for each type of source data, despite the differences in types of reports for that source, providing more evidence that these changes are signals of actual side effects from the Covoid vaccines.")
    st.markdown(""" The results and above considerations suggest, that while these increases do not provide rates of absolute risk, that these types of symptoms consititue real side effects that are highly unusual in their prevalence with respect to Covid vaccines.""")
    
    
