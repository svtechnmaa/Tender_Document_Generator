import streamlit as st
import sys
import os
import logging
from utils import *
import time 
import yaml
import docxtpl
import shutil

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

    input_data, output_preview = st.columns([1, 4])
    template_path = os.path.normpath(os.environ['TEMPLATE_DIR']
                                    )
    with input_data:
        if st.button(":star2: :orange[**NEW_TEMPLATE**]", use_container_width=True):
            inititate_template_dialog(template_directory= template_path,
                                     template_name = "")

        selected_template_sets = folder_selector(folder_path = template_path)
        
    with output_preview:
        for template in selected_template_sets:
            file_list = dir_element_list(os.path.join(template_path,template),"file")
            st.subheader("Template inside template set {}".format(template))
            st.write(file_list)
            
            delete_widget, download_widget, recreate_widget = st.columns([1,1,1])
            with delete_widget:
                with st.popover(":x: :red[DELETE_{}]".format(template), use_container_width=True):
                    st.subheader("Are you ABSOLUTELY SURE you want to delete this template set {}".format(template))
                    if st.button("Confirm delete {}".format(template)):
                        shutil.rmtree(os.path.join(template_path,template))
                        st.rerun()
            with recreate_widget:
                if st.button(":pencil2: :green[RECREATE_TEMPLATE_{}]".format(template), use_container_width=True):
                    inititate_template_dialog(template_directory= template_path,
                                              template_name=template)
            with download_widget:
                font_awesome_cdn = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">'
                st.markdown(font_awesome_cdn +download_file_button(compress_folder(os.path.join(template_path,template)).getvalue(),'template_{}.zip'.format(template),"<i class='btn-icon fas fa-download'></i> DOWNLOAD_{}".format(template)),unsafe_allow_html=True)
                # if st.button(":arrow_down: :green[DOWNLOAD_{}]".format(template), use_container_width=True):
                #     st.rerun()
                    ##use the same download function as the output rendering here - inprogress