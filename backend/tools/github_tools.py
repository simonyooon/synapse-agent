"""
GitHub tools for Synapse agent platform.
Provides functionality for issue triage and PR review.
"""
from typing import Dict, List, Optional
import time
from .github_client import GitHubClient
from ..llm.openai_client import OpenAIClient
from ..tracking.mlflow_tracker import MLflowTracker

class GitHubTools:
    def __init__(
        self,
        client: Optional[GitHubClient] = None,
        llm_client: Optional[OpenAIClient] = None,
        tracker: Optional[MLflowTracker] = None
    ):
        """Initialize GitHub tools with dependencies.
        
        Args:
            client: GitHubClient instance
            llm_client: OpenAIClient instance
            tracker: MLflowTracker instance
        """
        self.client = client or GitHubClient()
        self.llm_client = llm_client or OpenAIClient()
        self.tracker = tracker or MLflowTracker()

    async def triage_issues(
        self,
        repo: str,
        state: str = "open"
    ) -> Dict:
        """Triage repository issues using LLM.
        
        Args:
            repo: Repository name (owner/repo)
            state: Issue state to triage
            
        Returns:
            Dictionary containing triage results
        """
        start_time = time.time()
        
        try:
            # Get issues
            issues = await self.client.get_issues(repo, state=state)
            
            # Format issues for LLM
            issues_text = "\n\n".join([
                f"Issue #{issue.number}: {issue.title}\n"
                f"Labels: {', '.join(label.name for label in issue.labels)}\n"
                f"Body: {issue.body}"
                for issue in issues
            ])
            
            # Generate triage suggestions
            llm_start_time = time.time()
            prompt = f"""Analyze these GitHub issues and suggest:
            1. Priority level (high/medium/low)
            2. Appropriate labels
            3. Suggested assignees
            4. Brief summary of action needed

            Issues:
            {issues_text}

            Return a JSON array of objects with fields:
            - issue_number
            - priority
            - suggested_labels
            - suggested_assignees
            - action_summary"""

            response = await self.llm_client.client.chat.completions.create(
                model=self.llm_client.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that triages GitHub issues."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            triage_suggestions = response.choices[0].message.content
            
            # Log LLM usage
            self.tracker.log_llm_usage(
                model=self.llm_client.model,
                prompt=prompt,
                response=triage_suggestions,
                token_count=response.usage.total_tokens,
                duration=time.time() - llm_start_time
            )
            
            # Apply suggestions
            for suggestion in triage_suggestions:
                issue_number = suggestion["issue_number"]
                await self.client.update_labels(
                    repo=repo,
                    issue_number=issue_number,
                    labels=suggestion["suggested_labels"]
                )
                
                # Add triage comment
                comment = (
                    f"🤖 **Synapse Triage Report**\n\n"
                    f"Priority: {suggestion['priority']}\n"
                    f"Suggested Assignees: {', '.join(suggestion['suggested_assignees'])}\n"
                    f"Action Needed: {suggestion['action_summary']}"
                )
                await self.client.add_comment(repo, issue_number, comment)
            
            # Log tool usage
            self.tracker.log_tool_usage(
                tool_name="triage_issues",
                input_data={"repo": repo, "state": state},
                output_data={"suggestions": triage_suggestions},
                duration=time.time() - start_time
            )
            
            return {
                "status": "success",
                "issues_triaged": len(issues),
                "suggestions": triage_suggestions
            }
            
        except Exception as e:
            self.tracker.log_tool_usage(
                tool_name="triage_issues",
                input_data={"repo": repo, "state": state},
                output_data={"error": str(e)},
                duration=time.time() - start_time,
                status="error"
            )
            raise

    async def review_pull_request(
        self,
        repo: str,
        pr_number: int
    ) -> Dict:
        """Review a pull request using LLM.
        
        Args:
            repo: Repository name (owner/repo)
            pr_number: Pull request number
            
        Returns:
            Dictionary containing review results
        """
        start_time = time.time()
        
        try:
            # Get PR details
            prs = await self.client.get_pull_requests(repo)
            pr = next((p for p in prs if p.number == pr_number), None)
            if not pr:
                raise ValueError(f"Pull request #{pr_number} not found")
            
            # Format PR for LLM
            pr_text = (
                f"Title: {pr.title}\n"
                f"Description: {pr.body}\n"
                f"Changed Files: {pr.changed_files}\n"
                f"Additions: {pr.additions}\n"
                f"Deletions: {pr.deletions}"
            )
            
            # Generate review
            llm_start_time = time.time()
            prompt = f"""Review this pull request and provide:
            1. Code quality assessment
            2. Potential issues or concerns
            3. Suggestions for improvement
            4. Overall recommendation (approve/request changes)

            PR Details:
            {pr_text}

            Return a JSON object with fields:
            - assessment
            - issues
            - suggestions
            - recommendation"""

            response = await self.llm_client.client.chat.completions.create(
                model=self.llm_client.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that reviews pull requests."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            review = response.choices[0].message.content
            
            # Log LLM usage
            self.tracker.log_llm_usage(
                model=self.llm_client.model,
                prompt=prompt,
                response=review,
                token_count=response.usage.total_tokens,
                duration=time.time() - llm_start_time
            )
            
            # Add review comment
            comment = (
                f"🤖 **Synapse PR Review**\n\n"
                f"**Assessment:**\n{review['assessment']}\n\n"
                f"**Issues:**\n{review['issues']}\n\n"
                f"**Suggestions:**\n{review['suggestions']}\n\n"
                f"**Recommendation:** {review['recommendation']}"
            )
            await self.client.add_comment(repo, pr_number, comment)
            
            # Log tool usage
            self.tracker.log_tool_usage(
                tool_name="review_pull_request",
                input_data={"repo": repo, "pr_number": pr_number},
                output_data={"review": review},
                duration=time.time() - start_time
            )
            
            return {
                "status": "success",
                "pr_number": pr_number,
                "review": review
            }
            
        except Exception as e:
            self.tracker.log_tool_usage(
                tool_name="review_pull_request",
                input_data={"repo": repo, "pr_number": pr_number},
                output_data={"error": str(e)},
                duration=time.time() - start_time,
                status="error"
            )
            raise
