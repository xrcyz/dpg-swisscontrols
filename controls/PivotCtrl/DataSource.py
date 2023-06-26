import random
from typing import Dict

import pandas as pd
import numpy as np

from PivotFields import PivotField, PivotFieldTypes

def get_field_data() -> Dict[str, PivotField]:
    return {
        'Year': PivotField('Year', PivotFieldTypes.GroupBy.GROUPBY),
        'Quarter': PivotField('Quarter', PivotFieldTypes.GroupBy.GROUPBY),
        'Fruit': PivotField('Fruit', PivotFieldTypes.GroupBy.GROUPBY),
        'Shape': PivotField('Shape', PivotFieldTypes.GroupBy.GROUPBY),
        'Vibe': PivotField('Vibe', PivotFieldTypes.GroupBy.GROUPBY),
        'Weight': PivotField('Weight', PivotFieldTypes.Aggregate.SUM),
        'Volume': PivotField('Volume', PivotFieldTypes.Aggregate.SUM),
        'Price/kg': PivotField('Price/kg', PivotFieldTypes.Aggregate.WEIGHTED_AVERAGE, weight_field='Weight'),
    }

    

def get_flat_data():
    # Number of rows to generate
    n_rows = 100

    # Random fruits
    vibe = random.choices(["High", "Low"], k=n_rows)
    fruits = random.choices(["Apple", "Pear"], k=n_rows)
    grade = random.choices(["Round", "Square"], k=n_rows)

    # Random years and months
    years = random.choices([2022, 2023], k=n_rows)
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

