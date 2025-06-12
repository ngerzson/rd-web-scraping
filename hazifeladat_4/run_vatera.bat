@echo off
setlocal
cd /d %~dp0

echo [%date% %time%] Vatera Scraper es Export Indul...

:: Aktiválás
call venv\Scripts\activate.bat

:: Scraper + Export
python src\vatera_scraper.py
python src\vatera_product_parser.py
python src\vatera_export.py

echo [%date% %time%] ✅ Vatera Scraper es Export kesz.
pause