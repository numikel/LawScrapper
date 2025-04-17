from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import tempfile
import requests
import os
from PyPDF2 import PdfReader

load_dotenv()

class LegalActSummarizer():
    def __init__(self, model: str = "gpt-4.1-mini-2025-04-14", temperature: float = 0.2, max_tokens: int = 256):
        """
        Initializes the LLM summarizer for legal acts using Claude via LangChain.

        Parameters:
            model (str): The Claude model identifier to use.
            temperature (float): Sampling temperature for the LLM.
            max_tokens (int): Maximum token length for the generated summary.
        """
        self.model = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=None,
            max_retries=3,
        )

    def get_act_content(self, url: str) -> str:
        """
        Downloads a legal act from a given PDF URL and extracts its text content.

        Parameters:
            url (str): URL to the .pdf document.

        Returns:
            str: Extracted plain text from the PDF.

        Raises:
            requests.exceptions.RequestException: If the HTTP request fails.
            PdfReadError: If PDF parsing fails.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            temp_path = tmp_file.name

        try:
            reader = PdfReader(temp_path)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
        finally:
            os.remove(temp_path)

    def process_with_llm(self, content: str) -> str:
        """
        Sends content to the Claude LLM and returns a concise summary of the legal act.
    
        Parameters:
            content (str): Full plain-text content of the act to summarize.
    
        Returns:
            str: Short, context-aware summary (max 200 characters) or None if an error occurs.
        """
        try:
            messages = [
                (
                    "system",
                    """<prompt>
  <rola>Jesteś radcą prawnym.</rola>
  <kontekst>Użytkownik prześle Ci akty prawne. Twoje podsumowanie trafi na listę wielu takich aktów, więc musi być wyjątkowo zwięzłe, konkretne i unikalne.</kontekst>
  <zadanie>Stwórz krótkie podsumowanie aktu prawnego zawierające najważniejsze zmiany, nowe przepisy oraz tematykę. Skup się wyłącznie na treści aktu. Nie twórz wstępów, wyjaśnień ani opinii.</zadanie>
  <format>Tekst ciągły (bez punktów i numeracji), maksymalnie 200 znaków.</format>
  <instrukcje>Jeśli nie masz wystarczających informacji w akcie, napisz: „Brak wystarczających informacji w akcie”. Nie dodawaj nic więcej.</instrukcje>
  <przyklady>
    <dobry_przyklad>Ustawa dot. ochrony danych osobowych – nowe obowiązki dla administratorów, wprowadzenie kar za niewłaściwe przetwarzanie.</dobry_przyklad>
    <zly_przyklad>1. Zmiany w RODO. 2. Kary. 3. Ochrona danych.</zly_przyklad>
  </przyklady>
  <zakonczenie>Wygeneruj tylko tekst podsumowania. Nie dodawaj nic więcej.</zakonczenie>
</prompt>""",
                ),
                ("user", "Podsumuj ten akt prawny: "),
                ("assistant", "Oto podsumowanie aktu prawnego:"),
                ("user", content),
                ("assistant", "Oto podsumowanie:"),
                ("user", "Podsumuj ten akt prawny: "),
                ("assistant", "Oto podsumowanie aktu prawnego:"),
                ("human",content),
            ]

            response = self.model.invoke(messages)
            return(response.content)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    models = ["gpt-4.1-2025-04-14"]
    for model in models:
        summarizer = LegalActSummarizer(model=model)
        content = summarizer.get_act_content(r"https://api.sejm.gov.pl/eli/acts/DU/2025/394/text.pdf")
        summary = summarizer.process_with_llm(content)

        print(summary)