@echo off

REM Copy 'top' directory to 'top_bk2'
xcopy /s /e /i /h /y "top" "top_bk2"

REM Remove all files and directories inside 'top'
del /q /s /f "top\*.*"

REM Copy 'result' directory to 'result_bk2'
xcopy /s /e /i /h /y "result" "result_bk2"

REM Remove all files and directories inside 'result'
del /q /s /f "result\*.*"

REM Copy 'vstlogs_bk2' directory to 'vstlogs'
xcopy /s /e /i /h /y "vstlogs_bk2" "vstlogs"

REM Remove all files and directories inside 'vstlogs'
del /q /s /f "vstlogs\*.*"
