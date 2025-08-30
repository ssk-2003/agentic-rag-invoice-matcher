import json
from datetime import datetime
from typing import Dict, Any, List
import os

class AuditLogger:
    """
    The Audit Logger keeps track of everything the system does.
    Think of it as a detailed logbook of all actions.
    """
    
    def __init__(self, log_file: str = "data/audit_log.jsonl"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def log_action(
        self, 
        agent_name: str, 
        action: str, 
        input_data: Dict[str, Any], 
        output_data: Dict[str, Any], 
        confidence: float
    ):
        """Log an agent action"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "action": action,
            "input_data": input_data,
            "output_data": output_data,
            "confidence": confidence
        }
        
        # Write to file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_recent_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent log entries"""
        logs = []
        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    logs.append(json.loads(line.strip()))
        except FileNotFoundError:
            pass
        return logs
    
    def get_session_logs(self, session_id: str) -> List[Dict[str, Any]]:
        """Get logs for a specific session"""
        logs = []
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    log_entry = json.loads(line.strip())
                    if log_entry.get("input_data", {}).get("session_id") == session_id:
                        logs.append(log_entry)
        except FileNotFoundError:
            pass
        return logs

# Global audit logger instance
audit_logger = AuditLogger()
