"""
Module to handle storage and retrieval of previous Bluesky posts.
"""

import os
import re
from pathlib import Path
from typing import List, Optional


class BlueskyHistoryManager:
    """
    Manages the history of published Bluesky posts by checking existing files in the cache directory.
    """

    def __init__(self, cache_dir_path: Optional[Path] = None):
        """
        Initialize the history manager.

        Args:
            cache_dir_path: Path to the cache directory. If None, uses default location.
        """
        if cache_dir_path:
            self.cache_dir = cache_dir_path
        else:
            # Default location: ~/Documents/work/webDiis/
            home_dir = Path.home()
            self.cache_dir = home_dir / "Documents" / "work" / "webDiis"
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def save_post(self, content: str, url: Optional[str] = None) -> bool:
        """
        Save a Bluesky post. This is a no-op since we're using existing files as history.
        
        Args:
            content: The content of the post
            url: The URL associated with the post (if any)

        Returns:
            True (always successful since we don't save anything new)
        """
        # We don't save anything new since we're using existing files as history
        return True

    def find_similar_bsky_files_by_url(self, url: str) -> List[Path]:
        """
        Find similar Bluesky files in the cache directory based on URL similarity in filenames.

        Args:
            url: URL to match against filenames

        Returns:
            List of file paths with similar names
        """
        similar_files = []
        
        # Extract meaningful parts from the URL to match against filenames
        # Get the last part of the URL path (after the last slash)
        url_parts = url.rstrip('/').split('/')
        if len(url_parts) > 1:
            url_slug = url_parts[-1]
            if len(url_slug) <= 3:  # If the last part is too short, use the previous one
                url_slug = url_parts[-2] if len(url_parts) > 2 else url_parts[-1]
        else:
            url_slug = url.split('/')[-1]
        
        # Look for all _blsky.txt files in the cache directory that contain the URL slug
        for file_path in self.cache_dir.glob(f"*{url_slug}*_blsky.txt"):
            similar_files.append(file_path)
        
        # If no files found with the exact slug, try a more relaxed matching
        if not similar_files:
            # Look for files that might contain parts of the URL
            for file_path in self.cache_dir.glob("*_blsky.txt"):
                # Extract date prefix (YYYY-MM-DD) and compare the rest
                filename = file_path.stem  # Remove .txt extension
                # Remove date prefix if present (YYYY-MM-DD format)
                name_part = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename)
                
                # Check if URL slug is contained in the filename part (ignoring date)
                if url_slug.lower() in name_part.lower():
                    similar_files.append(file_path)
        
        return similar_files

    def get_recent_bsky_files(self, count: int = 5) -> List[Path]:
        """
        Get the most recently modified Bluesky files.

        Args:
            count: Number of recent files to return

        Returns:
            List of recent file paths
        """
        blsky_files = list(self.cache_dir.glob("*_blsky.txt"))
        # Sort by modification time, newest first
        blsky_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return blsky_files[:count]

    def find_post_by_content(self, content: str, url: str = None, threshold: float = 0.8) -> Optional[str]:
        """
        Find a post by its content or URL (prioritizing URL-based matching).

        Args:
            content: Content to search for (fallback)
            url: URL to match against filenames (primary)
            threshold: Similarity threshold (0.0 to 1.0)

        Returns:
            Content of the matching file or None if not found
        """
        # If URL is provided, try URL-based matching first
        if url:
            similar_files = self.find_similar_bsky_files_by_url(url)
            if similar_files:
                # Return content of the most recently modified matching file
                most_recent_file = max(similar_files, key=lambda f: f.stat().st_mtime)
                try:
                    with open(most_recent_file, 'r', encoding='utf-8') as f:
                        return f.read().strip()
                except Exception:
                    pass
        
        # Fallback to content-based matching if URL-based matching fails
        content_lower = content.lower().strip()
        
        # Look for all _blsky.txt files in the cache directory
        for file_path in self.cache_dir.glob("*_blsky.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read().strip().lower()
                    
                # Calculate similarity using difflib
                import difflib
                similarity = difflib.SequenceMatcher(None, content_lower, file_content).ratio()
                
                if similarity >= threshold:
                    return file_content
            except Exception:
                # Skip files that can't be read
                continue
                
        return None