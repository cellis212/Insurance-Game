# PowerShell script to run the Pygbag server in the background
Write-Host "Starting Pygbag server on http://localhost:8000..."

# Start the Pygbag server in a new PowerShell window
Start-Process powershell -ArgumentList "-Command python -m pygbag --ume_block 0 --port 8000 ."

# Open the default browser to the game URL after a short delay
Start-Sleep -Seconds 3
Start-Process "http://localhost:8000"

Write-Host "Server running in background. Close the other PowerShell window to stop the server." 