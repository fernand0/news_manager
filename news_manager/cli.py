import click
import os
from pathlib import Path
from dotenv import load_dotenv
from .llm import GeminiClient
import re
from datetime import datetime, timedelta
import unicodedata

# Para descarga y parsing de noticias
import requests
from bs4 import BeautifulSoup

from .utils_base import setup_logging

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

def siguiente_laborable(fecha):
    """Devuelve el siguiente día laborable (lunes-viernes) a partir de una fecha dada."""
    siguiente = fecha + timedelta(days=1)
    while siguiente.weekday() >= 5:  # 5=sábado, 6=domingo
        siguiente += timedelta(days=1)
    return siguiente

def extract_person_names(text):
    """Extrae nombres de personas del texto usando patrones comunes."""
    # Patrones para nombres de personas
    patterns = [
        r'\b(?:Dr\.|Dra\.|Prof\.|Profesora)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
        r'\b([A-Z][a-z]+)\s+(?:y|e)\s+([A-Z][a-z]+)\b',
        r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b',
        r'\b(?:el|la)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)\b'
    ]

    names = set()
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                for name in match:
                    if len(name) > 2:  # Filtrar nombres muy cortos
                        names.add(name.strip())
            else:
                if len(match) > 2:
                    names.add(match.strip())

    return list(names)

def slugify(text, max_words=4, person_names=None):
    """Convierte un texto en un slug para el nombre de archivo, incluyendo nombres de personas."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    words = text.split()

    # Si hay nombres de personas, incluirlos al principio
    if person_names:
        name_slug = '-'.join(person_names[:2])  # Máximo 2 nombres
        remaining_words = words[:max_words-1] if len(words) > max_words-1 else words
        return f"{name_slug}-{'-'.join(remaining_words)}"
    else:
        return '-'.join(words[:max_words])

def parse_output(generated_text):
    """Extrae título, texto, enlaces y bluesky del resultado generado."""
    titulo = texto = bluesky = None
    enlaces = []
    lines = generated_text.splitlines()
    buffer = []
    mode = None

    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            continue

        if line.startswith('Título:'):
            titulo = line.replace('Título:', '').strip()
            mode = None
        elif line.startswith('Texto:'):
            mode = 'texto'
            buffer = []
            # Check if there's text on the same line after "Texto:"
            text_part = line.replace('Texto:', '').strip()
            if text_part:
                buffer.append(text_part)
        elif line.startswith('Enlaces:'):
            mode = 'enlaces'
            enlaces = []
        elif line.startswith('Bluesky:'):
            bluesky = line.replace('Bluesky:', '').strip()
            mode = None
        elif mode == 'texto':
            buffer.append(line)
        elif mode == 'enlaces' and line.startswith('-'):
            enlaces.append(line)

    if buffer:
        texto = '\n'.join(buffer).strip()

    return titulo, texto, bluesky, enlaces

@click.group()
@click.version_option()
def cli():
    """
    A simple CLI to manage news.
    """
    setup_logging()

# @click.group()
# def main():
#     """
#     A simple CLI to manage news.
#     """
#     pass

@cli.command()
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
@click.option(
    '--output-dir',
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help='Directorio donde guardar los archivos generados (por defecto: usa NEWS_OUTPUT_DIR o no guarda archivos)'
)
def generate(input_file, url, prompt_extra, interactive_prompt, output_dir):
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

        # Si la URL es de diis.unizar.es, solo generamos la entrada de Bluesky
        solo_bluesky = url and 'diis.unizar.es' in url

        if solo_bluesky:
            # Generar solo la entrada de Bluesky
            client = GeminiClient()
            # El prompt solo pide el texto para Bluesky
            bluesky_prompt = (
                'Genera únicamente un post breve (máximo 300 caracteres) para la red social Bluesky, '
                'con tono neutro e informativo, mencionando a los protagonistas '
                'y terminando con el enlace a la noticia: ' + url
            )
            generated_text = client.generate_news(input_text, bluesky_prompt, url)
            # Extraer solo el campo bluesky
            _, _, bluesky, _ = parse_output(generated_text)
            if bluesky and url:
                bluesky = bluesky.replace('[enlace a la noticia]', url)
            output_lines = [f'Bluesky: {bluesky}'] if bluesky else []
            click.echo('\n'.join(output_lines))
        else:
            # Flujo normal: generar solo noticia (sin bluesky)
            client = GeminiClient()
            generated_text = client.generate_news(input_text, prompt_extra, url)
            titulo, texto, bluesky, enlaces = parse_output(generated_text)
            output_lines = []
            if titulo:
                output_lines.append(f'Título: {titulo}')
            if texto:
                output_lines.append(f'Texto: {texto}')
            if enlaces:
                output_lines.append('Enlaces:')
                output_lines.extend(enlaces)
            click.echo('\n'.join(output_lines))

        # Determinar directorio de salida
        final_output_dir = None
        if output_dir:
            final_output_dir = output_dir
        else:
            env_output_dir = os.getenv('NEWS_OUTPUT_DIR')
            if env_output_dir:
                final_output_dir = Path(env_output_dir)

        # Guardar archivos si se especifica output_dir
        if final_output_dir:
            hoy = datetime.now().date()
            hoy_str = hoy.strftime('%Y-%m-%d')
            # Si solo bluesky, no guardar noticia
            if not solo_bluesky:
                # Extraer nombres de personas del título y texto
                if titulo and texto:
                    person_names = extract_person_names(titulo + " " + texto)
                else:
                    person_names = []
                fecha = siguiente_laborable(hoy)
                fecha_str = fecha.strftime('%Y-%m-%d')
                slug = slugify(titulo, max_words=3, person_names=person_names)
                base_name = f"{fecha_str}-{slug}"
                final_output_dir.mkdir(parents=True, exist_ok=True)
                noticia_path = final_output_dir / f"{base_name}.txt"
                with open(noticia_path, 'w', encoding='utf-8') as f:
                    f.write(f"Título: {titulo}\n\nTexto: {texto}\n")
                    if enlaces:
                        f.write(f"\nEnlaces:\n")
                        for enlace in enlaces:
                            f.write(f"{enlace}\n")
                click.echo(f"Noticia guardada en: {noticia_path}")
            else:
                # Solo bluesky, usar input_text para slug
                slug = slugify(input_text, max_words=3)
                blsky_path = final_output_dir / f"{hoy_str}-{slug}_blsky.txt"
                if bluesky:
                    with open(blsky_path, 'w', encoding='utf-8') as f:
                        f.write(bluesky + '\n')
                    click.echo(f"Bluesky guardado en: {blsky_path}")

    except (ValueError, RuntimeError) as e:
        click.echo(f"Error: {e}", err=True)
    except PermissionError:
        click.echo(f"Error: No tienes permisos para leer el archivo {file_path}", err=True)
    except Exception as e:
        click.echo(f"Error inesperado: {e}", err=True)


if __name__ == '__main__':
    cli()
