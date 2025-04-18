import pandas as pd
from statsbombpy import sb

def get_all_competitions():
    df = sb.competitions()
    return df