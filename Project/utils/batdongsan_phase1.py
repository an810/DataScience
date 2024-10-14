from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def clear_file(file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.truncate(0)  # Xóa toàn bộ nội dung của tệp

def scrape_links():
    output_file = "../data/batdongsan.com.vn_links.txt"
    unscraped_links = set()
    with open(output_file, 'r', encoding='utf-8') as existing_links_file:
        existing_links = existing_links_file.read().splitlines()
        unscraped_links.update(existing_links)
    sourceUrl = 'https://batdongsan.com.vn'
    path = "/nha-dat-ban-ha-noi?gtn=7-ty&gcn=30-ty"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    page_index = 0

    while True:
        page_index += 1
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(sourceUrl + path)
        print(sourceUrl + path)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')

        # Tìm tất cả các phần tử <a> với class 'js__product-link-for-product-id'
        links = soup.find_all('a', class_='js__product-link-for-product-id')

        for link in links:
            href = link.get('href')
            unscraped_links.add(sourceUrl + href)

        if page_index % 10 == 0:
            clear_file(output_file)
            with open(output_file, 'a', encoding='utf-8') as linksfile:
                for link in unscraped_links:
                    linksfile.write(link + '\n')
            print(f"Links have been written to {output_file}")

        pagination_links = soup.find_all('a', class_='re__pagination-icon')
        next_page = False

        for link in pagination_links:
            if link.find('i', class_='re__icon-chevron-right--sm'):
                next_page = True
                path = link.get('href')
                break

        if not next_page:
            print("No page found. Process ended.")
            break

        driver.quit()

    clear_file(output_file)
    # Ghi dữ liệu
    with open(output_file, 'w', encoding='utf-8') as linksfile:
        for link in unscraped_links:
            linksfile.write(link + '\n')

    print(f"Links have been written to {output_file}")

if __name__ == "__main__":
    scrape_links()
