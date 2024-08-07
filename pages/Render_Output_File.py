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

    if 'selected_template_sets' not in st.session_state:
        st.session_state['selected_template_sets'] = []
        
    if 'context_data_list' not in st.session_state:
        st.session_state['context_data_list'] = []
        
        
    selected_template_sets = []
    context_data_list = []
    ##########Template column management
    template_path = os.path.normpath(os.environ['TEMPLATE_DIR']
                                    )
    with template_selection_col:
        st.header("TEMPLATE LIST")
        selected_template_sets = folder_selector(folder_path = template_path)
        
        for template_set in selected_template_sets:
            file_list = dir_element_list(os.path.join(template_path,template_set),"file")
            with st.popover("Preview template {}".format(template_set)):
                st.write(file_list)

    ### open data file
    db_file_path = os.path.normpath(
                                os.path.join(
                                os.environ['DB_DIR'],
                                "database.sqlite")
                            )
    conn = sqlite3.connect(db_file_path)

    # st.session_state['project_data'] = data
    st.session_state['data_state']=True
    from streamlit_dynamic_filters import DynamicFilters
    import pandas as pd
    ## display and select required data
    with data_selection_col:
        dynamic_filters = {}
        for data_type in ["BID_INFO", "BID_OWNER"]:
            st.header("{} LIST".format(data_type))
            df=loading_data(conn, data_type)
            if df.empty:
                st.session_state['data_state']=False
                st.write("Data {} is empty. Please provide data in View/Edit current data to apply filters.".format(data_type))
            else:
                if data_type == "BID_INFO":
                    dynamic_filters[data_type] = DynamicFilters(df, filters=['E_TBMT'], filters_name= data_type)
                elif data_type == "BID_OWNER":
                    dynamic_filters[data_type] = DynamicFilters(df, filters=['Ben_moi_thau'], filters_name= data_type)
                dynamic_filters[data_type].display_filters()


    ####Generate context data
    if st.session_state['data_state']==True:
        for selected_bid in  dynamic_filters["BID_INFO"].filter_df().to_dict('records'):
            # st.write(selected_bid)
            for selected_owner in dynamic_filters["BID_OWNER"].filter_df().to_dict('records'):
                context = dict()
                for key,value in selected_bid.items():
                    context[key] = value
                for key,value in selected_owner.items():
                    context[key] = value
                context_data_list.append(context)
                    
        with st.popover(":cinema: :orange[Preview before render]", use_container_width=True):
            st.write(selected_template_sets)
            for context in context_data_list:
                st.write(context)
        from docxtpl import DocxTemplate

        
        if st.button(":star2: :blue[**RENDER PROJECT FILE**]", use_container_width=True):
            with st.status("Exporting data..."):
                for context in context_data_list:
                    st.write("Processing data {}...".format(context['E_TBMT']))
                    for template_set_name in selected_template_sets:
                        
                        output_dir = CREATE_EXPORT_DIR(os.path.join(os.environ['OUTPUT_DIR'],
                                                                context['E_TBMT'],
                                                                template_set_name)
                                                )
                        st.write("Creating folder {}...".format(output_dir))
                        template_file_list = dir_element_list(os.path.join(template_path,template_set),"file")
                        for template_name in template_file_list:
                            template_file_path = os.path.normpath(
                                                    os.path.join(
                                                        template_path,
                                                        template_set_name , 
                                                        template_name)
                                                    )
                            template_object = DocxTemplate(template_file_path)
                            template_object.render(context)
                            output_file_name = os.path.join(output_dir,
                                                            template_name)
                            st.write("Creating file  {}...".format(os.path.abspath(output_file_name)))
                            template_object.save(os.path.abspath(output_file_name))
            st.success('Done')
            with st.container(border = True) as container:
                col3, col4 = st.columns([8,2])
                with col3:
                    st.write("*Use beside button for download output files ...*")
                with col4:
                    st.markdown(download_file_button(compress_folder(output_dir).getvalue(),'output_{}_{}.zip'.format(context['E_TBMT'],template_set_name),"Download output"),unsafe_allow_html=True)
                # Provide user with a download button that let them download the content of each output_dir
                # this should be simple but we need a way to store/edit actual data first.