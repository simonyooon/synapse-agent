"""
Base Synapse agent implementation.
Handles routing of user requests to appropriate tools.
"""
import json
from typing import Dict, Any
import time
from tools.slack_tools import SlackTools
from tools.github_tools import GitHubTools
from llm.openai_client import OpenAIClient
from tracking.mlflow_tracker import MLflowTracker

class SynapseAgent:
    def __init__(self):
        """Initialize agent with available tools and dependencies."""
        self.llm_client = OpenAIClient()
        self.tracker = MLflowTracker()
        self.slack_tools = SlackTools(
            llm_client=self.llm_client,
            tracker=self.tracker
        )
        self.github_tools = GitHubTools(
            llm_client=self.llm_client,
            tracker=self.tracker
        )
        self.tools = {
            "slack": self.slack_tools,
            "github": self.github_tools
        }

    async def handle(self, message: str) -> Dict[str, Any]:
        """Handle incoming user message and route to appropriate tool.
        
        Args:
            message: User input message
            
        Returns:
            Dictionary containing response and metadata
        """
        start_time = time.time()
        
        try:
            # Use LLM to extract intent and parameters
            thread_info = await self.llm_client.extract_thread_info(message)
            
            # Parse message to determine intent
            if "summarize" in message.lower() and "slack" in message.lower():
                if not thread_info.get("channel") or not thread_info.get("thread_ts"):
                    return {
                        "status": "error",
                        "message": "Could not extract channel or thread information from message"
                    }
                
                # Get thread summary
                summary = await self.slack_tools.summarize_thread(
                    channel=thread_info["channel"],
                    thread_ts=thread_info["thread_ts"]
                )
                
                # Post summary back to thread
                await self.slack_tools.post_summary(
                    channel=thread_info["channel"],
                    thread_ts=thread_info["thread_ts"],
                    summary=summary["summary"]
                )
                
                return {
                    "status": "success",
                    "action": "summarize_thread",
                    "data": summary
                }
                
            elif "monitor" in message.lower() and "slack" in message.lower():
                if not thread_info.get("channel"):
                    return {
                        "status": "error",
                        "message": "Could not extract channel information from message"
                    }
                
                # Extract keywords from message
                keywords = [word for word in message.lower().split() 
                          if word not in ["monitor", "slack", "channel", "for", "in"]]
                
                matches = await self.slack_tools.monitor_channel(
                    channel=thread_info["channel"],
                    keywords=keywords
                )
                
                return {
                    "status": "success",
                    "action": "monitor_channel",
                    "data": {"matches": matches}
                }
                
            elif "triage" in message.lower() and "github" in message.lower():
                # Extract repository from message
                repo = next((word for word in message.split() 
                           if "/" in word and "github.com" not in word), None)
                if not repo:
                    return {
                        "status": "error",
                        "message": "Could not extract repository information from message"
                    }
                
                result = await self.github_tools.triage_issues(repo=repo)
                return {
                    "status": "success",
                    "action": "triage_issues",
                    "data": result
                }
                
            elif "review" in message.lower() and "pr" in message.lower():
                # Extract repository and PR number from message
                repo = next((word for word in message.split() 
                           if "/" in word and "github.com" not in word), None)
                pr_number = next((int(word.strip("#")) for word in message.split() 
                                if word.strip("#").isdigit()), None)
                
                if not repo or not pr_number:
                    return {
                        "status": "error",
                        "message": "Could not extract repository or PR number from message"
                    }
                
                result = await self.github_tools.review_pull_request(
                    repo=repo,
                    pr_number=pr_number
                )
                return {
                    "status": "success",
                    "action": "review_pr",
                    "data": result
                }
                
            else:
                return {
                    "status": "error",
                    "message": "I'm not sure what to do with that request yet."
                }
                
        except Exception as e:
            self.tracker.log_tool_usage(
                tool_name="agent_handle",
                input_data={"message": message},
                output_data={"error": str(e)},
                duration=time.time() - start_time,
                status="error"
            )
            return {
                "status": "error",
                "message": f"Error processing request: {str(e)}"
            }