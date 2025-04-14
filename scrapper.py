import requests
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

class LawScrapper():
    def __init__(self):
        """
        Initializes the LawScrapper class with the current date and year context.
        Sets up a container to hold fetched acts.
        """
        self.current_date = datetime.now()
        self.current_year = self.current_date.strftime("%Y")
        self.acts = []

    def get_acts_list(self, year: int = None, keywords: list = None, date_from: str = None, date_to: str = None) -> list:
        """
        Fetches a list of legal acts from the Sejm API based on specified filters.

        Parameters:
            year (int, optional): Year of publication.
            keywords (list, optional): List of keywords to filter the acts.
            date_from (str, optional): Starting date of effectiveness (YYYY-MM-DD).
            date_to (str, optional): Ending date of effectiveness (YYYY-MM-DD).

        Returns:
            list: A list of legal acts matching the criteria.
        """
        params = {
            "publisher": "DU",
        }
        if (year):
            params["year"] = year
        else:
            params["year"] = self.current_year
        if (keywords):
            params["keyword"] = ",".join(keywords)
        if (date_from):
            params["dateEffectFrom"] = date_from.strftime("%Y-%m-%d")
        if (date_to):
            params["dateEffectTo"] = date_to.strftime("%Y-%m-%d")

        url = "https://api.sejm.gov.pl/eli/acts/search"

        response = requests.get(url, params=params, headers={"Accept": "application/json"})

        if response.status_code == 200:
            data = response.json().get("items", [])
        else:
            print(f"Error request: {response.status_code}")
            data = []

        if not data:
            print("Brak aktów spełniających kryteria.")

        self.acts = data
        return data
    
    def get_acts_from_last_week(self, keywords: list = None):
        """
        Returns acts from the past 7 days, optionally filtered by keywords.

        Parameters:
            keywords (list, optional): List of keywords to filter the acts.

        Returns:
            list: Filtered list of legal acts.
        """
        date_from = self.current_date - relativedelta(days=7)
        date_to = self.current_date

        return self.get_acts_list(self.current_year, keywords, date_from, date_to)
    
    def get_acts_from_current_month(self, keywords: list = None):
        """
        Returns acts from the current month, optionally filtered by keywords.

        Parameters:
            keywords (list, optional): List of keywords to filter the acts.

        Returns:
            list: Filtered list of legal acts.
        """
        date_from = self.current_date.replace(day=1)
        date_to = self.current_date

        return self.get_acts_list(self.current_year, keywords, date_from, date_to)

    def get_acts_from_last_month(self, keywords: list = None):
        """
        Returns acts from the last 30 days, optionally filtered by keywords.

        Parameters:
            keywords (list, optional): List of keywords to filter the acts.

        Returns:
            list: Filtered list of legal acts.
        """
        date_from = self.current_date - relativedelta(months=1)
        date_to = self.current_date

        return self.get_acts_list(self.current_year, keywords, date_from, date_to)
    
    def get_formatted_list(self, to_json=False)-> list:
        """
        Returns a cleaned and formatted version of the raw Sejm API data.

        Parameters:
            to_json (bool): If True, returns the data as a JSON string.

        Returns:
            list or str: Formatted list of acts, or JSON string if to_json=True.
        """
        formatted_list = []
        for act in self.acts:
            table = {
                "title": self.get_formated_value(act, "title"),
                "summary": None,
                "inForce": True if act.get("inForce") == "IN_FORCE" else False,
                "entryIntoForce": self.get_formated_value(act, "entryIntoForce"),
                "validFrom": self.get_formated_value(act, "validFrom"),
                "announcementDate": self.get_formated_value(act, "announcementDate"),
                "promulgation": self.get_formated_value(act, "promulgation"),
                "keywords": self.get_formated_value(act, "keywords"),
                "pdf": f"https://api.sejm.gov.pl/eli/acts/{act.get('ELI')}/text.pdf" if act.get("textPDF") else None,
                "html": f"https://api.sejm.gov.pl/eli/acts/{act.get('ELI')}/text.html" if act.get("textHTML") else None,
            }
            formatted_list.append(table)
        
        if to_json:
            formatted_list = json.dumps(formatted_list, ensure_ascii=False, indent=2)

        return formatted_list
    
    def get_formated_value(self, act: dict, value: str) -> str:
        """
        Safely extracts and formats a value from a dictionary.

        Parameters:
            act (dict): Dictionary representing a single legal act.
            value (str): Key to extract.

        Returns:
            str: Extracted and formatted value, or None.
        """
        if isinstance(act.get(value), str): 
           return act.get(value) if act.get(value) else None
        elif isinstance(act.get(value), list):
           return ", ".join(act.get(value)) if act.get(value) else None
        
    def get_keywords_list(self):
        """
        Retrieves a list of available keywords from the Sejm API.

        Returns:
            list: List of keywords.
        """
        url = "https://api.sejm.gov.pl/eli/keywords"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
        else:
            print(f"Error request: {response.status_code}")

        return data


if __name__ == "__main__":
    scrapper = LawScrapper()
    results = scrapper.get_acts_from_last_week(keywords=["przeciwpożarow ochrona"])
    print(scrapper.get_formatted_list(to_json=False))