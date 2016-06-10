*** Settings ***
Documentation               Simple Robot Test
Resource                    ./shared.robot
Test Teardown  			        Close Browser

*** Keywords ***
open page
	Open Browser With Proxy                  	https://www.google.de
	Title Should Be    Google

*** Test Cases ***
Test
	open page
