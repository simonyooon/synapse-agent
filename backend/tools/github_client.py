"""
GitHub API client for Synapse agent platform.
Handles authentication, issue management, and PR operations.
"""
from typing import Dict, List, Optional
from github import Github, Auth
from github.Issue import Issue
from github.PullRequest import PullRequest
from ..config import get_settings

class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client.
        
        Args:
            token: GitHub token. If None, uses token from config.
        """
        settings = get_settings()
        self.token = token or settings.github_token
        if not self.token:
            raise ValueError("GitHub token not provided")
        self.client = Github(auth=Auth.Token(self.token))

    async def get_issues(
        self,
        repo: str,
        state: str = "open",
        labels: Optional[List[str]] = None
    ) -> List[Issue]:
        """Get repository issues.
        
        Args:
            repo: Repository name (owner/repo)
            state: Issue state (open/closed/all)
            labels: List of labels to filter by
            
        Returns:
            List of Issue objects
        """
        try:
            repository = self.client.get_repo(repo)
            issues = repository.get_issues(state=state, labels=labels)
            return list(issues)
        except Exception as e:
            raise Exception(f"Error fetching issues: {str(e)}")

    async def get_pull_requests(
        self,
        repo: str,
        state: str = "open"
    ) -> List[PullRequest]:
        """Get repository pull requests.
        
        Args:
            repo: Repository name (owner/repo)
            state: PR state (open/closed/all)
            
        Returns:
            List of PullRequest objects
        """
        try:
            repository = self.client.get_repo(repo)
            prs = repository.get_pulls(state=state)
            return list(prs)
        except Exception as e:
            raise Exception(f"Error fetching pull requests: {str(e)}")

    async def create_issue(
        self,
        repo: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Issue:
        """Create a new issue.
        
        Args:
            repo: Repository name (owner/repo)
            title: Issue title
            body: Issue body
            labels: List of labels
            assignees: List of assignees
            
        Returns:
            Created Issue object
        """
        try:
            repository = self.client.get_repo(repo)
            issue = repository.create_issue(
                title=title,
                body=body,
                labels=labels or [],
                assignees=assignees or []
            )
            return issue
        except Exception as e:
            raise Exception(f"Error creating issue: {str(e)}")

    async def add_comment(
        self,
        repo: str,
        issue_number: int,
        body: str
    ) -> Dict:
        """Add a comment to an issue or PR.
        
        Args:
            repo: Repository name (owner/repo)
            issue_number: Issue/PR number
            body: Comment body
            
        Returns:
            Comment data
        """
        try:
            repository = self.client.get_repo(repo)
            issue = repository.get_issue(issue_number)
            comment = issue.create_comment(body)
            return {
                "id": comment.id,
                "body": comment.body,
                "created_at": comment.created_at.isoformat()
            }
        except Exception as e:
            raise Exception(f"Error adding comment: {str(e)}")

    async def update_labels(
        self,
        repo: str,
        issue_number: int,
        labels: List[str]
    ) -> List[str]:
        """Update issue/PR labels.
        
        Args:
            repo: Repository name (owner/repo)
            issue_number: Issue/PR number
            labels: New list of labels
            
        Returns:
            Updated list of labels
        """
        try:
            repository = self.client.get_repo(repo)
            issue = repository.get_issue(issue_number)
            issue.set_labels(*labels)
            return [label.name for label in issue.labels]
        except Exception as e:
            raise Exception(f"Error updating labels: {str(e)}") 