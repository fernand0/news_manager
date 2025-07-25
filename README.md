# News Manager

A command-line interface (CLI) that uses the Gemini API to generate news articles from a text file or a URL.

## Configuration

### 1. API Key

This project uses the Google Gemini API. You need to provide your API key in an environment file.

1.  Create a file named `.env` in the root of the project.
2.  Add your API key to the file like this:

    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

> **Note:** The `.env` file is included in `.gitignore` and should not be committed to your repository.

### 2. Input File Configuration (Optional)

You can configure a default input file using an environment variable:

```bash
# In your .env file
NEWS_INPUT_FILE="/path/to/your/default/file.txt"
```

Or set it in your shell:
```bash
export NEWS_INPUT_FILE="/path/to/your/default/file.txt"
```

### 3. Output Directory Configuration (Optional)

You can configure a default output directory for saving generated files using an environment variable:

```bash
# In your .env file
NEWS_OUTPUT_DIR="/path/to/your/output/directory"
```

Or set it in your shell:
```bash
export NEWS_OUTPUT_DIR="/path/to/your/output/directory"
```

When this variable is set, the generated news and Bluesky files will be automatically saved to this directory without needing to specify `--output-dir` each time.

## Installation

First, clone the repository and navigate into the project directory:

```bash
git clone https://github.com/fernand0/news_manager.git
cd news_manager
```

### 1. Create a Virtual Environment

It is highly recommended to use a virtual environment.

**Using `venv`:**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Using `uv`:**
```bash
uv venv
source .venv/bin/activate
```

### 2. Install the CLI and Dependencies

Install the project in "editable" mode, which also installs all the necessary dependencies defined in `pyproject.toml`.

**Using `pip`:**
```bash
pip install -e .
```

**Using `uv`:**
```bash
uv pip install -e .
```

## Usage

### `generate`

Generates a news story by sending the content of an input file or a URL to the Gemini API.

**Input options (exclusive):**

- `--input-file` / `-i`: Local text file
- `--url`: URL of an online news article

**Customization options:**

- `--prompt-extra`: Additional instructions to customize the generation
- `--interactive-prompt`: Interactive mode to add custom instructions
- `--output-dir`: Directory to save the generated files (default: uses NEWS_OUTPUT_DIR or does not save files)

> **Note:** You cannot use both input options at the same time. If you use both, the command will show an error.

**Usage examples:**

1. **From a local file**
   ```bash
   python -m news_manager generate --input-file ./my_news.txt
   # or
   python -m news_manager generate -i ./my_news.txt
   ```

2. **From a URL**
   ```bash
   python -m news_manager generate --url "https://www.bbc.com/news/world-xxxxxx"
   ```

3. **Default file**
   ```bash
   python -m news_manager generate
   # It will use /tmp/noticia.txt or the file configured in NEWS_INPUT_FILE
   ```

4. **With custom instructions**
   ```bash
   # Focus on a specific person
   python -m news_manager generate --url "https://example.com/news" --prompt-extra "focus on María Santos and ignore the rest"
   
   # Focus on a particular aspect
   python -m news_manager generate -i news.txt --prompt-extra "focus only on the technological aspects"
   
   # Change the tone
   python -m news_manager generate --url "https://example.com" --prompt-extra "use a more formal and academic tone"
   
   # Interactive mode (you will be asked for instructions)
   python -m news_manager generate --url "https://example.com" --interactive-prompt
   ```

5. **Saving generated files**
   ```bash
   # Specify output directory manually
   python -m news_manager generate --url "https://example.com" --output-dir ./my_news
   
   # Use directory configured in NEWS_OUTPUT_DIR
   export NEWS_OUTPUT_DIR="/home/user/news"
   python -m news_manager generate --url "https://example.com"
   # Files will be automatically saved in /home/user/news
   ```

### Special format for theses

When the generated news corresponds to a doctoral thesis, the system produces:
- **Title:** In the form `PhD Thesis Defense of [name] [first surname], "[thesis title]"`.
- **Slug/URL:** The generated file will include the author's name and first surname, followed by keywords from the thesis title.

**Example:**

- Generated title:
  ```
  PhD Thesis Defense of Name Surname, "The Title"
  ```
