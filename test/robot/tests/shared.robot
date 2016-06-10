*** Settings ***
Documentation               The primary resource file for the robot test for the inventory list webapp.
...
...                         The system specific keywords created here form our own
...                         domain specific language. They utilize keywords provided
...                         by the imported Selenium2Library.

Library                     Selenium2Library
Library                     DateTime
Library                     Collections
Library                     RequestsLibrary
Library                     HttpLibrary.HTTP

*** Variables ***
# This variables should be set by arguments to run-tests.py
${SERVER}
${BROWSER}
${REMOTE_URL}
${PROXY}

${DELAY}                    0

${PROXYCAPABILITIES}
${CAPABILITIES}

*** Keywords ***
Open Browser With Proxy2
    [Arguments]  ${URL}

    ${CAPABILITIES}=    Evaluate  {'platform':'${PLATFORM}', 'version':'${BROWSER_VERSION}'}

    Run Keyword Unless  '${PROXY}' == ''  ${PROXYCAPABILITIES}=  Evaluate  {'proxyType':'manual', 'httpProxy':'${PROXY}', 'sslProxy':'${PROXY}'}
    Run Keyword Unless  '${PROXYCAPABILITIES}' == ''  Set To Dictionary  ${CAPABILITIES}  proxy  ${PROXYCAPABILITIES}

    Open Browser  ${URL}  ${BROWSER}  None  ${REMOTE_URL}  ${CAPABILITIES}
    Set Selenium Implicit Wait  5seconds
    Set Window Size  ${1280}  ${1024}

Open Browser With Proxy
    [Arguments]                 ${URL}
    ${desiredcapabilities}=     Evaluate    {'proxy':{'proxyType':'manual','httpProxy':'${PROXY}', 'sslProxy':'${PROXY}'}, 'platform':'${PLATFORM}', 'version':'${BROWSER_VERSION}'}
    Run Keyword If        '${PROXY}' == ''     Open Browser         ${URL}      ${BROWSER}
    Run Keyword Unless    '${PROXY}' == ''     Open Browser         ${URL}      ${BROWSER}    None    ${REMOTE_URL}    ${desiredcapabilities}
    Set Selenium Implicit Wait  10
