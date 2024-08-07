import os
import sys 
import yaml
import logging

from streamlit.runtime.scriptrunner.script_run_context  import SCRIPT_RUN_CONTEXT_ATTR_NAME
import streamlit as st
from threading import current_thread
from contextlib import contextmanager
from io import StringIO


import locale
import logging
import os
import re
import sys
import time
import pickle
import pandas as pd
import json
import sqlite3
from datetime import datetime

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


# ## Read VAR_PATH from env 
# if "STREAMLIT_CONFIG" in os.environ:
#   file_path= os.environ['STREAMLIT_CONFIG']
# else:
#   file_path = "./default_variable.yml"
# print(f"STREAMLIT_CONFIG IS {file_path}")
# config=read_config_yaml(file_path)


def CREATE_EXPORT_DIR ( directory = "./" ) :
    """CREATE DIR"""
    if not os.path.exists ( directory ) :
        os.makedirs ( directory )
        logging.debug ( 'Created new directory: ' + directory )
    else :
        logging.debug ( 'Directory already existed ' + directory )
    return directory


def WALKDIR ( root = '.' ,
              verbose = False ) :
    if not os.path.exists ( root ) :
        logging.error ( '!!    Provided root import path do not exist - exiting !!' )
        return None
    else :
        DIR = [ ]
        for root , dirs , files in os.walk ( root , topdown = True ) :
            for name in files :
                fullName = os.path.join ( root , name )
                (parentDir , relativeDir) = os.path.split ( root )
                
                if verbose == True :
                    full_dir = os.path.join ( parentDir , relativeDir )
                    logging.info ( "Reading files from " + full_dir )
                
                DIR.append ( { 'fileName' : name , 'relativeDir' : relativeDir , 'parentDir' : parentDir } )
        return DIR


def PRINT_W_TIME ( message = "" ,
                   timestamp = time.strftime ( '%x' ) + "  " + time.strftime ( '%X' ) ) :
    #timestamp = "avoiding error, break-fix"
    for lines in message.splitlines ( ) :
        print ("{}\t{}".format(timestamp,message))


def TIME_INIT ( ) :
    # =====================Checking datetime & locale variable==================#
    current_time = dict ( )
    logging.debug ( 'initiating time parameter' )
    # Check and set locale
    if locale.getlocale ( ) == (None , None) :  #
        locale.setlocale ( locale.LC_ALL , '' )  #

    # Check datetime and save variable
    # Check datetime and save variable
    logging.info ( '==================================================================' )
    current_time [ 'Full_Date' ] = time.strftime ( '%x' )
    logging.debug ( 'Current date is ' + current_time [ 'Full_Date' ] )

    current_time [ 'Full_Time' ] = time.strftime ( '%X' )
    logging.debug ( 'Current time is ' + current_time [ 'Full_Time' ] )

    current_time [ 'Day' ] = time.strftime ( '%d' )
    logging.debug ( 'Current day is ' + current_time [ 'Day' ] )

    current_time [ 'Month' ] = time.strftime ( '%B' )
    logging.debug ( 'Current month is ' + current_time [ 'Month' ] )

    current_time [ 'MonthNum' ] = time.strftime ( '%m' )
    logging.debug ( 'Current month is ' + current_time [ 'MonthNum' ] )

    current_time [ 'Year' ] = time.strftime ( '%Y' )
    logging.debug ( 'Current year is ' + current_time [ 'Year' ] )

    current_time [ 'Hour' ] = time.strftime ( '%H' )
    logging.debug ( 'Current hour is ' + current_time [ 'Day' ] )

    current_time [ 'Min' ] = time.strftime ( '%M' )
    logging.debug ( 'Current minutes is ' + current_time [ 'Month' ] )

    current_time [ 'Sec' ] = time.strftime ( '%S' )
    logging.debug ( 'Current sec is ' + current_time [ 'Year' ] )

    return current_time


class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super(OneLineExceptionFormatter, self).formatException(exc_info)
        return repr(result) # or format into one line however you want to

    def format(self, record):
        s = super(OneLineExceptionFormatter, self).format(record)
        if record.exc_text:
            s = s.replace('\n', '') + '|'
        return s

