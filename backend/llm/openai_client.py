"""
OpenAI client wrapper for Synapse LLM operations.
Handles model interactions and prompt management.
"""
import os
from typing import Dict, List, Optional
from openai import AsyncOpenAI
import json

class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def summarize_thread(
        self,
        messages: List[Dict],
        model: str = "gpt-4-turbo-preview"
    ) -> Dict:
        """Summarize a thread of messages using LLM.
        
        Args:
            messages: List of message dictionaries
            model: Model to use for summarization
            
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
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes Slack threads."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            summary = response.choices[0].message.content
            
            return {
                "summary": summary,
                "model": model,
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
                model="gpt-4-turbo-preview",
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