import click
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
def generate():
    """
    Generates a news story from /tmp/noticia.txt by calling an LLM API.
    """
    try:
        # Read the input file first
        input_file = "/tmp/noticia.txt"
        with open(input_file, 'r') as f:
            input_text = f.read()

        click.echo("--- Initializing AI client and generating news... ---")
        
        # The CLI only knows about the generic client.
        # To switch to another AI, you would just change the line below.
        # For example: client = OpenAIClient()
        client = GeminiClient()
        
        # The client handles all the API-specific logic.
        generated_text = client.generate_news(input_text)
        
        click.echo(generated_text)

    except FileNotFoundError:
        click.echo(f"Error: Input file not found at {input_file}", err=True)
    except (ValueError, RuntimeError) as e:
        # Catch errors from our client (e.g., missing API key or API call failure)
        click.echo(f"Error: {e}", err=True)


if __name__ == '__main__':
    main()
