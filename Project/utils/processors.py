from bs4 import BeautifulSoup
from bs4.element import Tag

from Project.utils.send_requests import send_request

USD_TO_VND = 24000


class JobProcessor():
    def process_job(self, url: str, pause_between_jobs: int = 3):
        print("Scraping job info at", url)

        response = send_request("get", url)
        soup = BeautifulSoup(response.content, "html.parser")

        # job_id, job_title, company
        job_id = self._process_job_id(url)
        title_tag = soup.find("div", class_="apply-now-content")
        job_title = title_tag.find("h1", class_="title").text.strip("\n")
        company_tag = title_tag.find("a", class_="job-company-name")
        if company_tag:
            company = company_tag.text.strip("\n")
        else:
            company = "Unknown"

        # salary, yrs_of_exp, job_city, due_date
        detail_tags = soup.find_all("div", class_="detail-box")
        job_city_tag = detail_tags[0].find("a")
        job_city = job_city_tag.text.strip("\n")

        detail_box_tags = detail_tags[2].find_all("li")
        salary_tag = detail_box_tags[0].find("p")
        salary_min, salary_max = self._process_salary(salary_tag)
        if len(detail_box_tags) == 4:
            xp_tag = detail_box_tags[1].find("p")
            yrs_of_exp_min, yrs_of_exp_max = self._process_xp(xp_tag)
            due_tag = detail_box_tags[3].find("p")
        else :
            level_tag = detail_box_tags[1].find("p")
            level = level_tag.text.strip("\n")
            if level == "Mới tốt nghiệp":
                yrs_of_exp_min, yrs_of_exp_max = 0, 0
            else:
                yrs_of_exp_min, yrs_of_exp_max = None, None
            due_tag = detail_box_tags[2].find("p")

        day, month, year = due_tag.text.split(":")[-1].strip("").strip("\n").strip("\n").strip().replace("-",
                                                                                                         "/").split("/")
        due_date = f"{year}/{month}/{day}"  # due_tag.text.split(":")[1].strip()[::-1].replace("-", "/") # datetime.strptime(date_str, "%d/%m/%Y")

        # jd, req, benefits, location, other_info
        detail_row_tags = soup.find_all("div", class_="detail-row")
        benefit_tag = detail_row_tags[0]
        jd_tag = detail_row_tags[1]
        req_tag = detail_row_tags[2]
        if len(detail_row_tags) == 6:
            location_tag = detail_row_tags[3]
            other_info_tag = detail_row_tags[4]
        else:
            location_tag = None
            other_info_tag = detail_row_tags[3]

        benefit_li_tags = benefit_tag.find_all("li")
        # print("benefit_li_tags:", benefit_li_tags)
        benefits = ",".join([li.text.strip() for li in benefit_li_tags])

        jd = jd_tag.text.strip("\n").replace("\n", " ")
        req = req_tag.text.strip("\n").replace("\n", " ")

        if location_tag:
            location = location_tag.text.strip().replace("\n", "").replace("\r", "").replace("\t", "")
        else:
            location = None
        other_info = other_info_tag.text.strip().replace("\n", "").replace("\r", "").replace("\t", "")

        return {
            "job_id": job_id,
            "job_title": job_title,
            "company": company,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "yrs_of_exp_min": yrs_of_exp_min,
            "yrs_of_exp_max": yrs_of_exp_max,
            "job_city": job_city,
            "due_date": due_date,
            "job_details": jd,
            "job_requirements": req,
            "job_benefits": benefits,
            "location": location,
            "other_info": other_info
        }

    def _process_salary(self, salary_tag: Tag):
        salary_str = salary_tag.text.strip("\n").strip()
        min, max = None, None
        if salary_str == "Cạnh tranh":  # Default string for no salary info
            min, max = (None, None)
        else:
            salary_arr = list(
                filter(None, map(lambda x: x.replace(",", "").replace("Tr", "").replace("VND", "").strip(),
                                 salary_str.split(" "))))
            print("salary_arr:",salary_arr)
            if salary_arr[1] == "-":  # Normal range (<min> - <max> <unit>)
                min, max = map(float, (salary_arr[0], salary_arr[2]))
            elif salary_arr[0] == "Trên":  # Above a certain amount
                min, max = float(salary_arr[1]), None
            if salary_arr[-1] == "USD":
                min, max = map(
                    lambda x: int(x) * USD_TO_VND / 10 ** 6 if x != None else None,
                    (min, max)
                )

        return min, max

    def _process_xp(self, xp_tag: Tag):
        # Returns min & max required experience (years)
        xp_str = xp_tag.text.strip()
        xp_arr = list(filter(lambda x: x and x != '\r', xp_str.replace("\n", "").split(" ")))
        print("xp_arr:", xp_arr)
        if xp_str == "Không yêu cầu kinh nghiệm" or xp_str == "Mới tốt nghiệp":
            min, max = 0, 0
        elif xp_arr[0].isnumeric() and len(xp_arr) == 2 and xp_arr[1] == "năm":  # <xp> năm
            min, max = map(int, (xp_arr[0], xp_arr[0]))
        elif xp_arr[1] == "-" and xp_arr[2].isnumeric() and xp_arr[3] == "Năm":  # <min> - <max> Năm
            min, max = map(int, (xp_arr[0], xp_arr[2]))
        elif xp_arr[1].isnumeric() and xp_arr[2] == "Năm":  # Trên/Dưới <xp> năm
            if xp_arr[0] == "Trên":
                min, max = int(xp_arr[1]), None
            elif xp_arr[0] == "Dưới":
                min, max = None, int(xp_arr[1])
        else:
            min, max = None, None

        return min, max

    def _process_job_id(self, url: str) -> str:
        last_part = url.split("/")[-1]
        job_id_str = last_part.split("-")[-1]
        job_id = job_id_str.split(".")[-2]
        return job_id
