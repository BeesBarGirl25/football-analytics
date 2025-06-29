import pandas as pd
from .unified_heatmap import generate_heatmap


def generate_team_match_heatmap(match_data: pd.DataFrame, half: str = "full") -> dict:
    """
    Generate team possession heatmap using the unified heatmap function.
    
    This function maintains backward compatibility while using the consolidated logic.
    """
    return generate_heatmap(match_data, 'possession', half)

def generate_team_attack_heatmap(match_data: pd.DataFrame, half: str = "full") -> dict:
    """
    Generate team attack heatmap using the unified heatmap function.
    
    This function maintains backward compatibility while using the consolidated logic.
    """
    return generate_heatmap(match_data, 'attack', half)

def generate_team_defense_heatmap(match_data: pd.DataFrame, half: str = "full") -> dict:
    """
    Generate team defense heatmap using the unified heatmap function.
    
    This function maintains backward compatibility while using the consolidated logic.
    """
    return generate_heatmap(match_data, 'defense', half)