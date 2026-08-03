import sys
print("Python:", sys.executable)

try:
    import pyscreeze
    print("pyscreeze OK:", pyscreeze.__file__)
except Exception as e:
    print("pyscreeze ERRO:", e)

try:
    import pyautogui
    print("pyautogui OK")
    loc = pyautogui.locateOnScreen('test.png')
except Exception as e:
    print("locateOnScreen ERRO:", e)

try:
    import PIL
    print("Pillow OK:", PIL.__version__)
except Exception as e:
    print("Pillow ERRO:", e)

try:
    import cv2
    print("opencv OK:", cv2.__version__)
except Exception as e:
    print("opencv ERRO:", e)
