
from datetime import datetime
import os


while True:
    if datetime.now().strftime('%H:%M') == "19:32":
        os.system("shutdown -s")