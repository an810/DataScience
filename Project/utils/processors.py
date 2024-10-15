from typing import override
from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import date, datetime, timedelta
from time import sleep
from Project.utils.send_requests import send_request

USD_TO_VND = 24000

class JobProcessor():
    """
    Base class for processors of job details page from given URL.
    Main entrypoint for job page processing applications.
    Can handle different site templates.
    """

    def process_job(self, url: str, pause_between_jobs: int = 3):
        """
        Parse URL to find job detail page template based on first-level subdirectory

        Arguments:
            url [str]: URL of job detail page.
            pause_between_jobs [int]: Seconds between each request
                to get job detail page.

        Returns:
            job_item [dict]: Processed data.

        Usage: To scrape a job detail page onto job_item:
            job_item = Processor().process_job(<job_detail_url>)
        """
        print("Scraping job info at", url)

        # Parse URL and get keyword
        keyword = url.strip("https://www.").split("/")[1]
        keyword_map = {
            "viec-lam": _NormalJobProcessor(),
            "brand": _BrandJobProcessor()
        }

        # Instantiate suitable processor based on URL keyword
        try:
            processor = keyword_map[keyword]
        except KeyError:
            raise ValueError("Strange URL syntax detected. \
Wrong URL input or parsing for this page has not been implemented.")

        # Process job based on newly assigned processor
        sleep(pause_between_jobs)
        return processor.process_job(url)

    def _process_salary(self, salary_tag: Tag):
        """
        Parse salary tag into integer salary range (in million VND).
        Detects USD and convert to million VND.
        """
        salary_str = salary_tag.text.strip("\n").strip()
        print(salary_str)

        if salary_str == "Thoả thuận":  # Default string for no salary info
            min, max = (None, None)
        else:
            # Remove , thousand separators
            salary_arr = list(map(lambda x: x.replace(",", ""), salary_str.split(" ")))
            if salary_arr[1] == "-":  # Normal range (<min> - <max> <unit>)
                min, max = map(float, (salary_arr[0], salary_arr[2]))
            elif salary_arr[0] == "Trên":  # Min only (Trên <min> <unit>)
                min, max = float(salary_arr[1]), None
            elif salary_arr[0] == "Tới":  # Max only (Tới <max> <unit>)
                min, max = None, float(salary_arr[1])
            # else:
            #     min, max = None, None

            # Convert USD to million VND
            if salary_arr[-1] == "USD":
                min, max = map(
                    lambda x: int(x) * USD_TO_VND / 10 ** 6 if x != None else None,
                    (min, max)
                )

        return min, max

    def _process_xp(self, xp_tag: Tag):
        # Returns min & max required experience (years)
        xp_str = xp_tag.text.strip("\n")
        xp_arr = xp_str.split(" ")

        if xp_str == "Không yêu cầu kinh nghiệm":
            min, max = 0, 0
        elif xp_arr[0].isnumeric():  # <xp> năm
            min, max = map(int, (xp_arr[0], xp_arr[0]))
        elif xp_arr[1].isnumeric():  # Trên/Dưới <xp> năm
            if xp_arr[0] == "Trên":
                min, max = int(xp_arr[1]), None
            if xp_arr[0] == "Dưới":
                min, max = None, int(xp_arr[1])
        else:
            min, max = None, None

        return min, max


class _NormalJobProcessor(JobProcessor):
    """
    Used for processing job detail pages with ./viec-lam/... subdirectories
    """

    @override
    def process_job(self, url: str):
        # Send request, instantiate BS object and define necessary tags
        response = send_request("get", url)
        soup = BeautifulSoup(response.content, "html.parser")
        detail_tags = soup.find_all("div",
                                    class_="job-detail__info--section-content-value"
                                    )  # [salary_tag, city_tag, yrs_of_exp_tag]

        title_tag = soup.find("h1", class_="job-detail__info--title")
        company_tag = soup \
            .find("h2", class_="company-name-label").find("a")
        salary_tag = detail_tags[0]
        xp_tag = detail_tags[2]
        city_tag = detail_tags[1]
        due_tag = soup.find("div", class_="job-detail__info--deadline")
        jd_tags = soup.find_all("div", class_="job-description__item--content") # [jd_tag, req_tag, benefits_tag]
        jd_tag = jd_tags[0]
        req_tag = jd_tags[1]
        benefits_tag = jd_tags[2]
        worktime_tag = jd_tag[3]

        # Process field values
        job_id = int(url.split("/")[-1].split(".")[0])
        job_title = title_tag.text.strip("\n")
        company = company_tag.text.strip("\n")
        salary_min, salary_max = self._process_salary(salary_tag)
        yrs_of_exp_min, yrs_of_exp_max = self._process_xp(xp_tag)
        job_city = city_tag.text.strip("\n")
        day, month, year = due_tag.text.split(":")[-1].strip("").strip("\n").strip("\n").strip().replace("-",
                                                                                                         "/").split("/")
        due_date = f"{year}/{month}/{day}"  # due_tag.text.split(":")[1].strip()[::-1].replace("-", "/") # datetime.strptime(date_str, "%d/%m/%Y")
        jd = jd_tag.text.strip("\n")
        req = req_tag.text.strip("\n")
        benefits = benefits_tag.text.strip("\n")
        worktime = worktime_tag.text.strip("\n")

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
            "worktime": worktime
        }


