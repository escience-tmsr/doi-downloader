import os
import csv


def load_dois_from_file(file_path, column_name="doi", unique=False):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist. Please provide a valid file path.")
    with open(file_path, 'r') as f:
        array = [row['doi'] for row in csv.DictReader(f)]
    if unique:
        return list(set(array))
    else:
        return array


