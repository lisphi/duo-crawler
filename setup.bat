@echo off
REM Quick setup script for duo-crawler using uv on Windows

echo 🚀 Setting up duo-crawler with uv...

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 Installing uv...
    winget install astral-sh.uv
    if %errorlevel% neq 0 (
        echo ❌ Failed to install uv via winget. Please install manually.
        echo Visit: https://docs.astral.sh/uv/getting-started/installation/
        pause
        exit /b 1
    )
)

echo 📥 Installing dependencies...
uv sync
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ⚙️ Setting up configuration...
if not exist .env (
    copy .env.example .env
    echo 📝 Please edit .env file with your Duolingo credentials
)

echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your Duolingo credentials
echo 2. Run: uv run duo-crawler base-info
echo.
echo Available commands:
echo   uv run duo-crawler base-info    # Download base information
echo   uv run pytest                   # Run tests
echo   uv run black .                  # Format code
echo.
pause
