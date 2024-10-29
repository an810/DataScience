import csv
import re

def clean_text(text):
    # Loại bỏ các ký tự xuống dòng thừa và các ký tự space thừa
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def clean_csv(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Đọc và ghi header
        headers = next(reader)
        writer.writerow(headers)

        # Đọc và làm sạch từng dòng dữ liệu
        for row in reader:
            cleaned_row = [clean_text(cell) for cell in row]
            writer.writerow(cleaned_row)

# Sử dụng hàm
input_file = '../data/topcv.vn_data.csv'
output_file = '../data/cleaned_data.csv'
clean_csv(input_file, output_file)