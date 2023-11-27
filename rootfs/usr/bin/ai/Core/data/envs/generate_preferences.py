import random
import json

"""
This is the second version of generating user preference, the user has multiple/one/zero, overlapped, preferred signal for each meal.
This script is mainly used in the experiment 8, user type A, B, C, D.

Ruth: Personally I think that user C with a single signal has the most chance to be the more average person with dementia. Because repetition is the best method to learn new things for people with dementia.  

Experiment purpose: We want to know if the algorithm can adapt to different user types.

"""

def generate_preferences(user_type):
    signals = ["music", "smell", "light", "image", "voice", "video"]
    no_preference = ["UNK"]
    
    user_preferences = {
        "breakfast": [],
        "lunch": [],
        "dinner": []
    }

    for meal in user_preferences:
        if user_type["breakfast"] == user_type["lunch"] == user_type["dinner"] == 1:  # user_type_C
            p_signal = random.sample(signals, user_type[meal])
            user_preferences["breakfast"] = p_signal
            user_preferences["lunch"] = p_signal
            user_preferences["dinner"] = p_signal
        else:
            if user_type[meal] != 0:
                p_signal = random.sample(signals, user_type[meal])
                user_preferences[meal] = p_signal
            else: 
                user_preferences[meal] = no_preference

    return user_preferences

def save_to_json(user_preferences, json_filename):
    with open(json_filename, 'w') as json_file:
        json.dump(user_preferences, json_file, indent=4)


if __name__ == "__main__":
    user_type_A = {
        "breakfast": 2,
        "lunch": 1,
        "dinner": 0
    }

    user_type_B = {
        "breakfast": 2,
        "lunch": 2,
        "dinner": 3
    }

    user_type_C = {
        "breakfast": 1,
        "lunch": 1,
        "dinner": 1
    }

    user_type_D = {
        "breakfast": 0,
        "lunch": 0,
        "dinner": 0
    }

    # user_preferences = generate_preferences(user_type_A)
    # user_preferences = generate_preferences(user_type_B)
    user_preferences = generate_preferences(user_type_C)
    # user_preferences = generate_preferences(user_type_D)

    json_filename = './data/envs/user_preferences.json'
    save_to_json(user_preferences, json_filename)