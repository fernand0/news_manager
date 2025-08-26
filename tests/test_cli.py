import pytest
from click.testing import CliRunner
from news_manager.cli import cli
from unittest.mock import patch, mock_open
import os
from pathlib import Path
from datetime import date, timedelta

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {}, clear=True):
        yield

@pytest.fixture(autouse=True)
def mock_os_path_checks():
    """Fixture to mock file system checks for tests."""
    original_exists = os.path.exists
    original_is_file = os.path.isfile
    original_access = os.access

    def mock_exists(path):
        if isinstance(path, str) and path.startswith('/tmp/'):
            return True
        return original_exists(path)

    def mock_is_file(path):
        if isinstance(path, str) and path == '/tmp/not_a_file':
            return False
        if isinstance(path, str) and path.startswith('/tmp/'):
            return True
        return original_is_file(path)

    def mock_access(path, mode):
        if isinstance(path, str) and path == '/tmp/no_permission.txt' and mode == os.R_OK:
            return False
        if isinstance(path, str) and path.startswith('/tmp/'):
            return True
        return original_access(path, mode)

    def mock_path_exists(self):
        return mock_exists(str(self))

    def mock_path_is_file(self):
        return mock_is_file(str(self))

    with patch('os.path.exists', side_effect=mock_exists), \
         patch('os.path.isfile', side_effect=mock_is_file), \
         patch('os.access', side_effect=mock_access), \
         patch('pathlib.Path.exists', new=mock_path_exists), \
         patch('pathlib.Path.is_file', new=mock_path_is_file):
        yield


@pytest.fixture
def mock_news_generator():
    with patch('news_manager.cli.NewsGenerator') as mock_generator_class:
        mock_instance = mock_generator_class.return_value
        mock_instance.generate_from_file.return_value = {
            'titulo': 'Noticia de Prueba',
            'texto': 'Este es el texto de la noticia de prueba. ' * 10,
            'bluesky': 'Post de Bluesky de prueba.',
            'enlaces': ['- https://example.com/link1'],
            'raw_output': 'Generated content'
        }
        mock_instance.generate_from_url.return_value = {
            'titulo': 'Noticia de Prueba',
            'texto': 'Este es el texto de la noticia de prueba. ' * 10,
            'bluesky': 'Post de Bluesky de prueba.',
            'enlaces': ['- https://example.com/link1'],
            'raw_output': 'Generated content'
        }
        yield mock_instance

@pytest.fixture
def mock_extract_main_text_from_url():
    with patch('news_manager.web_extractor.WebContentExtractor.extract_content') as mock_extract:
        mock_extract.return_value = "Contenido de la URL de prueba. " * 10 # Ensure it's long enough
        yield mock_extract

@pytest.fixture(autouse=False)
def mock_file_manager():
    with patch('news_manager.cli.FileManager') as mock_fm_class:
        mock_instance = mock_fm_class.return_value
        mock_instance.save_news_content.return_value = {
            'news': Path('/tmp/output/2025-07-16-noticia-de-prueba.txt')
        }
        yield mock_instance

@pytest.fixture(autouse=True)
def mock_setup_logging():
    with patch('news_manager.cli.setup_logging') as mock_logging:
        yield mock_logging

