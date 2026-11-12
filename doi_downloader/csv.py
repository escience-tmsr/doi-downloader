import csv
import os


def load_dois_from_file(file_path, column_name="doi", unique=False):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist. Please provide a valid file path.")
    with open(file_path, "r") as f:
        try:
            array = [row[column_name] for row in csv.DictReader(f)]
        except KeyError:
            print("The specified DOI column name is not present in the CSV file.")
            return []
    if unique:
        return list(set(array))
    else:
        return array
