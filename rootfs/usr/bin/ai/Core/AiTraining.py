import logging
import os
import datetime
import time
import json
import numpy as np

from tensorboardX import SummaryWriter

from .AiCMAB import ContextualThompsonSamplingAgent
from .data.envs.exp_8 import UserBot_8
from .prediction import generate_and_save_table
from .utils import helpers
from .utils import training_config



class AiTraining:
    def __init__(self, persistent_data_path) -> object:
        """
        WieZorgt AI Training Module

        """

        # initializing directories
        # TODO check or redifine "persistent_data_path"
        self.persistent_data_path = persistent_data_path
        self.cache_data_path = f"{self.persistent_data_path}cache/"
        self.results_data_path = f"{self.cache_data_path}results/"
        self.models_data_path = f"{self.cache_data_path}models/"
        self.training_data_path = f"{self.cache_data_path}training_data/"
        self.figures_data_path = f"{self.persistent_data_path}figures/"
        self.static_data_path = "Core/data/envs/"

        # Define contexts and action combinations
        self.contexts = ["breakfast", "lunch", "dinner"]  # contexts: 3 meals
        self.actions = helpers.load_actions()

        # load HA output templates
        self.ha_output_templates = {}
        for key in self.contexts:
            self.ha_output_templates[key] = helpers.load_json(
                self.static_data_path, f"AI_HA_{key}.json"
            )

        self.ha_output = {}

        # load actions
        self.actions = helpers.load_json(
            self.static_data_path, "actions.json"
        )  # action_combinations
        self.st_sts_mapping = helpers.load_json(
            self.static_data_path, "st_sts_mapping.json"
        )  # signal to script mapping

    def load_dataset(self, dataset):
        """
        Load dataset

        :param dataset:
        :return:
        """
        self.dataset = dataset

    def store_dataset(self):
        """
        Store dataset

        :return:
        """
        with open(f"{self.training_data_path}data.json", "w") as ds:
            json.dump(self.dataset, ds)

    def run_training(self):
        """
        Run AI model training

        :return:
        """
        # reset home assistant output
        self.ha_output = {}

        # TODO: we might need to update real time environment. Here I just implement UserBot 8 as an example (20231024) - Wendy
        # Initialize the environment and agent
        env = UserBot_8()
        config = training_config.Config()

        # Load agent
        # Saved model path
        saved_model_path = "./models/ContextualThompsonSamplingAgent.pkl"

        # Check if saved model exists
        if os.path.exists(saved_model_path):
            # Load the agent from the saved model
            agent = ContextualThompsonSamplingAgent(
                n_actions=env.action_space.n, n_contexts=len(env.contexts)
            )
            agent.load_params(saved_model_path)
            print("="*20)
            print(f"Loading latest trained model from: {saved_model_path}")
        else:
            # Create a new agent
            agent = ContextualThompsonSamplingAgent(
                n_actions=env.action_space.n, n_contexts=len(env.contexts)
            )
            print("=" * 20)
            print(f"Creating new agent model.")

        # Training configs (Working on: real-time update)
        n_trials = config.n_trials
        total_training_time = 0
        rewards = (
            helpers.load_rewards()
        )  # Here: equals to "all_rewards" in simulation code

        # Logging configs (tensorboardX)
        agent_name = type(agent).__name__
        env_name = type(env).__name__
        log_dir_name = f"./logs/{env_name}/{agent_name}/"
        os.makedirs(log_dir_name, exist_ok=True)

        # Log hyperparameters
        writer = SummaryWriter(logdir=log_dir_name)
        writer.add_text("Hyperparameters/agent_name", agent_name, 0)
        writer.add_text("Hyperparameters/n_trials", str(n_trials), 0)

        # Prepare training
        print("=" * 20)
        print(f"Start running Experiment {env_name} with agent {agent_name}")

        # Initialize environment and agent
        env.__init__()

        trial_start_time = time.time()

        # Start running trials:
        for trial in range(n_trials):
            observation = env.reset()  # == context
            action = agent.act(observation)

            _, reward, _, _ = env.step(action, acceptance=1)

            next_secenario = generate_and_save_table(
                trial, env, agent, env_name, agent_name, random=None
            )

            # pp.pprint(next_secenario)


            agent.update(observation, action, reward)

            rewards.append(reward)

        # Accumulate epoch training time
        total_training_time += time.time() - trial_start_time

        print("=" * 20)
        print(f"End of Training {agent_name}")

        # Save model
        now = datetime.datetime.now()
        agent.save_params(file_path=f"./models/{now}/{agent_name}.pkl")  # model
        agent.save_params(file_path=f"./models/{agent_name}.pkl")

        # Save rewards
        helpers.save_rewards(rewards)

        # Standard deviation of rewards
        std_dev_rewards = np.std(rewards, axis=0)

        # Calculate and log training time for this trial
        # TODO: We might not need tensorboardX part or we need to modift it
        writer.add_scalar("Training time this trial", total_training_time, n_trials)
        writer.close()

        # create output for all contexts and write output to cache path for home assistant to run
        now = datetime.datetime.now()
        #logging.warning("AI training: ik ben bij de meal loop " + " Het result data path hier is: " + self.results_data_path)
        for meal in self.contexts:
            self.ha_output[meal] = helpers.write_stimuli_combination(
                self.ha_output_templates[meal],
                next_secenario[meal],
                self.st_sts_mapping,
                meal_type=meal
            )
            os.makedirs(self.results_data_path, exist_ok=True)
            
            helpers.write_json(
                # f"{self.results_data_path}/{now}_AI_HA_scenarios", self.ha_output # for testing
                f"{self.results_data_path}/AI_HA_scenarios", self.ha_output  # original
            )
        print("="*20)
        print(f"Save scenario script tomorrow at {self.results_data_path}/{now}_AI_HA_scenarios (Interface AI to HA)")
        print("="*20)

if __name__ == "__main__":
    persistent_data_path = (
        "WieZorgt/rootfs/usr/bin/ai/data"
    )
    AiTraining = AiTraining(persistent_data_path)
    AiTraining.run_training()
