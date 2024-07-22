import streamlit as st
import sys
import os
import logging
from utils import *
import time 

## EXPLAIN: setting shell_output = False will create a default log Streamhandler, which by default send all   all Python log to stderr
## then we send all console stdout to TerminalOutput tab
## all stderr data (which include formatted log) to the LogData tab



######################## Logging TAB ##########################################
with st.sidebar:
    TerminalOutput, LoggingOutput= init_logging_popup_button()


with st_stdout("code",TerminalOutput, cache_data=True), st_stderr("code",LoggingOutput, cache_data=True):
    
    #Initiate the session state var to store new info
    if "bid_info_input_dict" not in st.session_state:
        st.session_state["bid_info_input_dict"] = ''

    if "customer_info_input_dict" not in st.session_state:
        st.session_state["customer_info_input_dict"] = ''

    #Initiate the input button content base on input schema
    input_schema_file_path = os.path.normpath(
                                os.path.join(
                                os.path.dirname(os.path.abspath(__file__)),
                                ".." , 
                                "data",
                                "input_data_schema.yaml")
                            )
    with open(input_schema_file_path,'r',encoding='utf8') as data_file:
        input_schema = yaml.safe_load(data_file,)

    if st.button(":star2: :orange[**NEW_BID_INFO**]", use_container_width=True):
        init_bid_input_info_form_locked( bid_info_schema = input_schema["BID_INFO"])

    if st.button(":star2: :orange[**NEW_CUSTOMER_INFO**]", use_container_width=True):
        init_customer_input_info_form_locked( customer_info_schema = input_schema["BID_OWNER"])  
    ##saving operation should be done inside the function, not in the main thread here.
    
    #========================================================================================
    #sample loading and displaying current data in the data store
    #3 main problem is : 
    # 1. the content (list of field key for each item  ) of BID_INFO and BID_OWNER are subject to change
    # 2. user must be able to edit/save previous BID_INFO and BID_OWNER field without affecting new input schema or other rows
    # 3. user must be able to edit/save previous BID_INFO and BID_OWNER regardless of wherethere that row comply to CURRENT input_schema or not
    yaml_data_file_path = os.path.normpath(
                            os.path.join(
                                os.path.dirname(os.path.abspath(__file__)),
                                ".." , 
                                "data/project_data.yaml")
    )
    with open(yaml_data_file_path,'r',encoding='utf8') as data_file:
        data = yaml.safe_load(data_file,)

    st.header("SVTECH INFO")
    st.dataframe(data['SVTECH_INFO'],use_container_width = True)

    st.header("BID_OWNER LIST")
    st.dataframe(data['BID_OWNER'],use_container_width = True)
    
    st.header("BID_INFO LIST")
    st.dataframe(data['BID_INFO'],use_container_width = True)
    