from Project.utils.processors import JobProcessor


if __name__ == '__main__':
    job_processor = JobProcessor()
    link = "https://careerviet.vn/vi/tim-viec-lam/di6-senior-data-engineer-sql-%E2%80%93-msb-1y565.35C1AB26.html"
    scraped_data = job_processor.process_job(link, pause_between_jobs=1)
    print(scraped_data)
