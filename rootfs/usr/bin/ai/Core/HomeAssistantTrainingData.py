from copy import deepcopy
import json
from datetime import date
from datetime import timedelta
from datetime import datetime

class HomeAssistantTrainingData:
    def __init__(self, http, url, bearer) -> object:
        """
        Home Assistant Training Data module

        :type client: Client
        """
        self.http = http
        self.url = url
        self.bearer = bearer

        # entity filterlist for data retrieval
        self.entity_filter = frozenset({
            "scenario.breakfast",
            "scenario.lunch",
            "scenario.dinner",
            "automation.wz_breakfast",
            "automation.wz_lunch",
            "automation.wz_dinner",
            "script.wz_food_scenario",
            "script.wz_food_stage",
            "sensor.person_location",
            "binary_sensor.person_eating"
        })

        # default values for scenario

        self.default_scenario = {
            "meal_type": None,
            "activated": False,
            "start_time": None,
            "reacted": False,
            "reacted_probability": None,
            "finished": False,
            "reaction_time": None, # reaction time from start of scenario
            "current_stage": {
                "number": None,
                "start_time": None,
                "reaction_time": None # reaction time from start of stage
            },
            "stages": [],
        }

        # local storage for scenario attributes

        self.scenario_attributes = {
            "breakfast": {},
            "lunch": {},
            "dinner": {}
        }

        # set current states to default values
        self.current_states = {
            "scenario": deepcopy(self.default_scenario),
            "location": "not_home",
            "activity": "none",
            "needs_a_break": False,
            "activity_probability": None
        }

        self.raw_data = {
            "state_objects": {},
            "log_objects": {},
            "index": set(), # no duplicate timestamps
        }

    def retrieve_today(self, compact=False):
        """
        Retrieve today's data

        :type compact: retrieve in compact format
        :return: AI training data object
        """
        self.retrieve_data(date.today())
        return self.process_data(compact)

    def retrieve_yesterday(self, compact=False):
        """
        Retrieve yesterday's data

        :type compact: retrieve in compact format
        :return: AI training data object
        """
        self.retrieve_data(date.today() - timedelta(days = 1))
        return self.process_data(compact)

    def retrieve_data(self, start_timestamp: date) -> object:
        """
        Retrieve training data based on date stamp

        :param compact: retrieve in compact format
        :param start_timestamp: start time as date object
        :return: AI training data object
        """


        state_url = "{url}/history/period/{timestamp}".format(url=self.url, timestamp=start_timestamp)
        log_url = "{url}/logbook/{timestamp}".format(url=self.url, timestamp=start_timestamp)
        headers = {
            "Authorization": "Bearer {}".format(self.bearer),
            "content-type": "application/json"
        }

        resp = self.http.request(
            "GET",
            state_url,
            headers=headers,  # Add custom form fields
            fields={"filter_entity_id": ",".join(self.entity_filter)}
        )
        r_json = json.loads(resp.data)
        for r_ent in r_json:
            for state_change in r_ent:
                ts = int(datetime.fromisoformat(state_change["last_updated"]).timestamp() * 1000000)
                self.raw_data["index"].add(ts)
                self.raw_data["state_objects"][ts] = state_change

        resp = self.http.request(
            "GET",
            log_url,
            headers=headers,  # Add custom form fields
        )
        r_json = json.loads(resp.data)
        for r_log in r_json:
            if "entity_id" in r_log: #we only need log entries with entity id's in it
                ts = int(datetime.fromisoformat(r_log["when"]).timestamp() * 1000000)
                self.raw_data["index"].add(ts)
                self.raw_data["log_objects"][ts] = r_log

    def set_reaction_time(self, current_stage_start_time, scenario_start_time, state_obj):
        self.current_states["scenario"]["reacted"] = True
        self.current_states["scenario"]["reacted_probability"] = state_obj["attributes"]["probability"]
        self.current_states["scenario"]["finished"] = True
        # generate reaction time in seconds with microseconds accuracy
        reaction_time = (
                    datetime.fromisoformat(state_obj["last_updated"]) - datetime.fromisoformat(scenario_start_time))
        current_stage_reaction_time = (datetime.fromisoformat(state_obj["last_updated"]) - datetime.fromisoformat(
            current_stage_start_time))
        self.current_states["scenario"]["reaction_time"] = reaction_time.seconds + (
                    reaction_time.microseconds / 1000000.0)
        self.current_states["scenario"]["current_stage"]["reaction_time"] = current_stage_reaction_time.seconds + (
                    current_stage_reaction_time.microseconds / 1000000.0)

    def process_data(self, compact=False) -> object:
        """
        Process raw data into AI training data object

        :param compact:
        :return:
        """
        dataset = []

        # scenario's to filter on
        scenario_entity_filter = frozenset({"scenario.breakfast", "scenario.lunch", "scenario.dinner"})
        # scenario's to filter on
        automation_filter = frozenset({"automation.wz_breakfast", "automation.wz_lunch", "automation.wz_dinner"})
        # location entities to filter on
        location_entity_filter = frozenset({"sensor.person_location"})

        meal_type = None
        scenario_start_time = None
        current_stage_start_time = None
        current_time = None

        # loop through time sorted states and create dataset
        self.raw_data["index"] = list(self.raw_data["index"])
        self.raw_data["index"].sort()
        for data_idx in self.raw_data["index"]:
            # reset data
            state_obj = {}
            log_obj = {}
            state_changed = False
            has_state_obj = False
            has_log_obj = False

            # load data entries
            if data_idx in self.raw_data["state_objects"]:
                has_state_obj = True
                state_obj = self.raw_data["state_objects"][data_idx]
            if data_idx in self.raw_data["log_objects"]:
                has_log_obj = True
                log_obj = self.raw_data["log_objects"][data_idx]


            # reset timestamps
            if has_log_obj and log_obj["entity_id"]:
                current_time = log_obj["when"]
            if has_state_obj:
                current_time = state_obj["last_updated"]

            # reset states if scenario has finished previously
            if self.current_states["scenario"]["finished"]:
                state_changed = True
                meal_type = None
                scenario_start_time = None
                self.current_states["scenario"] = deepcopy(self.default_scenario)


            # set scenario attributes when scenario object had been called
            if has_state_obj and state_obj["entity_id"] in scenario_entity_filter:
                self.scenario_attributes[state_obj["entity_id"].removeprefix("scenario.")] = state_obj["attributes"]

            # set current scenario running
            if has_log_obj and log_obj["entity_id"] == "script.wz_food_scenario" and "state" in log_obj:
                if log_obj["state"] == "on" and "context_entity_id" in log_obj and log_obj["context_entity_id"] in automation_filter:
                    meal_type = log_obj["context_entity_id"].removeprefix("automation.wz_")
                    scenario_start_time = log_obj["when"]
                # reset state when the scenario script has ended
                elif log_obj["state"] == "off" and self.current_states["scenario"]["activated"]:
                    state_changed = True
                    self.current_states["scenario"]["finished"] = True


            # stage script has been turned on
            if has_state_obj and state_obj["entity_id"] == "script.wz_food_stage" and state_obj["state"] == "on":
                state_changed = True
                # update stage information
                current_stage_start_time = state_obj["last_updated"]
                self.current_states["scenario"]["activated"] = True
                self.current_states["scenario"]["meal_type"] = meal_type
                self.current_states["scenario"]["start_time"] = scenario_start_time
                self.current_states["scenario"]["current_stage"]["start_time"] = current_stage_start_time
                # increment stage number
                if self.current_states["scenario"]["current_stage"]["number"] is None:
                    self.current_states["scenario"]["current_stage"]["number"] = 0 # start at one
                else:
                    self.current_states["scenario"]["current_stage"]["number"] += 1

                # set stimuli and stimuli combinations if they're known
                try:
                    for key ,stage in enumerate(self.scenario_attributes[self.current_states["scenario"]["meal_type"]]["stages"]):
                        self.current_states["scenario"]["stages"].append(
                            {
                            "stimuli": stage["stimuli"],
                            "stimuli_combination": stage["stimuli_combination"]
                            }
                        )

                except Exception as e:
                    print("warning scenario state not known at this moment: {}".format(e))

            # set current location information
            if has_state_obj and state_obj["entity_id"] in location_entity_filter:
                if self.current_states["location"] != state_obj["state"]:
                    state_changed = True
                    self.current_states["location"] = state_obj["state"]

            # check person is eating state
            if has_state_obj and state_obj["entity_id"] == "binary_sensor.person_eating":
                # person is eating
                if state_obj["state"] == "on" and self.current_states["activity"] == "none":
                    state_changed = True
                    self.current_states["activity"] = "eating"
                    self.current_states["activity_probability"] = state_obj["attributes"]["probability"]
                    # when scenario is running during an eating start, store reaction times etc
                    if self.current_states["scenario"]["activated"]:
                        self.set_reaction_time(current_stage_start_time, scenario_start_time, state_obj)

                # person is eating state ended
                elif self.current_states["activity"] == "eating":
                    state_changed = True
                    self.current_states["activity"] = "none"

            # check person is eating state
            if has_state_obj and state_obj["entity_id"] == "binary_sensor.needs_a_break":
                # person is eating
                if state_obj["state"] == "on" and self.current_states["needs_a_break"] == False:
                    state_changed = True
                    self.current_states["needs_a_break"] = True
                    # when scenario is running during an eating start, store reaction times etc
                    if self.current_states["scenario"]["activated"]:
                        self.set_reaction_time(current_stage_start_time, scenario_start_time, state_obj)

                # person is eating state ended
                elif not self.current_states["needs_a_break"]:
                    state_changed = True
                    self.current_states["needs_a_break"] = False

            # create data entry
            if state_changed and (compact == False or (compact == True and self.current_states["scenario"]["finished"])):
                dataset.append(
                    {
                        "date": current_time,
                        "user_location": self.current_states["location"],
                        "user_activity": self.current_states["activity"],
                        "scenario": deepcopy(self.current_states["scenario"])
                    }
                )
        # return complete dataset
        return dataset


