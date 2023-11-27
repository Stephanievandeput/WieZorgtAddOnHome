import math
import numpy as np
import pickle
import os

class ContextualThompsonSamplingAgent:
    """
    Represents a reinforcement learning agent implementing the 
    Contextual Thompson Sampling algorithm.
    
    Attributes:
    - n_actions (int): Total number of available actions.
    - n_contexts (int): Number of different contexts like breakfast, lunch, and dinner.
    - alpha (np.ndarray): Success parameters for the Beta distribution.
    - beta (np.ndarray): Failure parameters for the Beta distribution.
    """
    def __init__(self, n_actions, n_contexts):
        """
        Initializes the agent with the given number of actions and contexts.
        
        Parameters:
        - n_actions (int): Total number of available actions.
        - n_contexts (int): Number of different contexts.
        """
        self.alpha = np.ones((n_contexts, n_actions))
        self.beta = np.ones((n_contexts, n_actions))

    def act(self, context):
        """
        Determines the best action for a given context by sampling from the Beta distribution.
        
        Parameters:
        - context (int): The current context.
        
        Returns:
        int: The chosen action.
        """
        theta = np.random.beta(np.clip(self.alpha[context], 1e-9, None), np.clip(self.beta[context], 1e-9, None))
        return np.argmax(theta)

    def update(self, context, action, reward):
        """
        Updates the success and failure parameters based on the observed reward.
        
        Parameters:
        - context (int): The context in which the action was taken.
        - action (int): The taken action.
        - reward (int): The observed reward.
        """
        self.alpha[context][action] += reward
        self.beta[context][action] += (1 - reward)

    def get_expected_values(self):
        """
        Computes the expected values based on current Beta distribution parameters.
        
        Returns:
        np.ndarray: Expected values for each action in each context.
        """
        return self.alpha / (self.alpha + self.beta)
    
    def save_params(self, file_path):
        """
        Saves the current Beta distribution parameters to a file.
        
        Parameters:
        - file_path (str): The path of the file to save the parameters.
        """
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'wb') as f:
            pickle.dump((self.alpha, self.beta), f)

    def load_params(self, file_path):
        """
        Loads Beta distribution parameters from a file.
        
        Parameters:
        - file_path (str): The path of the file from which to load the parameters.
        """
        with open(file_path, 'rb') as f:
            self.alpha, self.beta = pickle.load(f)

if __name__ == "__main__":
    # Sample code to test the functionality of ContextualThompsonSamplingAgent
    n_actions = 7
    n_context = 3

    agent_CTS = ContextualThompsonSamplingAgent(n_actions=n_actions, n_contexts=n_context)
    agent_CTS.initialize(n_contexts=n_context, n_actions=n_actions)
    print(f"agent_CTS: {agent_CTS}")
