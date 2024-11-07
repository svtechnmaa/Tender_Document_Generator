import streamlit as st
import os
import logging
from utils import *
import shutil
import threading
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
                                thread = threading.Thread(target=delete_folder_after, args=(os.path.join(template_set,template),15,))
                                thread.start()
                            except Exception as e:
                                logging.exception("Exception when delete template set:: {}".format(e))
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
            CREATE_EXPORT_DIR(os.path.join(template_inventory, t))
            all_files=pd.concat([all_files, pd.DataFrame({'Delete?': False,'Type': t, 'File': dir_element_list(folder_path=os.path.join(template_inventory, t), element_type='file')})])
        if all_files.empty:
            st.data_editor(data=pd.DataFrame(columns=['Delete?','Type','File','Preview file']), use_container_width = True, key='manage_template_inventory',hide_index=True, disabled=["File", 'Type','Preview file'])
        else:
            all_files.reset_index(drop=True, inplace=True)
            update_button= st.popover("UPDATE", disabled=st.session_state.get("update_state_inventory_disabled",True))
            all_files['Preview']=all_files.apply(lambda x: '/docxtemplate/Preview_template_file?file={}&type=template'.format(os.path.join(template_inventory, x['Type'], x['File'])), axis=1)
            all_files['Type'] = all_files['Type'].astype(pd.CategoricalDtype(['EHSDT','AHSDT','ThauGiay','English']))
            table_inventory=st.data_editor(data=all_files, use_container_width = True, key='manage_template_inventory',hide_index=True, disabled=['Preview'], 
                                        on_change=change_update_button_state, args=("update_state_inventory_disabled",),
                                        column_config={
                                            "Preview": st.column_config.LinkColumn(
                                                display_text="Open link"
                                            )
                                        }) 

            with update_button:
                delete_files=table_inventory.loc[table_inventory['Delete?']==True]
                editable_columns = ['File', 'Type']
                changed_files=pd.DataFrame([(*[all_files.at[i,col] for col in editable_columns], *[row[col] for col in editable_columns]) for i, row in table_inventory.iterrows() if (any(all_files.at[i, col] != row[col] for col in editable_columns) and row['Delete?']==False)], columns=[f'old_{col}' for col in editable_columns]+[f'new_{col}' for col in editable_columns])
                
                ###check duplicate for rename file###
                grouped_changed_files = changed_files.groupby('new_Type')
                duplicate_files=[]
                for new_type, sub_df in grouped_changed_files:
                    current_files_in_dir=dir_element_list(folder_path=os.path.join(template_inventory,new_type), element_type='file')
                    duplicate_files+=[new_type+'/'+f for f in list(set(sub_df['new_File'].unique()) & set(current_files_in_dir))]
                if duplicate_files:
                    st.error('Duplicate. List file {} already exist in template inventory.'.format(duplicate_files), icon="🚨")
                else:
                    if not delete_files.empty and not changed_files.empty:
                        st.subheader("Are you ABSOLUTELY SURE you want to template inventory delete {} and update {} to {}".format(', '.join(delete_files['File'].to_list()),', '.join((changed_files['old_Type'] + '+' + changed_files['old_File']).tolist()), ', '.join((changed_files['new_Type'] + '+' + changed_files['new_File']).tolist())))
                    elif not delete_files.empty:
                        st.subheader("Are you ABSOLUTELY SURE you want to template inventory delete {}".format(', '.join(delete_files['File'].to_list())))
                    elif not changed_files.empty:
                        st.subheader("Are you ABSOLUTELY SURE you want to template inventory update {} to {}".format(', '.join((changed_files['old_Type'] + '/' + changed_files['old_File']).tolist()), ', '.join((changed_files['new_Type'] + '/' + changed_files['new_File']).tolist())))
                    
                    if st.button("CONFIRM"):
                        if not delete_files.empty:
                            [os.remove(os.path.join(template_inventory, row['Type'], row['File'])) for index, row in delete_files.iterrows()]
                        if not changed_files.empty:
                            [shutil.move(os.path.join(template_inventory, row['old_Type'], row['old_File']), os.path.join(template_inventory, row['new_Type'], row['new_File'])) for index, row in changed_files.iterrows()]
                        st.success('Done')
                        st.session_state["update_state_inventory_disabled"]=True
                        time.sleep(1)
                        st.rerun()