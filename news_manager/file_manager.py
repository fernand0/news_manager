"""
File management module for News Manager.

This module handles saving generated news content to files with proper naming conventions.
"""

import os
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .news_generator import siguiente_laborable, extract_person_names, slugify
from .exceptions import FileOperationError, ValidationError
from .validators import InputValidator

logger = logging.getLogger(__name__)


class FileManager:
    """Handles saving generated news content to files."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the file manager.
        
        Args:
            output_dir: Directory to save files to. If None, files won't be saved.
            
        Raises:
            ValidationError: If output directory validation fails
        """
        self.output_dir = output_dir
        if self.output_dir:
            try:
                InputValidator.validate_directory_path(self.output_dir, create_if_missing=True)
            except ValidationError:
                raise
    
    def save_news_content(self, content: Dict[str, Any], input_text: str = "") -> Optional[Dict[str, Path]]:
        """
        Save generated news content to files.
        
        Args:
            content: Generated news content dictionary
            input_text: Original input text for slug generation
            
        Returns:
            Dictionary with paths of saved files, or None if no output directory
            
        Raises:
            FileOperationError: If file saving fails
        """
        if not self.output_dir:
            return None
        
        try:
            saved_files = {}
            
            # Handle Bluesky-only content
            if content.get('bluesky_only'):
                bluesky_path = self._save_bluesky_file(content['bluesky'], input_text)
                if bluesky_path:
                    saved_files['bluesky'] = bluesky_path
            else:
                # Save regular news content
                news_path = self._save_news_file(content)
                if news_path:
                    saved_files['news'] = news_path
            
            return saved_files
            
        except Exception as e:
            raise FileOperationError(
                f"Failed to save news content: {e}",
                operation="save"
            )
    
    def _save_news_file(self, content: Dict[str, Any]) -> Optional[Path]:
        """
        Save news content to a file.
        
        Args:
            content: News content dictionary
            
        Returns:
            Path to saved file, or None if no content to save
        """
        titulo = content.get('titulo')
        texto = content.get('texto')
        enlaces = content.get('enlaces', [])
        
        if not titulo or not texto:
            logger.warning("No title or text content to save")
            return None
        
        # Generate filename
        fecha = siguiente_laborable(datetime.now().date())
        fecha_str = fecha.strftime('%Y-%m-%d')
        
        # Generate slug based on content type
        slug = self._generate_news_slug(titulo, texto)
        
        filename = f"{fecha_str}-{slug}.txt"
        file_path = self.output_dir / filename
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"Título: {titulo}\n\nTexto: {texto}\n")
            if enlaces:
                f.write(f"\nEnlaces:\n")
                for enlace in enlaces:
                    f.write(f"{enlace}\n")
        
        logger.info(f"News saved to: {file_path}")
        return file_path
    
    def _save_bluesky_file(self, bluesky_content: str, input_text: str) -> Optional[Path]:
        """
        Save Bluesky content to a file.
        
        Args:
            bluesky_content: Bluesky post content
            input_text: Original input text for slug generation
            
        Returns:
            Path to saved file, or None if no content to save
        """
        if not bluesky_content:
            logger.warning("No Bluesky content to save")
            return None
        
        # Generate filename for Bluesky content
        today = datetime.now().date()
        today_str = today.strftime('%Y-%m-%d')
        
        # Use test slug if available, otherwise generate from input
        test_slug = os.getenv('NEWS_TEST_SLUG')
        if test_slug:
            slug = test_slug
        else:
            slug = slugify(input_text, max_words=3)
        
        filename = f"{today_str}-{slug}_blsky.txt"
        file_path = self.output_dir / filename
        
        # Write content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(bluesky_content + '\n')
        
        logger.info(f"Bluesky content saved to: {file_path}")
        return file_path
    
    def _generate_news_slug(self, titulo: str, texto: str) -> str:
        """
        Generate a slug for news content based on title and content.
        
        Args:
            titulo: News title
            texto: News text content
            
        Returns:
            Generated slug
        """
        # Check for test slug override
        test_slug = os.getenv('NEWS_TEST_SLUG')
        if test_slug:
            return test_slug
        
        # Special handling for thesis titles
        if titulo and titulo.startswith('Lectura de Tesis de'):
            return self._generate_thesis_slug(titulo)
        
        # Standard slug generation
        person_names = extract_person_names(titulo + " " + texto)
        return slugify(titulo, max_words=3, person_names=person_names)
    
    def _generate_thesis_slug(self, titulo: str) -> str:
        """
        Generate a slug specifically for thesis titles.
        
        Args:
            titulo: Thesis title
            
        Returns:
            Generated thesis slug
        """
        # Extract name and first surname from title
        match = re.match(r'Lectura de Tesis de ([A-Za-zÁÉÍÓÚáéíóúüÜñÑ]+) ([A-Za-zÁÉÍÓÚáéíóúüÜñÑ]+)', titulo)
        if match:
            nombre = match.group(1)
            apellido = match.group(2)
            slug = slugify(f"{nombre} {apellido}")
            
            # Add keywords from thesis title (between quotes)
            titulo_tesis = re.search(r'"([^"]+)"', titulo)
            if titulo_tesis:
                palabras = slugify(titulo_tesis.group(1), max_words=2)
                slug += '-' + palabras
            
            return slug
        else:
            # Fallback to standard slug generation
            return slugify(titulo, max_words=3)