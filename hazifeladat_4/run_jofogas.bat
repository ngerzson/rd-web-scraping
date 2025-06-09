@echo off
REM Aktiváljuk a virtuális környezetet
call .\venv\Scripts\activate.bat

REM Lekérjük a mai dátumot a konzolhoz
echo -------------------------------
echo 🗓️  Futtatás dátuma: %DATE%
echo -------------------------------

REM 1. scraper lefut (gyűjtőoldalak)
echo 🔄 Gyűjtő oldalak feldolgozása...
python .\src\jofogas_scraper.py
if errorlevel 1 (
    echo ❌ Hiba a scraper futása közben. Kilépés.
    pause
    exit /b 1
)

REM 2. parser indul (termékoldalak)
echo 🔍 Termék oldalak feldolgozása...
python .\src\jofogas_product_parser.py
if errorlevel 1 (
    echo ❌ Hiba a parser futása közben. Kilépés.
    pause
    exit /b 1
)

echo --------------------------------
echo ✅ Feldolgozás befejezve!
pause