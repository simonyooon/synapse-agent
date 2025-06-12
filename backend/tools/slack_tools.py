"""
Slack tools for Synapse agent platform.
Provides functionality for thread summarization and channel monitoring.
"""
from typing import Dict, List, Optional
import json
import time
from .slack_client import SlackClient
from ..llm.openai_client import OpenAIClient
from ..memory.redis_cache import RedisCache
from ..tracking.mlflow_tracker import MLflowTracker

class SlackTools:
    def __init__(
        self,
        client: Optional[SlackClient] = None,
        llm_client: Optional[OpenAIClient] = None,
        cache: Optional[RedisCache] = None,
        tracker: Optional[MLflowTracker] = None
    ):
        """Initialize Slack tools with dependencies.
        
        Args:
            client: SlackClient instance
            llm_client: OpenAIClient instance
            cache: RedisCache instance
            tracker: MLflowTracker instance
        """
        self.client = client or SlackClient()
        self.llm_client = llm_client or OpenAIClient()
        self.cache = cache or RedisCache()
        self.tracker = tracker or MLflowTracker()

    async def summarize_thread(
        self,
        channel: str,
        thread_ts: str,
        model: str = "gpt-4-turbo-preview"
    ) -> Dict:
        """Summarize a Slack thread using LLM.
        
        Args:
            channel: Slack channel ID
            thread_ts: Thread timestamp to summarize
            model: LLM model to use for summarization
            
        Returns:
            Dictionary containing summary and metadata
        """
        start_time = time.time()
        
        # Check cache first
        cached_summary = await self.cache.get_thread_summary(channel, thread_ts)
        if cached_summary:
            self.tracker.log_tool_usage(
                tool_name="summarize_thread",
                input_data={"channel": channel, "thread_ts": thread_ts},
                output_data=cached_summary,
                duration=time.time() - start_time,
                status="cache_hit"
            )
            return cached_summary

        try:
            # Get thread messages
            messages = await self.client.get_thread_messages(channel, thread_ts)
            
            # Generate summary using LLM
            llm_start_time = time.time()
            summary_result = await self.llm_client.summarize_thread(messages, model)
            llm_duration = time.time() - llm_start_time
            
            # Log LLM usage
            self.tracker.log_llm_usage(
                model=model,
                prompt=f"Summarize thread in channel {channel}",
                response=summary_result["summary"],
                token_count=summary_result["token_count"],
                duration=llm_duration
            )
            
            # Cache the summary
            await self.cache.set_thread_summary(channel, thread_ts, summary_result)
            
            # Log tool usage
            self.tracker.log_tool_usage(
                tool_name="summarize_thread",
                input_data={"channel": channel, "thread_ts": thread_ts},
                output_data=summary_result,
                duration=time.time() - start_time
            )
            
            return summary_result
            
        except Exception as e:
            self.tracker.log_tool_usage(
                tool_name="summarize_thread",
                input_data={"channel": channel, "thread_ts": thread_ts},
                output_data={"error": str(e)},
                duration=time.time() - start_time,
                status="error"
            )
            raise

    async def monitor_channel(
        self,
        channel: str,
        keywords: List[str],
        limit: int = 100
    ) -> List[Dict]:
        """Monitor channel for specific keywords and return matching messages.
        
        Args:
            channel: Slack channel ID
            keywords: List of keywords to search for
            limit: Maximum number of messages to check
            
        Returns:
            List of matching message dictionaries
        """
        start_time = time.time()
        
        try:
            messages = await self.client.get_channel_history(channel, limit=limit)
            
            # Filter messages containing keywords
            matches = []
            for msg in messages:
                text = msg.get("text", "").lower()
                if any(keyword.lower() in text for keyword in keywords):
                    matches.append(msg)
            
            # Log tool usage
            self.tracker.log_tool_usage(
                tool_name="monitor_channel",
                input_data={"channel": channel, "keywords": keywords},
                output_data={"matches": matches},
                duration=time.time() - start_time
            )
            
            return matches
            
        except Exception as e:
            self.tracker.log_tool_usage(
                tool_name="monitor_channel",
                input_data={"channel": channel, "keywords": keywords},
                output_data={"error": str(e)},
                duration=time.time() - start_time,
                status="error"
            )
            raise

    async def post_summary(
        self,
        channel: str,
        thread_ts: str,
        summary: str
    ) -> Dict:
        """Post a thread summary back to Slack.
        
        Args:
            channel: Slack channel ID
            thread_ts: Thread timestamp to reply to
            summary: Summary text to post
            
        Returns:
            Response from Slack API
        """
        start_time = time.time()
        
        try:
            result = await self.client.post_message(
                channel=channel,
                text=f"📝 *Thread Summary*\n{summary}",
                thread_ts=thread_ts
            )
            
            # Log tool usage
            self.tracker.log_tool_usage(
                tool_name="post_summary",
                input_data={"channel": channel, "thread_ts": thread_ts, "summary": summary},
                output_data=result,
                duration=time.time() - start_time
            )
            
            return result
            
        except Exception as e:
            self.tracker.log_tool_usage(
                tool_name="post_summary",
                input_data={"channel": channel, "thread_ts": thread_ts, "summary": summary},
                output_data={"error": str(e)},
                duration=time.time() - start_time,
                status="error"
            )
            raise
