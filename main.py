import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
import json
import asyncio
from agent import MultiAgentTeam

app = FastAPI()

# This is our custom HTML/CSS/JS frontend!


html_content = """\n<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus.AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
    <style>
        :root {
            --bg-dark: #171717;
            --bg-sidebar: #0d0d0d;
            --border-color: rgba(255, 255, 255, 0.08);
            --text-main: #e3e3e3;
            --text-muted: #b4b4b4;
            --accent: #10b981;
            --accent-glow: #34d399;
            --bubble-user: #2f2f2f;
            --bubble-agent: transparent;
            --font-main: 'Plus Jakarta Sans', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }

        body {
            font-family: var(--font-main);
            background-color: var(--bg-dark);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* Sidebar Styling */
        .sidebar {
            width: 260px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
            z-index: 100;
        }

        .sidebar-header {
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .sidebar-header h2 {
            margin: 0;
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 1px;
            color: var(--accent-glow);
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .sidebar-btn {
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            color: white;
            padding: 10px 16px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s;
        }

        .sidebar-btn:hover {
            background-color: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.25);
        }

        .sidebar-sessions {
            flex: 1;
            overflow-y: auto;
            padding: 0 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .sidebar-sessions::-webkit-scrollbar {
            width: 4px;
        }

        .sidebar-sessions::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }

        .session-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 12px;
            border-radius: 8px;
            font-size: 13.5px;
            cursor: pointer;
            color: #d1d1d1;
            transition: background 0.2s;
        }

        .session-item:hover {
            background-color: rgba(255, 255, 255, 0.05);
        }

        .session-item.active {
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
            font-weight: 500;
        }

        .session-title {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 170px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .session-delete {
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            padding: 2px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s, color 0.2s;
        }

        .session-item:hover .session-delete {
            opacity: 0.6;
        }

        .session-delete:hover {
            opacity: 1 !important;
            color: #f87171;
            background-color: rgba(248, 113, 113, 0.1);
        }

        .sidebar-footer {
            padding: 16px;
            border-top: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .settings-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 13px;
            color: var(--text-muted);
        }

        .settings-select {
            background: #2a2a2a;
            border: 1px solid var(--border-color);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            outline: none;
            cursor: pointer;
        }

        .switch {
            position: relative;
            display: inline-block;
            width: 34px;
            height: 20px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: #3e3e3e;
            transition: .4s;
            border-radius: 34px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 14px;
            width: 14px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background-color: var(--accent);
        }

        input:checked + .slider:before {
            transform: translateX(14px);
        }

        /* Main Content Panel */
        .main-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100vh;
            position: relative;
        }

        /* Top Header Navigation */
        .top-nav {
            height: 56px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 24px;
            flex-shrink: 0;
            background-color: var(--bg-dark);
        }

        .model-pill {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 12px;
            font-weight: 500;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .model-pulse-dot {
            width: 6px;
            height: 6px;
            background-color: var(--accent);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent);
        }

        /* Memory Alert Notification */
        .memory-core {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 11px;
            font-weight: 600;
            color: var(--accent-glow);
            opacity: 0;
            transform: translateY(-5px);
            transition: all 0.3s;
        }

        .memory-core.active {
            opacity: 1;
            transform: translateY(0);
        }

        .memory-pulse {
            width: 6px;
            height: 6px;
            background-color: var(--accent-glow);
            border-radius: 50%;
            animation: pulse 1s infinite alternate;
        }

        @keyframes pulse {
            from { opacity: 0.4; }
            to { opacity: 1; }
        }

        /* Chat Area */
        .chat-area {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 24px;
        }

        .chat-area::-webkit-scrollbar {
            width: 8px;
        }

        .chat-area::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }

        .chat-wrapper {
            width: 100%;
            max-width: 800px;
            padding: 0 24px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            gap: 28px;
        }

        /* Message Bubbles */
        .message-row {
            display: flex;
            gap: 16px;
            width: 100%;
            animation: fadeIn 0.4s ease forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message-row.user {
            justify-content: flex-end;
        }

        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 700;
            flex-shrink: 0;
        }

        .avatar.user-avatar {
            background: #4f46e5;
            color: white;
            order: 2;
        }

        .avatar.agent-avatar {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--accent);
            color: var(--accent-glow);
        }

        .bubble-content {
            max-width: 85%;
            font-size: 15px;
            line-height: 1.6;
        }

        .user .bubble-content {
            background-color: var(--bubble-user);
            padding: 10px 16px;
            border-radius: 18px 18px 2px 18px;
            color: white;
        }

        .agent .bubble-content {
            flex: 1;
            color: var(--text-main);
        }

        /* Collapsible Reasoning Process Accordion */
        .thought-accordion {
            border-left: 2px solid rgba(16, 185, 129, 0.3);
            background: rgba(16, 185, 129, 0.03);
            margin: 12px 0;
            border-radius: 0 6px 6px 0;
            overflow: hidden;
        }

        .thought-accordion summary {
            padding: 10px 14px;
            font-size: 12.5px;
            font-weight: 600;
            color: var(--accent-glow);
            cursor: pointer;
            outline: none;
            user-select: none;
            display: flex;
            align-items: center;
            gap: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .thought-accordion summary::-webkit-details-marker {
            display: none;
        }

        .thought-accordion summary::before {
            content: '▶';
            font-size: 9px;
            display: inline-block;
            transition: transform 0.2s;
        }

        .thought-accordion[open] summary::before {
            transform: rotate(90deg);
        }

        .reasoning-content {
            padding: 0 14px 14px 14px;
            font-family: var(--font-mono);
            font-size: 13px;
            color: #a7f3d0;
            white-space: pre-wrap;
            line-height: 1.5;
            max-height: 250px;
            overflow-y: auto;
        }

        /* Welcome Hologram Panel */
        .welcome-panel {
            margin: auto;
            text-align: center;
            max-width: 600px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
            padding-bottom: 8vh;
        }

        .welcome-panel h1 {
            font-size: 32px;
            font-weight: 800;
            margin: 0;
            background: linear-gradient(135deg, #fff 0%, #a7f3d0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.5px;
        }

        .welcome-panel p {
            font-size: 15px;
            color: var(--text-muted);
            margin: 0;
        }

        /* Suggestion Prompt Cards Grid */
        .suggestion-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 24px;
            width: 100%;
        }

        .suggestion-card {
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            text-align: left;
            cursor: pointer;
            transition: all 0.2s;
        }

        .suggestion-card:hover {
            background-color: rgba(255, 255, 255, 0.05);
            border-color: rgba(16, 185, 129, 0.3);
            transform: translateY(-2px);
        }

        .suggestion-card strong {
            display: block;
            font-size: 13.5px;
            font-weight: 600;
            color: white;
            margin-bottom: 4px;
        }

        .suggestion-card span {
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.4;
            display: block;
        }

        /* Code Block Styling */
        pre {
            background: #0f0f0f;
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
            position: relative;
            margin: 16px 0;
            border: 1px solid var(--border-color);
        }

        code {
            font-family: var(--font-mono);
            font-size: 14px;
            color: #67e8f9;
        }

        /* Copy Button for Code Blocks */
        .copy-btn {
            position: absolute;
            top: 8px;
            right: 8px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .copy-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }

        /* Markdown Styling inside Agent bubbles */
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {
            color: white;
            margin-top: 24px;
            margin-bottom: 12px;
        }

        .markdown-body p {
            margin-bottom: 16px;
        }

        .markdown-body ul, .markdown-body ol {
            padding-left: 20px;
            margin-bottom: 16px;
        }

        .markdown-body li {
            margin-bottom: 8px;
        }

        /* Input Panel */
        .input-panel {
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 16px 24px 24px 24px;
            box-sizing: border-box;
            background: linear-gradient(180deg, rgba(23, 23, 23, 0) 0%, rgba(23, 23, 23, 1) 40%);
            flex-shrink: 0;
            z-index: 10;
        }

        .input-dock {
            width: 100%;
            max-width: 800px;
            background-color: #262626;
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 6px 12px;
            display: flex;
            align-items: flex-end;
            gap: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .input-dock:focus-within {
            border-color: rgba(16, 185, 129, 0.4);
            box-shadow: 0 10px 30px rgba(16, 185, 129, 0.05);
        }

        .input-dock textarea {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: white;
            font-family: var(--font-main);
            font-size: 15px;
            resize: none;
            max-height: 200px;
            min-height: 24px;
            padding: 8px 0;
            line-height: 1.5;
        }

        .input-dock textarea::placeholder {
            color: rgba(255, 255, 255, 0.3);
        }

        .send-btn {
            background-color: var(--accent);
            color: black;
            border: none;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.2s, background-color 0.2s;
            margin-bottom: 4px;
            flex-shrink: 0;
        }

        .send-btn:hover {
            background-color: var(--accent-glow);
            transform: scale(1.05);
        }

        .send-btn svg {
            width: 16px;
            height: 16px;
            fill: none;
            stroke: currentColor;
            stroke-width: 2.5;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        /* --- Collapsible CSS 3D Robot Mascot (Bottom-Right) --- */
        #mascot-widget {
            position: fixed;
            bottom: 24px;
            right: 24px;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 12px;
            z-index: 1000;
            pointer-events: none;
            display: none; /* Hidden by default */
        }

        #mascot-model {
            width: 80px;
            height: 80px;
            animation: float 3s ease-in-out infinite alternate;
            filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.5));
            pointer-events: auto;
            cursor: pointer;
        }

        @keyframes float {
            from { transform: translateY(0); }
            to { transform: translateY(-8px); }
        }

        .mascot-bubble {
            background: #262626;
            border: 1px solid var(--border-color);
            border-radius: 12px 12px 0 12px;
            padding: 8px 12px;
            font-size: 11.5px;
            color: var(--text-main);
            max-width: 200px;
            opacity: 0;
            transition: opacity 0.3s;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .mascot-bubble.show {
            opacity: 1;
        }
    </style>
</head>
<body>

    <!-- Left Sidebar Panel -->
    <div class="sidebar">
        <div class="sidebar-header">
            <h2>Nexus.AI</h2>
            <button id="new-chat-btn" class="sidebar-btn">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                New chat
            </button>
        </div>
        <div class="sidebar-sessions" id="sidebar-sessions">
            <!-- Active sessions list -->
        </div>
        <div class="sidebar-footer">
            <div class="settings-item">
                <label>Chaos Mode</label>
                <label class="switch">
                    <input type="checkbox" id="chaos-toggle">
                    <span class="slider"></span>
                </label>
            </div>
            <div class="settings-item">
                <label>Show Mascot</label>
                <label class="switch">
                    <input type="checkbox" id="mascot-toggle">
                    <span class="slider"></span>
                </label>
            </div>
            <div class="settings-item">
                <label>Forced Tool</label>
                <select id="tool-select" class="settings-select">
                    <option value="">None (Auto)</option>
                    <option value="wiki_search">Wikipedia</option>
                    <option value="arxiv_search">ArXiv</option>
                    <option value="github_search">GitHub</option>
                </select>
            </div>
        </div>
    </div>

    <!-- Main Chat Workspace -->
    <div class="main-panel">
        
        <!-- Navigation Top Bar -->
        <div class="top-nav">
            <div class="model-pill">
                <div class="model-pulse-dot"></div>
                <select id="model-select" style="background:transparent; border:none; color:white; font-size:12px; font-weight:500; outline:none; cursor:pointer; font-family:inherit;">
                    <option value="gemini-3.6-flash" style="background:#222; color:white;">Gemini 3.6 Flash</option>
                    <option value="groq/llama-3.3-70b-versatile" style="background:#222; color:white;">Llama 3.3 70B (Groq)</option>
                    <option value="groq/llama-3.1-8b-instant" style="background:#222; color:white;">Llama 3.1 8B (Groq)</option>
                    <option value="huggingface/mistralai/Mixtral-8x7B-Instruct-v0.1" style="background:#222; color:white;">Mixtral 8x7B (HF Free)</option>
                    <option value="huggingface/meta-llama/Meta-Llama-3-8B-Instruct" style="background:#222; color:white;">Llama 3 8B (HF Free)</option>
                </select>
            </div>
            
            <div class="memory-core" id="memory-core">
                <div class="memory-pulse"></div>
                <span id="memory-text">MEMORY RETRIEVED</span>
            </div>
        </div>
        
        <!-- Message list space -->
        <div class="chat-area" id="chat-area">
            <div class="chat-wrapper" id="chat-wrapper">
                
                <!-- Welcome View -->
                <div class="welcome-panel" id="welcome-panel">
                    <h1>Nexus.AI</h1>
                    <p>Your self-healing, multi-agent assistant for coding, research, and analysis.</p>
                    
                    <div class="suggestion-grid">
                        <div class="suggestion-card" onclick="triggerSuggestion('Find autonomous vehicle news')">
                            <strong>Research vehicles</strong>
                            <span>Search Wikipedia for autonomous driving updates</span>
                        </div>
                        <div class="suggestion-card" onclick="triggerSuggestion('Explain topological qubits')">
                            <strong>Explain quantum</strong>
                            <span>Get definitions and physics parameters</span>
                        </div>
                        <div class="suggestion-card" onclick="triggerSuggestion('Write a quick Python script to compress files')">
                            <strong>Write code</strong>
                            <span>Draft a script to handle rolling compressions</span>
                        </div>
                        <div class="suggestion-card" onclick="triggerSuggestion('AI healthcare startup landscape')">
                            <strong>BioTech analysis</strong>
                            <span>Get reports on AlphaFold and medical approvals</span>
                        </div>
                    </div>
                </div>
                
            </div>
        </div>
        
        <!-- Sticky Bottom Input Dock -->
        <div class="input-panel">
            <div class="input-dock">
                <textarea id="prompt" placeholder="Message Nexus..." rows="1" onkeydown="handleKeyPress(event)"></textarea>
                <button class="send-btn" onclick="sendMessage()" id="send-btn">
                    <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </button>
            </div>
        </div>
        
    </div>

    <!-- 3D Mascot Widget -->
    <div id="mascot-widget">
        <div class="mascot-bubble" id="mascot-bubble">Awaiting your command, Commander.</div>
        <model-viewer id="mascot-model" 
                      src="https://modelviewer.dev/shared-assets/models/RobotExpressive.glb" 
                      ar 
                      alt="Robot Mascot" 
                      auto-rotate 
                      camera-controls 
                      interaction-prompt="none"
                      animation-name="Wave" 
                      autoplay></model-viewer>
    </div>

    <script>
        let SESSION_ID = "";
        let isChaosMode = false;
        let currentForcedTool = "";
        let isGenerating = false;

        // Auto-growing textarea
        const tx = document.getElementById('prompt');
        tx.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight - 16) + 'px';
        });

        // Chaos Mode toggle
        document.getElementById('chaos-toggle').addEventListener('change', function() {
            isChaosMode = this.checked;
        });

        // Mascot toggle
        const mascotWidget = document.getElementById('mascot-widget');
        const mascotBubble = document.getElementById('mascot-bubble');
        const mascotModel = document.getElementById('mascot-model');
        
        document.getElementById('mascot-toggle').addEventListener('change', function() {
            if(this.checked) {
                mascotWidget.style.display = 'flex';
                speakMascot("Hello! Ready to assist.", 4000);
            } else {
                mascotWidget.style.display = 'none';
            }
        });

        function speakMascot(msg, duration) {
            mascotBubble.innerText = msg;
            mascotBubble.classList.add('show');
            
            if (mascotModel) {
                const anims = ["Jump", "Wave", "ThumbsUp", "Walk"];
                const randAnim = anims[Math.floor(Math.random() * anims.length)];
                mascotModel.setAttribute('animation-name', randAnim);
            }

            setTimeout(() => {
                mascotBubble.classList.remove('show');
                if(mascotModel) mascotModel.setAttribute('animation-name', 'Idle');
            }, duration);
        }

        // Forced Tool Select
        document.getElementById('tool-select').addEventListener('change', function() {
            currentForcedTool = this.value;
        });

        // Initialize session on load
        window.addEventListener('DOMContentLoaded', async () => {
            const savedSession = localStorage.getItem('nexus_session_id');
            if (savedSession) {
                SESSION_ID = savedSession;
                await selectSession(SESSION_ID);
            } else {
                await startNewSession();
            }
            await loadSessions();
        });

        // Load all active sessions
        async function loadSessions() {
            try {
                const res = await fetch('/sessions');
                const sessions = await res.json();
                const container = document.getElementById('sidebar-sessions');
                container.innerHTML = '';
                
                sessions.forEach(sess => {
                    const activeClass = sess.session_id === SESSION_ID ? 'active' : '';
                    const div = document.createElement('div');
                    div.className = `session-item ${activeClass}`;
                    div.onclick = () => selectSession(sess.session_id);
                    
                    div.innerHTML = `
                        <div class="session-title">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                            ${sess.title}
                        </div>
                        <button class="session-delete" onclick="event.stopPropagation(); deleteSession('${sess.session_id}')">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                        </button>
                    `;
                    container.appendChild(div);
                });
            } catch (e) {
                console.error("Error loading sessions:", e);
            }
        }

        // Create New Session
        document.getElementById('new-chat-btn').onclick = startNewSession;

        async function startNewSession() {
            try {
                const res = await fetch('/sessions', { method: 'POST' });
                const data = await res.json();
                SESSION_ID = data.session_id;
                localStorage.setItem('nexus_session_id', SESSION_ID);
                
                clearChat();
                await loadSessions();
            } catch (e) {
                console.error("Error starting session:", e);
            }
        }

        // Select a Session & Load History
        async function selectSession(sessionId) {
            SESSION_ID = sessionId;
            localStorage.setItem('nexus_session_id', SESSION_ID);
            
            try {
                const res = await fetch(`/sessions/${sessionId}`);
                const data = await res.json();
                
                clearChat();
                
                if (data.history && data.history.length > 0) {
                    document.getElementById('welcome-panel').style.display = 'none';
                    const wrapper = document.getElementById('chat-wrapper');
                    
                    data.history.forEach(entry => {
                        // User message
                        const userRow = document.createElement('div');
                        userRow.className = 'message-row user';
                        userRow.innerHTML = `<div class="bubble-content">${entry.task}</div>`;
                        wrapper.appendChild(userRow);
                        
                        // Agent message
                        const agentRow = document.createElement('div');
                        agentRow.className = 'message-row agent';
                        agentRow.innerHTML = `
                            <div class="avatar agent-avatar">N</div>
                            <div class="bubble-content markdown-body">${marked.parse(entry.answer)}</div>
                        `;
                        wrapper.appendChild(agentRow);
                        addCodeCopyButtons(agentRow);
                    });
                }
                
                await loadSessions();
            } catch (e) {
                console.error("Error loading session history:", e);
            }
        }

        // Delete a session
        async function deleteSession(sessionId) {
            try {
                await fetch(`/sessions/${sessionId}`, { method: 'DELETE' });
                if (sessionId === SESSION_ID) {
                    await startNewSession();
                } else {
                    await loadSessions();
                }
            } catch (e) {
                console.error("Error deleting session:", e);
            }
        }

        function clearChat() {
            const wrapper = document.getElementById('chat-wrapper');
            wrapper.innerHTML = `
                <div class="welcome-panel" id="welcome-panel">
                    <h1>Nexus.AI</h1>
                    <p>Your self-healing, multi-agent assistant for coding, research, and analysis.</p>
                    <div class="suggestion-grid">
                        <div class="suggestion-card" onclick="triggerSuggestion('Find autonomous vehicle news')">
                            <strong>Research vehicles</strong>
                            <span>Search Wikipedia for autonomous driving updates</span>
                        </div>
                        <div class="suggestion-card" onclick="triggerSuggestion('Explain topological qubits')">
                            <strong>Explain quantum</strong>
                            <span>Get definitions and physics parameters</span>
                        </div>
                        <div class="suggestion-card" onclick="triggerSuggestion('Write a quick Python script to compress files')">
                            <strong>Write code</strong>
                            <span>Draft a script to handle rolling compressions</span>
                        </div>
                        <div class="suggestion-card" onclick="triggerSuggestion('AI healthcare startup landscape')">
                            <strong>BioTech analysis</strong>
                            <span>Get reports on AlphaFold and medical approvals</span>
                        </div>
                    </div>
                </div>
            `;
        }

        function triggerSuggestion(text) {
            document.getElementById('prompt').value = text;
            sendMessage();
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        }

        // Stream and Send Logic
        async function sendMessage() {
            if (isGenerating) return;
            
            const promptArea = document.getElementById('prompt');
            const text = promptArea.value.trim();
            if (!text) return;
            
            promptArea.value = '';
            promptArea.style.height = 'auto';
            
            const welcome = document.getElementById('welcome-panel');
            if (welcome) welcome.style.display = 'none';
            
            isGenerating = true;
            
            const wrapper = document.getElementById('chat-wrapper');
            const userRow = document.createElement('div');
            userRow.className = 'message-row user';
            userRow.innerHTML = `<div class="bubble-content">${text}</div>`;
            wrapper.appendChild(userRow);
            
            const agentRow = document.createElement('div');
            agentRow.className = 'message-row agent';
            
            const agentAvatar = document.createElement('div');
            agentAvatar.className = 'avatar agent-avatar';
            agentAvatar.innerText = 'N';
            
            const agentContent = document.createElement('div');
            agentContent.className = 'bubble-content';
            
            // Accordion thought panel
            const thoughtAccordion = document.createElement('details');
            thoughtAccordion.className = 'thought-accordion';
            thoughtAccordion.setAttribute('open', '');
            
            const thoughtSummary = document.createElement('summary');
            thoughtSummary.innerText = 'Thinking Process';
            
            const thoughtContent = document.createElement('div');
            thoughtContent.className = 'reasoning-content';
            
            thoughtAccordion.appendChild(thoughtSummary);
            thoughtAccordion.appendChild(thoughtContent);
            
            const finalAnswerBox = document.createElement('div');
            finalAnswerBox.className = 'markdown-body';
            
            agentContent.appendChild(thoughtAccordion);
            agentContent.appendChild(finalAnswerBox);
            
            agentRow.appendChild(agentAvatar);
            agentRow.appendChild(agentContent);
            
            wrapper.appendChild(agentRow);
            scrollToBottom();
            
            if(document.getElementById('mascot-toggle').checked) {
                speakMascot("Thinking and referencing databases...", 4000);
            }

            try {
                const selectedModel = document.getElementById('model-select').value;
                let url = '/stream?task=' + encodeURIComponent(text) + '&session_id=' + SESSION_ID + '&model=' + encodeURIComponent(selectedModel);
                if (currentForcedTool) url += '&force_tool=' + encodeURIComponent(currentForcedTool);
                if (isChaosMode) url += '&chaos_mode=true';
                
                const response = await fetch(url);
                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                let logText = "";
                let isThoughtOpen = true;
                
                let buffer = "";
                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\\n');
                    buffer = lines.pop(); // keep last incomplete line
                    
                    for (const line of lines) {
                        const trimmed = line.trim();
                        if (trimmed.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(trimmed.substring(6));
                                if (data.type === 'log') {
                                    logText += data.text + "\\n";
                                    thoughtContent.innerText = logText;
                                    thoughtContent.scrollTop = thoughtContent.scrollHeight;
                                    scrollToBottom();
                                } else if (data.type === 'memory') {
                                    const memCore = document.getElementById('memory-core');
                                    const memText = document.getElementById('memory-text');
                                    memCore.classList.add('active');
                                    memText.innerText = "ACTIVE: " + data.text.toUpperCase();
                                    setTimeout(() => { memCore.classList.remove('active'); }, 5000);
                                } else if (data.type === 'answer') {
                                    if (isThoughtOpen) {
                                        thoughtAccordion.removeAttribute('open');
                                        isThoughtOpen = false;
                                    }
                                    finalAnswerBox.innerHTML = marked.parse(data.text);
                                    addCodeCopyButtons(finalAnswerBox);
                                    scrollToBottom();
                                }
                            } catch (parseError) {
                                console.warn("Failed to parse JSON line:", trimmed, parseError);
                            }
                        }
                    }
                }
                
                if(document.getElementById('mascot-toggle').checked) {
                    speakMascot("Completed! Strategic report generated.", 3000);
                }
            } catch (e) {
                thoughtContent.innerText += "\\n[CRITICAL FAILURE] Interface connection interrupted: " + e;
            } finally {
                isGenerating = false;
                await loadSessions();
            }
        }

        function scrollToBottom() {
            const chatArea = document.getElementById('chat-area');
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        function addCodeCopyButtons(container) {
            const blocks = container.querySelectorAll('pre');
            blocks.forEach(block => {
                if (block.querySelector('.copy-btn')) return;
                
                const btn = document.createElement('button');
                btn.className = 'copy-btn';
                btn.innerText = 'Copy';
                btn.onclick = () => {
                    const code = block.querySelector('code').innerText;
                    navigator.clipboard.writeText(code).then(() => {
                        btn.innerText = 'Copied!';
                        setTimeout(() => { btn.innerText = 'Copy'; }, 2000);
                    });
                };
                block.appendChild(btn);
            });
        }
    </script>
</body>
</html>\n"""

