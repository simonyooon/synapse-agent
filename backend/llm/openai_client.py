"""
OpenAI client wrapper for Synapse LLM operations.
Handles model interactions and prompt management.
"""
from typing import Dict, List, Optional
from openai import AsyncOpenAI
import json
from ..config import get_settings

class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, uses key from config.
        """
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature

    async def summarize_thread(
        self,
        messages: List[Dict],
        model: Optional[str] = None
    ) -> Dict:
        """Summarize a thread of messages using LLM.
        
        Args:
            messages: List of message dictionaries
            model: Model to use for summarization (optional, uses config if None)
            
        Returns:
            Dictionary containing summary and metadata
        """
        # Format messages for the prompt
        thread_content = "\n".join([
            f"{msg.get('user', 'Unknown')}: {msg.get('text', '')}"
            for msg in messages
        ])
        
        prompt = f"""Please provide a concise summary of the following Slack thread discussion. 
        Focus on key points, decisions made, and action items. Format the summary with clear sections.

        Thread content:
        {thread_content}

        Summary:"""

        try:
            response = await self.client.chat.completions.create(
                model=model or self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes Slack threads."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            summary = response.choices[0].message.content
            
            return {
                "summary": summary,
                "model": model or self.model,
                "token_count": response.usage.total_tokens
            }
            
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")

    async def extract_thread_info(self, message: str) -> Dict:
        """Extract channel and thread information from a message.
        
        Args:
            message: User input message
            
        Returns:
            Dictionary containing channel and thread information
        """
        prompt = f"""Extract the Slack channel ID and thread timestamp from the following message.
        If not found, return null for those fields.
        
        Message: {message}
        
        Return the result as a JSON object with 'channel' and 'thread_ts' fields."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts Slack information."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            raise Exception(f"Error extracting thread info: {str(e)}") 