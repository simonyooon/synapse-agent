# API Documentation

## Overview

The Synapse API provides a RESTful interface for interacting with the LLM orchestrator. All endpoints return JSON responses and use standard HTTP status codes.

**Base URL**: `http://localhost:8000`

## Authentication

Currently, the API does not require authentication. In production, consider implementing API key authentication or OAuth2.

## Endpoints

### POST `/agent`

The main endpoint for processing agent requests. This endpoint accepts natural language commands and routes them to appropriate tools.

#### Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "message": "string"
}
```

**Parameters:**
- `message` (string, required): Natural language command describing the desired action

#### Response

**Success Response (200 OK):**
```json
{
  "status": "success",
  "action": "string",
  "data": {
    // Tool-specific response data
  },
  "message": "string"
}
```

**Error Response (400/500):**
```json
{
  "status": "error",
  "message": "Error description"
}
```

#### Supported Commands

##### Slack Operations

1. **Thread Summarization**
   ```
   "summarize slack thread in #channel-name"
   "summarize thread in #general with timestamp 1234567890.123456"
   ```

   **Response:**
   ```json
   {
     "status": "success",
     "action": "summarize_thread",
     "data": {
       "summary": "Thread summary content...",
       "model": "gpt-4-turbo-preview",
       "token_count": 150
     }
   }
   ```

2. **Channel Monitoring**
   ```
   "monitor slack channel #general for keywords: bug, error, crash"
   "monitor #alerts for critical issues"
   ```

   **Response:**
   ```json
   {
     "status": "success",
     "action": "monitor_channel",
     "data": {
       "matches": [
         {
           "user": "U123456",
           "text": "Found a bug in the login system",
           "ts": "1234567890.123456"
         }
       ]
     }
   }
   ```

##### GitHub Operations

1. **Issue Triaging**
   ```
   "triage github issues in owner/repo"
   "triage issues in myorg/myrepo"
   ```

   **Response:**
   ```json
   {
     "status": "success",
     "action": "triage_issues",
     "data": {
       "issues_triaged": 5,
       "suggestions": [
         {
           "issue_number": 123,
           "priority": "high",
           "suggested_labels": ["bug", "critical"],
           "suggested_assignees": ["developer1"],
           "action_summary": "Fix authentication bug"
         }
       ]
     }
   }
   ```

2. **Pull Request Review**
   ```
   "review pr #123 in owner/repo"
   "review pull request #456 in myorg/myrepo"
   ```

   **Response:**
   ```json
   {
     "status": "success",
     "action": "review_pr",
     "data": {
       "assessment": "Good code quality overall",
       "issues": ["Missing error handling in line 45"],
       "suggestions": ["Add input validation"],
       "recommendation": "approve"
     }
   }
   ```

## Error Handling

### Common Error Codes

- **400 Bad Request**: Invalid request format or missing required parameters
- **500 Internal Server Error**: Server-side error or tool failure

### Error Response Format

```json
{
  "status": "error",
  "message": "Detailed error description",
  "error_code": "OPTIONAL_ERROR_CODE"
}
```

### Common Error Messages

- `"Could not extract channel or thread information from message"`
- `"Could not extract repository information from message"`
- `"Could not extract repository or PR number from message"`
- `"I'm not sure what to do with that request yet."`

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Examples

### cURL Examples

**Thread Summarization:**
```bash
curl -X POST "http://localhost:8000/agent" \
     -H "Content-Type: application/json" \
     -d '{"message": "summarize slack thread in #general"}'
```

**Issue Triaging:**
```bash
curl -X POST "http://localhost:8000/agent" \
     -H "Content-Type: application/json" \
     -d '{"message": "triage github issues in myorg/myrepo"}'
```

**Channel Monitoring:**
```bash
curl -X POST "http://localhost:8000/agent" \
     -H "Content-Type: application/json" \
     -d '{"message": "monitor slack channel #alerts for keywords: error, critical"}'
```

### Python Examples

```python
import requests
import json

def call_synapse_agent(message):
    url = "http://localhost:8000/agent"
    headers = {"Content-Type": "application/json"}
    data = {"message": message}
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Example usage
result = call_synapse_agent("summarize slack thread in #general")
print(json.dumps(result, indent=2))
```

### JavaScript Examples

```javascript
async function callSynapseAgent(message) {
    const response = await fetch('http://localhost:8000/agent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message })
    });
    
    return await response.json();
}

// Example usage
callSynapseAgent("triage github issues in myorg/myrepo")
    .then(result => console.log(result))
    .catch(error => console.error('Error:', error));
```

## WebSocket Support

WebSocket support is planned for future releases to enable real-time communication and streaming responses.

## API Versioning

The current API is version 1.0. Future versions will be available at `/v2/agent`, `/v3/agent`, etc.

## Health Check

A health check endpoint will be added in future releases at `GET /health` to monitor service status. 