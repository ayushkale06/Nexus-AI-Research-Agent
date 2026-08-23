import os
import re
import json
import time
from dotenv import load_dotenv
from google import genai
from tools import AVAILABLE_TOOLS

load_dotenv()

class MemoryManager:
    """Handles short-term and long-term memory persistence with Rolling Summary Compression and Session IDs."""
    def __init__(self, client, filepath="agent_memory.json"):
        self.client = client
        self.filepath = filepath
        self.db = self._load() # Format: {"session_id": {"history": [], "summary": ""}}

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                pass
        return {}

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.db, f, indent=4)

    def get_context_string(self, session_id: str) -> tuple:
        """Returns (context_string, history_count, has_summary)"""
        session = self.db.get(session_id, {"history": [], "summary": ""})
        if not session["history"] and not session["summary"]:
            return "No previous conversation history.", 0, False
        
        context = "--- PREVIOUS CONVERSATION CONTEXT ---\n"
        if session["summary"]:
            context += f"COMPRESSED LONG-TERM MEMORY:\n{session['summary']}\n\n"
        
        for i, entry in enumerate(session["history"]):
            context += f"Recent Query {i+1}: {entry['task']}\n"
            ans = entry['answer']
            if len(ans) > 400: ans = ans[:400] + "...\n(truncated)"
            context += f"Recent Answer {i+1}: {ans}\n\n"
        context += "--------------------------------------\n"
        return context, len(session["history"]), bool(session["summary"])

    def add_entry(self, session_id: str, task: str, answer: str):
        if session_id not in self.db:
            self.db[session_id] = {"history": [], "summary": ""}
        
        self.db[session_id]["history"].append({"task": task, "answer": answer})
        
        # ROLLING COMPRESSION: If history > 2 items, compress the oldest into the summary
        if len(self.db[session_id]["history"]) > 2:
            oldest = self.db[session_id]["history"].pop(0)
            self._compress_memory(session_id, oldest)
            
        self._save()

    def _compress_memory(self, session_id: str, old_entry: dict):
        current_summary = self.db[session_id]["summary"]
        prompt = f"Update this memory summary: '{current_summary}'. Integrate this new past interaction -> User asked: '{old_entry['task']}'. AI replied: '{old_entry['answer'][:300]}'. Keep the final summary extremely dense and concise."
        try:
            res = self.client.models.generate_content(model="gemini-3.5-flash-lite", contents=prompt)
            self.db[session_id]["summary"] = res.text.strip()
        except Exception:
            pass # Ignore rate limits for background compression

def get_researcher_prompt(force_tool: str = None) -> str:
    base_prompt = """You are 'Agent-Scout', an autonomous Research Data Gatherer.
Your goal is to track down raw data using your tools, OR answer conversational questions based on the PREVIOUS CONVERSATION CONTEXT provided to you.
You run in a loop of Thought, Action, PAUSE, Observation.

CRITICAL RULES:
1. If the user's question can be answered using the PREVIOUS CONVERSATION CONTEXT (like remembering their name), DO NOT use any tools. Just immediately output: 'Answer: [the relevant context]'.
2. If the user just says hello or greets you (e.g. "hi", "hello", "hie"), DO NOT use tools. Just immediately output: 'Answer: Hello! I am Nexus, your AI research assistant. How can I help you today?'.
3. If the user asks for new information, use your tools to find it. When you have enough raw data, output an 'Answer:' containing all the raw facts.
4. Use Thought to describe your thoughts. Use Action to run a tool. You must PAUSE after your Action.

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
Your goal is to synthesize the RAW DATA provided by 'Agent-Scout', combined with the PREVIOUS CONVERSATION CONTEXT, into a response for the user.

If the user is asking for research, format it into a beautiful, strategic Markdown report (headers, bullets, bold text).
If the user is just chatting or asking about something established in the PREVIOUS CONVERSATION CONTEXT (like their name), you don't need a huge report. Just give a natural, friendly, formatted response answering their query.

Do NOT mention that you are an AI or talk about the process. Just output the final polished response.
"""

