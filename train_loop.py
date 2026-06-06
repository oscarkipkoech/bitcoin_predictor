import time
import traceback

from config import TRAIN_EVERY_SECONDS
from train_model import train

if __name__ == "__main__":
    while True:
        try:
            print("Training model...")
            train()
            print("Training complete.")
        except Exception:
            traceback.print_exc()

        time.sleep(TRAIN_EVERY_SECONDS)
