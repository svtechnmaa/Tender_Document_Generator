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
    template_selection_col, data_selection_col = st.columns([3, 3])


    ##########Template column management
    template_path = os.path.normpath(os.path.join(
                                                os.path.dirname(os.path.abspath(__file__)),
                                                ".." , 
                                                "templates")
                                    )
    with template_selection_col:
        st.header("TEMPLATE LIST")
        selected_template_sets = folder_selector(folder_path = template_path)
        
        for template_set in selected_template_sets:
            file_list = dir_element_list(os.path.join(template_path,template_set),"file")
            with st.popover("Preview template {}".format(template_set)):
                st.write(file_list)

    ### open data file
    yaml_file_path = os.path.normpath(
                            os.path.join(
                                os.path.dirname(os.path.abspath(__file__)),
                                ".." , 
                                "data/project_data.yaml")
                    )

    with open(yaml_file_path,'r',encoding='utf8') as data_file:
        data = yaml.safe_load(data_file,)
    st.session_state['project_data'] = data

    from streamlit_dynamic_filters import DynamicFilters
    import pandas as pd
    ## display and select required data
    with data_selection_col:
        dynamic_filters = {}
        for data_type in ["BID_INFO", "BID_OWNER"]:
            st.header("{} LIST".format(data_type))
            df = pd.DataFrame(st.session_state['project_data'][data_type])
            
            if data_type == "BID_INFO":
                dynamic_filters[data_type] = DynamicFilters(df, filters=['E_TBMT'], filters_name= data_type)
            elif data_type == "BID_OWNER":
                dynamic_filters[data_type] = DynamicFilters(df, filters=['Ben_moi_thau'], filters_name= data_type)
            dynamic_filters[data_type].display_filters()
            #dynamic_filters[data_type].display_df()


        ####Generate context data
        context_list = list()
        st.header("List context data")
        for selected_bid in  dynamic_filters["BID_INFO"].filter_df().to_dict('records'):
            # st.write(selected_bid)
            for selected_owner in dynamic_filters["BID_OWNER"].filter_df().to_dict('records'):
                context = dict()
                for key,value in selected_bid.items():
                    context[key] = value
                for key,value in selected_owner.items():
                    context[key] = value
                with st.popover(context['E_TBMT']):
                    st.write(context)

    from docxtpl import DocxTemplate

    if st.button("render"):
        for context in context_list:
            for template_set in selected_template_sets:
                template_file_list = dir_element_list(os.path.join(template_path,template_set),"file")
                for template in template_file_list:
                    template_file_path = os.path.normpath(
                                            os.path.join(
                                                template_path,
                                                template_set , 
                                                template)
                                            )
                template_object = DocxTemplate(template_file_path)
                template_object.render(context)
                template_object.save("test.docx")