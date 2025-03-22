# PowerShell script to run the Pygbag server
Write-Host "Starting Pygbag server on http://localhost:8000..."
python -m pygbag --ume_block 0 --port 8000 . 