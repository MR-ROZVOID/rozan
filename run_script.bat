@echo off
echo Installing dependencies using the active Python...

:: استخدام python -m pip يضمن التثبيت في المسار الصحيح الذي سيشغل السكربت
python -m pip install selenium webdriver-manager pyautogui requests opencv-python

echo Dependencies installed. Running Script...
:loop
:: تأكد من كتابة كلمة python قبل اسم السكربت
python arkain_login_fullscreen.py

echo Script finished or crashed. Re-running in 5 seconds...
timeout /t 5
goto loop