class TestGenerateCommand:
    def test_generate_with_default_input_file(self, runner, mock_news_generator):
        # Mock Path.exists and Path.is_file for /tmp/noticia.txt
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba del archivo.")):
            
            result = runner.invoke(cli, ['generate'])
            
            assert result.exit_code == 0
            assert "--- Leyendo archivo: /tmp/noticia.txt ---" in result.output
            assert "Título: Noticia de Prueba" in result.output
            assert "Texto: Este es el texto de la noticia de prueba." in result.output
            mock_news_generator.generate_from_file.assert_called_once()

    def test_generate_with_input_file_option(self, runner, mock_news_generator):
        test_file_path = "/tmp/my_custom_input.txt"
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba del archivo custom.")):
            
            result = runner.invoke(cli, ['generate', '-i', test_file_path])
            
            assert result.exit_code == 0
            assert f"--- Leyendo archivo: {test_file_path} ---" in result.output
            assert "Título: Noticia de Prueba" in result.output
            mock_news_generator.generate_from_file.assert_called_once()

    def test_generate_with_url_option(self, runner, mock_news_generator):
        test_url = "https://example.com/news"
        result = runner.invoke(cli, ['generate', '--url', test_url])
        
        assert result.exit_code == 0
        assert f"--- Descargando y extrayendo noticia de: {test_url} ---" in result.output
        assert "Título: Noticia de Prueba" in result.output
        mock_news_generator.generate_from_url.assert_called_once()

    def test_generate_exclusive_options_error(self, runner):
        result = runner.invoke(cli, ['generate', '-i', '/tmp/file.txt', '--url', 'http://example.com'])
        assert result.exit_code != 0
        assert "Error: No puedes usar --input-file y --url al mismo tiempo." in result.output

    def test_generate_with_prompt_extra(self, runner, mock_news_generator):
        test_prompt = "Enfócate en los detalles técnicos."
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba.")):
            
            result = runner.invoke(cli, ['generate', '--prompt-extra', test_prompt])
            
            assert result.exit_code == 0
            assert f"--- Instrucciones adicionales: {test_prompt} ---" in result.output
            # Check that generate_from_file was called with the prompt
            args, kwargs = mock_news_generator.generate_from_file.call_args
            assert test_prompt in args

    def test_generate_with_interactive_prompt(self, runner, mock_news_generator):
        test_prompt = "Instrucción interactiva."
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba.")):
            
            result = runner.invoke(cli, ['generate', '--interactive-prompt'], input=test_prompt + '\n')
            
            assert result.exit_code == 0
            assert "--- Instrucciones adicionales ---" in result.output
            assert f"--- Instrucciones adicionales: {test_prompt} ---" in result.output
            # Check that generate_from_file was called with the prompt
            args, kwargs = mock_news_generator.generate_from_file.call_args
            assert test_prompt in args

    def test_generate_with_output_dir(self, runner, mock_news_generator, mock_file_manager):
        test_output_dir = "/tmp/output_news"
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba.")):
            
            result = runner.invoke(cli, ['generate', '--output-dir', test_output_dir])
            
            assert result.exit_code == 0
            assert "Noticia guardada en:" in result.output
            mock_file_manager.save_news_content.assert_called_once()

    def test_generate_with_news_input_file_env_var(self, runner, mock_news_generator, mock_env_vars):
        os.environ['NEWS_INPUT_FILE'] = "/tmp/env_input.txt"
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba desde ENV.")):
            
            result = runner.invoke(cli, ['generate'])
            
            assert result.exit_code == 0
            assert "--- Leyendo archivo: /tmp/env_input.txt ---" in result.output
            mock_news_generator.generate_from_file.assert_called_once()

    def test_generate_with_news_output_dir_env_var(self, runner, mock_news_generator, mock_file_manager, mock_env_vars):
        os.environ['NEWS_OUTPUT_DIR'] = "/tmp/env_output_news"
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba.")):
            
            result = runner.invoke(cli, ['generate'])
            
            assert result.exit_code == 0
            assert "Noticia guardada en:" in result.output
            mock_file_manager.save_news_content.assert_called_once()

    def test_generate_url_diis_unizar_solo_bluesky(self, runner, mock_news_generator):
        test_url = "https://diis.unizar.es/some-news"
        mock_news_generator.generate_from_url.return_value = {
            'titulo': None,
            'texto': None,
            'bluesky': 'Post de Bluesky para DIIS.',
            'enlaces': [],
            'raw_output': 'Generated content',
            'bluesky_only': True
        }
        
        result = runner.invoke(cli, ['generate', '--url', test_url])
        
        assert result.exit_code == 0
        assert "Bluesky: Post de Bluesky para DIIS." in result.output
        mock_news_generator.generate_from_url.assert_called_once()

    def test_generate_file_not_found_error(self, runner, mock_news_generator):
        from news_manager.exceptions import ContentProcessingError
        mock_news_generator.generate_from_file.side_effect = ContentProcessingError("File does not exist")
        result = runner.invoke(cli, ['generate', '-i', '/nonexistent/file.txt'])
        assert result.exit_code != 0
        assert "Error:" in result.output

    def test_generate_path_is_not_file_error(self, runner, mock_news_generator):
        from news_manager.exceptions import ContentProcessingError
        mock_news_generator.generate_from_file.side_effect = ContentProcessingError("Path is not a file")
        result = runner.invoke(cli, ['generate', '-i', '/tmp/not_a_file'])
        assert result.exit_code != 0
        assert "Error:" in result.output

    def test_generate_empty_input_file_error(self, runner, mock_news_generator):
        from news_manager.exceptions import ContentProcessingError
        mock_news_generator.generate_from_file.side_effect = ContentProcessingError("File is empty")
        result = runner.invoke(cli, ['generate', '-i', '/tmp/empty.txt'])
        assert result.exit_code != 0
        assert "Error:" in result.output

    def test_generate_url_extraction_error(self, runner, mock_news_generator):
        from news_manager.exceptions import ContentProcessingError
        mock_news_generator.generate_from_url.side_effect = ContentProcessingError("Failed to extract content from URL")
        result = runner.invoke(cli, ['generate', '--url', 'http://bad.url'])
        assert result.exit_code != 0
        assert "Error:" in result.output

    def test_generate_url_empty_content_error(self, runner, mock_news_generator):
        from news_manager.exceptions import ContentProcessingError
        mock_news_generator.generate_from_url.side_effect = ContentProcessingError("Insufficient content extracted")
        result = runner.invoke(cli, ['generate', '--url', 'http://empty.url'])
        assert result.exit_code != 0
        assert "Error:" in result.output

    def test_generate_unicode_decode_error(self, runner, mock_news_generator):
        from news_manager.exceptions import ContentProcessingError
        mock_news_generator.generate_from_file.side_effect = ContentProcessingError("Cannot read file. Please verify it's a valid text file.")
        result = runner.invoke(cli, ['generate', '-i', '/tmp/bad_encoding.txt'])
        assert result.exit_code != 0
        assert "Error:" in result.output

    def test_generate_permission_error(self, runner, mock_news_generator):
        from news_manager.exceptions import ContentProcessingError
        mock_news_generator.generate_from_file.side_effect = ContentProcessingError("No permission to read file")
        result = runner.invoke(cli, ['generate', '-i', '/tmp/no_permission.txt'])
        assert result.exit_code != 0
        assert "Error:" in result.output

    def test_generate_general_exception(self, runner, mock_news_generator):
        mock_news_generator.generate_from_file.side_effect = Exception("Unexpected error")
        result = runner.invoke(cli, ['generate', '-i', '/tmp/any_file.txt'])
        assert result.exit_code != 0
        assert "Error inesperado:" in result.output

    def test_generate_thesis_slug_generation(self, runner, mock_news_generator, mock_file_manager):
        test_output_dir = "/tmp/output_thesis"
        mock_news_generator.generate_from_file.return_value = {
            'titulo': 'Lectura de Tesis de Juan Pérez "Un Título Interesante"',
            'texto': 'Contenido de la tesis.',
            'bluesky': 'Post de Bluesky de prueba.',
            'enlaces': [],
            'raw_output': 'Generated content'
        }
        mock_file_manager.save_news_content.return_value = {
            'news': Path(f"{test_output_dir}/2025-07-16-juan-perez-un-titulo.txt")
        }
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba.")):
            
            result = runner.invoke(cli, ['generate', '--output-dir', test_output_dir])
            assert result.exit_code == 0
            assert "Noticia guardada en:" in result.output
            mock_file_manager.save_news_content.assert_called_once()

    def test_generate_bluesky_output_saved(self, runner, mock_news_generator, mock_file_manager):
        test_output_dir = "/tmp/output_bluesky"
        test_url = "https://diis.unizar.es/some-news"
        mock_news_generator.generate_from_url.return_value = {
            'titulo': None,
            'texto': None,
            'bluesky': 'Post de Bluesky para DIIS.',
            'enlaces': [],
            'raw_output': 'Generated content',
            'bluesky_only': True
        }
        mock_file_manager.save_news_content.return_value = {
            'bluesky': Path(f"{test_output_dir}/2025-07-16-contenido-de-la_blsky.txt")
        }
        
        result = runner.invoke(cli, ['generate', '--url', test_url, '--output-dir', test_output_dir])
        assert result.exit_code == 0
        assert "Bluesky guardado en:" in result.output
        mock_file_manager.save_news_content.assert_called_once()