import Project.scraper.careerviet_phase2 as careerviet_phase2
import Project.scraper.careerviet_phase1 as careerviet_phase1
if __name__ == '__main__':
    careerviet_phase1.scrape_links()
    careerviet_phase2.scrape_data()