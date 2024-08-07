FROM python:3.10.12-slim
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libc6-dev make dpkg-dev git openssh-client\
    && apt-get clean all \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*
ARG git_token
ENV OUTPUT_DIR="/opt/Tender_Document_Generator/output"
ENV DB_DIR="/opt/Tender_Document_Generator/data"
ENV TEMPLATE_DIR="/opt/Tender_Document_Generator/templates"
RUN /usr/bin/git clone --branch update_db https://$git_token@github.com/moophat/Tender_Document_Generator.git /opt/Tender_Document_Generator
WORKDIR /opt/Tender_Document_Generator
RUN pip install --no-cache-dir -r requirements.txt
# Expose the port Streamlit will run on
EXPOSE 8503

# Command to run Streamlit
CMD ["streamlit", "run", "streamlit_mainpage.py","--server.port=8503", "--server.baseUrlPath=/docxtemplate/", "--server.address=0.0.0.0"]
