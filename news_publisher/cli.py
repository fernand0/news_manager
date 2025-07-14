import os
import sys
from pathlib import Path
import click
from configparser import ConfigParser
from dotenv import load_dotenv

def publish_bluesky(directory, user):
    load_dotenv()
    default_dir = os.getenv('BLUESKY_POSTS_DIR', '.')
    search_dir = directory or default_dir
    files = sorted(Path(search_dir).glob('*_blsky.txt'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        click.echo(f'No se encontró ningún archivo *_blsky.txt en el directorio {search_dir}.', err=True)
        sys.exit(1)
    last_file = files[0]
    click.echo(f'Archivo a publicar: {last_file}')
    with open(last_file, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    if not content:
        click.echo('El archivo está vacío.', err=True)
        sys.exit(1)
    click.echo('\n--- Contenido a publicar en Bluesky ---')
    click.echo(content)
    click.echo('--------------------------------------')
    if not click.confirm('¿Quieres publicar este contenido en Bluesky?', default=False):
        click.echo('Publicación cancelada.')
        sys.exit(0)
    if not user:
        config_path = os.path.expanduser('~/.mySocial/config/.rssBlsk')
        parser = ConfigParser()
        parser.read(config_path)
        if not parser.sections():
            click.echo('No se encontró ningún perfil en ~/.mySocial/config/.rssBlsk', err=True)
            sys.exit(1)
        user = parser.sections()[-1]
        click.echo(f'Usando usuario de Bluesky: {user}')
    try:
        from socialModules.configMod import getApi
    except ImportError:
        click.echo('No se pudo importar socialModules. ¿Está instalado y en el PYTHONPATH?', err=True)
        sys.exit(1)
    api = getApi('Bluesky', user)
    result = api.publishPost(content)
    click.echo(f'Respuesta de publicación: {result}')

@click.group()
def cli():
    """Herramientas para publicación en Bluesky"""
    pass

@cli.command()
@click.option('--dir', 'directory', default=None, help='Directorio donde buscar archivos *_blsky.txt (por defecto: BLUESKY_POSTS_DIR en .env o el actual)')
@click.option('--user', default=None, help='Usuario de Bluesky (si no se indica, se toma el último del fichero de configuración)')
def publish(directory, user):
    """Publica el último archivo *_blsky.txt en Bluesky usando social-modules."""
    publish_bluesky(directory, user)

if __name__ == '__main__':
    cli() 