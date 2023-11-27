from Core.AiTraining import AiTraining
import pprint
import json
import logging
import datetime
import urllib3
from Core.HomeAssistantMaintenance import HomeAssistantMaintenance

# set logging settings
logging.basicConfig(
    format="%(asctime)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)
logging.Formatter.formatTime = (lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat(sep="T",timespec="milliseconds"))

# create http pool manager
http = urllib3.PoolManager()

# initialize pretty printer
pp = pprint.PrettyPrinter(indent=2)

# _datapath = "/mnt/c/Data/WieZorgt/persistent/" #change to any directory you want, structure will be built by the maintenance class
_datapath = "/Users/wendywtchang/GitHub/WieZorgtAI/Data/WieZorgt/persistent/"
def main():
    """
    Main function

    :return:
    """
    # Run AI with testdata
    _HAMTN = HomeAssistantMaintenance(http, _datapath, "url_not_used", "bearer_not_used")
    AIT = AiTraining(_datapath)
    f = open("Core/data/test_data.json")
    data = json.load(f)
    print(data)
    AIT.load_dataset(data)
    AIT.store_dataset()
    AIT.run_training()
    _HAMTN.store_cache("test") # store cache dir in test.zip in history folder for backup purposes
    #AIT.run_simulation()

main()
