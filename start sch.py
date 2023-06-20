
from datetime import datetime
import os
from time import sleep


while True:
    if datetime.now().strftime('%H:%M') == "06:30":
        import main
        import main_reg
    else:
        print('wait')
        sleep(1)
        os.system('cls')
        print('wait.')
        sleep(1)
        os.system('cls')
        print('wait..')
        sleep(1)
        os.system('cls')
        print('wait...')
        sleep(1)
        os.system('cls')
        continue