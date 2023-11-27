import pprint
import json
import urllib3
from Core.HomeAssistantMaintenance import HomeAssistantMaintenance
from Core.HomeAssistantTrainingData import HomeAssistantTrainingData
from Core.AiTraining import AiTraining
import argparse
import logging
import datetime


logging.basicConfig(
    format="%(asctime)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)
logging.Formatter.formatTime = (lambda self, record, datefmt=None: datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc).astimezone().isoformat(sep="T",timespec="milliseconds"))

# create http pool manager
http = urllib3.PoolManager()

# parse arguments
parser = argparse.ArgumentParser(description='Updates scenario entities.')
parser.add_argument('--mode', choices=['production', 'development'], default="production", help='not in use for dev scripts')
parser.add_argument('--url', type=str, help='bearer token', required=True)
parser.add_argument('--bearer', type=str, help='bearer token', required=True)
parser.add_argument('--datapath', type=str, help='data path', default="/Core/data/", required=False)
args = parser.parse_args()
_url = args.url
_bearer = args.bearer
_datapath = args.datapath

# initialize pretty printer
pp = pprint.PrettyPrinter(indent=2)

def main():
    """
    Main function

    :return:
    """
    #Run AI with testdata
    _HAMTN = HomeAssistantMaintenance(http, _datapath, _url, _bearer)
    TD = HomeAssistantTrainingData(http, _url, _bearer)
    data = TD.retrieve_today()
    AIT = AiTraining("/Users/wendywtchang/GitHub/WieZorgtAI/Data/WieZorgt/persistent/")
    print(data)
    AIT.load_dataset(data)
    AIT.store_dataset()
    AIT.run_training()
    #AIT.run_simulation()

main()
