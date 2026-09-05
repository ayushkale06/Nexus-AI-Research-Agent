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
    <title>NEXUS.AI | Command Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
    <style>
        :root {
            --bg-base: #080a0c;
            --bg-panel: #0d1117;
            --bg-elevated: #111418;
            --border: rgba(255, 255, 255, 0.06);
            --border-highlight: rgba(0, 229, 160, 0.3);
            
            --text-main: #f0f6fc;
            --text-muted: #8b949e;
            
            --accent-primary: #00E5A0; /* Neon Emerald */
            --accent-secondary: #00C8FF; /* Electric Cyan */
            --accent-tertiary: #8B5CF6; /* Purple */
            --error: #f85149;
            
            --font-main: 'Plus Jakarta Sans', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            
            --glow-primary: 0 0 20px rgba(0, 229, 160, 0.15);
            --glow-active: 0 0 30px rgba(0, 229, 160, 0.3);
        }

        * { box-sizing: border-box; }

        body {
            font-family: var(--font-main);
            background-color: var(--bg-base);
            color: var(--text-main);
            margin: 0;
            padding: 0;
            display: flex;
            height: 100vh;
            overflow: hidden;
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(0, 229, 160, 0.03) 0%, transparent 50%),
                linear-gradient(rgba(255,255,255,0.01) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.01) 1px, transparent 1px);
            background-size: 100% 100%, 40px 40px, 40px 40px;
        }

        /* --- Scrollbars --- */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

        /* --- Layout --- */
        .sidebar-left {
            width: 280px;
            background: var(--bg-panel);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            z-index: 10;
        }

        .main-workspace {
            flex: 1;
            display: flex;
            flex-direction: column;
            position: relative;
        }

        .sidebar-right {
            width: 320px;
            background: var(--bg-panel);
            border-left: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            z-index: 10;
        }

        @media (max-width: 1100px) {
            .sidebar-right { display: none; }
        }
        @media (max-width: 768px) {
            .sidebar-left { display: none; }
        }

        /* --- Left Sidebar --- */
        .brand {
            padding: 24px;
            font-weight: 700;
            font-size: 20px;
            letter-spacing: 2px;
            background: linear-gradient(90deg, var(--text-main), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .new-mission-btn {
            margin: 0 24px 24px;
            background: rgba(0, 229, 160, 0.1);
            border: 1px solid var(--border-highlight);
            color: var(--accent-primary);
            padding: 12px;
            border-radius: 8px;
            font-family: var(--font-main);
            font-weight: 600;
            font-size: 13px;
            letter-spacing: 1px;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: var(--glow-primary);
        }
        .new-mission-btn:hover {
            background: rgba(0, 229, 160, 0.2);
            box-shadow: var(--glow-active);
            transform: translateY(-1px);
        }

        .nav-section {
            padding: 0 24px;
            margin-bottom: 24px;
        }
        .nav-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-muted);
            margin-bottom: 12px;
            font-weight: 600;
        }

        .session-item {
            padding: 10px 12px;
            margin: 4px 24px;
            border-radius: 6px;
            font-size: 13px;
            color: var(--text-muted);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.2s;
            border: 1px solid transparent;
        }
        .session-item:hover {
            background: rgba(255,255,255,0.03);
            color: var(--text-main);
        }
        .session-item.active {
            background: rgba(255,255,255,0.05);
            color: var(--accent-secondary);
            border-color: rgba(0, 200, 255, 0.2);
            font-weight: 500;
        }
        .session-delete {
            background: transparent;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            opacity: 0;
        }
        .session-item:hover .session-delete { opacity: 1; }
        .session-delete:hover { color: var(--error); }

        /* Settings footer */
        .sidebar-footer {
            margin-top: auto;
            padding: 24px;
            border-top: 1px solid var(--border);
            font-size: 12px;
        }
        .settings-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            color: var(--text-muted);
        }
        
        /* Toggles */
        .toggle-switch {
            position: relative;
            width: 32px;
            height: 18px;
        }
        .toggle-switch input { opacity: 0; width: 0; height: 0; }
        .toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: rgba(255,255,255,0.1);
            border-radius: 34px;
            transition: .3s;
        }
        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 12px;
            width: 12px;
            left: 3px;
            bottom: 3px;
            background-color: var(--text-muted);
            border-radius: 50%;
            transition: .3s;
        }
        input:checked + .toggle-slider {
            background-color: rgba(0, 229, 160, 0.2);
            border: 1px solid var(--accent-primary);
        }
        input:checked + .toggle-slider:before {
            transform: translateX(14px);
            background-color: var(--accent-primary);
        }

        .select-dark {
            background: var(--bg-elevated);
            color: var(--text-main);
            border: 1px solid var(--border);
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            outline: none;
        }

        /* --- Top Nav --- */
        .top-nav {
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 32px;
            border-bottom: 1px solid var(--border);
            background: rgba(8, 10, 12, 0.8);
            backdrop-filter: blur(10px);
            z-index: 20;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 11px;
            letter-spacing: 1px;
            text-transform: uppercase;
            font-weight: 600;
            color: var(--accent-primary);
        }
        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--accent-primary);
            box-shadow: 0 0 10px var(--accent-primary);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 0.5; box-shadow: 0 0 5px var(--accent-primary); }
            50% { opacity: 1; box-shadow: 0 0 15px var(--accent-primary); }
            100% { opacity: 0.5; box-shadow: 0 0 5px var(--accent-primary); }
        }

        /* --- Workspace / Chat --- */
        .chat-area {
            flex: 1;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 40px;
            scroll-behavior: smooth;
        }
        
        .chat-wrapper {
            width: 100%;
            max-width: 850px;
            padding: 0 32px;
            display: flex;
            flex-direction: column;
            gap: 32px;
        }

        /* Welcome Centerpiece */
        .welcome-panel {
            text-align: center;
            margin-top: 40px;
            animation: fadeUp 0.8s ease-out forwards;
        }
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .welcome-panel h1 {
            font-size: 42px;
            font-weight: 300;
            letter-spacing: 4px;
            margin-bottom: 12px;
        }
        .welcome-panel h1 span {
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .welcome-panel p {
            color: var(--text-muted);
            font-size: 16px;
            letter-spacing: 0.5px;
            margin-bottom: 48px;
        }

        /* Nexus Core Visualization */
        .nexus-core-vis {
            position: relative;
            width: 300px;
            height: 300px;
            margin: 0 auto 48px;
        }
        .core-center {
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 80px; height: 80px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(0,229,160,0.2) 0%, transparent 70%);
            border: 1px solid var(--accent-primary);
            box-shadow: var(--glow-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 5;
            animation: float 4s ease-in-out infinite;
        }
        .core-center::after {
            content: '';
            width: 40px; height: 40px;
            border-radius: 50%;
            background: var(--accent-primary);
            box-shadow: 0 0 30px var(--accent-primary);
        }
        @keyframes float {
            0% { transform: translate(-50%, -50%) translateY(0px); }
            50% { transform: translate(-50%, -50%) translateY(-10px); }
            100% { transform: translate(-50%, -50%) translateY(0px); }
        }
        
        .node {
            position: absolute;
            width: 40px; height: 40px;
            background: var(--bg-elevated);
            border: 1px solid var(--border);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: 700;
            color: var(--text-muted);
            z-index: 4;
            transition: all 0.3s;
        }
        .node.scout { top: 10%; left: 50%; transform: translateX(-50%); }
        .node.forge { top: 50%; right: 10%; transform: translateY(-50%); }
        .node.oracle { bottom: 10%; left: 50%; transform: translateX(-50%); }
        .node.sentinel { top: 50%; left: 10%; transform: translateY(-50%); }
        
        .connection-line {
            position: absolute;
            top: 50%; left: 50%;
            width: 120px; height: 1px;
            background: linear-gradient(90deg, var(--accent-primary) 0%, transparent 100%);
            transform-origin: 0 0;
            opacity: 0.3;
            z-index: 3;
        }
        .line-1 { transform: rotate(-90deg); }
        .line-2 { transform: rotate(0deg); }
        .line-3 { transform: rotate(90deg); }
        .line-4 { transform: rotate(180deg); }

        /* Mission Cards */
        .mission-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            max-width: 700px;
            margin: 0 auto;
        }
        .mission-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            text-align: left;
            cursor: pointer;
            transition: all 0.3s;
            backdrop-filter: blur(5px);
        }
        .mission-card:hover {
            background: rgba(255, 255, 255, 0.04);
            border-color: var(--border-highlight);
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .mission-card h3 {
            margin: 0 0 8px;
            font-size: 14px;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .mission-card p {
            margin: 0;
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.5;
        }

        /* --- Chat Messages --- */
        .message-row {
            display: flex;
            gap: 20px;
            width: 100%;
            animation: fadeUp 0.4s ease-out forwards;
        }
        .message-row.user {
            justify-content: flex-end;
        }
        
        .bubble-content {
            max-width: 85%;
            font-size: 15px;
            line-height: 1.7;
        }
        .user .bubble-content {
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            padding: 16px 24px;
            border-radius: 20px 20px 4px 20px;
            color: var(--text-main);
            backdrop-filter: blur(10px);
        }
        .agent .bubble-content {
            flex: 1;
            color: rgba(255,255,255,0.9);
        }

        .agent-avatar {
            width: 40px; height: 40px;
            border-radius: 10px;
            background: rgba(0, 229, 160, 0.1);
            border: 1px solid var(--border-highlight);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            color: var(--accent-primary);
            box-shadow: var(--glow-primary);
        }

        /* Console / Reasoning Accordion */
        .thought-accordion {
            background: #0d1117;
            border: 1px solid var(--border);
            border-left: 3px solid var(--accent-secondary);
            border-radius: 6px;
            margin: 16px 0;
            overflow: hidden;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
        }
        .thought-accordion summary {
            padding: 12px 16px;
            font-size: 11px;
            font-family: var(--font-mono);
            color: var(--accent-secondary);
            cursor: pointer;
            outline: none;
            display: flex;
            align-items: center;
            gap: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
            background: rgba(0,0,0,0.2);
        }
        .thought-accordion summary::-webkit-details-marker { display: none; }
        .thought-accordion summary::before {
            content: '>';
            transition: transform 0.2s;
        }
        .thought-accordion[open] summary::before { transform: rotate(90deg); }
        
        .reasoning-content {
            padding: 0 16px 16px 28px;
            font-family: var(--font-mono);
            font-size: 12px;
            color: var(--text-muted);
            white-space: pre-wrap;
            line-height: 1.6;
            max-height: 400px;
            overflow-y: auto;
        }

        /* Markdown blocks styling */
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {
            color: white;
            margin-top: 24px; margin-bottom: 12px;
        }
        .markdown-body p { margin-bottom: 16px; }
        .markdown-body ul, .markdown-body ol { padding-left: 20px; margin-bottom: 16px; }
        .markdown-body li { margin-bottom: 8px; }
        
        /* Code Blocks */
        pre {
            background: #0d1117 !important;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
            position: relative;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        code {
            font-family: var(--font-mono);
            font-size: 13.5px;
            color: #e3e3e3;
        }
        .copy-btn {
            position: absolute;
            top: 12px; right: 12px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            color: var(--text-muted);
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .copy-btn:hover { background: rgba(255,255,255,0.1); color: white; }

        
        .mic-btn {
            background: transparent;
            color: var(--text-muted);
            border: 1px solid var(--border);
            width: 40px; height: 40px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; transition: all 0.2s;
            margin-bottom: 2px;
        }
        .mic-btn:hover, .mic-btn.listening {
            color: var(--accent-primary);
            border-color: var(--accent-primary);
            box-shadow: var(--glow-primary);
        }
        .mic-btn svg { width: 18px; height: 18px; fill: currentColor; }
        
        .export-btn {
            margin-top: 16px;
            background: rgba(0, 200, 255, 0.1);
            border: 1px solid var(--accent-secondary);
            color: var(--accent-secondary);
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 12px; font-family: var(--font-mono);
            cursor: pointer; transition: all 0.2s;
            display: inline-flex; align-items: center; gap: 8px;
        }
        .export-btn:hover {
            background: rgba(0, 200, 255, 0.2);
            box-shadow: 0 0 15px rgba(0,200,255,0.3);
        }
/* --- Chat Input Dock --- */
        .input-panel {
            padding: 24px 32px 32px;
            background: linear-gradient(to top, var(--bg-base) 70%, transparent);
            display: flex;
            justify-content: center;
            z-index: 20;
        }
        .input-dock {
            width: 100%;
            max-width: 850px;
            background: rgba(17, 20, 24, 0.8);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 8px 12px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            transition: border-color 0.3s;
        }
        .input-dock:focus-within {
            border-color: var(--border-highlight);
            box-shadow: 0 20px 40px rgba(0, 229, 160, 0.1);
        }
        
        .input-top-bar {
            display: flex;
            align-items: center;
            padding: 4px 8px;
            font-size: 11px;
            color: var(--text-muted);
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            margin-bottom: 8px;
        }
        
        .input-row {
            display: flex;
            align-items: flex-end;
            gap: 12px;
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
            min-height: 44px;
            max-height: 250px;
            padding: 10px 8px;
            line-height: 1.5;
        }
        .input-dock textarea::placeholder { color: rgba(255,255,255,0.2); }

        .send-btn {
            background: var(--accent-primary);
            color: black;
            border: none;
            width: 40px; height: 40px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 2px;
        }
        .send-btn:hover {
            transform: translateY(-2px);
            box-shadow: var(--glow-primary);
            background: #00f0a8;
        }
        .send-btn svg { width: 18px; height: 18px; stroke: black; stroke-width: 2.5; fill: none; }

        /* --- Right Mission Control --- */
        .mc-header {
            padding: 24px;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-muted);
            font-weight: 600;
            border-bottom: 1px solid var(--border);
        }
        .mc-section {
            padding: 24px;
            border-bottom: 1px solid var(--border);
        }
        .mc-title {
            font-size: 12px;
            color: white;
            margin-bottom: 16px;
            font-weight: 600;
        }
        
        .agent-card {
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .agent-card.active {
            border-color: var(--border-highlight);
            background: rgba(0, 229, 160, 0.05);
        }
        .agent-icon {
            width: 32px; height: 32px;
            border-radius: 6px;
            background: rgba(255,255,255,0.05);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }
        .agent-info { flex: 1; }
        .agent-name {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 2px;
        }
        .agent-role {
            font-size: 11px;
            color: var(--text-muted);
        }
        .agent-status-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: #3e3e3e;
        }
        .agent-card.active .agent-status-dot {
            background: var(--accent-primary);
            box-shadow: 0 0 8px var(--accent-primary);
        }
        
        .system-health {
            margin-top: 16px;
        }
        .health-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 10px;
        }
        .health-status {
            color: var(--accent-primary);
        }

        /* --- Memory Alert --- */
        .memory-core {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(139, 92, 246, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.3);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            color: #d8b4fe;
            opacity: 0;
            transform: translateY(-5px);
            transition: all 0.3s;
        }
        .memory-core.active {
            opacity: 1; transform: translateY(0);
        }
        .memory-pulse {
            width: 6px; height: 6px;
            background: #a78bfa;
            border-radius: 50%;
            animation: pulse 1s infinite alternate;
        }

        /* 3D Mascot */
        #mascot-widget {
            position: fixed;
            bottom: 24px; left: 24px;
            display: none;
            flex-direction: column;
            align-items: flex-start;
            z-index: 1000;
        }
        #mascot-model {
            width: 100px; height: 100px;
            animation: float 3s ease-in-out infinite alternate;
            filter: drop-shadow(0 10px 20px rgba(0,0,0,0.8));
        }
        .mascot-bubble {
            background: var(--bg-elevated);
            border: 1px solid var(--accent-secondary);
            border-radius: 12px 12px 12px 0;
            padding: 10px 14px;
            font-size: 12px;
            color: white;
            box-shadow: 0 0 20px rgba(0, 200, 255, 0.2);
            margin-bottom: 12px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .mascot-bubble.show { opacity: 1; }

    
        /* Mission Feed */
        .mission-feed {
            position: fixed; bottom: 0; left: 0; width: 100%;
            background: #000; border-top: 1px solid var(--accent-primary);
            color: var(--accent-primary); font-family: var(--font-mono); font-size: 10px;
            padding: 4px 0; overflow: hidden; z-index: 100;
        }
        .feed-content {
            white-space: nowrap; animation: scrollFeed 30s linear infinite;
        }
        @keyframes scrollFeed { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }

        /* Hacker Terminal */
        #hacker-terminal {
            position: fixed; right: 340px; bottom: 40px;
            width: 350px; height: 250px;
            background: rgba(0, 20, 0, 0.9);
            border: 1px solid #0f0; border-radius: 4px;
            flex-direction: column; z-index: 90;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
            backdrop-filter: blur(5px);
        }
        .term-header {
            background: #0f0; color: #000;
            font-family: var(--font-mono); font-size: 10px; font-weight: bold;
            padding: 4px 8px; text-transform: uppercase;
        }
        .term-body {
            flex: 1; overflow-y: auto;
            color: #0f0; font-family: var(--font-mono); font-size: 10px;
            padding: 8px; white-space: pre-wrap; word-wrap: break-word;
        }

    </style>
