import streamlit as st
from utils import *
from streamlit_pdf_viewer import pdf_viewer
st.title("Preview File")
file_path = st.query_params.get("file")
if not file_path:
    st.write("Function not available. Please go back to menu Manage Template File or Render Output File and select file to preview")
else:
    if st.query_params.get("type")=='output':
        st.write("Preview output of owner {} with bid {} file {}".format(file_path.split('/')[-3], file_path.split('/')[-2], file_path.split('/')[-1]))
    elif st.query_params.get("type")=='template':
        st.write("Preview template {} file {}".format(file_path.split('/')[-2], file_path.split('/')[-1]))
    if "pdf" not in st.session_state:
        st.session_state.pdf = docx_to_pdf(file_path)
    if "pdf" in st.session_state:
        pdf_viewer(st.session_state.pdf)
    else:
        st.write("Please provide a valid file path.")