import streamlit as st
import os
import sys
import logging
from utils import *

st.set_page_config(
     layout="wide",
     initial_sidebar_state="expanded",
)

LOGGER_INIT(log_level=logging.DEBUG,
                      print_log_init = False,
                      shell_output= False) 

current_time = TIME_INIT()



st.title("# Sample application to render tender document base on pre-defined value")
st.subheader("# Different phase will be displayed on left-hand sidebar")

