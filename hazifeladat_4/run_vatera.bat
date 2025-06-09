@echo off
:: Dátum kiírása
echo [%date% %time%] Vatera scraper futtatása...

:: Virtuális környezet aktiválása
call D:\WebScraping\rd-web-scraping\venv\Scripts\activate.bat

:: Vatera scraper futtatása
python D:\WebScraping\rd-web-scraping\hazifeladat_4\src\vatera_scraper.py

:: Várakozás befejezés előtt (opcionális, ha ikonnal indítod)
pause