import click
import os
from pathlib import Path
from dotenv import load_dotenv
from .llm import GeminiClient

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
    click.echo("Welcome to News Manager CLI!")
    click.echo("This tool helps you generate and manage news content using the Gemini API.")
    click.echo("Try 'news-manager generate' to create a news story or 'news-manager --help' for more commands.")

@main.command()
@click.option(
    '--input-file', '-i',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    help='Archivo de entrada con el texto fuente (por defecto: /tmp/noticia.txt o NEWS_INPUT_FILE)'
)
def generate(input_file):
    """
    Generates a news story from an input file by calling an LLM API.
    
    El archivo de entrada se puede especificar de tres formas:
    1. Con el parámetro --input-file
    2. Con la variable de entorno NEWS_INPUT_FILE
    3. Por defecto usa /tmp/noticia.txt
    """
    try:
        # Determine the input file path
        if input_file:
            file_path = input_file
        else:
            # Check environment variable first, then default
            env_file = os.getenv('NEWS_INPUT_FILE')
            if env_file:
                file_path = Path(env_file)
            else:
                file_path = Path('/tmp/noticia.txt')
        
        # Validate file exists and is readable
        if not file_path.exists():
            click.echo(f"Error: El archivo no existe: {file_path}", err=True)
            click.echo(f"Sugerencia: Crea el archivo con tu texto fuente o especifica otro archivo con --input-file", err=True)
            return
        
        if not file_path.is_file():
            click.echo(f"Error: La ruta especificada no es un archivo: {file_path}", err=True)
            return
        
        # Read the input file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                input_text = f.read().strip()
        except UnicodeDecodeError:
            click.echo(f"Error: No se puede leer el archivo {file_path}. Verifica que sea un archivo de texto válido.", err=True)
            return
        
        if not input_text:
            click.echo(f"Error: El archivo {file_path} está vacío.", err=True)
            return

        click.echo(f"--- Leyendo archivo: {file_path} ---")
        click.echo(f"--- Inicializando cliente AI y generando noticia... ---")
        
        # The CLI only knows about the generic client.
        # To switch to another AI, you would just change the line below.
        # For example: client = OpenAIClient()
        client = GeminiClient()
        
        # The client handles all the API-specific logic.
        generated_text = client.generate_news(input_text)
        
        click.echo(generated_text)

    except (ValueError, RuntimeError) as e:
        # Catch errors from our client (e.g., missing API key or API call failure)
        click.echo(f"Error: {e}", err=True)
    except PermissionError:
        click.echo(f"Error: No tienes permisos para leer el archivo {file_path}", err=True)
    except Exception as e:
        click.echo(f"Error inesperado: {e}", err=True)


if __name__ == '__main__':
    main()
