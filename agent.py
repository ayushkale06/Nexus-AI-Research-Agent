import os
import re
import time
from dotenv import load_dotenv
from google import genai
from tools import AVAILABLE_TOOLS

load_dotenv()

def get_researcher_prompt(force_tool: str = None) -> str:
    base_prompt = """You are 'Agent-Scout', an autonomous Research Data Gatherer.
Your ONLY goal is to track down raw data, facts, research papers, and open-source repos using your tools.
You run in a loop of Thought, Action, PAUSE, Observation.
When you have gathered enough raw data to satisfy the user's request, output an 'Answer:' containing all the raw facts you found. Do NOT worry about formatting it perfectly.

Use Thought to describe your thoughts.
Use Action to run one of the actions available to you.
You must PAUSE after your Action. Do not hallucinate the Observation.

"""
    if force_tool == "wiki_search":
        tools_section = "Available actions:\n- wiki_search: Searches Wikipedia.\nCRITICAL: You are FORCED to ONLY use 'wiki_search'."
    elif force_tool == "arxiv_search":
        tools_section = "Available actions:\n- arxiv_search: Searches ArXiv papers.\nCRITICAL: You are FORCED to ONLY use 'arxiv_search'."
    elif force_tool == "github_search":
        tools_section = "Available actions:\n- github_search: Searches GitHub repos.\nCRITICAL: You are FORCED to ONLY use 'github_search'."
    else:
        tools_section = """Available actions:
- wiki_search: Searches Wikipedia.
- arxiv_search: Searches the ArXiv database.
- github_search: Searches GitHub."""

    example_section = """
Example session:
Question: What is OpenAI doing?
Thought: I should search Wikipedia.
Action: wiki_search: OpenAI
PAUSE

Observation: Title: OpenAI... Summary: OpenAI is an AI research organization...

Thought: I have the data.
Answer: Raw Data Found: OpenAI is an AI research organization..."""

    return base_prompt + tools_section + example_section

def get_synthesizer_prompt() -> str:
    return """You are 'Agent-Lead', a Senior Executive Strategic Analyst.
Your goal is to take the RAW DATA provided by 'Agent-Scout' (the Researcher) and synthesize it into a beautiful, professional, and strategic Markdown report for the user.

Your final output MUST be highly structured, using markdown headers, bullet points, and bold text for emphasis.
Do NOT mention that you are an AI or talk about the process. Just output the final polished report answering the user's original query based ONLY on the provided raw data.
"""

class ResearcherAgent:
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name

    def run_stream(self, task: str, max_turns: int = 5, force_tool: str = None):
        sys_prompt = get_researcher_prompt(force_tool)
        messages = [{"role": "user", "parts": [{"text": sys_prompt + f"\n\nQuestion: {task}"}]}]
        
        mode_text = f" [FORCED TOOL: {force_tool}]" if force_tool else " [AUTO MODE]"
        yield "log", f"--- [Agent-Scout (Researcher)] Starting Task: {task}{mode_text} ---"
        
        for turn in range(max_turns):
            yield "log", f"\n[Agent-Scout] --- Turn {turn + 1} ---"
            
            # Retry loop for rate limits
            reply = None
            for attempt in range(3):
                try:
                    response = self.client.models.generate_content(model=self.model_name, contents=messages)
                    reply = response.text
                    break
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        time.sleep(15 * (attempt + 1))
                    else:
                        raise e

            if not reply:
                yield "log", "[Agent-Scout] Failed due to rate limits."
                return
            
            yield "log", f"[Agent-Scout] {reply}"
            messages.append({"role": "model", "parts": [{"text": reply}]})
            
            if "Answer:" in reply:
                yield "log", "\n[Agent-Scout] Data gathering complete. Handing raw data to Agent-Lead."
                answer_text = reply.split("Answer:")[1].strip()
                yield "scout_done", answer_text
                break
                
            action_match = re.search(r"Action:\s*(.*?):\s*(.*)", reply, re.IGNORECASE)
            
            if action_match:
                tool_name = action_match.group(1).strip()
                action_input = action_match.group(2).strip()
                
                if tool_name in AVAILABLE_TOOLS:
                    yield "log", f"\n[Agent-Scout] [Executing Tool: {tool_name} with input: '{action_input}']"
                    observation = AVAILABLE_TOOLS[tool_name](action_input)
                    yield "log", f"[Agent-Scout] [Observation]:\n{observation[:500]}...\n"
                    
                    messages.append({"role": "user", "parts": [{"text": f"Observation: {observation}"}]})
                else:
                    messages.append({"role": "user", "parts": [{"text": f"Observation: Tool '{tool_name}' not found."}]})
            else:
                messages.append({"role": "user", "parts": [{"text": "Please provide either an 'Action: tool_name: input' or an 'Answer: ...'"}]})


class SynthesizerAgent:
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name

    def run_stream(self, original_task: str, raw_data: str):
        yield "log", "\n--- [Agent-Lead (Synthesizer)] Orchestration Transfer ---"
        yield "log", "[Agent-Lead] Received raw data from Agent-Scout."
        yield "log", "[Agent-Lead] Thought: I will now synthesize this data into a professional strategic report."
        
        sys_prompt = get_synthesizer_prompt()
        prompt = f"Original User Query: {original_task}\n\nRAW DATA from Agent-Scout:\n{raw_data}\n\nPlease synthesize this into the final markdown report now."
        messages = [{"role": "user", "parts": [{"text": sys_prompt + "\n\n" + prompt}]}]
        
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(model=self.model_name, contents=messages)
                yield "log", "\n[Agent-Lead] Report synthesis complete!"
                yield "answer", response.text
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    time.sleep(15 * (attempt + 1))
                else:
                    raise e


class MultiAgentTeam:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-3.5-flash-lite"
        
        self.scout = ResearcherAgent(self.client, self.model_name)
        self.lead = SynthesizerAgent(self.client, self.model_name)

    def run_stream(self, task: str, max_turns: int = 5, force_tool: str = None):
        raw_data = ""
        
        # 1. Agent-Scout (Researcher) Gathers Data
        for update_type, text in self.scout.run_stream(task, max_turns, force_tool):
            if update_type == "scout_done":
                raw_data = text
                break
            else:
                yield update_type, text
                
        if not raw_data:
            yield "answer", "The Researcher Agent failed to gather data."
            return
            
        # 2. Agent-Lead (Synthesizer) Writes Final Report
        for update_type, text in self.lead.run_stream(task, raw_data):
            yield update_type, text

if __name__ == "__main__":
    team = MultiAgentTeam()
    for update_type, text in team.run_stream("Who is the CEO of OpenAI?"):
        if update_type == "log":
            print(text)
        elif update_type == "answer":
            print("\nFINAL ANSWER:\n" + text)
