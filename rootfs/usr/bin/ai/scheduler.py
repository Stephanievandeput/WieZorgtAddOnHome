import time
import os
from Core.SafeScheduler import SafeScheduler
import urllib3
from Core.HomeAssistantMaintenance import HomeAssistantMaintenance
from Core.HomeAssistantTrainingData import HomeAssistantTrainingData
from Core.AiTraining import AiTraining
import argparse
import logging
import datetime
from datetime import date
from datetime import timedelta

# set logging settings
logging.basicConfig(
    format="%(asctime)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)
logging.Formatter.formatTime = (lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat(sep="T",timespec="milliseconds"))


# create http pool manager
http = urllib3.PoolManager()


# parse arguments
parser = argparse.ArgumentParser(description='Updates scenario entities.')
parser.add_argument('--mode', choices=['production', 'development'], default="production", help='In development mode it will used url and bearer argument instead of HA system variables')
parser.add_argument('--url', type=str, help='bearer token', required=False)
parser.add_argument('--bearer', type=str, help='bearer token', required=False)
parser.add_argument('--datapath', type=str, help='data path', default="/data/", required=False)
args = parser.parse_args()
_datapath = args.datapath


def ha_url():
    """
    Returns the url of the Home Assistant API

    :return:
    """
    if args.mode == "production":
        return "http://supervisor/core/api"
    else:
        return args.url


def ha_bearer():
    """
    Returns the bearer token of the Home Assistant API

    :return:
    """
    if args.mode == "production":
        return os.environ.get('SUPERVISOR_TOKEN')
    else:
        return args.bearer


def check_scenario_attributes():
    """
    Checks if the scenario attributes are present and if not updates them

    :return:
    """
    _HAMTN = HomeAssistantMaintenance(http, _datapath, ha_url(), ha_bearer())
    for i in range(3):
        if _HAMTN.is_api_running():
            logging.warning("Api is running - called in check_scenario_attributes")
            if not _HAMTN.has_breakfast_entity():
                logging.warning("No breakfast scenario entity found, reloading scenario data.")
                update_scenario_attributes()
            return
        time.sleep(5)
    logging.warning("HA API not running resulting in failure of performing breakfast scenario entity check.")


# tasks to schedule
def update_scenario_attributes():
    """
    Updates the scenario attributes

    :return:
    """
    _HAMTN = HomeAssistantMaintenance(http, _datapath, ha_url(), ha_bearer())
    logging.info("Updating scenario attributes")
    for i in range(3):
        if _HAMTN.is_api_running():
            _HAMTN.update_all_scenario_states()
            logging.info("Done")
            return
        time.sleep(5)
    logging.warning("HA API not running resulting in failure of updating scenario attributes.")


def run_AI():
    """
    Runs the AI module

    :return:
    """
    logging.warning("Starting run_AI process")

    _HAMTN = HomeAssistantMaintenance(http, _datapath, ha_url(), ha_bearer())
    logging.info("Starting run AI task")
    # HomeAssistant training data retrieval
    for i in range(64): # keep trying for 5 hours
        if _HAMTN.is_api_running():
            logging.warning("Retrieving yesterday's data from home assistant")
            HATD = HomeAssistantTrainingData(http, ha_url(), ha_bearer())
            result = HATD.retrieve_yesterday(compact=True)
            # Run AI with this data
            logging.warning("Running AI module on the retrieved data")
            AITM = AiTraining(_datapath)
            AITM.load_dataset(result)
            AITM.store_dataset()
            AITM.run_training()
            _HAMTN.store_cache(date.today() - timedelta(days = 1))
            update_scenario_attributes()
            logging.warning("Task complete")
            return
        time.sleep(5)
    logging.warning("HA API not running resulting in failure of running AI task.")


def make_backup():
    """
    Makes a backup of all the data

    :return:
    """
    _HAMTN = HomeAssistantMaintenance(http, _datapath, ha_url(), ha_bearer())
    logging.info("Creating backup")
    _HAMTN.make_backup()
    logging.info("Done creating backup")

# create scheduler
schedule = SafeScheduler()
schedule.every().day.at("00:10").do(run_AI) # 0:10 AM every day we run the AI module
#schedule.every(10).minutes.do(run_AI) # 0:10 AM every day we run the AI module
schedule.every().day.at("16:30").do(make_backup) # 2 AM every day we backup all of the data
schedule.every().minute.do(check_scenario_attributes)

# run scenario updater and backup flow upon start
try:
    update_scenario_attributes()
    make_backup()
except:
  print("Warning: Failed to initialize scheduler service properly")



# start scheduler loop
while True:
    schedule.run_pending()
    time.sleep(1)