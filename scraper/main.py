import time
import logging
from datetime import datetime, timedelta
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from ogloszenia_trojmiasto.spiders.ogloszenia import OgloszeniaSpider
from pathlib import Path
import traceback

# log dir setup
log_dir = Path("/scraper/logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "scraper.log"

# logger config 
def setup_logger():
    logger = logging.getLogger("scheduler")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    
    file_handler = logging.FileHandler(log_file, delay=False)
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    file_handler.flush()
    
    return logger

scheduler_logger = setup_logger()

def run_spider():
    """
    run the spider
    """
    scheduler_logger.info("Starting spider...")
    try:
        process = CrawlerProcess(get_project_settings())
        process.crawl(OgloszeniaSpider)
        process.start()
        scheduler_logger.info("Spider run completed successfully")
    except Exception as e:
        error_info = traceback.format_exc()
        scheduler_logger.error(f"Error during spider startup: {str(e)}\n{error_info}")
  

def run_scraping_session(is_initial=False):
    """
    run scraping session and log its duration
    returns end time for scheduling next run
    """
    session_type = "initial" if is_initial else "scheduled"
    start_time = datetime.now()
    scheduler_logger.info(f"Starting {session_type} scraping session at: {start_time}")
    
    run_spider()
    
    end_time = datetime.now()
    duration = end_time - start_time
    scheduler_logger.info(f"{session_type.capitalize()} scraping session completed. Duration: {duration}")
    
    return end_time

def calculate_next_run(end_time):
    """
    calculate and log the next run time
    returns datetime object for next scheduled run
    """
    next_run = end_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=3)
    scheduler_logger.info(f"Next scheduled run at: {next_run}")

    return next_run

def main():
    """
    main function to run the scheduler
    handles initial run and subsequent scheduled runs
    """
    scheduler_logger.info("Starting scheduler...")
    
    end_time = run_scraping_session(is_initial=True)
    next_run = calculate_next_run(end_time)
    
    while True:
        if datetime.now() >= next_run:
            end_time = run_scraping_session()
            next_run = calculate_next_run(end_time)
        time.sleep(60*60) # check every hour

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        scheduler_logger.critical(f"Critical error in scheduler: {str(e)}")
        raise
