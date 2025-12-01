import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from news_manager.llm import GeminiClient, LLMClient, SYSTEM_PROMPT
from news_manager.exceptions import ConfigurationError, APIError


class TestLLMClient:
    """Test the base LLMClient class."""
    
    def test_llm_client_abstract(self):
        """Test that LLMClient is abstract and cannot be instantiated."""
        # LLMClient is not actually abstract, it just raises NotImplementedError
        # when generate_news is called
        client = LLMClient()
        with pytest.raises(NotImplementedError):
            client.generate_news("test")


class TestGeminiClient:
    """Test the GeminiClient class."""
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_gemini_client_initialization(self):
        """Test GeminiClient initialization with valid API key."""
        with patch('news_manager.llm.genai') as mock_genai:
            client = GeminiClient()
            assert client.model is not None
            mock_genai.configure.assert_called_once_with(api_key='test_key')
    
    def test_gemini_client_no_api_key(self):
        """Test GeminiClient initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ConfigurationError, match="Google Gemini key not found"):
                GeminiClient()
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_generate_news_basic(self):
        """Test basic news generation."""
        mock_response = Mock()
        mock_response.text = """Título: Test Title
Texto: Test content.
Enlaces:
- https://example.com
Bluesky: Test bluesky post."""
        
        with patch('news_manager.llm.genai') as mock_genai:
            mock_model = Mock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient()
            result = client.generate_news("Test input text")
            
            assert "Título: Test Title" in result
            assert "Texto: Test content" in result
            assert "Bluesky: Test bluesky post" in result
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_generate_news_with_prompt_extra(self):
        """Test news generation with extra prompt."""
        mock_response = Mock()
        mock_response.text = "Generated content"
        
        with patch('news_manager.llm.genai') as mock_genai:
            mock_model = Mock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient()
            result = client.generate_news("Test input", "Focus on technology")
            
            # Verify that the prompt_extra was included in the call
            call_args = mock_model.generate_content.call_args[0][0]
            assert "Focus on technology" in call_args
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_generate_news_with_url(self):
        """Test news generation with URL."""
        mock_response = Mock()
        mock_response.text = "Generated content"
        
        with patch('news_manager.llm.genai') as mock_genai:
            mock_model = Mock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient()
            result = client.generate_news("Test input", url="https://example.com")
            
            # Verify that the URL was included in the call
            call_args = mock_model.generate_content.call_args[0][0]
            assert "https://example.com" in call_args
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_generate_news_api_error(self):
        """Test handling of API errors."""
        with patch('news_manager.llm.genai') as mock_genai:
            mock_model = Mock()
            mock_model.generate_content.side_effect = Exception("API Error")
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient()
            
            with pytest.raises(APIError, match="Failed to generate content"):
                client.generate_news("Test input")
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_generate_news_all_parameters(self):
        """Test news generation with all parameters."""
        mock_response = Mock()
        mock_response.text = "Generated content"
        
        with patch('news_manager.llm.genai') as mock_genai:
            mock_model = Mock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient()
            result = client.generate_news(
                "Test input", 
                "Focus on science", 
                "https://example.com"
            )
            
            # Verify all parameters were included
            call_args = mock_model.generate_content.call_args[0][0]
            assert "Focus on science" in call_args
            assert "https://example.com" in call_args
            assert "Test input" in call_args


class TestSystemPrompt:
    """Test the system prompt content."""
    
    def test_system_prompt_contains_required_sections(self):
        """Test that the system prompt contains all required sections."""
        assert "Title:" in SYSTEM_PROMPT
        assert "Text:" in SYSTEM_PROMPT
        assert "Links:" in SYSTEM_PROMPT
        assert "Bluesky:" in SYSTEM_PROMPT
    
    def test_system_prompt_format_example(self):
        """Test that the system prompt contains the correct format example."""
        assert "Title: [Generated title]" in SYSTEM_PROMPT
        assert "Text: [Generated text]" in SYSTEM_PROMPT
        assert "https://example.com/news" in SYSTEM_PROMPT
        assert "Bluesky: [Generated post]" in SYSTEM_PROMPT
    
    def test_system_prompt_style_guidelines(self):
        """Test that the system prompt contains style guidelines."""
        assert "Active Voice" in SYSTEM_PROMPT
        assert "Neutral Tone" in SYSTEM_PROMPT
        assert "informative and objective" in SYSTEM_PROMPT


class TestIntegration:
    """Integration tests for the LLM module."""
    
    @patch.dict(os.environ, {'GOOGLE_API_KEY': 'test_key'})
    def test_full_generation_flow(self):
        """Test the complete generation flow."""
        expected_output = """Title: Test News
Text: This is a test news article.
Links:
- https://example.com
Bluesky: Test bluesky post."""
        
        mock_response = Mock()
        mock_response.text = expected_output
        
        with patch('news_manager.llm.genai') as mock_genai:
            mock_model = Mock()
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            client = GeminiClient()
            result = client.generate_news("Test input text")
            
            assert result == expected_output
            mock_model.generate_content.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__]) 