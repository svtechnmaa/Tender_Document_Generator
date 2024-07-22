import streamlit as st
import os
import sys
import logging
from utils import *

LOGGER_INIT(log_level=logging.DEBUG,
                      print_log_init = False,
                      shell_output= False) 

current_time = TIME_INIT()



st.set_page_config(
     layout="wide",
     initial_sidebar_state="expanded",
)

st.subheader("# Sample application to render tender document base on pre-defined value")
st.subheader("# Different phase will be displayed on left-hand sidebar")

pg = st.navigation([st.Page("pages/Input_New_Data.py", title="Manage Project Data", icon="✒️"), 
                    st.Page("pages/View_Current_Data.py", title="View/Edit current data", icon="👁️"),
                    st.Page("pages/Template_File_Management.py", title="Manage Template file", icon="📑"),
                    st.Page("pages/Render_Output_File.py", title="Render Output File", icon="📓")   
                    ])

pg.run()
