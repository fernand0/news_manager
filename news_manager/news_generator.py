"""
News generation module for News Manager.

This module handles the core logic for generating news articles from input content.
"""

import os
import re
import unicodedata
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import logging

from .llm import GeminiClient
from .web_extractor import WebContentExtractor
from .exceptions import NewsManagerError, ValidationError, ContentProcessingError, APIError, NetworkError, FileOperationError
from .validators import InputValidator

logger = logging.getLogger(__name__)


# NewsGenerationError removed - using specific exceptions from exceptions.py


class NewsGenerator:
    """Handles the generation of news articles from various input sources."""
    
    def __init__(self):
        """Initialize the news generator with required clients."""
        self.llm_client = GeminiClient()
        self.web_extractor = WebContentExtractor()
    
    def generate_from_file(self, file_path: Path, prompt_extra: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate news from a text file.
        
        Args:
            file_path: Path to the input text file
            prompt_extra: Additional instructions for the AI
            
        Returns:
            Dictionary containing generated content
            
        Raises:
            ContentProcessingError: If generation fails
        """
        try:
            content = self._read_file_content(file_path)
            return self._generate_news_content(content, prompt_extra)
        except Exception as e:
            raise ContentProcessingError(f"Failed to generate news from file {file_path}: {e}")
    
    def generate_from_text(self, text_content: str, prompt_extra: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate news from direct text content (e.g., from email).
        
        Args:
            text_content: Text content to generate news from
            prompt_extra: Additional instructions for the AI
            
        Returns:
            Dictionary containing generated content
            
        Raises:
            ContentProcessingError: If generation fails
        """
        try:
            if not text_content or len(text_content.strip()) < 10:
                raise ValidationError("Text content is too short or empty")
            return self._generate_news_content(text_content, prompt_extra)
        except Exception as e:
            raise ContentProcessingError(f"Failed to generate news from text: {e}")
    
    def generate_from_url(self, url: str, prompt_extra: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate news from a URL.
        
        Args:
            url: URL to extract content from
            prompt_extra: Additional instructions for the AI
            
        Returns:
            Dictionary containing generated content
            
        Raises:
            ContentProcessingError: If generation fails
            ValidationError: If input validation fails
        """
        try:
            content = self.web_extractor.extract_content(url)
            
            # Special handling for DIIS URLs (only generate Bluesky content)
            if 'diis.unizar.es' in url:
                return self._generate_bluesky_only(content, url)
            
            return self._generate_news_content(content, prompt_extra, url)
        except (ValidationError, ContentProcessingError, NetworkError) as e:
            raise ContentProcessingError(f"Failed to extract content from URL: {e}")
        except Exception as e:
            raise ContentProcessingError(f"Failed to generate news from URL {url}: {e}")
    
    def _read_file_content(self, file_path: Path) -> str:
        """
        Read and validate file content.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string
            
        Raises:
            ContentProcessingError: If file reading fails
        """
        try:
            # Use validators for comprehensive file validation
            InputValidator.validate_file_path(file_path, must_exist=True, must_be_readable=True)
            InputValidator.validate_file_content(file_path, min_length=10)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            return content
            
        except (ValidationError, FileOperationError) as e:
            raise ContentProcessingError(str(e))
        except Exception as e:
            raise ContentProcessingError(f"Unexpected error reading file {file_path}: {e}")
    
    def _generate_news_content(self, content: str, prompt_extra: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate complete news content using the LLM.

        Args:
            content: Input content to generate news from
            prompt_extra: Additional instructions for the AI
            url: Source URL if applicable

        Returns:
            Dictionary with parsed news components
        """
        logger.info("Generating news content with LLM")

        generated_text = self.llm_client.generate_news(content, prompt_extra, url)
        titulo, texto, bluesky, enlaces = self._parse_output(generated_text)

        # If there's a Bluesky post and a URL, replace placeholders with the actual URL
        if bluesky and url:
            bluesky = self._replace_url_placeholder(bluesky, url)

        return {
            'titulo': titulo,
            'texto': texto,
            'bluesky': bluesky,
            'enlaces': enlaces,
            'raw_output': generated_text
        }
    
    def _generate_bluesky_only(self, content: str, url: str) -> Dict[str, Any]:
        """
        Generate only Bluesky content for special URLs.
        
        Args:
            content: Input content
            url: Source URL
            
        Returns:
            Dictionary with only Bluesky content
        """
        logger.info("Generating Bluesky-only content for DIIS URL")
        
        bluesky_prompt = (
            'Generate only a short post (maximum 300 characters) for the Bluesky social network, '
            'with a neutral and informative tone, mentioning the protagonists with only one surname, '
            'the date (you can abbreviate it as dd/mm hh; if it is an hour on the dot you do not need '
            'to put the :00)) and the place (for example, abc seminar in xyz) '
            'if it is a thesis follow the scheme: "PhD Thesis of [Name] [Surname], [dd]/[m] [hh]h, '
            '[local] the defense of the thesis "[Title]" will take place '
            'and ending with the link to the news: ' + url
        )
        
        generated_text = self.llm_client.generate_news(content, bluesky_prompt, url)
        _, _, bluesky, _ = self._parse_output(generated_text)
        
        if bluesky and url:
            bluesky = self._replace_url_placeholder(bluesky, url)
        
        return {
            'titulo': None,
            'texto': None,
            'bluesky': bluesky,
            'enlaces': [],
            'raw_output': generated_text,
            'bluesky_only': True
        }
    
    def _parse_output(self, generated_text: str) -> Tuple[Optional[str], Optional[str], Optional[str], List[str]]:
        """
        Parse the generated text into structured components.
        
        Args:
            generated_text: Raw text output from the LLM
            
        Returns:
            Tuple containing (title, text, bluesky_post, links)
        """
        titulo = texto = bluesky = None
        enlaces = []
        lines = generated_text.splitlines()
        buffer = []
        mode = None

        for line in lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            if line.startswith('Title:'):
                titulo = line.replace('Title:', '').strip()
                mode = None
            elif line.startswith('Text:'):
                mode = 'texto'
                buffer = []
                # Check if there's text on the same line after "Texto:"
                text_part = line.replace('Text:', '').strip()
                if text_part:
                    buffer.append(text_part)
            elif line.startswith('Links:'):
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

    def _replace_url_placeholder(self, text: str, url: str) -> str:
        """
        Replace URL placeholders in text with the actual URL, with validation.
        
        Args:
            text: Text that may contain URL placeholders
            url: The URL to replace placeholders with
            
        Returns:
            Text with URL placeholders replaced
        """
        import re
        
        # Validate URL format
        if not self._is_valid_url(url):
            logger.warning(f"Invalid URL format: {url}")
            return text  # Return original text without replacement
            
        # Define possible placeholders
        placeholders = [
            r'\[link to the news\]',
            r'\[link to news\]',
            r'\[news link\]',
            r'\[enlace a la noticia\]',
            r'\[enlace a la noticia\]',
            r'\[noticia\]'
        ]
        
        # Replace any of the placeholders with the URL
        for placeholder in placeholders:
            text = re.sub(placeholder, url, text, flags=re.IGNORECASE)
            
        # Also handle cases where the URL might already be present but malformed
        # Clean up any duplicate or malformed URLs
        text = self._clean_urls(text)
        
        return text
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate if the given string is a properly formatted URL.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL is valid, False otherwise
        """
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # Domain name
            r'(?:/[^\s]*)?$'  # Optional path
        )
        return bool(url_pattern.match(url))
    
    def _clean_urls(self, text: str) -> str:
        """
        Clean up URLs in the text to prevent duplicates or formatting issues.
        
        Args:
            text: Text that may contain URLs
            
        Returns:
            Cleaned text
        """
        import re
        
        # Replace multiple consecutive identical URLs with a single one
        # This regex finds a URL followed by whitespace and the same URL again
        # It repeats until no more duplicates are found
        prev_text = None
        while prev_text != text:
            prev_text = text
            # Look for a URL followed by any whitespace and the same URL again
            text = re.sub(r'(https?://[^\s]+)\s+\1', r'\1', text)
        
        # Ensure proper spacing around URLs
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        return text.strip()


def siguiente_laborable(fecha: date) -> date:
    """
    Get the next working day (Monday-Friday) from a given date.
    
    Args:
        fecha: Starting date
        
    Returns:
        Next working day
    """
    siguiente = fecha + timedelta(days=1)
    while siguiente.weekday() >= 5:  # 5=Saturday, 6=Sunday
        siguiente += timedelta(days=1)
    return siguiente


def extract_person_names(text: str) -> List[str]:
    """
    Extract person names from text using common patterns.
    
    Args:
        text: Text to extract names from
        
    Returns:
        List of extracted names
    """
    patterns = [
        r'\b(?:Dr\.|Dra\.|Prof\.|Profesora)\s+([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+(?:\s+[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)*)\b',
        r'\b([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)\s+(?:y|e)\s+([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)\b',
        r'\b([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)\s+([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)\b',
        r'\b(?:el|la)\s+([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)\s+([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)\b'
    ]

    names = set()
    for pattern in patterns:
        matches = re.findall(pattern, text, re.U)
        for match in matches:
            if isinstance(match, tuple):
                for name in match:
                    if len(name) > 2:  # Filter very short names
                        names.add(name.strip())
            else:
                if len(match) > 2:
                    names.add(match.strip())

    return list(names)


def slugify(text: str, max_words: int = 4, person_names: Optional[List[str]] = None) -> str:
    """
    Convert text to a slug for filename, including person names.
    
    Args:
        text: Text to convert to slug
        max_words: Maximum number of words in the slug
        person_names: List of person names to include
        
    Returns:
        Generated slug
    """
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    words = text.split()

    # If there are person names, include them at the beginning
    if person_names:
        name_slug = '-'.join(person_names[:2])  # Maximum 2 names
        remaining_words = words[:max_words-1] if len(words) > max_words-1 else words
        return f"{name_slug}-{'-'.join(remaining_words)}"
    else:
        return '-'.join(words[:max_words])