import requests
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

class JOLScrapper():
    def __init__(self):
        self.current_date = datetime.now()
        self.current_year = self.current_date.strftime("%Y")
        self.acts = []

    def get_acts_list(self, year: int = None, keywords: list = None, date_from: str = None, date_to: str = None) -> list:
        params = {
            "publisher": "DU"
        }
        if (year):
            params["year"] = year
        else:
            params["year"] = self.current_year
        if (keywords):
            params["keyword"] = ",".join(keywords)
        if (date_from):
            params["dateFrom"] = date_from.strftime("%Y-%m-%d")
        if (date_to):
            params["dateTo"] = date_to.strftime("%Y-%m-%d")
        url = "https://api.sejm.gov.pl/eli/acts/search"

        response = requests.get(url, params = params)

        if response.status_code == 200:
            data = response.json()
            data = data.get("items")
        else:
            print(f"Error request: {response.status_code}")

        self.acts = data
        return data
    
    def get_acts_from_last_week(self, keywords: list = None):
        date_from = self.current_date - relativedelta(days=7)
        date_to = self.current_date

        return self.get_acts_list(self.current_year, keywords, date_from, date_to)
    
    def get_acts_from_current_mont(self, keywords: list = None):
        date_from = self.current_date.replace(day=1)
        date_to = self.current_date

        return self.get_acts_list(self.current_year, keywords, date_from, date_to)

    def get_acts_from_last_month(self, keywords: list = None):
        date_from = self.current_date - relativedelta(months=1)
        date_to = self.current_date

        return self.get_acts_list(self.current_year, keywords, date_from, date_to)
    
    def get_formatted_list(self, to_json=False)-> list:
        formatted_list = []
        for act in self.acts:
            table = {
                "title": act.get("title"),
                "inForce": True if act.get("inForce") == "IN_FORCE" else False,
                "entryIntoForce": act.get("entryIntoForce") if act.get("entryIntoForce") else None,
                "validFrom": act.get("validFrom") if act.get("validFrom") else None,
                "announcementDate": act.get("announcementDate") if act.get("announcementDate") else None,
                "changeDate": act.get("changeDate") if act.get("changeDate") else None,
                "promulgation": act.get("promulgation") if act.get("promulgation") else None,
                "pdf": f"https://api.sejm.gov.pl/eli/acts/{act.get("ELI")}/text.pdf" if act.get("textPDF") else None,
                "html": f"https://api.sejm.gov.pl/eli/acts/{act.get("ELI")}/text.html" if act.get("textHTML") else None,
            }
            formatted_list.append(table)
        
        if to_json:
            formatted_list = json.dumps(formatted_list)

        return formatted_list

if __name__ == "__main__":
    scrapper = JOLScrapper()
    results = scrapper.get_acts_from_last_week(keywords=["przeciwpożarow ochrona"])
    print(results)