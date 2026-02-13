#!/usr/bin/env python3
"""
Test script for the Bluesky history functionality.
"""

from pathlib import Path
from news_manager.bluesky_history import BlueskyHistoryManager

def test_bluesky_history():
    """Test the Bluesky history functionality."""
    print("Testing Bluesky history functionality...")
    
    # Create a temporary cache directory for testing
    test_cache_dir = Path("/tmp/test_webDiis")
    test_cache_dir.mkdir(exist_ok=True)
    
    # Create test blsky files
    test_file = test_cache_dir / "2025-01-01-test_blsky.txt"
    sample_content = "This is a test post for Bluesky about a research paper."
    with open(test_file, 'w') as f:
        f.write(sample_content)
    
    # Create another file with a name that matches the URL pattern
    url_test_file = test_cache_dir / "2025-01-01-test-paper_blsky.txt"
    with open(url_test_file, 'w') as f:
        f.write("This is content from test paper.")
    
    # Initialize the history manager
    history_manager = BlueskyHistoryManager(test_cache_dir)
    
    # Test saving a post (should be a no-op)
    sample_content_new = "This is a test post for Bluesky about a research paper."
    sample_url = "https://diis.unizar.es/test-paper"
    
    success = history_manager.save_post(sample_content_new, sample_url)
    print(f"Save post success: {success}")
    
    # Test getting recent posts
    recent_posts = history_manager.get_recent_bsky_files(5)
    print(f"Recent posts: {recent_posts}")
    
    # Test finding a post by content
    found_post = history_manager.find_post_by_content(sample_content, "https://diis.unizar.es/test-paper")
    print(f"Found post by content: {found_post}")
    
    # Test with a slightly different content to check similarity matching
    similar_content = "This is a test post for Bluesky about a research paper with minor changes."
    found_similar = history_manager.find_post_by_content(similar_content, "https://diis.unizar.es/test-paper", threshold=0.8)
    print(f"Found similar post: {found_similar}")
    
    # Clean up
    import shutil
    if test_cache_dir.exists():
        shutil.rmtree(test_cache_dir)
    
    print("Test completed!")

if __name__ == "__main__":
    test_bluesky_history()