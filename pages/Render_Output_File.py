import streamlit as st
import sys
import os
import logging
from utils import *
import time 
import yaml
import docxtpl

## EXPLAIN: setting shell_output = False will create a default log Streamhandler, which by default send all   all Python log to stderr
## then we send all console stdout to TerminalOutput tab
## all stderr data (which include formatted log) to the LogData tab

LOGGER_INIT(log_level=logging.DEBUG,
                      print_log_init = False,
                      shell_output= False) 

######################## Logging TAB ##########################################
with st.sidebar:
    TerminalOutput, LoggingOutput= init_logging_popup_button()


with st_stdout("code",TerminalOutput, cache_data=True), st_stderr("code",LoggingOutput, cache_data=True):
    if "bid_info_input_dict" not in st.session_state:
        st.session_state["bid_info_input_dict"] = ''

    if "customer_info_input_dict" not in st.session_state:
        st.session_state["customer_info_input_dict"] = ''

    yaml_file_path = os.path.normpath(
                            os.path.join(
                                os.path.dirname(os.path.abspath(__file__)),
                                ".." , 
                                "data/project_data.yaml")
                    )
    with open(yaml_file_path,'r',encoding='utf8') as data_file:
        data = yaml.safe_load(data_file,)

    st.session_state['project_data'] = data
    st.data_editor(st.session_state['project_data']['SVTECH_INFO'])
    st.data_editor(st.session_state['project_data']['BID_INFO'], key='E_TBMT', num_rows="dynamic")
    st.data_editor(st.session_state['project_data']['BID_OWNER'])

    from docxtpl import DocxTemplate
    template_file_path = os.path.normpath(
                            os.path.join(
                                os.path.dirname(os.path.abspath(__file__)),
                                ".." , 
                                "templates/Form1/1.2 THU BLDT VCB Firewall.docx")
                    )
    template_object = DocxTemplate(template_file_path)
    context = dict()
    for key,value in st.session_state['project_data']['BID_INFO'][0].items():
        context[key] = value
    for key,value in st.session_state['project_data']['BID_OWNER'][0].items():
        context[key] = value
    st.write(context)
    

    template_object.render(context)
    if st.button("render"):
        template_object.save("test.docx")