@echo off
chcp 65001 >nul
echo 正在抓取最新市场数据...
echo.
python "%~dp0fetch_market_data.py"
echo.
echo 完成后请刷新 dca_calculator.html（浏览器按 F5）
pause
