import os
from typing import Optional
import google.generativeai as genai

# The system prompt is now part of the LLM implementation
SYSTEM_PROMPT = """Eres un asistente de redacción de noticias. A partir del texto proporcionado, genera una noticia y un post para redes sociales siguiendo estas directrices:

**Estilo General:**
*   **Voz Activa:** Utiliza la voz activa siempre que sea posible. Evita el uso excesivo de la voz pasiva para que el texto resulte más directo y enérgico.
*   **Tono Neutro:** Mantén un tono informativo y objetivo.

**Formato de Salida:**
1.  **Título:** Debe contener el asunto principal y los nombres de los protagonistas. **Hazlo conciso y evita acrónimos o códigos específicos. Por ejemplo, en lugar de "ganadores del ABCxxx2025", usa un término más general como "premiados"**.
2.  **Texto:** Debe tener un párrafo inicial con los aspectos fundamentales, incluyendo a las personas protagonistas junto al nombre del proyecto o actividad. 
Luego, uno o más párrafos con detalles sobre las personas y las organizaciones implicadas. Si es posible, agrupar los protagonistas con sus directores. Cuando se trate de un proyecto, me gustaría que primero aparezcan las personas y luego los datos relativos al mismo. Si el texto original contiene un resumen, abstract o biografía, inclúyelos al final del texto.
3.  **Enlaces:** Una lista de URLs relevantes si se mencionan.
4.  **Bluesky:** Un post breve (máximo 300 caracteres) para la red social Bluesky. **Debe tener un tono neutro e informativo**, mencionar a los protagonistas, usar hashtags relevantes y terminar con un enlace a la noticia completa (puedes usar un marcador de posición como '[enlace a la noticia]').

Formatea la salida EXACTAMENTE así, sin texto adicional antes o después:
Título: [Título generado]
Texto: [Texto generado]
Enlaces:
- [Enlace 1]
- [Enlace 2]
Bluesky: [Post generado]
"""

class LLMClient:
    """
    A generic base class for Large Language Model clients.
    Subclasses must implement the generate_news method.
    """
    def generate_news(self, input_text: str, prompt_extra: Optional[str] = None) -> str:
        """
        Generates a news article from the given input text.
        
        Args:
            input_text: The source text for the news article.
            prompt_extra: Optional additional instructions for the AI.
        
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
        if not api_key:
            raise ValueError("Error: GOOGLE_API_KEY not found. Please set it in your .env file.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def generate_news(self, input_text: str, prompt_extra: Optional[str] = None) -> str:
        """
        Generates a news story by calling the Gemini API.
        """
        # Construir el prompt completo
        full_prompt = SYSTEM_PROMPT
        
        # Añadir instrucciones adicionales si se proporcionan
        if prompt_extra:
            full_prompt += f"\n\n**Instrucciones adicionales:** {prompt_extra}"
        
        full_prompt += f"\n\n--- Texto de entrada ---\n{input_text}"
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            # Raise the exception to be handled by the CLI
            raise RuntimeError(f"An error occurred with the Gemini API: {e}") from e


