import os
import re
import ast
import json
import base64
import random
import tempfile
import urllib.parse
import datetime
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 1. STREAMLIT FULL-VIEWPORT CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Raaj AI Voice Console",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit default UI chrome and completely eliminate ALL outer margins, paddings & side spaces
st.markdown(
    """
    <style>
    /* 1. Global Reset for Streamlit Shell */
    html, body, .stApp, [data-testid="stAppViewContainer"], section.main, .main, [data-testid="stMain"] {
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        width: 100vw !important;
        height: 100vh !important;
        max-width: 100vw !important;
        max-height: 100vh !important;
        background-color: #060818 !important;
    }

    /* 2. Remove all headers, decoration bars, toolbars, and footers */
    [data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stToolbar"], #MainMenu, footer, header {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 3. Strip all Streamlit container side & top spaces */
    .block-container, [data-testid="block-container"] {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100vw !important;
        width: 100vw !important;
        height: 100vh !important;
    }

    div[data-testid="stVerticalBlock"], 
    div[data-testid="stVerticalBlockBorderWrapper"], 
    div[data-testid="element-container"], 
    [data-testid="stCustomComponentV1"] {
        padding: 0 !important;
        margin: 0 !important;
        gap: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        max-width: 100vw !important;
        max-height: 100vh !important;
    }

    /* 4. Force the application iframe to take over 100% full screen edge-to-edge */
    iframe {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        max-width: 100vw !important;
        max-height: 100vh !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        outline: none !important;
        z-index: 999999 !important;
        display: block !important;
        background-color: #060818 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 2. LOAD ROBOT AVATAR IMAGE (AS BASE64)
# ==============================================================================
def get_robot_avatar_b64() -> str:
    """Retrieve base64 encoded string of the 3D robot avatar image."""
    avatar_file = Path(__file__).parent / "assets" / "robot_avatar.jpg"
    if avatar_file.exists():
        try:
            with open(avatar_file, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            pass
    return ""


ROBOT_B64 = get_robot_avatar_b64()


# ==============================================================================
# 3. HTML, CSS & JAVASCRIPT: MASTERCLASS RESPONSIVE AI CONSOLE
# ==============================================================================
HTML_CONTENT = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>Raaj AI Voice Console</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>
/* ==========================================================================
   CSS VARIABLES & DESIGN TOKENS
   ========================================================================== */
:root {{
    --bg-dark: #060818;
    --bg-surface: #0a0e2a;
    --bg-card: rgba(13, 18, 50, 0.72);
    --bg-card-hover: rgba(22, 28, 66, 0.85);
    --border-glass: rgba(139, 92, 246, 0.28);
    --border-glass-hover: rgba(56, 189, 248, 0.55);
    
    --accent-blue: #38bdf8;
    --accent-indigo: #6366f1;
    --accent-purple: #8b5cf6;
    --accent-magenta: #d946ef;
    --accent-pink: #ec4899;
    --accent-cyan: #06b6d4;
    --accent-emerald: #10b981;
    --accent-amber: #f59e0b;
    --accent-rose: #f43f5e;
    
    --text-primary: #ffffff;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    
    --radius-sm: 8px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-xl: 26px;
    --radius-pill: 9999px;
    
    --shadow-subtle: 0 4px 14px rgba(0, 0, 0, 0.35);
    --shadow-glow-purple: 0 0 25px rgba(139, 92, 246, 0.45);
    --shadow-glow-blue: 0 0 25px rgba(56, 189, 248, 0.45);
    --shadow-glow-mic: 0 0 28px rgba(99, 102, 241, 0.65);
    
    --transition-fast: 0.18s ease;
    --transition-smooth: 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    
    --safe-bottom: env(safe-area-inset-bottom, 0px);
}}

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    -webkit-tap-highlight-color: transparent;
}}

html, body {{
    width: 100vw;
    height: 100vh;
    margin: 0;
    padding: 0;
    background-color: var(--bg-dark);
    color: #f1f5f9;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    overflow: hidden;
    user-select: none;
    -webkit-font-smoothing: antialiased;
}}

/* Sleek Modern Scrollbar */
::-webkit-scrollbar {{
    width: 5px;
    height: 5px;
}}
::-webkit-scrollbar-track {{
    background: transparent;
}}
::-webkit-scrollbar-thumb {{
    background: rgba(139, 92, 246, 0.35);
    border-radius: 999px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: rgba(56, 189, 248, 0.7);
}}

/* ==========================================================================
   APP SHELL LAYOUT
   ========================================================================== */
.app-shell {{
    display: flex;
    width: 100vw;
    height: 100vh;
    margin: 0;
    padding: 0;
    overflow: hidden;
    position: relative;
    background: 
        radial-gradient(circle at 15% 20%, rgba(99, 102, 241, 0.12) 0%, transparent 45%),
        radial-gradient(circle at 85% 80%, rgba(217, 70, 239, 0.10) 0%, transparent 50%),
        #060818;
}}

/* ==========================================================================
   DESKTOP / TABLET SIDEBAR (WITH LEFT-RIGHT SLIDE & 3-DOT MENU)
   ========================================================================== */
.sidebar {{
    width: 260px;
    height: 100vh;
    overflow-y: auto;
    overflow-x: hidden;
    background: linear-gradient(180deg, #090c24 0%, #07091a 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    flex-direction: column;
    padding: 20px 14px 16px 14px;
    flex-shrink: 0;
    position: relative;
    z-index: 30;
    transition: margin-left 0.32s cubic-bezier(0.16, 1, 0.3, 1),
                opacity 0.25s ease;
}}

.sidebar.collapsed {{
    margin-left: -260px;
    opacity: 0;
    pointer-events: none;
}}

/* Left/Right Slide Toggle Handle on the Border */
.sidebar-slide-handle {{
    position: absolute;
    top: 50%;
    right: -13px;
    transform: translateY(-50%);
    width: 26px;
    height: 52px;
    background: #0d1238;
    border: 1.5px solid rgba(139, 92, 246, 0.5);
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 50;
    color: #38bdf8;
    font-size: 0.75rem;
    box-shadow: 0 0 16px rgba(56, 189, 248, 0.45);
    transition: all 0.2s ease;
    user-select: none;
}}

.sidebar-slide-handle:hover {{
    background: #182052;
    border-color: #38bdf8;
    box-shadow: 0 0 24px rgba(56, 189, 248, 0.8);
    transform: translateY(-50%) scale(1.12);
    color: #ffffff;
}}

/* Sidebar action buttons in brand box */
.sidebar-icon-btn {{
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #94a3b8;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all var(--transition-fast);
}}

.sidebar-icon-btn:hover {{
    background: rgba(56, 189, 248, 0.18);
    border-color: rgba(56, 189, 248, 0.5);
    color: #38bdf8;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.35);
}}

/* Three Dot Dropdown Menu */
.sidebar-dropdown-menu {{
    display: none;
    position: absolute;
    top: 38px;
    right: 0;
    width: 210px;
    background: rgba(13, 18, 50, 0.95);
    backdrop-filter: blur(14px);
    border: 1.5px solid rgba(139, 92, 246, 0.45);
    border-radius: var(--radius-md);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.75);
    z-index: 100;
    padding: 6px;
}}

.sidebar-dropdown-menu.show {{
    display: flex;
    flex-direction: column;
    gap: 3px;
    animation: menuFadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}}

@keyframes menuFadeIn {{
    from {{ opacity: 0; transform: translateY(-8px) scale(0.96); }}
    to {{ opacity: 1; transform: translateY(0) scale(1); }}
}}

.dropdown-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 0.82rem;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
}}

.dropdown-item:hover {{
    background: linear-gradient(90deg, rgba(56, 189, 248, 0.2), rgba(139, 92, 246, 0.25));
    color: #38bdf8;
}}

/* Expand Button in Main Header */
.sidebar-expand-btn {{
    display: none;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: rgba(13, 18, 50, 0.85);
    border: 1px solid rgba(139, 92, 246, 0.4);
    color: #38bdf8;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all var(--transition-fast);
    flex-shrink: 0;
    margin-right: 12px;
}}

.sidebar-expand-btn:hover {{
    background: rgba(22, 28, 66, 0.95);
    border-color: #38bdf8;
    box-shadow: 0 0 14px rgba(56, 189, 248, 0.5);
    color: #ffffff;
}}

.sidebar.collapsed ~ .main-area .sidebar-expand-btn {{
    display: inline-flex;
}}

/* Mountain landscape silhouette at bottom of sidebar */
.sidebar-mountain-bg {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 140px;
    background: linear-gradient(180deg, transparent 0%, rgba(139, 92, 246, 0.08) 30%, rgba(236, 72, 153, 0.14) 70%, #07091a 100%);
    pointer-events: none;
    z-index: 1;
}}

.sidebar-mountain-svg {{
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 100px;
    pointer-events: none;
    z-index: 2;
}}

.sidebar-content {{
    position: relative;
    z-index: 5;
    display: flex;
    flex-direction: column;
    min-height: 100%;
}}

/* Brand Logo */
.brand-box {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 22px;
    padding: 4px 8px;
    cursor: pointer;
}}

.brand-icon {{
    width: 38px;
    height: 38px;
    border-radius: 12px;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.25rem;
    box-shadow: 0 0 16px rgba(129, 140, 248, 0.5);
    flex-shrink: 0;
}}

.brand-title {{
    font-weight: 800;
    font-size: 1.15rem;
    letter-spacing: -0.3px;
    color: #ffffff;
    line-height: 1.1;
}}

.brand-sub {{
    font-size: 0.72rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}}

/* Navigation Menu */
.nav-menu {{
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 20px;
}}

.nav-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border-radius: 12px;
    color: #94a3b8;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    transition: all var(--transition-fast);
    position: relative;
}}

.nav-item:hover {{
    background: rgba(255, 255, 255, 0.05);
    color: #ffffff;
    transform: translateX(2px);
}}

.nav-item.active {{
    background: linear-gradient(90deg, rgba(56, 189, 248, 0.18) 0%, rgba(139, 92, 246, 0.22) 100%);
    border: 1px solid rgba(56, 189, 248, 0.45);
    color: #ffffff;
    font-weight: 600;
    box-shadow: 0 2px 10px rgba(56, 189, 248, 0.2);
}}

.nav-item.active::before {{
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3.5px;
    height: 18px;
    background: #38bdf8;
    border-radius: 0 4px 4px 0;
    box-shadow: 0 0 8px #38bdf8;
}}

.nav-icon {{
    font-size: 1.05rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 22px;
}}

/* Assistant Settings Box in Sidebar */
.settings-section {{
    margin-top: auto;
    padding-top: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 8px;
}}

.settings-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #c084fc;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}}

.field-label {{
    font-size: 0.74rem;
    color: #94a3b8;
    margin-bottom: 5px;
    font-weight: 500;
}}

.select-styled {{
    width: 100%;
    background: rgba(14, 18, 48, 0.85);
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 8px;
    color: #f1f5f9;
    padding: 7px 10px;
    font-size: 0.82rem;
    outline: none;
    cursor: pointer;
    transition: border-color var(--transition-fast);
}}

.select-styled:focus {{
    border-color: #38bdf8;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
}}

.two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}}

.toggle-row {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 4px;
}}

.toggle-switch {{
    position: relative;
    width: 38px;
    height: 22px;
    background: #8b5cf6;
    border-radius: 999px;
    cursor: pointer;
    transition: background var(--transition-fast);
    flex-shrink: 0;
}}

.toggle-thumb {{
    position: absolute;
    top: 2px;
    right: 2px;
    width: 18px;
    height: 18px;
    background: white;
    border-radius: 50%;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
    transition: all var(--transition-fast);
}}

.toggle-label {{
    font-size: 0.76rem;
    color: #cbd5e1;
}}

/* ==========================================================================
   MOBILE TOP HEADER & SLIDE-OUT DRAWER (MOBILE-FIRST)
   ========================================================================== */
.mobile-header {{
    display: none; /* Shown on <= 767px */
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: rgba(9, 12, 36, 0.92);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid rgba(139, 92, 246, 0.25);
    position: sticky;
    top: 0;
    z-index: 60;
    width: 100%;
}}

.mobile-header-left {{
    display: flex;
    align-items: center;
    gap: 10px;
}}

.hamburger-btn {{
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
    cursor: pointer;
    transition: background var(--transition-fast);
}}

.hamburger-btn span {{
    display: block;
    width: 18px;
    height: 2px;
    background-color: #f1f5f9;
    border-radius: 2px;
}}

.mobile-brand-box {{
    display: flex;
    align-items: center;
    gap: 8px;
}}

.mobile-brand-icon {{
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.95rem;
}}

.mobile-brand-title {{
    font-weight: 800;
    font-size: 1rem;
    color: #ffffff;
    line-height: 1.1;
}}

.mobile-header-right {{
    display: flex;
    align-items: center;
    gap: 8px;
}}

.mobile-core-pill {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(52, 211, 153, 0.4);
    border-radius: 999px;
    color: #34d399;
    font-size: 0.72rem;
    font-weight: 600;
}}

.mobile-notif-btn {{
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    cursor: pointer;
    position: relative;
}}

/* Mobile Drawer Overlay & Sliding Panel */
.drawer-backdrop {{
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(4, 6, 18, 0.75);
    backdrop-filter: blur(8px);
    z-index: 100;
    opacity: 0;
    transition: opacity var(--transition-smooth);
}}

.drawer-backdrop.open {{
    display: block;
    opacity: 1;
}}

.mobile-drawer {{
    position: fixed;
    top: 0;
    left: 0;
    width: 290px;
    max-width: 85vw;
    height: 100vh;
    background: #090d2a;
    border-right: 1.5px solid rgba(139, 92, 246, 0.4);
    box-shadow: 0 0 35px rgba(0, 0, 0, 0.8);
    z-index: 101;
    transform: translateX(-100%);
    transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    flex-direction: column;
    padding: 20px 16px;
    overflow-y: auto;
}}

.mobile-drawer.open {{
    transform: translateX(0);
}}

.drawer-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}}

.drawer-close-btn {{
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    border: none;
    color: #94a3b8;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}}

/* ==========================================================================
   MAIN RIGHT CONTENT AREA
   ========================================================================== */
.main-area {{
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 16px 22px 20px 22px;
    height: 100vh;
    overflow-y: auto;
    overflow-x: hidden;
    position: relative;
    max-width: 100%;
}}

/* Desktop/Tablet Top Header Bar */
.top-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
    flex-wrap: wrap;
    gap: 12px;
    flex-shrink: 0;
}}

.welcome-box {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.welcome-hand {{
    font-size: 1.6rem;
    animation: waveHand 2s infinite ease-in-out;
}}

@keyframes waveHand {{
    0%, 100% {{ transform: rotate(0deg); }}
    20%, 60% {{ transform: rotate(14deg); }}
    40%, 80% {{ transform: rotate(-14deg); }}
}}

.welcome-title {{
    font-size: 1.2rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
}}

.welcome-sub {{
    font-size: 0.82rem;
    color: #94a3b8;
}}

.header-right {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.core-ready-pill {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(52, 211, 153, 0.4);
    border-radius: 999px;
    color: #34d399;
    font-size: 0.82rem;
    font-weight: 600;
}}

.core-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #34d399;
    box-shadow: 0 0 8px #34d399;
}}

.notif-bell-btn {{
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    cursor: pointer;
    font-size: 0.95rem;
    transition: background var(--transition-fast);
}}

.notif-bell-btn:hover {{
    background: rgba(255, 255, 255, 0.12);
}}

.notif-badge {{
    position: absolute;
    top: -2px;
    right: -2px;
    background: #ef4444;
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid #060818;
}}

.deploy-btn {{
    background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%);
    color: white;
    font-weight: 600;
    font-size: 0.82rem;
    padding: 8px 18px;
    border-radius: 999px;
    border: 1px solid rgba(168, 85, 247, 0.5);
    box-shadow: 0 4px 14px rgba(139, 92, 246, 0.4);
    cursor: pointer;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}}

.deploy-btn:hover {{
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
}}

/* ==========================================================================
   HERO VOICE CONSOLE BANNER (RESPONSIVE)
   ========================================================================== */
.hero-banner {{
    background: 
        radial-gradient(circle at 85% 30%, rgba(0, 198, 255, 0.18) 0%, transparent 55%),
        radial-gradient(circle at 60% 60%, rgba(139, 92, 246, 0.16) 0%, transparent 60%),
        linear-gradient(135deg, rgba(16, 22, 60, 0.92) 0%, rgba(9, 13, 38, 0.96) 100%);
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: var(--radius-xl);
    padding: 24px 30px;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    gap: 32px;
    position: relative;
    overflow: hidden;
    margin-bottom: 20px;
    flex-shrink: 0;
    min-height: 250px;
}}

/* Planet Hologram Arc Overlay on Right */
.planet-arc {{
    position: absolute;
    right: -40px;
    top: -20px;
    width: 320px;
    height: 320px;
    border-radius: 50%;
    border: 2px solid rgba(56, 189, 248, 0.25);
    box-shadow: 0 0 40px rgba(56, 189, 248, 0.2), inset 0 0 30px rgba(139, 92, 246, 0.25);
    pointer-events: none;
    background: radial-gradient(circle, rgba(14, 165, 233, 0.08) 0%, transparent 70%);
}}

/* Left 3D Robot Avatar inside Glowing Neon Ring */
.robot-wrap {{
    position: relative;
    width: 165px;
    height: 165px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

.neon-ring-glow {{
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 2.5px solid rgba(139, 92, 246, 0.65);
    box-shadow: 0 0 25px rgba(139, 92, 246, 0.6), inset 0 0 15px rgba(56, 189, 248, 0.4);
    animation: pulseRing 4s ease-in-out infinite alternate;
}}

@keyframes pulseRing {{
    0% {{ transform: scale(0.97); box-shadow: 0 0 20px rgba(139, 92, 246, 0.5); }}
    100% {{ transform: scale(1.03); box-shadow: 0 0 32px rgba(56, 189, 248, 0.7); }}
}}

.robot-image {{
    width: 150px;
    height: 150px;
    border-radius: 50%;
    object-fit: cover;
    z-index: 2;
    border: 2px solid rgba(255, 255, 255, 0.25);
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.6);
}}

/* Center Stage */
.hero-center {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    z-index: 2;
}}

.assistant-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    background: rgba(139, 92, 246, 0.16);
    border: 1px solid rgba(168, 85, 247, 0.45);
    border-radius: 999px;
    color: #c084fc;
    font-size: 0.78rem;
    font-weight: 600;
    margin-bottom: 8px;
}}

.hero-title {{
    font-size: clamp(1.6rem, 3.2vw, 2.3rem);
    font-weight: 800;
    letter-spacing: -0.8px;
    background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.15;
    margin-bottom: 4px;
}}

.hero-subtitle {{
    font-size: clamp(0.78rem, 1.5vw, 0.88rem);
    color: #94a3b8;
    margin-bottom: 14px;
}}

/* Waveform & Central Mic */
.waveform-box {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 14px;
}}

.wave-bars {{
    display: flex;
    align-items: center;
    gap: 3.5px;
    height: 32px;
}}

.wave-bar {{
    width: 3.5px;
    background: linear-gradient(180deg, #38bdf8, #818cf8);
    border-radius: 999px;
    animation: barPulse 1.2s ease-in-out infinite alternate;
}}

.wave-bar:nth-child(1) {{ height: 8px; animation-delay: 0.1s; }}
.wave-bar:nth-child(2) {{ height: 18px; animation-delay: 0.3s; }}
.wave-bar:nth-child(3) {{ height: 26px; animation-delay: 0.15s; }}
.wave-bar:nth-child(4) {{ height: 32px; animation-delay: 0.35s; }}
.wave-bar:nth-child(5) {{ height: 22px; animation-delay: 0.2s; }}
.wave-bar:nth-child(6) {{ height: 14px; animation-delay: 0.4s; }}
.wave-bar:nth-child(7) {{ height: 24px; animation-delay: 0.1s; }}
.wave-bar:nth-child(8) {{ height: 12px; animation-delay: 0.25s; }}

@keyframes barPulse {{
    0% {{ transform: scaleY(0.35); opacity: 0.5; }}
    100% {{ transform: scaleY(1.0); opacity: 1; }}
}}

.center-mic-btn {{
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0284c7 0%, #6366f1 50%, #a855f7 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    box-shadow: 0 0 22px rgba(129, 140, 248, 0.65), inset 0 0 8px rgba(255, 255, 255, 0.4);
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    border: none;
    color: white;
}}

.center-mic-btn:hover {{
    transform: scale(1.08);
    box-shadow: 0 0 32px rgba(56, 189, 248, 0.85);
}}

.center-mic-btn.listening {{
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    box-shadow: 0 0 35px rgba(239, 68, 68, 0.95), inset 0 0 10px rgba(255, 255, 255, 0.5) !important;
    animation: micPulseListening 1s infinite alternate;
}}

@keyframes micPulseListening {{
    0% {{ transform: scale(1.0); box-shadow: 0 0 20px rgba(239, 68, 68, 0.7); }}
    100% {{ transform: scale(1.12); box-shadow: 0 0 40px rgba(239, 68, 68, 1); }}
}}

.voice-status-text {{
    font-size: 0.75rem;
    font-weight: 600;
    color: #38bdf8;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}}

/* Capsule Command Bar */
.command-capsule {{
    width: 100%;
    max-width: 580px;
    background: rgba(9, 14, 38, 0.88);
    border: 1.5px solid rgba(56, 189, 248, 0.4);
    border-radius: 999px;
    padding: 6px 8px 6px 18px;
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.45);
    transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}}

.command-capsule:focus-within {{
    border-color: #38bdf8;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
}}

.capsule-mic-icon {{
    font-size: 1.15rem;
    color: #38bdf8;
    cursor: pointer;
    transition: transform var(--transition-fast);
}}

.capsule-mic-icon:hover {{
    transform: scale(1.15);
}}

.capsule-input {{
    flex: 1;
    background: transparent;
    border: none;
    color: #ffffff;
    font-size: 0.92rem;
    outline: none;
    font-family: inherit;
}}

.capsule-input::placeholder {{
    color: #64748b;
    font-size: 0.86rem;
}}

.capsule-send-btn {{
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0ea5e9, #6366f1);
    border: none;
    color: white;
    font-size: 1.05rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(14, 165, 233, 0.4);
    transition: transform var(--transition-fast);
    flex-shrink: 0;
}}

.capsule-send-btn:hover {{
    transform: scale(1.08);
}}

/* ==========================================================================
   FEATURE CARDS GRID (RESPONSIVE)
   ========================================================================== */
.quick-cards-grid {{
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 12px;
    margin-bottom: 22px;
    flex-shrink: 0;
}}

.feature-card {{
    background: rgba(13, 18, 50, 0.7);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: var(--radius-lg);
    padding: 16px 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    cursor: pointer;
    transition: all var(--transition-fast);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
    position: relative;
    overflow: hidden;
}}

.feature-card:hover {{
    transform: translateY(-3px);
    border-color: rgba(56, 189, 248, 0.6);
    background: rgba(20, 26, 68, 0.85);
    box-shadow: 0 8px 22px rgba(56, 189, 248, 0.25);
}}

.feature-card:active {{
    transform: scale(0.97);
}}

.card-ico {{
    font-size: 1.7rem;
    margin-bottom: 8px;
}}

.card-title {{
    font-size: 0.84rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: 3px;
}}

.card-desc {{
    font-size: 0.72rem;
    color: #94a3b8;
    line-height: 1.25;
}}

/* ==========================================================================
   SHOWCASE UTILITIES & FUN ENGINE (RESPONSIVE)
   ========================================================================== */
.showcase-wrapper {{
    background: rgba(10, 14, 40, 0.75);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: var(--radius-xl);
    padding: 20px 24px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
    margin-bottom: 22px;
    flex-shrink: 0;
}}

.showcase-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    color: #ffffff;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 16px;
    letter-spacing: -0.2px;
}}

.showcase-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}}

.engine-card {{
    background: rgba(16, 22, 60, 0.65);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: var(--radius-lg);
    padding: 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: all var(--transition-fast);
}}

.engine-card:hover {{
    border-color: rgba(56, 189, 248, 0.45);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
}}

.card-heading {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.95rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 12px;
}}

.input-label {{
    font-size: 0.76rem;
    color: #94a3b8;
    margin-bottom: 6px;
}}

.engine-input {{
    width: 100%;
    background: rgba(9, 13, 38, 0.85);
    border: 1px solid rgba(139, 92, 246, 0.35);
    border-radius: 10px;
    color: #ffffff;
    padding: 10px 12px;
    font-size: 0.88rem;
    outline: none;
    font-family: inherit;
    margin-bottom: 12px;
    transition: border-color var(--transition-fast);
}}

.engine-input:focus {{
    border-color: #38bdf8;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.35);
}}

.btn-solve {{
    width: 100%;
    height: 42px;
    background: linear-gradient(90deg, #38bdf8 0%, #6366f1 100%);
    border: none;
    border-radius: 10px;
    color: white;
    font-weight: 700;
    font-size: 0.88rem;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(56, 189, 248, 0.35);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all var(--transition-fast);
}}

.btn-solve:hover {{
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(56, 189, 248, 0.5);
}}

.btn-solve:active {{
    transform: scale(0.98);
}}

/* Slider Component */
.slider-container {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 14px;
}}

.slider-label-row {{
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    color: #94a3b8;
}}

.range-slider {{
    -webkit-appearance: none;
    width: 100%;
    height: 6px;
    border-radius: 999px;
    background: #1e293b;
    outline: none;
    cursor: pointer;
}}

.range-slider::-webkit-slider-thumb {{
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #f472b6;
    box-shadow: 0 0 10px #f472b6;
    cursor: pointer;
}}

.slider-scale {{
    display: flex;
    justify-content: space-between;
    font-size: 0.72rem;
    color: #64748b;
}}

.btn-password {{
    width: 100%;
    height: 42px;
    background: linear-gradient(90deg, #ec4899 0%, #a855f7 100%);
    border: none;
    border-radius: 10px;
    color: white;
    font-weight: 700;
    font-size: 0.88rem;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(236, 72, 153, 0.35);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all var(--transition-fast);
}}

.btn-password:hover {{
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(236, 72, 153, 0.5);
}}

.btn-password:active {{
    transform: scale(0.98);
}}

/* Coin & Dice */
.coin-dice-buttons {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 12px;
}}

.btn-flip-coin, .btn-roll-dice {{
    height: 42px;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    color: white;
    font-weight: 600;
    font-size: 0.84rem;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: all var(--transition-fast);
}}

.btn-flip-coin {{
    background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
    box-shadow: 0 3px 10px rgba(217, 119, 6, 0.3);
}}

.btn-roll-dice {{
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
    box-shadow: 0 3px 10px rgba(124, 58, 237, 0.3);
}}

.coin-dice-results {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}}

.coin-display-card, .dice-display-card {{
    background: rgba(9, 13, 38, 0.9);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 10px;
    height: 72px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}}

.coin-medal {{
    font-size: 1.5rem;
    margin-bottom: 2px;
}}

.coin-text {{
    font-size: 0.74rem;
    color: #fbbf24;
    font-weight: 700;
}}

.dice-cube {{
    font-size: 2.2rem;
    color: #c084fc;
    line-height: 1;
}}

/* ==========================================================================
   QUICK WEB PORTALS (RESPONSIVE)
   ========================================================================== */
.portals-section {{
    background: rgba(10, 14, 40, 0.6);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: var(--radius-lg);
    padding: 16px 20px;
    margin-bottom: 22px;
    flex-shrink: 0;
}}

.portals-title {{
    font-size: 0.85rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}}

.portals-grid {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
}}

.portal-btn {{
    background: rgba(16, 22, 60, 0.7);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 10px;
    padding: 10px 12px;
    color: #ffffff;
    font-size: 0.84rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    cursor: pointer;
    text-decoration: none;
    transition: all var(--transition-fast);
}}

.portal-btn:hover {{
    background: rgba(30, 41, 89, 0.9);
    border-color: #38bdf8;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.25);
}}

/* ==========================================================================
   BOTTOM TELEMETRY STATUS BAR (RESPONSIVE)
   ========================================================================== */
.bottom-bar {{
    background: rgba(10, 14, 40, 0.85);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: var(--radius-xl);
    padding: 14px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
    margin-top: 10px;
    margin-bottom: 10px;
    flex-shrink: 0;
}}

.bar-metric {{
    display: flex;
    align-items: center;
    gap: 12px;
}}

.metric-ico-box {{
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}}

.metric-num {{
    font-weight: 800;
    font-size: 1.15rem;
    color: #ffffff;
    line-height: 1.1;
}}

.metric-tag {{
    font-size: 0.72rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* Live Equalizer Animation inside Metric */
.live-wave-equalizer {{
    display: flex;
    align-items: center;
    gap: 2.5px;
    height: 16px;
}}

.equalizer-bar {{
    width: 2.5px;
    background: #34d399;
    border-radius: 2px;
    animation: eqPulse 1s ease-in-out infinite alternate;
}}

.equalizer-bar:nth-child(1) {{ height: 6px; animation-delay: 0.1s; }}
.equalizer-bar:nth-child(2) {{ height: 16px; animation-delay: 0.35s; }}
.equalizer-bar:nth-child(3) {{ height: 10px; animation-delay: 0.2s; }}
.equalizer-bar:nth-child(4) {{ height: 14px; animation-delay: 0.45s; }}

@keyframes eqPulse {{
    0% {{ transform: scaleY(0.3); }}
    100% {{ transform: scaleY(1.0); }}
}}

/* ==========================================================================
   FIXED BOTTOM MOBILE NAVIGATION (MOBILE-FIRST)
   ========================================================================== */
.bottom-mobile-nav {{
    display: none; /* Shown on <= 767px */
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 64px;
    background: rgba(8, 12, 34, 0.94);
    backdrop-filter: blur(18px);
    border-top: 1px solid rgba(139, 92, 246, 0.35);
    z-index: 70;
    align-items: center;
    justify-content: space-around;
    padding: 0 10px var(--safe-bottom) 10px;
    box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.5);
}}

.bnav-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 3px;
    color: #94a3b8;
    font-size: 0.7rem;
    font-weight: 600;
    cursor: pointer;
    flex: 1;
    height: 100%;
    transition: color var(--transition-fast);
}}

.bnav-item:hover, .bnav-item.active {{
    color: #38bdf8;
}}

.bnav-icon {{
    font-size: 1.25rem;
}}

/* Elevated center voice button in mobile nav */
.bnav-voice-btn {{
    position: relative;
    top: -14px;
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0284c7 0%, #6366f1 50%, #a855f7 100%);
    border: 2px solid rgba(255, 255, 255, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5rem;
    box-shadow: 0 0 20px rgba(129, 140, 248, 0.75);
    cursor: pointer;
    transition: transform var(--transition-fast);
}}

.bnav-voice-btn:active {{
    transform: scale(0.92);
}}

.bnav-voice-btn.listening {{
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    animation: micPulseListening 1s infinite alternate;
}}

/* ==========================================================================
   TOAST NOTIFICATION COMPONENT
   ========================================================================== */
.toast-container {{
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 250;
    display: flex;
    flex-direction: column;
    gap: 8px;
    pointer-events: none;
}}

.toast-message {{
    background: rgba(15, 23, 62, 0.95);
    border: 1px solid rgba(56, 189, 248, 0.5);
    backdrop-filter: blur(12px);
    color: #ffffff;
    padding: 10px 20px;
    border-radius: 999px;
    font-size: 0.86rem;
    font-weight: 600;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    gap: 8px;
    animation: toastFadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1), toastFadeOut 0.3s cubic-bezier(0.16, 1, 0.3, 1) 2.7s forwards;
    pointer-events: auto;
}}

@keyframes toastFadeIn {{
    from {{ opacity: 0; transform: translateY(-12px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes toastFadeOut {{
    from {{ opacity: 1; transform: translateY(0); }}
    to {{ opacity: 0; transform: translateY(-12px); }}
}}

/* ==========================================================================
   MODAL DIALOGS (RESPONSIVE)
   ========================================================================== */
.modal-overlay {{
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(4, 6, 18, 0.85);
    backdrop-filter: blur(14px);
    z-index: 150;
    align-items: center;
    justify-content: center;
    padding: 20px;
}}

.modal-overlay.open {{
    display: flex;
}}

.modal-box {{
    background: #0d1232;
    border: 1.5px solid rgba(139, 92, 246, 0.45);
    border-radius: var(--radius-xl);
    width: 100%;
    max-width: 720px;
    max-height: 88vh;
    overflow-y: auto;
    padding: 24px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
    position: relative;
    animation: modalPop 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}}

@keyframes modalPop {{
    from {{ opacity: 0; transform: scale(0.95); }}
    to {{ opacity: 1; transform: scale(1); }}
}}

.modal-close {{
    position: absolute;
    top: 18px;
    right: 18px;
    background: rgba(255, 255, 255, 0.08);
    border: none;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    color: #94a3b8;
    font-size: 1.15rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-fast);
}}

.modal-close:hover {{
    color: white;
    background: rgba(255, 255, 255, 0.16);
}}

.btn-voice-record {{
    background: linear-gradient(135deg, #0284c7 0%, #6366f1 100%);
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
    padding: 0 16px;
    height: 42px;
    border-radius: 10px;
    border: 1px solid rgba(56, 189, 248, 0.4);
    box-shadow: 0 4px 14px rgba(14, 165, 233, 0.35);
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    white-space: nowrap;
    transition: all var(--transition-fast);
}}

.btn-voice-record:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(14, 165, 233, 0.5);
}}

.btn-voice-record.recording {{
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    border-color: #f87171 !important;
    box-shadow: 0 0 22px rgba(239, 68, 68, 0.8) !important;
    animation: micPulseGlow 1s infinite alternate;
}}

@keyframes micPulseGlow {{
    0% {{ transform: scale(0.97); box-shadow: 0 0 14px rgba(239, 68, 68, 0.6); }}
    100% {{ transform: scale(1.04); box-shadow: 0 0 26px rgba(239, 68, 68, 1); }}
}}


/* ==========================================================================
   RESPONSIVE MEDIA QUERIES (3 BREAKPOINTS)
   1. Laptop / Desktop: 1200px+
   2. Tablet: 768px - 1199px
   3. Mobile Phone: 320px - 767px
   ========================================================================== */

/* --------------------------------------------------------------------------
   TABLET BREAKPOINT: 768px to 1199px
   -------------------------------------------------------------------------- */
@media (min-width: 768px) and (max-width: 1199px) {{
    .sidebar {{
        width: 210px;
        padding: 16px 10px;
    }}
    
    .sidebar.collapsed {{
        margin-left: -210px;
    }}
    
    .brand-title {{
        font-size: 1.05rem;
    }}
    
    .nav-item {{
        padding: 8px 10px;
        font-size: 0.82rem;
    }}
    
    .main-area {{
        padding: 16px 18px;
    }}
    
    .hero-banner {{
        padding: 20px;
        gap: 20px;
        flex-shrink: 0;
        min-height: 240px;
    }}
    
    .robot-wrap {{
        width: 130px;
        height: 130px;
    }}
    
    .robot-image {{
        width: 118px;
        height: 118px;
    }}
    
    .quick-cards-grid {{
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
    }}
    
    .showcase-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
    
    .portals-grid {{
        grid-template-columns: repeat(3, 1fr);
    }}
    
    .bottom-bar {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        padding: 12px 16px;
    }}
}}

/* --------------------------------------------------------------------------
   MOBILE PHONE BREAKPOINT: 320px to 767px
   -------------------------------------------------------------------------- */
@media (max-width: 767px) {{
    /* Hide desktop sidebar and desktop top header */
    .sidebar {{
        display: none !important;
    }}
    
    .top-header {{
        display: none !important;
    }}
    
    /* Show mobile top header and bottom mobile nav */
    .mobile-header {{
        display: flex;
    }}
    
    .bottom-mobile-nav {{
        display: flex;
    }}
    
    .main-area {{
        padding: 12px 14px 85px 14px; /* Extra bottom padding so bottom nav doesn't cover content */
    }}
    
    /* Transform Hero Section into stacked mobile view */
    .hero-banner {{
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 20px 14px;
        gap: 16px;
        border-radius: var(--radius-lg);
        flex-shrink: 0;
        min-height: auto;
    }}
    
    .planet-arc {{
        display: none;
    }}
    
    .robot-wrap {{
        width: 105px;
        height: 105px;
    }}
    
    .robot-image {{
        width: 95px;
        height: 95px;
    }}
    
    .hero-title {{
        font-size: 1.65rem;
    }}
    
    .hero-subtitle {{
        font-size: 0.78rem;
        margin-bottom: 10px;
    }}
    
    .waveform-box {{
        gap: 10px;
        margin-bottom: 12px;
    }}
    
    .center-mic-btn {{
        width: 58px;
        height: 58px;
        font-size: 1.55rem;
    }}
    
    .command-capsule {{
        max-width: 100%;
        padding: 4px 6px 4px 14px;
    }}
    
    .capsule-input {{
        font-size: 0.88rem;
    }}
    
    /* Transform Feature cards to 2-column mobile grid */
    .quick-cards-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        margin-bottom: 16px;
    }}
    
    .feature-card {{
        padding: 12px 8px;
        border-radius: var(--radius-md);
    }}
    
    .card-ico {{
        font-size: 1.45rem;
        margin-bottom: 4px;
    }}
    
    .card-title {{
        font-size: 0.8rem;
    }}
    
    .card-desc {{
        font-size: 0.68rem;
    }}
    
    /* Transform Showcase to 1-column mobile stack */
    .showcase-wrapper {{
        padding: 16px 14px;
        border-radius: var(--radius-lg);
        margin-bottom: 16px;
    }}
    
    .showcase-grid {{
        grid-template-columns: 1fr;
        gap: 14px;
    }}
    
    .engine-card {{
        padding: 14px;
    }}
    
    /* Transform Quick Portals to 2-column */
    .portals-section {{
        padding: 14px;
        margin-bottom: 16px;
    }}
    
    .portals-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
    }}
    
    /* Transform Bottom Telemetry to compact 2x2 grid */
    .bottom-bar {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        padding: 12px 14px;
        border-radius: var(--radius-lg);
    }}
    
    .bar-metric {{
        gap: 8px;
    }}
    
    .metric-ico-box {{
        width: 32px;
        height: 32px;
        font-size: 0.95rem;
    }}
    
    .metric-num {{
        font-size: 1rem;
    }}
    
    .metric-tag {{
        font-size: 0.65rem;
    }}
    
    /* Modal full-width on mobile */
    .modal-box {{
        padding: 18px 14px;
        max-height: 92vh;
        border-radius: var(--radius-lg);
    }}
}}

/* --------------------------------------------------------------------------
   SMALL MOBILE PHONES: 320px to 479px
   -------------------------------------------------------------------------- */
@media (max-width: 479px) {{
    .main-area {{
        padding: 10px 10px 85px 10px;
    }}
    
    .hero-title {{
        font-size: 1.45rem;
    }}
    
    .robot-wrap {{
        width: 90px;
        height: 90px;
    }}
    
    .robot-image {{
        width: 80px;
        height: 80px;
    }}
    
    .quick-cards-grid {{
        gap: 6px;
    }}
    
    .feature-card {{
        padding: 10px 6px;
    }}
}}

/* --------------------------------------------------------------------------
   ACCESSIBILITY: REDUCED MOTION SUPPORT
   -------------------------------------------------------------------------- */
@media (prefers-reduced-motion: reduce) {{
    *, ::before, ::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }}
}}
</style>
</head>
<body>

<!-- Toast Notification Container -->
<div class="toast-container" id="toastContainer"></div>

<!-- Mobile Drawer Backdrop -->
<div class="drawer-backdrop" id="drawerBackdrop" onclick="closeDrawer()"></div>

<!-- Slide-out Mobile Navigation Drawer -->
<aside class="mobile-drawer" id="mobileDrawer">
    <div class="drawer-header">
        <div class="brand-box" style="margin-bottom: 0;">
            <div class="brand-icon">✦</div>
            <div>
                <div class="brand-title">Raaj AI</div>
                <div class="brand-sub">Voice Console</div>
            </div>
        </div>
        <button class="drawer-close-btn" onclick="closeDrawer()" title="Close menu">✕</button>
    </div>

    <!-- Drawer Navigation Links -->
    <nav class="nav-menu">
        <div class="nav-item active" onclick="switchNav('Dashboard', this); closeDrawer()">
            <span class="nav-icon">🏠</span>
            <span>Dashboard</span>
        </div>
        <div class="nav-item" onclick="openModal('voiceModal'); closeDrawer()">
            <span class="nav-icon">🎙️</span>
            <span>AI Voice & Chat</span>
        </div>
        <div class="nav-item" onclick="openModal('ytModal'); closeDrawer()">
            <span class="nav-icon">🎬</span>
            <span>YouTube Studio</span>
        </div>
        <div class="nav-item" onclick="openModal('weatherModal'); closeDrawer()">
            <span class="nav-icon">⛅</span>
            <span>Weather & World</span>
        </div>
        <div class="nav-item" onclick="openModal('wikiModal'); closeDrawer()">
            <span class="nav-icon">📖</span>
            <span>Wikipedia Hub</span>
        </div>
        <div class="nav-item" onclick="openModal('notesModal'); closeDrawer()">
            <span class="nav-icon">📝</span>
            <span>Smart Notes</span>
        </div>
        <div class="nav-item" onclick="openModal('waModal'); closeDrawer()">
            <span class="nav-icon">💬</span>
            <span>WhatsApp Portal</span>
        </div>
        <div class="nav-item" onclick="scrollToSection('utilitiesSection'); closeDrawer()">
            <span class="nav-icon">🛠️</span>
            <span>Tools & Fun</span>
        </div>
        <div class="nav-item" onclick="openModal('sysModal'); closeDrawer()">
            <span class="nav-icon">🖥️</span>
            <span>System Assistant</span>
        </div>
    </nav>

    <!-- Drawer Settings -->
    <div class="settings-section">
        <div class="settings-header">
            <span>⚙️</span>
            <span>Assistant Settings</span>
        </div>

        <div>
            <div class="field-label">Voice Persona</div>
            <select id="drawerPersonaSelect" class="select-styled" onchange="syncPersona(this.value)">
                <option value="Raaj AI" selected>Raaj AI</option>
                <option value="Alexa Edition">Alexa Edition</option>
                <option value="Jarvis Ultra">Jarvis Ultra</option>
                <option value="Friday AI">Friday AI</option>
            </select>
        </div>

        <div>
            <div class="field-label">Voice Accent / Language</div>
            <select id="drawerAccentSelect" class="select-styled" onchange="syncLanguage(this.value)">
                <option value="en-IN" selected>English (India)</option>
                <option value="hi-IN">Hindi (हिंदी)</option>
                <option value="or-IN">Odia (ଓଡ଼ିଆ)</option>
                <option value="te-IN">Telugu (తెలుగు)</option>
                <option value="en-US">English (US)</option>
                <option value="en-GB">English (UK)</option>
                <option value="en-AU">English (Australia)</option>
            </select>
        </div>

        <div class="two-col">
            <div>
                <div class="field-label">Speed</div>
                <select id="drawerSpeedSelect" class="select-styled" onchange="syncSpeed(this.value)">
                    <option value="1" selected>Normal</option>
                    <option value="0.85">Slow</option>
                </select>
            </div>
            <div>
                <div class="field-label">Autoplay</div>
                <select id="drawerAutoplaySelect" class="select-styled" onchange="syncAutoplay(this.value)">
                    <option value="true" selected>Enabled</option>
                    <option value="false">Muted</option>
                </select>
            </div>
        </div>
    </div>
</aside>


<!-- Main App Shell -->
<div class="app-shell">

    <!-- ==========================================================================
         DESKTOP & TABLET LEFT SIDEBAR
         ========================================================================== -->
    <aside class="sidebar" id="desktopSidebar">
        <!-- Floating Left-Right Slide Handle on Border -->
        <div class="sidebar-slide-handle" id="sidebarSlideHandle" onclick="toggleSidebarSlide()" title="Slide/Collapse Sidebar (◀ / ▶)">◀</div>

        <div class="sidebar-mountain-bg"></div>
        <svg class="sidebar-mountain-svg" viewBox="0 0 260 110" preserveAspectRatio="none">
            <defs>
                <linearGradient id="twilightGlow" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#ec4899" stop-opacity="0.3"/>
                    <stop offset="50%" stop-color="#8b5cf6" stop-opacity="0.2"/>
                    <stop offset="100%" stop-color="#07091a" stop-opacity="0.9"/>
                </linearGradient>
            </defs>
            <path d="M0 110 L0 60 L40 38 L85 65 L135 25 L190 70 L230 45 L260 62 L260 110 Z" fill="url(#twilightGlow)"/>
            <path d="M0 110 L0 75 L30 58 L65 80 L115 50 L165 85 L210 60 L245 78 L260 68 L260 110 Z" fill="#121844" opacity="0.85"/>
            <path d="M0 110 L0 90 L25 78 L55 95 L95 72 L140 98 L185 80 L220 95 L260 84 L260 110 Z" fill="#07091a"/>
            <polygon points="20,110 28,88 36,110" fill="#040612"/>
            <polygon points="45,110 52,82 59,110" fill="#040612"/>
            <polygon points="105,110 114,84 123,110" fill="#040612"/>
            <polygon points="170,110 178,86 186,110" fill="#040612"/>
            <polygon points="225,110 233,80 241,110" fill="#040612"/>
        </svg>

        <div class="sidebar-content">
            <!-- Brand with Left/Right Slide & Three-Dot Menu -->
            <div class="brand-box">
                <div style="display: flex; align-items: center; gap: 10px; flex: 1;">
                    <div class="brand-icon">✦</div>
                    <div>
                        <div class="brand-title">Raaj AI</div>
                        <div class="brand-sub">Voice Console</div>
                    </div>
                </div>
                <!-- Slide Collapse & Three Dot Option -->
                <div style="display: flex; align-items: center; gap: 4px; position: relative;">
                    <button class="sidebar-icon-btn" onclick="toggleSidebarSlide()" title="Slide Left / Collapse Sidebar (◀)">
                        ◀
                    </button>
                    <button class="sidebar-icon-btn" id="threeDotBtn" onclick="toggleSidebarMenu(event)" title="Options (⋮)">
                        ⋮
                    </button>
                    <!-- Three Dot Dropdown Menu -->
                    <div class="sidebar-dropdown-menu" id="sidebarMenu">
                        <div class="dropdown-item" onclick="toggleSidebarSlide()">
                            <span>◀</span>
                            <span>Slide Left / Collapse</span>
                        </div>
                        <div class="dropdown-item" onclick="openModal('voiceModal'); hideSidebarMenu()">
                            <span>🎙️</span>
                            <span>AI Voice & Chat</span>
                        </div>
                        <div class="dropdown-item" onclick="openModal('settingsModal'); hideSidebarMenu()">
                            <span>⚙️</span>
                            <span>Assistant Settings</span>
                        </div>
                        <div class="dropdown-item" onclick="openModal('notesModal'); hideSidebarMenu()">
                            <span>📝</span>
                            <span>Quick Notes</span>
                        </div>
                        <div class="dropdown-item" onclick="toggleAutoplaySwitch(); hideSidebarMenu()">
                            <span>🔊</span>
                            <span>Toggle Autoplay Voice</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Navigation Menu -->
            <nav class="nav-menu">
                <div class="nav-item active" onclick="switchNav('Dashboard', this)">
                    <span class="nav-icon">🏠</span>
                    <span>Home</span>
                </div>
                <div class="nav-item" onclick="openModal('voiceModal')">
                    <span class="nav-icon">🎙️</span>
                    <span>AI Voice & Chat</span>
                </div>
                <div class="nav-item" onclick="openModal('ytModal')">
                    <span class="nav-icon">🎬</span>
                    <span>YouTube Studio</span>
                </div>
                <div class="nav-item" onclick="openModal('weatherModal')">
                    <span class="nav-icon">⛅</span>
                    <span>Weather & World</span>
                </div>
                <div class="nav-item" onclick="openModal('wikiModal')">
                    <span class="nav-icon">📖</span>
                    <span>Wikipedia Hub</span>
                </div>
                <div class="nav-item" onclick="openModal('notesModal')">
                    <span class="nav-icon">📝</span>
                    <span>Smart Notes</span>
                </div>
                <div class="nav-item" onclick="openModal('waModal')">
                    <span class="nav-icon">💬</span>
                    <span>WhatsApp Portal</span>
                </div>
                <div class="nav-item" onclick="scrollToSection('utilitiesSection')">
                    <span class="nav-icon">🛠️</span>
                    <span>Tools & Fun</span>
                </div>
                <div class="nav-item" onclick="openModal('sysModal')">
                    <span class="nav-icon">🖥️</span>
                    <span>System Assistant</span>
                </div>
            </nav>

            <!-- Desktop Assistant Settings -->
            <div class="settings-section">
                <div class="settings-header">
                    <span>⚙️</span>
                    <span>Assistant Settings</span>
                </div>

                <div>
                    <div class="field-label">Voice Persona</div>
                    <select id="personaSelect" class="select-styled" onchange="syncPersona(this.value)">
                        <option value="Raaj AI" selected>Raaj AI</option>
                        <option value="Alexa Edition">Alexa Edition</option>
                        <option value="Jarvis Ultra">Jarvis Ultra</option>
                        <option value="Friday AI">Friday AI</option>
                    </select>
                </div>

                <div class="two-col">
                    <div>
                        <div class="field-label">Voice Accent / Language</div>
                        <select id="accentSelect" class="select-styled" onchange="syncLanguage(this.value)">
                            <option value="en-IN" selected>English (India)</option>
                            <option value="hi-IN">Hindi (हिंदी)</option>
                            <option value="or-IN">Odia (ଓଡ଼ିଆ)</option>
                            <option value="te-IN">Telugu (తెలుగు)</option>
                            <option value="en-US">English (US)</option>
                            <option value="en-GB">English (UK)</option>
                            <option value="en-AU">English (Australia)</option>
                        </select>
                    </div>
                    <div>
                        <div class="field-label">Speed</div>
                        <select id="speedSelect" class="select-styled" onchange="syncSpeed(this.value)">
                            <option value="1" selected>Normal</option>
                            <option value="0.85">Slow</option>
                        </select>
                    </div>
                </div>

                <div class="toggle-row">
                    <div class="toggle-switch" id="autoplayToggle" onclick="toggleAutoplaySwitch()">
                        <div class="toggle-thumb" id="autoplayThumb"></div>
                    </div>
                    <span class="toggle-label">Autoplay Voice Response</span>
                </div>
            </div>
        </div>
    </aside>

    <!-- ==========================================================================
         MAIN AREA: HEADER, HERO, CARDS, UTILITIES, PORTALS & TELEMETRY
         ========================================================================== -->
    <main class="main-area">

        <!-- Mobile Top Header Bar (Visible on Mobile <= 767px) -->
        <header class="mobile-header">
            <div class="mobile-header-left">
                <button class="hamburger-btn" onclick="openDrawer()" title="Open menu">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
                <div class="mobile-brand-box">
                    <div class="mobile-brand-icon">✦</div>
                    <div class="mobile-brand-title">Raaj AI</div>
                </div>
            </div>
            <div class="mobile-header-right">
                <div class="mobile-core-pill">
                    <div class="core-dot"></div>
                    <span>Ready</span>
                </div>
                <div class="mobile-notif-btn" onclick="showToast('Assistant Core is 100% operational.')">
                    🔔
                    <div class="notif-badge">1</div>
                </div>
            </div>
        </header>

        <!-- Desktop & Tablet Top Header Bar (Visible on >= 768px) -->
        <header class="top-header">
            <div class="welcome-box">
                <button class="sidebar-expand-btn" id="sidebarExpandBtn" onclick="toggleSidebarSlide()" title="Expand Sidebar (Slide Right ▶)">
                    ▶
                </button>
                <div class="welcome-hand">👋</div>
                <div>
                    <div class="welcome-title">Hello, Rajendra (Raaj)</div>
                    <div class="welcome-sub">Your Next-Gen Intelligent AI Assistant</div>
                </div>
            </div>
            <div class="header-right">
                <div class="core-ready-pill">
                    <div class="core-dot"></div>
                    <span>Core Ready</span>
                </div>
                <div class="notif-bell-btn" onclick="showToast('Assistant Core is 100% operational.')" title="System Notifications">
                    🔔
                    <div class="notif-badge">1</div>
                </div>
                <div class="notif-bell-btn" onclick="openModal('settingsModal')" title="Assistant Settings">
                    ⚙️
                </div>
                <a href="https://share.streamlit.io/" target="_blank" class="deploy-btn">
                    🚀 Deploy
                </a>
            </div>
        </header>

        <!-- Hero Voice Console Banner (Fully Responsive Across Mobile, Tablet & Desktop) -->
        <section class="hero-banner">
            <div class="planet-arc"></div>

            <!-- Left 3D Robot Avatar in Glowing Neon Ring -->
            <div class="robot-wrap">
                <div class="neon-ring-glow"></div>
                <img src="data:image/jpeg;base64,{ROBOT_B64}" class="robot-image" alt="Raaj AI Robot Avatar">
            </div>

            <!-- Center Stage -->
            <div class="hero-center">
                <div class="assistant-tag">🎙️ Next-Gen AI Assistant</div>
                <h1 class="hero-title">Raaj AI Voice Console</h1>
                <div class="hero-subtitle">Talk • Search • Create • Automate • Explore</div>

                <!-- Voice Status Badge -->
                <div class="voice-status-text" id="voiceStatusText">
                    <span id="voiceStatusDot">⚡</span>
                    <span id="voiceStatusLabel">Click to Speak or Type a Command</span>
                </div>

                <!-- Waveform & Mic Center -->
                <div class="waveform-box">
                    <div class="wave-bars" id="waveBarsLeft">
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                    </div>
                    <button class="center-mic-btn" id="mainMicBtn" onclick="toggleVoiceRecording()" title="Click to Speak with Microphone">
                        🎙️
                    </button>
                    <div class="wave-bars" id="waveBarsRight">
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                        <div class="wave-bar"></div>
                    </div>
                </div>

                <!-- Capsule Command Bar -->
                <div class="command-capsule">
                    <span class="capsule-mic-icon" onclick="toggleVoiceRecording()" title="Voice input">🎙️</span>
                    <input type="text" id="commandInput" class="capsule-input" placeholder="Click to Speak or Type a Command..." onkeydown="handleInputKey(event)">
                    <button class="capsule-send-btn" onclick="executeCommand()" title="Send command">➤</button>
                </div>
            </div>
        </section>

        <!-- Middle Quick Navigation 8 Cards (Desktop 8-col, Tablet 4-col, Mobile 2-col) -->
        <section class="quick-cards-grid">
            <div class="feature-card" onclick="openModal('voiceModal')">
                <div class="card-ico">🎙️</div>
                <div class="card-title">Voice & Chat</div>
                <div class="card-desc">Talk with Raaj AI</div>
            </div>
            <div class="feature-card" onclick="openModal('ytModal')">
                <div class="card-ico" style="color: #ef4444;">▶️</div>
                <div class="card-title">YouTube Studio</div>
                <div class="card-desc">Play, Search & Watch</div>
            </div>
            <div class="feature-card" onclick="openModal('weatherModal')">
                <div class="card-ico" style="color: #fbbf24;">⛅</div>
                <div class="card-title">Weather & World</div>
                <div class="card-desc">Live Weather & News</div>
            </div>
            <div class="feature-card" onclick="openModal('wikiModal')">
                <div class="card-ico" style="font-family: serif; font-weight: bold; color: #c084fc;">🆆</div>
                <div class="card-title">Wikipedia Hub</div>
                <div class="card-desc">Search Knowledge</div>
            </div>
            <div class="feature-card" onclick="openModal('notesModal')">
                <div class="card-ico" style="color: #f97316;">📝</div>
                <div class="card-title">Smart Notes</div>
                <div class="card-desc">Write & Save Ideas</div>
            </div>
            <div class="feature-card" onclick="openModal('waModal')">
                <div class="card-ico" style="color: #22c55e;">💬</div>
                <div class="card-title">WhatsApp Portal</div>
                <div class="card-desc">Send Messages</div>
            </div>
            <div class="feature-card" onclick="scrollToSection('utilitiesSection')">
                <div class="card-ico" style="color: #a855f7;">🛠️</div>
                <div class="card-title">Tools & Fun</div>
                <div class="card-desc">Math, Password, Dice</div>
            </div>
            <div class="feature-card" onclick="openModal('sysModal')">
                <div class="card-ico" style="color: #38bdf8;">🖥️</div>
                <div class="card-title">System Assistant</div>
                <div class="card-desc">Open Apps & More</div>
            </div>
        </section>

        <!-- Utilities, Mini-Tools & Fun Engine (Desktop 3-col, Tablet 2-col, Mobile 1-col) -->
        <section class="showcase-wrapper" id="utilitiesSection">
            <div class="showcase-header">
                <span>🚀</span>
                <span>Utilities, Mini-Tools & Fun Engine</span>
            </div>

            <div class="showcase-grid">
                <!-- Card 1: Instant Math Solver -->
                <div class="engine-card">
                    <div>
                        <div class="card-heading">
                            <span>🧮</span>
                            <span>Instant Math Solver</span>
                            <span style="font-size: 0.8rem; color: #38bdf8;">✦</span>
                        </div>
                        <div class="input-label">Arithmetic Expression</div>
                        <input type="text" id="mathInput" class="engine-input" value="15 * 84 + 120" onkeydown="if(event.key==='Enter') solveMath()">
                    </div>
                    <div>
                        <button class="btn-solve" onclick="solveMath()">
                            <span>🧮</span>
                            <span>Solve</span>
                        </button>
                        <div id="mathResult" style="font-size: 0.8rem; color: #38bdf8; margin-top: 10px; text-align: center; font-family: monospace;">Result: 1380</div>
                    </div>
                </div>

                <!-- Card 2: Password Generator -->
                <div class="engine-card">
                    <div>
                        <div class="card-heading">
                            <span>🔐</span>
                            <span>Password Generator</span>
                        </div>
                        <div class="slider-container">
                            <div class="slider-label-row">
                                <span>Password Length: <strong id="sliderValDisplay" style="color: #f472b6;">14</strong></span>
                            </div>
                            <input type="range" id="pwdSlider" class="range-slider" min="8" max="24" value="14" oninput="updateSliderVal(this.value)">
                            <div class="slider-scale">
                                <span>8</span>
                                <span>24</span>
                            </div>
                        </div>
                    </div>
                    <div>
                        <button class="btn-password" onclick="generatePassword()">
                            <span>🔧</span>
                            <span>Generate Password</span>
                        </button>
                        <div id="pwdResult" style="font-size: 0.84rem; color: #f472b6; margin-top: 10px; text-align: center; font-family: monospace;">Click Generate Password</div>
                    </div>
                </div>

                <!-- Card 3: Coin & Dice -->
                <div class="engine-card">
                    <div>
                        <div class="card-heading">
                            <span>🎲</span>
                            <span>Coin & Dice</span>
                        </div>
                        <div class="coin-dice-buttons">
                            <button class="btn-flip-coin" onclick="flipCoin()">
                                <span>🟡</span>
                                <span>Flip Coin</span>
                            </button>
                            <button class="btn-roll-dice" onclick="rollDice()">
                                <span>🎲</span>
                                <span>Roll Dice</span>
                            </button>
                        </div>
                    </div>
                    <div class="coin-dice-results">
                        <div class="coin-display-card">
                            <div class="coin-medal" id="coinIcon">🪙</div>
                            <div class="coin-text" id="coinText">Heads</div>
                        </div>
                        <div class="dice-display-card">
                            <div class="dice-cube" id="diceDisplay">⚅</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Quick Web Portals (Desktop 6-col, Tablet 3-col, Mobile 2-col) -->
        <section class="portals-section">
            <div class="portals-title">
                <span>🌐</span>
                <span>Quick Web Portals</span>
            </div>
            <div class="portals-grid">
                <a href="https://www.google.com" target="_blank" class="portal-btn">
                    <span>🔍</span> Google
                </a>
                <a href="https://www.youtube.com" target="_blank" class="portal-btn">
                    <span>▶️</span> YouTube
                </a>
                <a href="https://chatgpt.com" target="_blank" class="portal-btn">
                    <span>🤖</span> ChatGPT
                </a>
                <a href="https://github.com" target="_blank" class="portal-btn">
                    <span>🐙</span> GitHub
                </a>
                <a href="https://www.linkedin.com" target="_blank" class="portal-btn">
                    <span>💼</span> LinkedIn
                </a>
                <a href="https://mail.google.com" target="_blank" class="portal-btn">
                    <span>✉️</span> Gmail
                </a>
            </div>
        </section>

        <!-- Bottom Telemetry Status Bar (Desktop 4-col, Tablet 4-col, Mobile 2x2 grid) -->
        <footer class="bottom-bar">
            <div class="bar-metric">
                <div class="metric-ico-box" style="background: rgba(245, 158, 11, 0.15); color: #fbbf24;">⚡</div>
                <div>
                    <div class="metric-num" id="commandCountDisplay">0</div>
                    <div class="metric-tag">Commands Today</div>
                </div>
            </div>

            <div class="bar-metric">
                <div class="metric-ico-box" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8;">📄</div>
                <div>
                    <div class="metric-num" id="savedNotesDisplay">1</div>
                    <div class="metric-tag">Saved Notes</div>
                </div>
            </div>

            <div class="bar-metric">
                <div class="metric-ico-box" style="background: rgba(52, 211, 153, 0.15); color: #34d399;">
                    <div class="live-wave-equalizer">
                        <div class="equalizer-bar"></div>
                        <div class="equalizer-bar"></div>
                        <div class="equalizer-bar"></div>
                        <div class="equalizer-bar"></div>
                    </div>
                </div>
                <div>
                    <div class="metric-num" style="color: #34d399;">Core Ready</div>
                    <div class="metric-tag">Assistant Status</div>
                </div>
            </div>

            <div class="bar-metric">
                <div class="metric-ico-box" style="background: rgba(168, 85, 247, 0.15); color: #c084fc;">🕒</div>
                <div>
                    <div class="metric-num" id="sessionTimerDisplay" style="font-family: monospace;">00:00:00</div>
                    <div class="metric-tag">Session Duration</div>
                </div>
            </div>
        </footer>

    </main>
</div>


<!-- ==========================================================================
     FIXED BOTTOM MOBILE NAVIGATION (VISIBLE ON MOBILE ONLY)
     ========================================================================== -->
<nav class="bottom-mobile-nav">
    <div class="bnav-item active" onclick="switchNav('Dashboard', null)">
        <span class="bnav-icon">🏠</span>
        <span>Home</span>
    </div>
    <div class="bnav-item" onclick="scrollToSection('utilitiesSection')">
        <span class="bnav-icon">🛠️</span>
        <span>Tools</span>
    </div>
    <!-- Elevated Center Voice Action -->
    <div class="bnav-voice-btn" id="mobileVoiceFab" onclick="toggleVoiceRecording()" title="Speak Voice">
        🎙️
    </div>
    <div class="bnav-item" onclick="openModal('notesModal')">
        <span class="bnav-icon">📝</span>
        <span>Notes</span>
    </div>
    <div class="bnav-item" onclick="openDrawer()">
        <span class="bnav-icon">☰</span>
        <span>More</span>
    </div>
</nav>


<!-- ==========================================================================
     INTERACTIVE MODALS
     ========================================================================== -->

<!-- 1. Voice & Chat Modal -->
<div class="modal-overlay" id="voiceModal">
    <div class="modal-box">
        <button class="modal-close" onclick="closeModal('voiceModal')">✕</button>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; flex-wrap: wrap; gap: 8px;">
            <h3 style="margin: 0; color: #38bdf8; display: flex; align-items: center; gap: 8px; font-size: 1.15rem;">
                <span>🎙️</span>
                <span>Live Voice & Chat Stream</span>
            </h3>
            <span style="font-size: 0.75rem; color: #34d399; background: rgba(52, 211, 153, 0.12); border: 1px solid rgba(52, 211, 153, 0.35); padding: 3px 10px; border-radius: 999px;">
                Voice Core Active
            </span>
        </div>

        <div id="listeningBanner" style="display: none; padding: 10px 14px; background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.5); border-radius: 10px; color: #fca5a5; font-size: 0.88rem; margin-bottom: 12px; align-items: center; gap: 10px;">
            <span style="animation: micPulseGlow 0.8s infinite alternate; font-size: 1.1rem;">🔴</span>
            <strong>Listening to your microphone... Speak clearly!</strong>
        </div>

        <div id="chatTimeline" style="max-height: 380px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; padding-right: 4px;">
            <div style="background: rgba(22, 28, 66, 0.85); border: 1px solid rgba(139, 92, 246, 0.3); padding: 14px 18px; border-radius: 14px; font-size: 0.92rem; line-height: 1.5;">
                <strong style="color: #818cf8;">🤖 Raaj AI:</strong> Welcome Rajendra! I am your AI assistant. Tap <strong>🎙️ Speak Voice</strong> or type below to command me in English, Hindi, Odia, or Telugu!
            </div>
        </div>

        <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
            <button id="modalVoiceBtn" class="btn-voice-record" onclick="toggleModalVoice()" title="Click to Speak with Microphone">
                <span id="modalVoiceIcon">🎙️</span>
                <span id="modalVoiceLabel">Speak Voice</span>
            </button>
            <input type="text" id="modalChatInput" class="engine-input" placeholder="Speak or type a command..." style="margin-bottom: 0; flex: 1; min-width: 140px;" onkeydown="if(event.key==='Enter') sendModalChat()">
            <button class="btn-solve" style="width: 90px; height: 42px;" onclick="sendModalChat()">Send ➤</button>
        </div>

        <div style="display: flex; gap: 6px; margin-top: 12px; flex-wrap: wrap;">
            <span style="font-size: 0.74rem; color: #94a3b8; align-self: center;">Try:</span>
            <button class="select-styled" style="width: auto; padding: 4px 10px; font-size: 0.75rem;" onclick="setAndSendModal('open youtube')">▶️ open youtube</button>
            <button class="select-styled" style="width: auto; padding: 4px 10px; font-size: 0.75rem;" onclick="setAndSendModal('tell about you')">🤖 tell about you</button>
            <button class="select-styled" style="width: auto; padding: 4px 10px; font-size: 0.75rem;" onclick="setAndSendModal('weather Hyderabad')">⛅ weather Hyderabad</button>
            <button class="select-styled" style="width: auto; padding: 4px 10px; font-size: 0.75rem;" onclick="setAndSendModal('play Nazar Lagi')">🎵 play Nazar Lagi</button>
            <button class="select-styled" style="width: auto; padding: 4px 10px; font-size: 0.75rem;" onclick="setAndSendModal('calculate 15 * 84 + 120')">🧮 calculate 15 * 84</button>
        </div>
    </div>
</div>

<!-- 2. YouTube Modal -->
<div class="modal-overlay" id="ytModal">
    <div class="modal-box">
        <button class="modal-close" onclick="closeModal('ytModal')">✕</button>
        <h3 style="margin-bottom: 14px; color: #ef4444; font-size: 1.2rem;">🎬 YouTube Studio</h3>
        <input type="text" id="ytQuery" class="engine-input" placeholder="Search track, artist or video..." value="Alan Walker Faded">
        <button class="btn-solve" onclick="searchYouTube()" style="background: linear-gradient(90deg, #ef4444, #dc2626);">Search on YouTube</button>
        <div style="margin-top: 18px;">
            <p style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 8px;">Curated Focus Playlists:</p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                <button class="engine-input" onclick="window.open('https://www.youtube.com/results?search_query=lofi+hip+hop+study','_blank')">☕ Lofi Study Beats</button>
                <button class="engine-input" onclick="window.open('https://www.youtube.com/results?search_query=synthwave+coding+focus','_blank')">⚡ Coding Synthwave</button>
                <button class="engine-input" onclick="window.open('https://www.youtube.com/results?search_query=bollywood+acoustic+unplugged','_blank')">🔥 Bollywood Hits</button>
                <button class="engine-input" onclick="window.open('https://www.youtube.com/results?search_query=relaxing+rain+sounds','_blank')">🌧️ Rain Relaxation</button>
            </div>
        </div>
    </div>
</div>

<!-- 3. Weather Modal -->
<div class="modal-overlay" id="weatherModal">
    <div class="modal-box">
        <button class="modal-close" onclick="closeModal('weatherModal')">✕</button>
        <h3 style="margin-bottom: 14px; color: #fbbf24; font-size: 1.2rem;">⛅ Live Weather Telemetry</h3>
        <input type="text" id="weatherCity" class="engine-input" placeholder="Enter city (e.g. Hyderabad, Delhi, London, Tokyo)" value="Hyderabad">
        <button class="btn-solve" onclick="fetchLiveWeather()" style="background: linear-gradient(90deg, #f59e0b, #d97706); color: #1e1b4b;">Check Weather</button>
        <div id="weatherDisplay" style="margin-top: 16px; padding: 14px; background: rgba(14, 18, 48, 0.7); border-radius: 12px; font-size: 0.9rem; line-height: 1.6;">
            ⛅ Click above to get live weather telemetry.
        </div>
    </div>
</div>

<!-- 4. Wikipedia Modal -->
<div class="modal-overlay" id="wikiModal">
    <div class="modal-box">
        <button class="modal-close" onclick="closeModal('wikiModal')">✕</button>
        <h3 style="margin-bottom: 14px; color: #c084fc; font-size: 1.2rem;">📖 Wikipedia Knowledge Hub</h3>
        <input type="text" id="wikiQuery" class="engine-input" placeholder="Search personality or topic..." value="Artificial Intelligence">
        <button class="btn-solve" onclick="fetchWiki()" style="background: linear-gradient(90deg, #a855f7, #6366f1);">Search Wikipedia</button>
        <div id="wikiDisplay" style="margin-top: 16px; padding: 14px; background: rgba(14, 18, 48, 0.7); border-radius: 12px; font-size: 0.9rem; line-height: 1.6;">
            Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans.
        </div>
    </div>
</div>

<!-- 5. Smart Notes Modal -->
<div class="modal-overlay" id="notesModal">
    <div class="modal-box">
        <button class="modal-close" onclick="closeModal('notesModal')">✕</button>
        <h3 style="margin-bottom: 14px; color: #f97316; font-size: 1.2rem;">📝 Smart Notes</h3>
        <div style="display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap;">
            <input type="text" id="newNoteText" class="engine-input" placeholder="Add a new quick note..." style="margin-bottom: 0; flex: 1; min-width: 160px;">
            <button class="btn-solve" style="width: 90px; background: linear-gradient(90deg, #f97316, #ea580c);" onclick="addNote()">Add</button>
        </div>
        <div id="notesList" style="display: flex; flex-direction: column; gap: 8px; max-height: 250px; overflow-y: auto;">
            <div style="padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; font-size: 0.88rem;">📌 Explore Raaj AI Voice Console: Try 'weather Hyderabad' or 'calculate 25 * 18'</div>
        </div>
    </div>
</div>

<!-- 6. WhatsApp Modal -->
<div class="modal-overlay" id="waModal">
    <div class="modal-box">
        <button class="modal-close" onclick="closeModal('waModal')">✕</button>
        <h3 style="margin-bottom: 14px; color: #22c55e; font-size: 1.2rem;">💬 WhatsApp Direct Messenger</h3>
        <input type="text" id="waPhone" class="engine-input" placeholder="Phone with country code (e.g. +919876543210)" value="+91">
        <textarea id="waMsg" class="engine-input" rows="3" placeholder="Message content...">Hello from Raaj AI Assistant!</textarea>
        <button class="btn-solve" style="background: linear-gradient(90deg, #22c55e, #16a34a);" onclick="generateWhatsApp()">Open WhatsApp Chat</button>
    </div>
</div>

<!-- 7. System Assistant Modal -->
<div class="modal-overlay" id="sysModal">
    <div class="modal-box">
        <button class="modal-close" onclick="closeModal('sysModal')">✕</button>
        <h3 style="margin-bottom: 14px; color: #38bdf8; font-size: 1.2rem;">🖥️ System Assistant & Portals</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <button class="engine-input" onclick="window.open('https://www.youtube.com','_blank')">▶️ YouTube</button>
            <button class="engine-input" onclick="window.open('https://www.google.com','_blank')">🔍 Google</button>
            <button class="engine-input" onclick="window.open('https://mail.google.com','_blank')">✉️ Gmail</button>
            <button class="engine-input" onclick="window.open('https://github.com','_blank')">🐙 GitHub</button>
            <button class="engine-input" onclick="window.open('https://www.linkedin.com','_blank')">💼 LinkedIn</button>
            <button class="engine-input" onclick="window.open('https://chatgpt.com','_blank')">🤖 ChatGPT</button>
        </div>
    </div>
</div>

<!-- 8. Assistant Settings Modal -->
<div class="modal-overlay" id="settingsModal">
    <div class="modal-box" style="max-width: 480px;">
        <button class="modal-close" onclick="closeModal('settingsModal')">✕</button>
        <h3 style="margin-bottom: 16px; color: #c084fc; font-size: 1.2rem;">⚙️ Assistant Settings</h3>
        
        <div style="display: flex; flex-direction: column; gap: 14px;">
            <div>
                <div class="field-label">Voice Persona</div>
                <select id="modalPersonaSelect" class="select-styled" onchange="syncPersona(this.value)">
                    <option value="Raaj AI" selected>Raaj AI</option>
                    <option value="Alexa Edition">Alexa Edition</option>
                    <option value="Jarvis Ultra">Jarvis Ultra</option>
                    <option value="Friday AI">Friday AI</option>
                </select>
            </div>

            <div>
                <div class="field-label">Voice Accent / Language</div>
                <select id="modalAccentSelect" class="select-styled" onchange="syncLanguage(this.value)">
                    <option value="en-IN" selected>English (India)</option>
                    <option value="hi-IN">Hindi (हिंदी)</option>
                    <option value="or-IN">Odia (ଓଡ଼ିଆ)</option>
                    <option value="te-IN">Telugu (తెలుగు)</option>
                    <option value="en-US">English (US)</option>
                    <option value="en-GB">English (UK)</option>
                    <option value="en-AU">English (Australia)</option>
                </select>
            </div>

            <div class="two-col">
                <div>
                    <div class="field-label">Speed</div>
                    <select id="modalSpeedSelect" class="select-styled" onchange="syncSpeed(this.value)">
                        <option value="1" selected>Normal</option>
                        <option value="0.85">Slow</option>
                    </select>
                </div>
                <div>
                    <div class="field-label">Autoplay Voice</div>
                    <select id="modalAutoplaySelect" class="select-styled" onchange="syncAutoplay(this.value)">
                        <option value="true" selected>Enabled</option>
                        <option value="false">Muted</option>
                    </select>
                </div>
            </div>
            
            <button class="btn-solve" onclick="closeModal('settingsModal')" style="margin-top: 10px;">Save & Close</button>
        </div>
    </div>
</div>


<!-- ==========================================================================
     CLIENT JAVASCRIPT: MULTILINGUAL ENGINE, VOICE RECOGNITION, STATE & LOGIC
     ========================================================================== -->
<script>
// State
let commandsCount = 0;
let savedNotesCount = 1;
let sessionSeconds = 0;
let autoplayVoice = true;
let isRecording = false;
let recognition = null;
let currentVoiceState = 'idle'; // 'idle' | 'listening' | 'processing' | 'speaking'

// Live Session Duration Timer
setInterval(() => {{
    sessionSeconds++;
    const h = String(Math.floor(sessionSeconds / 3600)).padStart(2, '0');
    const m = String(Math.floor((sessionSeconds % 3600) / 60)).padStart(2, '0');
    const s = String(sessionSeconds % 60).padStart(2, '0');
    const el = document.getElementById('sessionTimerDisplay');
    if (el) el.textContent = `${{h}}:${{m}}:${{s}}`;
}}, 1000);

function incCommand() {{
    commandsCount++;
    const el = document.getElementById('commandCountDisplay');
    if (el) el.textContent = commandsCount;
}}

// Toast Notification System
function showToast(msg, icon = '✦') {{
    const container = document.getElementById('toastContainer');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.innerHTML = `<span>${{icon}}</span> <span>${{msg}}</span>`;
    container.appendChild(toast);
    setTimeout(() => {{
        if (toast && toast.parentNode) toast.parentNode.removeChild(toast);
    }}, 3000);
}}

// Sidebar Left/Right Slide & 3-Dot Options Control
let sidebarCollapsed = false;

function toggleSidebarSlide() {{
    const sidebar = document.getElementById('desktopSidebar');
    const handle = document.getElementById('sidebarSlideHandle');
    sidebarCollapsed = !sidebarCollapsed;
    
    if (sidebar) {{
        if (sidebarCollapsed) {{
            sidebar.classList.add('collapsed');
            if (handle) handle.innerHTML = '▶';
            showToast('Sidebar collapsed (slide left)', '◀');
        }} else {{
            sidebar.classList.remove('collapsed');
            if (handle) handle.innerHTML = '◀';
            showToast('Sidebar expanded (slide right)', '▶');
        }}
    }}
    hideSidebarMenu();
}}

function toggleSidebarMenu(e) {{
    if (e) e.stopPropagation();
    const menu = document.getElementById('sidebarMenu');
    if (menu) {{
        menu.classList.toggle('show');
    }}
}}

function hideSidebarMenu() {{
    const menu = document.getElementById('sidebarMenu');
    if (menu) menu.classList.remove('show');
}}

// Close dropdown menu on outside click
document.addEventListener('click', (e) => {{
    const menu = document.getElementById('sidebarMenu');
    if (menu && !menu.contains(e.target)) {{
        menu.classList.remove('show');
    }}
}});

// Mobile Drawer Control
function openDrawer() {{
    const drawer = document.getElementById('mobileDrawer');
    const backdrop = document.getElementById('drawerBackdrop');
    if (drawer) drawer.classList.add('open');
    if (backdrop) backdrop.classList.add('open');
}}

function closeDrawer() {{
    const drawer = document.getElementById('mobileDrawer');
    const backdrop = document.getElementById('drawerBackdrop');
    if (drawer) drawer.classList.remove('open');
    if (backdrop) backdrop.classList.remove('open');
}}

// Scroll to anchor helper
function scrollToSection(id) {{
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({{ behavior: 'smooth' }});
}}

// Voice State Visualizer Machine
function setVoiceState(state) {{
    currentVoiceState = state;
    const mainBtn = document.getElementById('mainMicBtn');
    const mobileFab = document.getElementById('mobileVoiceFab');
    const statusLabel = document.getElementById('voiceStatusLabel');
    const statusDot = document.getElementById('voiceStatusDot');
    const modalBtn = document.getElementById('modalVoiceBtn');
    const modalLabel = document.getElementById('modalVoiceLabel');
    const banner = document.getElementById('listeningBanner');
    const waveLeft = document.getElementById('waveBarsLeft');
    const waveRight = document.getElementById('waveBarsRight');

    if (state === 'listening') {{
        if (mainBtn) mainBtn.classList.add('listening');
        if (mobileFab) mobileFab.classList.add('listening');
        if (modalBtn) modalBtn.classList.add('recording');
        if (statusLabel) statusLabel.textContent = 'Listening... Speak your command now';
        if (statusDot) statusDot.textContent = '🔴';
        if (modalLabel) modalLabel.textContent = 'Listening...';
        if (banner) banner.style.display = 'flex';
        if (waveLeft) waveLeft.style.opacity = '1';
        if (waveRight) waveRight.style.opacity = '1';
    }} else if (state === 'processing') {{
        if (mainBtn) mainBtn.classList.remove('listening');
        if (mobileFab) mobileFab.classList.remove('listening');
        if (modalBtn) modalBtn.classList.remove('recording');
        if (statusLabel) statusLabel.textContent = 'Thinking... Processing command';
        if (statusDot) statusDot.textContent = '⚡';
        if (modalLabel) modalLabel.textContent = 'Thinking...';
        if (banner) banner.style.display = 'none';
    }} else if (state === 'speaking') {{
        if (mainBtn) mainBtn.classList.remove('listening');
        if (mobileFab) mobileFab.classList.remove('listening');
        if (modalBtn) modalBtn.classList.remove('recording');
        if (statusLabel) statusLabel.textContent = 'Raaj AI is speaking...';
        if (statusDot) statusDot.textContent = '🔊';
        if (modalLabel) modalLabel.textContent = 'Speaking...';
        if (banner) banner.style.display = 'none';
    }} else {{
        // idle
        if (mainBtn) mainBtn.classList.remove('listening');
        if (mobileFab) mobileFab.classList.remove('listening');
        if (modalBtn) modalBtn.classList.remove('recording');
        if (statusLabel) statusLabel.textContent = 'Click to Speak or Type a Command';
        if (statusDot) statusDot.textContent = '⚡';
        if (modalLabel) modalLabel.textContent = 'Speak Voice';
        if (banner) banner.style.display = 'none';
    }}
}}

// ==========================================================================
// MULTILINGUAL LOCALIZATION ENGINE (Hindi, Odia, Telugu, English)
// ==========================================================================
const I18N = {{
    'en-IN': {{
        langCode: 'en-IN',
        greeting: 'Hello Rajendra! Voice language set to Indian English.',
        welcomeText: 'Welcome Rajendra! I am listening. Speak or type any command!',
        openSite: (name) => `🚀 Opening <strong>${{name}}</strong> in a new tab.`,
        openSiteSpoken: (name) => `Opening ${{name}}`,
        openYt: `🚀 Opening <strong>YouTube</strong> in a new tab.`,
        openYtSpoken: `Opening YouTube`,
        playMusic: (song) => `▶️ Playing / Searching YouTube for: <strong>"${{escapeHtml(song)}}"</strong>`,
        playMusicSpoken: (song) => `Playing ${{song}} on YouTube`,
        weatherSpoken: (city, desc, temp) => `The weather in ${{city}} is ${{desc}} with a temperature of ${{temp}} degrees celsius.`,
        mathResultSpoken: (expr, res) => `The result of ${{expr}} is ${{res}}`,
        noteSavedSpoken: `Note saved successfully.`,
        timeSpoken: (t) => `The current time is ${{t}}`,
        dateSpoken: (d) => `Today is ${{d}}`,
        coinSpoken: (pick) => `It is ${{pick}}!`,
        diceSpoken: (num) => `You rolled a ${{num}}!`,
        pwdGenSpoken: `A secure password has been generated and copied to your clipboard.`,
        searchSpoken: (q) => `Searching Google for ${{q}}`,
        bioText: `I am Raaj AI, your Next-Gen Voice and Cloud Assistant, created by Rajendra (Raaj).`,
        bioGreeting: `👋 <strong>I am Raaj AI</strong>, your Next-Gen AI Voice & Cloud Assistant built for <strong>Rajendra (Raaj)</strong>!`,
        jokes: [
            "Why do programmers prefer dark mode? Because light attracts bugs! 🪲",
            "Why did the Python developer need glasses? Because they couldn't C#! 🐍👓",
            "There are 10 types of people: those who understand binary, and those who don't.",
            "A SQL query walks into a bar, walks up to two tables and asks: Can I join you? 🍺",
            "Why was the JavaScript developer sad? Because they didn't Node how to Express themselves!"
        ]
    }},
    'hi-IN': {{
        langCode: 'hi-IN',
        greeting: 'नमस्ते राजेंद्र! भाषा हिंदी में सेट कर दी गई है। अब मैं आपसे हिंदी में बात करूँगा।',
        welcomeText: 'नमस्ते राजेंद्र! मैं आपकी बात सुन रहा हूँ। कृपया कोई भी कमांड बोलें या टाइप करें!',
        openSite: (name) => `🚀 <strong>${{name}}</strong> एक नए टैब में खोला जा रहा है।`,
        openSiteSpoken: (name) => `${{name}} खोला जा रहा है`,
        openYt: `🚀 <strong>यूट्यूब</strong> एक नए टैब में खोला जा रहा है।`,
        openYtSpoken: `यूट्यूब खोला जा रहा है`,
        playMusic: (song) => `▶️ यूट्यूब पर <strong>"${{escapeHtml(song)}}"</strong> बजाया जा रहा है...`,
        playMusicSpoken: (song) => `यूट्यूब पर ${{song}} बजाया जा रहा है`,
        weatherSpoken: (city, desc, temp) => `${{city}} में मौसम ${{desc}} है और तापमान ${{temp}} डिग्री सेल्सियस है।`,
        mathResultSpoken: (expr, res) => `${{expr}} का परिणाम ${{res}} है`,
        noteSavedSpoken: `नोट सफलतापूर्वक सहेज लिया गया है।`,
        timeSpoken: (t) => `वर्तमान समय ${{t}} है।`,
        dateSpoken: (d) => `आज ${{d}} है।`,
        coinSpoken: (pick) => `सिक्के का परिणाम ${{pick === 'Heads' ? 'हेड्स यानी चित' : 'टेल्स यानी पट'}} आया है!`,
        diceSpoken: (num) => `पासे पर अंक ${{num}} आया है!`,
        pwdGenSpoken: `एक सुरक्षित पासवर्ड जनरेट हो गया है और क्लिपबोर्ड पर कॉपी कर दिया गया है।`,
        searchSpoken: (q) => `${{q}} के लिए गूगल पर खोजा जा रहा है`,
        bioText: `नमस्ते राजेंद्र! मैं आपका राज एआई वॉयस असिस्टेंट हूँ। मैं गाने बजा सकता हूँ, मौसम बता सकता हूँ और आपके सवालों के जवाब दे सकता हूँ।`,
        bioGreeting: `👋 <strong>नमस्ते राजेंद्र! मैं राज एआई हूँ।</strong> आपका नेक्स्ट-जेन वॉयस और क्लाउड असिस्टेंट!`,
        jokes: [
            "अध्यापक: बताओ न्यूटन का चौथा नियम क्या है? छात्र: परीक्षा के समय किताबें अपने आप बंद हो जाती हैं! 😄",
            "सोनू: यार, मेरा कंप्यूटर बार-बार हैंग हो जाता है! मोनू: पंखा चालू कर दे, ठंड लगेगी तो ठीक चलेगा! 😂",
            "प्रोग्रामर की पत्नी: बाज़ार से एक ब्रेड ले आओ, अगर अंडे मिलें तो 10 ले आना। प्रोग्रामर 10 ब्रेड ले आया क्योंकि अंडे मिल गए थे! 🍞",
            "डॉक्टर: आपको आराम की सख्त ज़रूरत है। मरीज़: डॉक्टर साहब, कोई ऐसा ऐप बता दीजिए जो मेरे बदले आराम कर सके! 📱"
        ]
    }},
    'or-IN': {{
        langCode: 'or-IN',
        greeting: 'ନମସ୍କାର ରାଜେନ୍ଦ୍ର! ଭାଷା ଓଡ଼ିଆରେ ସେଟ୍ ହୋଇଛି। ଏବେ ମୁଁ ଆପଣଙ୍କ ସହିତ ଓଡ଼ିଆରେ କଥା ହେବି।',
        welcomeText: 'ନମସ୍କାର ରାଜେନ୍ଦ୍ର! ମୁଁ ଶୁଣୁଛି। ଦୟାକରି କୌଣସି କମାଣ୍ଡ କୁହନ୍ତୁ କିମ୍ବା ଟାଇପ୍ କରନ୍ତୁ!',
        openSite: (name) => `🚀 <strong>${{name}}</strong> ଏକ ନୂଆ ଟ୍ୟାବ୍‌ରେ ଖୋଲାଯାଉଛି।`,
        openSiteSpoken: (name) => `${{name}} ଖୋଲାଯାଉଛି`,
        openYt: `🚀 <strong>ୟୁଟ୍ୟୁବ୍</strong> ଏକ ନୂଆ ଟ୍ୟାବ୍‌ରେ ଖୋଲାଯାଉଛି।`,
        openYtSpoken: `ୟୁଟ୍ୟୁବ୍ ଖୋଲାଯାଉଛି`,
        playMusic: (song) => `▶️ ୟୁଟ୍ୟୁବ୍‌ରେ <strong>"${{escapeHtml(song)}}"</strong> ବଜାଯାଉଛି...`,
        playMusicSpoken: (song) => `ୟୁଟ୍ୟୁବ୍‌ରେ ${{song}} ବଜାଯାଉଛି`,
        weatherSpoken: (city, desc, temp) => `${{city}} ରେ ପାଣିପାଗ ${{desc}} ଅଟେ ଏବଂ ତାପମାତ୍ରା ${{temp}} ଡିଗ୍ରୀ ସେଲସିୟସ୍ ଅଟେ।`,
        mathResultSpoken: (expr, res) => `${{expr}} ର ଫଳାଫଳ ${{res}} ଅଟେ`,
        noteSavedSpoken: `ନୋଟ୍ ସଫଳତାର ସହିତ ସାଇତି ରଖାଗଲା।`,
        timeSpoken: (t) => `ବର୍ତ୍ତମାନ ସମୟ ${{t}} ଅଟେ।`,
        dateSpoken: (d) => `ଆଜି ${{d}} ଅଟେ।`,
        coinSpoken: (pick) => `ଫଳାଫଳ ${{pick === 'Heads' ? 'ହେଡ୍ସ' : 'ଟେଲ୍ସ'}} ଆସିଛି!`,
        diceSpoken: (num) => `ଡାଇସ୍ ର ଫଳାଫଳ ${{num}} ଆସିଛି!`,
        pwdGenSpoken: `ଏକ ସୁରକ୍ଷିତ ପାସୱାର୍ଡ ତିଆରି ହୋଇଛି ଏବଂ କ୍ଲିପବୋର୍ଡରେ କପି ହୋଇଛି।`,
        searchSpoken: (q) => `${{q}} ପାଇଁ ଗୁଗଲ୍‌ରେ ଖୋଜାଯାଉଛି`,
        bioText: `ନମସ୍କାର ରାଜେନ୍ଦ୍ର! ମୁଁ ଆପଣଙ୍କର ରାଜ ଏଆଇ ସହାୟକ ଅଟେ। ମୁଁ ଗୀତ ବଜାଇ ପାରିବି, ପାଣିପାଗ କହିପାରିବି ଏବଂ ପ୍ରଶ୍ନର ଉତ୍ତର ଦେଇପାରିବି।`,
        bioGreeting: `👋 <strong>ନମସ୍କାର ରାଜେନ୍ଦ୍ର! ମୁଁ ରାଜ ଏଆଇ।</strong> ଆପଣଙ୍କର ବୁଦ୍ଧିମାନ ଭଏସ୍ ସହାୟକ!`,
        jokes: [
            "ଶିକ୍ଷକ: ପୃଥିବୀ କାହିଁକି ଘୁରୁଛି? ଛାତ୍ର: ଆଜ୍ଞା, କାଲି ତା'ର ପରୀକ୍ଷା ଅଛି ବୋଧେ ସେଥିପାଇଁ ମୁଣ୍ଡ ଘୁରୁଛି! 😄",
            "ଗୋପାଳ: ମୋ କମ୍ପ୍ୟୁଟର ବହୁତ ଗରମ ହୋଇଯାଉଛି! ହରି: ଆରେ ତାକୁ ଟିକେ ଥଣ୍ଡା ପାଣି ପିଆଇ ଦିଅ! 😂",
            "ଡାକ୍ତର: ଦିନକୁ ଅତିକମରେ ଆଠ ଘଣ୍ଟା ଶୁଅନ୍ତୁ। ରୋଗୀ: ମୁଁ ତ ଅଫିସ୍‌ରେ ଛଅ ଘଣ୍ଟା ଶୋଇଯାଏ, ଆଉ ଦୁଇ ଘଣ୍ଟା ଘରେ ଶୋଇବି! 😴"
        ]
    }},
    'te-IN': {{
        langCode: 'te-IN',
        greeting: 'నమస్కారం రాజేంద్ర! భాష తెలుగుగా మార్చబడింది. ఇకపై నేను మీతో తెలుగులోనే మాట్లాడతాను.',
        welcomeText: 'నమస్కారం రాజేంద్ర! నేను వింటున్నాను. దయచేసి ఏదైనా కమాండ్ మాట్లాడండి లేదా టైప్ చేయండి!',
        openSite: (name) => `🚀 <strong>${{name}}</strong> కొత్త ట్యాబ్‌లో ఓపెన్ చేయబడుతోంది.`,
        openSiteSpoken: (name) => `${{name}} ఓపెన్ చేయబడుతోంది`,
        openYt: `🚀 <strong>యూట్యూబ్</strong> కొత్త ట్యాబ్‌లో ఓపెన్ చేయబడుతోంది.`,
        openYtSpoken: `యూట్యూబ్ ఓపెన్ చేయబడుతోంది`,
        playMusic: (song) => `▶️ యూట్యూబ్‌లో <strong>"${{escapeHtml(song)}}"</strong> ప్లే చేయబడుతోంది...`,
        playMusicSpoken: (song) => `యూట్యూబ్‌లో ${{song}} ప్లే చేయబడుతోంది`,
        weatherSpoken: (city, desc, temp) => `${{city}}లో వాతావరణం ${{desc}} మరియు ఉష్ణోగ్రత ${{temp}} డిగ్రీల సెల్సియస్.`,
        mathResultSpoken: (expr, res) => `${{expr}} యొక్క ఫలితం ${{res}}`,
        noteSavedSpoken: `గమనిక విజయవంతంగా సేవ్ చేయబడింది.`,
        timeSpoken: (t) => `ప్రస్తుత సమయం ${{t}}.`,
        dateSpoken: (d) => `ఈ రోజు ${{d}}.`,
        coinSpoken: (pick) => `టాస్ ఫలితం ${{pick === 'Heads' ? 'హెడ్స్' : 'టెయిల్స్'}} వచ్చింది!`,
        diceSpoken: (num) => `డైస్ సంఖ్య ${{num}} వచ్చింది!`,
        pwdGenSpoken: `సురక్షితమైన పాస్‌వర్డ్ రూపొందించబడింది మరియు క్లిప్‌బోర్డ్‌కు కాపీ చేయబడింది.`,
        searchSpoken: (q) => `${{q}} కోసం గూగుల్‌లో శోధించబడుతోంది`,
        bioText: `నమస్కారం రాజేంద్ర! నేను మీ రాజ్ AI అసిస్టెంట్‌ని. నేను యూట్యూబ్‌లో పాటలు ప్లే చేయగలను, వాతావరణ సమాచారం అందించగలను.`,
        bioGreeting: `👋 <strong>నమస్కారం రాజేంద్ర! నేను రాజ్ AI ని.</strong> మీ నెక్స్ట్-జెన్ AI వాయిస్ అసిస్టెంట్!`,
        jokes: [
            "టీచర్: భూమి గుండ్రంగా ఎందుకు తిరుగుతుంది? స్టూడెంట్: పరీక్షల భయంతో తలతిరిగి తిరుగుతోంది సార్! 😄",
            "స్నేహితుడు 1: నా కంప్యూటర్ పని చేయడం లేదు రా! స్నేహితుడు 2: కాస్త టీ తాగించు, యాక్టివ్ అవుతుంది! 😂",
            "డాక్టర్: రోజూ వ్యాయామం చేస్తున్నారా? రోగి: అవును డాక్టర్, రోజూ సోషల్ మీడియాలో కిందకి పైకి వేలితో స్క్రోల్ చేస్తున్నా! 📱"
        ]
    }}
}};

function getActiveLang() {{
    const el = document.getElementById('accentSelect');
    return el ? el.value : 'en-IN';
}}

function getI18n() {{
    const lang = getActiveLang();
    return I18N[lang] || I18N['en-IN'];
}}

// Settings Synchronizer between Sidebar, Drawer and Modal
function syncPersona(val) {{
    const selects = ['personaSelect', 'drawerPersonaSelect', 'modalPersonaSelect'];
    selects.forEach(id => {{
        const el = document.getElementById(id);
        if (el) el.value = val;
    }});
    showToast(`Voice Persona changed to ${{val}}`);
}}

function syncLanguage(val) {{
    const selects = ['accentSelect', 'drawerAccentSelect', 'modalAccentSelect'];
    selects.forEach(id => {{
        const el = document.getElementById(id);
        if (el) el.value = val;
    }});
    if (recognition) {{
        recognition.lang = (val === 'or-IN') ? 'hi-IN' : val;
    }}
    const i18n = getI18n();
    const g = i18n.greeting;

    const chatBox = document.getElementById('chatTimeline');
    if (chatBox) {{
        chatBox.innerHTML += `
            <div style="background: rgba(139, 92, 246, 0.15); border: 1px dashed rgba(168, 85, 247, 0.4); color: #c084fc; padding: 10px 14px; border-radius: 12px; font-size: 0.86rem; text-align: center; margin: 6px 0;">
                🌐 <strong>Assistant Language:</strong> ${{g}}
            </div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    }}
    showToast(`Language: ${{val}}`);
    speak(g, val);
}}

function syncSpeed(val) {{
    const selects = ['speedSelect', 'drawerSpeedSelect', 'modalSpeedSelect'];
    selects.forEach(id => {{
        const el = document.getElementById(id);
        if (el) el.value = val;
    }});
    showToast(`Speed set to ${{val === '1' ? 'Normal' : 'Slow'}}`);
}}

function syncAutoplay(val) {{
    autoplayVoice = (val === 'true' || val === true);
    const selects = ['drawerAutoplaySelect', 'modalAutoplaySelect'];
    selects.forEach(id => {{
        const el = document.getElementById(id);
        if (el) el.value = String(autoplayVoice);
    }});
    const thumb = document.getElementById('autoplayThumb');
    const toggle = document.getElementById('autoplayToggle');
    if (toggle) toggle.style.background = autoplayVoice ? '#8b5cf6' : '#475569';
    if (thumb) {{
        thumb.style.right = autoplayVoice ? '2px' : 'auto';
        thumb.style.left = autoplayVoice ? 'auto' : '2px';
    }}
    showToast(`Autoplay ${{autoplayVoice ? 'Enabled' : 'Disabled'}}`);
}}

function toggleAutoplaySwitch() {{
    syncAutoplay(!autoplayVoice);
}}

// Odia to Devanagari Phonetic Converter for Speech Synthesis
function convertOdiaToPhonetic(text) {{
    let res = '';
    for (let i = 0; i < text.length; i++) {{
        let code = text.charCodeAt(i);
        if (code >= 0x0B01 && code <= 0x0B71) {{
            res += String.fromCharCode(code - 0x0200);
        }} else {{
            res += text[i];
        }}
    }}
    return res;
}}

// High-Fidelity Multi-Language Text-to-Speech
function speak(text, langOverride = null) {{
    if (!autoplayVoice) return;
    const lang = langOverride || getActiveLang();

    let ttsLang = 'en-IN';
    let ttsText = text;

    if (lang === 'hi-IN' || lang === 'hi') {{
        ttsLang = 'hi';
    }} else if (lang === 'te-IN' || lang === 'te') {{
        ttsLang = 'te';
    }} else if (lang === 'or-IN' || lang === 'or') {{
        ttsLang = 'hi';
        ttsText = convertOdiaToPhonetic(text);
    }} else if (lang === 'en-US') {{
        ttsLang = 'en';
    }} else if (lang === 'en-GB') {{
        ttsLang = 'en';
    }} else {{
        ttsLang = 'en-IN';
    }}

    setVoiceState('speaking');

    const cleanQ = ttsText.replace(/<[^>]*>/g, '').replace(/[*_#`\\[\\]\\(\\)]/g, ' ').replace(/\\s+/g, ' ').trim().substring(0, 190);
    const ttsUrl = 'https://translate.google.com/translate_tts?ie=UTF-8&q=' + encodeURIComponent(cleanQ) + '&tl=' + ttsLang + '&client=tw-ob';
    const audio = new Audio(ttsUrl);
    const speedEl = document.getElementById('speedSelect');
    const speed = speedEl ? parseFloat(speedEl.value || 1) : 1;
    audio.playbackRate = speed;

    audio.onended = () => {{
        setVoiceState('idle');
    }};

    audio.play().catch(err => {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance(cleanQ);
            utter.rate = speed;
            utter.lang = (lang === 'or-IN') ? 'hi-IN' : lang;

            const voices = window.speechSynthesis.getVoices();
            if (voices && voices.length > 0) {{
                const match = voices.find(v => v.lang === utter.lang || v.lang.startsWith(utter.lang.split('-')[0]));
                if (match) utter.voice = match;
            }}
            utter.onend = () => {{ setVoiceState('idle'); }};
            utter.onerror = () => {{ setVoiceState('idle'); }};
            window.speechSynthesis.speak(utter);
        }} else {{
            setVoiceState('idle');
        }}
    }});
}}

// Math Solver
function solveMath() {{
    const expr = document.getElementById('mathInput').value;
    try {{
        const sanitized = expr.replaceAll('x', '*').replaceAll('^', '**');
        const res = Function('"use strict";return (' + sanitized + ')')();
        document.getElementById('mathResult').innerHTML = `Result: <strong>${{res}}</strong>`;
        const i18n = getI18n();
        speak(i18n.mathResultSpoken(expr, res));
        incCommand();
        showToast(`Math solved: ${{res}}`);
    }} catch (e) {{
        document.getElementById('mathResult').innerHTML = '<span style="color:#ef4444;">Invalid Expression</span>';
    }}
}}

// Password Generator
function updateSliderVal(val) {{
    document.getElementById('sliderValDisplay').textContent = val;
}}

function generatePassword() {{
    const len = parseInt(document.getElementById('pwdSlider').value) || 14;
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let pwd = '';
    for (let i = 0; i < len; i++) {{
        pwd += chars.charAt(Math.floor(Math.random() * chars.length));
    }}
    document.getElementById('pwdResult').textContent = pwd;
    navigator.clipboard.writeText(pwd).catch(() => {{}});
    const i18n = getI18n();
    speak(i18n.pwdGenSpoken);
    incCommand();
    showToast("Password copied to clipboard!", "🔐");
}}

// Coin & Dice
function flipCoin() {{
    const outcomes = ['Heads', 'Tails'];
    const pick = outcomes[Math.floor(Math.random() * outcomes.length)];
    document.getElementById('coinText').textContent = pick;
    const i18n = getI18n();
    speak(i18n.coinSpoken(pick));
    incCommand();
    showToast(`Coin: ${{pick}}!`, "🪙");
}}

function rollDice() {{
    const num = Math.floor(Math.random() * 6) + 1;
    const glyphs = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
    document.getElementById('diceDisplay').textContent = glyphs[num - 1];
    const i18n = getI18n();
    speak(i18n.diceSpoken(num));
    incCommand();
    showToast(`Dice: ${{num}}!`, "🎲");
}}

// Escape HTML helper
function escapeHtml(str) {{
    if (!str) return '';
    return str.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
}}

// Speech Recognition Engine
function initSpeech() {{
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRec) {{
        recognition = new SpeechRec();
        recognition.continuous = false;
        recognition.interimResults = false;
        const currentSelectedLang = getActiveLang();
        recognition.lang = (currentSelectedLang === 'or-IN') ? 'hi-IN' : currentSelectedLang;

        recognition.onstart = () => {{
            isRecording = true;
            setVoiceState('listening');
        }};

        recognition.onresult = (e) => {{
            const transcript = e.results[0][0].transcript;
            setVoiceState('processing');
            processCommand(transcript, true);
        }};

        recognition.onerror = (e) => {{
            isRecording = false;
            setVoiceState('idle');
        }};

        recognition.onend = () => {{
            isRecording = false;
            if (currentVoiceState === 'listening') {{
                setVoiceState('idle');
            }}
        }};
    }}
}}
initSpeech();

function toggleVoiceRecording() {{
    openModal('voiceModal');
    toggleModalVoice();
}}

function toggleModalVoice() {{
    if (!recognition) initSpeech();
    if (recognition) {{
        if (isRecording) {{
            recognition.stop();
            isRecording = false;
            setVoiceState('idle');
        }} else {{
            try {{
                const sel = getActiveLang();
                recognition.lang = (sel === 'or-IN') ? 'hi-IN' : sel;
                recognition.start();
            }} catch(e) {{
                isRecording = false;
                setVoiceState('idle');
            }}
        }}
    }} else {{
        alert("Microphone recognition is supported in Google Chrome, Microsoft Edge, and Safari. Please ensure microphone permissions are granted.");
    }}
}}

// Unified Intelligent Multilingual Command Processor
function processCommand(cmdText, isModal = false) {{
    const cmd = cmdText.trim();
    if (!cmd) return;

    incCommand();
    const lcmd = cmd.toLowerCase();
    const personaEl = document.getElementById('personaSelect');
    const persona = personaEl ? personaEl.value : 'Raaj AI';
    const chatBox = document.getElementById('chatTimeline');
    const i18n = getI18n();
    const currentLang = getActiveLang();

    // Add User Message
    if (chatBox) {{
        chatBox.innerHTML += `
            <div style="background: linear-gradient(135deg, #4f46e5, #6366f1); color: white; padding: 12px 16px; border-radius: 16px 16px 4px 16px; margin-left: auto; max-width: 82%; font-size: 0.9rem; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);">
                <div style="font-size: 0.72rem; opacity: 0.85; margin-bottom: 2px;">You</div>
                ${{escapeHtml(cmd)}}
            </div>`;
        chatBox.scrollTop = chatBox.scrollHeight;
    }}

    function addBotReply(replyHtml, speakText) {{
        if (chatBox) {{
            const safeSpeak = escapeHtml(speakText || '').replace(/'/g, "\\'");
            chatBox.innerHTML += `
                <div style="background: rgba(22, 28, 66, 0.9); border: 1px solid rgba(139, 92, 246, 0.35); color: #f8fafc; padding: 14px 18px; border-radius: 16px 16px 16px 4px; max-width: 88%; font-size: 0.9rem; line-height: 1.5; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 0.78rem; font-weight: 700; color: #818cf8;">🤖 ${{persona}}</span>
                        <button onclick="speak('${{safeSpeak}}', '${{currentLang}}')" style="background: rgba(56, 189, 248, 0.15); border: 1px solid rgba(56, 189, 248, 0.35); color: #38bdf8; border-radius: 6px; padding: 2px 8px; font-size: 0.72rem; cursor: pointer;">
                            🔊 Replay Voice
                        </button>
                    </div>
                    ${{replyHtml}}
                </div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }}
        if (speakText) {{
            speak(speakText, currentLang);
        }}
    }}

    // 1. OPEN WEBSITES & APPS
    const websites = {{
        'youtube': {{ url: 'https://www.youtube.com', name: 'YouTube', icon: '▶️' }},
        'google': {{ url: 'https://www.google.com', name: 'Google', icon: '🔍' }},
        'gmail': {{ url: 'https://mail.google.com', name: 'Gmail', icon: '✉️' }},
        'github': {{ url: 'https://github.com', name: 'GitHub', icon: '🐙' }},
        'linkedin': {{ url: 'https://www.linkedin.com', name: 'LinkedIn', icon: '💼' }},
        'chatgpt': {{ url: 'https://chatgpt.com', name: 'ChatGPT', icon: '🤖' }},
        'spotify': {{ url: 'https://open.spotify.com', name: 'Spotify', icon: '🎵' }},
        'netflix': {{ url: 'https://www.netflix.com', name: 'Netflix', icon: '🎬' }},
        'twitter': {{ url: 'https://twitter.com', name: 'Twitter', icon: '🐦' }},
        'x': {{ url: 'https://x.com', name: 'X (Twitter)', icon: '✖️' }}
    }};

    // Multi-language YouTube detection
    if (lcmd.includes('यूट्यूब') || lcmd.includes('ୟୁଟ୍ୟୁବ୍') || lcmd.includes('యూట్యూబ్') || lcmd.includes('open youtube') || lcmd === 'youtube') {{
        window.open('https://www.youtube.com', '_blank');
        addBotReply(`${{i18n.openYt}}<br><br><a href="https://www.youtube.com" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:7px 16px; background:linear-gradient(135deg, #ef4444, #dc2626); color:white; border-radius:8px; text-decoration:none; font-weight:600; font-size:0.84rem;"><span>▶️</span> Launch YouTube ↗</a>`, i18n.openYtSpoken);
        return;
    }}

    for (let key in websites) {{
        if (lcmd.includes('open ' + key) || lcmd === key || lcmd.includes('खोलो ' + key) || lcmd.includes(key + ' खोलो') || lcmd.includes(key + ' ଖୋଲ') || lcmd.includes(key + ' ఓపెన్')) {{
            const site = websites[key];
            window.open(site.url, '_blank');
            addBotReply(
                `${{i18n.openSite(site.name)}}<br><br>
                 <a href="${{site.url}}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:7px 16px; background:linear-gradient(135deg, #0ea5e9, #3b82f6); color:white; border-radius:8px; text-decoration:none; font-weight:600; font-size:0.84rem;">
                     <span>${{site.icon}}</span> Launch ${{site.name}} ↗
                 </a>`,
                i18n.openSiteSpoken(site.name)
            );
            return;
        }}
    }}

    // 2. TELL ABOUT YOU / WHO ARE YOU / GREETINGS (MULTILINGUAL)
    if (lcmd.includes('tell about you') || lcmd.includes('who are you') || lcmd.includes('tell me about you') || lcmd.includes('about you') || lcmd.includes('who made you') || lcmd.includes('introduce yourself') || lcmd === 'hello' || lcmd === 'hi' || lcmd.includes('नमस्ते') || lcmd.includes('तुम कौन हो') || lcmd.includes('आप कौन हैं') || lcmd.includes('ନମସ୍କାର') || lcmd.includes('ତୁମେ କିଏ') || lcmd.includes('నమస్కారం') || lcmd.includes('నువ్వు ఎవరు') || lcmd.includes('మీరు ఎవరు')) {{
        const bioHtml = `
            ${{i18n.bioGreeting}}<br><br>
            ${{currentLang === 'hi-IN' ? 'मैं आपके लिए ये सभी कार्य कर सकता हूँ:' : (currentLang === 'or-IN' ? 'ମୁଁ ଆପଣଙ୍କ ପାଇଁ ଏହି ସବୁ କରିପାରିବି:' : (currentLang === 'te-IN' ? 'నేను మీ కోసం ఇవన్నీ చేయగలను:' : 'Here is what I can do for you:'))}}<br>
            • 🎬 <strong>Play Music:</strong> <em>"play Nazar Lagi"</em> / <em>"गाना बजाओ"</em><br>
            • ⛅ <strong>Live Weather:</strong> <em>"weather Hyderabad"</em> / <em>"हैदराबाद का मौसम"</em><br>
            • 📖 <strong>Wikipedia:</strong> <em>"who is Nikola Tesla"</em> / <em>"what is AI"</em><br>
            • 🧮 <strong>Math Solver:</strong> <em>"calculate 15 * 84 + 120"</em><br>
            • 🚀 <strong>App Launcher:</strong> <em>"open youtube"</em>, <em>"open google"</em><br>
            • 📝 <strong>Smart Notes:</strong> <em>"note buy groceries"</em><br>
            • 🎲 <strong>Fun:</strong> <em>"tell me a joke"</em>, <em>"flip a coin"</em>`;
        addBotReply(bioHtml, i18n.bioText);
        return;
    }}

    // 3. PLAY SONG ON YOUTUBE (MULTILINGUAL)
    if (lcmd.includes('play ') || lcmd.startsWith('play') || lcmd.includes('बजाओ') || lcmd.includes('चलाओ') || lcmd.includes('गाना') || lcmd.includes('गीत') || lcmd.includes('ବଜାଅ') || lcmd.includes('ଗୀତ') || lcmd.includes('ప్లే') || lcmd.includes('పాట')) {{
        let song = lcmd.replace(/^(can you )?play/, '').replace(/(the song|music|video|on youtube|गाना बजाओ|गाना चलाओ|बजाओ|चलाओ|ଗୀତ ବଜାଅ|ବଜାଅ|ପ୍ଲେ କର|ప్లే చేయి|పాట ప్లే|పాట)/g, '').trim();
        if (!song) song = 'Alan Walker Faded';
        const ytUrl = 'https://www.youtube.com/results?search_query=' + encodeURIComponent(song);
        window.open(ytUrl, '_blank');
        addBotReply(
            `${{i18n.playMusic(song)}}<br><br>
             <a href="${{ytUrl}}" target="_blank" style="display:inline-flex; align-items:center; gap:6px; padding:7px 16px; background:linear-gradient(135deg, #ef4444, #dc2626); color:white; border-radius:8px; text-decoration:none; font-weight:600; font-size:0.84rem;">
                 <span>📺</span> Open YouTube Video ↗
             </a>`,
            i18n.playMusicSpoken(song)
        );
        return;
    }}

    // 4. REAL-TIME WEATHER (MULTILINGUAL)
    if (lcmd.includes('weather') || lcmd.includes('temperature') || lcmd.includes('forecast') || lcmd.includes('मौसम') || lcmd.includes('तापमान') || lcmd.includes('ପାଣିପାଗ') || lcmd.includes('వాతావరణం')) {{
        let city = lcmd.replace(/(what is the|tell me the|how is the|weather|temperature|forecast|in|of|for|today|now|का मौसम|मौसम|तापमान|ର ପାଣିପାଗ|ପାଣିପାଗ|వాతావరణం)/g, '').trim() || 'Hyderabad';
        fetch(`https://wttr.in/${{encodeURIComponent(city)}}?format=j1`)
            .then(r => r.json())
            .then(d => {{
                const c = d.current_condition[0];
                const reportHtml = `
                    ⛅ <strong>Weather in ${{city.toUpperCase()}}</strong><br>
                    • Condition: <strong>${{c.weatherDesc[0].value}}</strong><br>
                    • Temperature: <strong>${{c.temp_C}}°C (${{c.temp_F}}°F)</strong> (Feels like ${{c.FeelsLikeC}}°C)<br>
                    • Humidity: <strong>${{c.humidity}}%</strong> | Wind: <strong>${{c.windspeedKmph}} km/h</strong><br><br>
                    <a href="https://www.accuweather.com/en/search-locations?query=${{encodeURIComponent(city)}}" target="_blank" style="color:#38bdf8; font-weight:600;">View Radar & Detailed Forecast ↗</a>`;
                addBotReply(reportHtml, i18n.weatherSpoken(city, c.weatherDesc[0].value, c.temp_C));
            }})
            .catch(() => {{
                addBotReply(
                    `⛅ Live Weather for <strong>${{city}}</strong>:<br><a href="https://www.google.com/search?q=weather+${{encodeURIComponent(city)}}" target="_blank" style="color:#38bdf8;">View live weather on Google ↗</a>`,
                    i18n.weatherSpoken(city, 'clear', '28')
                );
            }});
        return;
    }}

    // 5. WIKIPEDIA
    if (lcmd.startsWith('who is ') || lcmd.startsWith('what is ') || lcmd.startsWith('tell me about ') || lcmd.startsWith('wikipedia ') || lcmd.includes('विकिपीडिया')) {{
        const q = lcmd.replace(/^(who is|what is|tell me about|wikipedia|विकिपीडिया)\\s+/, '').trim();
        fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${{encodeURIComponent(q)}}`)
            .then(r => r.json())
            .then(d => {{
                if (d.extract) {{
                    const wikiHtml = `
                        📖 <strong>${{d.title}}</strong><br><br>
                        ${{d.extract}}<br><br>
                        <a href="${{d.content_urls.desktop.page}}" target="_blank" style="color:#38bdf8; font-weight:600;">Read complete article on Wikipedia ↗</a>`;
                    addBotReply(wikiHtml, d.extract.substring(0, 160));
                }} else {{
                    addBotReply(
                        `🔎 Search: "${{q}}"<br><a href="https://www.google.com/search?q=${{encodeURIComponent(q)}}" target="_blank" style="color:#38bdf8;">Search Google for ${{q}} ↗</a>`,
                        i18n.searchSpoken(q)
                    );
                }}
            }})
            .catch(() => {{
                addBotReply(
                    `🔎 Search: <a href="https://www.google.com/search?q=${{encodeURIComponent(q)}}" target="_blank" style="color:#38bdf8;">Search Google for ${{q}} ↗</a>`,
                    i18n.searchSpoken(q)
                );
            }});
        return;
    }}

    // 6. MATH SOLVER
    if (lcmd.includes('+') || lcmd.includes('*') || lcmd.includes('/') || lcmd.startsWith('calculate') || lcmd.includes('% of')) {{
        const cleanExpr = lcmd.replace('calculate', '').trim();
        try {{
            const sanitized = cleanExpr.replaceAll('x', '*').replaceAll('^', '**');
            const res = Function('"use strict";return (' + sanitized + ')')();
            document.getElementById('mathInput').value = cleanExpr;
            document.getElementById('mathResult').innerHTML = `Result: <strong>${{res}}</strong>`;
            addBotReply(`🧮 Result: <code>${{cleanExpr}}</code> = <strong>${{res}}</strong>`, i18n.mathResultSpoken(cleanExpr, res));
            return;
        }} catch(e) {{}}
    }}

    // 7. JOKES (MULTILINGUAL)
    if (lcmd.includes('joke') || lcmd.includes('laugh') || lcmd.includes('चुटकुला') || lcmd.includes('मजाक') || lcmd.includes('ହସ') || lcmd.includes('ଜୋକ୍') || lcmd.includes('నవ్వు') || lcmd.includes('జోక్')) {{
        const jList = i18n.jokes;
        const j = jList[Math.floor(Math.random() * jList.length)];
        addBotReply(`😄 <strong>Joke:</strong><br><br><em>"${{j}}"</em>`, j);
        return;
    }}

    // 8. NOTES (MULTILINGUAL)
    if (lcmd.startsWith('note ') || lcmd.startsWith('remember ') || lcmd.includes('नोट') || lcmd.includes('ନୋଟ୍') || lcmd.includes('గమనిక')) {{
        const noteContent = cmd.replace(/^(note|remember to|remember|नोट|ନୋଟ୍|గమనిక)\\s*/i, '').trim();
        if (noteContent) {{
            savedNotesCount++;
            document.getElementById('savedNotesDisplay').textContent = savedNotesCount;
            const notesList = document.getElementById('notesList');
            if (notesList) {{
                const div = document.createElement('div');
                div.style = 'padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; font-size: 0.88rem;';
                div.textContent = '📌 ' + noteContent;
                notesList.prepend(div);
            }}
            addBotReply(`📝 <strong>Note Saved:</strong> "${{escapeHtml(noteContent)}}"`, i18n.noteSavedSpoken);
            return;
        }}
    }}

    // 9. TIME & DATE (MULTILINGUAL)
    if (lcmd.includes('time') || lcmd.includes('समय') || lcmd.includes('टाइम') || lcmd.includes('ବେଳ') || lcmd.includes('సమయం') || lcmd.includes('టైమ్')) {{
        const timeNow = new Date().toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}});
        addBotReply(`🕐 Current Time: <strong>${{timeNow}}</strong>`, i18n.timeSpoken(timeNow));
        return;
    }}
    if (lcmd.includes('date') || lcmd.includes('day') || lcmd.includes('तारीख') || lcmd.includes('आज') || lcmd.includes('ତାରିଖ') || lcmd.includes('ଆଜି') || lcmd.includes('తేదీ')) {{
        const dateNow = new Date().toLocaleDateString([], {{weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'}});
        addBotReply(`📅 Today is <strong>${{dateNow}}</strong>`, i18n.dateSpoken(dateNow));
        return;
    }}

    // 10. COIN & DICE (MULTILINGUAL)
    if (lcmd.includes('coin') || lcmd.includes('toss') || lcmd.includes('सिक्का') || lcmd.includes('ଟସ୍') || lcmd.includes('టాస్')) {{
        const outcomes = ['Heads', 'Tails'];
        const pick = outcomes[Math.floor(Math.random() * outcomes.length)];
        document.getElementById('coinText').textContent = pick;
        addBotReply(`🪙 Coin Toss: <strong>${{pick}}</strong>!`, i18n.coinSpoken(pick));
        return;
    }}
    if (lcmd.includes('dice') || lcmd.includes('roll') || lcmd.includes('पासा') || lcmd.includes('ଡାଇସ୍') || lcmd.includes('డైస్')) {{
        const num = Math.floor(Math.random() * 6) + 1;
        const glyphs = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
        document.getElementById('diceDisplay').textContent = glyphs[num - 1];
        addBotReply(`🎲 Dice Roll: <strong>${{num}}</strong>!`, i18n.diceSpoken(num));
        return;
    }}

    // 11. DEFAULT FALLBACK: SEARCH GOOGLE
    const gUrl = 'https://www.google.com/search?q=' + encodeURIComponent(cmd);
    addBotReply(
        `🌐 Search results for: <strong>"${{escapeHtml(cmd)}}"</strong><br><br>
         <a href="${{gUrl}}" target="_blank" style="display:inline-block; padding:7px 16px; background:linear-gradient(135deg, #0ea5e9, #3b82f6); color:white; border-radius:8px; text-decoration:none; font-weight:600; font-size:0.84rem;">🔍 Open Google Search Results ↗</a>`,
        i18n.searchSpoken(cmd)
    );
    window.open(gUrl, '_blank');
}}

// Command Inputs
function handleInputKey(e) {{
    if (e.key === 'Enter') executeCommand();
}}

function executeCommand() {{
    const input = document.getElementById('commandInput');
    const cmd = input.value.trim();
    if (!cmd) return;
    input.value = '';
    openModal('voiceModal');
    processCommand(cmd, true);
}}

function sendModalChat() {{
    const inp = document.getElementById('modalChatInput');
    const text = inp.value.trim();
    if (!text) return;
    inp.value = '';
    processCommand(text, true);
}}

function setAndSendModal(text) {{
    processCommand(text, true);
}}

// Weather Fetcher
function fetchLiveWeather() {{
    const city = document.getElementById('weatherCity').value || 'Hyderabad';
    fetch(`https://wttr.in/${{encodeURIComponent(city)}}?format=j1`)
        .then(r => r.json())
        .then(d => {{
            const c = d.current_condition[0];
            const report = `⛅ <strong>Weather in ${{city.toUpperCase()}}</strong><br>
                            - Condition: ${{c.weatherDesc[0].value}}<br>
                            - Temperature: <strong>${{c.temp_C}}°C (${{c.temp_F}}°F)</strong> — Feels like ${{c.FeelsLikeC}}°C<br>
                            - Humidity: ${{c.humidity}}% | Wind: ${{c.windspeedKmph}} km/h`;
            document.getElementById('weatherDisplay').innerHTML = report;
            const i18n = getI18n();
            speak(i18n.weatherSpoken(city, c.weatherDesc[0].value, c.temp_C));
            showToast(`Weather in ${{city}}: ${{c.temp_C}}°C`, "⛅");
        }})
        .catch(() => {{
            document.getElementById('weatherDisplay').innerHTML = `⛅ Live forecast for ${{city}}: <a href="https://www.google.com/search?q=weather+${{encodeURIComponent(city)}}" target="_blank" style="color:#38bdf8;">View on Google</a>`;
            const i18n = getI18n();
            speak(i18n.weatherSpoken(city, 'clear', '28'));
        }});
}}

// Wiki Fetcher
function fetchWiki() {{
    const query = document.getElementById('wikiQuery').value || 'Artificial Intelligence';
    fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${{encodeURIComponent(query)}}`)
        .then(r => r.json())
        .then(d => {{
            if (d.extract) {{
                document.getElementById('wikiDisplay').innerHTML = `<strong>${{d.title}}</strong><br>${{d.extract}}<br><a href="${{d.content_urls.desktop.page}}" target="_blank" style="color:#38bdf8;">Read full article &rarr;</a>`;
                speak(d.extract.substring(0, 180));
                showToast(`Wikipedia: ${{d.title}}`, "📖");
            }} else {{
                document.getElementById('wikiDisplay').innerHTML = `Search: <a href="https://www.google.com/search?q=${{encodeURIComponent(query)}}" target="_blank" style="color:#38bdf8;">Google Search for ${{query}}</a>`;
            }}
        }})
        .catch(() => {{
            document.getElementById('wikiDisplay').innerHTML = `Search: <a href="https://www.google.com/search?q=${{encodeURIComponent(query)}}" target="_blank" style="color:#38bdf8;">Google Search for ${{query}}</a>`;
        }});
}}

// Modals
function openModal(id) {{
    const el = document.getElementById(id);
    if (el) el.classList.add('open');
}}

function closeModal(id) {{
    const el = document.getElementById(id);
    if (el) el.classList.remove('open');
}}

function switchNav(name, el) {{
    document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
    document.querySelectorAll('.bnav-item').forEach(i => i.classList.remove('active'));
    if (el) el.classList.add('active');
    showToast(`Navigated to ${{name}}`);
}}

function addNote() {{
    const txt = document.getElementById('newNoteText').value.trim();
    if (!txt) return;
    savedNotesCount++;
    const numEl = document.getElementById('savedNotesDisplay');
    if (numEl) numEl.textContent = savedNotesCount;
    const div = document.createElement('div');
    div.style = 'padding: 10px; background: rgba(255,255,255,0.05); border-radius: 8px; font-size: 0.88rem;';
    div.textContent = '📌 ' + txt;
    document.getElementById('notesList').prepend(div);
    document.getElementById('newNoteText').value = '';
    const i18n = getI18n();
    speak(i18n.noteSavedSpoken);
    incCommand();
    showToast("Note added!", "📝");
}}

function searchYouTube() {{
    const q = document.getElementById('ytQuery').value;
    window.open('https://www.youtube.com/results?search_query=' + encodeURIComponent(q), '_blank');
    const i18n = getI18n();
    speak(i18n.playMusicSpoken(q));
    incCommand();
    showToast(`Searching YouTube for ${{q}}`, "▶️");
}}

function generateWhatsApp() {{
    const phone = document.getElementById('waPhone').value.replace(/[^0-9]/g, '');
    const msg = document.getElementById('waMsg').value;
    window.open(`https://wa.me/${{phone}}?text=${{encodeURIComponent(msg)}}`, '_blank');
    incCommand();
    showToast("Launching WhatsApp...", "💬");
}}
</script>
</body>
</html>
"""

# Render the responsive application via Streamlit component
components.html(HTML_CONTENT, height=1050, scrolling=False)
