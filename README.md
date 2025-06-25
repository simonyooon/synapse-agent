# Synapse: Distributed LLM Orchestrator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Synapse is an intelligent agent-based platform that integrates GitHub and Slack workflows to reduce engineering overhead. It uses modular tools, Redis caching, and MLflow tracking to enable AI-assisted team automation.

## 🚀 Features

- **LLM-driven Agent**: Intelligent parsing and routing of developer prompts
- **Slack Integration**: Thread summarization and channel monitoring
- **GitHub Automation**: Issue triaging and PR review suggestions
- **Performance Tracking**: MLflow-based model behavior and tool usage tracking
- **Caching Layer**: Redis-backed session and metric management
- **Modular Architecture**: Extensible tool system for easy integration

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Development](#development)
- [Contributing](#contributing)

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │  Synapse Agent  │    │   Tool Modules  │
│                 │    │                 │    │                 │
│  POST /agent    │───▶│  Intent Parser │───▶│  Slack Tools    │
│                 │    │                 │    │                 │
│  Health Check   │    │  LLM Client     │    │  GitHub Tools   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis Cache   │    │  MLflow Tracker │    │  External APIs  │
│                 │    │                 │    │                 │
│  Thread Summary │    │  Tool Usage     │    │  Slack API      │
│  Session Data   │    │  LLM Metrics    │    │  GitHub API     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

- **Agent Layer**: Central orchestrator that routes requests to appropriate tools
- **Tool Modules**: Specialized handlers for Slack and GitHub operations
- **LLM Integration**: OpenAI client for intelligent text processing
- **Caching Layer**: Redis for performance optimization
- **Tracking System**: MLflow for monitoring and analytics

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Redis server
- MLflow tracking server (optional)
- API keys for Slack, GitHub, and OpenAI

### 1. Clone and Install

```bash
git clone <repository-url>
cd synapse
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# API Keys
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
OPENAI_API_KEY=sk-your-openai-api-key
GITHUB_TOKEN=ghp-your-github-token

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=synapse

# OpenAI Configuration
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3
```

### 3. Start Services

```bash
# Start Redis (if not running)
redis-server

# Start MLflow tracking server (optional)
mlflow server --host 0.0.0.0 --port 5000

# Start Synapse
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test the API

```bash
curl -X POST "http://localhost:8000/agent" \
     -H "Content-Type: application/json" \
     -d '{"message": "summarize slack thread in #general"}'
```

## 📦 Installation

### System Requirements

- **Python**: 3.8 or higher
- **Redis**: 6.0 or higher
- **Memory**: Minimum 2GB RAM
- **Storage**: 1GB free space

### Dependencies

The project uses the following key dependencies:

- **FastAPI**: Web framework for API development
- **Uvicorn**: ASGI server for running the application
- **Redis**: In-memory data structure store for caching
- **MLflow**: Machine learning lifecycle platform
- **Slack SDK**: Official Slack API client
- **PyGithub**: GitHub API wrapper
- **OpenAI**: Official OpenAI API client
- **Pydantic**: Data validation using Python type annotations

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio black isort mypy
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SLACK_BOT_TOKEN` | Slack bot user OAuth token | - | Yes |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `GITHUB_TOKEN` | GitHub personal access token | - | Yes |
| `REDIS_HOST` | Redis server hostname | localhost | No |
| `REDIS_PORT` | Redis server port | 6379 | No |
| `REDIS_DB` | Redis database number | 0 | No |
| `MLFLOW_TRACKING_URI` | MLflow tracking server URI | http://localhost:5000 | No |
| `OPENAI_MODEL` | OpenAI model to use | gpt-4-turbo-preview | No |
| `OPENAI_MAX_TOKENS` | Maximum tokens for responses | 500 | No |
| `OPENAI_TEMPERATURE` | Model temperature | 0.3 | No |

### Configuration Classes

The application uses Pydantic settings for type-safe configuration management. See `backend/config.py` for the complete configuration schema.

## 📚 API Documentation

### Endpoints

#### POST `/agent`

Main endpoint for processing agent requests.

**Request Body:**
```json
{
  "message": "string"
}
```

**Response:**
```json
{
  "status": "success|error",
  "action": "string",
  "data": "object",
  "message": "string"
}
```

### Supported Actions

#### Slack Operations

1. **Thread Summarization**
   ```
   "summarize slack thread in #channel-name"
   ```

2. **Channel Monitoring**
   ```
   "monitor slack channel #general for keywords: bug, error, crash"
   ```

#### GitHub Operations

1. **Issue Triaging**
   ```
   "triage github issues in owner/repo"
   ```

2. **Pull Request Review**
   ```
   "review pr #123 in owner/repo"
   ```

## 💡 Usage Examples

### Slack Thread Summarization

```python
import requests

response = requests.post("http://localhost:8000/agent", json={
    "message": "summarize slack thread in #general with timestamp 1234567890.123456"
})

print(response.json())
```

### GitHub Issue Triaging

```python
response = requests.post("http://localhost:8000/agent", json={
    "message": "triage github issues in myorg/myrepo"
})

print(response.json())
```

### Channel Monitoring

```python
response = requests.post("http://localhost:8000/agent", json={
    "message": "monitor slack channel #alerts for keywords: error, critical, down"
})

print(response.json())
```

## 🔧 Development

### Project Structure

```
synapse/
├── backend/
│   ├── agent/
│   │   └── base.py              # Main agent orchestrator
│   │   └── tools/
│   │       └── github_client.py  # GitHub API client
│   ├── config.py                # Configuration management
│   ├── llm/
│   │   └── openai_client.py     # OpenAI integration
│   ├── main.py                  # FastAPI application
│   ├── memory/
│   │   └── redis_cache.py       # Redis caching layer
│   ├── tools/
│   │   ├── github_client.py     # GitHub API client
│   │   ├── github_tools.py      # GitHub automation tools
│   │   ├── slack_client.py      # Slack API client
│   │   └── slack_tools.py       # Slack automation tools
│   └── tracking/
│       └── mlflow_tracker.py    # MLflow tracking
├── frontend/                    # Future frontend implementation
├── scripts/                     # Utility scripts
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

### Adding New Tools

1. Create a new tool class in `backend/tools/`
2. Implement the required interface
3. Register the tool in `SynapseAgent.__init__()`
4. Add routing logic in `SynapseAgent.handle()`

Example tool structure:

```python
class NewTool:
    def __init__(self, llm_client, tracker):
        self.llm_client = llm_client
        self.tracker = tracker
    
    async def process(self, **kwargs):
        # Tool implementation
        pass
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_agent.py
```

### Code Quality

```bash
# Format code
black backend/
isort backend/

# Type checking
mypy backend/

# Linting
flake8 backend/
```

## 📊 Monitoring and Analytics

### MLflow Tracking

The application automatically tracks:

- Tool usage patterns and performance
- LLM model interactions and costs
- Error rates and response times
- User request patterns

Access the MLflow UI at `http://localhost:5000` to view metrics.

### Redis Monitoring

Monitor cache performance:

```bash
# Connect to Redis CLI
redis-cli

# View cache statistics
INFO memory
INFO stats
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive docstrings
- Include tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check the `/docs` directory for detailed guides
- **Discussions**: Use GitHub Discussions for questions and ideas

## 🔮 Roadmap

- [ ] Web-based dashboard for monitoring
- [ ] Additional tool integrations (Jira, Discord, etc.)
- [ ] Advanced LLM prompt management
- [ ] Multi-tenant support
- [ ] Real-time notifications
- [ ] Advanced analytics and reporting
