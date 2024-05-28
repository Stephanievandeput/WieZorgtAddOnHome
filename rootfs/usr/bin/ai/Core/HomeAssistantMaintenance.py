import json
import os
import subprocess
import logging
import shutil
from datetime import date, datetime, timedelta
from .utils.helpers import *


class HomeAssistantMaintenance:
    def __init__(self, http: object, persistent_data_path: str, url: str, bearer: str) -> object:
        """
        Home Assistant Training Data module

        :type client: Client
        """
        self.http = http
        self.url = url
        self.bearer = bearer
        logging.warning("Bearer: " + bearer)
        self.persistent_data_path = persistent_data_path
        logging.warning("Persistent data path: " + persistent_data_path)
        self.cache_data_path = f"{self.persistent_data_path}cache/"
        self.results_data_path = f"{self.cache_data_path}results/"
        logging.warning("Result data path: " + self.results_data_path)
        self.models_data_path = f"{self.cache_data_path}models/"
        self.training_data_path = f"{self.cache_data_path}training_data/"
        self.history_data_path = f"{self.persistent_data_path}history/"
        self.figures_data_path = f"{self.persistent_data_path}figures/"
        self.logbook_data_path = f"{self.persistent_data_path}logbook/"
        self.static_data_path = "Core/data/"
        self.config = {}
        self.fix_base_structure()
        self.read_conf()

    def fix_path(self, path):
        """
        Create path if not existing

        :param path:
        :return:
        """
        if not os.path.exists(path):
            logging.warning("Path van fix_path/mkdirs: " + path)
            os.makedirs(path)
            logging.warning("Done with fix_path")

    def fix_base_structure(self):
        """
        Create base structure if not existing

        :return:
        """
        logging.warning(os.listdir("/"))
        self.fix_path(self.persistent_data_path)
        self.fix_path(self.cache_data_path)
        self.fix_path(self.results_data_path)
        self.fix_path(self.models_data_path)
        self.fix_path(self.training_data_path)
        self.fix_path(self.history_data_path)
        self.fix_path(self.figures_data_path)
        self.fix_path(self.logbook_data_path)
        logging.warning(os.listdir("/"))
        if not os.path.exists(f"{self.results_data_path}AI_HA_scenarios.json"):
            logging.warning("Scenario's entity objects do not exist yet, creating.")
            with open(f"{self.static_data_path}AI_HA_default_scenarios.json", "r") as inpf, open(f"{self.results_data_path}AI_HA_scenarios.json", "w") as outpf:
                for line in inpf:
                    outpf.write(line)
        if not os.path.exists(f"{self.persistent_data_path}options.json"):
            logging.warning("Options file not existing, creating it.")
            with open(f"{self.static_data_path}options.json", "r") as inpf, open(f"{self.persistent_data_path}options.json", "w") as outpf:
                for line in inpf:
                    outpf.write(line)

    def read_conf(self):
        """
        Read configuration file

        :return:
        """
        with open(f"{self.persistent_data_path}options.json") as cf:
            self.config = json.load(cf)
        with open(f"{self.persistent_data_path}repo_passwd", "w") as pwpf:
            pwpf.write(self.config["backup"]["repopass"])

    def update_all_scenario_states(self):
        """
        Add test scenario parameter on breakfast scenario

        :return: homeassistant state object
        """

        with open(f"{self.results_data_path}AI_HA_scenarios.json", "r") as file:
            scenario_states = json.load(file)
            self.update_states("breakfast", scenario_states["breakfast"])
            self.update_states("lunch", scenario_states["lunch"])
            self.update_states("dinner", scenario_states["dinner"])
            return True

    def is_api_running(self):
        """
        Check if Home Assistant API is running

        :return:
        """
        logging.warning(self.url)
        resp = self.http.request(
            "GET",
            f"{self.url}/",
            headers={
                "Authorization": "Bearer {}".format(self.bearer),
                "content-type": "application/json"
            }
        )
        logging.warning("Response: " + str(resp.status) + " data: " + str(resp.data))
        if resp.status == 200:
            return True
        else:
            return False

    def has_breakfast_entity(self):
        """
        Check if breakfast scenario entity exists

        :return:
        """
        resp = self.http.request(
            "GET",
            f"{self.url}/states/scenario.breakfast",
            headers={
                "Authorization": "Bearer {}".format(self.bearer),
                "content-type": "application/json"
            }
        )

        if resp.status == 200:
            return True
        else:
            return False

    def update_states(self, identifier: str, attributes: object) -> object:
        """
        Update states of scenario

        :param identifier: scenario id (ie: breakfast, lunch, dinner)
        :param attributes: attributes object (can be any object the Home Assistant scripts can interpret)
        :return: 
        """

        url = f"{self.url}/states/scenario.{identifier}"
        headers = {
            "Authorization": "Bearer {}".format(self.bearer),
            "content-type": "application/json"
        }
        self.http.request(
            "POST",
            url,
            headers=headers,  # Add custom form fields
            body=json.dumps({"state": "inactive", "attributes": attributes})
        )
        resp = self.http.request(
            "POST",
            url,
            headers=headers,  # Add custom form fields
            body=json.dumps({"state": "active", "attributes": attributes})
        )
        return json.loads(resp.data)

    def store_cache(self, date):
        """
        Store cache data in persistent data directory
        :param date:
        :return:
        """
        shutil.make_archive(f"{self.history_data_path}{date}", 'zip', self.cache_data_path)

    def get_logbook(self):
        """
        Get logbook from supervisor

        :return:
        """
        start_time = (date.today() - timedelta( days=7 )).isoformat()
        end_time = datetime.now().isoformat()

        resp = self.http.request(
            "GET",
            f"{self.url}/logbook/{start_time}?end_time={end_time}",
            headers={
                "Authorization": "Bearer {}".format(self.bearer),
                "content-type": "application/json"
            }
        )

        if resp.status == 200:
            return resp.json()
        else:
            return ""

    def save_logbook(self):
        """
        Dump logbook to file 

        :return:
        """

        logbook = self.get_logbook()
        today = date.today().isoformat()

        write_json( f"{self.logbook_data_path}/logbook-{today}", logbook )


    def make_backup(self):
        """
        Make backup of persistent data directory

        :return:
        """
        # get the most recent config
        self.read_conf()
        if self.config['backup']['username'] != "" and self.config['backup']['username'] != "" and self.config['backup']['userpass'] != "" and self.config['backup']['repopass'] != "":
            dev_null = open(os.devnull, 'wb')
            # creating repo (will only create one if no one exists, error outputs will be ignored)
            subprocess.call(f"restic --password-file='{self.persistent_data_path}repo_passwd' --repo='rest:https://{self.config['backup']['username']}:{self.config['backup']['userpass']}@{self.config['backup']['host']}/{self.config['backup']['username']}/addon_data' init --repository-version 2", shell=True, stderr=dev_null)
            # Run backup script
            subprocess.call(f"restic --password-file='{self.persistent_data_path}repo_passwd' --repo='rest:https://{self.config['backup']['username']}:{self.config['backup']['userpass']}@{self.config['backup']['host']}/{self.config['backup']['username']}/addon_data' backup '{self.persistent_data_path}' --compression auto", shell=True)

