import time

try:
    import pyautogui
except ImportError:
    raise SystemExit("ثبّت المكتبة أولاً:  python -m pip install pyautogui")

print("تحريك الماوس سيعرض الإحداثيات. للإيقاف اضغط Ctrl + C\n")

try:
    while True:
        x, y = pyautogui.position()
        # \r يرجّع المؤشر لبداية السطر لتحديث نفس السطر بدون أسطر جديدة
        print(f"\rX: {x:4d}  Y: {y:4d}", end="", flush=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nتم الإيقاف.")
