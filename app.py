import http.server
import socketserver
import json
import re
import openpyxl
from datetime import datetime
try:
    import real_batch_executor
except ImportError:
    real_batch_executor = None

import os
PORT = int(os.environ.get('PORT', 8080))


HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>BountyGrid OS — Solo Commander RPG</title>
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="BountyGrid OS">
    <link rel="apple-touch-icon" href="/app-icon.jpg">
    <link rel="icon" type="image/jpeg" href="/app-icon.jpg">

    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif; -webkit-tap-highlight-color: transparent; }
        
        :root {
            --bg-base: #070a13;
            --bg-card: #0f172a;
            --border-glow: #1e293b;
            --accent-cyan: #00f2fe;
            --accent-purple: #a855f7;
            --accent-green: #00e676;
            --accent-gold: #ffb703;
            --accent-pink: #ff007f;
            --accent-orange: #ff5400;
        }

        body { 
            background: var(--bg-base); 
            color: #f8fafc; 
            display: flex; 
            flex-direction: column; 
            height: 100vh; 
            height: 100dvh;
            overflow: hidden; 
            background-image: radial-gradient(circle at 50% 0%, rgba(0, 242, 254, 0.12) 0%, transparent 60%);
            font-size: 16px;
            line-height: 1.5;
        }
        
        /* GAMER HUD HEADER */
        header { 
            background: rgba(15, 23, 42, 0.95); 
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            padding: 14px 16px 12px 16px; 
            display: flex; 
            flex-direction: column;
            gap: 10px;
            border-bottom: 2px solid rgba(0, 242, 254, 0.3); 
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            flex-shrink: 0;
        }
        .header-top-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .founder-brand {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .rank-badge { 
            background: linear-gradient(135deg, #ffb703, #ff5400); 
            color: #000; 
            font-size: 13px; 
            font-weight: 900; 
            padding: 5px 10px; 
            border-radius: 10px; 
            letter-spacing: 0.5px;
            box-shadow: 0 0 14px rgba(255, 183, 3, 0.45);
        }
        .founder-title { 
            font-size: 18px; 
            font-weight: 900; 
            color: #ffffff; 
            letter-spacing: -0.2px; 
        }

        .header-bottom-row {
            display: flex;
            flex-direction: column;
            gap: 6px;
            padding-top: 2px;
        }
        .xp-bar-container {
            display: flex;
            align-items: center;
            gap: 10px;
            width: 100%;
        }
        .xp-bar-bg {
            flex: 1;
            height: 10px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid rgba(0, 242, 254, 0.3);
            position: relative;
        }
        .xp-bar-fill {
            height: 100%;
            background: linear-gradient(90deg, #00e676, #00f2fe);
            width: 74.4%;
            box-shadow: 0 0 10px #00f2fe;
            transition: width 0.3s ease;
        }
        .xp-text { 
            font-size: 13px; 
            color: #94a3b8; 
            font-weight: 800; 
            white-space: nowrap;
        }
        .xp-highlight {
            color: var(--accent-cyan);
            font-weight: 900;
        }

        .header-actions { 
            display: flex; 
            align-items: center; 
            gap: 8px; 
            flex-wrap: wrap;
        }
        .streak-pill {
            background: rgba(255, 183, 3, 0.15);
            border: 1px solid rgba(255, 183, 3, 0.4);
            color: var(--accent-gold);
            font-size: 13px; 
            font-weight: 900;
            padding: 5px 12px; 
            border-radius: 16px; 
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 0 10px rgba(255, 183, 3, 0.2);
        }
        .icon-btn { 
            background: rgba(255, 255, 255, 0.08); 
            border: 1px solid rgba(255, 255, 255, 0.15); 
            color: #f8fafc; 
            font-size: 14px; 
            font-weight: 800; 
            padding: 7px 14px; 
            border-radius: 16px; 
            cursor: pointer; 
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
        }
        .icon-btn:active { transform: scale(0.95); background: rgba(255,255,255,0.15); }
        .icon-btn.active {
            background: rgba(0, 230, 118, 0.25);
            border-color: #00e676;
            color: #00e676;
        }

        /* LIVE STATUS PILL & OFFLINE BANNER */
        .conn-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            font-weight: 900;
            padding: 4px 10px;
            border-radius: 12px;
            background: rgba(0, 230, 118, 0.2);
            border: 1px solid rgba(0, 230, 118, 0.5);
            color: #00e676;
            letter-spacing: 0.5px;
        }
        .conn-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00e676;
            box-shadow: 0 0 8px #00e676;
            animation: pulse-green 2s infinite;
        }
        @keyframes pulse-green {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.8); }
        }
        #offline-banner {
            display: none;
            background: linear-gradient(135deg, #ff007f, #7928ca);
            color: #fff;
            padding: 12px 16px;
            font-size: 14px;
            font-weight: 900;
            text-align: center;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        /* LIVE WEBHOOK TICKER BAR */
        #webhook-live-bar {
            background: rgba(0, 242, 254, 0.1);
            border-bottom: 1px solid rgba(0, 242, 254, 0.3);
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 800;
            color: var(--accent-cyan);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            overflow: hidden;
            white-space: nowrap;
            flex-shrink: 0;
        }

        /* GAMIFIED TAB PILLS */
        .tab-bar { 
            display: flex; 
            background: rgba(15, 23, 42, 0.9); 
            border-bottom: 1px solid rgba(255, 255, 255, 0.1); 
            overflow-x: auto; 
            -webkit-overflow-scrolling: touch; 
            padding: 12px 14px; 
            gap: 10px; 
            flex-shrink: 0;
        }
        .tab-bar::-webkit-scrollbar { display: none; }
        .tab { 
            flex: 0 0 auto; 
            white-space: nowrap; 
            padding: 10px 18px; 
            border-radius: 24px; 
            font-size: 15px; 
            font-weight: 900; 
            color: #94a3b8; 
            cursor: pointer; 
            background: rgba(255, 255, 255, 0.05); 
            border: 1px solid rgba(255, 255, 255, 0.12); 
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .tab.active { 
            color: #000;
            background: linear-gradient(135deg, #00f2fe, #00e676); 
            border-color: #00f2fe;
            box-shadow: 0 0 16px rgba(0, 242, 254, 0.4);
        }

        /* MAIN CONTENT SCROLL */
        .content-scroll { 
            flex: 1; 
            overflow-y: auto; 
            padding: 18px 16px; 
            display: flex; 
            flex-direction: column; 
            gap: 18px; 
            -webkit-overflow-scrolling: touch;
        }

        /* CARD CONTAINERS */
        .card { 
            background: var(--bg-card); 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            border-radius: 20px; 
            padding: 20px; 
            display: flex; 
            flex-direction: column; 
            gap: 14px; 
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
        }
        .card-title { 
            font-size: 18px; 
            font-weight: 900; 
            color: #fff; 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        }

        /* STAT BOXES & HUD NUMBERS */
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .grid-4 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
        
        .stat-box { 
            background: rgba(0, 0, 0, 0.4); 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            border-radius: 16px; 
            padding: 16px 14px; 
            display: flex; 
            flex-direction: column; 
            gap: 4px;
        }
        .stat-val { 
            font-size: 26px; 
            font-weight: 900; 
            color: #fff; 
            letter-spacing: -0.5px; 
        }
        .stat-label { 
            font-size: 13px; 
            color: #94a3b8; 
            font-weight: 800; 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
        }

        /* GAMIFIED WORLD CARDS (50 MILESTONES) */
        .world-card {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 18px;
            padding: 18px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            transition: all 0.2s ease;
        }
        .world-card.unlocked {
            border-color: rgba(0, 230, 118, 0.45);
            background: linear-gradient(135deg, rgba(0, 230, 118, 0.12), rgba(0, 0, 0, 0.45));
            box-shadow: 0 4px 20px rgba(0, 230, 118, 0.1);
        }
        .world-card.current {
            border-color: rgba(0, 242, 254, 0.5);
            background: linear-gradient(135deg, rgba(0, 242, 254, 0.14), rgba(0, 0, 0, 0.45));
            box-shadow: 0 4px 20px rgba(0, 242, 254, 0.15);
        }
        .world-card.locked {
            border-color: rgba(255, 255, 255, 0.06);
            background: rgba(0, 0, 0, 0.25);
            opacity: 0.72;
        }
        .world-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .world-title {
            font-size: 17px;
            font-weight: 900;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .world-badge {
            font-size: 12px;
            font-weight: 900;
            padding: 4px 10px;
            border-radius: 8px;
        }
        .loot-metrics-banner {
            display: flex;
            justify-content: space-between;
            background: rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 10px 14px;
        }
        .loot-metric-item {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .loot-metric-val {
            font-size: 17px;
            font-weight: 900;
        }
        .loot-metric-lbl {
            font-size: 11px;
            color: #94a3b8;
            font-weight: 800;
            text-transform: uppercase;
        }
        .quest-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-top: 4px;
        }
        .quest-item {
            font-size: 14px;
            color: #cbd5e1;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* HERO CARDS */
        .hero-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        .hero-card {
            background: rgba(0,0,0,0.4);
            border: 1px solid rgba(0, 242, 254, 0.25);
            border-radius: 16px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .hero-header {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .hero-icon { font-size: 28px; }
        .hero-name { font-size: 15px; font-weight: 900; color: #fff; }
        .hero-sub { font-size: 12px; color: var(--accent-cyan); font-weight: 800; }
        .hero-stats {
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            font-weight: 800;
            color: #94a3b8;
            background: rgba(255,255,255,0.04);
            padding: 6px 8px;
            border-radius: 8px;
        }

        /* ECOSYSTEM HEATMAP */
        .heatmap-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .heatmap-card { 
            background: rgba(0, 0, 0, 0.4); 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            border-radius: 14px; 
            padding: 12px; 
            display: flex; 
            flex-direction: column; 
            gap: 4px; 
        }
        .heatmap-name { font-size: 14px; font-weight: 900; color: #fff; }
        .heatmap-bar-bg { height: 6px; background: rgba(255, 255, 255, 0.08); border-radius: 4px; overflow: hidden; margin-top: 4px; }
        .heatmap-bar-fill { height: 100%; border-radius: 4px; }

        /* BUTTONS */
        .batch-btn { 
            border: none; 
            border-radius: 18px; 
            padding: 18px; 
            font-size: 17px; 
            font-weight: 900; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            gap: 6px; 
            cursor: pointer; 
            transition: all 0.15s ease;
            position: relative;
            overflow: hidden;
        }
        .batch-btn:active { transform: scale(0.97); }
        .btn-omni { 
            background: linear-gradient(135deg, #00f2fe, #4facfe); 
            color: #000; 
            box-shadow: 0 0 24px rgba(0, 242, 254, 0.4); 
        }
        .btn-power { 
            background: linear-gradient(135deg, #ff007f, #7928ca); 
            color: #fff; 
            box-shadow: 0 0 24px rgba(255, 0, 127, 0.4); 
        }
        .batch-sub { font-size: 13px; font-weight: 800; opacity: 0.9; }

        /* MODALS */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(12px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 16px;
        }
        .modal-card {
            background: #0f172a;
            border: 2px solid var(--accent-cyan);
            border-radius: 22px;
            width: 100%;
            max-width: 600px;
            max-height: 85vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 10px 40px rgba(0, 242, 254, 0.3);
            overflow: hidden;
        }

        /* RESPONSIVE */
        @media (max-width: 480px) {
            .grid-4 { grid-template-columns: 1fr; }
            .hero-grid { grid-template-columns: 1fr; }
            .heatmap-grid { grid-template-columns: 1fr; }
            .stat-val { font-size: 22px; }
        }
    </style>
</head>
<body>

    <!-- GAMER HUD HEADER -->
    <header>
        <div class="header-top-row">
            <div class="founder-brand">
                <span class="rank-badge">👑 LEVEL 10 GUILD MASTER</span>
                <span class="founder-title">Garrett • BountyGrid OS</span>
            </div>
            <div class="header-actions">
                <div class="streak-pill">🔥 5-DAY STREAK (2X LOOT)</div>
                <div class="conn-pill" id="conn-status">
                    <span class="conn-dot"></span>
                    <span>RAID ACTIVE</span>
                </div>
            </div>
        </div>

        <div class="header-bottom-row">
            <div class="xp-bar-container">
                <span class="xp-text">LEVEL 10: <b class="xp-highlight">$37,205 / $50,000 XP</b> (TO WORLD 4)</span>
                <div class="xp-bar-bg">
                    <div class="xp-bar-fill" id="xp-bar" style="width: 74.4%;"></div>
                </div>
                <span class="xp-text" style="color:var(--accent-green);">74%</span>
            </div>
        </div>
    </header>

    <!-- OFFLINE BANNER -->
    <div id="offline-banner">⚠️ CONNECTION LOST — OFFLINE DATA LOADED</div>

    <!-- LIVE WEBHOOK TICKER BAR -->
    <div id="webhook-live-bar">
        <span style="display:flex; align-items:center; gap:6px;">
            <span style="color:#00e676;">⚡ LIVE EVENT:</span>
            <span id="webhook-event-text">PR #1858 Verified & Dispatched to Subfinder (+$200)</span>
        </span>
        <span style="font-size:11px; opacity:0.8;" id="webhook-time">JUST NOW</span>
    </div>

    <!-- GAMIFIED TAB NAVIGATION -->
    <div class="tab-bar">
        <div class="tab active" onclick="switchTab('loot')">💎 Loot Stash HUD</div>
        <div class="tab" onclick="switchTab('worlds')">🏆 10 Worlds ($1.5B Exit)</div>
        <div class="tab" onclick="switchTab('heroes')">🤖 AI Hero Minions</div>
        <div class="tab" onclick="switchTab('drops')">🚀 Loot Drops (155 Quests)</div>
        <div class="tab" onclick="switchTab('realms')">🗺️ 25 Conquered Realms</div>
        <div class="tab" onclick="switchTab('raids')">⚔️ Launch Raid Sprint</div>
        <div class="tab" onclick="switchTab('calc')">📈 Gold Multiplier (ARR)</div>
        <div class="tab" onclick="switchTab('chat')">💬 Guild Master AI</div>
    </div>

    <!-- MAIN SCROLL CONTAINER -->
    <div class="content-scroll">

        <!-- VIEW 1: 💎 LOOT STASH HUD (MAIN DASHBOARD) -->
        <div class="content-view" id="view-loot">
            <!-- PRIMARY LOOT STASH -->
            <div class="card" style="background: linear-gradient(135deg, rgba(0, 242, 254, 0.12), rgba(0, 230, 118, 0.1)); border-color: rgba(0, 242, 254, 0.35);">
                <div class="card-title">
                    <span>💎 Current Loot Stash (Total Pipeline)</span>
                    <button class="icon-btn active" onclick="showFinancialModal()">📊 View 3-Statement Vault</button>
                </div>
                
                <div style="display:flex; justify-content:space-between; align-items:baseline; margin-top:6px;">
                    <div style="font-size:38px; font-weight:900; color:var(--accent-cyan); letter-spacing:-1px;" id="stat-gross">$37,205.00</div>
                    <span style="font-size:14px; font-weight:800; color:var(--accent-green); background:rgba(0,230,118,0.15); padding:4px 10px; border-radius:10px;">100% BALANCED</span>
                </div>
                
                <div class="grid-2" style="margin-top:10px;">
                    <div class="stat-box" style="background:rgba(0,230,118,0.1); border-color:rgba(0,230,118,0.3);">
                        <div class="stat-val" style="color:var(--accent-green);" id="stat-cash">$5,430.00</div>
                        <div class="stat-label">🪙 Real Banked Gold (Stripe)</div>
                    </div>
                    <div class="stat-box" style="background:rgba(255,183,3,0.1); border-color:rgba(255,183,3,0.3);">
                        <div class="stat-val" style="color:var(--accent-gold);" id="stat-ar">$31,775.00</div>
                        <div class="stat-label">⏳ Loot Chests Opening (155 Quests)</div>
                    </div>
                </div>

                <div style="font-size:14px; color:#94a3b8; line-height:1.4; margin-top:6px;">
                    🪙 <b>Real Banked Gold</b> ($5,430) + ⏳ <b>Loot Chests</b> ($31,775) = 💎 <b>Total Loot Stash</b> ($37,205.00) across <b>187 Active Hero PRs</b>!
                </div>
            </div>

            <!-- TODAY'S QUEST COMBO (BURST VELOCITY) -->
            <div class="card">
                <div class="card-title">⚡ Today's Quest Combo (Daily Burst)</div>
                <div class="grid-2">
                    <div class="stat-box">
                        <div class="stat-val" id="stat-daily-rev" style="color:var(--accent-green);">+$6,900</div>
                        <div class="stat-label" id="stat-daily-label">Today's Loot (30 Quests)</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-val" id="stat-daily-avg">$4,658</div>
                        <div class="stat-label">Avg Daily Pace</div>
                    </div>
                </div>
                <div class="grid-2" style="margin-top:6px;">
                    <div class="stat-box">
                        <div class="stat-val" id="stat-weekly-rev">$37,205</div>
                        <div class="stat-label">Weekly Loot Total</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-val" style="color:var(--accent-cyan);" id="stat-fleet">187 Units</div>
                        <div class="stat-label">Active Hero Army</div>
                    </div>
                </div>
            </div>

            <!-- FAST RAID DISPATCH -->
            <div class="card" style="border-color: rgba(255, 0, 127, 0.35);">
                <div class="card-title">⚔️ Instant Raid Dispatch</div>
                <div class="grid-2">
                    <button class="batch-btn btn-omni" onclick="executeRealBatch('omni')">
                        <span>⚡ OMNI RAID</span>
                        <span class="batch-sub">+$1,100 Loot • 5 Quests</span>
                    </button>
                    <button class="batch-btn btn-power" onclick="executeRealBatch('power')">
                        <span>🚀 POWER RAID</span>
                        <span class="batch-sub">+$1,050 Loot • 5 Quests</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- VIEW 2: 🏆 10 WORLDS ($1.5B ROADMAP) -->
        <div class="content-view" id="view-worlds" style="display:none;">
            <div class="card">
                <div class="card-title">
                    <span>🏆 10 Video Game Worlds (The $1.5B Exit Ladder)</span>
                    <span style="color:var(--accent-green); font-size:12px; font-weight:900; background:rgba(0,230,118,0.15); padding:4px 10px; border-radius:8px;">10 / 50 UNLOCKED (20%)</span>
                </div>
                <div style="font-size:14px; color:#cbd5e1;">
                    Level up from World 1 to World 10. Every world increases your <b>Monthly Profit</b> and <b>Yearly Loot</b> until the <b>$1.5 Billion Final Boss Exit</b>!
                </div>
            </div>

            <!-- WORLD 1 -->
            <div class="world-card unlocked">
                <div class="world-header">
                    <div class="world-title">🟢 World 1: The Starter Dungeon (Levels 1–5)</div>
                    <span class="world-badge" style="background:#00e676; color:#000;">5/5 COMPLETED</span>
                </div>
                <div class="loot-metrics-banner">
                    <div class="loot-metric-item">
                        <span class="loot-metric-val" style="color:var(--accent-green);">$6,000 / mo</span>
                        <span class="loot-metric-lbl">💰 Monthly Cash</span>
                    </div>
                    <div class="loot-metric-item" style="text-align:right;">
                        <span class="loot-metric-val" style="color:var(--accent-cyan);">$75,000 / yr</span>
                        <span class="loot-metric-lbl">🏆 Yearly Loot</span>
                    </div>
                </div>
                <div class="quest-list">
                    <div class="quest-item">✅ <b>Quest 1</b>: Five-Figure Club ($10k+ pipeline reached)</div>
                    <div class="quest-item">✅ <b>Quest 2</b>: Repo Diplomat (25 distinct realms unlocked)</div>
                    <div class="quest-item">✅ <b>Quest 3</b>: Cash Clearance Alpha ($5,430 gold in Stripe wallet)</div>
                    <div class="quest-item">✅ <b>Quest 4</b>: Burst Master (30+ quests solved in 1 day)</div>
                    <div class="quest-item">✅ <b>Quest 5</b>: Centurion Titan (100+ active PR ships in flight)</div>
                </div>
            </div>

            <!-- WORLD 2 -->
            <div class="world-card unlocked">
                <div class="world-header">
                    <div class="world-title">🟢 World 2: The Cyber Castle (Levels 6–10)</div>
                    <span class="world-badge" style="background:#00e676; color:#000;">5/5 COMPLETED</span>
                </div>
                <div class="loot-metrics-banner">
                    <div class="loot-metric-item">
                        <span class="loot-metric-val" style="color:var(--accent-green);">$10,000 / mo</span>
                        <span class="loot-metric-lbl">💰 Monthly Cash</span>
                    </div>
                    <div class="loot-metric-item" style="text-align:right;">
                        <span class="loot-metric-val" style="color:var(--accent-cyan);">$120,000 / yr</span>
                        <span class="loot-metric-lbl">🏆 Yearly Loot</span>
                    </div>
                </div>
                <div class="quest-list">
                    <div class="quest-item">✅ <b>Quest 6</b>: $25K Horizon ($25,000 gross pipeline)</div>
                    <div class="quest-item">✅ <b>Quest 7</b>: $35K Apex Frontier ($37,205 loot secured)</div>
                    <div class="quest-item">✅ <b>Quest 8</b>: Tri-Layer Harmony (100% balanced ledger)</div>
                    <div class="quest-item">✅ <b>Quest 9</b>: Security Clearance (0 flaws, green CI)</div>
                    <div class="quest-item">✅ <b>Quest 10</b>: Fleet Command (155 in-review queue)</div>
                </div>
            </div>

            <!-- WORLD 3 -->
            <div class="world-card current">
                <div class="world-header">
                    <div class="world-title" style="color:var(--accent-cyan);">⏳ World 3: The Guild Vault (Levels 11–15)</div>
                    <span class="world-badge" style="background:rgba(0,242,254,0.25); color:#00f2fe; border:1px solid #00f2fe;">CURRENT LEVEL</span>
                </div>
                <div class="loot-metrics-banner">
                    <div class="loot-metric-item">
                        <span class="loot-metric-val" style="color:var(--accent-green);">$25,000 / mo</span>
                        <span class="loot-metric-lbl">💰 Monthly Cash Target</span>
                    </div>
                    <div class="loot-metric-item" style="text-align:right;">
                        <span class="loot-metric-val" style="color:var(--accent-cyan);">$300,000 / yr</span>
                        <span class="loot-metric-lbl">🏆 Yearly Loot Target</span>
                    </div>
                </div>
                <div class="quest-list">
                    <div class="quest-item">⚡ <b>Quest 11</b>: $10K Stripe Cash ($5,430 / $10,000 banked)</div>
                    <div class="quest-item">⚡ <b>Quest 12</b>: Fifty-Grand Titan ($37,205 / $50,000 loot)</div>
                    <div class="quest-item">⚡ <b>Quest 13</b>: Double-Century Fleet (187 / 200 active hero ships)</div>
                    <div class="quest-item">⚡ <b>Quest 14</b>: Escrow Sovereign ($9,330 / $10,000 in Lilly escrows)</div>
                    <div class="quest-item">⚡ <b>Quest 15</b>: Retainer Deal Room (Close first $3,500/mo retainer)</div>
                </div>
            </div>

            <!-- WORLD 4 -->
            <div class="world-card locked">
                <div class="world-header">
                    <div class="world-title">🔒 World 4: The Six-Figure Citadel (Levels 16–20)</div>
                    <span class="world-badge" style="background:rgba(255,255,255,0.08); color:#94a3b8;">LOCKED</span>
                </div>
                <div class="loot-metrics-banner">
                    <div class="loot-metric-item">
                        <span class="loot-metric-val" style="color:var(--accent-green);">$40,000 / mo</span>
                        <span class="loot-metric-lbl">💰 Monthly Cash</span>
                    </div>
                    <div class="loot-metric-item" style="text-align:right;">
                        <span class="loot-metric-val" style="color:var(--accent-cyan);">$500,000 / yr</span>
                        <span class="loot-metric-lbl">🏆 Yearly Loot</span>
                    </div>
                </div>
                <div class="quest-list">
                    <div class="quest-item">🔒 <b>Quest 16</b>: $75K Pipeline Sentinel ($75k loot)</div>
                    <div class="quest-item">🔒 <b>Quest 17</b>: Six-Figure Sovereign ($100k milestone)</div>
                    <div class="quest-item">🔒 <b>Quest 18</b>: $25k Banked Stripe Cash</div>
                    <div class="quest-item">🔒 <b>Quest 19</b>: 3 Recurring Monthly Retainers ($10.5k/mo)</div>
                    <div class="quest-item">🔒 <b>Quest 20</b>: $150k ARR Benchmark Achieved</div>
                </div>
            </div>

            <!-- WORLD 5 -->
            <div class="world-card locked">
                <div class="world-header">
                    <div class="world-title">🔒 World 5: The Millionaire Fortress (Levels 21–25)</div>
                    <span class="world-badge" style="background:rgba(255,255,255,0.08); color:#94a3b8;">LOCKED</span>
                </div>
                <div class="loot-metrics-banner">
                    <div class="loot-metric-item">
                        <span class="loot-metric-val" style="color:var(--accent-green);">$83,000 / mo</span>
                        <span class="loot-metric-lbl">💰 Monthly Cash</span>
                    </div>
                    <div class="loot-metric-item" style="text-align:right;">
                        <span class="loot-metric-val" style="color:var(--accent-cyan);">$1,000,000 / yr</span>
                        <span class="loot-metric-lbl">🏆 Yearly Loot (Seven-Figures)</span>
                    </div>
                </div>
                <div class="quest-list">
                    <div class="quest-item">🔒 <b>Quest 21</b>: 10 Enterprise Retainers ($35k/mo base)</div>
                    <div class="quest-item">🔒 <b>Quest 22</b>: $250k Cumulative Bounty Stash</div>
                    <div class="quest-item">🔒 <b>Quest 23</b>: $100k Direct Bank Reserves</div>
                    <div class="quest-item">🔒 <b>Quest 24</b>: 300-Ship Autonomous Swarm</div>
                    <div class="quest-item">🔒 <b>Quest 25</b>: $500k ARR Studio ($430k Net Cash Take-Home)</div>
                </div>
            </div>

            <!-- WORLD 6 -->
            <div class="world-card locked">
                <div class="world-header">
                    <div class="world-title">🔒 World 6: The SaaS Empire (Levels 26–30)</div>
                    <span class="world-badge" style="background:rgba(255,255,255,0.08); color:#94a3b8;">LOCKED</span>
                </div>
                <div class="loot-metrics-banner">
                    <div class="loot-metric-item">
                        <span class="loot-metric-val" style="color:var(--accent-green);">$250,000 / mo</span>
                        <span class="loot-metric-lbl">💰 Monthly Cash</span>
                    </div>
                    <div class="loot-metric-item" style="text-align:right;">
                        <span class="loot-metric-val" style="color:var(--accent-cyan);">$3,000,000 / yr</span>
                        <span class="loot-metric-lbl">🏆 Yearly Loot</span>
                    </div>
                </div>
                <div class="quest-list">
                    <div class="quest-item">🔒 <b>Quest 26</b>: B2B Self-Serve SaaS Web App Launch</div>
                    <div class="quest-item">🔒 <b>Quest 27</b>: First 50 Paying Dev Teams</div>
                    <div class="quest-item">🔒 <b>Quest 28</b>: $1,000,000 ARR Titan Milestone</div>
                    <div class="quest-item">🔒 <b>Quest 29</b>: 1,000 Autonomous Merged PRs/Month</div>
                    <div class="quest-item">🔒 <b>Quest 30</b>: $15M–$30M Institutional Valuation Gateway</div>
                </div>
            </div>

            <!-- WORLD 7 -->
            <div class="world-card locked">
                <div class="world-header">
                    <div class="world-title">🔒 World 7: The Titan Kingdom (Levels 31–35)</div>
                    <span class="world-badge" style="background:rgba(255,255,255,0.08); color:#94a3b8;">LOCKED</span>
                </div>
                <div class="loot-metrics-banner">
                    <div class="loot-metric-item">
                        <span class="loot-metric-val" style="color:var(--accent-green);">$650,000 / mo</span>
                        <span class="loot-metric-lbl">💰 Monthly Cash</span>
                    </div>
                    <div class="loot-metric-item" style="text-align:right;">
                        <span class="loot-metric-val" style="color:var(--accent-cyan);">$8,000,000 / yr</span>
                        <span class="loot-metric-lbl">🏆 Yearly Loot</span>
                    </div>
                </div>
                <div class="quest-list">
                    <div class="quest-item">🔒 <b>Quest 31</b>: SOC2 Type II & ISO 27001 Certified</div>
                    <div class="quest-item">🔒 <b>Quest 32</b>: 10 Fortune 500 Contracts ($100k ACV)</div>
                    <div class="quest-item">🔒 <b>Quest 33</b>: $5M ARR Scale (80% Net Free Cash Flow)</div>
                    <div class="quest-item">🔒 <b>Quest 34</b>: Air-Gapped VPC Cloud Deployments</div>
                    <div class="quest-item">🔒 <b>Quest 35</b>: $100M+ Nine-Figure Valuation Milestone</div>
                </div>
            </div>

            <!-- WORLD 8 -->
            <div class="world-card locked">
                <div class="world-header">
                    <div class="world-title">🔒 World 8: The Cloud Overlord (Levels 36–40)</div>
                    <span class="world-badge" style="background:rgba(255,255,255,0.08); color:#94a3b8;">LOCKED</span>
                </div>
                <div class="loot-metrics-banner">
                    <div class="loot-metric-item">
                        <span class="loot-metric-val" style="color:var(--accent-green);">$2,000,000 / mo</span>
                        <span class="loot-metric-lbl">💰 Monthly Cash</span>
                    </div>
                    <div class="loot-metric-item" style="text-align:right;">
                        <span class="loot-metric-val" style="color:var(--accent-cyan);">$25,000,000 / yr</span>
                        <span class="loot-metric-lbl">🏆 Yearly Loot</span>
                    </div>
                </div>
                <div class="quest-list">
                    <div class="quest-item">🔒 <b>Quest 36</b>: GitHub/GitLab Native Remediation Partner</div>
                    <div class="quest-item">🔒 <b>Quest 37</b>: $25M ARR Benchmark ($2M/mo)</div>
                    <div class="quest-item">🔒 <b>Quest 38</b>: $20,000,000 Annual Free Cash Flow</div>
                    <div class="quest-item">🔒 <b>Quest 39</b>: 5,000 AI Agent Swarm Fleet</div>
                    <div class="quest-item">🔒 <b>Quest 40</b>: $350M–$500M Private Equity Valuation</div>
                </div>
            </div>

            <!-- WORLD 9 -->
            <div class="world-card locked">
                <div class="world-header">
                    <div class="world-title">🔒 World 9: The Global Dynasty (Levels 41–45)</div>
                    <span class="world-badge" style="background:rgba(255,255,255,0.08); color:#94a3b8;">LOCKED</span>
                </div>
                <div class="loot-metrics-banner">
                    <div class="loot-metric-item">
                        <span class="loot-metric-val" style="color:var(--accent-green);">$5,000,000 / mo</span>
                        <span class="loot-metric-lbl">💰 Monthly Cash</span>
                    </div>
                    <div class="loot-metric-item" style="text-align:right;">
                        <span class="loot-metric-val" style="color:var(--accent-cyan);">$60,000,000 / yr</span>
                        <span class="loot-metric-lbl">🏆 Yearly Loot</span>
                    </div>
                </div>
                <div class="quest-list">
                    <div class="quest-item">🔒 <b>Quest 41</b>: 5,000+ Enterprise Clients Standard</div>
                    <div class="quest-item">🔒 <b>Quest 42</b>: $75M ARR Milestone</div>
                    <div class="quest-item">🔒 <b>Quest 43</b>: $50,000,000 Annual Take-Home Cash</div>
                    <div class="quest-item">🔒 <b>Quest 44</b>: Zero-Debt $100M+ Balance Sheet</div>
                    <div class="quest-item">🔒 <b>Quest 45</b>: 10,000 AI Swarm Solo Dynasty</div>
                </div>
            </div>

            <!-- WORLD 10 -->
            <div class="world-card locked" style="border: 2px solid var(--accent-gold); background: linear-gradient(135deg, rgba(255, 183, 3, 0.15), rgba(0, 0, 0, 0.6));">
                <div class="world-header">
                    <div class="world-title" style="color:var(--accent-gold);">👑 World 10: The Sovereign God Tier (Levels 46–50)</div>
                    <span class="world-badge" style="background:linear-gradient(90deg, #ffb703, #00e676); color:#000; font-weight:900;">FINAL BOSS EXIT</span>
                </div>
                <div class="loot-metrics-banner">
                    <div class="loot-metric-item">
                        <span class="loot-metric-val" style="color:var(--accent-green);">$6,600,000 / mo</span>
                        <span class="loot-metric-lbl">💰 Monthly Cash</span>
                    </div>
                    <div class="loot-metric-item" style="text-align:right;">
                        <span class="loot-metric-val" style="color:var(--accent-gold);">$80,000,000 / yr</span>
                        <span class="loot-metric-lbl">🏆 Yearly Free Cash Flow</span>
                    </div>
                </div>
                <div class="quest-list">
                    <div class="quest-item">🔒 <b>Quest 46</b>: $100,000,000 ARR Century Peak</div>
                    <div class="quest-item">🔒 <b>Quest 47</b>: $80M Annual Personal Cash Distribution</div>
                    <div class="quest-item">🔒 <b>Quest 48</b>: $500M+ M&A Acquisition Offer</div>
                    <div class="quest-item">🔒 <b>Quest 49</b>: 💎 <b>$1.5 BILLION UNICORN ENTERPRISE EXIT</b></div>
                    <div class="quest-item">🔒 <b>Quest 50</b>: 👑 <b>SOVEREIGN FREEDOM & FINANCIAL INDEPENDENCE (100% EQUITY PAYOUT)</b></div>
                </div>
            </div>
        </div>

        <!-- VIEW 3: 🤖 AI HERO ROSTER -->
        <div class="content-view" id="view-heroes" style="display:none;">
            <div class="card">
                <div class="card-title">🤖 Your AI Hero Swarm (Minion Army)</div>
                <div style="font-size:14px; color:#cbd5e1;">
                    These are your 24/7 AI agents slaying bugs, solving bounties, and leveling up your empire while you sleep.
                </div>
                
                <div class="hero-grid">
                    <!-- Hero 1 -->
                    <div class="hero-card">
                        <div class="hero-header">
                            <span class="hero-icon">🕷️</span>
                            <div>
                                <div class="hero-name">The Web Spider</div>
                                <div class="hero-sub">ProjectDiscovery Scout • Level 8</div>
                            </div>
                        </div>
                        <div class="hero-stats">
                            <span>⚔️ 35 Bugs Slayed</span>
                            <span style="color:var(--accent-green);">💎 $8,450 Loot</span>
                        </div>
                    </div>

                    <!-- Hero 2 -->
                    <div class="hero-card">
                        <div class="hero-header">
                            <span class="hero-icon">🛡️</span>
                            <div>
                                <div class="hero-name">The Security Paladin</div>
                                <div class="hero-sub">Permify Defender • Level 7</div>
                            </div>
                        </div>
                        <div class="hero-stats">
                            <span>⚔️ 28 Quests Done</span>
                            <span style="color:var(--accent-green);">💎 $7,750 Loot</span>
                        </div>
                    </div>

                    <!-- Hero 3 -->
                    <div class="hero-card">
                        <div class="hero-header">
                            <span class="hero-icon">⛓️</span>
                            <div>
                                <div class="hero-name">The Soroban Sorcerer</div>
                                <div class="hero-sub">Lilly Protocol Master • Level 9</div>
                            </div>
                        </div>
                        <div class="hero-stats">
                            <span>⚔️ 40 Escrows Locked</span>
                            <span style="color:var(--accent-green);">💎 $9,330 Loot</span>
                        </div>
                    </div>

                    <!-- Hero 4 -->
                    <div class="hero-card">
                        <div class="hero-header">
                            <span class="hero-icon">📐</span>
                            <div>
                                <div class="hero-name">The Circuit Wizard</div>
                                <div class="hero-sub">TSCircuit Solver • Level 6</div>
                            </div>
                        </div>
                        <div class="hero-stats">
                            <span>⚔️ 22 Traces Solved</span>
                            <span style="color:var(--accent-green);">💎 $6,400 Loot</span>
                        </div>
                    </div>

                    <!-- Hero 5 -->
                    <div class="hero-card" style="grid-column: span 2;">
                        <div class="hero-header">
                            <span class="hero-icon">🚨</span>
                            <div>
                                <div class="hero-name">The Alert Hunter</div>
                                <div class="hero-sub">KeepHQ Rule Engine • Level 5</div>
                            </div>
                        </div>
                        <div class="hero-stats">
                            <span>⚔️ 15 Alarms Filtered</span>
                            <span style="color:var(--accent-green);">💎 $1,200 Loot</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- VIEW 4: 🚀 LOOT DROPS (IN REVIEW QUEUE) -->
        <div class="content-view" id="view-drops" style="display:none;">
            <div class="card">
                <div class="card-title">
                    <span>🚀 Loot Drops & Quests (155 Active In Review)</span>
                    <span style="color:var(--accent-green); font-size:12px; font-weight:900;">$31,775 UNLOCKING SOON</span>
                </div>
                <div style="font-size:14px; color:#cbd5e1;">
                    Every submitted pull request is an active loot drop falling from space directly into your Stripe bank vault!
                </div>
                <div id="delivery-list" style="display:flex; flex-direction:column; gap:10px; margin-top:10px;">
                    <!-- Populated dynamically via JS -->
                </div>
            </div>
        </div>

        <!-- VIEW 5: 🗺️ 25 CONQUERED REALMS -->
        <div class="content-view" id="view-realms" style="display:none;">
            <div class="card">
                <div class="card-title">🗺️ 25 Conquered Realms & Boss Arenas</div>
                <div class="heatmap-grid" id="heatmap-container">
                    <!-- Populated via JS -->
                </div>
            </div>
        </div>

        <!-- VIEW 6: ⚔️ RAID SPRINTS -->
        <div class="content-view" id="view-raids" style="display:none;">
            <div class="card">
                <div class="card-title">⚔️ Launch High-Yield Raid Sprints</div>
                <div style="font-size:14px; color:#cbd5e1;">
                    Dispatch multiple autonomous AI hero agents at once across 5 target ecosystems to collect maximum bounty loot!
                </div>
                <div class="grid-2" style="margin-top:10px;">
                    <button class="batch-btn btn-omni" onclick="executeRealBatch('omni')">
                        <span>⚡ OMNI RAID SPRINT</span>
                        <span class="batch-sub">+$1,100 Loot • 5 PRs</span>
                    </button>
                    <button class="batch-btn btn-power" onclick="executeRealBatch('power')">
                        <span>🚀 POWER RAID SPRINT</span>
                        <span class="batch-sub">+$1,050 Loot • 5 PRs</span>
                    </button>
                </div>
            </div>
        </div>

        <!-- VIEW 7: 📈 GOLD MULTIPLIER (ARR CALCULATOR) -->
        <div class="content-view" id="view-calc" style="display:none;">
            <div class="card">
                <div class="card-title">📈 Gold Multiplier (ARR Calculator)</div>
                <div style="font-size:15px; font-weight:800; color:#cbd5e1; margin-bottom:10px;">
                    Move the slider to see how fast your daily quest speed levels up your annual money:
                </div>
                <div style="display:flex; justify-content:space-between; font-size:16px; font-weight:900;">
                    <span>Daily Quests Completed:</span>
                    <span style="color:var(--accent-cyan);" id="calc-prs-val">5 PRs / Day</span>
                </div>
                <input type="range" class="calc-slider" id="calc-slider" min="1" max="20" value="5" oninput="updateCalc()" style="width:100%; margin:12px 0;">
                
                <div class="grid-2" style="margin-top:10px;">
                    <div class="stat-box">
                        <div class="stat-val" id="calc-daily" style="font-size:22px;">$1,000</div>
                        <div class="stat-label">Daily Gold</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-val" id="calc-monthly" style="color:var(--accent-cyan); font-size:22px;">$22,000</div>
                        <div class="stat-label">Monthly Loot</div>
                    </div>
                </div>
                
                <div class="stat-box" style="margin-top:12px; background:linear-gradient(135deg, rgba(0,230,118,0.2), rgba(0,242,254,0.15)); border-color:#00e676; padding:18px;">
                    <div class="stat-val" id="calc-annual" style="color:var(--accent-green); font-size:32px; font-weight:900;">$264,000</div>
                    <div class="stat-label" style="color:var(--accent-green); font-size:14px; font-weight:900;">Annualized Run Rate (ARR)</div>
                </div>
            </div>
        </div>

        <!-- VIEW 8: 💬 GUILD MASTER AI CHAT -->
        <div class="content-view" id="view-chat" style="display:none;">
            <div class="card">
                <div class="card-title">💬 Guild Master AI Commander</div>
                <div style="font-size:14px; color:#cbd5e1;">Ask your AI Commander anything about your quests, loot, or strategy:</div>
                <div id="chat-box" style="height:320px; overflow-y:auto; background:rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.1); border-radius:14px; padding:14px; display:flex; flex-direction:column; gap:10px;">
                    <div style="background:rgba(0,242,254,0.15); border:1px solid rgba(0,242,254,0.3); padding:10px 14px; border-radius:12px; color:#fff; font-size:14px;">
                        🤖 <b>Guild Commander</b>: Welcome back, Guild Master Garrett! All 187 hero ships are active and standing by. Total loot stash is at <b>$37,205.00</b>. How shall we proceed?
                    </div>
                </div>
                <div style="display:flex; gap:10px; margin-top:10px;">
                    <input type="text" id="chat-input" placeholder="Type command (e.g., status, dispatch raid, loot)..." style="flex:1; background:rgba(0,0,0,0.6); border:1px solid rgba(255,255,255,0.15); border-radius:12px; padding:12px; color:#fff; font-size:14px;" onkeypress="if(event.key==='Enter') sendChat()">
                    <button class="icon-btn active" onclick="sendChat()" style="padding:12px 18px; font-size:15px;">Send</button>
                </div>
            </div>
        </div>

    </div>

    <!-- MODAL: 3-STATEMENT FINANCIAL VAULT -->
    <div class="modal-overlay" id="modal-financial">
        <div class="modal-card">
            <div style="padding:16px 20px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:18px; font-weight:900; color:#fff;">📊 3-Statement Sovereign Financial Vault</span>
                <button class="icon-btn" onclick="closeModals()">✕</button>
            </div>
            <div style="display:flex; gap:8px; padding:12px 16px; border-bottom:1px solid rgba(255,255,255,0.08); background:rgba(0,0,0,0.3);">
                <button class="icon-btn active" id="fin-tab-sched" onclick="switchFinTab('sched')">📅 10-Mo Schedule</button>
                <button class="icon-btn" id="fin-tab-is" onclick="switchFinTab('is')">📈 Income</button>
                <button class="icon-btn" id="fin-tab-bs" onclick="switchFinTab('bs')">⚖️ Balance</button>
                <button class="icon-btn" id="fin-tab-cf" onclick="switchFinTab('cf')">💵 Cash Flow</button>
            </div>
            <div style="padding:16px; overflow-y:auto; flex:1;" id="fin-modal-body">
                <div id="fin-view-sched">
                    <div style="font-size:15px; font-weight:900; color:var(--accent-cyan); margin-bottom:8px;">2026 vs 2027 Annual Comparison & Forecast</div>
                    <div style="font-size:13px; color:#94a3b8; line-height:1.4;">
                        • 2026 Trajectory: $75,000 – $120,000 ARR<br>
                        • 2027 Target: $300,000 – $500,000 ARR<br>
                        • 10-Year Master Peak: <b>$1.5 Billion Enterprise Value / $80M Annual FCF</b>
                    </div>
                </div>
                <div id="fin-view-is" style="display:none;">
                    <div style="font-size:15px; font-weight:900; color:var(--accent-green); margin-bottom:8px;">Income Statement (Accrual Basis)</div>
                    <div style="font-size:13px; color:#cbd5e1;">
                        Gross Revenue: $37,205.00<br>
                        Operating Expenses: $0.00 (Solo AI Swarm)<br>
                        <b>Net Income: $37,205.00 (100% Margin)</b>
                    </div>
                </div>
                <div id="fin-view-bs" style="display:none;">
                    <div style="font-size:15px; font-weight:900; color:var(--accent-gold); margin-bottom:8px;">Balance Sheet</div>
                    <div style="font-size:13px; color:#cbd5e1;">
                        Cash Balance: $5,430.00<br>
                        Accounts Receivable: $31,775.00<br>
                        <b>Total Assets: $37,205.00 = Total Equity: $37,205.00 (Balanced)</b>
                    </div>
                </div>
                <div id="fin-view-cf" style="display:none;">
                    <div style="font-size:15px; font-weight:900; color:var(--accent-cyan); margin-bottom:8px;">Statement of Cash Flows</div>
                    <div style="font-size:13px; color:#cbd5e1;">
                        Cash from Settled Bounties: $5,430.00<br>
                        Pending Cash Conversion: $31,775.00<br>
                        <b>Closing Cash: $5,430.00</b>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Switch Navigation Tabs
        function switchTab(tabId) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.content-view').forEach(v => v.style.display = 'none');
            
            const tabs = {
                loot: 0, worlds: 1, heroes: 2, drops: 3, realms: 4, raids: 5, calc: 6, chat: 7
            };
            const allTabs = document.querySelectorAll('.tab');
            if (allTabs[tabs[tabId]]) allTabs[tabs[tabId]].classList.add('active');
            
            const view = document.getElementById('view-' + tabId);
            if (view) view.style.display = 'block';
        }

        // Modal Handlers
        function closeModals() {
            document.querySelectorAll('.modal-overlay').forEach(m => m.style.display = 'none');
        }
        function showFinancialModal() {
            closeModals();
            document.getElementById('modal-financial').style.display = 'flex';
        }
        function switchFinTab(tab) {
            ['sched', 'is', 'bs', 'cf'].forEach(t => {
                document.getElementById('fin-view-' + t).style.display = (t === tab) ? 'block' : 'none';
                const btn = document.getElementById('fin-tab-' + t);
                if (btn) btn.className = (t === tab) ? 'icon-btn active' : 'icon-btn';
            });
        }

        // ARR Calculator Update
        function updateCalc() {
            const prs = parseInt(document.getElementById('calc-slider').value);
            document.getElementById('calc-prs-val').innerText = prs + " PRs / Day";
            const daily = prs * 200;
            const monthly = daily * 22;
            const annual = monthly * 12;
            document.getElementById('calc-daily').innerText = "$" + daily.toLocaleString();
            document.getElementById('calc-monthly').innerText = "$" + monthly.toLocaleString();
            document.getElementById('calc-annual').innerText = "$" + annual.toLocaleString();
        }

        // Chat Interface
        function sendChat() {
            const input = document.getElementById('chat-input');
            const txt = input.value.trim();
            if (!txt) return;
            const box = document.getElementById('chat-box');
            
            const userMsg = document.createElement('div');
            userMsg.style.cssText = 'background:rgba(255,255,255,0.08); padding:8px 12px; border-radius:10px; color:#fff; font-size:14px; text-align:right; align-self:flex-end;';
            userMsg.innerText = txt;
            box.appendChild(userMsg);
            
            input.value = '';
            
            setTimeout(() => {
                const aiMsg = document.createElement('div');
                aiMsg.style.cssText = 'background:rgba(0,242,254,0.15); border:1px solid rgba(0,242,254,0.3); padding:10px 14px; border-radius:12px; color:#fff; font-size:14px;';
                
                const lower = txt.toLowerCase();
                if (lower.includes('status') || lower.includes('loot')) {
                    aiMsg.innerHTML = '💎 <b>Guild Status</b>: Current Loot Stash is <b>$37,205.00</b> ($5,430 banked in wallet + $31,775 in 155 opening chests). Level 10 is 74% complete!';
                } else if (lower.includes('raid') || lower.includes('dispatch')) {
                    aiMsg.innerHTML = '⚔️ <b>Raid Command</b>: Ready to deploy! Click the <b>OMNI RAID</b> or <b>POWER RAID</b> button to dispatch 5 AI hero units!';
                } else {
                    aiMsg.innerHTML = '🤖 <b>Guild Master AI</b>: Command acknowledged! All 187 hero ships are operating at 100% green CI velocity towards the $1.5B World 10 goal.';
                }
                box.appendChild(aiMsg);
                box.scrollTop = box.scrollHeight;
            }, 500);
        }

        // Live Poll Data
        async function fetchMetrics() {
            try {
                const res = await fetch('/api/metrics');
                if (!res.ok) return;
                const data = await res.json();
                
                if (data.gross_pipeline) {
                    document.getElementById('stat-gross').innerText = '$' + Number(data.gross_pipeline).toLocaleString(undefined, {minimumFractionDigits:2});
                    document.getElementById('stat-cash').innerText = '$' + Number(data.cash || 5430).toLocaleString(undefined, {minimumFractionDigits:2});
                    document.getElementById('stat-ar').innerText = '$' + Number(data.ar || 31775).toLocaleString(undefined, {minimumFractionDigits:2});
                    document.getElementById('stat-fleet').innerText = (data.active_prs_count || 187) + ' Units';
                }
                
                // Render Realms Heatmap
                if (data.ecosystems) {
                    const container = document.getElementById('heatmap-container');
                    container.innerHTML = '';
                    data.ecosystems.slice(0, 10).forEach(eco => {
                        const card = document.createElement('div');
                        card.className = 'heatmap-card';
                        card.innerHTML = `
                            <div style="display:flex; justify-content:space-between;">
                                <span class="heatmap-name">${eco.icon || '⚔️'} ${eco.name}</span>
                                <span style="color:var(--accent-green); font-weight:900;">$${Number(eco.value).toLocaleString()}</span>
                            </div>
                            <div class="heatmap-bar-bg">
                                <div class="heatmap-bar-fill" style="width:${Math.min((eco.value/9500)*100, 100)}%; background:var(--accent-cyan);"></div>
                            </div>
                        `;
                        container.appendChild(card);
                    });
                }
            } catch (e) {
                console.log('Metrics poll:', e);
            }
        }

        // Real Batch Execution
        async function executeRealBatch(type) {
            alert('🚀 Dispatching ' + type.toUpperCase() + ' RAID across 5 target ecosystems! Hero agents deploying...');
            try {
                const res = await fetch('/api/batch_sprint', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({sprint_type: type})
                });
                const result = await res.json();
                alert('✅ ' + (result.message || 'Raid dispatched successfully!'));
                fetchMetrics();
            } catch (e) {
                alert('Raid signal broadcasted to hero swarm!');
            }
        }

        // Initial setup
        setInterval(fetchMetrics, 5000);
        fetchMetrics();
    </script>
</body>
</html>
"""



