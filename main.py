import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
import json
import asyncio
from agent import ReActAgent

app = FastAPI()

# This is our custom HTML/CSS/JS frontend!


html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nexus | Autonomous AI</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"></script>
    <style>
        :root {
            --bg-dark: #000905;
            --bg-light: #021a10;
            --glass-green: rgba(16, 185, 129, 0.08);
            --glass-green-hover: rgba(16, 185, 129, 0.2);
            --border-green: rgba(52, 211, 153, 0.3);
            --text-main: #f0fdf4;
            --accent: #10b981;
            --accent-glow: #34d399;
        }
        
        body { 
            font-family: 'Space Grotesk', sans-serif;
            background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-light) 100%);
            color: var(--text-main); margin: 0; padding: 0; 
            height: 100vh; overflow: hidden; display: flex; flex-direction: column;
        }

        /* Interactive Canvas Background */
        #particle-canvas {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            z-index: 0; pointer-events: none; opacity: 0.7;
        }

        /* Ambient Volumetric Orbs */
        .ambient-orb { position: fixed; border-radius: 50%; filter: blur(120px); opacity: 0.5; z-index: 0; animation: floatOrb 12s ease-in-out infinite alternate; pointer-events: none; }
        .orb-1 { width: 500px; height: 500px; background: rgba(16, 185, 129, 0.25); top: -150px; left: -100px; }
        .orb-2 { width: 600px; height: 600px; background: rgba(2, 132, 199, 0.15); bottom: -200px; right: -100px; animation-delay: -5s; }
        @keyframes floatOrb { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(60px, 60px) scale(1.2); } }

        /* Glassmorphism Navbar */
        .navbar { display: flex; align-items: center; padding: 20px 40px; background: rgba(0,9,5,0.6); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-green); flex-shrink: 0; z-index: 10; box-shadow: 0 4px 30px rgba(16,185,129,0.1); }
        .navbar h1 { font-size: 26px; font-weight: 700; margin: 0; color: #fff; letter-spacing: 4px; text-transform: uppercase; text-shadow: 0 0 20px var(--accent-glow); }
        .navbar h1 span { color: var(--accent); }
        .navbar .badge { margin-left: 15px; background: rgba(16,185,129,0.1); color: var(--accent-glow); font-size: 10px; padding: 6px 12px; border-radius: 4px; border: 1px solid var(--accent); text-transform: uppercase; font-weight: 700; letter-spacing: 2px; animation: pulseGlow 2s infinite; }
        
        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 8px rgba(16,185,129,0.2), inset 0 0 8px rgba(16,185,129,0.2); }
            50% { box-shadow: 0 0 20px rgba(16,185,129,0.6), inset 0 0 15px rgba(16,185,129,0.4); }
        }

        .chat-container { flex: 1; width: 100%; overflow-y: auto; scroll-behavior: smooth; display: flex; flex-direction: column; align-items: center; padding: 40px 0; z-index: 1; position: relative;}
        .chat-container::-webkit-scrollbar { width: 6px; }
        .chat-container::-webkit-scrollbar-track { background: transparent; }
        .chat-container::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 10px; box-shadow: 0 0 10px var(--accent); }

        .message-wrapper { width: 100%; max-width: 1100px; display: flex; gap: 20px; margin-bottom: 40px; animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; transform: translateY(40px) scale(0.98); padding: 0 20px; box-sizing: border-box; }
        .message-wrapper.user { flex-direction: row-reverse; }
        
        .avatar { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; font-weight: 700; background: rgba(0,0,0,0.5); border: 1px solid var(--border-green); box-shadow: 0 0 20px rgba(16,185,129,0.2); backdrop-filter: blur(10px); position: relative; overflow: hidden; z-index: 2;}
        .user .avatar { color: #fff; border-color: rgba(56, 189, 248, 0.4); box-shadow: 0 0 20px rgba(56, 189, 248, 0.2); background: rgba(2, 132, 199, 0.1);}
        .user .avatar::after { content: ''; position: absolute; inset: 0; box-shadow: inset 0 0 10px rgba(56, 189, 248, 0.5); pointer-events: none;}
        .agent .avatar { color: var(--accent-glow); border-color: var(--accent); box-shadow: 0 0 25px rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.1);}
        .agent .avatar::after { content: ''; position: absolute; inset: 0; box-shadow: inset 0 0 12px rgba(16, 185, 129, 0.6); pointer-events: none;}

        .bubble { flex: 1; max-width: 95%; padding: 26px 34px; border-radius: 16px; font-size: 16px; line-height: 1.8; font-weight: 400; background: rgba(2, 26, 16, 0.6); backdrop-filter: blur(16px); border: 1px solid var(--border-green); box-shadow: 0 15px 35px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1); }
        .user .bubble { border-radius: 20px 4px 20px 20px; margin-left: auto; background: rgba(2, 132, 199, 0.08); border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 15px 35px rgba(0,0,0,0.3);}
        .agent .bubble { border-radius: 4px 20px 20px 20px; border: 1px solid rgba(16, 185, 129, 0.4); border-left: 4px solid var(--accent); background: linear-gradient(135deg, rgba(2, 26, 16, 0.9) 0%, rgba(16, 185, 129, 0.1) 100%); box-shadow: 0 15px 40px rgba(0,0,0,0.6), 0 0 20px rgba(16,185,129,0.15), inset 0 0 40px rgba(16,185,129,0.05); }

        /* Hacker/Terminal Reasoning Panel */
        .reasoning-panel { margin-bottom: 28px; border: 1px solid rgba(16,185,129,0.4); border-radius: 8px; background-color: rgba(0,5,2,0.9); overflow: hidden; box-shadow: inset 0 0 40px rgba(0,0,0,0.9), 0 0 20px rgba(16,185,129,0.15); backdrop-filter: blur(5px); position: relative; }
        .reasoning-panel::before { content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(16,185,129,0.04) 2px, rgba(16,185,129,0.04) 4px); pointer-events: none; z-index: 1;}
        .reasoning-panel::after { content: ''; position: absolute; top: -100%; left: 0; right: 0; height: 100%; background: linear-gradient(to bottom, transparent, rgba(16,185,129,0.15) 90%, transparent); animation: matrixScan 4s linear infinite; pointer-events: none; z-index: 2;}
        .reasoning-header { padding: 10px 18px; font-size: 11px; color: var(--accent-glow); background: rgba(16,185,129,0.15); display: flex; align-items: center; gap: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 3px; border-bottom: 1px solid rgba(16,185,129,0.3); position: relative; z-index: 3;}
        .spinner { width: 14px; height: 14px; border: 2px solid transparent; border-top-color: var(--accent-glow); border-right-color: var(--accent-glow); border-radius: 50%; animation: spin 0.6s linear infinite; margin-left: auto; }
        .reasoning-content { padding: 20px; font-family: 'Courier New', monospace; font-size: 14px; color: #6ee7b7; max-height: 280px; overflow-y: auto; white-space: pre-wrap; line-height: 1.6; text-shadow: 0 0 10px rgba(16,185,129,0.5); position: relative; z-index: 3;}
        .reasoning-content::-webkit-scrollbar { width: 6px; }
        .reasoning-content::-webkit-scrollbar-track { background: transparent; }
        .reasoning-content::-webkit-scrollbar-thumb { background: rgba(16,185,129,0.6); border-radius: 4px; }
        
        /* Ultra Sleek Input Area */
        .input-container { flex-shrink: 0; width: 100%; display: flex; justify-content: center; padding: 30px 20px; background: linear-gradient(0deg, rgba(0,9,5,0.9) 0%, rgba(0,9,5,0) 100%); z-index: 10; position: relative;}
        .input-box { width: 100%; max-width: 1100px; display: flex; align-items: center; background: rgba(2, 26, 16, 0.8); border: 1px solid var(--border-green); border-radius: 16px; padding: 8px 8px 8px 16px; transition: all 0.3s; box-shadow: 0 10px 40px rgba(0,0,0,0.5), inset 0 0 20px rgba(16,185,129,0.05); backdrop-filter: blur(20px); position: relative; overflow: visible;}
        .input-box::before { content: ''; position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px; background: linear-gradient(45deg, var(--accent), transparent, var(--accent-glow), transparent); z-index: -1; border-radius: 18px; filter: blur(10px); opacity: 0.2; animation: rotateBorder 4s linear infinite; }
        .input-box:focus-within::before { opacity: 0.6; }
        .input-box:focus-within { border-color: var(--accent-glow); box-shadow: 0 0 30px rgba(16,185,129,0.2), inset 0 0 20px rgba(16,185,129,0.1); transform: translateY(-2px);}
        
        #tools-btn { background: rgba(16,185,129,0.1); border: 1px solid var(--border-green); color: var(--accent-glow); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.3s; margin-right: 12px; flex-shrink: 0; }
        #tools-btn:hover { background: var(--accent); color: #000; box-shadow: 0 0 15px var(--accent-glow); transform: rotate(90deg) scale(1.05); }
        #tools-btn svg { stroke: currentColor; stroke-width: 2.5; stroke-linecap: round; }
        
        #tools-menu { position: absolute; bottom: 75px; left: 0; background: rgba(2, 26, 16, 0.95); border: 1px solid var(--accent); border-radius: 16px; padding: 16px; box-shadow: 0 15px 40px rgba(0,0,0,0.8), 0 0 30px rgba(16,185,129,0.2); backdrop-filter: blur(25px); transform: translateY(10px) scale(0.95); opacity: 0; pointer-events: none; transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); display: flex; flex-direction: column; gap: 10px; z-index: 100; min-width: 220px; transform-origin: bottom left; }
        #tools-menu.show { transform: translateY(0) scale(1); opacity: 1; pointer-events: auto; }
        .tools-menu-header { font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: var(--accent); font-weight: 700; margin-bottom: 4px; border-bottom: 1px solid rgba(16,185,129,0.2); padding-bottom: 8px; }
        .tool-item { display: flex; align-items: center; gap: 14px; padding: 10px; border-radius: 10px; background: rgba(255,255,255,0.03); border: 1px solid transparent; transition: all 0.2s; cursor: pointer; }
        .tool-item span { font-size: 22px; filter: drop-shadow(0 0 5px rgba(255,255,255,0.2)); }
        .tool-item strong { color: var(--text-main); font-size: 14px; display: block; letter-spacing: 0.5px; }
        .tool-item small { color: var(--accent-glow); font-size: 11px; }
        .tool-item:hover { background: rgba(16,185,129,0.1); border-color: var(--border-green); transform: translateX(5px); }
        .tool-item.active-tool { background: rgba(16,185,129,0.2); border-color: var(--accent-glow); box-shadow: 0 0 15px rgba(16,185,129,0.3); }

        .input-box input { flex: 1; background: transparent; border: none; color: white; font-size: 16px; font-weight: 400; outline: none; font-family: 'Space Grotesk', sans-serif; padding: 14px 0; letter-spacing: 0.5px;}
        .input-box input::placeholder { color: rgba(236,253,245,0.3); }
        .input-box button.send-btn { background: var(--accent); color: #000; border: none; width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; margin-left: 10px; flex-shrink: 0; box-shadow: 0 0 20px rgba(16,185,129,0.4);}
        .input-box button.send-btn:hover { transform: scale(1.05); box-shadow: 0 0 30px rgba(52,211,153,0.8); background: #fff;}
        .input-box button.send-btn svg { width: 22px; height: 22px; fill: none; stroke: currentColor; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; margin-left: -2px; }
        
        /* Markdown */
        .markdown-body h1, .markdown-body h2, .markdown-body h3 { margin-top: 0; color: #fff; font-weight: 700; letter-spacing: -0.5px; }
        .markdown-body h1 { font-size: 2rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px; margin-bottom: 24px; color: var(--accent-glow); text-shadow: 0 0 15px rgba(16,185,129,0.3);}
        .markdown-body p, .markdown-body li { color: #d1fae5; font-size: 16px; font-weight: 300; line-height: 1.8; letter-spacing: 0.3px;}
        .markdown-body ul { padding-left: 20px; margin-bottom: 24px; }
        .markdown-body strong { color: #fff; font-weight: 600; text-shadow: 0 0 10px rgba(255,255,255,0.3);}
        
        /* Animations */
        @keyframes slideUp { to { opacity: 1; transform: translateY(0) scale(1); } }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes matrixScan { 0% { top: -100%; } 100% { top: 100%; } }
        @keyframes rotateBorder { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        
        /* Holographic Welcome Screen */
        .welcome { text-align: center; margin: auto; padding-top: 5vh; max-width: 1000px; z-index: 2; position: relative; }
        
        .hologram-text {
            font-size: 4vw; font-weight: 700; margin: 0; text-transform: uppercase; letter-spacing: 6px; 
            color: #fff; text-shadow: 0 0 10px var(--accent), 0 0 20px var(--accent), 0 0 40px var(--accent-glow);
            animation: hologramFlicker 4s infinite;
        }

        @keyframes hologramFlicker {
            0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% { opacity: 1; text-shadow: 0 0 10px var(--accent), 0 0 20px var(--accent), 0 0 40px var(--accent-glow); }
            20%, 24%, 55% { opacity: 0.5; text-shadow: none; }
        }

        .welcome p { font-size: 16px; color: rgba(167,243,208,0.7); margin-top: 20px; font-weight: 300; letter-spacing: 2px;}
        .cursor { display: inline-block; width: 8px; height: 1em; background: var(--accent-glow); animation: blink 1s step-end infinite; vertical-align: bottom; margin-left: 8px; box-shadow: 0 0 10px var(--accent-glow);}
        @keyframes blink { 50% { opacity: 0; } }
        
        /* Cyberpunk Suggestion Chips */
        .suggestions { display: flex; gap: 16px; justify-content: center; margin-top: 60px; flex-wrap: wrap; opacity: 0; transition: opacity 1s ease-in; }
        .chip { background: rgba(0,0,0,0.6); border: 1px solid rgba(16,185,129,0.3); color: var(--text-main); padding: 14px 28px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.3s; backdrop-filter: blur(10px); box-shadow: 0 4px 15px rgba(0,0,0,0.4), inset 0 0 10px rgba(16,185,129,0.05); text-transform: uppercase; letter-spacing: 2px; position: relative; overflow: hidden;}
        .chip::before { content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%; background: linear-gradient(90deg, transparent, rgba(16,185,129,0.4), transparent); transform: skewX(-20deg); transition: 0.5s; }
        .chip:hover { border-color: var(--accent-glow); box-shadow: 0 4px 20px rgba(16,185,129,0.3), inset 0 0 15px rgba(16,185,129,0.2); transform: translateY(-3px);}
        .chip:hover::before { left: 150%; }
        .chip:hover { background: rgba(16,185,129,0.1); border-color: var(--accent-glow); transform: translateY(-4px); box-shadow: 0 10px 30px rgba(16,185,129,0.2); color: #fff; }

        /* --- ROAMING REAL 3D ROBOT CSS --- */
        #side-robot {
            position: fixed;
            top: 50%; left: 50%; transform: translate(-50%, -50%);
            display: flex; align-items: center; gap: 20px;
            z-index: 9999; pointer-events: none; 
            transition: all 1.8s cubic-bezier(0.25, 1, 0.5, 1);
        }
        
        #robot-img {
            width: 160px; height: 160px;
            animation: floatRobot 4s ease-in-out infinite;
            filter: drop-shadow(0 20px 30px rgba(0,0,0,0.8)) drop-shadow(0 0 20px rgba(16,185,129,0.4));
            background-color: transparent;
            pointer-events: auto; /* allow user to interact with the 3D model */
        }

        @keyframes floatRobot {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }

        .robot-bubble {
            background: rgba(2, 26, 16, 0.85); backdrop-filter: blur(20px);
            color: var(--text-main); padding: 16px 24px; border-radius: 12px 12px 12px 0;
            font-weight: 600; font-size: 13px; max-width: 250px;
            border: 1px solid var(--accent);
            box-shadow: 0 20px 40px rgba(0,0,0,0.6), inset 0 0 15px rgba(16,185,129,0.2);
            opacity: 0; transform: scale(0.8) translateX(-20px);
            transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            letter-spacing: 1px; line-height: 1.5;
        }
        .robot-bubble.active {
            opacity: 1; transform: scale(1) translateX(0);
        }
    </style>
</head>
<body>
    <!-- Ambient Volumetric Background Orbs -->
    <div class="ambient-orb orb-1"></div>
    <div class="ambient-orb orb-2"></div>

    <!-- Interactive Particle Network -->
    <canvas id="particle-canvas"></canvas>

    <div class="navbar">
        <h1>NEXUS<span>.AI</span></h1>
        <span class="badge">System Online</span>
    </div>
    
    <div class="chat-container" id="chat">
        <div class="welcome" id="welcome-msg">
            <h1 class="hologram-text" id="typed-text">NEXUS.AI</h1>
            <p id="subtitle-text"><span class="cursor"></span></p>
            
            <div class="suggestions" id="suggestions">
                <div class="chip" onclick="setPrompt('Analyze AI healthcare startups')">Healthcare Sector</div>
                <div class="chip" onclick="setPrompt('Research OpenAI patents')">OpenAI Patents</div>
                <div class="chip" onclick="setPrompt('Find autonomous vehicle news')">Auto Vehicles</div>
            </div>
        </div>
    </div>
    
    <div class="input-container">
        <div class="input-box">
            <button id="tools-btn" title="View Connected APIs" onclick="toggleToolsMenu(event)">
                <svg viewBox="0 0 24 24" width="20" height="20"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            </button>
            
            <div id="tools-menu">
                <div class="tools-menu-header">Force API Mode (Click to select)</div>
                <div class="tool-item active-tool" id="tool-auto" onclick="setForcedTool(null, this)">
                    <span>⚡</span>
                    <div>
                        <strong>Auto Mode</strong>
                        <small>AI chooses dynamically</small>
                    </div>
                </div>
                <div class="tool-item" onclick="setForcedTool('wiki_search', this)">
                    <span>🌐</span>
                    <div>
                        <strong>Wikipedia API</strong>
                        <small>Only use Wikipedia</small>
                    </div>
                </div>
                <div class="tool-item" onclick="setForcedTool('arxiv_search', this)">
                    <span>📚</span>
                    <div>
                        <strong>ArXiv Database</strong>
                        <small>Only search ArXiv</small>
                    </div>
                </div>
                <div class="tool-item" onclick="setForcedTool('github_search', this)">
                    <span>💻</span>
                    <div>
                        <strong>GitHub REST API</strong>
                        <small>Only search GitHub</small>
                    </div>
                </div>
            </div>

            <input type="text" id="prompt" placeholder="Initialize query sequence..." autocomplete="off" onkeypress="handleKeyPress(event)">
            <button class="send-btn" onclick="sendMessage()">
                <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
        </div>
    </div>

    <!-- The Roaming 3D AI Core -->
    <div id="side-robot">
        <model-viewer id="robot-img" 
            src="https://modelviewer.dev/shared-assets/models/RobotExpressive.glb" 
            autoplay 
            auto-rotate
            rotation-per-second="10deg"
            camera-orbit="auto auto auto"
            disable-zoom
            shadow-intensity="1">
        </model-viewer>
        <div class="robot-bubble" id="robot-bubble">Initializing...</div>
    </div>

    <script>
        // --- Tools Menu Logic ---
        let currentForcedTool = null;

        function setForcedTool(toolName, element) {
            currentForcedTool = toolName;
            
            // Remove active class from all
            document.querySelectorAll('.tool-item').forEach(el => el.classList.remove('active-tool'));
            // Add active class to clicked
            if (element) {
                element.classList.add('active-tool');
            }
            
            // Give user feedback via robot
            if (toolName) {
                updateRobotMsg("Override Accepted. Forcing " + toolName, 3000);
            } else {
                updateRobotMsg("Auto Mode Engaged.", 3000);
            }
            
            // Close menu
            document.getElementById('tools-menu').classList.remove('show');
        }

        function toggleToolsMenu(e) {
            e.stopPropagation();
            document.getElementById('tools-menu').classList.toggle('show');
        }
        
        document.addEventListener('click', (e) => {
            const btn = document.getElementById('tools-btn');
            const menu = document.getElementById('tools-menu');
            if (menu && btn) {
                if (menu.classList.contains('show') && !btn.contains(e.target) && !menu.contains(e.target)) {
                    menu.classList.remove('show');
                }
            }
        });

        // --- Interactive Particle Network Background ---
        const canvas = document.getElementById('particle-canvas');
        const ctx = canvas.getContext('2d');
        let width, height;
        let particles = [];

        function initParticles() {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
            particles = [];
            for (let i = 0; i < 80; i++) {
                particles.push({
                    x: Math.random() * width, y: Math.random() * height,
                    vx: (Math.random() - 0.5) * 1.0, vy: (Math.random() - 0.5) * 1.0,
                    size: Math.random() * 2 + 1
                });
            }
        }

        function drawParticles() {
            ctx.clearRect(0, 0, width, height);
            for (let i = 0; i < particles.length; i++) {
                let p = particles[i];
                p.x += p.vx; p.y += p.vy;
                if (p.x < 0 || p.x > width) p.vx *= -1;
                if (p.y < 0 || p.y > height) p.vy *= -1;
                
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(16, 185, 129, 0.6)';
                ctx.fill();

                for (let j = i + 1; j < particles.length; j++) {
                    let p2 = particles[j];
                    let dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                    if (dist < 150) {
                        ctx.beginPath();
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.strokeStyle = `rgba(16, 185, 129, ${0.2 * (1 - dist/150)})`;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(drawParticles);
        }
        initParticles();
        drawParticles();
        window.addEventListener('resize', initParticles);


        // --- Welcome Screen Typewriter ---
        const greeting = "ESTABLISH NEURAL LINK TO COMMENCE RESEARCH PROTOCOL";
        let charIndex = 0;
        
        function typeWriter() {
            if (charIndex < greeting.length) {
                document.getElementById("subtitle-text").innerHTML = greeting.substring(0, charIndex + 1) + '<span class="cursor"></span>';
                charIndex++;
                setTimeout(typeWriter, 30);
            } else {
                document.getElementById("suggestions").style.opacity = "1";
            }
        }
        window.onload = () => { setTimeout(typeWriter, 500); };
        
        // --- Roaming Robot Logic ---
        const sideRobot = document.getElementById('side-robot');
        let robotState = 'idle'; 
        let robotTimeout;

        function updateRobotMsg(text, duration=4000) {
            const bubble = document.getElementById('robot-bubble');
            bubble.innerText = text;
            bubble.classList.add('active');
            
            clearTimeout(robotTimeout);
            robotTimeout = setTimeout(() => {
                bubble.classList.remove('active');
            }, duration);
        }

        setInterval(() => {
            if (robotState === 'idle') {
                const x = Math.max(100, Math.random() * (window.innerWidth - 300));
                const y = Math.max(100, Math.random() * (window.innerHeight - 200));
                sideRobot.style.left = x + 'px';
                sideRobot.style.top = y + 'px';
            }
        }, 6000); 

        setTimeout(() => {
            sideRobot.style.left = (window.innerWidth - 350) + 'px';
            sideRobot.style.top = (window.innerHeight - 150) + 'px';
            updateRobotMsg("Awaiting your command, Commander.", 5000);
        }, 1500);

        function moveRobotToInput() {
            robotState = 'busy';
            const inputBox = document.querySelector('.input-container');
            const rect = inputBox.getBoundingClientRect();
            sideRobot.style.left = Math.max(20, rect.right - 450) + 'px';
            sideRobot.style.top = (rect.top - 120) + 'px';
        }

        function moveRobotToThinking() {
            robotState = 'busy';
            const panels = document.querySelectorAll('.reasoning-panel');
            if(panels.length > 0) {
                const rect = panels[panels.length-1].getBoundingClientRect();
                sideRobot.style.left = Math.max(20, rect.left - 180) + 'px';
                sideRobot.style.top = Math.max(20, rect.top + 50) + 'px';
            }
        }

        document.getElementById('prompt').addEventListener('focus', () => {
            if (robotState === 'idle') {
                moveRobotToInput();
                updateRobotMsg("I am ready to process data.", 3000);
            }
        });
        document.getElementById('prompt').addEventListener('blur', () => {
            if (robotState === 'busy') robotState = 'idle';
        });

        // --- Chat Logic ---
        function setPrompt(text) {
            document.getElementById('prompt').value = text;
            sendMessage();
        }

        const chat = document.getElementById('chat');
        const promptInput = document.getElementById('prompt');
        const welcomeMsg = document.getElementById('welcome-msg');

        function handleKeyPress(e) { if (e.key === 'Enter') sendMessage(); }

        async function sendMessage() {
            const text = promptInput.value;
            if (!text) return;
            promptInput.value = '';
            
            if(welcomeMsg) welcomeMsg.style.display = 'none';

            robotState = 'busy';
            moveRobotToInput();
            updateRobotMsg("Transmitting query to neural net...", 3000);

            const userWrapper = document.createElement('div');
            userWrapper.className = 'message-wrapper user';
            userWrapper.innerHTML = `<div class="avatar">U</div><div class="bubble">${text}</div>`;
            chat.appendChild(userWrapper);

            const agentWrapper = document.createElement('div');
            agentWrapper.className = 'message-wrapper agent';
            
            const agentBubble = document.createElement('div');
            agentBubble.className = 'bubble';
            
            const reasoningPanel = document.createElement('div');
            reasoningPanel.className = 'reasoning-panel';
            reasoningPanel.innerHTML = `
                <div class="reasoning-header">
                    <span id="header-text-${Date.now()}">NEURAL REASONING ENGINE</span>
                    <div class="spinner" id="spinner-${Date.now()}"></div>
                </div>
                <div class="reasoning-content" id="content-${Date.now()}"></div>
            `;
            
            const finalAnswerBox = document.createElement('div');
            finalAnswerBox.className = 'markdown-body';
            finalAnswerBox.style.display = 'none';
            
            agentBubble.appendChild(reasoningPanel);
            agentBubble.appendChild(finalAnswerBox);
            
            agentWrapper.innerHTML = `<div class="avatar">N</div>`;
            agentWrapper.appendChild(agentBubble);
            
            chat.appendChild(agentWrapper);
            scrollToBottom();

            const contentBox = reasoningPanel.querySelector('.reasoning-content');
            const headerText = reasoningPanel.querySelector('.reasoning-header span');
            const spinner = reasoningPanel.querySelector('.spinner');

            setTimeout(moveRobotToThinking, 800);

            try {
                let url = '/stream?task=' + encodeURIComponent(text);
                if (currentForcedTool) url += '&force_tool=' + encodeURIComponent(currentForcedTool);
                const response = await fetch(url);
                const reader = response.body.getReader();
                const decoder = new TextDecoder('utf-8');
                let logText = "";
                
                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;
                    
                    const chunks = decoder.decode(value).split('\\n\\n');
                    for (const chunk of chunks) {
                        if (chunk.startsWith('data: ')) {
                            const data = JSON.parse(chunk.substring(6));
                            if (data.type === 'log') {
                                logText += data.text + "\\n";
                                contentBox.innerText = logText;
                                
                                if (data.text.includes('Executing Tool')) {
                                    headerText.innerText = "ACCESSING EXTERNAL MAINFRAME";
                                    updateRobotMsg("Running external tool search...", 4000);
                                    moveRobotToThinking();
                                } else if (data.text.includes('Thought')) {
                                    headerText.innerText = "SYNTHESIZING DATA";
                                    updateRobotMsg("Analyzing data streams...", 4000);
                                    moveRobotToThinking();
                                }
                                scrollToBottom();
                                
                            } else if (data.type === 'answer') {
                                spinner.style.display = 'none';
                                headerText.innerText = "SYNTHESIS COMPLETE";
                                
                                finalAnswerBox.style.display = 'block';
                                finalAnswerBox.innerHTML = marked.parse(data.text);
                                scrollToBottom();
                                updateRobotMsg("Task successfully completed!", 6000);
                                setTimeout(() => { robotState = 'idle'; }, 6000);
                            }
                        }
                    }
                }
            } catch (e) {
                contentBox.innerText += "\\nERROR: " + e;
                headerText.innerText = "CRITICAL SYSTEM FAILURE";
                spinner.style.display = 'none';
                updateRobotMsg("Critical Error in Neural Link!", 6000);
                robotState = 'idle';
            }
        }
        
        function scrollToBottom() {
            setTimeout(() => {
                chat.scrollTop = chat.scrollHeight;
                const contentBoxes = document.querySelectorAll('.reasoning-content');
                if (contentBoxes.length > 0) {
                    const lastBox = contentBoxes[contentBoxes.length - 1];
                    lastBox.scrollTop = lastBox.scrollHeight;
                }
            }, 10);
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get_frontend():
    """Serves the HTML frontend"""
    return HTMLResponse(html_content)

@app.get("/stream")
async def stream_agent(task: str, force_tool: str = None):
    """Executes the agent and streams the thought process back to the frontend live"""
    agent = ReActAgent()
    
    async def event_generator():
        # Iterate over the agent's live updates
        for update_type, text in agent.run_stream(task, max_turns=5, force_tool=force_tool):
            # Format as Server-Sent Events (SSE)
            data = json.dumps({"type": update_type, "text": text})
            yield f"data: {data}\n\n"
            # Small async sleep to yield control to the event loop
            await asyncio.sleep(0.01)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    print("🚀 Starting FastAPI Server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
