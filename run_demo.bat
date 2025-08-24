@echo off
echo =====================================================
echo Career Copilot Agent - Hackathon Demo Mode
echo =====================================================
echo.
echo This will run the Gmail extraction in demo mode without 
echo requiring Google Sheets API setup.
echo.
echo Press any key to start...
pause > nul

python cli.py gmail-to-sheets --sheet-id "1Pf2DhcyiHcRb03ue8LxXemqQe33mArsElXztMG0-2QY" --demo

echo.
echo =====================================================
echo Demo completed! Press any key to exit...
pause > nul
