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
create_default_table(os.path.normpath(
                                os.path.join(
                                os.environ['DB_DIR'],
                                "database.sqlite")
                            ))
pg = st.navigation([st.Page("pages/Edit_var_list.py", title="View/Edit variable list", icon="✒️"),
                    st.Page("pages/View_current_data.py", title="View/Edit current data", icon="👁️"),
                    st.Page("pages/Template_file_management.py", title="Manage Template file", icon="📑"),
                    st.Page("pages/Render_Output_File.py", title="Render Output File", icon="📓")   
                    ])
pg.run()
