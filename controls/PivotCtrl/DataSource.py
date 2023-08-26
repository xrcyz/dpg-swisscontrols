import random
from typing import Dict

import pandas as pd
import numpy as np

from controls.PivotCtrl.PivotField import PivotField, PivotFieldType

def get_field_data() -> Dict[str, PivotField]:
    return {
        'Year': PivotField('Year', PivotFieldType.GroupBy.ORDINAL),
        'Quarter': PivotField('Quarter', PivotFieldType.GroupBy.ORDINAL),
        'Fruit': PivotField('Fruit', PivotFieldType.GroupBy.CATEGORY),
        'Shape': PivotField('Shape', PivotFieldType.GroupBy.CATEGORY),
        'Vibe': PivotField('Vibe', PivotFieldType.GroupBy.CATEGORY),
        'Weight': PivotField('Weight', PivotFieldType.Aggregate.SUM),
        'Volume': PivotField('Volume', PivotFieldType.Aggregate.SUM),
        'Price/kg': PivotField('Price/kg', PivotFieldType.Aggregate.WEIGHTED_AVERAGE, weight_field='Weight'),
    }

    

def get_flat_data():
    # Number of rows to generate
    n_rows = 10

    # Random fruits
    vibe = random.choices(["Relaxing", "Ambient", "Chill", "Flawless"], k=n_rows)
    fruits = random.choices(["Apple", "Pear", "Cherry", "Fig", "Banana"], k=n_rows)
    grade = random.choices(["Round", "Square", "Star", "Cone", "Torus"], k=n_rows)

    # Random years and months
    years = random.choices([2022, 2023, 2024, 2025, 2026, 2027], k=n_rows)
    quarters = random.choices(np.arange(1,5), k=n_rows)

    # Random weights and volumes
    weights = np.random.rand(n_rows)
    volumes = np.random.rand(n_rows)
    price = np.random.rand(n_rows)

    # Create DataFrame
    df = pd.DataFrame({
        'Year': years,
        'Quarter': quarters,
        'Fruit': fruits,
        'Shape': grade,
        'Vibe': vibe,
        'Weight': weights,
        'Volume': volumes,
        'Price/kg': price,
    })

    return df

def get_pivot_data():

    """
    Returns a dataframe like this.
    Fruit           Apple               Cherry              Pear
                    Volume    Weight    Volume    Weight    Volume    Weight
    Year    Month
    2022    1       6.896494  7.042704  4.536400  5.091052  7.183056  6.905257
            2       3.416444  4.850913  1.073033  2.000163  6.995971  7.126390
    2023    1       2.007010  2.951129  2.415113  1.579377  5.249216  3.125248
            2       2.164300  3.162353  1.964546  2.241498  6.641311  7.045404
    """

    # Create DataFrame
    df = get_flat_data()

    # Perform groupby, sum and unstack operations
    df_grouped = (df.groupby(['Fruit', 'Shape', 'Year', 'Quarter'])
                  .sum(numeric_only=True)
                  .unstack(['Fruit', 'Shape'])
                  .reorder_levels([1, 2, 0], axis=1)
                  .sort_index(axis=1)
                  .fillna(0)
    )
    df_grouped.columns.names = ['Fruit', 'Field', 'Shape']
    return df_grouped