def LOGGER_INIT ( log_level = logging.INFO ,
                  log_file = 'unconfigured_log.log' ,
                  file_size = 2 * 1024 * 1024 ,
                  file_count = 2 ,
                  shell_output = False ,
                  log_file_mode = 'a' ,
                  log_format = '%(asctime)s %(levelname)s %(funcName)s(%(lineno)d)     %(message)s',
                  print_log_init = False) :
    try :
        main_logger = logging.getLogger ( )
        main_logger.setLevel ( log_level )
        # add a format handler
        log_formatter = OneLineExceptionFormatter ( log_format )

    except Exception as e :
        PRINT_W_TIME ( "Exception  when format logger cause by:    {}".format( e ) )
        logging.error ( "Exception  when format logger cause by:    {}".format( e ) )
    
    log_dir = os.path.dirname( os.path.abspath(log_file) ) 
    if print_log_init == True: PRINT_W_TIME("Creating log directory ()".format(log_dir))
    

    try :
        main_logger.handlers = [] #init blank handler first otherwise the stupid thing will create a few and print to console
        main_logger.propagate = False #Only need this if basicConfig is used

        # add a rotating handler
        from logging.handlers import RotatingFileHandler
        log_rorate_handler = RotatingFileHandler ( log_file , 
                                                   mode = log_file_mode , 
                                                   maxBytes = file_size , 
                                                   backupCount = file_count ,
                                                   encoding = None , 
                                                   delay = 0 )
        log_rorate_handler.setFormatter ( log_formatter )
        log_rorate_handler.setLevel ( log_level )
        #add the rotation handler only
        main_logger.addHandler ( log_rorate_handler )

    except Exception as e :
        PRINT_W_TIME ( "Exception when creating main logger handler cause by:    {}".format( e ) )
        logging.error ( "Exception when creating main logger handler cause by:    {}".format( e ) )

    try :
        CREATE_EXPORT_DIR ( log_dir ) # Only do this after the 2 above step, otherwise fcking main_logger will spam debug log to stdout
        if shell_output == True :
            stream_log_handler = logging.StreamHandler ( stream = sys.stdout )
        else:
            #by default StreamHandler already set stream = stderr, but somehome if leave alone it will cause streamlit error 
            stream_log_handler = logging.StreamHandler ( )
            
        stream_log_handler.setFormatter ( log_formatter )
        stream_log_handler.setLevel ( log_level )
        #add the stdout handler properly
        main_logger.addHandler ( stream_log_handler )

    except Exception as e :
        PRINT_W_TIME ( "Exception when creating log directory and setup log stdout handler cause by:    {}".format( e ) )
        logging.error ( "Exception when creating log directory and setup log stdout handler cause by:    {}".format ( e ) )

    if print_log_init == True: PRINT_W_TIME("Done, logging level {} to {} ".format(log_level , os.path.abspath(log_file)) )



@contextmanager
def st_redirect(src_data_stream,
                display_type, 
                display_container,
                src_name,
                cache_data):
    '''
    src_data_stream: the data to be displayed on streamlit container, we will sepcify either sys.stdout or sys.stderr obj here
    display_type: the streamlit component type to store the src data (text box, code, header whatever)
    display_container: the streamlit larger container to help navigate to the container that store the src data (tab,sidebar..etc..)
    src_name: name of "src", to store as key in streamlit session_state (since in Python there's no clean way to access a variable name by itself)
    '''
    
    if all(v is not None for v in [src_data_stream, display_type, display_container, src_name, cache_data]):
      pass
    placeholder = display_container.empty()
    output_func = getattr(placeholder, display_type)
    

    #we will use the source data stream's name as key to store the stream data in streamlit cache, in case we want to save this log or console output somewhere else
    #initiation will be done regardless of whether cache is True or False to avoid complicatiton
    if "{}".format(src_name) not in st.session_state:
      st.session_state["{}".format(src_name)] = ""
    
    with StringIO() as buffer:
        old_write = src_data_stream.write

        def new_write(b):
            if getattr(current_thread(), SCRIPT_RUN_CONTEXT_ATTR_NAME, None):
                

                #the data must be written to session state first, BEFORE the buffer.getvalue to output_func, otherwise stringIO stream can possibly be closed already, causing error when saving data from stringIO to session state
                #this way session_state is ALWAYS updated with lastest console/log data
                if cache_data is True:
                  st.session_state["{}".format(src_name)] += '{}\r'.format(b)
                
                buffer.write('{}\r'.format(b))
                output_func(buffer.getvalue() + '')
            else:
                old_write(b)
        try:
            src_data_stream.write = new_write
            yield
        finally:
            src_data_stream.write = old_write

            #this is an alternative, this way we can avoid racing issue mentioned in new_write
            #but the call to st_redirect must END before session_state data is updated with new log, so we can only access lastest console/log data from session_state at the END of the main script
            #st.session_state["{}".format(src_name)] += buffer.getvalue()

