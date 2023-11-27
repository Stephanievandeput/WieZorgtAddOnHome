import random

"""
This script is deprecated and will be removed in the future.
"""

class UserBot:
    def __init__(self):
        pass

    def has_eaten_or_not(self, simulation=True, reaction=None):
        """
        Determines if the user has eaten or not.

        :param simulation:
        :param reaction:
        :return:
        """
        has_eaten_or_not_mapping = {
            "reacted": 2,
            "no_reaction": -2,
        }
        if simulation:
            result = random.choice(list(has_eaten_or_not_mapping.keys()))
            score = has_eaten_or_not_mapping[result]
            return score
        else:
            if reaction == True:
                score = has_eaten_or_not_mapping["reacted"]
            else:
                score = has_eaten_or_not_mapping["no_reaction"]
            return score

    def reaction_time(self, simulation=True, reaction_time=None):
        """
        Determines the reaction time of the user.

        :param simulation:
        :param reaction_time:
        :return:
        """
        score = 0
        if simulation:
            reaction_time = random.randint(0, 1800)
        else:
            reaction_time = reaction_time

        if reaction_time is None:
            score = -4
        elif reaction_time <= 10 * 60:
            score = 2
        elif reaction_time > 10 * 60 and reaction_time <= 20 * 60:
            score = 0
        elif reaction_time > 20 * 60 and reaction_time <= 30 * 60:
            score = -2
        else:
            score = -4

        return score
