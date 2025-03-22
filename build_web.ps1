# PowerShell script to build the web version for deployment

# Clean up any previous build
if (Test-Path -Path "build") {
    Write-Host "Removing previous build..."
    Remove-Item -Recurse -Force "build"
}

# Create our icons in multiple sizes
Write-Host "Creating game icons..."
python create_icons.py

# Build the web version
Write-Host "Building web version..."
python -m pygbag --ume_block 0 --build .

# Copy additional files for PWA support
Write-Host "Adding PWA support..."
Copy-Item "web_manifest.json" -Destination "build/web/manifest.json"
Copy-Item "icon-192.png" -Destination "build/web/"
Copy-Item "icon-512.png" -Destination "build/web/"
Copy-Item "service-worker.js" -Destination "build/web/"

# Add PWA meta tags to the index.html
Write-Host "Updating HTML..."
$indexPath = "build/web/index.html"
$content = Get-Content -Path $indexPath -Raw
$metaTags = @"
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#0066cc">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="apple-touch-icon" href="icon-192.png">
"@
$content = $content -replace "<head>", "<head>`n$metaTags"

# Add service worker registration
$serviceWorkerScript = @"
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/service-worker.js')
      .then(function(registration) {
        console.log('Service Worker registered with scope:', registration.scope);
      })
      .catch(function(error) {
        console.error('Service Worker registration failed:', error);
      });
  });
}
</script>
"@
$content = $content -replace "</body>", "$serviceWorkerScript`n</body>"
Set-Content -Path $indexPath -Value $content

Write-Host "Web build completed successfully! Find your files in the build/web directory." 