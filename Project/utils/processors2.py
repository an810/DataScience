from bs4 import BeautifulSoup
from bs4.element import Tag

from utils.send_requests import send_request

USD_TO_VND = 24000

class JobProcessor():
    def process_job(self, url: str, pause_between_jobs: int = 3):
        print("Scraping job info at", url)

        response = send_request("get", url)
        soup = BeautifulSoup(response.content, "html.parser")

        # job_id, job_title, company
        job_id = self._process_job_id(url)
        title_tag = soup.find("div", class_="sc-8868b866-0 dvidDw")
        job_title = title_tag.find("h1", class_="sc-df6f4dcb-0 bsKseP").text.strip("\n")
        company_tag = soup.find("a", class_="sc-df6f4dcb-0 iNMvve sc-f0821106-0 gWSkfE")
        if company_tag:
            company = company_tag.text.strip("\n")
        else:
            company = "Unknown"

        # salary, yrs_of_exp, job_city, due_date
        salary_tag = soup.find("div", "sc-8868b866-0 lmzgIo")
        salary_min, salary_max = self._process_salary(salary_tag)

        detail_tags = soup.find_all("div", "sc-7bf5461f-2 JtIju")
        xp_tags = detail_tags[6]
        xp_tag = xp_tags.find("p", "sc-df6f4dcb-0 ioTZSy")
        yrs_of_exp = self._process_xp(xp_tag)

        job_city_tag = soup.find("div", "sc-4dcd9b5d-1 sZNRu")
        job_city = job_city_tag.text.strip("\n")

        due_date_tag = soup.find("div", "sc-4dcd9b5d-1 LTCxx")
        due_date = due_date_tag.text.replace("Hết hạn trong ", "").strip("\n")

        # jd, req, benefits, location, other_info
        jd_tags = soup.find_all("div", "sc-4913d170-6 hlTVkb")
        jd = jd_tags[0].text.strip("\n")
        req = jd_tags[1].text.strip("\n")

        benefits_tag = soup.find("div", "sc-b8164b97-0 kxYTHC")
        benefits = benefits_tag.text.strip("\n")

        location_tags = soup.find("div", "sc-a137b890-0 bAqPjv")
        location_tag = location_tags.find_all("p", "sc-df6f4dcb-0 ioTZSy")
        locations = [tag.text.strip("\n") for tag in location_tag]
        location = "; ".join(locations)



        return {
            "job_id": job_id,
            "job_title": job_title,
            "company": company,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "yrs_of_exp": yrs_of_exp,
            "job_city": job_city,
            "due_date": due_date,
            "job_details": jd,
            "job_requirements": req,
            "job_benefits": benefits,
            "location": location,
            # "other_info": other_info
        }

    def _process_salary(self, salary_tag: Tag):
        salary_str = salary_tag.text.strip("\n").strip()

        if salary_str == "Thương lượng":
            return None, None

        salary_str = salary_str.replace(",", "").replace("₫/tháng", "").replace("/tháng", "").strip()
        min, max = None, None

        if "-" in salary_str:
            salary_arr = salary_str.split("-")
            min = float(salary_arr[0].replace("tr", "").replace("$", "").strip())
            max = float(salary_arr[1].replace("tr", "").replace("$", "").strip())
            if "$" in salary_str:
                min *= USD_TO_VND / 10**6
                max *= USD_TO_VND / 10**6
        elif "Tới" in salary_str:
            max = float(salary_str.split(" ")[-1].replace("$", "").strip())
            if "$" in salary_str:
                max *= USD_TO_VND / 10**6
        elif "Từ" in salary_str:
            min = float(salary_str.split(" ")[-1].replace("$", "").strip())
            if "$" in salary_str:
                min *= USD_TO_VND / 10**6

        return min, max

    def _process_xp(self, xp_tag: Tag):
        xp_str = xp_tag.text.strip()
        if xp_str == "Không yêu cầu":
            xp = 0
        else:
            xp = int(xp_str)

        return xp

    def _process_job_id(self, url: str) -> str:
        last_part = url.split("?")[0]
        job_id_str = last_part.split("-")[-2]
        return job_id_str
