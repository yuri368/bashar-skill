@echo off
setlocal
cd /d "%~dp0"
echo Publishing Bashar skill to GitHub...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\publish_to_github.ps1"
set "EXIT_CODE=%ERRORLEVEL%"
echo.
if "%EXIT_CODE%"=="0" (
  echo Publish finished successfully.
) else (
  echo Publish failed with exit code %EXIT_CODE%.
)
echo.
pause
exit /b %EXIT_CODE%
