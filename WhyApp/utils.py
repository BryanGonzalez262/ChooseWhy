import itertools
from flask import request
import requests
import json
from . import app


# Instructions for different experiments
instruction_text = {
    'pure_conjunction': ["In this study, you will be observe a series of winning players' lottery outcomes.",
            "The rules of the lottery are as follows: A player draws one ball from each of three different jars, A, B, & C.",
            "In order to win the lottery, the player must draw three red balls - one from each of the three jars",
            "Here, a player drew a red ball from jar A, B, & C; so they won the lottery.",
            "Here, a player drew only two red balls, so they did not win the lottery.",
            "Before observing a draw, you will also be shown the chances of a player drawing a red ball from each individual jar.",
            "After observing the draw, your task is to use what you know about the lottery to indicate how much you think each jar was responsible for the final outcome.",
            "Occasionally, you will be asked about a specific jar you observed in the preceeding trial. Do your best to pay attention.",
            "Let's make sure you understand these instructions"],
    'pure_disjunction': ["In this study, you will observe a series of winning players' lottery outcomes.",
                         "The rules of the lottery are as follows: \n A player draws one ball from three different jars, A, B, & C.",
                         "In order to win the lottery, the player must draw AT LEAST ONE red ball from the three jars. So if they draw one or more red balls, they will win",
                         "Here, a player drew a red ball from jar A and jar B, so they won the lottery.",
                         "Here, a player did not draw a red ball from jar A, B or C, so they lost the lottery.",
                         "After observing a lottery outcome, you will also be shown the chances of a player drawing a red ball from each individual jar.",
                         "After observing the draw, your task is to use what you know about the lottery to indicate how much you think each jar was responsible for the final outcome.",
                         "After each trial, you will be asked about a specific jar you observed in the preceding trial. Do your best to pay attention",
                         "Let's make sure you understand these instructions"
                         ],
    'mixed_conjunction': [
        "In this study, you will be observe a series of winning players' lottery outcomes.",
        "The rules of the lottery are as follows: \n  A player draws one ball from each of three different jars, A, B, & C.",
        "In order to win the lottery, the player must draw a red ball from Jar A, and must also draw at least one red ball from Jar B or Jar C. \n \n So if they draw one red ball from Jar A, and one or more red balls from Jar B and C, they will win.",
        "Here, a player drew a red ball from jar A AND a red ball from jar B or C, so they won the lottery.",
        "Here, a player drew a red ball from jar B or jar C, but did not draw a red ball from jar A so they lost the lottery.",
        "After observing a lottery outcome, you will also be shown the chances of a player drawing a red ball from each individual jar.",
        "After observing the draw, your task is to use what you know about the lottery to indicate how much you think each jar was responsible for the final outcome.",
        "After each trial, you will be asked about a specific jar you observed in the preceding trial. Do your best to pay attention",
        "Let's make sure you understand these instructions..."
    ],
    'mixed_disjunction': [
        "In this study, you will be observe a series of winning players' lottery outcomes.",
        "The rules of the lottery are as follows: \n  A player draws one ball from each of three different jars, A, B, & C.",
        "In order to win the lottery, the player must draw a red ball from Jar A, OR must draw a red ball from both Jar B AND Jar C. \n \n So if they draw one red ball from Jar A, OR red balls from both Jar B AND C, they will win.",
        "Here, a player drew a red ball from jar A, so they won the lottery.",
        "Here, a player did not draw a red ball from jar A, but they did draw a red ball from jar B and jar C, so they won the lottery.",
        "Here, a player did not draw a red ball from jar A, they also did not draw a red ball from jar B and jar C, so they lost the lottery.",
        "After observing a lottery outcome, you will also be shown the chances of a player drawing a red ball from each individual jar.",
        "After observing the draw, your task is to use what you know about the lottery to indicate how much you think each jar was responsible for the final outcome.",
        "After each trial, you will be asked about a specific jar you observed in the preceding trial. Do your best to pay attention",
        "Let's make sure you understand these instructions..."
    ],
}


# check VPN
def check_client_net():
    api = app.config.get("NETWORK_CHECKER_KEY")
    ip_addy = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    response = requests.get("https://vpnapi.io/api/" + ip_addy + "?key=" + api)
    data = json.loads(response.text)
    if sum(data["security"].values()) > 0:
        print("Someone is attempting to access through hidden network. ")
        return True
    else:
        return False