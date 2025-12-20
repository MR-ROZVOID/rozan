import os
import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

URL = "https://account.arkain.io/login"

def make_driver(i: int):
    options = Options()

    # بروفايل مؤقت
    profile_dir = os.path.join(tempfile.gettempdir(), f"arkain_profile_{i}")
    options.add_argument(f"--user-data-dir={profile_dir}")

    # خيارات استقرار على ويندوز
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--remote-debugging-port=0")
    options.add_argument("--start-maximized")

    # جرّبها إذا استمر الكراش (تساعد ببعض الأجهزة/الحمايات)
    # options.add_argument("--no-sandbox")

    # Selenium Manager يختار chromedriver المناسب تلقائيًا
    driver = webdriver.Chrome(options=options)
    return driver

drivers = []
for i in range(5):
    try:
        d = make_driver(i)
        d.get(URL)
        drivers.append(d)
        print(f"✅ فتح المتصفح {i+1}/5")
        time.sleep(1)
    except Exception as e:
        print(f"❌ فشل المتصفح {i+1}: {e}")

input("اضغط Enter لإغلاق الكل...")

for d in drivers:
    try:
        d.quit()
    except:
        pass
