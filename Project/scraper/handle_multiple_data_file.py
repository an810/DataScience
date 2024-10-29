import csv

def read_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

def write_csv(file_path, data, fieldnames):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def merge_csv(file1, file2, output_file):
    data1 = read_csv(file1)
    data2 = read_csv(file2)

    # Merge data and remove duplicates
    combined_data = {tuple(row.items()): row for row in data1 + data2}.values()

    # Convert dict_values to list
    combined_data = list(combined_data)

    # Write the merged data to the output file
    if combined_data:
        fieldnames = combined_data[0].keys()
        write_csv(output_file, combined_data, fieldnames)

file1 = '../data/test_data.csv'
file2 = '../data/cleaned_data.csv'
output_file = '../data/final_data.csv'

merge_csv(file1, file2, output_file)