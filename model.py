from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import tempfile
import requests
import os
from PyPDF2 import PdfReader

load_dotenv()

class SummarizeAct():
    def __init__(self, model: str = "claude-3-5-sonnet-latest", temperature: float = 0.2, max_tokens: int = 128):
        self.model = ChatAnthropic(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=None,
            max_retries=3,
        )

    def get_act_content(self, url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            temp_path = tmp_file.name

        try:
            reader = PdfReader(temp_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        finally:
            os.remove(temp_path)

    def process_with_llm(self, content: str) -> str:
        try:
            messages = [
                (
                    "system",
                    """<rola>Jesteś radcą prawnym</rola><kontekst>Użytkownik prześle Ci akty prawne. Twoje podsumowanie trafi na listę kilkunastu takich aktów, dlatego musi być wyjątkowo zwięzłe i informacyjne.</kontekst><zadanie>Stwórz krótkie podsumowanie aktu prawnego, zawierające najważniejsze zmiany, nowe przepisy oraz tematykę. Zwróć tylko podsumowanie aktu.</zadanie><format>Tekst ciągły (bez punktów i numeracji), maksymalnie 200 znaków.</format>
    <przykłady><dobry_przykład>Ustawa dot. ochrony danych osobowych – nowe obowiązki dla administratorów, wprowadzenie kar za niewłaściwe przetwarzanie.</dobry_przykład><zły_przykład>1. Zmiany w RODO. 2. Kary. 3. Ochrona danych – zbyt ogólne i punktowane.</zły_przykład></przykłady>""",
                ),
                ("human",{content}),
            ]

            response = self.model.invoke(messages)
            return(response.content)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    summarizer = SummarizeAct()
    content = summarizer.get_act_content(r"https://api.sejm.gov.pl/eli/acts/DU/2025/373/text.pdf")
    summary = summarizer.process_with_llm(content)

    print(summary)