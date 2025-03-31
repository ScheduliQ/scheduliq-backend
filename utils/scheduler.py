from apscheduler.schedulers.background import BackgroundScheduler
import time
from datetime import datetime, timezone, timedelta
# יש לייבא את הפונקציה transition_cycle ממודול ההגדרות/מודל המתאמים שלך
from models.manager_settings_model import transition_cycle, get_manager_settings

# Global variable to hold the scheduler instance
SCHEDULER = None

def get_cron_trigger_params(submission_date: datetime,local_tz) -> dict:
    print("get_cron_trigger_params..................")
    """
    Converts a datetime (submission_date) to cron trigger parameters.
    The function extracts:
      - day_of_week: a three-letter lowercase string (e.g., 'sun', 'mon', etc.)
      - hour: the hour (0-23)
      - minute: the minute (0-59)
    """
    local_date = submission_date.astimezone(local_tz)
    day_of_week = local_date.strftime('%a').lower()  # e.g., "wed"
    return {
        "day_of_week": day_of_week,
        "hour": local_date.hour,
        "minute": local_date.minute,
    }


def start_scheduler() -> BackgroundScheduler:
    global SCHEDULER

    print("start_scheduler..................")
    """
    Initializes and starts the APScheduler with the transition_cycle job.
    The job is scheduled to run every Sunday at 00:00 UTC.
    Returns the scheduler instance.
    """
    scheduler = BackgroundScheduler(timezone=timezone.utc)
    local_tz = timezone(timedelta(hours=2))
    cron_params = get_cron_trigger_params(get_manager_settings().get("submissionStart"), local_tz)
    print(f"cron_params: {cron_params}")
    scheduler.add_job(transition_cycle, 'cron',id="transition_cycle_job", **cron_params)
    scheduler.start()
    SCHEDULER = scheduler

    print(f"Scheduler started at {datetime.now(timezone.utc)}")
    return scheduler


def reschedule_transition_job():
    global SCHEDULER
    local_tz = timezone(timedelta(hours=2))
    new_cron_params = get_cron_trigger_params(get_manager_settings().get("submissionStart"), local_tz)
    if SCHEDULER is not None:
        try:
            SCHEDULER.reschedule_job("transition_cycle_job", trigger='cron', **new_cron_params)
            print(f"Rescheduled transition_cycle_job with new parameters: {new_cron_params}")
        except Exception as e:
            print("Error rescheduling job:", e)
    else:
        print("Scheduler is not running.")

# If this file is run as main, start the scheduler in a loop.
if __name__ == '__main__':
    scheduler = start_scheduler()
    try:
        # Keep the scheduler running
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler shutdown")