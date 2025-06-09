@echo off
setlocal

REM ───── Aktiváljuk a virtuális környezetet ─────
call "%~dp0venv\Scripts\activate.bat"

REM ───── Kiírjuk az aktuális dátumot ─────
echo -----------------------------------------
echo 🕒  Futtatás dátuma: %DATE%
echo -----------------------------------------

REM ───── 1. Gyűjtőoldalak feldolgozása ─────
echo 📥 Elindult: jofogas_scraper.py
python "%~dp0src\jofogas_scraper.py"
if errorlevel 1 (
    echo ❌ Hiba a scraper futása közben.
    pause
    exit /b 1
)

REM ───── 2. Termékoldalak feldolgozása ─────
echo 🛠️ Elindult: jofogas_product_parser.py
python "%~dp0src\jofogas_product_parser.py"
if errorlevel 1 (
    echo ❌ Hiba a parser futása közben.
    pause
    exit /b 1
)

REM ───── Vége ─────
echo -----------------------------------------
echo ✅ Minden feldolgozás sikeresen befejeződött!
echo -----------------------------------------
pause
exit /b 0