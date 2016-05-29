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

*** Variables ***
${SERVER}                   SHOULD BE DEFINED PER COMMAND LINE PARAMETER
${BROWSER}                  SHOULD BE DEFINED PER COMMAND LINE PARAMETER
${REMOTE_URL}               SHOULD BE DEFINED PER COMMAND LINE PARAMETER
${PROXY}                    SHOULD BE DEFINED PER COMMAND LINE PARAMETER
&{PROXIES}                  http=${PROXY}
${DELAY}                    0

*** Keywords ***
Open Browser With Proxy
    [Arguments]  ${URL}

    ${capabilities}=        Evaluate    {'proxy':{'proxyType':'manual', 'httpProxy':'${PROXY}', 'sslProxy':'${PROXY}'}, 'platform':'${PLATFORM}', 'version':'${BROWSER_VERSION}'}
                            Run Keyword If        '${PROXY}' == ''     Open Browser         ${URL}      ${BROWSER}
                            Run Keyword Unless    '${PROXY}' == ''     Open Browser         ${URL}      ${BROWSER}    None    ${REMOTE_URL}    ${capabilities}
                            Set Selenium Implicit Wait  5seconds
                            Set Window Size  ${1280}  ${1024}
