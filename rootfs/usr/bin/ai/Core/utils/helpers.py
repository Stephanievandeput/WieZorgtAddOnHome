import json
import os
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import pprint as pp

def load_actions():
    # action list has to be fix
    actions_path = "./Core/data/envs/actions.json"  
    with open(actions_path, 'r') as json_file:
        actions = json.load(json_file)
    return actions

def load_json(data_path, file):
    """
    Load a json file

    :param data_path:
    :param file:
    :return:
    """
    f = open(f"{data_path}{file}")
    file = json.load(f)
    return file

def write_json(file_name, data):
    """
    Write a dictionary to a json file

    :param file_name:
    :param data:
    :return:
    """
    with open(f"{file_name}.json", "w") as file:
        json.dump(data, file, indent=4)


def write_file(file_path, dictionary):
    """
    Write a dictionary to a file

    :param file_path:
    :param dictionary:
    :return:
    """
    with open(file_path, "w") as file:
        file.write(dictionary)

def load_rewards():
    """
    Load the rewards

    :return:
    """
    # Define the path to the rewards JSON file
    rewards_path = "./Core/data/env/rewards.json"

    # Load the rewards list from the JSON file
    if os.path.exists(rewards_path):
        with open(rewards_path, "r") as f:
            rewards = json.load(f)
    else:
        rewards = []

    return rewards

def save_rewards(rewards):
    """
    Save the rewards

    :return:
    """
    # Save the updated rewards list to the JSON file
    rewards_path = "./Core/data/envs/rewards.json"
    with open(rewards_path, "w") as f:
        json.dump(rewards, f)


def save_model(agent, agent_name):
    """
    Save the model

    :return:
    """
    model_dir = "./models"
    os.makedirs(model_dir, exist_ok=True)
    agent.save_params(f"{model_dir}/{agent_name}.pkl")

def plotly_average_rewards(env_name, agent_name, average_rewards, std_dev_rewards):
    # Create a plot using Plotly
    fig = go.Figure()

    # Add line for average rewards
    fig.add_trace(go.Scatter(x=list(range(len(average_rewards))), y=average_rewards, mode='lines', name='Average Rewards'))

    # Add shadow for standard deviation
    fig.add_trace(go.Scatter(
        x=list(range(len(average_rewards))) + list(reversed(range(len(average_rewards)))),
        y=list(average_rewards + std_dev_rewards) + list(reversed(average_rewards - std_dev_rewards)),
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Standard Deviation'
    ))

    # Update layout for better visualization
    fig.update_layout(
        title='Average Rewards with Standard Deviation Shadow',
        xaxis_title='Trial',
        yaxis_title='Average Rewards',
        template='plotly'
    )

    save_path = "./figures/"
    save_path = f"{save_path}{env_name}/{agent_name}"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    pio.write_html(fig, file=f"{save_path}/average_rewards.html", auto_open=False)


def plotly_rolling_average_rewards(env_name, agent_name, average_rewards, rolling_avg_rewards, rolling_std_dev_rewards, window_size):
    # Define x-axis
    x = np.arange(window_size - 1, len(average_rewards))

    # Create the plotly figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=rolling_avg_rewards,
                        mode='lines',
                        name='Rolling Average Rewards'))
    fig.add_trace(go.Scatter(x=x, y=rolling_avg_rewards + rolling_std_dev_rewards,
                        fill=None,
                        mode='lines',
                        line_color='rgba(255,165,0,0.3)',
                        name='Upper Bound'))
    fig.add_trace(go.Scatter(x=x, y=rolling_avg_rewards - rolling_std_dev_rewards,
                        fill='tonexty',
                        mode='lines',
                        line_color='rgba(255,165,0,0.3)',
                        name='Lower Bound'))

    fig.update_layout(
        title="Rolling Average Rewards with Standard Deviation Shadow",
        xaxis_title="Trials",
        yaxis_title="Rolling Average Rewards",
        template='ggplot2'
    )

    save_path = "./figures/"
    save_path = f"{save_path}{env_name}/{agent_name}"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    pio.write_html(fig, file=f"{save_path}/rolling_average_rewards.html", auto_open=False)

def write_stimuli_combination(scenario_dict, next_meal_secenario, mapping, meal_type):
    """
    This function writes the stimuli combination to the scenario_dict

    :param scenario_dict:
    :param top_3_reminders:
    :param mapping:
    :return:
    """
    for num, action_combination in enumerate(next_meal_secenario):
        scenario_dict["stages"][num]["stimuli_combination"] = [action_combination]

    # for num, action_combination in enumerate(next_secenario):
    #     # Wendy: you still have to update this part if you want to use more stimuli per stage
    #     scenario_dict["stages"][num]["stimuli_combination"] = [action_combination]

        # I'm using the stimuli_combination above to add the correct stimuli scripts
        scenario_dict["stages"][num]["stimuli_scripts"] = []

        # add the correct stimuli scripts, first try to see if stimuli exists in the meal_type mapping, if not use the default mapping
        for stimuli in scenario_dict["stages"][num]["stimuli_combination"]:
            if meal_type in mapping and stimuli in mapping[meal_type]:
                scenario_dict["stages"][num]["stimuli_scripts"].append(mapping[meal_type][stimuli])
            elif stimuli in mapping["default"]:
                scenario_dict["stages"][num]["stimuli_scripts"].append(mapping["default"][stimuli])

    return scenario_dict


if __name__ == "__main__":
    ha_output_templates = {}
    contexts = ["breakfast", "lunch", "dinner"]
    static_data_path = "data/envs/"

    for key in contexts:
        ha_output_templates[key] = load_json(static_data_path, f"AI_HA_{key}.json")

    pp.pprint(ha_output_templates)

    # scenario_dict = 
    # meal_type
    # top_3_reminders = ["r1", "r2", "r3]
    # mapping
    # write_stimuli_combination(scenario_dict, meal_type, top_3_reminders, mapping)