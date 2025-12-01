import click
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from .utils import select_from_list, select_news_source
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
    help='Input file with the source text (default: /tmp/noticia.txt or NEWS_INPUT_FILE)'
)
@click.option(
    '--url',
    type=str,
    default=None,
    help='URL of a news article to download and generate the news from its content.'
)
@click.option(
    '--prompt-extra',
    type=str,
    default=None,
    help='Additional instructions to customize the generation (e.g., "focus on a specific person and ignore the rest")'
)
@click.option(
    '--interactive-prompt',
    is_flag=True,
    default=False,
    help='Enable interactive mode for additional instructions'
)
@click.option(
    '--output-dir',
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help='Directory to save the generated files (default: use NEWS_OUTPUT_DIR or do not save files)'
)
@click.option(
    '--user',
    default=None,
    help='Bluesky user to publish the post'
)
def generate(input_file, url, prompt_extra, interactive_prompt, output_dir, user):
    """
    Generates a news article from a file or a URL (exclusive options).

    The input file can be specified in three ways:
    1. With the --input-file parameter
    2. With the NEWS_INPUT_FILE environment variable
    3. By default, it uses /tmp/noticia.txt
    Alternatively, you can use --url to download a news article from the internet.

    The output directory can be specified in two ways:
    1. With the --output-dir parameter
    2. With the NEWS_OUTPUT_DIR environment variable

    You can use --prompt-extra to add custom instructions.
    Use --interactive-prompt to enable interactive mode.
    """
    try:
        # Validate exclusive options
        if input_file and url:
            click.echo("Error: You cannot use --input-file and --url at the same time. Choose only one option.", err=True)
            sys.exit(1)

        # Handle interactive prompt
        if interactive_prompt:
            prompt_extra = _handle_interactive_prompt()

        # Show additional instructions if provided
        if prompt_extra:
            click.echo(f"--- Additional instructions: {prompt_extra} ---")

        # Initialize components
        news_generator = NewsGenerator()
        output_dir_path = _determine_output_directory(output_dir)
        file_manager = FileManager(output_dir_path)

        click.echo("--- Initializing AI client and generating news... ---")

        # Determine the source and generate news content
        source_info = None
        input_text = ""
        
        # Check if we should use source selection
        if not input_file and not url:
            # Try source selection (interactive mode for choosing email/web)
            source_info = select_news_source()
            if source_info is None:
                click.echo("No source selected. Exiting.")
                sys.exit(0)
        
        # Generate news content based on source
        if source_info:
            click.echo(f"--- Processing from: {source_info['description']} ---")
            if source_info['type'] == 'email':
                content = news_generator.generate_from_text(source_info['content'], prompt_extra)
                input_text = source_info['content']
            elif source_info['type'] == 'web':
                click.echo(f"--- Downloading and extracting news from: {source_info['url']} ---")
                content = news_generator.generate_from_url(source_info['url'], prompt_extra)
                input_text = ""
        elif url:
            click.echo(f"--- Downloading and extracting news from: {url} ---")
            content = news_generator.generate_from_url(url, prompt_extra)
            input_text = ""  # Not needed for URL-based generation
        else:
            file_path = _determine_input_file(input_file, url)
            if not file_path:
                return
            click.echo(f"--- Reading file: {file_path} ---")
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
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


def _handle_bluesky_interactive(content: dict, user: str):
    """Handle the interactive workflow for Bluesky posts."""
    click.echo(f"\n--- Candidate for Bluesky post ---\n{content['bluesky']}\n")

    if click.confirm('Do you want to modify the post?', default=False):
        edited_text = click.edit(content['bluesky'])
        if edited_text is not None:
            content['bluesky'] = edited_text.strip()
            click.echo(f"\n--- Modified post ---\n{content['bluesky']}\n")

    if click.confirm('Do you want to publish the post on Bluesky?', default=True):
        publish_content(content['bluesky'], user)


def _handle_interactive_prompt() -> str:
    """Handle interactive prompt for additional instructions."""
    click.echo("\n--- Additional instructions ---")
    click.echo("Examples of instructions you can use:")
    click.echo("• 'focus on María Santos and ignore the rest'")
    click.echo("• 'focus only on the technological aspects'")
    click.echo("• 'use a more formal and academic tone'")
    click.echo("• 'especially highlight the achievements and awards obtained'")
    click.echo("• 'ignore the technical details and focus on the social impact'")
    click.echo("• (leave empty to not add instructions)")
    click.echo()

    return click.prompt(
        "What additional instructions do you want to add?",
        default="",
        type=str
    ).strip()


def _display_saved_files(saved_files: dict):
    """Display information about saved files."""
    if not saved_files:
        return

    for file_type, file_path in saved_files.items():
        if file_type == 'news':
            click.echo(f"News saved in: {file_path}")
        elif file_type == 'bluesky':
            click.echo(f"Bluesky saved in: {file_path}")


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
        output_lines.append(f"Title: {content['titulo']}")
    if content.get('texto'):
        output_lines.append(f"Text: {content['texto']}")
    if content.get('enlaces'):
        output_lines.append('Links:')
        output_lines.extend(content['enlaces'])

    if output_lines:
        click.echo('\n'.join(output_lines))


def _select_source_from_menu() -> Path:
    """
    Presents a menu to the user to select a source file.
    """
    news_sources_dir = Path.home() / "news_sources"
    if not news_sources_dir.exists():
        news_sources_dir.mkdir()

    sources = list(news_sources_dir.glob("*.txt"))
    if not sources:
        click.echo(f"No news sources found in {news_sources_dir}")
        return None

    _, selected_source = select_from_list([str(s) for s in sources])
    if not selected_source:
        return None
    return Path(selected_source)

def _determine_input_file(input_file: Path, url:str) -> Path:
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

    if not url and not file_path.exists():
        file_path = _select_source_from_menu()
        if not file_path:
            click.echo("No source selected. Exiting.")
            sys.exit(0)

    return file_path


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
