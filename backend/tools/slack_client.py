"""
Slack API client for Synapse agent platform.
Handles authentication, message retrieval, and thread operations.
"""
from typing import List, Dict, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from ..config import get_settings

class SlackClient:
    def __init__(self, token: Optional[str] = None):
        """Initialize Slack client with bot token.
        
        Args:
            token: Slack bot token. If None, uses token from config.
        """
        settings = get_settings()
        self.token = token or settings.slack_bot_token
        if not self.token:
            raise ValueError("Slack bot token not provided")
        self.client = WebClient(token=self.token)

    async def get_thread_messages(self, channel: str, thread_ts: str) -> List[Dict]:
        """Retrieve all messages in a thread.
        
        Args:
            channel: Slack channel ID
            thread_ts: Thread timestamp to retrieve
            
        Returns:
            List of message dictionaries containing thread content
        """
        try:
            result = self.client.conversations_replies(
                channel=channel,
                ts=thread_ts
            )
            return result["messages"]
        except SlackApiError as e:
            raise Exception(f"Error fetching thread messages: {str(e)}")

    async def get_channel_history(
        self, 
        channel: str, 
        limit: int = 100,
        oldest: Optional[str] = None
    ) -> List[Dict]:
        """Get recent channel messages.
        
        Args:
            channel: Slack channel ID
            limit: Maximum number of messages to retrieve
            oldest: Timestamp to start from (optional)
            
        Returns:
            List of message dictionaries
        """
        try:
            result = self.client.conversations_history(
                channel=channel,
                limit=limit,
                oldest=oldest
            )
            return result["messages"]
        except SlackApiError as e:
            raise Exception(f"Error fetching channel history: {str(e)}")

    async def post_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None
    ) -> Dict:
        """Post a message to a channel or thread.
        
        Args:
            channel: Slack channel ID
            text: Message text to post
            thread_ts: Thread timestamp to reply to (optional)
            
        Returns:
            Response dictionary from Slack API
        """
        try:
            result = self.client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts
            )
            return result
        except SlackApiError as e:
            raise Exception(f"Error posting message: {str(e)}") 