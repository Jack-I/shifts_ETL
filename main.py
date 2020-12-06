import logging
from datetime import date, timedelta
from time import sleep
import schedule

from one_day import load_one_day


def job():
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    load_one_day(yesterday)
    logger.info(f"{yesterday} loading finished")


if __name__ == '__main__':
    print('Script execution started')
    logging.basicConfig(filename='s_m.log',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filemode='w',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Schedule a job
    schedule.every().day.at("08:40").do(job)
    # Do the job
    while True:
        schedule.run_pending()
        sleep(60)  # 60 seconds
