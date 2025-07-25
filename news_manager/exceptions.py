"""
Custom exceptions for News Manager.

This module defines a hierarchy of exceptions that provide specific error handling
and better error messages for different types of failures in the application.
"""

from typing import Optional


class NewsManagerError(Exception):
    """
    Base exception for News Manager.
    
    All custom exceptions in the application should inherit from this class.
    """
    
    def __init__(self, message: str, details: Optional[str] = None, suggestion: Optional[str] = None):
        """
        Initialize the exception.
        
        Args:
            message: The main error message
            details: Additional details about the error
            suggestion: Suggested solution or next steps
        """
        self.message = message
        self.details = details
        self.suggestion = suggestion
        
        # Build the full error message
        full_message = message
        if details:
            full_message += f"\nDetails: {details}"
        if suggestion:
            full_message += f"\nSuggestion: {suggestion}"
            
        super().__init__(full_message)


class ValidationError(NewsManagerError):
    """
    Exception raised when input validation fails.
    
    This includes file path validation, URL validation, and other input checks.
    """
    pass


class ConfigurationError(NewsManagerError):
    """
    Exception raised when there are configuration issues.
    
    This includes missing environment variables, invalid API keys, etc.
    """
    pass


class ContentProcessingError(NewsManagerError):
    """
    Exception raised when content processing fails.
    
    This includes issues with text extraction, parsing, or generation.
    """
    pass


class APIError(NewsManagerError):
    """
    Exception raised when external API calls fail.
    
    This includes Gemini API errors, network issues, etc.
    """
    
    def __init__(self, message: str, api_name: str = "Unknown", status_code: Optional[int] = None, **kwargs):
        """
        Initialize API error with additional context.
        
        Args:
            message: The main error message
            api_name: Name of the API that failed
            status_code: HTTP status code if applicable
            **kwargs: Additional arguments passed to parent
        """
        self.api_name = api_name
        self.status_code = status_code
        
        # Enhance message with API context
        enhanced_message = f"{api_name} API Error: {message}"
        if status_code:
            enhanced_message += f" (Status: {status_code})"
            
        super().__init__(enhanced_message, **kwargs)


class FileOperationError(NewsManagerError):
    """
    Exception raised when file operations fail.
    
    This includes file reading, writing, and permission issues.
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None, operation: Optional[str] = None, **kwargs):
        """
        Initialize file operation error with additional context.
        
        Args:
            message: The main error message
            file_path: Path to the file that caused the error
            operation: The operation that failed (read, write, etc.)
            **kwargs: Additional arguments passed to parent
        """
        self.file_path = file_path
        self.operation = operation
        
        # Enhance message with file context
        enhanced_message = message
        if operation and file_path:
            enhanced_message = f"Failed to {operation} file '{file_path}': {message}"
        elif file_path:
            enhanced_message = f"File operation failed for '{file_path}': {message}"
            
        super().__init__(enhanced_message, **kwargs)


class NetworkError(NewsManagerError):
    """
    Exception raised when network operations fail.
    
    This includes URL fetching, connection timeouts, etc.
    """
    
    def __init__(self, message: str, url: Optional[str] = None, **kwargs):
        """
        Initialize network error with additional context.
        
        Args:
            message: The main error message
            url: URL that caused the error
            **kwargs: Additional arguments passed to parent
        """
        self.url = url
        
        # Enhance message with URL context
        enhanced_message = message
        if url:
            enhanced_message = f"Network error for '{url}': {message}"
            
        super().__init__(enhanced_message, **kwargs)