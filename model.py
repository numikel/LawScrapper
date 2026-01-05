from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import tempfile
import requests
import os
from pypdf import PdfReader
from logger import Logger

logger = Logger(to_file=True).get_logger()

load_dotenv()

class LegalActSummarizer():
    def __init__(self, model: str = "gpt-4.1-mini-2025-04-14", temperature: float = 0.2, max_tokens: int = 256):
        """
        Initializes the LLM summarizer for legal acts using OpenAI via LangChain.

        Parameters:
            model (str): The OpenAI model identifier to use.
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
            logger.error(f"Error: {e}")
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
        Sends content to the OpenAI LLM and returns a concise summary of the legal act.
    
        Parameters:
            content (str): Full plain-text content of the act to summarize.
    
        Returns:
            str: Short, context-aware summary (max 200 characters) or None if an error occurs.
        """
        try:
            system_prompt = self._get_prompt("summary")
            messages = [
                (
                    "system",
                    system_prompt
                ),
                ("user", f"Podsumuj ten akt prawny: {content}"),
                ("assistant", "Oto podsumowanie aktu prawnego:"),
            ]

            response = self.model.invoke(messages)
            return(response.content)
        except Exception as e:
            logger.error(f"Error: {e}")
            return (f"Error: {e}")
        
    def _get_prompt(self, prompt_name: str):
        with open(f"prompts/{prompt_name}.md", "r") as file:
            return file.read()

if __name__ == "__main__":
    models = ["gpt-4.1-2025-04-14"]
    for model in models:
        summarizer = LegalActSummarizer(model=model)
        content = summarizer.get_act_content(r"https://api.sejm.gov.pl/eli/acts/DU/2025/394/text.pdf")
        summary = summarizer.process_with_llm(content)

        logger.info(summary)