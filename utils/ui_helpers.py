"""
UI styling helpers, custom CSS injection, rich badges, diff viewer,
and report export generators for Streamlit with Vercel/Linear Dark Mode Aesthetic.
"""

import html
import json
from typing import Optional
import streamlit as st


def inject_custom_css():
    """Injects Vercel / Linear dark-mode CSS styling with modern typography, micro-interactions, and glowing accents."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Global Typography & Background (Vercel/Linear Dark Canvas) */
        html, body, [class*="css"], .stMarkdown, .stText, p, span, div, label {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            letter-spacing: -0.015em;
            color: #ededed;
        }
        
        .stApp {
            background-color: #000000 !important;
            background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 0);
            background-size: 24px 24px;
        }

        code, pre, .stCodeBlock, [data-testid="stCode"] {
            font-family: 'JetBrains Mono', 'Fira Code', Menlo, Monaco, Consolas, monospace !important;
        }

        /* Hero Header Styling (Linear/Vercel Frosted Banner) */
        .hero-container {
            background: linear-gradient(180deg, rgba(24, 24, 27, 0.7) 0%, rgba(9, 9, 11, 0.9) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 26px 30px;
            margin-bottom: 24px;
            box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.05), 0 20px 40px -15px rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(12px);
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(180deg, #ffffff 0%, #a1a1aa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            letter-spacing: -0.03em;
        }

        .hero-subtitle {
            color: #a1a1aa;
            font-size: 1.0rem;
            margin-top: 6px;
            margin-bottom: 14px;
            font-weight: 400;
        }

        /* Status & Pipeline Badges */
        .badge-bar {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 12px;
        }

        .badge-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.76rem;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 9999px;
            background: rgba(24, 24, 27, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #d4d4d8;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .badge-pill:hover {
            transform: translateY(-1px);
            border-color: rgba(255, 255, 255, 0.25);
        }

        .badge-cyan {
            border-color: rgba(56, 189, 248, 0.35);
            color: #38bdf8;
            background: rgba(56, 189, 248, 0.08);
        }

        .badge-emerald {
            border-color: rgba(52, 211, 153, 0.35);
            color: #34d399;
            background: rgba(52, 211, 153, 0.08);
        }

        .badge-purple {
            border-color: rgba(192, 132, 252, 0.35);
            color: #c084fc;
            background: rgba(192, 132, 252, 0.08);
        }

        .badge-rose {
            border-color: rgba(251, 113, 133, 0.35);
            color: #fb7185;
            background: rgba(251, 113, 133, 0.08);
        }

        .badge-amber {
            border-color: rgba(251, 191, 36, 0.35);
            color: #fbbf24;
            background: rgba(251, 191, 36, 0.08);
        }

        .badge-crimson {
            border-color: rgba(239, 68, 68, 0.45);
            color: #f87171;
            background: rgba(239, 68, 68, 0.12);
        }

        /* Vercel / Linear Cards */
        .glass-card {
            background: rgba(18, 18, 18, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 18px 22px;
            margin-bottom: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
        }

        .premium-card {
            background: linear-gradient(180deg, rgba(24, 24, 27, 0.75) 0%, rgba(9, 9, 11, 0.85) 100%);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 16px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(10px);
            transition: all 0.2s ease-in-out;
        }

        .premium-card:hover {
            border-color: rgba(255, 255, 255, 0.18);
            transform: translateY(-1px);
        }

        /* Pulsing Red/Orange Glowing Border Animation for Savage Roast */
        @keyframes roastPulseGlow {
            0% {
                border-color: rgba(239, 68, 68, 0.45);
                box-shadow: 0 0 16px rgba(239, 68, 68, 0.2), inset 0 0 10px rgba(245, 158, 11, 0.05);
            }
            50% {
                border-color: rgba(249, 115, 22, 0.9);
                box-shadow: 0 0 32px rgba(249, 115, 22, 0.45), 0 0 16px rgba(239, 68, 68, 0.3), inset 0 0 14px rgba(245, 158, 11, 0.12);
            }
            100% {
                border-color: rgba(239, 68, 68, 0.45);
                box-shadow: 0 0 16px rgba(239, 68, 68, 0.2), inset 0 0 10px rgba(245, 158, 11, 0.05);
            }
        }

        /* Savage Roast Output Card with Glowing Border */
        .roast-card {
            background: linear-gradient(180deg, rgba(28, 10, 10, 0.8) 0%, rgba(12, 10, 10, 0.95) 100%);
            border: 2px solid rgba(239, 68, 68, 0.5);
            border-left: 6px solid #f97316;
            border-radius: 14px;
            padding: 22px 26px;
            margin-bottom: 22px;
            animation: roastPulseGlow 3s ease-in-out infinite;
            backdrop-filter: blur(12px);
        }

        .roast-header {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.18rem;
            font-weight: 800;
            color: #f87171;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 12px;
        }

        .roast-content {
            color: #fed7aa;
            font-size: 0.98rem;
            line-height: 1.65;
            white-space: pre-line;
        }

        /* Tutor 3-Bullet Styling */
        .tutor-card {
            background: linear-gradient(180deg, rgba(24, 24, 27, 0.8) 0%, rgba(9, 9, 11, 0.95) 100%);
            border-left: 4px solid #a855f7;
            border-top: 1px solid rgba(168, 85, 247, 0.2);
            border-right: 1px solid rgba(168, 85, 247, 0.2);
            border-bottom: 1px solid rgba(168, 85, 247, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        }

        .tutor-bullet {
            display: flex;
            align-items: flex-start;
            gap: 14px;
            padding: 14px 18px;
            margin-bottom: 12px;
            background: rgba(18, 18, 18, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            color: #f4f4f5;
            font-size: 0.95rem;
            line-height: 1.6;
        }

        .tutor-bullet-num {
            background: linear-gradient(135deg, #a855f7, #38bdf8);
            color: white;
            font-weight: 800;
            font-size: 0.8rem;
            width: 26px;
            height: 26px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            margin-top: 2px;
        }

        /* Diff Viewer Styling */
        .diff-container {
            background: #09090b;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.86rem;
            overflow-x: auto;
            max-height: 480px;
            line-height: 1.5;
        }

        .diff-add {
            background-color: rgba(46, 160, 67, 0.18);
            color: #4ade80;
            display: block;
            padding: 2px 6px;
            border-radius: 3px;
        }

        .diff-del {
            background-color: rgba(248, 81, 73, 0.18);
            color: #f87171;
            display: block;
            padding: 2px 6px;
            border-radius: 3px;
        }

        .diff-info {
            color: #60a5fa;
            display: block;
            padding: 2px 6px;
            font-weight: 600;
        }

        .diff-normal {
            color: #a1a1aa;
            display: block;
            padding: 2px 6px;
        }

        /* Vercel Action Buttons */
        div.stButton > button:first-child {
            background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            font-weight: 600;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 8px;
            padding: 10px 24px;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.35);
        }

        div.stButton > button:first-child:hover {
            background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%);
            border-color: rgba(255, 255, 255, 0.3);
            transform: translateY(-1px);
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.5);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_roast_card(roast_content: str):
    """Renders the Savage Code Roast card with pulsing crimson/orange glowing border and Vercel/Linear styling."""
    if not roast_content:
        return
    escaped_roast = html.escape(roast_content).replace("\n", "<br/>")
    st.markdown(
        f"""
        <div class="roast-card">
            <div class="roast-header">
                <span style="font-size: 1.3rem;">🔥</span>
                <span>Savage Code Roast</span>
                <span class="badge-pill badge-crimson" style="margin-left: auto; font-size: 0.72rem;">Brutal CS Review</span>
            </div>
            <div class="roast-content">{escaped_roast}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_premium_card(
    title: str,
    icon: str,
    content: str,
    subtitle: str = "",
    border_color: str = "rgba(255, 255, 255, 0.08)",
):
    """Renders a Vercel/Linear dark-mode premium card with modern hierarchy, clean typography, and subtle border."""
    escaped_content = html.escape(str(content)).replace("\n", "<br/>") if isinstance(content, str) else str(content)
    sub_html = f'<div style="font-size: 0.82rem; color: #71717a; margin-top: 2px;">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="premium-card" style="border-color: {border_color};">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <span style="font-size: 1.25rem;">{icon}</span>
                <div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #f4f4f5; letter-spacing: -0.01em;">{html.escape(title)}</div>
                    {sub_html}
                </div>
            </div>
            <div style="font-size: 0.92rem; color: #d4d4d8; line-height: 1.6;">{escaped_content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero_header():
    """Renders the top CodeRage branding hero header and 5-step pipeline badges."""
    st.markdown(
        """
        <div class="hero-container">
            <h1 class="hero-title">🔥 CodeRage</h1>
            <div class="hero-subtitle">Your bugs aren't ready for this review.</div>
            <div class="badge-bar">
                <span class="badge-pill badge-cyan">🔍 Diagnose</span>
                <span class="badge-pill badge-purple">🔧 Repair</span>
                <span class="badge-pill badge-emerald">🧪 Verify</span>
                <span class="badge-pill badge-crimson">🔥 Roast</span>
                <span class="badge-pill badge-amber">🧠 Learn</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_diff_html(diff_text: str) -> str:
    """Converts a unified diff string into stylized HTML lines."""
    if not diff_text or diff_text == "No textual differences detected.":
        return "<div class='diff-container'><span class='diff-info'>No textual differences detected.</span></div>"

    html_lines = ["<div class='diff-container'>"]
    for line in diff_text.splitlines():
        escaped = html.escape(line)
        if line.startswith("+++") or line.startswith("---"):
            html_lines.append(f"<span class='diff-info'>{escaped}</span>")
        elif line.startswith("@@"):
            html_lines.append(f"<span class='diff-info'>{escaped}</span>")
        elif line.startswith("+"):
            html_lines.append(f"<span class='diff-add'>{escaped}</span>")
        elif line.startswith("-"):
            html_lines.append(f"<span class='diff-del'>{escaped}</span>")
        else:
            html_lines.append(f"<span class='diff-normal'>{escaped}</span>")
    html_lines.append("</div>")
    return "\n".join(html_lines)


def generate_markdown_report(results: dict) -> str:
    """Generates an exportable comprehensive Markdown Debug & Review Report."""
    parser = results.get("parser", {})
    fixer = results.get("fixer", {})
    tutor = results.get("tutor", {})
    judge0 = results.get("judge0", {})
    telemetry = results.get("telemetry", {})
    language = results.get("language", "Code")

    bullets = tutor.get("three_bullet_root_cause", [])
    bullets_md = "\n".join([f"- {b.lstrip('• ')}" for b in bullets])

    patches = fixer.get("patch_summary", [])
    patches_md = "\n".join([f"- {p}" for p in patches])

    optimizations = fixer.get("optimizations_applied", [])
    opts_md = "\n".join([f"- {opt}" for opt in optimizations])

    roast = tutor.get("code_roast", "None")

    report = f"""# 🔥 CodeRage Debug & Code Review Report
*Generated by CodeRage Multi-Agent Pipeline (`{telemetry.get('model_name', 'gemini-3.5-flash')}`) in {telemetry.get('total_duration_sec', 0)}s*

---

## 🔥 Savage Code Roast (Tutor Agent)
> {roast}

---

## 1. 🔍 Bug Diagnostics (Parser Agent)
- **Bug Title:** {parser.get('bug_title', 'Identified Defect')}
- **Category:** `{parser.get('bug_category', 'N/A')}` | **Error Type:** `{parser.get('error_type', 'N/A')}`
- **Severity:** `{parser.get('severity', 'High')}`
- **Impacted Lines:** `{parser.get('impacted_lines', 'N/A')}`
- **Core Summary:** {parser.get('core_bug_summary', '')}

---

## 2. 🎓 Root Cause Explanation (Tutor Agent: 3-Bullet Rule)
{bullets_md}

### 💡 Core Concept: {tutor.get('core_concept_title', 'Fundamental CS Concept')}
{tutor.get('core_concept_summary', '')}

> **Pro-Tip:** {tutor.get('pro_tip', '')}

---

## 3. 🛠️ Corrected & Optimized Code (Fixer Agent & Judge0 Self-Healing)
- **Judge0 Verification:** {'✅ Verified (Passed)' if judge0.get('verified') else '⚠️ Unverified / Simulated'}
- **Self-Healing Iterations:** {judge0.get('total_attempts', 1)} attempts ({'Healed via Retry' if judge0.get('is_healed') else 'First Attempt'})
- **Time Complexity:** `{fixer.get('time_complexity', 'O(N)')}`
- **Space Complexity:** `{fixer.get('space_complexity', 'O(1)')}`

```{language.lower()}
{fixer.get('fixed_code', '')}
```

### ⚡ Patches Applied
{patches_md}

### 🚀 Optimizations
{opts_md}

---

## 4. 📝 Original Source Code
```{language.lower()}
{results.get('original_code', '')}
```

---
*Report generated with CodeRage Multi-Agent Self-Healing Pipeline.*
"""
    return report.strip()


def generate_json_report(results: dict) -> str:
    """Generates an exportable structured JSON report."""
    return json.dumps(results, indent=2)
