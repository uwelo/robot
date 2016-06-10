@echo off

rem Version of the selenium jar file
set SELENIUM_VERSION=2.53.0
set SELENIUM_HOME=C:\seleniumGrid
set PATH=%PATH%;%SELENIUM_HOME%\IEDriver

rem wait for the network to come up
timeout /t 20
echo java -version
echo %cd%

rem Start the grid node
rem java -jar %SELENIUM_HOME%\Selenium\selenium-server-standalone-%SELENIUM_VERSION%.jar -role node -nodeConfig %SELENIUM_HOME%\config\ie11.json
java -jar %SELENIUM_HOME%\Selenium\selenium-server-standalone-%SELENIUM_VERSION%.jar -role node -nodeConfig %SELENIUM_HOME%\config\ie11.json
