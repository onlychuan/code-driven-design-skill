@echo off
setlocal
where pwsh >nul 2>nul
if errorlevel 1 goto use_windows_powershell
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
goto finished

:use_windows_powershell
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*

:finished
set "INSTALL_EXIT_CODE=%ERRORLEVEL%"
if not "%~1"=="" goto return_exit_code
echo.
pause

:return_exit_code
exit /b %INSTALL_EXIT_CODE%
