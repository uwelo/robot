*** Settings ***
Documentation               Simple Robot Test
Resource                    ./shared.robot
Test Teardown  			        Close Browser

*** Keywords ***
open page
	Open Browser With Proxy                  	http://www.mobile.de
	Title Should Be    mobile.de – Gebrauchtwagen und Neuwagen – Deutschlands größter Fahrzeugmarkt

*** Test Cases ***
Test
	open page