@app.get("/")
async def get_frontend():
    """Serves the HTML frontend"""
    return HTMLResponse(html_content)

@app.get("/stream")
async def stream_agent(task: str, session_id: str, model: str = "gemini-3.6-flash", force_tool: str = None, chaos_mode: bool = False):
    """Executes the agent and streams the thought process back to the frontend live"""
    agent = MultiAgentTeam(model_name=model)
    
    async def event_generator():
        # Iterate over the agent's live updates
        for update_type, text in agent.run_stream(task, session_id, max_turns=5, force_tool=force_tool, chaos_mode=chaos_mode):
            # Format as Server-Sent Events (SSE)
            data = json.dumps({"type": update_type, "text": text})
            yield f"data: {data}\n\n"
            # Small async sleep to yield control to the event loop
            await asyncio.sleep(0.01)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

import os
import uuid
from fastapi import Path

@app.get("/sessions")
async def get_sessions():
    """Retrieves all active session IDs and their parsed titles for the sidebar list"""
    filepath = "agent_memory.json"
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            db = json.load(f)
            sessions = []
            for session_id, data in db.items():
                title = "New Session"
                if data.get("history"):
                    first_task = data["history"][0]["task"]
                    title = first_task[:25] + "..." if len(first_task) > 25 else first_task
                elif data.get("summary"):
                    title = data["summary"][:25] + "..."
                sessions.append({"session_id": session_id, "title": title})
            return sessions
    except Exception:
        return []

@app.post("/sessions")
async def create_session():
    """Creates a new unique session and returns the ID"""
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    filepath = "agent_memory.json"
    db = {}
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                db = json.load(f)
        except Exception:
            pass
    db[session_id] = {"history": [], "summary": ""}
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4)
    except Exception:
        pass
    return {"session_id": session_id}

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str = Path(..., description="The session ID to delete")):
    """Deletes a specific session from memory database"""
    filepath = "agent_memory.json"
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                db = json.load(f)
            if session_id in db:
                del db[session_id]
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=4)
                return {"status": "deleted"}
        except Exception:
            pass
    return {"status": "not_found"}

@app.get("/sessions/{session_id}")
async def get_session_history(session_id: str = Path(..., description="The session ID to fetch")):
    """Retrieves the complete history of a specific session"""
    filepath = "agent_memory.json"
    if not os.path.exists(filepath):
        return {"history": [], "summary": ""}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            db = json.load(f)
        return db.get(session_id, {"history": [], "summary": ""})
    except Exception:
        return {"history": [], "summary": ""}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting FastAPI Server on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
