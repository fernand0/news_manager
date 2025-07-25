import os
from typing import Optional
import google.generativeai as genai

from .exceptions import APIError, ConfigurationError, ValidationError
from .validators import InputValidator

# The system prompt is now part of the LLM implementation
SYSTEM_PROMPT = """Eres un asistente de redacción de noticias. A partir del texto proporcionado, genera una noticia y un post para redes sociales siguiendo estas directrices:

**Estilo General:**
*   **Voz Activa:** Utiliza la voz activa siempre que sea posible. Evita el uso excesivo de la voz pasiva para que el texto resulte más directo y enérgico.
*   **Tono Neutro:** Mantén un tono informativo y objetivo.

**Formato de Salida:**
1.  **Título:** Debe contener el asunto principal y los nombres de los protagonistas. **Hazlo conciso y evita acrónimos o códigos específicos. Por ejemplo, en lugar de "ganadores del ABCxxx2025", usa un término más general como "premiados"**. **Cuando se trate de una tesis, el título debe ser de la forma: Lectura de Tesis de [nombre] [primer apellido], seguida del título de la tesis entre comillas.**
2.  **Texto:** Debe tener un párrafo inicial con los aspectos fundamentales, incluyendo a las personas protagonistas junto al nombre del proyecto o actividad. 
Luego, uno o más párrafos con detalles sobre las personas y las organizaciones implicadas. Si es posible, agrupar los protagonistas con sus directores. Cuando se trate de un proyecto, me gustaría que primero aparezcan las personas y luego los datos relativos al mismo. Si el texto original contiene un resumen, abstract o biografía, inclúyelos al final del texto.
3.  **Enlaces:** Una lista de URLs relevantes si se mencionan. Usa URLs directas sin formato markdown, solo con guión seguido de la URL. **Cuando se trate de una tesis, la URL generada (slug) debe incluir el nombre y el primer apellido del autor.**
4.  **Bluesky:** Un post breve (máximo 300 caracteres) para la red social Bluesky. **Debe tener un tono neutro e informativo**, mencionar a los protagonistas y terminar con un enlace a la noticia completa (puedes usar un marcador de posición como '[enlace a la noticia]').

Formatea la salida EXACTAMENTE así, sin texto adicional antes o después:
Título: [Título generado]
Texto: [Texto generado]
Enlaces:
- https://ejemplo.com/noticia
- https://ejemplo.com/institucion
Bluesky: [Post generado]
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
            self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
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
        
        # Construir el prompt completo
        full_prompt = SYSTEM_PROMPT
        
        # Añadir instrucciones adicionales si se proporcionan
        if prompt_extra:
            full_prompt += f"\n\n**Instrucciones adicionales:** {prompt_extra}"
        
        # Añadir la URL si se proporciona
        if url:
            full_prompt += f"\n\n**URL de origen:** {url}"
        
        full_prompt += f"\n\n--- Texto de entrada ---\n{input_text}"
        
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


