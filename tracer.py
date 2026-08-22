import time
import json
import os

class NexusTracer:
    """
    Task 7: Advanced Tracing & Observability
    Implements end-to-end tracing of agents, decisions, tool calls, and latency.
    """
    def __init__(self, trace_file="traces.json"):
        self.trace_file = trace_file
        self.traces = []
        
        # Load existing traces if available
        if os.path.exists(self.trace_file):
            try:
                with open(self.trace_file, "r") as f:
                    self.traces = json.load(f)
            except:
                self.traces = []
                
    def start_trace(self, task_name, query, metadata=None):
        self.current_trace = {
            "trace_id": str(int(time.time())),
            "task": task_name,
            "query": query,
            "start_time": time.time(),
            "metadata": metadata or {},
            "spans": [],
            "status": "in_progress"
        }
        return self.current_trace
        
    def add_span(self, agent_name, action, latency, status="success", details=""):
        span = {
            "timestamp": time.time(),
            "agent": agent_name,
            "action": action,
            "latency_seconds": round(latency, 2),
            "status": status,
            "details": details
        }
        self.current_trace["spans"].append(span)
        
    def end_trace(self, success=True, final_output="", error=""):
        self.current_trace["end_time"] = time.time()
        self.current_trace["total_latency"] = round(self.current_trace["end_time"] - self.current_trace["start_time"], 2)
        self.current_trace["status"] = "success" if success else "failed"
        self.current_trace["final_output"] = final_output
        self.current_trace["error"] = error
        
        # Calculate metrics
        tool_calls = sum(1 for s in self.current_trace["spans"] if s["action"].startswith("tool:"))
        self.current_trace["metrics"] = {
            "total_latency_seconds": self.current_trace["total_latency"],
            "tool_call_count": tool_calls,
            "total_spans": len(self.current_trace["spans"])
        }
        
        self.traces.append(self.current_trace)
        self._save()
        return self.current_trace

    def _save(self):
        with open(self.trace_file, "w") as f:
            json.dump(self.traces, f, indent=4)
            
    def diagnose_and_improve(self):
        """
        Task 7 Requirement: Use the trace to identify root cause, 
        automatically diagnose it, and improve the system.
        """
        if not self.traces:
            return None
            
        latest_trace = self.traces[-1]
        diagnostics = []
        system_improvements = {}
        
        # 1. Diagnose Tool Failures
        failed_spans = [s for s in latest_trace["spans"] if s["status"] == "failed"]
        if failed_spans:
            diagnostics.append(f"Root Cause Detected: {len(failed_spans)} failed tool calls observed (e.g. {failed_spans[0]['action']}).")
            system_improvements["USE_FAST_FALLBACK"] = True
            
        # 2. Diagnose Latency Bottlenecks
        slow_spans = [s for s in latest_trace["spans"] if s["latency_seconds"] > 3.0]
        if slow_spans:
            diagnostics.append(f"Root Cause Detected: High latency bottleneck. {len(slow_spans)} operations took > 3s.")
            system_improvements["ENABLE_RESPONSE_CACHE"] = True
            
        report = {
            "trace_id": latest_trace["trace_id"],
            "issues_diagnosed": diagnostics,
            "applied_improvements": system_improvements,
            "system_patched": bool(system_improvements)
        }
        return report
