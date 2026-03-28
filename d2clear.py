import schedule
import time
from actions.clear_inventory import clear_inventory

if __name__ == "__main__":
    schedule.every().hour.at("00:00").do(clear_inventory)
    print("Scheduler started. Will clear inventory at the top of every hour.")

    while True:
        schedule.run_pending()
        time.sleep(1)
