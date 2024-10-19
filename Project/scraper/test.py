from Project.utils.processors import JobProcessor
from Project.scraper.topcv_phase2 import write_to_file
from Project.scraper.topcv_phase2 import clear_file

if __name__ == '__main__':
    # job_processor = JobProcessor()
    # link = "https://www.topcv.vn/viec-lam/backend-developer-hybrid/1324000.html?ta_source=ITJobs_LinkDetail"
    # scraped_data = job_processor.process_job(link, pause_between_jobs=1)
    # print(scraped_data)
    clear_file((r"../data/topcv.vn_data.csv"))