@echo off
setlocal

:: Időbélyeg kiírása
echo [%date% %time%] Jófogás teljes scraper pipeline indítása...

:: Virtuális környezet aktiválása
call D:\WebScraping\rd-web-scraping\venv\Scripts\activate.bat

:: 1. Jófogás scraper
echo [%date% %time%] 1. Jófogás scraper indul...
python D:\WebScraping\rd-web-scraping\hazifeladat_4\src\jofogas_scraper.py

:: 2. Jófogás termék parser
echo [%date% %time%] 2. Jófogás termék parser indul...
python D:\WebScraping\rd-web-scraping\hazifeladat_4\src\jofogas_product_parser.py

:: 3. Jófogás Excel export
echo [%date% %time%] 3. Jófogás Excel export indul...
python D:\WebScraping\rd-web-scraping\hazifeladat_4\src\jofogas_export.py

:: Befejezés
echo [%date% %time%] ✅ Jófogás scraping és export kész.
pause