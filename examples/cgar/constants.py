AIRLINES = ['Finnair']

AIRLINES_DATA = {'Finnair': {'crew_budget': 1e10, 'hub': ['Helsinki']}}

OPERATING_COSTS = {
    'DH8D': {
        'standard': 922,
        'ground': 540,
        'copy': 1630
    },
    'JS32': {
        'standard': 2887,
        'ground': 540,
        'copy': 1630
    },
    'A319': {
        'standard': 9734,
        'ground': 810,
        'copy': 3420
    },
    'A320': {
        'standard': 9734,
        'ground': 900,
        'copy': 3490
    },
    'B738': {
        'standard': 10430,
        'ground': 1010,
        'copy': 3650
    },
    'B752': {
        'standard': 10430,
        'ground': 720,
        'copy': 4210
    },
    'A359': {
        'standard': 13912,
        'ground': 1050,
        'copy': 4130
    },
    'B77L': {
        'standard': 13912,
        'ground': 1310,
        'copy': 6230
    },
}

MIN_MAINT = 2
CREW_COST = {0: 477, 1: 750, 2: 1356, 'wait': 100}
PENALTY = 10
CREW_REST = 1  # 1 hour rest minimum
MAX_CREWD1 = 24
MAX_CREWD2 = 12
