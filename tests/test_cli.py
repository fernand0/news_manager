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
def mock_gemini_client():
    with patch('news_manager.cli.GeminiClient') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.generate_news.return_value =(
            "Título: Noticia de Prueba\n"
            "Texto: Este es el texto de la noticia de prueba. " * 10 + "\n"
            "Enlaces:\n- https://example.com/link1\n"
            "Bluesky: Post de Bluesky de prueba."
        )
        yield mock_instance

@pytest.fixture
def mock_extract_main_text_from_url():
    with patch('news_manager.cli.extract_main_text_from_url') as mock_extract:
        mock_extract.return_value = "Contenido de la URL de prueba. " * 10 # Ensure it's long enough
        yield mock_extract

@pytest.fixture(autouse=False)
def mock_slugify_func():
    with patch('news_manager.cli.slugify') as mock_sf:
        mock_sf.return_value = "mocked-slug"
        yield mock_sf

@pytest.fixture
def mock_siguiente_laborable():
    with patch('news_manager.cli.siguiente_laborable') as mock_sl:
        mock_sl.return_value = date(2025, 7, 16) # Un día fijo para pruebas
        yield mock_sl

@pytest.fixture(autouse=True)
def mock_setup_logging():
    with patch('news_manager.cli.setup_logging') as mock_logging:
        yield mock_logging

