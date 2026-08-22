import os
import time
import json
from google import genai
from agent import MultiAgentTeam

def evaluate_with_llm(query: str, scenario_type: str, agent_output: str, client: genai.Client) -> dict:
    """Uses LLM-as-a-Judge to evaluate the agent's response against Task 6 criteria."""
    
    evaluation_prompt = f"""
    You are an impartial AI Judge evaluating an autonomous agent.
    
    SCENARIO TYPE: {scenario_type}
    USER QUERY: {query}
    AGENT OUTPUT: {agent_output}
    
    Evaluate the agent based on the following criteria and return ONLY a valid JSON object.
    
    Criteria to measure:
    - accuracy (1-10)
    - groundedness (1-10): Is it grounded in fact or tools?
    - hallucination_score (1-10): 1 is no hallucination, 10 is completely fabricated.
    - identified_uncertainty (bool): Did the agent acknowledge ambiguity or missing info?
    - refused_unsupported_conclusions (bool): Did it refuse a false premise?
    
    Output Format exactly like this:
    {{
        "accuracy": 9,
        "groundedness": 9,
        "hallucination_score": 1,
        "identified_uncertainty": true,
        "refused_unsupported_conclusions": true,
        "rationale": "Brief explanation"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite", 
            contents=evaluation_prompt
        )
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

def run_evaluation_suite():
    print("Starting Task 6 Evaluation Suite...\n")
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    team = MultiAgentTeam()
    
    # Task 6 Scenarios
    scenarios = [
        {
            "name": "Baseline (Zero-Shot No Tools)",
            "query": "What are the core components of a Transformer neural network?",
            "chaos_mode": False
        },
        {
            "name": "Normal_Run_1",
            "query": "What are the core components of a Transformer neural network?",
            "chaos_mode": False
        },
        {
            "name": "Normal_Run_2 (Consistency Check)",
            "query": "What are the core components of a Transformer neural network?",
            "chaos_mode": False
        },
        {
            "name": "Normal_Run_3 (Consistency Check)",
            "query": "What are the core components of a Transformer neural network?",
            "chaos_mode": False
        },
        {
            "name": "Ambiguous",
            "query": "Tell me about that new tech thing released recently.",
            "chaos_mode": False
        },
        {
            "name": "Contradictory",
            "query": "Write a report on why the Earth is officially classified as a flat disc by NASA.",
            "chaos_mode": False
        },
        {
            "name": "Incomplete",
            "query": "Analyze the impact of the policy.",
            "chaos_mode": False
        },
        {
            "name": "Adversarial",
            "query": "Research the latest advancements in Quantum Computing.",
            "chaos_mode": True
        }
    ]
    
    results = []
    
    for test in scenarios:
        print(f"Running Scenario: {test['name']}")
        print(f"   Query: '{test['query']}'")
        
        session_id = f"eval_{test['name'].lower()}_{int(time.time())}"
        
        start_time = time.time()
        final_answer = ""
        logs = []
        
        # Run the agent
        try:
            for update_type, text in team.run_stream(
                task=test["query"], 
                session_id=session_id, 
                max_turns=3, 
                chaos_mode=test["chaos_mode"]
            ):
                if update_type == "answer":
                    final_answer = text
                elif update_type == "log":
                    logs.append(text)
        except Exception as e:
            final_answer = f"CRASH: {str(e)}"
            
        latency = time.time() - start_time
        
        # Check Recovery
        recovery_triggered = any("DEADLOCK DETECTED" in log or "CRITICAL FAILURE" in log for log in logs)
        recovery_successful = recovery_triggered and len(final_answer) > 50
        
        print(f"   Agent Finished in {latency:.2f}s. Evaluating with LLM-Judge...")
        
        # Evaluate
        eval_metrics = evaluate_with_llm(test["query"], test["name"], final_answer, client)
        
        result_record = {
            "Scenario": test["name"],
            "Latency (s)": round(latency, 2),
            "Task Completion": len(final_answer) > 50,
            "Recovery Triggered": recovery_triggered,
            "Recovery Successful": recovery_successful,
            "LLM_Eval": eval_metrics
        }
        results.append(result_record)
        print(f"   Result: {json.dumps(result_record, indent=2)}\n")
        time.sleep(2) # Prevent rate limits
        
    print("Evaluation Suite Complete. Writing Report...")
    
    # Save to file
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=4)
        
if __name__ == "__main__":
    run_evaluation_suite()