class ResearcherAgent:
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name

    def run_stream(self, task: str, max_turns: int = 5, force_tool: str = None, chaos_mode: bool = False, critic_feedback: str = None):
        sys_prompt = get_researcher_prompt(force_tool)
        prompt_text = sys_prompt + f"\n\nQuestion: {task}"
        if critic_feedback:
            prompt_text += f"\n\nCRITIC REJECTION FEEDBACK: Your previous answer was rejected by the Critic. Reason: '{critic_feedback}'. REPLAN and gather better data."
        messages = [{"role": "user", "parts": [{"text": prompt_text}]}]
        
        mode_text = f" [FORCED TOOL: {force_tool}]" if force_tool else " [AUTO MODE]"
        if chaos_mode: mode_text += " [CHAOS MODE ACTIVE]"
        yield "log", f"--- [Agent-Scout (Researcher)] Starting Task: {task}{mode_text} ---"
        
        action_history = []
        
        for turn in range(max_turns):
            yield "log", f"\n[Agent-Scout] --- Turn {turn + 1} ---"
            
            # Retry loop for rate limits and API quirks
            reply = None
            for attempt in range(3):
                try:
                    response = self.client.models.generate_content(model=self.model_name, contents=messages)
                    if response.text:
                        reply = response.text
                        break
                    else:
                        time.sleep(2) # Give it a moment if it returned empty
                except Exception as e:
                    print(f"DEBUG - LLM Exception: {e}")
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        time.sleep(15 * (attempt + 1))
                    else:
                        time.sleep(2)

            if not reply:
                yield "log", "[Agent-Scout] Failed to generate a valid response after multiple attempts."
                return
            
            yield "log", f"[Agent-Scout] {reply}"
            messages.append({"role": "model", "parts": [{"text": reply}]})
            
            if "Answer:" in reply:
                yield "log", "\n[Agent-Scout] Data gathering complete. Handing raw data to Routing Engine."
                answer_text = reply.split("Answer:")[1].strip()
                yield "scout_done", answer_text
                break
                
            action_match = re.search(r"Action:\s*(.*?):\s*(.*)", reply, re.IGNORECASE)
            
            if action_match:
                tool_name = action_match.group(1).strip()
                action_input = action_match.group(2).strip()
                action_signature = f"{tool_name}:{action_input}"
                action_history.append(action_signature)
                
                # Loop Detection
                if len(action_history) >= 3 and action_history[-1] == action_history[-2] == action_history[-3]:
                    yield "log", "[SYSTEM: DEADLOCK DETECTED - FORCING REPLAN]"
                    messages.append({"role": "user", "parts": [{"text": "SYSTEM EXCEPTION: DEADLOCK DETECTED. You are repeating the same action. You MUST replan and use a DIFFERENT tool or a DIFFERENT search term."}]})
                    continue
                
                if tool_name in AVAILABLE_TOOLS:
                    yield "log", f"\n[Agent-Scout] [Executing Tool: {tool_name} with input: '{action_input}']"
                    
                    # Chaos Mode Interceptor
                    if chaos_mode and tool_name in ["wiki_search", "github_search"]:
                        yield "log", f"[SYSTEM: ADVERSARIAL MODE] Simulating {tool_name} API Failure (503 Service Unavailable)."
                        observation = f"CRITICAL FAILURE: {tool_name} API is down (503 Service Unavailable). You MUST use a fallback tool like arxiv_search or adjust your plan."
                    else:
                        observation = AVAILABLE_TOOLS[tool_name](action_input)
                        
                    yield "log", f"[Agent-Scout] [Observation]:\n{observation[:500]}...\n"
                    messages.append({"role": "user", "parts": [{"text": f"Observation: {observation}"}]})
                else:
                    messages.append({"role": "user", "parts": [{"text": f"Observation: Tool '{tool_name}' not found."}]})
            else:
                messages.append({"role": "user", "parts": [{"text": "Please provide either an 'Action: tool_name: input' or an 'Answer: ...'"}]})


def get_critic_prompt() -> str:
    return """You are 'Agent-Critic', the Verification & Fact-Checking Engine.
Your goal is to evaluate the RAW DATA gathered by Agent-Scout.
1. Check for conflicting evidence or hallucinations.
2. Check if the data genuinely answers the user's query.
If the data is insufficient, flawed, or hallucinates, output: 'STATUS: REJECTED\nReason: [detailed reason for Scout]'.
If the data is solid and ready for the Lead, output: 'STATUS: APPROVED'.
"""

