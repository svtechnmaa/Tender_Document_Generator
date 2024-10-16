FROM python:3.10.12-slim

LABEL org.opencontainers.image.source=https://github.com/svtechnmaa/Tender_Document_Generator

# Update and install necessary packages
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libc6-dev make dpkg-dev git openssh-client libreoffice-common libreoffice-core libreoffice-writer \
    && apt-get clean all \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

# Set environment variables
ARG git_token
ARG CACHEBUST=1  # This argument will help to bust the cache for the git clone step
ARG BRANCH="main"
ARG OWNER="svtechnmaa"

ENV OUTPUT_DIR="/opt/Tender_Document_Generator/output"
ENV DB_DIR="/opt/Tender_Document_Generator/data"
ENV TEMPLATE_SET_DIR="/opt/Tender_Document_Generator/templates_set"
ENV TEMPLATE_INVENTORY_DIR="/opt/Tender_Document_Generator/templates_inventory"

# Clone the repository
RUN /usr/bin/git clone --branch $BRANCH https://$git_token@github.com/$OWNER/Tender_Document_Generator.git /opt/Tender_Document_Generator

# Set the working directory
WORKDIR /opt/Tender_Document_Generator
RUN mkdir /opt/Tender_Document_Generator/templates_set \
 && mkdir /opt/Tender_Document_Generator/templates_inventory
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Streamlit will run on
EXPOSE 8503

# Command to run Streamlit
CMD ["streamlit", "run", "streamlit_mainpage.py", "--server.port=8503", "--server.baseUrlPath=/docxtemplate/", "--server.address=0.0.0.0"]

# docker build --build-arg git_token=your_git_token --build-arg CACHEBUST=$(date +%s) --build-arg BRANCH=main --build-arg OWNER=vutuong -t your_image_name .

# or

# docker build --build-arg git_token=your_git_token --build-arg BRANCH=main --no-cache -t your_image_name .
