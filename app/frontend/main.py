import time
import logging
from logging.handlers import RotatingFileHandler
import threading
import map_generator
from app import app
from datetime import datetime
from pathlib import Path

# log dir setup
log_dir = Path("/frontend/logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "frontend.log"

def setup_logger():
    logger = logging.getLogger("frontend")
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

frontend_logger = setup_logger()

def run_map_generator():
    """
    run map generation and log its execution
    """
    try:
        start_time = datetime.now()
        frontend_logger.info(f"Generating new map")
        
        map_generator.create_new_map()
        
        end_time = datetime.now()
        duration = end_time - start_time
        frontend_logger.info(f"New map generated successfully. Duration: {duration}")
    except Exception as e:
        frontend_logger.error(f"Map generation failed: {str(e)}")

def get_next_run_date():
    """
    calculate next map generation time based on the current time
    """
    now = datetime.now()
    if now.hour < 6:
        next_run = now.replace(hour=6, minute=0, second=0, microsecond=0)
    elif now.hour < 18:
        next_run = now.replace(hour=18, minute=0, second=0, microsecond=0)
    else:
        next_run = now.replace(hour=6, minute=0, second=0, microsecond=0)
        next_run = next_run.replace(day=now.day + 1)
    return next_run

def schedule_map_generation():
    """
    schedule map generation at 6:00 and 18:00 daily
    """
    while True:
        try:
            now = datetime.now()
            frontend_logger.info(f"Checking time... {now.strftime('%Y-%m-%d %H:%M:%S')}")

            if now.hour in [6, 18] and now.minute in [0, 1, 2]: # generate at 6 and 18 with buffer window
                run_map_generator()
                time.sleep(60*3)  # sleep to avoid multiple runs
                
                next_run = get_next_run_date()
                frontend_logger.info(f"Next map generation scheduled for {next_run.strftime("%Y-%m-%d %H:%M")}")
            time.sleep(10) # check every 10s 
        except Exception as e:
            frontend_logger.error(f"Scheduler encountered error: {str(e)}")

def main():
    """
    main function to run the frontend application and scheduler
    """
    frontend_logger.info("Starting app")
    
    map_generator.create_default_map()
    frontend_logger.info("Default map created")
 
    try:
        frontend_logger.info("Initializing map generation scheduler")
        scheduler_thread = threading.Thread(target=schedule_map_generation, daemon=True)
        scheduler_thread.start()
        frontend_logger.info("Map generation scheduler started successfully")

        next_run = get_next_run_date()
        frontend_logger.info(f"Next map generation scheduled for {next_run.strftime("%Y-%m-%d %H:%M")}")
 
        app.run_server(host="0.0.0.0", port=8050, debug=False)
    except Exception as e:
        frontend_logger.error(f"Error app startup: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        frontend_logger.critical(str(e))
        raise
