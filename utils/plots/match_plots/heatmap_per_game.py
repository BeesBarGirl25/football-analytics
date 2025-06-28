import pandas as pd
from .unified_heatmap import generate_heatmap, _generate_pitch_shapes_vertical


def generate_dominance_heatmap_json(match_data: pd.DataFrame, half: str = "full") -> dict:
    """
    Generate dominance heatmap using the unified heatmap function.
    
    This function maintains backward compatibility while using the consolidated logic.
    """
    return generate_heatmap(match_data, 'dominance', half)
