*** Settings ***
Documentation               Simple Robot Test
Resource                    ./shared.robot
Test Teardown  			        Close Browser

*** Keywords ***
open page with title
	[Arguments]   ${URL} ${TITLE}
	Open Browser With Proxy                  	${URL}
  Wait Until Page Contains Element 			    title
	${VAR}=  Get Text 							          title
	Should Contain   ${VAR}  ${TITLE}

*** Test Cases ***
open page with title    http://google.de  Google
