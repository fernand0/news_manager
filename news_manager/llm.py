import os
from typing import Optional
import google.generativeai as genai

from .exceptions import APIError, ConfigurationError, ValidationError
from .validators import InputValidator

# The system prompt is now part of the LLM implementation
SYSTEM_PROMPT = """You are a news writing assistant for the web of a computer science department. From the provided text, generate a news article and a social media post in Spanish (but do not translate the texts that are written in English) following these guidelines:

**General Style:**
*   **Active Voice:** Use active voice whenever possible. Avoid excessive use of passive voice to make the text more direct and energetic.
*   **Neutral Tone:** Maintain an informative and objective tone.

**Output Format:**
1.  **Title:** It should contain the main subject and the names of the protagonists. **Make it concise and avoid specific acronyms or codes. For example, instead of "winners of the ABCxxx2025", use a more general term like "awardees"**. **When it is a thesis, the title should be in the form: PhD Thesis of [name] [first surname], followed by the title of the thesis in quotes.**
2.  **Text:** It should have an initial paragraph with the main aspects, including the protagonists along with the name of the project or activity.
Then, one or more paragraphs with details about the people and organizations involved. If possible, group the protagonists with their directors. When it is a project, I would like the people to appear first and then the data related to it. If the original text contains a summary, abstract or biography, include them at the end of the text.
3.  **Links:** A list of relevant URLs if mentioned. Use direct URLs without markdown format, just with a hyphen followed by the URL. **When it is a thesis, the generated URL (slug) must include the name and first surname of the author.**
4.  **Bluesky:** A short post (maximum 300 characters) for the Bluesky social network. **It must have a neutral and informative tone**, mention the protagonists and end with a link to the full news (you can use a placeholder like '[link to the news]').

Format the output EXACTLY like this, with no additional text before or after:
Title: [Generated title]
Text: [Generated text]
Links:
- https://example.com/news
- https://example.com/institution
Bluesky: [Generated post]
"""

class LLMClient:
    """
    A generic base class for Large Language Model clients.
    Subclasses must implement the generate_news method.
    """
    def generate_news(self, input_text: str, prompt_extra: Optional[str] = None, url: Optional[str] = None) -> str:
        """
        Generates a news article from the given input text.

        Args:
            input_text: The source text for the news article.
            prompt_extra: Optional additional instructions for the AI.
            url: Optional URL that should be included in the links section.

        Returns:
            The generated news article as a string.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class GeminiClient(LLMClient):
    """
    An LLM client implementation for Google's Gemini API.
    """
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")

        # Use validator for API key validation
        try:
            InputValidator.validate_api_key(api_key, "Google Gemini")
        except Exception as e:
            raise ConfigurationError(str(e))

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        except Exception as e:
            raise ConfigurationError(
                "Failed to initialize Gemini client",
                details=str(e),
                suggestion="Check your API key and internet connection"
            )

    def generate_news(self, input_text: str, prompt_extra: Optional[str] = None, url: Optional[str] = None) -> str:
        """
        Generates a news story by calling the Gemini API.

        Args:
            input_text: The source text for the news article
            prompt_extra: Optional additional instructions for the AI
            url: Optional URL that should be included in the links section

        Returns:
            The generated news article as a string

        Raises:
            APIError: If the Gemini API call fails
            ValidationError: If input validation fails
        """
        # Validate inputs
        if not input_text or not input_text.strip():
            raise ValidationError(
                "Input text is empty",
                suggestion="Provide some text content to generate news from"
            )

        if prompt_extra is not None:
            InputValidator.validate_prompt_extra(prompt_extra)

        if url is not None:
            InputValidator.validate_url(url)

        # Build the full prompt
        full_prompt = SYSTEM_PROMPT

        # Add additional instructions if provided
        if prompt_extra:
            full_prompt += f"\n\n**Additional instructions:** {prompt_extra}"

        # Add the URL if provided
        if url:
            full_prompt += f"\n\n**Source URL:** {url}"

        full_prompt += f"\n\n--- Input text ---\n{input_text}"

        try:
            response = self.model.generate_content(full_prompt)
            if not response or not response.text:
                raise APIError(
                    "Empty response from API",
                    api_name="Google Gemini",
                    suggestion="Try again or check if the input content is appropriate"
                )
            return response.text
        except Exception as e:
            if isinstance(e, (APIError, ValidationError)):
                raise
            # Convert generic exceptions to APIError
            raise APIError(
                f"Failed to generate content: {str(e)}",
                api_name="Google Gemini",
                suggestion="Check your API key, internet connection, and input content"
            ) from e


