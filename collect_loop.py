import time
import traceback

from collect_data import save_data
from config import COLLECT_EVERY_SECONDS

if __name__ == "__main__":
    while True:
        try:
            print("Collecting latest BTC data...")
            save_data()
        except Exception:
            traceback.print_exc()

        time.sleep(COLLECT_EVERY_SECONDS)
