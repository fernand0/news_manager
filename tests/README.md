# Tests for News Manager

This directory contains comprehensive tests for the News Manager project.

## Test Structure

### `test_utils.py`
Tests for utility functions:
- **TestSlugify**: Tests for the `slugify` function
- **TestExtractPersonNames**: Tests for person name extraction
- **TestSiguienteLaborable**: Tests for business day calculation
- **TestParseOutput**: Tests for parsing LLM output
- **TestFileOperations**: Tests for file operations

### `test_llm.py`
Tests for the LLM module:
- **TestLLMClient**: Tests for the base LLM client class
- **TestGeminiClient**: Tests for the Gemini API client
- **TestSystemPrompt**: Tests for the system prompt content
- **TestIntegration**: Integration tests for the LLM module

### `test_url_functions.py`
Tests for URL-related functions:
- **TestExtractMainTextFromURL**: Tests for web scraping functionality
- **TestURLValidation**: Tests for URL validation
- **TestContentExtraction**: Tests for content extraction logic

## Running Tests

### Run all tests:
```bash
python -m pytest tests/ -v
```

### Run specific test file:
```bash
python -m pytest tests/test_utils.py -v
```

### Run specific test class:
```bash
python -m pytest tests/test_utils.py::TestSlugify -v
```

### Run specific test method:
```bash
python -m pytest tests/test_utils.py::TestSlugify::test_basic_slugify -v
```

### Run with coverage:
```bash
python -m pytest tests/ --cov=news_manager --cov-report=html
```

### Run with custom script:
```bash
python run_tests.py
```

## Test Configuration

The tests use `pytest.ini` for configuration:
- Verbose output (`-v`)
- Short traceback format (`--tb=short`)
- Disabled warnings (`--disable-warnings`)
- Custom markers for test categorization

## Test Coverage

The tests cover:
- ✅ **Utility functions**: slugify, extract_person_names, siguiente_laborable, parse_output
- ✅ **LLM functionality**: GeminiClient, system prompt, error handling
- ✅ **URL processing**: web scraping, content extraction, error handling
- ✅ **File operations**: temporary files, environment variables
- ✅ **Edge cases**: empty inputs, malformed data, network errors

## Mocking Strategy

Tests use extensive mocking to:
- **Avoid API calls**: Mock Gemini API responses
- **Isolate components**: Test functions independently
- **Control dependencies**: Mock file system and network calls
- **Test error conditions**: Simulate various failure scenarios

## Adding New Tests

When adding new functionality:

1. **Create test file**: `tests/test_new_feature.py`
2. **Follow naming**: `TestClassName` and `test_method_name`
3. **Use descriptive names**: Clear test method names
4. **Add docstrings**: Explain what each test does
5. **Mock external dependencies**: Don't rely on external services
6. **Test edge cases**: Include error conditions and boundary cases

## Test Best Practices

- **Isolation**: Each test should be independent
- **Descriptive names**: Test names should explain the scenario
- **Arrange-Act-Assert**: Structure tests clearly
- **Mock external calls**: Don't make real API or network calls
- **Test error conditions**: Include tests for failure scenarios
- **Keep tests fast**: Tests should run quickly
- **Use fixtures**: Reuse common test setup

## Continuous Integration

Tests are designed to run in CI/CD environments:
- No external dependencies
- Fast execution
- Clear pass/fail results
- Comprehensive coverage 