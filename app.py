from pages import percent_change, vaccine_comparison, symptom_graph, demographics, introduction, methodology

import streamlit as st
import numpy as np
import altair as alt
import pandas as pd
import pickle
import datetime
import json
        
if __name__ == "__main__":
    st.set_page_config(layout="wide")
# st.markdown(
#     """ <style>
#             div[role="radiogroup"] >  :first-child{
#                 display: none !important;
#             }
#         </style>
#         """,
#     unsafe_allow_html=True
#     )  
    # Create a page dropdown
st.sidebar.title('Analysis of Covid Vaccine Adverse Event Reports')
st.sidebar.caption('From VAERS and EudraVigilance Data')

page = st.sidebar.selectbox("Select page:", ["Introduction", "Symptom Comparison", "Vaccine Comparison", "Demographics/Source Comparison", "MedDRA Terms", "Methodology"])

# page = st.sidebar.radio("Navigation menu:", ["", "Introduction", "Symptom Comparison", "Time Series", "MedDRA Symptoms", "Demographics", "Source Comparison",  "Methodology"], key = 'sidebar', index = 1) 
st.sidebar.caption('By John Dever')
st.sidebar.caption('November 21, 2021')
st.sidebar.caption('Data current up to November 19, 2021')
if page == "MedDRA Terms":
    st.title("MedDRA Terms")
    symptom_graph.app()
elif page == "Introduction":
    st.title('Introduction')
    introduction.app()
elif page == "Symptom Comparison":
    st.title('Symptom Comparison')
    percent_change.app()
elif page == "Vaccine Comparison":
    st.title("Vaccine Comparison")
    vaccine_comparison.app()
elif page == "Demographics/Source Comparison":
    st.title("Demographics and Data Source Comparison")
    demographics.app()
elif page == "Methodology":
    st.title("Methodology")
    methodology.app()
