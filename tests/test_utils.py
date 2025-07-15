import pytest
from datetime import date, timedelta
from pathlib import Path
import tempfile
import os

# Import the functions we want to test
from news_manager.cli import slugify, extract_person_names, siguiente_laborable, parse_output


class TestSlugify:
    """Test the slugify function."""
    
    def test_basic_slugify(self):
        """Test basic slugify functionality."""
        result = slugify("Hello World Test")
        assert result == "hello-world-test"
    
    def test_slugify_with_special_chars(self):
        """Test slugify with special characters."""
        result = slugify("¡Hola! ¿Cómo estás?")
        assert result == "hola-como-estas"
    
    def test_slugify_with_numbers(self):
        """Test slugify with numbers."""
        result = slugify("Test 123 Numbers")
        assert result == "test-123-numbers"
    
    def test_slugify_with_person_names(self):
        """Test slugify with person names."""
        result = slugify("Test Title", person_names=["John", "Jane"])
        # The function adds person names to the slug, but they might be capitalized
        assert "John" in result or "john" in result
        assert "Jane" in result or "jane" in result
    
    def test_slugify_max_words(self):
        """Test slugify with max_words limit."""
        result = slugify("This is a very long title with many words", max_words=3)
        assert result == "this-is-a"
    
    def test_slugify_empty_string(self):
        """Test slugify with empty string."""
        result = slugify("")
        assert result == ""


class TestExtractPersonNames:
    """Test the extract_person_names function."""
    
    def test_extract_single_name(self):
        """Test extracting a single person name."""
        text = "El Dr. Carlos Ruiz ha desarrollado una nueva técnica."
        result = extract_person_names(text)
        assert "Carlos" in result
        assert "Ruiz" in result
    
    def test_extract_multiple_names(self):
        """Test extracting multiple person names."""
        text = "Los doctores María Santos y Juan García han colaborado en el proyecto."
        result = extract_person_names(text)
        # The function extracts individual names, not full names
        # It looks for patterns like "Dr. Name" or "Name Name"
        assert "María" in result or "Santos" in result
        assert "Juan" in result or "García" in result
    
    def test_extract_names_with_titles(self):
        """Test extracting names with academic titles."""
        text = "La Dra. Ana Martínez y el Dr. Miguel García han publicado sus hallazgos."
        result = extract_person_names(text)
        # The function extracts individual names from patterns
        # It might extract "Ana", "Martínez", "Miguel", "García" separately
        assert "Ana" in result or "Martínez" in result
        assert "Miguel" in result or "García" in result
    
    def test_extract_names_no_names(self):
        """Test extracting names when no names are present."""
        text = "Este es un texto sin nombres de personas."
        result = extract_person_names(text)
        assert result == []
    
    def test_extract_names_empty_text(self):
        """Test extracting names from empty text."""
        result = extract_person_names("")
        assert result == []


class TestSiguienteLaborable:
    """Test the siguiente_laborable function."""
    
    def test_monday_to_tuesday(self):
        """Test from Monday to Tuesday."""
        monday = date(2025, 1, 6)  # Monday
        result = siguiente_laborable(monday)
        assert result == date(2025, 1, 7)  # Tuesday
    
    def test_friday_to_monday(self):
        """Test from Friday to Monday."""
        friday = date(2025, 1, 10)  # Friday
        result = siguiente_laborable(friday)
        assert result == date(2025, 1, 13)  # Monday
    
    def test_saturday_to_monday(self):
        """Test from Saturday to Monday."""
        saturday = date(2025, 1, 11)  # Saturday
        result = siguiente_laborable(saturday)
        assert result == date(2025, 1, 13)  # Monday
    
    def test_sunday_to_monday(self):
        """Test from Sunday to Monday."""
        sunday = date(2025, 1, 12)  # Sunday
        result = siguiente_laborable(sunday)
        assert result == date(2025, 1, 13)  # Monday
    
    def test_weekday_to_next_day(self):
        """Test from any weekday to next day."""
        wednesday = date(2025, 1, 8)  # Wednesday
        result = siguiente_laborable(wednesday)
        assert result == date(2025, 1, 9)  # Thursday


class TestParseOutput:
    """Test the parse_output function."""
    
    def test_parse_complete_output(self):
        """Test parsing complete output with all sections."""
        text = """Título: Test Title
Texto: This is the main text content.
It has multiple lines.

Enlaces:
- https://example.com
- https://test.com

Bluesky: This is a bluesky post."""
        
        titulo, texto, bluesky, enlaces = parse_output(text)
        
        assert titulo == "Test Title"
        assert texto is not None
        assert "This is the main text content" in texto
        assert "It has multiple lines" in texto
        assert bluesky == "This is a bluesky post."
        assert len(enlaces) == 2
        assert "- https://example.com" in enlaces
        assert "- https://test.com" in enlaces
    
    def test_parse_output_without_enlaces(self):
        """Test parsing output without enlaces section."""
        text = """Título: Test Title
Texto: This is the main text content.

Bluesky: This is a bluesky post."""
        
        titulo, texto, bluesky, enlaces = parse_output(text)
        
        assert titulo == "Test Title"
        assert texto is not None
        assert "This is the main text content" in texto
        assert bluesky == "This is a bluesky post."
        assert enlaces == []
    
    def test_parse_output_without_bluesky(self):
        """Test parsing output without bluesky section."""
        text = """Título: Test Title
Texto: This is the main text content.

Enlaces:
- https://example.com"""
        
        titulo, texto, bluesky, enlaces = parse_output(text)
        
        assert titulo == "Test Title"
        assert texto is not None
        assert "This is the main text content" in texto
        assert bluesky is None
        assert len(enlaces) == 1
        assert "- https://example.com" in enlaces
    
    def test_parse_output_empty(self):
        """Test parsing empty output."""
        titulo, texto, bluesky, enlaces = parse_output("")
        
        assert titulo is None
        assert texto is None
        assert bluesky is None
        assert enlaces == []
    
    def test_parse_output_malformed(self):
        """Test parsing malformed output."""
        text = """Some random text without proper format."""
        
        titulo, texto, bluesky, enlaces = parse_output(text)
        
        assert titulo is None
        assert texto is None
        assert bluesky is None
        assert enlaces == []


class TestFileOperations:
    """Test file operations and CLI functionality."""
    
    def test_create_temp_file(self):
        """Test creating a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content for news generation.")
            temp_file = f.name
        
        try:
            # Verify file exists and has content
            assert Path(temp_file).exists()
            with open(temp_file, 'r') as f:
                content = f.read()
                assert "Test content" in content
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    


if __name__ == '__main__':
    pytest.main([__file__]) 