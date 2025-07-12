import click
import os
from pathlib import Path
from dotenv import load_dotenv
from .llm import GeminiClient

# Para descarga y parsing de noticias
import requests
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

def extract_main_text_from_url(url):
    """
    Descarga la URL y extrae el texto principal de la noticia.
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"No se pudo descargar la URL: {e}")

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Heurística: buscar <article>, si no, buscar el <div> más grande con mucho texto
    article = soup.find('article')
    if article:
        text = article.get_text(separator='\n', strip=True)
        if len(text) > 200:
            return text
    # Si no hay <article>, buscar el <div> más largo
    candidates = soup.find_all(['div', 'section'], recursive=True)
    best = ''
    for c in candidates:
        t = c.get_text(separator='\n', strip=True)
        if len(t) > len(best):
            best = t
    # Fallback: todo el body
    if len(best) > 200:
        return best
    body = soup.body.get_text(separator='\n', strip=True) if soup.body else ''
    if len(body) > 200:
        return body
    # Fallback final: todo el texto visible
    return soup.get_text(separator='\n', strip=True)

@click.group()
def main():
    """
    A simple CLI to manage news.
    """
    pass

@main.command()
@click.option(
    '--input-file', '-i',
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    help='Archivo de entrada con el texto fuente (por defecto: /tmp/noticia.txt o NEWS_INPUT_FILE)'
)
@click.option(
    '--url',
    type=str,
    default=None,
    help='URL de una noticia para descargar y generar la noticia a partir de su contenido.'
)
@click.option(
    '--prompt-extra',
    type=str,
    default=None,
    help='Instrucciones adicionales para personalizar la generación (ej: "céntrate en tal persona e ignora el resto")'
)
@click.option(
    '--interactive-prompt',
    is_flag=True,
    default=False,
    help='Activar modo interactivo para instrucciones adicionales'
)
def generate(input_file, url, prompt_extra, interactive_prompt):
    """
    Genera una noticia a partir de un archivo o una URL (opciones exclusivas).
    
    El archivo de entrada se puede especificar de tres formas:
    1. Con el parámetro --input-file
    2. Con la variable de entorno NEWS_INPUT_FILE
    3. Por defecto usa /tmp/noticia.txt
    O bien, se puede usar --url para descargar una noticia de internet.
    
    Puedes usar --prompt-extra para añadir instrucciones personalizadas.
    Usa --interactive-prompt para activar el modo interactivo.
    """
    try:
        # Exclusividad de opciones
        if input_file and url:
            click.echo("Error: No puedes usar --input-file y --url al mismo tiempo. Elige solo una opción.", err=True)
            return
        
        if url:
            click.echo(f"--- Descargando y extrayendo noticia de: {url} ---")
            try:
                input_text = extract_main_text_from_url(url)
            except Exception as e:
                click.echo(f"Error al procesar la URL: {e}", err=True)
                return
            if not input_text or len(input_text.strip()) < 100:
                click.echo("Error: No se pudo extraer suficiente texto de la URL proporcionada.", err=True)
                return
            click.echo(f"--- Texto extraído (primeros 300 caracteres): ---\n{input_text[:300]}\n--- Fin de muestra ---")
        else:
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
        
        # Manejar prompt_extra interactivamente si se activa el modo interactivo
        if interactive_prompt:
            click.echo("\n--- Instrucciones adicionales ---")
            click.echo("Ejemplos de instrucciones que puedes usar:")
            click.echo("• 'céntrate en María Santos e ignora el resto'")
            click.echo("• 'enfócate solo en los aspectos tecnológicos'")
            click.echo("• 'usa un tono más formal y académico'")
            click.echo("• 'destaca especialmente los logros y premios obtenidos'")
            click.echo("• 'ignora los detalles técnicos y céntrate en el impacto social'")
            click.echo("• (deja vacío para no añadir instrucciones)")
            click.echo()
            
            prompt_extra = click.prompt(
                "¿Qué instrucciones adicionales quieres añadir?",
                default="",
                type=str
            ).strip()
        
        click.echo(f"--- Inicializando cliente AI y generando noticia... ---")
        
        # Mostrar instrucciones adicionales si se proporcionan
        if prompt_extra:
            click.echo(f"--- Instrucciones adicionales: {prompt_extra} ---")
        
        client = GeminiClient()
        # Pasar la URL al cliente para que aparezca en los enlaces
        generated_text = client.generate_news(input_text, prompt_extra, url)
        click.echo(generated_text)

    except (ValueError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
    except PermissionError:
        click.echo(f"Error: No tienes permisos para leer el archivo {file_path}", err=True)
    except Exception as e:
        click.echo(f"Error inesperado: {e}", err=True)


if __name__ == '__main__':
    main()
