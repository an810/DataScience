import time
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import scrapeBatdongsan

def clear_file(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.truncate(0)  # Xóa toàn bộ nội dung của tệp

def write_to_file(data, links, data_file, links_file):
    clear_file(data_file)
    with open(data_file, 'a', newline='', encoding='utf-8') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')

        writer.writerow(data.keys())

        # Viết các dòng mới vào file
        for i in range(len(data["Tên"])):
            row_data = [data[key][i] for key in data.keys()]
            writer.writerow(row_data)

    print(f"Data has been written to {data_file}")

    clear_file(links_file)
    with open(links_file, 'a', encoding='utf-8') as linksfile:
        for link in links:
            linksfile.write(link + '\n')

    print(f"Links have been written to {links_file}")

def scrape_data():
    links_file_path = "../data/batdongsan.com.vn_links.txt"
    data_file_path = "../data/batdongsan.com.vn_data.tsv"
    with open(links_file_path, 'r', encoding='utf-8') as links_file:
        links = links_file.read().splitlines()

    # Đọc dữ liệu hiện có từ tệp
    data = {
        "Tên": [],
        "Diện tích": [],
        "Mặt tiền": [],
        "Mức giá": [],
        "Hướng nhà": [],
        "Số phòng ngủ": [],
        "Số toilet": [],
        "Nội thất": [],
        "Pháp lý": [],
        "lat": [],
        "lon": [],
        "Địa chỉ": [],
        "Quận": [],
        "Thành phố": []
    }

    with open(data_file_path, 'r', newline='', encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            for key, value in row.items():
                if key not in data:
                    data[key] = []
                data[key].append(value)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    successful_links = set()

    def process_link(link):
        url = link
        successful_links.add(url)
        print(f"Scraping link {len(successful_links) + 1}: {url}")
        scraped_data = scrapeBatdongsan.scrape_data(url)
        if scraped_data:
            for key, value in scraped_data.items():
                if key in data:
                    data[key].append(value)

        if len(successful_links) % 100 == 0:
            unscraped_links = [link for link in links if link not in successful_links]
            write_to_file(data, unscraped_links, data_file_path, links_file_path)

    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        futures = [executor.submit(process_link, link) for link in links]
    concurrent.futures.wait(futures)

    links = [link for link in links if link not in successful_links]
    write_to_file(data, links, data_file_path, links_file_path)

    print(f"All data has been written")

if __name__ == "__main__":
    scrape_data()
