import click
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

@click.group()
def main():
    """
    A simple CLI to manage news.
    """
    pass

@main.command()
def hello():
    """Prints a hello message."""
    click.echo("Hello, world!")

# Instructions for the AI on how to generate the news
SYSTEM_PROMPT = """Eres un asistente de redacción de noticias. A partir del texto proporcionado, genera una noticia siguiendo estas directrices:

**Estilo General:**
*   **Voz Activa:** Utiliza la voz activa siempre que sea posible. Evita el uso excesivo de la voz pasiva para que el texto resulte más directo y enérgico.

**Formato de Salida:**
1.  **Título:** Debe contener el asunto principal y los nombres de los protagonistas. **Hazlo conciso y evita acrónimos o códigos específicos. Por ejemplo, en lugar de "ganadores del TFM3M2025", usa un término más general como "premiados"**.
2.  **Texto:** Debe tener un párrafo inicial con los aspectos fundamentales. Luego, uno o más párrafos con detalles sobre las personas y las organizaciones implicadas. Si el texto original contiene un resumen, abstract o biografía, inclúyelos al final del texto.
3.  **Enlaces:** Una lista de URLs relevantes si se mencionan.

Formatea la salida EXACTAMENTE así, sin texto adicional antes o después:
Título: [Título generado]
Texto: [Texto generado]
Enlaces:
- [Enlace 1]
- [Enlace 2]
"""

@main.command()
def generate():
    """
    Generates a news story from /tmp/noticia.txt by calling the Gemini API.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        click.echo("Error: GOOGLE_API_KEY not found. Please set it in your .env file.", err=True)
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')

    input_file = "/tmp/noticia.txt"
    try:
        with open(input_file, 'r') as f:
            input_text = f.read()
    except FileNotFoundError:
        click.echo(f"Error: Input file not found at {input_file}", err=True)
        return

    click.echo("--- Calling Gemini API to generate news... ---")

    # Combine the system prompt with the user's input text
    full_prompt = f"{SYSTEM_PROMPT}\n\n--- Texto de entrada ---\n{input_text}"

    try:
        response = model.generate_content(full_prompt)
        click.echo(response.text)
    except Exception as e:
        click.echo(f"An error occurred with the Gemini API: {e}", err=True)


if __name__ == '__main__':
    main()
