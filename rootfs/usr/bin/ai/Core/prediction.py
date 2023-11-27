import datetime
import os
# import sys

import numpy as np
from tabulate import tabulate

# sys.path.append("/Users/wendywtchang/GitHub/WieZorgtAI/wiezorgt/rootfs/usr/bin/ai")
from .data.envs.exp_8 import UserBot_8
from .AiCMAB import ContextualThompsonSamplingAgent
from .utils import training_config as config

def generate_and_save_table(trial, env, agent, env_name, agent_name, random=None):
    actions = env.actions
    meals = env.contexts
    user_preferences = env.user_preferences
    next_secenario = {}

    # Create an empty list to store table data
    table_data = []

    
    for meal in meals:
        observation = env.predict(meal=meal)
        # env.render()

        action = agent.act(observation)
        _, reward, _, _ = env.step(action)

        # Append data for each iteration to the table_data list
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        table_data.append([tomorrow, meal, action + 1, actions[action], reward, user_preferences[meal]])
        
        next_secenario[meal] = actions[action]


    # Define table headers
    headers = ["Next Day", "Meal", "Predicted Action", "Combination", "Reward", "User Preference"]

    # Use tabulate to create a formatted table
    table = tabulate(table_data, headers, tablefmt="grid")


    # Save the table to a text file
    if env_name == "UserBot_8":
        prediction_table_dir = f"./logs/prediction/{env_name}/{tomorrow}/{env.user_type_id}/{agent_name}/"
    # else:
    #     prediction_table_dir = f"./logs/prediction/{env_name}/{config.n_trials}/{agent_name}/"

    os.makedirs(prediction_table_dir, exist_ok=True)

    
    # with open(f"{prediction_table_dir}{tomorrow}_table.txt", "w") as f: # for HA
    now = datetime.datetime.now()
    with open(f"{prediction_table_dir}{now}_table.txt", "w") as f: # for testing
        f.write(table)

    # Print a confirmation message
    print(f"Table saved at {prediction_table_dir}")
    return next_secenario

# If this script is run directly, execute the function
if __name__ == "__main__":
    # assume env and agent are already defined or imported
    config = config.Config()
    trial = config.n_trials
    env = UserBot_8()
    agent = ContextualThompsonSamplingAgent(n_actions=env.action_space.n, n_contexts=len(env.contexts))
    env_name = type(env).__name__
    agent_name = type(agent).__name__
    generate_and_save_table(trial, env, agent, env_name, agent_name, random=None)