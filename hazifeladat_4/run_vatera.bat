@echo off
echo [%date% %time%] Vatera scraper futtatása...

:: Virtuális környezet aktiválása
call D:\WebScraping\rd-web-scraping\venv\Scripts\activate.bat

:: Scraper futtatása
python D:\WebScraping\rd-web-scraping\hazifeladat_4\src\vatera_scraper.py

:: Excel exportálás
python D:\WebScraping\rd-web-scraping\hazifeladat_4\src\vatera_export.py

:: Készen vagyunk
echo [%date% %time%] ✅ Vatera scraping és export kész.
pause