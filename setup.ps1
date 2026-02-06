# Quick Setup Script for Agentic Honey-Pot API
# Run this script to set up your development environment

Write-Host "🛡️ Agentic Honey-Pot API - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Docker
Write-Host "`nChecking Docker..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ $dockerVersion" -ForegroundColor Green
} else {
    Write-Host "⚠ Docker not found. You'll need Redis separately." -ForegroundColor Yellow
}

# Create .env if not exists
Write-Host "`nSetting up environment file..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env from template" -ForegroundColor Green
    Write-Host "  ⚠ IMPORTANT: Edit .env with your API keys!" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env already exists" -ForegroundColor Green
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate venv
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host "`nInstalling dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install --upgrade pip -q
pip install -r requirements.txt -q
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ All dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Start Redis (if Docker available)
if ($dockerVersion) {
    Write-Host "`nStarting Redis container..." -ForegroundColor Yellow
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Redis is running" -ForegroundColor Green
    } else {
        Write-Host "⚠ Failed to start Redis. Check Docker." -ForegroundColor Yellow
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env with your API keys:" -ForegroundColor White
Write-Host "   - GOOGLE_API_KEY" -ForegroundColor Gray
Write-Host "   - ANTHROPIC_API_KEY" -ForegroundColor Gray
Write-Host "   - GUVI_CALLBACK_URL" -ForegroundColor Gray
Write-Host "   - GUVI_API_KEY" -ForegroundColor Gray
Write-Host "   - API_KEY (for your API security)`n" -ForegroundColor Gray

Write-Host "2. Run tests:" -ForegroundColor White
Write-Host "   pytest tests/ -v`n" -ForegroundColor Gray

Write-Host "3. Generate mock scam messages:" -ForegroundColor White
Write-Host "   python tests/mock_scammer.py`n" -ForegroundColor Gray

Write-Host "4. Start the API server:" -ForegroundColor White
Write-Host "   python main.py`n" -ForegroundColor Gray

Write-Host "5. Test the API:" -ForegroundColor White
Write-Host "   curl http://localhost:8000/health`n" -ForegroundColor Gray

Write-Host "📖 For full documentation, see README.md" -ForegroundColor Cyan
