import pandas as pd


def validate_array(array, required_columns):
    for i, row in enumerate(array):
        missing = [col for col in required_columns if col not in row]
        if missing:
            raise ValueError(f"Item number {i} is missing required keys: {missing}")
