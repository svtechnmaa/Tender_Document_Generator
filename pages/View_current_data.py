import streamlit as st
import os
import logging
from utils import *
from datetime import datetime

## EXPLAIN: setting shell_output = False will create a default log Streamhandler, which by default send all   all Python log to stderr
## then we send all console stdout to TerminalOutput tab
## all stderr data (which include formatted log) to the LogData tab

LOGGER_INIT(log_level=logging.DEBUG,
                      print_log_init = False,
                      shell_output= False) 

######################## Logging TAB ##########################################
with st.sidebar:
    TerminalOutput, LoggingOutput= init_logging_popup_button()     
st.markdown("""
            <style>
                div[data-testid="column"] {
                    width: fit-content !important;
                    flex: unset;
                }
                div[data-testid="column"] * {
                    width: fit-content !important;
                }
            </style>
            """, unsafe_allow_html=True)
with st_stdout("code",TerminalOutput, cache_data=True), st_stderr("code",LoggingOutput, cache_data=True):
    ##########INPUT NEW DATA##########
    if "bid_info_input_dict" not in st.session_state:
        st.session_state["bid_info_input_dict"] = ''

    if "customer_info_input_dict" not in st.session_state:
        st.session_state["customer_info_input_dict"] = ''
    input_schema_file_path = os.path.normpath(
                                os.path.join(
                                os.environ['DB_DIR'],
                                "input_data_schema.yaml")
                            )
    db_file_path = os.path.normpath(
                                os.path.join(
                                os.environ['DB_DIR'],
                                "database.sqlite")
                            )
    template_set = os.path.normpath(os.environ['TEMPLATE_SET_DIR'])
    input_schema=read_config_yaml(input_schema_file_path)
    conn = sqlite3.connect(db_file_path, check_same_thread=False)
    if st.button(":star2: :orange[**NEW_BID_INFO**]", use_container_width=True):
        init_bid_input_info_form_locked( bid_info_schema = input_schema["BID_INFO"], conn= conn)

    if st.button(":star2: :orange[**NEW_CUSTOMER_INFO**]", use_container_width=True):
        init_customer_input_info_form_locked( customer_info_schema = input_schema["BID_OWNER"], conn= conn)
    
    ##########LISTING CURRENT DATA##########
    unique_key_col={'BID_INFO':'E_TBMT','BID_OWNER':'Ten_viet_tat_BMT','SVTECH_INFO':'Ten_nha_thau'}
    for i in ['SVTECH_INFO','BID_OWNER','BID_INFO']:
        st.header(i if 'SVTECH' in i else i+' LIST')
        save_widget, import_widget = st.columns(2)
        with save_widget:
            save_button=st.popover("Update", disabled=st.session_state.get(f"update_state_{i}_disabled",True))
        with import_widget:
            import_button=st.button("Import data",key=f"button_import_{i}")
        if import_button:
            inititate_import_data_dialog(i,conn)
        current_data=loading_data(conn, i)
        if current_data.empty:
            current_data = pd.DataFrame(columns=input_schema[i])
        else:
            column_order=input_schema[i]+sorted(list(set(list(current_data)) - set(input_schema[i])),reverse=True)
            current_data = current_data.reindex(columns=column_order)
        current_data.insert(loc=0, column='Delete?', value=False)
        if i=='BID_INFO':
            current_data['Form_type'] = current_data['Form_type'].astype(pd.CategoricalDtype(['EHSDT','AHSDT','ThauGiay','English']))
        if i!='SVTECH_INFO':
            new_data=st.data_editor(key=f"current_data_{i}",data= current_data,use_container_width = True,disabled=["time"], args=(f"update_state_{i}_disabled",),on_change=change_update_button_state, hide_index=True, column_config={'ID':None,'type':None,'time':None})
        else:
            new_data=st.data_editor(key=f"current_data_{i}",data= current_data,use_container_width = True,disabled=["time"], args=(f"update_state_{i}_disabled",),on_change=change_update_button_state, hide_index=True, column_config={'ID':None,'type':None,'time':None,'Delete?':None})
        with save_button:
            if not current_data.empty:
                cur = conn.cursor()
                delete_data=new_data.loc[new_data['Delete?']==True]
                diff_data=(current_data.merge(new_data.loc[new_data['Delete?']==False], how='outer', indicator=True).query("_merge == 'right_only'")[current_data.columns])
                if not delete_data.empty and not diff_data.empty:
                    st.subheader("Are you ABSOLUTELY SURE you want to this {} delete {} and update {}".format(i,', '.join(delete_data[unique_key_col[i]].to_list()),', '.join(diff_data[unique_key_col[i]].to_list())))
                elif not delete_data.empty:
                    st.subheader("Are you ABSOLUTELY SURE you want to this {} delete {}".format(i,', '.join(delete_data[unique_key_col[i]].to_list())))
                elif not diff_data.empty:
                    st.subheader("Are you ABSOLUTELY SURE you want to this {} update {}".format(i,', '.join(diff_data[unique_key_col[i]].to_list())))
                if st.button("CONFIRM", key=f"button_{i}"):
                    if i!='SVTECH_INFO':
                        duplicated_in_data=new_data.duplicated(subset=[unique_key_col[i]])
                        if duplicated_in_data.any():
                            st.error("Duplicated {} value {} in data".format(i,', '.join(new_data.loc[~duplicated_in_data][unique_key_col[i]].to_list())))
                            continue
                    if not delete_data.empty:
                        cur.execute('DELETE FROM data WHERE id IN ({})'.format(','.join(['?'] * delete_data.shape[0])),delete_data['ID'].to_list())
                        conn.commit()
                    if not diff_data.empty:
                        cur.execute('DELETE FROM data WHERE id IN ({})'.format(','.join(['?'] * diff_data.shape[0])),diff_data['ID'].to_list())
                        conn.commit()
                        diff_data_flattern=diff_data.drop(columns=['Delete?']).melt(id_vars=['ID', 'type','time']).reset_index().drop(columns=['index'])
                        diff_data_flattern['time']=datetime.now()
                        diff_data_flattern.to_sql(name='data', con=conn, if_exists='append', index=False)
                    if i=='BID_OWNER':
                        diff_data['old_{}'.format(unique_key_col[i])]=diff_data['ID'].map(current_data.set_index('ID')[unique_key_col[i]])
                        changed_TVT_BMT=diff_data.loc[diff_data['old_{}'.format(unique_key_col[i])]!=diff_data[unique_key_col[i]]]
                        for index, row in changed_TVT_BMT.iterrows():
                            rename_folder(folder_path=template_set, old_text=row['old_{}'.format(unique_key_col[i])], new_text=row[unique_key_col[i]], delimiter='_', position=0)
                    cur.close()
                    st.success('Done')
                    st.session_state[f"update_state_{i}_disabled"]=True
                    st.rerun()