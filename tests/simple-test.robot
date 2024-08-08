# wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_120.0.6099.71-1_amd64.deb
# apt install -y /tmp/chrome.deb
# rm /tmp/chrome.deb
# wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip \
# unzip chromedriver-linux64.zip
# cp app/chromedriver-linux64/chromedriver /usr/local/bin/


*** Settings ***
Library  SeleniumLibrary
Library  Process

*** Variables ***
#${URL}             http://10.98.12.25:8503/docxtemplate
${URL}             http://127.0.0.1:8503/docxtemplate
${BROWSER}         headlesschrome

*** Test Cases ***
web run success test
    Log To Console  test1
    ${chrome_options}=  Evaluate  sys.modules['selenium.webdriver'].ChromeOptions()  sys, selenium.webdriver
    Call Method    ${chrome_options}    add_argument    --no-sandbox
    Call Method    ${chrome_options}    add_argument    --headless
    Call Method    ${chrome_options}    add_argument    --remote-debugging-pipe
    Open Browser  ${URL}  browser=${BROWSER}    options=${chrome_options} 
    sleep   10
    Page Should Contain     VARIABLES MANAGEMENT
    Close Browser