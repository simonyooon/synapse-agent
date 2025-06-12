# Synapse: Distributed LLM Orchestrator

Synapse is an agent-based platform that integrates GitHub and Slack workflows to reduce engineering overhead. It uses modular tools, Redis caching, and MLflow tracking to enable AI-assisted team automation.

## Features
- LLM-driven agent parsing developer prompts
- Slack thread summarization
- GitHub issue triaging and assignment suggestions
- MLflow model behavior tracking
- Redis-backed session and metric management

## How to Run
```
pip install -r requirements.txt
uvicorn main:app --reload
```

## API Endpoint
POST `/agent`
```json
{
  "message": "summarize slack thread about project x"
}
``` 
