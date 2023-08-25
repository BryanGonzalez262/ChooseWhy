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
    'omission_conjunction': [
        "In this study, you will be observe a series of winning players' lottery outcomes.",
        "The rules of the lottery are as follows: \nA player draws one ball from each of two different jars, A & B.",
        "In order to win the lottery, BOTH of the following must occur: \n - The player must NOT draw a red ball from jar A \n AND \n  - The player must draw a red ball from jar B",
        "Here, a player did NOT draw a red ball from jar A, AND the player drew a red ball from jar B, so they won the lottery",
        "Here, a player drew a red ball from jar B, but did not succeed in NOT drawing a red ball from jar A, so they did not win the lottery.",
        "Here, a player <i>did</i> succeed in NOT drawing a red ball from jar A, but did not draw a red ball from jar B, so they did not win the lottery.",
        "After observing a lottery outcome, you will also be shown the chances of a player drawing a red ball from each individual jar.",
        "After observing the draw, your task is to use what you know about the lottery to indicate how much you think each jar was responsible for the final outcome.",
        "After each trial, you will be asked about a specific jar you observed in the preceding trial. Do your best to pay attention",
        "Let's make sure you understand these instructions..."
    ]
}


instruction_img = {
    'pure_disjunction': {
        'im1': 'static/stim/instructions/jars.png',
        'im2': 'static/stim/instructions/rrb.gif',
        'im3': 'static/stim/instructions/bbb.gif',
        'im4': None,
        'im5': None
    },
    'mixed_conjunction': {
        'im1': 'static/stim/instructions/jars.png',
        'im2': 'static/stim/instructions/rrb.gif',
        'im3': 'static/stim/instructions/brb.gif',
        'im4': None,
        'im5': 'static/stim/instructions/mix_conj.png'
    },
    'mixed_disjunction': {
        'im1': 'static/stim/instructions/jars.png',
        'im2': 'static/stim/instructions/rrb.gif',
        'im3': 'static/stim/instructions/brr.gif',
        'im4': 'static/stim/instructions/brb.gif',
        'im5': 'static/stim/instructions/mix_disj.png'
    },
    'omission_conjunction': {
        'im1': 'static/stim/instructions/jarsab.png',
        'im2': 'static/stim/instructions/br.gif',
        'im3': 'static/stim/instructions/rr.gif',
        'im4': 'static/stim/instructions/bb.gif',
        'im5': 'static/stim/instructions/omit_conj.png'
    }
}



# check VPN
def check_client_net():
    api = app.config.get("NETWORK_CHECKER_KEY")
    ip_addy = "2603:7000:a000:1a58:6cba:3bf7:c12e:225d" #request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    response = requests.get("https://vpnapi.io/api/" + ip_addy + "?key=" + api)
    data = json.loads(response.text)
    if sum(data["security"].values()) > 0:
        print("Someone is attempting to access through hidden network. ")
        return True
    else:
        return False