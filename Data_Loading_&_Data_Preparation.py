import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set visualization style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)

# ✅ Your CSV file path
FILE_PATH = r"SkyCity Auckland Restaurants & Bars.csv"

# Load data
def load_data(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f'CSV file not found: {filepath}')
    return pd.read_csv(filepath)

# Data validation and cleaning
def validate_data(df):
    print('Missing Values:')
    print(df.isnull().sum())

    channels = ['InStore', 'UberEats', 'DoorDash', 'SelfDelivery']

    for channel in channels:
        orders_col = f'{channel}OrdersCount'
        profit_col = f'{channel}NetProfit'

        if orders_col in df.columns and profit_col in df.columns:
            df[f'{channel}_ProfitPerOrder'] = np.where(
                df[orders_col] > 0,
                df[profit_col] / df[orders_col],
                0
            )

    return df

# Main execution
if __name__ == '__main__':
    try:
        df = load_data(FILE_PATH)
        df = validate_data(df)

        print('\nSample data:')
        print(df.head())

    except FileNotFoundError as exc:
        print(exc)

    except pd.errors.EmptyDataError:
        print(f'Error: file is empty or not a valid CSV: {FILE_PATH}')

    except Exception as exc:
        print(f'Unexpected error: {exc}')