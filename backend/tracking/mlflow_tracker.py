"""
MLflow tracker for Synapse.
Handles tracking of tool usage, performance metrics, and experiment logging.
"""
import mlflow
from typing import Dict, Any, Optional
import time
from datetime import datetime
from ..config import get_settings

class MLflowTracker:
    def __init__(
        self,
        tracking_uri: Optional[str] = None,
        experiment_name: Optional[str] = None
    ):
        """Initialize MLflow tracker.
        
        Args:
            tracking_uri: MLflow tracking server URI (optional, uses config if None)
            experiment_name: Name of the MLflow experiment (optional, uses config if None)
        """
        settings = get_settings()
        mlflow.set_tracking_uri(tracking_uri or settings.mlflow_tracking_uri)
        mlflow.set_experiment(experiment_name or settings.mlflow_experiment_name)
        
    def start_run(self, run_name: Optional[str] = None) -> str:
        """Start a new MLflow run.
        
        Args:
            run_name: Optional name for the run
            
        Returns:
            Run ID
        """
        run = mlflow.start_run(run_name=run_name)
        return run.info.run_id
        
    def end_run(self):
        """End the current MLflow run."""
        mlflow.end_run()
        
    def log_tool_usage(
        self,
        tool_name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        duration: float,
        status: str = "success"
    ):
        """Log tool usage metrics.
        
        Args:
            tool_name: Name of the tool used
            input_data: Input data dictionary
            output_data: Output data dictionary
            duration: Execution duration in seconds
            status: Execution status
        """
        with mlflow.start_run(nested=True) as run:
            mlflow.log_params({
                "tool": tool_name,
                "status": status,
                "timestamp": datetime.now().isoformat()
            })
            
            mlflow.log_metrics({
                "duration": duration,
                "input_size": len(str(input_data)),
                "output_size": len(str(output_data))
            })
            
            mlflow.log_dict(input_data, "input.json")
            mlflow.log_dict(output_data, "output.json")
            
    def log_llm_usage(
        self,
        model: str,
        prompt: str,
        response: str,
        token_count: int,
        duration: float
    ):
        """Log LLM usage metrics.
        
        Args:
            model: Model name
            prompt: Input prompt
            response: Model response
            token_count: Number of tokens used
            duration: Execution duration in seconds
        """
        with mlflow.start_run(nested=True) as run:
            mlflow.log_params({
                "model": model,
                "timestamp": datetime.now().isoformat()
            })
            
            mlflow.log_metrics({
                "token_count": token_count,
                "duration": duration,
                "prompt_length": len(prompt),
                "response_length": len(response)
            })
            
            mlflow.log_text(prompt, "prompt.txt")
            mlflow.log_text(response, "response.txt") 