import streamlit as st
import sys
import os
import logging
from utils import *
import time 
import yaml
from datetime import datetime

## EXPLAIN: setting shell_output = False will create a default log Streamhandler, which by default send all   all Python log to stderr
## then we send all console stdout to TerminalOutput tab
## all stderr data (which include formatted log) to the LogData tab

LOGGER_INIT(log_level=logging.DEBUG,
                      print_log_init = False,
                      shell_output= False) 

def change_update_button_state(t):
    st.session_state[f"update_state_{t}"]=False

######################## Logging TAB ##########################################
with st.sidebar:
    TerminalOutput, LoggingOutput= init_logging_popup_button()     

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

    if st.button(":star2: :orange[**NEW_BID_INFO**]", use_container_width=True):
        init_bid_input_info_form_locked( bid_info_schema = input_schema["BID_INFO"],database_path= db_file_path)

    if st.button(":star2: :orange[**NEW_CUSTOMER_INFO**]", use_container_width=True):
        init_customer_input_info_form_locked( customer_info_schema = input_schema["BID_OWNER"],database_path= db_file_path)
    
    ##########LISTING CURRENT DATA##########
    conn = sqlite3.connect(db_file_path)
    all_data=pd.read_sql_query("SELECT * FROM 'data'" , conn)
    for i in ['SVTECH_INFO','BID_OWNER','BID_INFO']:
        st.header(i if 'SVTECH' in i else i+' LIST')
        save_button=st.button("UPDATE", key=f"button_{i}",disabled=st.session_state.get(f"update_state_{i}", True))
        # current_data=all_data.loc[all_data['type']==i].pivot(values='value', index=['ID', 'type','time'], columns='key').reset_index()
        current_data=loading_data(conn, i)
        current_data.insert(loc=0, column='Delete?', value=False)
        new_data=st.data_editor(key=f"current_data_{i}",data=   current_data,use_container_width = True,disabled=["time"], args=(i,),on_change=change_update_button_state, hide_index=True, column_config={'ID':None,'type':None,'time':None})
        if save_button:
            cur = conn.cursor()
            list_delete_id=new_data.loc[new_data['Delete?']==True]['ID'].to_list()
            if len(list_delete_id)>0:
                cur.execute('DELETE FROM data WHERE id IN ({})'.format(','.join(['?'] * len(list_delete_id))),list_delete_id)
                conn.commit()
            diff_data=(current_data.merge(new_data.loc[new_data['Delete?']==False], how='outer', indicator=True).query("_merge == 'right_only'")[current_data.columns])
            list_diff_id=diff_data['ID'].to_list()
            if len(list_diff_id)>0:
                cur.execute('DELETE FROM data WHERE id IN ({})'.format(','.join(['?'] * len(list_diff_id))),list_diff_id)
                conn.commit()
                diff_data=diff_data.drop(columns=['Delete?']).melt(id_vars=['ID', 'type','time']).reset_index().drop(columns=['index'])
                diff_data['time']=datetime.now()
                diff_data.to_sql(name='data', con=conn, if_exists='append', index=False)
            cur.close()
            st.success('Done')
            st.rerun()
    conn.close()