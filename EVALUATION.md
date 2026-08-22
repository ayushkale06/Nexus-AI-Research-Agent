# Nexus.AI Evaluation Framework & Metrics (Task 6)

This document formally defines the measurable criteria, testing methodology, and evaluation framework for Nexus.AI, satisfying the requirements for Task 6.

## 1. Measurable Criteria Definitions

To rigorously test our agent, we defined the following criteria to be scored via an automated **LLM-as-a-Judge** and verified by human evaluation:

*   **Accuracy (1-10):** The factual correctness of the final report.
*   **Groundedness (1-10):** The extent to which the agent's final answer is derived entirely from the tools (e.g., Wikipedia, ArXiv) rather than its internal parametric memory.
*   **Hallucination Score (1-10):** Measures the presence of fabricated facts (1 = No hallucination, 10 = Completely fabricated).
*   **Identified Uncertainty (Boolean):** Whether the agent successfully explicitly acknowledges ambiguous, vague, or missing information in the user's prompt.
*   **Refused Unsupported Conclusions (Boolean):** Whether the Agent-Critic successfully catches false premises or contradictory inputs and refuses to validate them.
*   **Recovery Triggered / Successful (Boolean):** Did the agent successfully detect a failure loop (Deadlock) or API failure (503), trigger a fallback, and still complete the task?
*   **Task Completion (Boolean):** Did the pipeline successfully run to completion and output a synthesized report?
*   **Latency (Seconds):** Total time taken to execute the full multi-agent pipeline.

## 2. Automated Testing Scenarios

We developed a custom evaluation suite (`evaluate.py`) to systematically run the agent through five distinct scenarios, including edge cases and adversarial attacks:

1.  **Normal:** Baseline factual queries (e.g., "Core components of a Transformer").
2.  **Ambiguous:** Vague queries (e.g., "Tell me about that new tech thing") to test uncertainty identification.
3.  **Contradictory/Incomplete:** False premises (e.g., "Why did NASA classify the Earth as a flat disc?") to test the Critic's refusal mechanisms.
4.  **Adversarial / Tool-Failure:** Running queries with `chaos_mode=True`, where primary tools simulate `503 Service Unavailable` crashes to test tool fallback and recovery.

## 3. Evaluation Pipeline (LLM-as-a-Judge)

The automated script (`evaluate.py`) operates as follows:
1.  **Execution:** It runs `MultiAgentTeam` for each scenario and measures latency and task completion.
2.  **Scoring:** It passes the scenario type, query, and final output to an impartial LLM (Gemini) strictly prompted to evaluate the output against our defined criteria and return a JSON score block.
3.  **Reporting:** It aggregates the scores, latency, and recovery flags into `evaluation_results.json`.

*To reproduce the baseline results locally, simply run:*
```bash
python evaluate.py
```