</head>
<body>

    <!-- LEFT SIDEBAR -->
    <div class="sidebar-left">
        <div class="brand">NEXUS.AI</div>
        
        <button id="new-chat-btn" class="new-mission-btn">
            + New Mission
        </button>
        
        <div class="nav-section">
            <div class="nav-title">Mission Logs</div>
        </div>
        
        <div class="sidebar-sessions" id="sidebar-sessions" style="flex: 1; overflow-y: auto;">
            <!-- Active sessions list injected via JS -->
        </div>
        
        <div class="sidebar-footer">
            <div class="settings-row">
                <span>Chaos Mode</span>
                <label class="toggle-switch">
                    <input type="checkbox" id="chaos-toggle">
                    <span class="toggle-slider"></span>
                </label>
            </div>
            
            <div class="settings-row">
                <span>Hacker Terminal</span>
                <label class="toggle-switch">
                    <input type="checkbox" id="term-toggle">
                    <span class="toggle-slider"></span>
                </label>
            </div>
            <div class="settings-row">
                <span>Show Mascot</span>
                <label class="toggle-switch">
                    <input type="checkbox" id="mascot-toggle">
                    <span class="toggle-slider"></span>
                </label>
            </div>
            <div class="settings-row" style="flex-direction: column; align-items: flex-start; gap: 8px;">
                <span>Forced Tool Override</span>
                <select id="tool-select" class="select-dark" style="width: 100%;">
                    <option value="">None (Autonomous)</option>
                    <option value="wiki_search">Wikipedia</option>
                    <option value="arxiv_search">ArXiv</option>
                    <option value="github_search">GitHub</option>
                    <option value="web_scraper">Web Scraper (Live)</option>
                </select>
            </div>
            <div class="settings-row" style="flex-direction: column; align-items: flex-start; gap: 8px; margin-top: 12px;">
                <span>Neural Engine</span>
                <select id="model-select" class="select-dark" style="width: 100%;">
                    <option value="gemini-3.6-flash">Gemini 3.6 Flash</option>
                    <option value="groq/openai/gpt-oss-120b">GPT-OSS 120B (Groq)</option>
                    <option value="groq/groq/compound">Groq Compound (Groq)</option>
                    <option value="huggingface/mistralai/Mixtral-8x7B-Instruct-v0.1">Mixtral 8x7B (HF)</option>
                    <option value="huggingface/meta-llama/Meta-Llama-3-8B-Instruct">Llama 3 8B (HF)</option>
                </select>
            </div>
        </div>
    </div>

    <!-- MAIN WORKSPACE -->
    <div class="main-workspace">
        <div class="top-nav">
            <div class="status-indicator">
                <div class="status-dot"></div>
                SYSTEM ONLINE
            </div>
            <div class="memory-core" id="memory-core">
                <div class="memory-pulse"></div>
                <span id="memory-text">MEMORY RETRIEVED</span>
            </div>
        </div>
        
        <div class="chat-area" id="chat-area">
            <div class="chat-wrapper" id="chat-wrapper">
                
                <div class="welcome-panel" id="welcome-panel">
                    <div class="nexus-core-vis">
                        <div class="connection-line line-1"></div>
                        <div class="connection-line line-2"></div>
                        <div class="connection-line line-3"></div>
                        <div class="connection-line line-4"></div>
                        <div class="node scout">S</div>
                        <div class="node forge">F</div>
                        <div class="node oracle">O</div>
                        <div class="node sentinel">V</div>
                        <div class="core-center"></div>
                    </div>
                    
                    <h1><span>NEXUS</span>.AI</h1>
                    <p>Your Autonomous AI Workspace</p>
                    
                    <div class="mission-grid">
                        <div class="mission-card" onclick="triggerSuggestion('Investigate autonomous driving breakthroughs')">
                            <h3>🔍 Research Mission</h3>
                            <p>Investigate autonomous vehicle news</p>
                        </div>
                        <div class="mission-card" onclick="triggerSuggestion('Build a FastAPI AI application')">
                            <h3>⚒ Build Mission</h3>
                            <p>Write an API service architecture</p>
                        </div>
                        <div class="mission-card" onclick="triggerSuggestion('Explain topological qubits and quantum entanglement')">
                            <h3>🧠 Analysis Mission</h3>
                            <p>Analyze complex quantum concepts</p>
                        </div>
                        <div class="mission-card" onclick="triggerSuggestion('What is the current AI healthcare startup landscape?')">
                            <h3>📊 BioTech Survey</h3>
                            <p>Analyze market data and approvals</p>
                        </div>
                    </div>
                </div>
                
            </div>
        </div>
        
        <div class="input-panel">
            <div class="input-dock">
                <div class="input-top-bar">✦ Give Nexus a command</div>
                <div class="input-row">
                    <textarea id="prompt" placeholder="Type your command..." rows="1" onkeydown="handleKeyPress(event)"></textarea>
                    <button class="mic-btn" onclick="startDictation()" id="mic-btn" title="Voice Command">
                        <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                    </button>
                    <button class="send-btn" onclick="sendMessage()" id="send-btn">
                        <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- RIGHT MISSION CONTROL -->
    <div class="sidebar-right">
        <div class="mc-header">Mission Control</div>
        
        <div class="mc-section">
            <div class="mc-title">Agent Network</div>
            
            <div class="agent-card active" id="card-nexus">
                <div class="agent-icon" style="color: var(--accent-primary)">◉</div>
                <div class="agent-info">
                    <div class="agent-name">Nexus Core</div>
                    <div class="agent-role">Orchestrator</div>
                </div>
                <div class="agent-status-dot"></div>
            </div>
            
            <div class="agent-card" id="card-scout">
                <div class="agent-icon" style="color: var(--accent-secondary)">🔍</div>
                <div class="agent-info">
                    <div class="agent-name">Scout</div>
                    <div class="agent-role">Research</div>
                </div>
                <div class="agent-status-dot"></div>
            </div>
            
            <div class="agent-card" id="card-oracle">
                <div class="agent-icon" style="color: var(--text-main)">🧠</div>
                <div class="agent-info">
                    <div class="agent-name">Oracle</div>
                    <div class="agent-role">Analysis</div>
                </div>
                <div class="agent-status-dot"></div>
            </div>
            
            <div class="agent-card" id="card-sentinel">
                <div class="agent-icon" style="color: var(--accent-tertiary)">🛡</div>
                <div class="agent-info">
                    <div class="agent-name">Sentinel</div>
                    <div class="agent-role">Verification</div>
                </div>
                <div class="agent-status-dot"></div>
            </div>
        </div>
        
        <div class="mc-section" style="border:none;">
            <div class="mc-title">System Health</div>
            <div class="system-health">
                <div class="health-row">
                    <span>Memory Engine</span>
                    <span class="health-status">Online</span>
                </div>
                <div class="health-row">
                    <span>Tool Access</span>
                    <span class="health-status">Connected</span>
                </div>
                <div class="health-row">
                    <span>Self-Healing Protocol</span>
                    <span class="health-status">Active</span>
                </div>
                <div class="health-row">
                    <span>System Load</span>
                    <span id="system-load" style="color: var(--text-muted)">14%</span>
                </div>
            </div>
        </div>
    </div>

    
    <!-- HACKER TERMINAL -->
    <div id="hacker-terminal" style="display: none;">
        <div class="term-header">RAW PAYLOAD STREAM</div>
        <div class="term-body" id="term-body">Awaiting connection...</div>
    </div>

    <!-- MISSION FEED TICKER -->
    <div class="mission-feed">
        <div class="feed-content" id="feed-content">
            [LIVE] Agent Oracle compiling generative dataset in Tokyo... &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; 
            [LIVE] Scout navigating ArXiv repositories... &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; 
            [ALERT] Security Sentinel blocked unauthorized payload... &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
            [LIVE] Forge synthesizing React components... &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
            [LIVE] Global Network Status: OPTIMAL
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

        document.getElementById('term-toggle').addEventListener('change', function() {
            document.getElementById('hacker-terminal').style.display = this.checked ? 'flex' : 'none';
        });

        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playSound(type) {
            if(audioCtx.state === 'suspended') audioCtx.resume();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            if (type === 'click') {
                osc.type = 'square'; osc.frequency.setValueAtTime(800, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(400, audioCtx.currentTime + 0.1);
                gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.1);
                osc.start(); osc.stop(audioCtx.currentTime + 0.1);
            } else if (type === 'receive') {
                osc.type = 'sine'; osc.frequency.setValueAtTime(1500, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.02, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.1);
                osc.start(); osc.stop(audioCtx.currentTime + 0.1);
            }
        }
        
        document.addEventListener('click', (e) => {
            if (e.target.tagName === 'BUTTON' || e.target.closest('button')) playSound('click');
        });


        
        mermaid.initialize({ startOnLoad: false, theme: 'dark' });

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.onstart = () => document.getElementById('mic-btn').classList.add('listening');
            recognition.onend = () => document.getElementById('mic-btn').classList.remove('listening');
            recognition.onresult = (e) => {
                document.getElementById('prompt').value = e.results[0][0].transcript;
                sendMessage();
            };
        }
        function startDictation() {
            if(recognition) recognition.start();
            else alert("Voice recognition not supported in this browser.");
        }
        
        function downloadReport(text) {
            const blob = new Blob([text], {type: "text/markdown"});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "Nexus_Mission_Report.md";
            a.click();
            URL.revokeObjectURL(url);
        }

        // Auto-growing textarea

        const tx = document.getElementById('prompt');
        tx.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });

        // Toggles & Settings
        document.getElementById('chaos-toggle').addEventListener('change', function() { isChaosMode = this.checked; });
        document.getElementById('tool-select').addEventListener('change', function() { currentForcedTool = this.value; });
        
        // Mascot
        const mascotWidget = document.getElementById('mascot-widget');
        const mascotBubble = document.getElementById('mascot-bubble');
        const mascotModel = document.getElementById('mascot-model');
        
        document.getElementById('mascot-toggle').addEventListener('change', function() {
            if(this.checked) {
                mascotWidget.style.display = 'flex';
                speakMascot("Commander. System is online.", 4000);
            } else {
                mascotWidget.style.display = 'none';
            }
        });

        function speakMascot(msg, duration) {
            mascotBubble.innerText = msg;
            mascotBubble.classList.add('show');
            if (mascotModel) {
                const anims = ["Jump", "Wave", "ThumbsUp"];
                mascotModel.setAttribute('animation-name', anims[Math.floor(Math.random() * anims.length)]);
            }
            setTimeout(() => {
                mascotBubble.classList.remove('show');
                if(mascotModel) mascotModel.setAttribute('animation-name', 'Idle');
            }, duration);
        }

        // Initialize
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

        // Sessions Management
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
                        <div style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                            ${sess.title}
                        </div>
                        <button class="session-delete" onclick="event.stopPropagation(); deleteSession('${sess.session_id}')">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                        </button>
                    `;
                    container.appendChild(div);
                });
            } catch (e) { console.error("Error loading sessions", e); }
        }

        document.getElementById('new-chat-btn').onclick = startNewSession;

        async function startNewSession() {
            try {
                const res = await fetch('/sessions', { method: 'POST' });
                const data = await res.json();
                SESSION_ID = data.session_id;
                localStorage.setItem('nexus_session_id', SESSION_ID);
                clearChat();
                await loadSessions();
            } catch (e) { console.error("Error starting session", e); }
        }

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
                        const userRow = document.createElement('div');
                        userRow.className = 'message-row user';
                        userRow.innerHTML = `<div class="bubble-content">${entry.task}</div>`;
                        wrapper.appendChild(userRow);
                        
                        const agentRow = document.createElement('div');
                        agentRow.className = 'message-row agent';
                        agentRow.innerHTML = `
                            <div class="agent-avatar">◉</div>
                            <div class="bubble-content markdown-body">${marked.parse(entry.answer).replace(/<pre><code class="language-mermaid">([\s\S]*?)<\/code><\/pre>/g, '<div class="mermaid">$1</div>')}</div>
                        `;
                        wrapper.appendChild(agentRow);
                        addCodeCopyButtons(agentRow);
                    });
                }
                await loadSessions();
                scrollToBottom();
            } catch (e) { console.error("Error loading session history", e); }
        }

        async function deleteSession(sessionId) {
            try {
                await fetch(`/sessions/${sessionId}`, { method: 'DELETE' });
                if (sessionId === SESSION_ID) await startNewSession();
                else await loadSessions();
            } catch (e) { console.error("Error deleting session", e); }
        }

        function clearChat() {
            const wrapper = document.getElementById('chat-wrapper');
            wrapper.innerHTML = `
                <div class="welcome-panel" id="welcome-panel">
                    <div class="nexus-core-vis">
                        <div class="connection-line line-1"></div>
                        <div class="connection-line line-2"></div>
                        <div class="connection-line line-3"></div>
                        <div class="connection-line line-4"></div>
                        <div class="node scout">S</div>
                        <div class="node forge">F</div>
                        <div class="node oracle">O</div>
                        <div class="node sentinel">V</div>
                        <div class="core-center"></div>
                    </div>
                    <h1><span>NEXUS</span>.AI</h1>
                    <p>Your Autonomous AI Workspace</p>
                    <div class="mission-grid">
                        <div class="mission-card" onclick="triggerSuggestion('Investigate autonomous driving breakthroughs')">
                            <h3>🔍 Research Mission</h3><p>Investigate autonomous vehicle news</p>
                        </div>
                        <div class="mission-card" onclick="triggerSuggestion('Build a FastAPI AI application')">
                            <h3>⚒ Build Mission</h3><p>Write an API service architecture</p>
                        </div>
                        <div class="mission-card" onclick="triggerSuggestion('Explain topological qubits and quantum entanglement')">
                            <h3>🧠 Analysis Mission</h3><p>Analyze complex quantum concepts</p>
                        </div>
                        <div class="mission-card" onclick="triggerSuggestion('What is the current AI healthcare startup landscape?')">
                            <h3>📊 BioTech Survey</h3><p>Analyze market data and approvals</p>
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
        
        function scrollToBottom() {
            const chatArea = document.getElementById('chat-area');
            chatArea.scrollTo({ top: chatArea.scrollHeight, behavior: 'smooth' });
        }
        
        // Agent UI Activity Toggler
        function updateAgentActivity(logText) {
            document.querySelectorAll('.agent-card').forEach(c => c.classList.remove('active'));
            document.getElementById('card-nexus').classList.add('active'); // Always active
            
            const lowerLog = logText.toLowerCase();
            
            if (lowerLog.includes('scout') || lowerLog.includes('search') || lowerLog.includes('retrieving')) {
                document.getElementById('card-scout').classList.add('active');
                document.getElementById('system-load').innerText = "42%";
            }
            if (lowerLog.includes('critic') || lowerLog.includes('verify') || lowerLog.includes('check')) {
                document.getElementById('card-sentinel').classList.add('active');
                document.getElementById('system-load').innerText = "67%";
            }
            if (lowerLog.includes('lead') || lowerLog.includes('think') || lowerLog.includes('analyzing')) {
                document.getElementById('card-oracle').classList.add('active');
                document.getElementById('system-load').innerText = "89%";
            }
            
            // Self healing UI trigger
            if (lowerLog.includes('error') || lowerLog.includes('fail') || lowerLog.includes('retry') || lowerLog.includes('rotating') || lowerLog.includes('quota')) {
                const sysHealth = document.querySelectorAll('.health-status');
                sysHealth[2].innerText = "Recovering...";
                sysHealth[2].style.color = "orange";
                setTimeout(() => {
                    sysHealth[2].innerText = "Active";
                    sysHealth[2].style.color = "var(--accent-primary)";
                }, 3000);
            }
        }

        async function sendMessage() {
            if (isGenerating) return;
            
            const promptEl = document.getElementById('prompt');
            const text = promptEl.value.trim();
            if (!text) return;
            
            promptEl.value = '';
            promptEl.style.height = 'auto';
            isGenerating = true;
            document.getElementById('send-btn').style.opacity = '0.5';
            document.getElementById('welcome-panel').style.display = 'none';
            document.getElementById('system-load').innerText = "31%";
            
            const wrapper = document.getElementById('chat-wrapper');
            
            // Append User Message
            const userRow = document.createElement('div');
            userRow.className = 'message-row user';
            userRow.innerHTML = `<div class="bubble-content">${text}</div>`;
            wrapper.appendChild(userRow);
            
            // Append Agent Container
            const agentRow = document.createElement('div');
            agentRow.className = 'message-row agent';
            agentRow.innerHTML = `
                <div class="agent-avatar">◉</div>
                <div class="bubble-content">
                    <details class="thought-accordion" open>
                        <summary>SYSTEM CONSOLE</summary>
                        <div class="reasoning-content"></div>
                    </details>
                    <div class="markdown-body" style="display:none;"></div>
                </div>
            `;
            wrapper.appendChild(agentRow);
            scrollToBottom();
            
            const reasoningContainer = agentRow.querySelector('.reasoning-content');
            const markdownContainer = agentRow.querySelector('.markdown-body');
            const accordion = agentRow.querySelector('.thought-accordion');
            
            const modelEl = document.getElementById('model-select');
            const selectedModel = modelEl ? modelEl.value : "gemini-3.6-flash";
            
            const params = new URLSearchParams({
                task: text,
                session_id: SESSION_ID,
                model: selectedModel,
                chaos_mode: isChaosMode
            });
            if (currentForcedTool) params.append('force_tool', currentForcedTool);
            
            const evtSource = new EventSource(`/stream?${params.toString()}`);
            
            evtSource.onmessage = function(event) {
                const termBody = document.getElementById('term-body');
                if(termBody && event.data) {
                    termBody.innerText += "\\n> " + event.data;
                    termBody.scrollTop = termBody.scrollHeight;
                }
                playSound('receive');

                const data = JSON.parse(event.data);
                
                if (data.type === "log") {
                    reasoningContainer.textContent += data.text + "\\n";
                    updateAgentActivity(data.text);
                    scrollToBottom();
                } 
                else if (data.type === "memory") {
                    document.getElementById('memory-core').classList.add('active');
                    setTimeout(() => { document.getElementById('memory-core').classList.remove('active'); }, 4000);
                }
                else if (data.type === "answer") {
                    accordion.removeAttribute('open');
                    markdownContainer.style.display = 'block';
                    
                    let htmlContent = marked.parse(data.text);
                    htmlContent = htmlContent.replace(/<pre><code class="language-mermaid">([\s\S]*?)<\/code><\/pre>/g, '<div class="mermaid">$1</div>');
                    markdownContainer.innerHTML = htmlContent;
                    
                    const exportBtn = document.createElement('button');
                    exportBtn.className = 'export-btn';
                    exportBtn.innerHTML = '📥 Export Mission Report';
                    exportBtn.onclick = () => downloadReport(data.text);
                    markdownContainer.appendChild(exportBtn);
                    
                    addCodeCopyButtons(agentRow);
                    
                    setTimeout(() => {
                        try { mermaid.run({ querySelector: '.mermaid' }); } catch(e) { console.error(e); }
                        scrollToBottom();
                    }, 100);
                    
                    evtSource.close();
                    
                    isGenerating = false;
                    document.getElementById('send-btn').style.opacity = '1';
                    document.getElementById('system-load').innerText = "14%";
                    loadSessions();
                    
                    // Reset agents
                    setTimeout(() => {
                        document.querySelectorAll('.agent-card').forEach(c => c.classList.remove('active'));
                        document.getElementById('card-nexus').classList.add('active');
                    }, 2000);
                }
            };
            
            evtSource.onerror = function() {
                reasoningContainer.textContent += "\\n\\n[CONNECTION ERROR OR STREAM ENDED]\\n";
                evtSource.close();
                isGenerating = false;
                document.getElementById('send-btn').style.opacity = '1';
                document.getElementById('system-load').innerText = "14%";
            };
        }

        function addCodeCopyButtons(container) {
            container.querySelectorAll('pre').forEach(pre => {
                if (pre.querySelector('.copy-btn')) return;
                const btn = document.createElement('button');
                btn.className = 'copy-btn';
                btn.innerText = 'Copy';
                btn.onclick = () => {
                    const code = pre.querySelector('code').innerText;
                    navigator.clipboard.writeText(code);
                    btn.innerText = 'Copied!';
                    setTimeout(() => btn.innerText = 'Copy', 2000);
                };
                pre.appendChild(btn);
            });
        }
        
    // Welcome Voice Greeting
    let voicePlayed = false;
    function playWelcome() {
        if (voicePlayed) return;
        voicePlayed = true;
        let msg = new SpeechSynthesisUtterance("Commander. Welcome to Nexus AI Command Center.");
        msg.rate = 0.95;
        msg.pitch = 1.0;
        
        // Fix for Chrome garbage collection bug
        window.speechUtteranceChunk = msg;
        
        window.speechSynthesis.speak(msg);
    }
    
    // Autoplay is blocked by modern browsers, so we MUST play on first user interaction
    document.body.addEventListener('click', playWelcome, {once: true});
    document.body.addEventListener('keydown', playWelcome, {once: true});

    </script>
</body>
</html>\n"""

@app.get("/groq_models")
async def groq_models():
    import os
    import requests
    key = os.environ.get("GROQ_API_KEY")
    if not key:
        return {"error": "No GROQ_API_KEY"}
    res = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {key.strip()}"})
    return res.json()

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
