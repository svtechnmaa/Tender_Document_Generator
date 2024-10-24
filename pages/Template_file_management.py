import streamlit as st
import os
import logging
from utils import *
import shutil
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
    # input_data, output_preview = st.columns([1, 4])
    template_set = os.path.normpath(os.environ['TEMPLATE_SET_DIR'])
    template_inventory=os.path.normpath(os.environ['TEMPLATE_INVENTORY_DIR'])
    db_file_path = os.path.normpath(
                                os.path.join(
                                os.environ['DB_DIR'],
                                "database.sqlite")
                            )
    
    if 'update_state_inventory_disabled' not in st.session_state:
        st.session_state['update_state_inventory_disabled'] = True

    col1, col2= st.columns(2)
    with col1:
        if st.button(":star2: :orange[**UPLOAD TEMPLATE FILES**]", use_container_width=True):
            inititate_upload_template_files_dialog(template_directory = template_inventory)
    with col2:
        if st.button(":star2: :orange[**NEW TEMPLATE SET**]", use_container_width=True):
            inititate_template_dialog(inventory_path=template_inventory, template_path=template_set, db_path=db_file_path)

    with st.expander("Manage template set"):
        input_data, output_preview = st.columns([1, 4])
        with input_data:
            selected_template_sets = folder_selector(folder_path = template_set)
        with output_preview:
            for template in selected_template_sets:
                file_list = dir_element_list(os.path.join(template_set,template),"file")
                st.subheader("Template inside template set {}".format(template))
                for file in file_list:
                    st.markdown('<a href="/docxtemplate/Preview_template_file?file={}&type=template" target="_blank">{}</a>'.format(os.path.join(template_set,template, file), file), unsafe_allow_html=True)
                
                delete_widget, download_widget, recreate_widget = st.columns([1,1,1])
                with delete_widget:
                    with st.popover(":x: :red[DELETE_{}]".format(template), use_container_width=True):
                        st.subheader("Are you ABSOLUTELY SURE you want to delete this template set {}".format(template))
                        if st.button("Confirm delete {}".format(template)):
                            try:
                                shutil.rmtree(os.path.join(template_set,template))
                                time.sleep(3)
                                shutil.rmtree(os.path.join(template_set,template))
                            except Exception as e:
                                logging.exception("Exeption when delete template set: {}".format(e))
                            st.rerun()
                with recreate_widget:
                    if st.button(":pencil2: :green[RECREATE_{}]".format(template), use_container_width=True):
                        inititate_recreate_template_dialog(inventory_path=template_inventory, template_path=template_set, db_path=db_file_path, template_name=template)
                with download_widget:
                    font_awesome_cdn = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">'
                    st.markdown(font_awesome_cdn +download_file_button(compress_folder(os.path.join(template_set,template)).getvalue(),'template_{}.zip'.format(template),"<i class='btn-icon fas fa-download'></i>DOWNLOAD_{}".format(template)),unsafe_allow_html=True)

    with st.expander("Manage template inventory"):
        all_files=pd.DataFrame()
        for t in ['EHSDT','AHSDT','ThauGiay','English']:
            all_files=pd.concat([all_files, pd.DataFrame({'Delete?': False,'Type': t, 'File': dir_element_list(folder_path=os.path.join(template_inventory, t), element_type='file')})])
        if all_files.empty:
            st.data_editor(data=pd.DataFrame(columns=['Delete?','Type','File','Preview file']), use_container_width = True, key='manage_template_inventory',hide_index=True, disabled=["File", 'Type','Preview file'])
        else:
            update_button= st.popover("UPDATE", disabled=st.session_state.get("update_state_inventory_disabled",True))
            all_files['Preview file']=all_files.apply(lambda x: '/docxtemplate/Preview_template_file?file={}&type=template'.format(os.path.join(template_inventory, x['Type'], x['File']), x['File']), axis=1)
            table_inventory=st.data_editor(data=all_files, use_container_width = True, key='manage_template_inventory',hide_index=True, disabled=["File", 'Type','Preview file'], 
                                        on_change=change_update_button_state, args=("update_state_inventory_disabled",),
                                        column_config={
                                            "Preview file": st.column_config.LinkColumn(
                                                display_text="Open link"
                                            )
                                        }) 

            with update_button:
                delete_files=table_inventory.loc[table_inventory['Delete?']==True]
                st.subheader("Are you ABSOLUTELY SURE you want to delete list files {} from template inventory?".format(', '.join((delete_files['Type'] + '/' + delete_files['File']).tolist())))
                if st.button("CONFIRM"):
                    for index, row in delete_files.iterrows():
                        os.remove(os.path.join(template_inventory, row['Type'], row['File']))
                    st.success('Done')
                    st.session_state["update_state_inventory_disabled"]=True
                    st.rerun()