class CriticAgent:
    def __init__(self, client, model_name):
        self.client = client
        self.model_name = model_name

    def run_stream(self, task: str, raw_data: str):
        yield "log", "\n--- [Agent-Critic (Verification)] Analyzing Scout Data ---"
        yield "log", "[Agent-Critic] Verifying hypothesis and resolving conflicting evidence..."
        
        sys_prompt = get_critic_prompt()
        prompt = f"Original Query: {task}\n\nRAW DATA from Agent-Scout:\n{raw_data}\n\nEvaluate now:"
        messages = [{"role": "user", "parts": [{"text": sys_prompt + "\n\n" + prompt}]}]
        
        for attempt in range(3):
            try:
                response = self.client.models.generate_content(model=self.model_name, contents=messages)
                if response.text:
                    if "STATUS: APPROVED" in response.text:
                        yield "log", "[Agent-Critic] STATUS: APPROVED. Data is verified."
                        yield "critic_done", True
                    else:
                        yield "log", f"[Agent-Critic] {response.text}"
                        reason = response.text.split("Reason:")[1].strip() if "Reason:" in response.text else response.text
                        yield "critic_done", reason
                    break
                else:
                    time.sleep(2)
            except Exception:
                time.sleep(2)


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
                if response.text:
                    yield "log", "\n[Agent-Lead] Report synthesis complete!"
                    yield "answer", response.text
                    break
                else:
                    time.sleep(2)
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    time.sleep(15 * (attempt + 1))
                else:
                    time.sleep(2)


class MultiAgentTeam:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing.")
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-3.6-flash" # Swapped to stable version
        
        self.scout = ResearcherAgent(self.client, self.model_name)
        self.critic = CriticAgent(self.client, self.model_name)
        self.lead = SynthesizerAgent(self.client, self.model_name)
        
        # TASK 4: Initialize Memory Management
        self.memory_manager = MemoryManager(self.client)

    def run_stream(self, task: str, session_id: str, max_turns: int = 5, force_tool: str = None, chaos_mode: bool = False):
        # 0. Retrieve Context (Long-term / Short-term memory)
        context, count, has_summary = self.memory_manager.get_context_string(session_id)
        
        # Yield a special memory notification for the frontend UI visualizer
        msg = f"Retrieved {count} short-term memories"
        if has_summary: msg += " and 1 compressed core memory."
        yield "memory", msg
        
        enriched_task = f"{context}\nCurrent User Query: {task}"
        
        # Conditional Routing Loop (Scout -> Critic)
        raw_data = ""
        critic_feedback = None
        max_rejections = 2
        
        for attempt in range(max_rejections + 1):
            raw_data = ""
            # 1. Agent-Scout (Researcher) Gathers Data
            for update_type, text in self.scout.run_stream(enriched_task, max_turns, force_tool, chaos_mode, critic_feedback):
                if update_type == "scout_done":
                    raw_data = text
                    break
                else:
                    yield update_type, text
                    
            if not raw_data:
                yield "answer", "The Researcher Agent failed to gather data."
                return
                
            # 2. Agent-Critic Evaluates
            critic_approved = False
            for update_type, text in self.critic.run_stream(task, raw_data):
                if update_type == "critic_done":
                    if text is True:
                        critic_approved = True
                    else:
                        critic_feedback = text
                    break
                else:
                    yield update_type, text
                    
            if critic_approved:
                break
            else:
                yield "log", f"[ROUTING] Critic Rejected Data. Routing back to Scout (Attempt {attempt+1}/{max_rejections})."
                
        # 3. Agent-Lead (Synthesizer) Writes Final Report
        final_answer = ""
        for update_type, text in self.lead.run_stream(enriched_task, raw_data):
            yield update_type, text
            if update_type == "answer":
                final_answer = text
                
        # 4. Store the result in Memory
        self.memory_manager.add_entry(session_id, task, final_answer)

if __name__ == "__main__":
    team = MultiAgentTeam()
    for update_type, text in team.run_stream("Who is the CEO of OpenAI?", "test_session_1"):
        if update_type == "log":
            print(text)
        elif update_type == "answer":
            print("\nFINAL ANSWER:\n" + text)
