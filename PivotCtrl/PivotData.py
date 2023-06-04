import pandas as pd
import numpy as np
import random


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

    # Number of rows to generate
    n_rows = 100

    # Random fruits
    coord = random.choices(["X", "Y", "Z"], k=n_rows)
    fruits = random.choices(["Apple", "Pear"], k=n_rows)
    grade = random.choices(["A", "B"], k=n_rows)

    # Random years and months
    years = random.choices([2022, 2023], k=n_rows)
    quarters = random.choices(np.arange(1,5), k=n_rows)

    # Random weights and volumes
    weights = np.random.rand(n_rows)
    volumes = np.random.rand(n_rows)

    # Create DataFrame
    df = pd.DataFrame({
        'Fruit': fruits,
        # 'Coord': coord,
        'Grade': grade,
        'Year': years,
        'Quarter': quarters,
        'Weight': weights,
        'Volume': volumes
    })

    # Perform groupby, sum and unstack operations
    df_grouped = (df.groupby(['Fruit', 'Grade', 'Year', 'Quarter'])
                  .sum(numeric_only=True)
                  .unstack(['Fruit', 'Grade'])
                  .reorder_levels([1, 2, 0], axis=1)
                  .sort_index(axis=1)
                  .fillna(0)
    )
    df_grouped.columns.names = ['Fruit', 'Field', 'Grade']
    return df_grouped