@contextmanager
def st_stdout(display_type,
              display_container,
              cache_data = False):
  
    with st_redirect(src_data_stream = sys.stdout, 
                     display_type = display_type,
                     display_container = display_container,
                     src_name = "sys.stdout",
                     cache_data = cache_data):
        yield

@contextmanager
def st_stderr(display_type,
              display_container,
              cache_data = False):
  
    with st_redirect(src_data_stream = sys.stderr, 
                     display_type = display_type,
                     display_container = display_container,
                     src_name = "sys.stderr",
                     cache_data = cache_data):
        yield

## read file yaml config
def read_config_yaml(file_path):
    with open(file_path, 'r') as yaml_file:
        config_data = yaml.safe_load(yaml_file)
        return config_data

def generate_single_input_dict(usable_input_option = ''):
    input_dict={} 
    for item in usable_input_option:
        input_dict[item] = st.text_input(':orange[Your %s:]'%item, placeholder = 'Please input {}'.format(item))

    return input_dict

def init_logging_popup_button():
    #a simple function to inititate the popup element that will contain the code/text block that hold the log output
    
    terminalColumn, loggingColumn= st.columns([1,1])
    
    with terminalColumn:
        TerminalOutput = st.popover(":blue[messages]", use_container_width=True)
    with loggingColumn:
        LoggingOutput = st.popover(":blue[debugLog]", use_container_width=True)

    with TerminalOutput:
    ##EXPLAIN: you dont have to do anything here, passing this object name to my st_stdout/st_stderr function will let the system know to write stdout/stderr output to it
        st.subheader("Python printing operation (STDOUT) will be displayed on this tab")

    with LoggingOutput:
        ##EXPLAIN: you dont have to do anything here, passing this object name to my st_stdout/st_stderr function will let the system know to write stdout/stderr output to it
        st.subheader("Python Logging operation (STDERR) will be displayed on this tab")


    return TerminalOutput,LoggingOutput


def extract_tar(data, output_dir):
    import tarfile
    from io import BytesIO
    with tarfile.open(fileobj=BytesIO(data), mode='r') as tar:
        tar.extractall(output_dir)

def extract_tar_gz(data, output_dir):
    import tarfile
    from io import BytesIO
    with tarfile.open(fileobj=BytesIO(data), mode='r:gz') as tar_gz:
        tar_gz.extractall(output_dir)

def extract_zip(data, output_dir):
    import zipfile
    from io import BytesIO
    with zipfile.ZipFile(BytesIO(data), 'r') as zip_file:
        zip_file.extractall(output_dir)

def extract_rar(data, output_dir):
    import rarfile
    from io import BytesIO
    with rarfile.RarFile(BytesIO(data), 'r') as rar:
        rar.extractall(output_dir)

def compress_folder(folder_path):
    import io
    import zipfile
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Walk through the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Add file to the zip file
                zip_file.write(file_path, os.path.relpath(file_path, folder_path))
    zip_file.close()
    zip_buffer.seek(0)  # Move to the beginning of the buffer
    return zip_buffer

