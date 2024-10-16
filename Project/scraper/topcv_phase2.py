import concurrent.futures
from selenium.webdriver.chrome.options import Options
import csv

from Project.utils.processors import JobProcessor

def clear_file(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.truncate(0)  # Xóa toàn bộ nội dung của tệp

def write_to_file(data, links, data_file, links_file):
    clear_file(data_file)
    print("Writing data to file")
    with open(data_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(data.keys())

        # Viết các dòng mới vào file
        for i in range(len(data["Job ID"])):
            row_data = [data[key][i] for key in data.keys()]
            print(row_data)
            writer.writerow(row_data)

    print(f"Data has been written to {data_file}")

    clear_file(links_file)
    with open(links_file, 'a', encoding='utf-8') as linksfile:
        for link in links:
            linksfile.write(link + '\n')

    print(f"Links have been written to {links_file}")

def scrape_data():
    links_file_path = "../data/links.txt"
    data_file_path = "../data/topcv.vn_data.csv"
    with open(links_file_path, 'r', encoding='utf-8') as links_file:
        links = links_file.read().splitlines()

    # Đọc dữ liệu hiện có từ tệp
    data = {
        "Job ID": [],
        "Job Title": [],
        "Company": [],
        "Salary min": [],
        "Salary max": [],
        "Years of experience min": [],
        "Years of experience max": [],
        "Location": [],
        "Due date": [],
        "Job Details": [],
        "Requirements": [],
        "Benefits": [],
        "Working Time": [],
    }

    with open(data_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            for key, value in row.items():
                if key not in data:
                    data[key] = []
                data[key].append(value)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    successful_links = set()

    job_processor = JobProcessor()

    def process_link(link):
        url = link
        successful_links.add(url)
        print(f"Scraping link {len(successful_links) + 1}: {url}")
        scraped_data = job_processor.process_job(url, pause_between_jobs=3)
        print(scraped_data)
        if scraped_data:
            for key, value in scraped_data.items():
                if key in data:
                    data[key].append(value)

        if len(successful_links) % 1000 == 0:
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
