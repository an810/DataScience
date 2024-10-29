from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def clear_file(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.truncate(0)  # Xóa toàn bộ nội dung của tệp

def scrape_links():
    output_file = "../data/vietnamworks_links.txt"
    unscraped_links = set()
    with open(output_file, 'r', encoding='utf-8') as existing_links_file:
        existing_links = existing_links_file.read().splitlines()
        unscraped_links.update(existing_links)

    base_url = "https://www.vietnamworks.com/viec-lam?g=5&page="

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    page_index = 1

    while page_index <= 10:
        url_path = base_url + str(page_index)
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url_path)
        print(url_path)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        jobs_in_page = soup.find_all("div", "sc-eBfVOF bpNIXv")

        for job in jobs_in_page:
            job_link = job.find("a", target="_blank")["href"]
            unscraped_links.add(job_link)

        clear_file(output_file)
        with open(output_file, 'a', encoding='utf-8') as linksfile:
            for link in unscraped_links:
                linksfile.write(link + '\n')
        print(f"Links have been written to {output_file}")

        page_index += 1
        driver.quit()

    print("Page finished. Crawl ended.")
    clear_file(output_file)
    with open(output_file, 'w', encoding='utf-8') as linksfile:
        for link in unscraped_links:
            linksfile.write(link + '\n')

    print(f"Links have been written to {output_file}")

if __name__ == "__main__":
    scrape_links()