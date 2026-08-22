"""
UI styling helpers, custom CSS injection, rich badges, diff viewer,
and report export generators for Streamlit.
"""

import html
import json
import streamlit as st


def inject_custom_css():
    """Injects high-end dark mode CSS styling with modern glassmorphic cards and typography."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Global Typography & Background */
        html, body, [class*="css"], .stMarkdown, .stText, p, span, div, label {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            letter-spacing: -0.01em;
        }
        
        code, pre, .stCodeBlock, [data-testid="stCode"] {
            font-family: 'JetBrains Mono', 'Fira Code', Menlo, Monaco, Consolas, monospace !important;
        }

        /* Hero Header Styling */
        .hero-container {
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.12) 0%, rgba(168, 85, 247, 0.12) 50%, rgba(30, 41, 59, 0.4) 100%);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 16px;
            padding: 24px 28px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
        }

        .hero-title {
            font-size: 2.1rem;
            font-weight: 800;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            letter-spacing: -0.02em;
        }

        .hero-subtitle {
            color: #94a3b8;
            font-size: 0.98rem;
            margin-top: 6px;
            margin-bottom: 12px;
            font-weight: 400;
        }

        /* Status & Pipeline Badges */
        .badge-bar {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .badge-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 9999px;
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(148, 163, 184, 0.2);
            color: #e2e8f0;
            transition: all 0.2s ease-in-out;
        }

        .badge-pill:hover {
            transform: translateY(-1px);
        }

        .badge-cyan {
            border-color: rgba(56, 189, 248, 0.4);
            color: #38bdf8;
            background: rgba(56, 189, 248, 0.1);
        }

        .badge-emerald {
            border-color: rgba(52, 211, 153, 0.4);
            color: #34d399;
            background: rgba(52, 211, 153, 0.1);
        }

        .badge-purple {
            border-color: rgba(192, 132, 252, 0.4);
            color: #c084fc;
            background: rgba(192, 132, 252, 0.1);
        }

        .badge-rose {
            border-color: rgba(251, 113, 133, 0.4);
            color: #fb7185;
            background: rgba(251, 113, 133, 0.1);
        }

        .badge-amber {
            border-color: rgba(251, 191, 36, 0.4);
            color: #fbbf24;
            background: rgba(251, 191, 36, 0.1);
        }

        .badge-crimson {
            border-color: rgba(239, 68, 68, 0.5);
            color: #f87171;
            background: rgba(239, 68, 68, 0.15);
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(22, 27, 34, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        }

        /* Pulsing Red/Orange Glowing Border Animation for Savage Roast */
        @keyframes roastPulseGlow {
            0% {
                border-color: rgba(239, 68, 68, 0.45);
                box-shadow: 0 0 15px rgba(239, 68, 68, 0.2), inset 0 0 8px rgba(245, 158, 11, 0.05);
            }
            50% {
                border-color: rgba(249, 115, 22, 0.85);
                box-shadow: 0 0 28px rgba(249, 115, 22, 0.4), 0 0 14px rgba(239, 68, 68, 0.25), inset 0 0 12px rgba(245, 158, 11, 0.1);
            }
            100% {
                border-color: rgba(239, 68, 68, 0.45);
                box-shadow: 0 0 15px rgba(239, 68, 68, 0.2), inset 0 0 8px rgba(245, 158, 11, 0.05);
            }
        }

        /* Savage Roast Output Card with Glowing Border */
        .roast-card {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.14) 0%, rgba(245, 158, 11, 0.1) 50%, rgba(15, 23, 42, 0.94) 100%);
            border: 2px solid rgba(239, 68, 68, 0.5);
            border-left: 6px solid #f97316;
            border-radius: 14px;
            padding: 22px 26px;
            margin-bottom: 22px;
            animation: roastPulseGlow 3s ease-in-out infinite;
            backdrop-filter: blur(8px);
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
            font-size: 0.96rem;
            line-height: 1.6;
            white-space: pre-line;
        }

        /* Tutor 3-Bullet Styling */
        .tutor-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
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
            gap: 12px;
            padding: 12px 16px;
            margin-bottom: 10px;
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(148, 163, 184, 0.12);
            border-radius: 10px;
            color: #f1f5f9;
            font-size: 0.94rem;
            line-height: 1.55;
        }

        .tutor-bullet-num {
            background: linear-gradient(135deg, #a855f7, #38bdf8);
            color: white;
            font-weight: 700;
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

        /* Judge0 Self-Healing Box */
        .judge0-timeline {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 10px;
            padding: 14px 18px;
            margin: 12px 0;
        }

        /* Diff Viewer Styling */
        .diff-container {
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 14px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            overflow-x: auto;
            max-height: 480px;
            line-height: 1.45;
        }

        .diff-add {
            background-color: rgba(46, 160, 67, 0.15);
            color: #3fb950;
            display: block;
            padding: 2px 6px;
            border-radius: 2px;
        }

        .diff-del {
            background-color: rgba(248, 81, 73, 0.15);
            color: #f85149;
            display: block;
            padding: 2px 6px;
            border-radius: 2px;
        }

        .diff-info {
            color: #58a6ff;
            display: block;
            padding: 2px 6px;
            font-weight: 600;
        }

        .diff-normal {
            color: #c9d1d9;
            display: block;
            padding: 2px 6px;
        }

        /* Streamlit Button Tweaks */
        div.stButton > button:first-child {
            background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
            color: white;
            font-weight: 600;
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 8px;
            padding: 10px 24px;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 4px 14px 0 rgba(2, 132, 199, 0.39);
        }

        div.stButton > button:first-child:hover {
            background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%);
            border-color: #38bdf8;
            transform: translateY(-1px);
            box-shadow: 0 6px 20px 0 rgba(2, 132, 199, 0.6);
        }
        </style>
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

    report = f"""# 🛡️ Assignment Debug & Code Review Report
*Generated by Multi-Agent Gemini Debugger (`{telemetry.get('model_name', 'gemini-2.5-flash')}`) in {telemetry.get('total_duration_sec', 0)}s*

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
