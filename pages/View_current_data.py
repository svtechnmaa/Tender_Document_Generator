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

def change_update_button_state(t):
    st.session_state[f"update_state_{t}_disabled"]=False

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
    input_schema=read_config_yaml(input_schema_file_path)
    conn = sqlite3.connect(db_file_path, check_same_thread=False)
    if st.button(":star2: :orange[**NEW_BID_INFO**]", use_container_width=True):
        init_bid_input_info_form_locked( bid_info_schema = input_schema["BID_INFO"], conn= conn)

    if st.button(":star2: :orange[**NEW_CUSTOMER_INFO**]", use_container_width=True):
        init_customer_input_info_form_locked( customer_info_schema = input_schema["BID_OWNER"], conn= conn)
    
    ##########LISTING CURRENT DATA##########
    all_data=pd.read_sql_query("SELECT * FROM 'data'" , conn)
    all_config_schema=read_config_yaml(os.path.normpath(
                                os.path.join(
                                os.environ['DB_DIR'],
                                "input_data_schema.yaml")
                            ))
    for i in ['SVTECH_INFO','BID_OWNER','BID_INFO']:
        st.header(i if 'SVTECH' in i else i+' LIST')
        save_widget, import_widget = st.columns(2)
        with save_widget:
            save_button=st.popover("Update", disabled=st.session_state.get(f"update_state_{i}_disabled",True))
        with import_widget:
            import_button=st.button("Import data",key=f"button_import_{i}")
        if import_button:
            inititate_import_data_dialog(i,conn)
        # save_button=st.button("UPDATE", key=f"button_{i}",disabled=st.session_state.get(f"update_state_{i}", True))
        current_data=loading_data(conn, i)
        type_column_order=all_config_schema[i]
        if current_data.empty:
            column_order=type_column_order+sorted(list(set(list(current_data)) - set(type_column_order)),reverse=True)
            current_data = pd.DataFrame(columns=column_order)
        else:
            column_order=type_column_order+sorted(list(set(list(current_data)) ^ set(type_column_order)),reverse=True)
        current_data.insert(loc=0, column='Delete?', value=False)
        column_order.insert(0, "Delete?")
        if i!='SVTECH_INFO':
            new_data=st.data_editor(key=f"current_data_{i}",data= current_data,use_container_width = True,disabled=["time"], args=(i,),on_change=change_update_button_state, hide_index=True, column_order=column_order, column_config={'ID':None,'type':None,'time':None})
        else:
            new_data=st.data_editor(key=f"current_data_{i}",data= current_data,use_container_width = True,disabled=["time"], args=(i,),on_change=change_update_button_state, hide_index=True, column_order=column_order, column_config={'ID':None,'type':None,'time':None,'Delete?':None})
        # if save_button:
        with save_button:
            cur = conn.cursor()
            list_delete_id=new_data.loc[new_data['Delete?']==True]['ID'].to_list()
            diff_data=(current_data.merge(new_data.loc[new_data['Delete?']==False], how='outer', indicator=True).query("_merge == 'right_only'")[current_data.columns])
            list_diff_id=diff_data['ID'].to_list()
            unique_key_col='E_TBMT' if i=="BID_INFO" else 'Ten_viet_tat_BMT'
            if len(list_diff_id)>0 and len(list_delete_id)>0:
                st.subheader("Are you ABSOLUTELY SURE you want to this {} delete {} and update {}".format(i,', '.join(new_data.loc[new_data['ID'].isin(list_delete_id)][unique_key_col].to_list()),', '.join(new_data.loc[new_data['ID'].isin(list_diff_id)][unique_key_col].to_list())))
            elif len(list_delete_id)>0:
                st.subheader("Are you ABSOLUTELY SURE you want to this {} delete {}".format(i,', '.join(new_data.loc[new_data['ID'].isin(list_delete_id)][unique_key_col].to_list())))
            elif len(list_diff_id)>0:
                st.subheader("Are you ABSOLUTELY SURE you want to this {} update {}".format(i,', '.join(new_data.loc[new_data['ID'].isin(list_diff_id)][unique_key_col].to_list())))
            if st.button("CONFIRM", key=f"button_{i}"):
                if i!='SVTECH_INFO':
                    duplicated_in_data=new_data.duplicated(subset=[unique_key_col])
                    if duplicated_in_data.any():
                        st.error("Duplicated {} value {} in data".format(i,', '.join(new_data.loc[~duplicated_in_data][unique_key_col].to_list())))
                        continue
                if len(list_delete_id)>0:
                    cur.execute('DELETE FROM data WHERE id IN ({})'.format(','.join(['?'] * len(list_delete_id))),list_delete_id)
                    conn.commit()
                if len(list_diff_id)>0:
                    cur.execute('DELETE FROM data WHERE id IN ({})'.format(','.join(['?'] * len(list_diff_id))),list_diff_id)
                    conn.commit()
                    diff_data=diff_data.drop(columns=['Delete?']).melt(id_vars=['ID', 'type','time']).reset_index().drop(columns=['index'])
                    diff_data['time']=datetime.now()
                    diff_data.to_sql(name='data', con=conn, if_exists='append', index=False)
                cur.close()
                st.success('Done')
                st.session_state[f"update_state_{i}_disabled"]=True
                st.rerun()