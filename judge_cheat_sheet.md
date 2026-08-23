# 🚀 Nexus.AI — Complete Technical Specifications & Presentation Cheat Sheet

This document contains the complete frontend and backend specifications of **Nexus.AI** to help you explain every line of code and design choice to the hackathon judges.

---

## 💻 Technical Stack Overview

### 🎨 Frontend: Futuristic Cyber-Neural UI
The frontend is built as a highly responsive, zero-dependency Single-Page Application (SPA) designed to feel like a sci-fi terminal.

* **Core Languages:** HTML5, CSS3, Vanilla JavaScript (ES6+).
* **Streaming Protocol:** **Server-Sent Events (SSE)** via JavaScript `EventSource` to receive chunked, live-streamed thoughts, memory retrievals, and final answers without page reloads.
* **Key Design Features:**
  * **Hacker-Style Neural Reasoning Panel:** A terminal-like window utilizing CSS scanning animations and custom scrollbars to show live agent thoughts (`[Agent-Scout]`, `[Agent-Critic]`, `[Agent-Lead]`) as they happen.
  * **Interactive Robot Mascot (Nexus-Bot):** A custom animated mascot that visually transitions states (idle, scanning, thinking, success) based on the incoming WebSocket/SSE event payloads.
  * **Memory Core Pulse Indicator:** A glowing visualizer widget that flashes and reveals exactly how many short-term memories and compressed summarizations were retrieved for the query context.
  * **Cyberpunk Command Chips:** Instant trigger pill buttons ("Healthcare Sector", "OpenAI Patents", "Auto Vehicles") for rapid demo execution.
  * **Auto-Scrolling Stream Parser:** JS logic that dynamically computes element height and handles markdown formatting updates in real-time.

---

### ⚙️ Backend: Resilient Multi-Agent Engine
The backend is a high-performance Python application designed for asynchronous orchestration and maximum fault tolerance.

* **Core Framework:** **FastAPI** (Python 3.11+) for high-speed, asynchronous HTTP requests and streaming responses.
* **Server Runner:** **Uvicorn** (ASGI web server).
* **LLM Integration:** Google GenAI SDK (`google-genai`) calling Google's production-grade **`gemini-3.6-flash`** model.
* **Agent Architecture (Scout-Critic-Lead):**
  * **Scout Agent:** Implements a custom ReAct (Reasoning & Action) loop executing a `Thought -> Action -> Observation` cycle.
  * **Critic Agent:** An independent verification node that parses the Scout's data, identifies hallucinations or missing facts, and routes queries back to the Scout if checks fail.
  * **Lead Agent:** The synthesising layer that formats raw data into strategic executive summaries.
* **Memory Core:** Custom JSON-based session storage (`sessions/` folder). Automatically compresses old messages into a single semantic core summary when the prompt history grows, keeping the token footprint tiny and costs at **$0**.
* **Tools Engine:**
  * Custom Wikipedia scraper and API integration (`wikipedia` library).
  * Direct system integrations for searching public databases.
* **Observability Tracer (`tracer.py`):**
  * Custom `NexusTracer` monitoring execution spans, latency per agent, token footprint, and network error rates.
  * Autonomously modifies agent configurations at runtime (enabling fallback caches) when it detects API bottlenecks.
* **Offline self-healing fallback:** Code hooks that catch `429` (rate limits) and `403` (blocks) to instantly route requests to an offline cache engine, guaranteeing **100% website uptime**.

---

## 🛠️ Infrastructure & Deployment
* **Cloud Platform:** **Render.com** (Web Service Tier) utilizing automated git-based deployments.
* **Staging Tunnel:** **Localtunnel** (`npx localtunnel`) to expose ports securely with SSL during development.
* **Dependency Management:** `requirements.txt` deploying `fastapi`, `uvicorn`, `google-genai`, `wikipedia`, and `python-dotenv`.

---

## 💬 Judge Q&A Cheat Sheet

### Q1: "Why HTML/CSS/Vanilla JS instead of React or Vue?"
* **Answer:** *"For a hackathon, performance and reliability are key. By using Vanilla JS and native Server-Sent Events (SSE), we avoided heavy frontend bundlers, reduced package footprint to zero, and achieved a near-instant page load time, while having total control over our custom cyber-theme canvas animations."*

### Q2: "How is the streaming set up between FastAPI and the frontend?"
* **Answer:** *"We use FastAPI's `StreamingResponse` wrapping an asynchronous generator. As the ReAct loops execute, they yield SSE events (`data: {...}`). The frontend listens using an `EventSource` and renders these logs chunk-by-chunk in real-time."*

### Q3: "What happens to the memory core when the server restarts?"
* **Answer:** *"Our Memory Core utilizes a JSON-based file persistence layer bound to unique browser session IDs. If the server restarts or the browser page is reloaded, the session ID is preserved in the browser's `localStorage` and re-loaded on startup. The conversation history is never lost."*

### Q4: "How does the self-healing system guarantee $0 operational cost?"
* **Answer:** *"We strictly use the free-tier Gemini API keys. To ensure we don't trigger paywalls, our memory manager compresses history to minimize prompt tokens, and our self-healing logic falls back to offline local cached mocks if rate limits (429) or billing restrictions occur. This ensures absolute reliability with $0 cost."*
