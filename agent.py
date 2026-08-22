import os
import re
from dotenv import load_dotenv
from google import genai
from tools import AVAILABLE_TOOLS

load_dotenv()

# We will use the new google-genai SDK
# You will need to get a free Gemini API key from Google AI Studio (https://aistudio.google.com/)
# Set it in a .env file as GEMINI_API_KEY=your_key

SYSTEM_PROMPT = """
You are an autonomous Research & Competitor Tracking AI Agent.
Your goal is to track research trends, patent developments, and competitor activities.

You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer.

Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you.
You must PAUSE after your Action. Do not hallucinate the Observation. The system will provide the Observation.

Available actions:
- wiki_search: Searches Wikipedia for general knowledge and company overviews.
  e.g. Action: wiki_search: OpenAI
- patent_search: Searches the patent database for recent patents filed by a competitor.
  e.g. Action: patent_search: OpenAI

Example session:

Question: What is OpenAI and do they have any recent patents?
Thought: I should first find out what OpenAI is using wiki_search.
Action: wiki_search: OpenAI
PAUSE

You will be called again with this:
Observation: Title: OpenAI... Summary: OpenAI is an AI research organization...

Thought: Now I should check their recent patents.
Action: patent_search: OpenAI
PAUSE

Observation: Recent Patents for OpenAI: 1. US-Pat-109...

Thought: I have the information I need.
Answer: # Competitor Report: OpenAI
OpenAI is an AI research organization. 
**Recent Patents:**
- US-Pat-109...

Now begin! Always format your final Answer beautifully in Markdown.
"""

class ReActAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing. Please set it in a .env file or environment variable.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-3.5-flash-lite" # Lite model with higher quota limits

    def run_stream(self, task: str, max_turns: int = 5):
        import time
        messages = [{"role": "user", "parts": [{"text": SYSTEM_PROMPT + f"\n\nQuestion: {task}"}]}]
        
        yield "log", f"--- Starting Task: {task} ---"
        
        for turn in range(max_turns):
            yield "log", f"\n--- Turn {turn + 1} ---"
            
            # Retry loop for rate limits (429 errors)
            max_retries = 3
            reply = None
            for attempt in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=messages
                    )
                    reply = response.text
                    break # Success, exit retry loop
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        wait_time = 15 * (attempt + 1)
                        yield "log", f"[Rate Limit Hit] Waiting {wait_time} seconds before retrying..."
                        time.sleep(wait_time)
                    else:
                        raise e

            if not reply:
                yield "log", "Failed after multiple retries due to rate limits."
                return
            
            yield "log", reply
            
            messages.append({"role": "model", "parts": [{"text": reply}]})
            
            if "Answer:" in reply:
                yield "log", "\n[SUCCESS] Task Complete!"
                # Extract the final answer text
                answer_text = reply.split("Answer:")[1].strip()
                yield "answer", answer_text
                break
                
            action_match = re.search(r"Action:\s*(.*?):\s*(.*)", reply, re.IGNORECASE)
            
            if action_match:
                tool_name = action_match.group(1).strip()
                action_input = action_match.group(2).strip()
                
                if tool_name in AVAILABLE_TOOLS:
                    yield "log", f"\n[Executing Tool: {tool_name} with input: '{action_input}']"
                    observation = AVAILABLE_TOOLS[tool_name](action_input)
                    yield "log", f"[Observation]:\n{observation[:500]}...\n"
                    
                    obs_message = f"Observation: {observation}"
                    messages.append({"role": "user", "parts": [{"text": obs_message}]})
                else:
                    obs_message = f"Observation: Tool '{tool_name}' not found. Available tools: {list(AVAILABLE_TOOLS.keys())}"
                    messages.append({"role": "user", "parts": [{"text": obs_message}]})
            else:
                messages.append({"role": "user", "parts": [{"text": "Please provide either an 'Action: tool_name: input' or an 'Answer: ...'"}]})

    def run(self, task: str, max_turns: int = 5):
        # Keeps backwards compatibility for terminal usage
        for update_type, text in self.run_stream(task, max_turns):
            if update_type == "log":
                print(text)

if __name__ == "__main__":
    try:
        agent = ReActAgent()
        test_task = "Research the competitor 'OpenAI' and tell me about their company background and any recent patents they filed."
        agent.run(test_task)
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have set GEMINI_API_KEY in a .env file.")
