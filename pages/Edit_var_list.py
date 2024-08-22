import streamlit as st
import os
from utils import *

def change_update_button_state():
    st.session_state["update_state_variable_disabled"]=False

LOGGER_INIT(log_level=logging.DEBUG,
                      print_log_init = False,
                      shell_output= False) 
with st.sidebar:
    TerminalOutput, LoggingOutput= init_logging_popup_button()
variable_options=[]
with st_stdout("code",TerminalOutput, cache_data=False), st_stderr("code",LoggingOutput, cache_data=True):
    yaml_data_file_path = os.path.normpath(
                                os.path.join(
                                os.environ['DB_DIR'],
                                "input_data_schema.yaml")
                            )
    st.header("VARIABLES MANAGEMENT")
    update_button= st.popover("UPDATE", disabled=st.session_state.get("update_state_variable_disabled",True))
    current_schema=read_config_yaml(yaml_data_file_path)
    current_schema=pd.DataFrame([(key, value) for key, values in current_schema.items() for value in values], 
                  columns=['Type', 'Variable'])
    new_schema=st.data_editor(current_schema, num_rows="dynamic",use_container_width = True, on_change=change_update_button_state)
    with update_button:
        ######diff_data: data deleted from old schema, contain updated data
        delete_data=(current_schema.merge(new_schema.drop_duplicates(), on=['Type','Variable'], 
                how='left', indicator=True)).query("_merge == 'left_only'")['Variable'].to_list()
        new_data=(new_schema.merge(current_schema.drop_duplicates(), on=['Type','Variable'], 
                how='left', indicator=True)).query("_merge == 'left_only'")['Variable'].to_list()
        if len(delete_data)>0 and len(new_data)>0 and delete_data[0]!=None and new_data[0]!=None:
            st.subheader("Are you ABSOLUTELY SURE you want to delete {} and add {} to list variables".format(', '.join(delete_data),', '.join(new_data)))
        elif len(delete_data)>0 and delete_data[0]!=None:
            st.subheader("Are you ABSOLUTELY SURE you want to delete {} from list variables".format(', '.join(delete_data)))
        elif len(new_data)>0 and new_data[0]!=None:
            st.subheader("Are you ABSOLUTELY SURE you want to add {} to list variables".format(', '.join(new_data)))
        if st.button("CONFIRM"):
            invalid_type_list=new_schema[~(new_schema['Type'].isin(['SVTECH_INFO', 'BID_OWNER','BID_INFO']))]['Type'].to_list()
            if len(invalid_type_list)>0:
                st.error("Invalid type {}. Allow only type SVTECH_INFO, BID_OWNER, BID_INFO".format(', '.join(invalid_type_list)))
            else:
                new_schema = new_schema.groupby('Type')['Variable'].apply(list).to_dict()
                write_config_yaml(file_path=yaml_data_file_path,data=new_schema)
                st.session_state['update_state_variable_disabled']=True
                st.rerun()
    # update_button=st.button("UPDATE")
    # current_schema=load_schema_data(yaml_data_file_path)
    # new_schema=st.data_editor(current_schema, num_rows="dynamic",use_container_width = True,)
    # if update_button:
    #     new_schema = new_schema.groupby('Type')['Variable'].apply(list).to_dict()
        # write_schema_data(yaml_data_file_path,new_schema)
        # st.rerun()