- Generated file:
  ```
  2025-07-15-name-surname-the-title.txt
  ```

This facilitates the identification and access to thesis news, and improves the readability of files and URLs.

**Advanced options:**
```bash
# See command help
python -m news_manager generate --help
```

**Example Output:**

The output will be the formatted news article generated by the Gemini API.
```
--- Initializing AI client and generating news... ---
Title: New species of luminescent butterfly discovered in the Amazon by doctors Alistair Finch and Elena Vance
Text: Dr. Alistair Finch, a biologist from Greendale University, along with Dr. Elena Vance, has announced the discovery of a new species of butterfly that glows in the dark in the Amazon rainforest. This finding has been published in a recent scientific study.

The research details the unique characteristics of this insect, which uses bioluminescence as a possible defense and communication mechanism. Dr. Finch has dedicated more than a decade to the study of entomology in the region, while Dr. Vance is an expert in insect genetics. Greendale University has financed a large part of this expedition.
Links:
- https://example.com/original-news
Bluesky: A new species of luminescent butterfly has been discovered in the Amazon by doctors Alistair Finch and Elena Vance. This incredible finding opens new doors for bioluminescence research. #science #nature #discovery [link to news]
```

### `hello`

Prints a welcome message to confirm that the `news-manager` CLI is correctly installed and accessible in your environment.

**How to run:**
```bash
python -m news_manager hello
```

**Example Output:**
```
Welcome to News Manager CLI!
This tool helps you generate and manage news content using the Gemini API.
Try 'python -m news_manager generate' to create a news story or 'python -m news_manager --help' for more commands.
```

---

## About This Project

This project was developed using a collaborative approach with AI tools:

- **[Google Gemini AI](https://developers.google.com/gemini/ai-hub/docs/cli)**: Used for the AI-powered news generation functionality and initial development
- **[Cursor](https://cursor.sh/)**: The world's best AI-powered code editor was used for pair programming, code generation, and iterative development

The development process involved a conversational flow to build, refactor, and enhance the application step by step, leveraging the strengths of both tools for optimal code quality and functionality.

## 🌐 Website

Visit our beautiful website to learn more about News Manager:

**[📰 News Manager Website](https://fernand0.github.io/news_manager/)**

The website features:
- ✨ Modern, responsive design
- 📱 Mobile-friendly interface
- 🚀 Interactive examples
- 📊 Live demonstrations
- 🛠️ Complete documentation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Publish to Bluesky

The project includes an auxiliary CLI to publish posts to Bluesky from the files generated by News Manager.

### Project Structure

- `news_manager/`: Main package for news generation and main CLI.
- `news_publisher/`: Auxiliary tools for publishing to Bluesky (own CLI).

### Configuration

1. **Post search directory**
   - By default, the CLI searches for `*_blsky.txt` files in the directory configured in the `BLUESKY_POSTS_DIR` variable of your `.env`:
     ```
     BLUESKY_POSTS_DIR=/path/to/your/directory
     ```
   - If not defined, it will use the current directory.
   - You can override it with the `--dir` argument.

2. **Bluesky User**
   - By default, the last profile defined in `~/.mySocial/config/.rssBlsk` is used.
   - You can override it with the `--user` argument.

### Usage

To publish the last generated post to Bluesky, you can use `uv run` or execute the module directly:

**Using `uv run`:**
```bash
uv run news_publisher publish
```

**Executing the module:**
```bash
python -m news_publisher publish
```

Options:
- `--dir /path/to/files` to specify the search directory.
- `--user your_bluesky_user` to specify the Bluesky user.

**Example:**
```bash
uv run news_publisher publish --dir /home/user/news --user myuser
```

The CLI will show the content to be published and ask for confirmation before sending it to Bluesky.

### Requirements
- Have the `.env` file configured with the `BLUESKY_POSTS_DIR` variable if you want a default directory.
- Have the `~/.mySocial/config/.rssBlsk` file configured with your Bluesky credentials.
- Dependencies are managed automatically from `pyproject.toml`.

For specific conventions on the format of titles, slugs, and special rules (for example, for doctoral theses), see the [CONVENTIONES.md](CONVENCIONES.md) file.