class TestGenerateCommand:
    def test_generate_with_default_input_file(self, runner, mock_gemini_client, mock_siguiente_laborable):
        # Mock Path.exists and Path.is_file for /tmp/noticia.txt
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba del archivo.")):
            
            result = runner.invoke(cli, ['generate'])
            
            assert result.exit_code == 0
            assert "--- Leyendo archivo: /tmp/noticia.txt ---" in result.output
            assert "Título: Noticia de Prueba" in result.output
            assert "Texto: Este es el texto de la noticia de prueba." in result.output
            mock_gemini_client.generate_news.assert_called_once()

    def test_generate_with_input_file_option(self, runner, mock_gemini_client, mock_siguiente_laborable):
        test_file_path = "/tmp/my_custom_input.txt"
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba del archivo custom.")):
            
            result = runner.invoke(cli, ['generate', '-i', test_file_path])
            
            assert result.exit_code == 0
            assert f"--- Leyendo archivo: {test_file_path} ---" in result.output
            assert "Título: Noticia de Prueba" in result.output
            mock_gemini_client.generate_news.assert_called_once()

    def test_generate_with_url_option(self, runner, mock_gemini_client, mock_extract_main_text_from_url):
        test_url = "https://example.com/news"
        result = runner.invoke(cli, ['generate', '--url', test_url])
        
        assert result.exit_code == 0
        assert f"--- Descargando y extrayendo noticia de: {test_url} ---" in result.output
        assert "Título: Noticia de Prueba" in result.output
        mock_extract_main_text_from_url.assert_called_once_with(test_url)
        mock_gemini_client.generate_news.assert_called_once()

    def test_generate_exclusive_options_error(self, runner):
        result = runner.invoke(cli, ['generate', '-i', '/tmp/file.txt', '--url', 'http://example.com'])
        assert result.exit_code != 0
        assert "Error: No puedes usar --input-file y --url al mismo tiempo." in result.output

    def test_generate_with_prompt_extra(self, runner, mock_gemini_client, mock_siguiente_laborable):
        test_prompt = "Enfócate en los detalles técnicos."
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba.")):
            
            result = runner.invoke(cli, ['generate', '--prompt-extra', test_prompt])
            
            assert result.exit_code == 0
            assert f"--- Instrucciones adicionales: {test_prompt} ---" in result.output
            mock_gemini_client.generate_news.assert_called_once_with("Contenido de prueba.", test_prompt, None)

    def test_generate_with_interactive_prompt(self, runner, mock_gemini_client, mock_siguiente_laborable):
        test_prompt = "Instrucción interactiva."
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba.")):
            
            result = runner.invoke(cli, ['generate', '--interactive-prompt'], input=test_prompt + '\n')
            
            assert result.exit_code == 0
            assert "--- Instrucciones adicionales ---" in result.output
            assert f"--- Instrucciones adicionales: {test_prompt} ---" in result.output
            mock_gemini_client.generate_news.assert_called_once_with("Contenido de prueba.", test_prompt, None)

    def test_generate_with_output_dir(self, runner, mock_gemini_client, mock_siguiente_laborable, mock_slugify_func):
        test_output_dir = "/tmp/output_news"
        # Usamos NEWS_TEST_SLUG para forzar el slug esperado en el nombre del archivo
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba.")) as mocked_open, \
             patch('pathlib.Path.mkdir') as mocked_mkdir, \
             patch.dict(os.environ, {"NEWS_TEST_SLUG": "noticia-de-prueba"}):
            
            result = runner.invoke(cli, ['generate', '--output-dir', test_output_dir])
            
            assert result.exit_code == 0
            mocked_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mocked_open.assert_called_with(Path(f"{test_output_dir}/2025-07-16-noticia-de-prueba.txt"), 'w', encoding='utf-8')
            assert "Noticia guardada en:" in result.output

    def test_generate_with_news_input_file_env_var(self, runner, mock_gemini_client, mock_siguiente_laborable, mock_env_vars):
        os.environ['NEWS_INPUT_FILE'] = "/tmp/env_input.txt"
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba desde ENV.")):
            
            result = runner.invoke(cli, ['generate'])
            
            assert result.exit_code == 0
            assert "--- Leyendo archivo: /tmp/env_input.txt ---" in result.output
            mock_gemini_client.generate_news.assert_called_once()

    def test_generate_with_news_output_dir_env_var(self, runner, mock_gemini_client, mock_siguiente_laborable, mock_env_vars, mock_slugify_func):
        os.environ['NEWS_OUTPUT_DIR'] = "/tmp/env_output_news"
        # Usamos NEWS_TEST_SLUG para forzar el slug esperado en el nombre del archivo
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba.")) as mocked_open, \
             patch('pathlib.Path.mkdir') as mocked_mkdir, \
             patch.dict(os.environ, {"NEWS_TEST_SLUG": "noticia-de-prueba"}):
            
            result = runner.invoke(cli, ['generate'])
            
            assert result.exit_code == 0
            mocked_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mocked_open.assert_called_with(Path(f"/tmp/env_output_news/2025-07-16-noticia-de-prueba.txt"), 'w', encoding='utf-8')
            assert "Noticia guardada en:" in result.output

    def test_generate_url_diis_unizar_solo_bluesky(self, runner, mock_gemini_client, mock_extract_main_text_from_url):
        test_url = "https://diis.unizar.es/some-news"
        mock_gemini_client.generate_news.return_value = "Bluesky: Post de Bluesky para DIIS."
        
        result = runner.invoke(cli, ['generate', '--url', test_url])
        
        assert result.exit_code == 0
        assert "Bluesky: Post de Bluesky para DIIS." in result.output
        mock_gemini_client.generate_news.assert_called_once()
        # Ensure it calls with the specific bluesky prompt
        args, kwargs = mock_gemini_client.generate_news.call_args
        assert "Genera únicamente un post breve" in args[1]
        assert test_url in args[1]

    def test_generate_file_not_found_error(self, runner):
        with patch('pathlib.Path.exists', return_value=False):
            result = runner.invoke(cli, ['generate', '-i', '/nonexistent/file.txt'])
            assert result.exit_code != 0
            assert "Error: El archivo no existe: /nonexistent/file.txt" in result.output

    def test_generate_path_is_not_file_error(self, runner):
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=False):
            result = runner.invoke(cli, ['generate', '-i', '/tmp/not_a_file'])
            assert result.exit_code != 0
            assert "Error: La ruta especificada no es un archivo: /tmp/not_a_file" in result.output

    def test_generate_empty_input_file_error(self, runner):
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="")):
            result = runner.invoke(cli, ['generate', '-i', '/tmp/empty.txt'])
            assert result.exit_code != 0
            assert "Error: El archivo /tmp/empty.txt está vacío." in result.output

    def test_generate_url_extraction_error(self, runner, mock_extract_main_text_from_url):
        mock_extract_main_text_from_url.side_effect = Exception("Error de red simulado.")
        result = runner.invoke(cli, ['generate', '--url', 'http://bad.url'])
        assert result.exit_code != 0
        assert "Error al procesar la URL: Error de red simulado." in result.output

    def test_generate_url_empty_content_error(self, runner, mock_extract_main_text_from_url):
        mock_extract_main_text_from_url.return_value = "   " # Less than 100 chars after strip
        result = runner.invoke(cli, ['generate', '--url', 'http://empty.url'])
        assert result.exit_code != 0
        assert "Error: No se pudo extraer suficiente texto de la URL proporcionada." in result.output

    def test_generate_unicode_decode_error(self, runner):
        with patch('news_manager.cli.open', side_effect=UnicodeDecodeError('utf-8', b'\x80', 0, 1, 'invalid start byte')):
            result = runner.invoke(cli, ['generate', '-i', '/tmp/bad_encoding.txt'])
            assert result.exit_code != 0
            assert "Error: No se puede leer el archivo /tmp/bad_encoding.txt. Verifica que sea un archivo de texto válido." in result.output

    def test_generate_permission_error(self, runner):
        with patch('news_manager.cli.open', side_effect=PermissionError):
            result = runner.invoke(cli, ['generate', '-i', '/tmp/no_permission.txt'])
            assert result.exit_code != 0
            assert "Error: No tienes permisos para leer el archivo /tmp/no_permission.txt" in result.output

    def test_generate_general_exception(self, runner):
        with patch('pathlib.Path.exists', side_effect=Exception("Error inesperado de Path.")):
            result = runner.invoke(cli, ['generate', '-i', '/tmp/any_file.txt'])
            assert result.exit_code != 0
            assert "Error inesperado: Error inesperado de Path." in result.output

    @pytest.mark.usefixtures('mock_gemini_client', 'mock_siguiente_laborable')
    def test_generate_thesis_slug_generation(self, runner):
        test_output_dir = "/tmp/output_thesis"
        from unittest.mock import patch, mock_open
        # No usamos el mock de slugify aquí para que se use la función real
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('builtins.open', mock_open(read_data="Contenido de prueba.")) as mocked_open, \
             patch('pathlib.Path.mkdir') as mocked_mkdir, \
             patch('news_manager.cli.GeminiClient') as mock_client, \
             patch('news_manager.cli.siguiente_laborable') as mock_siguiente_laborable:
            mock_client.return_value.generate_news.return_value = (
                'Título: Lectura de Tesis de Juan Pérez "Un Título Interesante"\n'
                'Texto: Contenido de la tesis.\n'
            )
            mock_siguiente_laborable.return_value = date(2025, 7, 16)
            result = runner.invoke(cli, ['generate', '--output-dir', test_output_dir])
            assert result.exit_code == 0
            mocked_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            # Check for the specific slug format for thesis
            mocked_open.assert_called_with(Path(f"{test_output_dir}/2025-07-16-juan-perez-un-titulo.txt"), 'w', encoding='utf-8')
            assert "Noticia guardada en:" in result.output

    def test_generate_bluesky_output_saved(self, runner, mock_gemini_client, mock_extract_main_text_from_url, mock_slugify_func):
        test_output_dir = "/tmp/output_bluesky"
        test_url = "https://diis.unizar.es/some-news"
        mock_gemini_client.generate_news.return_value = "Bluesky: Post de Bluesky para DIIS."
        from datetime import date
        # Usamos NEWS_TEST_SLUG para forzar el slug esperado en el nombre del archivo
        with patch('pathlib.Path.mkdir') as mocked_mkdir, \
             patch('builtins.open', mock_open()) as mocked_open, \
             patch.dict(os.environ, {"NEWS_TEST_SLUG": "contenido-de-la.txt"}):
            result = runner.invoke(cli, ['generate', '--url', test_url, '--output-dir', test_output_dir])
            assert result.exit_code == 0
            mocked_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mocked_open.assert_called_with(Path(f"{test_output_dir}/{date.today().strftime('%Y-%m-%d')}-contenido-de-la.txt_blsky.txt"), 'w', encoding='utf-8')
            assert "Bluesky guardado en:" in result.output