class _BrandJobProcessor(JobProcessor):
    """
    Used for processing job detail pages with ./brand/... subdirectories.
    - Template for diamond companies
    - Premium template

    Note: There are multiple templates for this subdirectory. Therefore, the class
    recognize template based on some tags and parse data based on it.
    """

    @override
    def process_job(self, url: str):
        # Send request, instantiate BS object
        response = send_request("get", url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Recognize template and select appropriate strategy
        if soup.find("div", id="premium-job"):
            job_item = self._process_job_premium(soup, url)
        else:
            job_item = self._process_job_diamond(soup, url)
        return job_item

    def _process_job_diamond(self, soup: BeautifulSoup, url: str):
        # Define necessary tags
        box_infos = soup.find_all("div", class_="box-info", limit=2)
        item_tags = box_infos[0] \
            .find("div", class_="box-main") \
            .find_all("div", class_="box-item")

        title_tag = soup \
            .find("div", class_="box-header") \
            .find("h2", class_="title")
        company_tag = soup.find("div", class_="footer-info-company-name")
        salary_tag = item_tags[0].find("span")
        xp_tag = item_tags[-1].find("span")
        city_tag = soup \
            .find("div", class_="box-address") \
            .find("div")  # Type 1 syntax
        due_tag = soup.find("span", class_="deadline").find("strong")
        jd_tags = box_infos[1].find_all("div", class_="content-tab")
        jd_tag = jd_tags[0]
        req_tag = jd_tags[1]
        benefits_tag = jd_tags[2]
        worktime_tag = jd_tags[3]


        # Get job detail values
        job_id = int(url.split("/")[-1].split(".")[0].split("-")[-1][1:])
        job_title = title_tag.text.strip("\n")
        company = company_tag.text.strip("\n")
        salary_min, salary_max = self._process_salary(salary_tag)
        yrs_of_exp_min, yrs_of_exp_max = self._process_xp(xp_tag)
        job_city = city_tag.text[2:(city_tag.text.index(":") - 1)]
        days_remaining = int(due_tag.text)
        due_date = (date.today() + timedelta(days=days_remaining))
        jd = jd_tag.text.strip("\n")
        req = req_tag.text.strip("\n")
        benefits = benefits_tag.text.strip("\n")
        worktime = worktime_tag.text.strip("\n")

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
            "worktime": worktime
        }

    def _process_job_premium(self, soup: BeautifulSoup, url: str):
        # Define necessary tags
        detail_tags = soup.find_all(
            "div",
            class_="basic-information-item__data--value"
        )

        title_tag = soup.find("h2", "premium-job-basic-information__content--title")
        company_tag = soup.find("h1", "company-content__title--name")
        salary_tag = detail_tags[0]
        xp_tag = detail_tags[-1]
        city_tag = detail_tags[1]
        due_tag = soup.find_all("div", class_="general-information-data__value")[-1]
        jd_tags = soup.find_all("div", class_="premium-job-description__box--content")
        jd_tag = jd_tags[0]
        req_tag = jd_tags[1]
        benefits_tag = jd_tags[2]
        worktime_tag = jd_tags[3]

        # Get job detail values
        job_id = int(url.split("/")[-1].split(".")[0].split("-")[-1][1:])
        job_title = title_tag.text.strip("\n")
        company = company_tag.text.strip("\n")
        salary_min, salary_max = self._process_salary(salary_tag)
        yrs_of_exp_min, yrs_of_exp_max = self._process_xp(xp_tag)
        job_city = city_tag.text.strip("\n")
        date_str = due_tag.text.split(" ")[-1].strip("\n")
        due_date = datetime.strptime(date_str, "%d/%m/%Y")
        jd = jd_tag.text.strip("\n")
        req = req_tag.text.strip("\n")
        benefits = benefits_tag.text.strip("\n")
        worktime = worktime_tag.text.strip("\n")

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
            "worktime": worktime
        }
