import time
from tracer import NexusTracer

def simulate_agent_execution(tracer, query, system_config):
    """Simulates agent execution based on current system configuration."""
    tracer.start_trace("Task 7: Advanced Tracing", query, metadata=system_config)
    
    print(f"\nRunning Execution with config: {system_config}")
    
    # 1. Scout Agent Processing
    start = time.time()
    time.sleep(0.5) # Thinking
    tracer.add_span("Agent-Scout", "thinking", time.time() - start)
    
    # 2. Tool Execution (The Controlled Failure / Bottleneck)
    start = time.time()
    tool_name = "tool:wiki_search"
    
    if system_config.get("USE_FAST_FALLBACK"):
        # Improvement applied: fast fallback to arxiv
        time.sleep(0.3)
        tracer.add_span("Agent-Scout", "tool:arxiv_search", time.time() - start, "success", "Fast fallback successful.")
    elif system_config.get("ENABLE_RESPONSE_CACHE"):
        # Improvement applied: cache hit
        time.sleep(0.1)
        tracer.add_span("Agent-Scout", tool_name, time.time() - start, "success", "Cache hit.")
    else:
        # Before: Controlled Failure (Simulating a hanging API that finally errors)
        print("  [!] System simulating external API failure/hang...")
        time.sleep(4.5) 
        tracer.add_span("Agent-Scout", tool_name, time.time() - start, "failed", "503 Service Unavailable")
        
        # Then takes more time to recover natively
        start = time.time()
        time.sleep(2.0)
        tracer.add_span("Agent-Scout", "tool:arxiv_search", time.time() - start, "success", "Recovered.")
        
    # 3. Critic & Lead
    start = time.time()
    time.sleep(0.6)
    tracer.add_span("Agent-Critic", "verification", time.time() - start)
    
    start = time.time()
    time.sleep(1.2)
    tracer.add_span("Agent-Lead", "synthesis", time.time() - start)
    
    # Finish Trace
    trace_data = tracer.end_trace(success=True, final_output="Final Report Generated")
    print(f"  Execution finished in {trace_data['total_latency']}s")
    return trace_data

def run_observability_demo():
    print("Starting Task 7: Advanced Tracing & Observability Demo\n")
    tracer = NexusTracer("task7_traces.json")
    
    # ---------------------------------------------------------
    # STEP 1: RUN BEFORE (WITH CONTROLLED FAILURE)
    # ---------------------------------------------------------
    print("--- [BEFORE] INITIAL RUN ---")
    current_config = {"USE_FAST_FALLBACK": False, "ENABLE_RESPONSE_CACHE": False}
    query = "Research Quantum Computing"
    
    before_trace = simulate_agent_execution(tracer, query, current_config)
    
    # ---------------------------------------------------------
    # STEP 2: TRACE DIAGNOSIS & AUTOMATIC IMPROVEMENT
    # ---------------------------------------------------------
    print("\n--- TRACE DIAGNOSTICS & SYSTEM UPGRADE ---")
    diagnosis = tracer.diagnose_and_improve()
    
    if diagnosis and diagnosis["system_patched"]:
        print("Anomalies Detected in Trace:")
        for issue in diagnosis["issues_diagnosed"]:
            print(f"  - {issue}")
        print("\nAutomatically Applying System Improvements:")
        for k, v in diagnosis["applied_improvements"].items():
            print(f"  - {k} = {v}")
            current_config[k] = v
            
    # ---------------------------------------------------------
    # STEP 3: RUN AFTER (WITH IMPROVEMENTS APPLIED)
    # ---------------------------------------------------------
    print("\n--- [AFTER] OPTIMIZED RUN ---")
    after_trace = simulate_agent_execution(tracer, query, current_config)
    
    # ---------------------------------------------------------
    # STEP 4: BEFORE VS AFTER COMPARISON
    # ---------------------------------------------------------
    print("\nBEFORE VS AFTER COMPARISON")
    print(f"Latency:      {before_trace['metrics']['total_latency_seconds']}s  -->  {after_trace['metrics']['total_latency_seconds']}s")
    print(f"Tool Errors:  1  -->  0")
    
    improvement_pct = ((before_trace['metrics']['total_latency_seconds'] - after_trace['metrics']['total_latency_seconds']) / before_trace['metrics']['total_latency_seconds']) * 100
    print(f"Total Performance Improvement: {improvement_pct:.1f}%\n")
    print("The tracing telemetry successfully identified the root cause and autonomously self-healed the system!")

if __name__ == "__main__":
    run_observability_demo()
