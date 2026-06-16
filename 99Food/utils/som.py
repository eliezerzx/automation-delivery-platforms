import winsound
import time
def som_erro():
    for _ in range(3):
        winsound.Beep(1000, 300)  # frequência, duração(ms)
        time.sleep(0.1)

def som_sucesso():
    winsound.Beep(600, 300)
    time.sleep(0.1)
    winsound.Beep(800, 300)
    time.sleep(0.1)
    winsound.Beep(1000, 400)
