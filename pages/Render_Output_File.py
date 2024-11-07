import streamlit as st
import os
import logging
from utils import *
from docxtpl import DocxTemplate
import pandas as pd
from glob import glob
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
    st.header("FORM TYPE")
    bid_type = st.selectbox("Select form type", ['EHSDT','AHSDT','ThauGiay','English'])
    data_selection_col, template_selection_col = st.columns([3, 3])

    if 'selected_template_sets' not in st.session_state:
        st.session_state['selected_template_sets'] = []
        
    if 'context_data_list' not in st.session_state:
        st.session_state['context_data_list'] = []

    if 'data_state' not in st.session_state:
        st.session_state['data_state']=True

    selected_template_sets = []
    context_data_list = []
    list_template_selected=[]
    
    ### open data file
    db_file_path = os.path.normpath(
                                os.path.join(
                                os.environ['DB_DIR'],
                                "database.sqlite")
                            )
    conn = sqlite3.connect(db_file_path)
    ## display and select required data
    with data_selection_col:
        all_data={}
        select_data={}
        for data_type in ["BID_INFO", "BID_OWNER"]:
            st.header("{} LIST".format(data_type))
            all_data[data_type]=loading_data(conn, data_type).drop(columns=['ID', 'type','time'])
            if all_data[data_type].empty:
                st.session_state['data_state']=False
                st.write("Data {} is empty. Please provide data in View/Edit current data to apply filters.".format(data_type))
            elif data_type == "BID_INFO" and ('Form_type' not in all_data[data_type].columns or all_data[data_type]['Form_type'].isnull().all()):
                st.session_state['data_state']=False
                st.write("No BID_INFO has Form_type value. Please provide Form_type in View/Edit current data to apply filters.".format(data_type))
            else:
                if data_type == "BID_INFO":
                    select_data[data_type]=st.multiselect("Select E_TBMT", sorted(all_data[data_type].loc[all_data[data_type]['Form_type']==bid_type]['E_TBMT'].unique()))
                elif data_type == "BID_OWNER":
                    select_data[data_type]=st.multiselect("Select Ten_viet_tat_BMT", sorted(all_data[data_type]['Ten_viet_tat_BMT'].unique()))

    ####Generate context data
    if st.session_state['data_state']==True and select_data['BID_INFO'] and select_data['BID_OWNER']:
        selected_bid=all_data['BID_INFO'].loc[all_data['BID_INFO']['E_TBMT'].isin(select_data['BID_INFO'])]
        selected_owner=all_data['BID_OWNER'].loc[all_data['BID_OWNER']['Ten_viet_tat_BMT'].isin(select_data['BID_OWNER'])]
        context_data_list=selected_bid.assign(key=1).merge(selected_owner.assign(key=1), on='key').drop('key', axis=1).to_dict('records')

    ##########Template column management
    template_set = os.path.normpath(os.environ['TEMPLATE_SET_DIR'])
    template_inventory=os.path.normpath(os.environ['TEMPLATE_INVENTORY_DIR'])
    with template_selection_col:
        st.header("TEMPLATE SET LIST")
        if context_data_list:
            selected_template_sets = folder_selector(folder_path = template_set, regex=r'({})_{}.*'.format('|'.join([item['Ten_viet_tat_BMT'] for item in context_data_list]),bid_type))
        else:
            st.multiselect('Select folders', [])

        for template_set_selected in selected_template_sets:
            file_list = dir_element_list(os.path.join(template_set,template_set_selected),"file")
            with st.popover("Preview template {}".format(template_set_selected)):
                list_all_files=pd.DataFrame({'Select?': True, 'List files': file_list})
                select_files=st.data_editor(list_all_files, hide_index=True, disabled=["List files"], key='select_files_for_template_{}'.format(template_set_selected))
                list_template_selected+=[os.path.join(template_set,template_set_selected, file) for file in select_files.loc[select_files['Select?']==True]['List files'].to_list()]

        st.header("LIST FILES TEMPLATE")
        selected_template_files = file_selector(folder_path = os.path.join(template_inventory, bid_type))
        if selected_template_files:
            st.markdown('<p style="font-size: 12px;">Selected files {} to render output.</p>'.format(', '.join(selected_template_files)), unsafe_allow_html=True)
            list_template_selected+=[os.path.join(template_inventory,bid_type, file) for file in selected_template_files]

    if st.session_state['data_state']==True and context_data_list and list_template_selected:               
        with st.popover(":cinema: :orange[Preview before render]", use_container_width=True):
            st.subheader('List template files:')
            for f in list_template_selected:
                st.markdown('<a href="/docxtemplate/Preview_template_file?file={}&type=template" target="_blank">{}</a>'.format(f, '/'.join(f.split('/')[-2:])), unsafe_allow_html=True)
            st.subheader('List context data:')
            for context in context_data_list:
                st.write(context)
        if st.button(":star2: :blue[**RENDER PROJECT FILE**]", use_container_width=True):
            with st.status("Exporting data..."):
                list_output_dir=[]
                for context in context_data_list:
                    st.write("Processing data {}...".format(context['E_TBMT']))
                    output_dir=os.path.join(os.environ['OUTPUT_DIR'],context['Ten_viet_tat_BMT'], context['E_TBMT'])
                    if os.path.isdir(output_dir):
                        [os.remove(file) for file in glob(os.path.join(output_dir,'*'))]
                    else:
                        CREATE_EXPORT_DIR(output_dir)
                    st.write("Creating folder {}...".format(output_dir))
                    for template_file in list_template_selected:
                        template_object = DocxTemplate(template_file)
                        template_object.render(context)
                        output_file_name = os.path.join(output_dir, os.path.basename(template_file))
                        st.write("Creating file  {}...".format(os.path.abspath(output_file_name)))
                        template_object.save(os.path.abspath(output_file_name))
                    list_output_dir.append({'output_dir': output_dir, 'Ten_viet_tat_BMT':context['Ten_viet_tat_BMT'], 'E_TBMT':context['E_TBMT']})
            st.success('Done')
            with st.expander("Preview output data"):
                for item in list_output_dir:
                    download_data, preview_data = st.columns([3, 7])
                    with download_data:
                        st.markdown(download_file_button(compress_folder(item['output_dir']).getvalue(),'output_{}_{}.zip'.format(item['Ten_viet_tat_BMT'],item['E_TBMT']),"Download output of {} bid {}".format(item['Ten_viet_tat_BMT'], item['E_TBMT'])),unsafe_allow_html=True)
                    with preview_data:
                        for file in dir_element_list(folder_path=item['output_dir'], element_type='file'):
                            st.markdown('<a href="/docxtemplate/Preview_template_file?file={}&type=output" target="_blank">{}</a>'.format(os.path.join(item['output_dir'], file), file), unsafe_allow_html=True)