import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

def extract_number_from_string(s):
    # Replace commas with dots and filter out non-digit characters
    cleaned_s = ''.join(filter(lambda x: x.isdigit() or x == '.', s.replace(',', '.')))
    return cleaned_s


def scrape_data(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    html_content = driver.page_source

    data = {
        "Tên": "",
        "Diện tích": "",
        "Mặt tiền": "",
        "Mức giá": "",
        "Hướng nhà": "",
        "Số phòng ngủ": "",
        "Số toilet": "",
        "Nội thất": "",
        "Pháp lý": "",
        "lat": "",
        "lon": "",
        "Địa chỉ": "",
        "Quận": "",
        "Thành phố": ""
    }

    soup = BeautifulSoup(html_content, 'html.parser')

    address = soup.find('span', class_='re__pr-short-description js__pr-address')
    data["Địa chỉ"] = address.text

    # Get tọa độ
    data_src_value = soup.find('div', class_='re__section re__pr-map js__section js__li-other').find('iframe')['data-src']
    match = re.search(r'q=([-+]?\d*\.\d+),([-+]?\d*\.\d+)', data_src_value)
    if match:
        # Tọa độ lat, lon
        data["lat"] = match.group(1)
        data["lon"] = match.group(2)


    tabs = soup.find_all('a', class_='re__link-se')
    if tabs:
        for tab in tabs:
            level_value = tab.get('level')
            if level_value == "2":
                data["Thành phố"] = tab.text.strip()
            if level_value == "3":
                data["Quận"] = tab.text.strip()
            if level_value == "4":
                data["Tên"] = tab.text.strip()
    else:
        driver.quit()
        return None

    section_body = soup.find('div', class_='re__pr-specs-content js__other-info')

    if section_body:
        specs_items = section_body.find_all('div', class_='re__pr-specs-content-item')

        for item in specs_items:
            title = item.find('span', class_='re__pr-specs-content-item-title').text.strip()
            value = item.find('span', class_='re__pr-specs-content-item-value').text.strip()

            # Kiểm tra xem title có trong data không trước khi thêm vào
            if title in data:
                data[title] = value

    else:
        driver.quit()
        return None

    # Đóng trình duyệt
    driver.quit()

    return data

if __name__ == "__main__":
    # Gọi hàm scrape_data với URL nhận được
    scraped_data = scrape_data("https://batdongsan.com.vn/ban-nha-mat-pho-duong-nguyen-xien-xa-tan-trieu-prj-rue-de-charme/chinh-chu-ban-luong-the-vinh-pr37988329")

    # In ra kết quả hoặc làm gì đó với dữ liệu scrape được
    print(scraped_data)