def download_file_button(object_to_download, download_filename, button_text, pickle_it=False):
    import base64
    import uuid
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')
    """
    st.write()
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None
    else:
        if isinstance(object_to_download, bytes):
            pass
        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False)
        else:
            object_to_download = json.dumps(object_to_download)
    try:
        b64 = base64.b64encode(object_to_download.encode()).decode()
    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()
    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                width: 100%;
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: 0.41em 0.38em;
                position: relative;
                text-decoration: none;
                border-radius: 6px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(49, 51, 63, 0.2);
                border-image: initial;
                white-space: normal;
                display: inline-block; /* Make the <a> element respect width and height properties */
                word-wrap: break-word; /* Break long words onto new lines if needed */
                overflow-wrap: break-word; /* Fallback for older browsers */
                text-align: center;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

    return dl_link

def dir_element_list(folder_path='.', element_type = "all" ):
    
    element_names = []
    directory_element_names = os.listdir(folder_path)
    logging.debug("{}".format( element_type) )
    if element_type.lower() not in ["file", "folder"]:
        raise ValueError("Invalid element type to list, Expected either file or folder")

    for item in directory_element_names:
        if os.path.isdir(os.path.join(folder_path, item)) and element_type.lower() == "folder":
            element_names.append(item)
        elif os.path.isfile(os.path.join(folder_path, item)) and element_type.lower() == "file":
            element_names.append(item)

    return element_names


def folder_selector(folder_path='.'):
    folder_names = dir_element_list (folder_path = folder_path,
                                     element_type="folder")
    selected_filename = st.multiselect('Select folders', folder_names)
    return selected_filename

def file_selector(folder_path='.'):
    file_names = dir_element_list (folder_path = folder_path,
                                     element_type="file")
    selected_filename = st.multiselect('Select files', file_names)
    return selected_filename

def create_default_table(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    listOfTables = cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='data' ''')
    if listOfTables.fetchone()[0]==0:
        table = """ CREATE TABLE data (
                ID INT NOT NULL,
                type VARCHAR(25) NOT NULL,
                key VARCHAR(50) NOT NULL,
                value VARCHAR(65535) NOT NULL,
                time DATETIME
            ); """
        cur.execute(table)
        insert_query="""INSERT INTO data (ID,type,key,value,time) VALUES(?,?,?,?,?)"""
        cur.executemany(insert_query, 
                        [(1,"SVTECH_INFO","Ten_nha_thau","Công ty Cổ phần Phát triển Công nghệ Viễn thông Tin học Sun Việt (SV Technologies JSC)",datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                        (1,"SVTECH_INFO","Dia_chi_nha_thau","Số 2A Phan Thúc Duyện, Phường 4, Quận Tân Bình, TP. Hồ Chí Minh, Việt Nam",datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                        (1,"SVTECH_INFO","Dia_chi_VP_HN","Toà nhà IC, Tầng 6, 82 Duy Tân, Cầu Giấy, Hà Nội",datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                        ])
        conn.commit()
    cur.close()
    conn.close()

def loading_data(conn, type):
    data=pd.read_sql_query("SELECT * FROM 'data' where type=(?)" , conn,params=(type,))
    return data.pivot(values='value', index=['ID', 'type','time'], columns='key').reset_index()

@st.experimental_dialog("NEW_BID_INFO_INPUT_DIAGLOG")
def init_bid_input_info_form_locked(database_path,bid_info_schema = None):

    st.subheader(':orange[**Get info of new Bid and saving it to DB**]')

    if bid_info_schema is None:
        logging.error("No bid info data field fount, exiting")
        sys.exit(1)
    
    ### submission of data cannot be put inside if/else otherwise Streamlit will complain
    with st.form("BidInfo"):
        logging.info("Generating input form for data schema {}".format(bid_info_schema))
        bid_input_data = generate_single_input_dict(bid_info_schema)
        
        submitted = st.form_submit_button(label= "SAVE", type= 'primary')

    if submitted:
        with st.spinner('Saving new Bid data...'):
            st.session_state["bid_info_input_dict"] = bid_input_data

        if not st.session_state.bid_info_input_dict:
            st.error('No new info available')
        else:
            # st.write(st.session_state.bid_info_input_dict) 
            conn = sqlite3.connect(database_path)
            cur = conn.cursor()
            listOfTables = cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='data' ''')
            if listOfTables.fetchone()[0]==1:
                list_E_TBMT=cur.execute('select value from data where key="E_TBMT"').fetchall()
                if st.session_state.bid_info_input_dict['E_TBMT'] in [d[0] for d in list_E_TBMT]:
                    st.error('E_TBMT {} already exist!!!!!'.format(st.session_state.bid_info_input_dict['E_TBMT']))
                    return
                id=cur.execute('''SELECT COALESCE(MAX(ID)+1, 0) FROM data''').fetchone()[0]
            else:
                id=1
            cur.close()
            bid_info=pd.DataFrame(list(st.session_state.bid_info_input_dict.items()), columns=['key', 'value'])
            bid_info['type']='BID_INFO'
            bid_info['time']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            bid_info['ID']=id
            bid_info.to_sql(name='data', con=conn, if_exists='append', index=False)
            conn.close()
            st.success('Done')
            st.rerun()
    ## tu.doan July 2024
    # need to do something here to save to selected datastore of choice, SQLite do not work OK so fuurther code has been removed

@st.experimental_dialog("NEW_CUSTOMER_INFO_INPUT_DIAGLOG")
def init_customer_input_info_form_locked(database_path,customer_info_schema = None ):

    st.subheader(':orange[**Get info of new customer and saving it to DB**]')
    if customer_info_schema is None:
        logging.error("No bid info data field fount, exiting")
        sys.exit(1)
    
    ### submission of data cannot be put inside if/else otherwise Streamlit will complain
    with st.form("CustomerInfo"):
        logging.info("Generating input form for data schema {}".format(customer_info_schema))
        customer_input_data = generate_single_input_dict(customer_info_schema)
        submitted = st.form_submit_button(label= "SAVE", type= 'primary')

    if submitted:
        with st.spinner('Saving new customer data...'):
            time.sleep(1)
            st.session_state["customer_info_input_dict"] = customer_input_data

        if not st.session_state.customer_info_input_dict:
            st.error('No new info available')
        else:
            conn = sqlite3.connect(database_path)
            cur = conn.cursor()
            listOfTables = cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='data' ''')
            if listOfTables.fetchone()[0]==1:
                id=cur.execute('''SELECT COALESCE(MAX(ID)+1, 0) FROM data''').fetchone()[0]
            else:
                id=1
            cur.close()
            bid_info=pd.DataFrame(list(st.session_state.customer_info_input_dict.items()), columns=['key', 'value'])
            bid_info['type']='BID_OWNER'
            bid_info['time']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            bid_info['ID']=id
            bid_info.to_sql(name='data', con=conn, if_exists='append', index=False)
            conn.close()
            st.success('Done')
            st.rerun()
    ## tu.doan July 2024
    # need to do something here to save to selected datastore of choice, SQLite do not work OK so fuurther code has been removed


@st.experimental_dialog("NEW_TEMPLATE_SET_DIALOG")
def inititate_template_dialog(template_directory = "templates",template_name = ""):
    st.subheader(':orange[**Upload new template set**]')
    
    with st.form("CustomerInfo"):

        data_name = st.text_input("Input the name of the template set",
                                  value = template_name)
        uploaded_files_list = st.file_uploader(label = "choose files in the template set",
                                         accept_multiple_files= True)
        
        submitted = st.form_submit_button(label= "SAVE TEMPLATE SET", type= 'primary')

    if submitted:
        with st.spinner('Saving new template set '):
            saving_dir = os.path.normpath(
                            os.path.join(
                                template_directory,
                                data_name)
                             )

            CREATE_EXPORT_DIR(saving_dir)
            for uploaded_file in uploaded_files_list:
                bytes_data = uploaded_file.getvalue()
                with open(os.path.join(os.path.abspath(saving_dir),
                                                        uploaded_file.name)
                            , 'wb') as f: 
                    f.write(bytes_data)
            st.write(os.listdir(saving_dir))
            st.success('Done')
            st.rerun()
    