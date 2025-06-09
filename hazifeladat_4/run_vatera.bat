@echo off
setlocal
cd /d %~dp0

echo [%date% %time%] Vatera scraper és export indul...

:: Aktiválás
call venv\Scripts\activate.bat

:: Scraper + Export
python src\vatera_scraper.py
python src\vatera_export.py

:: Jófogás export is, ha kéred a végén
python src\jofogas_export.py

echo [%date% %time%] ✅ Vatera + Jófogás export kész.
pause
