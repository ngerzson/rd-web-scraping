@echo off
setlocal
cd /d %~dp0

echo [%date% %time%] Jófogás teljes futás indul...

:: Aktiválás
call venv\Scripts\activate.bat

:: Scraper → Parser → Excel export
python src\jofogas_scraper.py
python src\jofogas_product_parser.py
python src\jofogas_export.py

echo [%date% %time%] ✅ Jófogás futás kész.
pause
