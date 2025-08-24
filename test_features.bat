@echo off
echo =====================================================
echo Career Copilot Agent - Feature Test Mode
echo =====================================================
echo.
echo This script will test specific features of the Career Copilot Agent
echo to ensure they are working correctly for the hackathon.
echo.
echo 1. Test Interview Prep
echo 2. Test Gmail Scanner (Demo Mode)
echo 3. Exit
echo.
set /p choice=Enter your choice (1-3): 

if "%choice%"=="1" (
    echo.
    echo Testing Interview Prep Feature...
    python test_interview_prep.py
) else if "%choice%"=="2" (
    echo.
    echo Testing Gmail Scanner in Demo Mode...
    python cli.py gmail-to-sheets --sheet-id "1Pf2DhcyiHcRb03ue8LxXemqQe33mArsElXztMG0-2QY" --demo
) else if "%choice%"=="3" (
    echo Exiting...
    exit /b
) else (
    echo Invalid choice. Please try again.
)

echo.
echo =====================================================
echo Test completed! Press any key to exit...
pause > nul
