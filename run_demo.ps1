Write-Host "====================================================="
Write-Host "Career Copilot Agent - Hackathon Demo Mode" -ForegroundColor Cyan
Write-Host "====================================================="
Write-Host ""
Write-Host "This will run the Gmail extraction in demo mode without"
Write-Host "requiring Google Sheets API setup."
Write-Host ""
Write-Host "Press any key to start..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "`n🚀 Starting demo mode..." -ForegroundColor Green
python .\cli.py gmail-to-sheets --sheet-id "1Pf2DhcyiHcRb03ue8LxXemqQe33mArsElXztMG0-2QY" --demo

Write-Host ""
Write-Host "====================================================="
Write-Host "Demo completed! Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
