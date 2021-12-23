from .nlp_parser import Rule   

L = 'Left'
R = 'Right'
leftarcs = {
    ('TRAIN-N', 'ARRIVE-V'): Rule('nsubj', L),
    ('TRAIN-N', 'TRAIN-V'): Rule('nsubj', L),
    ('FROM', 'CITY-NAME'): Rule('case-d', L),
    ('TO', 'CITY-NAME'): Rule('case-a', L),
    ('AT', 'TIME-MOD'): Rule('case-t', L),
    ('AT', 'TIME-MOD-WH'): Rule('case-t-wh', L),
    ('IS', 'TIME-MOD-WH'): Rule('is', L),
    ('AUX', 'TRAIN-V'): Rule('advmod', L),
    ('AUX', 'ARRIVE-V'): Rule('advmod', L),
    ('TIME-N', 'TRAIN-N'): Rule('nmod', L),
    ('CITY-N', 'CITY-NAME'): Rule('nmod', L)
}
rightarcs = {
    ('ROOT','ARRIVE-V'): Rule('ROOT', R),
    ('ROOT','TRAIN-V'): Rule('ROOT', R),
    ('TRAIN-N', 'DET'): Rule('det-wh', R),
    ('ARRIVE-V', 'CITY-NAME'): Rule('dobj-a', R),
    ('TRAIN-V', 'CITY-NAME'): Rule('obl', R),
    # Time
    ('ARRIVE-V', 'TIME-MOD'): Rule('obl', R),
    ('TRAIN-V', 'TIME-MOD'): Rule('obl', R),
    ('ARRIVE-V', 'TIME-MOD-WH'): Rule('obl', R),
    ('TRAIN-V', 'TIME-MOD-WH'): Rule('obl', R),
    # Train name
    ('TRAIN-N', 'TRAIN-NAME'): Rule('namemod', R),
    # Yes/No
    ('ARRIVE-V', 'AUX-END'): Rule('advmod', R),
    ('TRAIN-V', 'AUX-END'): Rule('advmod', R),

    ('ARRIVE-V','QUESTION'): Rule('punct', R),
    ('TRAIN-V','QUESTION'): Rule('punct', R),
}