# Contributing to Synapse

Thank you for your interest in contributing to Synapse! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Review Guidelines](#code-review-guidelines)
- [Release Process](#release-process)

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Docker (optional, for containerized development)
- Redis (for caching)
- API keys for external services (Slack, GitHub, OpenAI)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/synapse.git
   cd synapse
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/simonyooon/synapse.git
   ```

## Development Setup

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 2. Configuration

Create a `.env` file in the project root:

```env
# API Keys (get these from respective services)
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
OPENAI_API_KEY=sk-your-openai-api-key
GITHUB_TOKEN=ghp-your-github-token

# Development settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ENABLE_DEBUG_ENDPOINTS=true

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=synapse-dev
```

### 3. Start Services

```bash
# Start Redis (if not running)
redis-server

# Start MLflow tracking server (optional)
mlflow server --host 0.0.0.0 --port 5000

# Start Synapse in development mode
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Setup

```bash
# Run tests
pytest

# Check code quality
black --check backend/
isort --check-only backend/
mypy backend/
flake8 backend/
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: 88 characters (Black default)
- **Import Order**: Use `isort` for automatic import sorting
- **Type Hints**: Required for all function parameters and return values
- **Docstrings**: Use Google-style docstrings

### Code Formatting

We use automated tools for code formatting:

```bash
# Format code
black backend/
isort backend/

# Type checking
mypy backend/

# Linting
flake8 backend/
```

### File Organization

```
backend/
├── agent/           # Agent orchestration logic
├── config.py        # Configuration management
├── llm/            # LLM integration
├── main.py         # FastAPI application
├── memory/         # Caching and storage
├── tools/          # Tool implementations
└── tracking/       # Monitoring and analytics
```

### Naming Conventions

- **Files**: snake_case (e.g., `slack_tools.py`)
- **Classes**: PascalCase (e.g., `SynapseAgent`)
- **Functions/Methods**: snake_case (e.g., `summarize_thread`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`)
- **Variables**: snake_case (e.g., `thread_messages`)

### Documentation Standards

#### Function Docstrings

```python
async def summarize_thread(
    self,
    channel: str,
    thread_ts: str,
    model: str = "gpt-4-turbo-preview"
) -> Dict[str, Any]:
    """Summarize a Slack thread using LLM.
    
    Args:
        channel: Slack channel ID
        thread_ts: Thread timestamp to summarize
        model: LLM model to use for summarization
        
    Returns:
        Dictionary containing summary and metadata
        
    Raises:
        ValueError: If channel or thread_ts is invalid
        APIError: If external API call fails
    """
```

#### Class Docstrings

```python
class SlackTools:
    """Slack tools for Synapse agent platform.
    
    Provides functionality for thread summarization and channel monitoring.
    
    Attributes:
        client: SlackClient instance
        llm_client: OpenAIClient instance
        cache: RedisCache instance
        tracker: MLflowTracker instance
    """
```

## Testing Guidelines

### Test Structure

```
tests/
├── unit/           # Unit tests
│   ├── test_agent.py
│   ├── test_slack_tools.py
│   └── test_github_tools.py
├── integration/    # Integration tests
│   ├── test_api.py
│   └── test_tools.py
├── fixtures/       # Test fixtures and data
└── conftest.py     # Pytest configuration
```

### Writing Tests

#### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch
from backend.tools.slack_tools import SlackTools

class TestSlackTools:
    @pytest.fixture
    def slack_tools(self):
        """Create SlackTools instance for testing."""
        return SlackTools()
    
    @pytest.mark.asyncio
    async def test_summarize_thread_success(self, slack_tools):
        """Test successful thread summarization."""
        # Arrange
        channel = "C123456"
        thread_ts = "1234567890.123456"
        expected_summary = "Test summary"
        
        with patch.object(slack_tools.client, 'get_thread_messages') as mock_get:
            mock_get.return_value = [{"user": "U123", "text": "Test message"}]
            
            with patch.object(slack_tools.llm_client, 'summarize_thread') as mock_llm:
                mock_llm.return_value = {"summary": expected_summary}
                
                # Act
                result = await slack_tools.summarize_thread(channel, thread_ts)
                
                # Assert
                assert result["summary"] == expected_summary
                mock_get.assert_called_once_with(channel, thread_ts)
                mock_llm.assert_called_once()
```

#### Integration Tests

```python
import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_agent_endpoint():
    """Test the main agent endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/agent", json={
            "message": "summarize slack thread in #general"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
```

### Test Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest tests/unit/test_slack_tools.py

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v
```

### Test Coverage

- **Target**: 80%+ code coverage
- **Critical Paths**: 100% coverage required
- **New Features**: 90%+ coverage required

## Pull Request Process

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following coding standards
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new slack monitoring feature

- Add real-time keyword monitoring
- Implement alert notifications
- Add configuration options
- Include comprehensive tests

Closes #123"
```

### 4. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:

- **Title**: Clear, descriptive title
- **Description**: Detailed description of changes
- **Checklist**: Complete the PR template checklist
- **Labels**: Add appropriate labels (bug, feature, documentation, etc.)

### 5. PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes

## Related Issues
Closes #123
```

## Code Review Guidelines

### For Contributors

- **Be Responsive**: Respond to review comments promptly
- **Be Open**: Accept constructive feedback
- **Be Thorough**: Address all review comments
- **Be Clear**: Explain your reasoning when needed

### For Reviewers

- **Be Constructive**: Provide helpful, actionable feedback
- **Be Specific**: Point out exact issues and suggest solutions
- **Be Timely**: Review PRs within 24-48 hours
- **Be Respectful**: Maintain a positive, collaborative tone

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Error handling is appropriate
- [ ] Logging is adequate

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Release Steps

1. **Update Version**
   ```bash
   # Update version in setup.py or pyproject.toml
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Create Release Notes**
   - Document new features
   - List bug fixes
   - Note breaking changes
   - Include migration guide if needed

3. **Deploy**
   - Deploy to staging environment
   - Run integration tests
   - Deploy to production
   - Monitor for issues

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Release notes prepared
- [ ] Security audit completed
- [ ] Performance testing done
- [ ] Backup procedures verified

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Requests**: Code reviews and collaboration

### Resources

- [Architecture Documentation](ARCHITECTURE.md)
- [API Documentation](API.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Code Style Guide](https://www.python.org/dev/peps/pep-0008/)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) for details.

## License

By contributing to Synapse, you agree that your contributions will be licensed under the MIT License. 