@echo off
echo Installing dependencies...
pip install selenium webdriver-manager pyautogui requests opencv-python

echo Dependencies installed. Running Script...
:loop
python arkain_login_fullscreen.py
echo Script finished or crashed.
pause
