import json
import random
import numpy as np
import gym
from gym import spaces
from itertools import product

# import sys
# sys.path.append("/Users/wendywtchang/GitHub/WieZorgtAI/wiezorgt/rootfs/usr/bin/ai")
from .generate_preferences import *

"""
This environment is for Randomness Test [People with different type of preference, diversity]

Experiment purpose: We want to know if the algorithm can adapt to different user types A-I (9 types)
--> All the user types are pre-generated from generate_preference.py

"""

def load_actions():
    # action list has to be fix
    actions_path = "./Core/data/envs/actions.json"  
    with open(actions_path, 'r') as json_file:
        actions = json.load(json_file)
    return actions

def load_user_preferences():
    # action list has to be fix
    preferences_path = "./Core/data/envs/user_preferences.json"  
    with open(preferences_path, 'r') as json_file:
        user_preferences = json.load(json_file)
    return user_preferences

def load_user_types():
    # action list has to be fix
    preferences_path = "./Core/data/envs/user_types.json"  
    with open(preferences_path, 'r') as json_file:
        user_types = json.load(json_file)
    return user_types


class UserBot_8(gym.Env):
    def __init__(self):
        super(UserBot_8, self).__init__()

        # contexts: 3 meals
        self.contexts = ["breakfast", "lunch", "dinner"]
        self.actions = load_actions()

        # Defining the action and observation spaces
        self.action_space = spaces.Discrete(len(self.actions))  
        self.observation_space = spaces.Discrete(len(self.contexts))

        # User preference dict (pre-defined)
        self.user_preferences = load_user_preferences()

        # User type experiment
        user_types = load_user_types()
        self.user_type_id = "user_type_C"
        self.user_type = user_types[self.user_type_id]

    def shift(self, mode=1):
        user_types = load_user_types()

        if mode==1:
            user_type_id = f"{self.user_type_id}"
        if mode==2:
            user_type_id = f"{self.user_type_id}_2"

        self.user_type = user_types[user_type_id]

        return self.user_type

    def shuffle(self):
        reset_user_preference = generate_preferences(user_type=self.user_type)
        json_filename = './Core/data/envs/user_preferences.json'
        save_to_json(reset_user_preference, json_filename)
        self.user_preferences = load_user_preferences()

    def step(self, action, acceptance=1):
        context = self.contexts[self.current_context]
        action_name = self.actions[action]
        reward = 0

        # Check if action is in user preferences for the current context
        for signal in action_name:
            if signal in self.user_preferences[context]:
                if np.random.rand() < acceptance:
                    reward = 1
                    break
                else:
                    reward = 0

        done = True  # End the episode after one step
        return self.current_context, reward, done, {}

    def reset(self):
        # Randomly initialize the context
        self.current_context = np.random.choice([0, 1, 2])
        return self.current_context

    def predict(self, meal):
        if meal == "breakfast":
            self.current_context = np.random.choice([0])
        elif meal == "lunch":
            self.current_context = np.random.choice([1])
        elif meal == "dinner":
            self.current_context = np.random.choice([2])
        return self.current_context

    def render(self, mode='human'):
        print(f"Current context: {self.contexts[self.current_context]}")

    def close(self):
        pass



if __name__ == "__main__":
    # Test the environment
    env = UserBot_8()

    env.shift(mode=1)
    # env.shift(mode=2)
    env.shuffle()

    for _ in range(5):
        observation = env.reset()
        env.render()
        action = env.action_space.sample()  # Taking a random action
        actions = load_actions()
        print(f"Robot took action: {action+1}, {actions[action]}")
        observation, reward, done, info = env.step(action)
        print(f"Received reward: {reward}\n")