import click
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from .news_generator import NewsGenerator
from .file_manager import FileManager
from .utils_base import setup_logging
from .web_extractor import extract_main_text_from_url  # For backward compatibility
from .exceptions import (
    NewsManagerError, ValidationError, ConfigurationError, 
    ContentProcessingError, APIError, NetworkError, FileOperationError
)
from news_publisher.cli import publish_content

# Load environment variables from .env file
load_dotenv()

@click.group()
@click.version_option()
def cli():
    """
    A simple CLI to manage news.
    """
    setup_logging()



@cli.command()
@click.option(
    '--input-file', '-i',
    type=click.Path(exists=False, file_okay=True, dir_okay=False, path_type=Path),
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
@click.option(
    '--output-dir',
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help='Directorio donde guardar los archivos generados (por defecto: usa NEWS_OUTPUT_DIR o no guarda archivos)'
)
@click.option(
    '--user',
    default=None,
    help='Usuario de Bluesky para publicar el post'
)
def generate(input_file, url, prompt_extra, interactive_prompt, output_dir, user):
    """
    Genera una noticia a partir de un archivo o una URL (opciones exclusivas).

    El archivo de entrada se puede especificar de tres formas:
    1. Con el parámetro --input-file
    2. Con la variable de entorno NEWS_INPUT_FILE
    3. Por defecto usa /tmp/noticia.txt
    O bien, se puede usar --url para descargar una noticia de internet.

    El directorio de salida se puede especificar de dos formas:
    1. Con el parámetro --output-dir
    2. Con la variable de entorno NEWS_OUTPUT_DIR

    Puedes usar --prompt-extra para añadir instrucciones personalizadas.
    Usa --interactive-prompt para activar el modo interactivo.
    """
    try:
        # Validate exclusive options
        if input_file and url:
            click.echo("Error: No puedes usar --input-file y --url al mismo tiempo. Elige solo una opción.", err=True)
            sys.exit(1)

        # Handle interactive prompt
        if interactive_prompt:
            prompt_extra = _handle_interactive_prompt()

        # Show additional instructions if provided
        if prompt_extra:
            click.echo(f"--- Instrucciones adicionales: {prompt_extra} ---")

        # Initialize components
        news_generator = NewsGenerator()
        output_dir_path = _determine_output_directory(output_dir)
        file_manager = FileManager(output_dir_path)

        click.echo("--- Inicializando cliente AI y generando noticia... ---")

        # Generate news content
        if url:
            click.echo(f"--- Descargando y extrayendo noticia de: {url} ---")
            content = news_generator.generate_from_url(url, prompt_extra)
            input_text = ""  # Not needed for URL-based generation
        else:
            file_path = _determine_input_file(input_file)
            click.echo(f"--- Leyendo archivo: {file_path} ---")
            content = news_generator.generate_from_file(file_path, prompt_extra)
            # Read input text for file saving
            with open(file_path, 'r', encoding='utf-8') as f:
                input_text = f.read().strip()

        # Display and save content
        if content.get('bluesky_only'):
            _handle_bluesky_interactive(content, user)
            if file_manager.output_dir:
                saved_files = file_manager.save_news_content(content, input_text)
                _display_saved_files(saved_files)
        else:
            _display_content(content)
            if file_manager.output_dir:
                saved_files = file_manager.save_news_content(content, input_text)
                _display_saved_files(saved_files)

    except (ValidationError, ConfigurationError, ContentProcessingError, APIError, NetworkError, FileOperationError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error inesperado: {e}", err=True)
        sys.exit(1)


def _handle_bluesky_interactive(content: dict, user: str):
    """Handle the interactive workflow for Bluesky posts."""
    click.echo(f"\n--- Candidato a post para Bluesky ---\n{content['bluesky']}\n")

    if click.confirm('¿Quieres modificar el post?', default=False):
        edited_text = click.edit(content['bluesky'])
        if edited_text is not None:
            content['bluesky'] = edited_text.strip()
            click.echo(f"\n--- Post modificado ---\n{content['bluesky']}\n")

    if click.confirm('¿Quieres publicar el post en Bluesky?', default=True):
        publish_content(content['bluesky'], user)


def _handle_interactive_prompt() -> str:
    """Handle interactive prompt for additional instructions."""
    click.echo("\n--- Instrucciones adicionales ---")
    click.echo("Ejemplos de instrucciones que puedes usar:")
    click.echo("• 'céntrate en María Santos e ignora el resto'")
    click.echo("• 'enfócate solo en los aspectos tecnológicos'")
    click.echo("• 'usa un tono más formal y académico'")
    click.echo("• 'destaca especialmente los logros y premios obtenidos'")
    click.echo("• 'ignora los detalles técnicos y céntrate en el impacto social'")
    click.echo("• (deja vacío para no añadir instrucciones)")
    click.echo()

    return click.prompt(
        "¿Qué instrucciones adicionales quieres añadir?",
        default="",
        type=str
    ).strip()


def _determine_input_file(input_file: Path) -> Path:
    """Determine the input file path from options and environment."""
    if input_file:
        file_path = input_file
    else:
        # Check environment variable first, then default
        env_file = os.getenv('NEWS_INPUT_FILE')
        if env_file:
            file_path = Path(env_file)
        else:
            file_path = Path('/tmp/noticia.txt')
    
    return file_path


def _determine_output_directory(output_dir: Path) -> Path:
    """Determine the output directory from options and environment."""
    if output_dir:
        return output_dir
    
    env_output_dir = os.getenv('NEWS_OUTPUT_DIR')
    if env_output_dir:
        return Path(env_output_dir)
    
    return None


def _display_content(content: dict):
    """Display the generated content to the user."""
    output_lines = []
    
    if content.get('titulo'):
        output_lines.append(f"Título: {content['titulo']}")
    if content.get('texto'):
        output_lines.append(f"Texto: {content['texto']}")
    if content.get('enlaces'):
        output_lines.append('Enlaces:')
        output_lines.extend(content['enlaces'])
    
    if output_lines:
        click.echo('\n'.join(output_lines))


def _display_saved_files(saved_files: dict):
    """Display information about saved files."""
    if not saved_files:
        return
    
    for file_type, file_path in saved_files.items():
        if file_type == 'news':
            click.echo(f"Noticia guardada en: {file_path}")
        elif file_type == 'bluesky':
            click.echo(f"Bluesky guardado en: {file_path}")


@cli.command()
def hello():
    """
    Prints a welcome message to confirm that the news-manager CLI is correctly installed.
    """
    click.echo("Welcome to News Manager CLI!")
    click.echo("This tool helps you generate and manage news content using the Gemini API.")
    click.echo("Try 'news-manager generate' to create a news story or 'news-manager --help' for more commands.")


if __name__ == '__main__':
    cli()
