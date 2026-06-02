import os
import sys
import time
import datetime
import threading
import subprocess
import config

def run_database_update():
    """
    Executes the ingestion and indexing scripts to refresh the database.
    Runs them as separate subprocesses to prevent thread-safety or duplicate import issues.
    """
    print(f"[{datetime.datetime.now()}] Starting scheduled database update...")
    
    # Locate Python interpreter (insulates virtual environment)
    python_bin = sys.executable
    
    # 1. Run Ingestion Script
    ingest_script = os.path.join("src", "ingest.py")
    if os.path.exists(ingest_script):
        try:
            print(f"[{datetime.datetime.now()}] Running ingestion scraper: {ingest_script}")
            subprocess.run([python_bin, ingest_script], check=True, capture_output=True, text=True)
            print(f"[{datetime.datetime.now()}] Ingestion completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[{datetime.datetime.now()}] ERROR: Ingestion failed with exit code {e.returncode}.")
            print(f"Error details:\n{e.stderr}")
            return False
    else:
        print(f"[{datetime.datetime.now()}] ERROR: Ingestion script not found at {ingest_script}")
        return False

    # 2. Run Index Builder Script
    builder_script = os.path.join("src", "index_builder.py")
    if os.path.exists(builder_script):
        try:
            print(f"[{datetime.datetime.now()}] Running vector index builder: {builder_script}")
            subprocess.run([python_bin, builder_script], check=True, capture_output=True, text=True)
            print(f"[{datetime.datetime.now()}] Vector index rebuilding completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[{datetime.datetime.now()}] ERROR: Vector rebuilding failed with exit code {e.returncode}.")
            print(f"Error details:\n{e.stderr}")
            return False
    else:
        print(f"[{datetime.datetime.now()}] ERROR: Index builder script not found at {builder_script}")
        return False

    print(f"[{datetime.datetime.now()}] Database update successfully finished.")
    return True

def scheduler_thread_loop():
    """
    Continuous loop running in a background daemon thread.
    Calculates sleep time until configured time daily and executes updates.
    """
    target_hour = config.SCHEDULER_HOUR
    target_minute = config.SCHEDULER_MINUTE
    
    print(f"[{datetime.datetime.now()}] Database Scheduler Thread Initialized. Daily run target: {target_hour:02d}:{target_minute:02d} AM.")
    
    while True:
        now = datetime.datetime.now()
        
        # Calculate target time today
        target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        # If target time is in the past today, set for tomorrow
        if now >= target:
            target += datetime.timedelta(days=1)
            
        sleep_seconds = (target - now).total_seconds()
        print(f"[{datetime.datetime.now()}] Next database update scheduled at {target}. Sleeping for {sleep_seconds:.1f} seconds...")
        
        # Sleep until target time
        try:
            time.sleep(sleep_seconds)
        except Exception as e:
            print(f"[{datetime.datetime.now()}] Scheduler sleep interrupted: {e}")
            break
            
        # Execute the update when waking up at 09:25 AM
        print(f"[{datetime.datetime.now()}] Scheduler triggered!")
        run_database_update()

def start_scheduler():
    """
    Starts the scheduler loop in a non-blocking background daemon thread.
    """
    scheduler_thread = threading.Thread(target=scheduler_thread_loop, name="DBSchedulerThread")
    scheduler_thread.daemon = True
    scheduler_thread.start()
    print(f"[{datetime.datetime.now()}] Database scheduler thread started successfully.")
    return scheduler_thread

if __name__ == "__main__":
    # Test block to execute immediate update when run directly
    print("Running manual scheduler test run...")
    run_database_update()
