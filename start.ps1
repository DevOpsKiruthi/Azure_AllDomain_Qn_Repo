# Azure Assessment Automation - Windows Startup
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Azure Assessment Automation System" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found" -ForegroundColor Red
    Write-Host "Install Python 3.9+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check credentials
if (-not $env:AZURE_OPENAI_ENDPOINT -or -not $env:AZURE_OPENAI_KEY) {
    Write-Host "[WARNING] Azure OpenAI credentials not set" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To enable AI features, run:" -ForegroundColor Yellow
    Write-Host '  $env:AZURE_OPENAI_ENDPOINT = "https://your-instance.openai.azure.com/"' -ForegroundColor Cyan
    Write-Host '  $env:AZURE_OPENAI_KEY = "your-key"' -ForegroundColor Cyan
    Write-Host '  $env:AZURE_OPENAI_DEPLOYMENT = "gpt-4"' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "AI chat will not work, but direct creation will." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Continue? (Y/N): " -NoNewline
    $continue = Read-Host
    if ($continue -ne "Y" -and $continue -ne "y") {
        exit 0
    }
}

Write-Host ""
Write-Host "[1/4] Setting up environment..." -ForegroundColor Yellow

# Create venv
if (-not (Test-Path "venv")) {
    Write-Host "  Creating virtual environment..."
    python -m venv venv
}

# Activate venv
Write-Host "  Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "  Installing dependencies..."
pip install -q -r requirements.txt

Write-Host "[OK] Environment ready" -ForegroundColor Green
Write-Host ""

# Start Backend
Write-Host "[2/4] Starting Backend API..." -ForegroundColor Yellow
$backend = Start-Process python -ArgumentList "api_server.py" -PassThru -WindowStyle Hidden
Write-Host "[OK] Backend started (PID: $($backend.Id))" -ForegroundColor Green
Write-Host ""

# Wait for backend
Write-Host "Waiting for backend..."
$ready = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 1 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Backend is ready" -ForegroundColor Green
            $ready = $true
            break
        }
    } catch { }
    Start-Sleep -Seconds 1
}

if (-not $ready) {
    Write-Host "[ERROR] Backend failed to start" -ForegroundColor Red
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Start Frontend
Write-Host "[3/4] Starting Streamlit Frontend..." -ForegroundColor Yellow
$frontend = Start-Process streamlit -ArgumentList "run streamlit_app.py" -PassThru
Write-Host "[OK] Frontend started (PID: $($frontend.Id))" -ForegroundColor Green
Write-Host ""

Start-Sleep -Seconds 3

# Summary
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "System is ready!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "Frontend UI:  http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Monitor
try {
    while ($true) {
        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host ""
    Write-Host "Shutting down..." -ForegroundColor Yellow
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Services stopped" -ForegroundColor Green
}