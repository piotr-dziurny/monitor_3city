import subprocess
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import traceback

log_dir = Path("/scraper/logs")
log_dir.mkdir(exist_ok=True)

# global logger
logger = logging.getLogger("scheduler")
logger.setLevel(logging.INFO)
logger.propagate = False

formatter = logging.Formatter(
    "%(asctime)s [%(name)s] - %(levelname)-8s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# StreamHandler -> docker logs
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def add_file_handler(session_date, formatter):
    """
    adding a file handler for this current scraping session
    """
    log_file = log_dir / f"session_{session_date}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return file_handler


def remove_file_handler(handler):
    logger.removeHandler(handler)
    handler.close()


def run_spider():
    logger.info("Starting spider...")

    try:
        process = subprocess.Popen(
            ["scrapy", "crawl", "ogloszenia"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        logger.info("Spider stdout:")

        if process.stdout is not None:
            for line in process.stdout:
                logger.info(line.rstrip())
        else:
            logger.warning("No stdout from spider process.")

        process.wait()
        logger.info("Spider run completed.")

    except Exception:
        logger.error(f"Error running spider:\n{traceback.format_exc()}")


def run_scraping_session(formatter, is_initial=False):
    start = datetime.now()
    session_date = start.strftime("%Y-%m-%d")
    session_type = "initial" if is_initial else "scheduled"

    file_handler = add_file_handler(session_date, formatter)

    logger.info(f"Starting {session_type} scraping session at: {start}")

    run_spider()

    end = datetime.now()
    duration = end - start

    logger.info(f"{session_type.capitalize()} scraping session completed. Duration: {duration}")

    next_run = end.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=3)
    logger.info(f"Next scheduled run at: {next_run}")

    remove_file_handler(file_handler)

    return next_run 


def main():
    logger.info("Starting scheduler...")

    next_run = run_scraping_session(formatter, is_initial=True)

    while True:
        if datetime.now() >= next_run:
            next_run = run_scraping_session(formatter)
        time.sleep(60*60)


if __name__ == "__main__":
    main()
