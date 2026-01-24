@echo off
echo ==========================================
echo  Trading Bot Dashboard - Auto Setup
echo ==========================================
echo.

cd /d E:\TradingBot

echo Step 1: Upgrade yfinance...
pip install --upgrade yfinance==0.2.32
if %errorlevel% neq 0 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)
echo ✓ yfinance upgraded successfully

echo.
echo Step 2: Starting Dash Dashboard...
echo Dashboard will run on http://localhost:8050
echo.
python run_dash.py

pause
