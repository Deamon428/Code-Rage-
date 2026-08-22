"""
CodeRage Multi-Agent Web App
Enhanced with GitHub Ingestion, Self-Healing Judge0 Loop, and 'Roast My Code' Tutor Persona.
"""

import html
import os
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

from agents.orchestrator import MultiAgentOrchestrator
from data.sample_presets import SAMPLE_PRESETS
from utils.github_fetcher import fetch_github_resource
from utils.ui_helpers import (
    generate_json_report,
    generate_markdown_report,
    inject_custom_css,
    render_diff_html,
    render_hero_header,
    render_premium_card,
    render_roast_card,
)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="CodeRage | Multi-Agent Code Review & Debugger",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom Dark Mode CSS & Typography
inject_custom_css()

# Initialize session state variables
if "code_input" not in st.session_state:
    st.session_state.code_input = ""
if "error_log" not in st.session_state:
    st.session_state.error_log = ""
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "Python"
if "debug_results" not in st.session_state:
    st.session_state.debug_results = None
if "github_repo_files" not in st.session_state:
    st.session_state.github_repo_files = None
if "github_selected_url" not in st.session_state:
    st.session_state.github_selected_url = ""


def clear_pipeline_results():
    """Explicitly pops and clears all pipeline result keys, diagnostics, and telemetry from session state."""
    keys_to_clear = [
        "debug_results",
        "github_repo_files",
        "github_selected_url",
        "quiz_radio_choice",
    ]
    for k in keys_to_clear:
        st.session_state.pop(k, None)
    st.session_state.debug_results = None


def on_language_change():
    """Resets code input, error log, and explicitly clears all pipeline result keys when language changes."""
    st.session_state.code_input = ""
    st.session_state.error_log = ""
    clear_pipeline_results()


def apply_preset(language: str, preset_name: str):
    """Updates session state with selected code preset."""
    preset = SAMPLE_PRESETS.get(language, {}).get(preset_name)
    if preset:
        st.session_state.code_input = preset["code"]
        st.session_state.error_log = preset["error_log"]
        st.session_state.selected_language = language
        st.session_state.debug_results = None
        st.session_state.github_repo_files = None


# ==========================================
# SIDEBAR (CONFIGURATION & INGESTION)
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ System Configuration")
    
    # Gemini API Key configuration
    env_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    api_key_input = st.text_input(
        "🔑 Gemini API Key",
        value=env_api_key,
        type="password",
        help="Enter your Google Gemini API Key. If empty, the app runs in built-in offline simulation mode.",
        placeholder="AIzaSy...",
    )
    
    active_api_key = api_key_input.strip() or env_api_key

    # Model Selection
    model_choice = st.selectbox(
        "🧠 Gemini Model",
        options=["gemini-3.5-flash", "gemini-3.5-pro", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"],
        index=0,
        help="Select the Gemini model for multi-agent reasoning.",
    )

    st.markdown("---")

    # Target Language Selector
    st.markdown("### 🎯 Target Language")
    st.radio(
        "Select Programming Language",
        options=["Python", "C++", "Java"],
        horizontal=True,
        key="selected_language",
        on_change=on_language_change,
        label_visibility="collapsed",
    )

    st.markdown("---")
    
    # 1-Click Bug Presets
    st.markdown("### 🧪 1-Click Bug Presets")
    st.caption("Load pre-configured buggy student assignments:")

    preset_lang = st.session_state.selected_language
    preset_options = list(SAMPLE_PRESETS.get(preset_lang, {}).keys())
    selected_preset = st.selectbox(
        f"Select {preset_lang} Scenario",
        options=preset_options,
        key="preset_scenario_select",
    )

    if st.button("📥 Load Preset into Editor", use_container_width=True):
        apply_preset(preset_lang, selected_preset)
        st.toast(f"Loaded preset: {selected_preset} ({preset_lang})", icon="🧪")
        st.rerun()

    st.markdown("---")

    # GitHub Repository Ingestion in Sidebar
    st.markdown("### 🐙 GitHub Ingestion")
    with st.expander("Fetch Code from GitHub", expanded=False):
        st.caption("Paste a GitHub file URL or Repository URL:")
        github_url_input = st.text_input(
            "GitHub URL Input",
            value=st.session_state.github_selected_url,
            placeholder="https://github.com/user/repo/blob/main/file.py",
            label_visibility="collapsed",
            key="gh_sidebar_input",
        )
        fetch_btn = st.button("📥 Fetch Code", use_container_width=True, key="gh_fetch_btn")

        if fetch_btn:
            if not github_url_input.strip():
                st.error("Please enter a valid GitHub URL.")
            else:
                with st.spinner("Fetching data from GitHub API..."):
                    gh_res = fetch_github_resource(github_url_input.strip())
                    
                    if not gh_res.get("success"):
                        st.error(gh_res.get("error", "Failed to fetch from GitHub."))
                    else:
                        if gh_res.get("type") == "file":
                            st.session_state.code_input = gh_res.get("content", "")
                            st.session_state.error_log = ""
                            st.session_state.selected_language = gh_res.get("language", "Python")
                            st.session_state.github_repo_files = None
                            st.session_state.debug_results = None
                            st.toast(f"Loaded `{gh_res.get('filename')}` from GitHub ({gh_res.get('language')})", icon="🐙")
                            st.rerun()
                        
                        elif gh_res.get("type") == "repo_contents":
                            st.session_state.github_repo_files = gh_res.get("files", [])
                            st.session_state.github_selected_url = github_url_input.strip()
                            st.toast(f"Discovered repo files for `{gh_res.get('owner')}/{gh_res.get('repo')}`", icon="📁")

        # If repo contents were loaded, show file picker
        if st.session_state.github_repo_files:
            code_files = [f for f in st.session_state.github_repo_files if f.get("is_code") or f.get("type") == "file"]
            if code_files:
                file_options = {f"{f['name']} ({f['path']})": f for f in code_files}
                selected_file_label = st.selectbox("Select File from Repository:", options=list(file_options.keys()), key="gh_repo_file_select")
                
                if st.button("📂 Load Selected File", use_container_width=True, key="gh_load_file_btn"):
                    chosen = file_options[selected_file_label]
                    with st.spinner(f"Loading {chosen['name']}..."):
                        if chosen.get("download_url"):
                            f_res = fetch_github_resource(chosen["download_url"])
                        else:
                            f_res = fetch_github_resource(chosen.get("html_url", ""))
                        
                        if f_res.get("success"):
                            st.session_state.code_input = f_res.get("content", "")
                            st.session_state.error_log = ""
                            st.session_state.selected_language = f_res.get("language", "Python")
                            st.session_state.debug_results = None
                            st.toast(f"Loaded `{chosen['name']}` into the editor!", icon="📂")
                            st.rerun()
                        else:
                            st.error(f_res.get("error", "Failed to load chosen file."))
            else:
                st.warning("No code files found in top-level directory.")

    st.markdown("---")
    
    # Multi-Agent Architecture Status
    st.markdown("### 🤖 Active Agent Fleet")
    st.markdown(
        """
        <div style="font-size: 0.85rem; line-height: 1.6; color: #94a3b8;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="color: #38bdf8;">🔍</span> <b>Parser Agent:</b> AST & Error Extraction
            </div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="color: #34d399;">🛠️</span> <b>Fixer Agent:</b> Self-Healing Patch (Judge0)
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="color: #f87171;">🔥</span> <b>Tutor Agent:</b> Savage Roast & 3-Bullet Root Cause
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# MAIN WORKSPACE (HERO & CLEAN SPLIT)
# ==========================================

# Hero Section
render_hero_header()

# Side-by-Side Clean Split IDE
col_code, col_logs = st.columns([6, 4], gap="medium")

with col_code:
    st.markdown("#### 💻 Source Code Input")
    st.text_area(
        "Enter Buggy Assignment Code:",
        height=400,
        key="code_input",
        help="Paste the student source code here, load from presets, or ingest from GitHub in the sidebar.",
        placeholder="Paste your source code here...",
        label_visibility="collapsed",
    )

with col_logs:
    st.markdown("#### 🚨 Error Log & Diagnostics")
    st.text_area(
        "Compiler / Runtime Error Trace:",
        height=400,
        key="error_log",
        help="Paste any stack traces, compiler errors, or test failure logs here.",
        placeholder="e.g. IndexError: list index out of range\n  at line 6...\n(Optional: compiler errors will also be detected automatically by Judge0)",
        label_visibility="collapsed",
    )

# ==========================================
# THE ACTION CENTER
# ==========================================
col_act1, col_act2 = st.columns([5, 1], gap="small")

with col_act1:
    run_clicked = st.button("🚀 Run Self-Healing Debugger & Roast", use_container_width=True, type="primary")

with col_act2:
    if st.button("🧹 Clear Inputs", use_container_width=True):
        st.session_state.code_input = ""
        st.session_state.error_log = ""
        clear_pipeline_results()
        st.rerun()


# ==========================================
# EXECUTION PIPELINE (SELF-HEALING & ROAST)
# ==========================================
if run_clicked:
    if not st.session_state.code_input.strip():
        st.warning("⚠️ Please provide source code to debug.")
    else:
        # Clear previous pipeline results before starting
        clear_pipeline_results()

        try:
            with st.status("Initializing CodeRage Multi-Agent Pipeline...", expanded=True) as status:
                def update_progress(stage: str, pct: int, msg: str):
                    if "Parser" in stage or pct <= 30:
                        status.update(label=f"🔍 1. Parsing & Isolating Bug ({pct}%) — {msg}", state="running")
                        st.write(f"🔍 **Parser Agent:** {msg}")
                    elif "Fixer" in stage or (pct > 30 and pct <= 50):
                        status.update(label=f"🔧 2. Fixer Synthesizing Code Patch ({pct}%) — {msg}", state="running")
                        st.write(f"🔧 **Fixer Agent:** {msg}")
                    elif "Compiler" in stage or "Judge0" in stage or "Self-Healing" in stage or (pct > 50 and pct <= 75):
                        status.update(label=f"🧪 3. Judge0 Compilation & Self-Healing ({pct}%) — {msg}", state="running")
                        st.write(f"🧪 **Judge0 Sandbox:** {msg}")
                    elif "Tutor" in stage or pct > 75:
                        status.update(label=f"🔥 4. Tutor Roast & Pedagogical Review ({pct}%) — {msg}", state="running")
                        st.write(f"🔥 **Tutor Agent:** {msg}")
                    else:
                        status.update(label=f"⚡ {stage} ({pct}%) — {msg}", state="running")
                        st.write(f"⚡ **{stage}:** {msg}")

                orchestrator = MultiAgentOrchestrator(
                    api_key=active_api_key,
                    model_name=model_choice,
                )

                results = orchestrator.run_debug_workflow(
                    code=st.session_state.code_input,
                    language=st.session_state.selected_language,
                    error_log=st.session_state.error_log,
                    progress_callback=update_progress,
                )

                status.update(label="Review Complete", state="complete", expanded=False)

            st.session_state.debug_results = results
            st.toast("🎉 Self-Healing Analysis & Roast Complete!", icon="🚀")

        except Exception as e:
            st.error(f"🚨 Pipeline Execution Crash: {str(e)}")


# ==========================================
# RESULTS DISPLAY DASHBOARD
# ==========================================
if st.session_state.debug_results:
    results = st.session_state.debug_results
    parser = results.get("parser", {})
    fixer = results.get("fixer", {})
    tutor = results.get("tutor", {})
    judge0 = results.get("judge0", {})
    telemetry = results.get("telemetry", {})

    st.markdown("---")
    
    # Executive Summary Card with Judge0 Status Pill
    verified_pill = '<span class="badge-pill badge-emerald">🧪 Judge0: Verified</span>' if judge0.get('verified') else '<span class="badge-pill badge-amber">🧪 Judge0: Tested</span>'
    healed_pill = f'<span class="badge-pill badge-purple">✨ Self-Healed ({judge0.get("total_attempts")} attempts)</span>' if judge0.get("is_healed") else '<span class="badge-pill badge-cyan">⚡ 1st Pass Fix</span>'

    st.markdown(
        f"""
        <div class="glass-card" style="border-left: 4px solid #38bdf8; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
            <div>
                <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; font-weight: 700;">Diagnostic Verdict</div>
                <div style="font-size: 1.3rem; font-weight: 700; color: #f8fafc; margin-top: 2px;">{parser.get('bug_title', 'Core Defect Isolated')}</div>
                <div style="font-size: 0.88rem; color: #94a3b8; margin-top: 4px;">{parser.get('core_bug_summary', '')}</div>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <span class="badge-pill badge-rose">Severity: {parser.get('severity', 'High')}</span>
                {verified_pill}
                {healed_pill}
                <span class="badge-pill badge-cyan">⚡ {telemetry.get('total_duration_sec', 0)}s</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Result Tabs
    tab_tutor, tab_fixer, tab_parser, tab_export = st.tabs(
        [
            "🔥 1. Savage Roast & Tutor Review",
            "🛠️ 2. Clean Fixed Code & Judge0 Verification",
            "🔍 3. Parser Diagnostics & AST",
            "📥 4. Export Full Report",
        ]
    )

    # ------------------------------------------
    # TAB 1: TUTOR AGENT (SAVAGE ROAST & 3-BULLET EXPLANATION)
    # ------------------------------------------
    with tab_tutor:
        # FEATURE 3: RUTHLESS CODE ROAST SECTION
        roast_text = tutor.get("code_roast", "")
        if roast_text:
            render_roast_card(roast_text)

        st.markdown("### 🎓 Root Cause Analysis & Pedagogical Review")
        st.caption("Structured 3-bullet breakdown explaining the trigger, runtime mechanics, and golden rules:")

        # Strict 3-Bullet Root Cause Cards
        bullets = tutor.get("three_bullet_root_cause", [])
        if bullets:
            for idx, bullet in enumerate(bullets, start=1):
                clean_bullet = bullet.lstrip("• ")
                st.markdown(
                    f"""
                    <div class="tutor-bullet">
                        <div class="tutor-bullet-num">{idx}</div>
                        <div>{clean_bullet}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Core Concept & Pro Tip Card
        col_c1, col_c2 = st.columns([3, 2], gap="medium")
        with col_c1:
            render_premium_card(
                title=tutor.get("core_concept_title", "Defensive Programming & Bounds"),
                icon="💡",
                content=tutor.get("core_concept_summary", ""),
                subtitle="Core Computer Science Concept",
                border_color="rgba(168, 85, 247, 0.35)",
            )

        with col_c2:
            render_premium_card(
                title="Golden Pro-Tip",
                icon="✨",
                content=tutor.get("pro_tip", "Always validate inputs at function boundaries."),
                subtitle="Instructor Recommendation",
                border_color="rgba(52, 211, 153, 0.35)",
            )

        # Interactive Quiz / Knowledge Check
        quiz = tutor.get("concept_quiz")
        if quiz and isinstance(quiz, dict) and "question" in quiz and "options" in quiz:
            st.markdown("#### 🧠 Quick Concept Check")
            st.write(quiz.get("question", ""))
            
            options = quiz.get("options", [])
            correct_idx = quiz.get("correct_index", 0)
            
            selected_option = st.radio(
                "Choose the correct statement:",
                options=options,
                key="quiz_radio_choice",
            )

            if st.button("Check My Answer"):
                user_idx = options.index(selected_option) if selected_option in options else -1
                if user_idx == correct_idx:
                    st.success(f"🎉 **Correct!** {quiz.get('explanation', '')}")
                else:
                    st.error(f"❌ **Not quite.** {quiz.get('explanation', '')}")

    # ------------------------------------------
    # TAB 2: FIXER AGENT & FEATURE 2: JUDGE0 SELF-HEALING
    # ------------------------------------------
    with tab_fixer:
        st.markdown("### 🛠️ Corrected, Production-Ready Code & Compiler Verification")
        
        # FEATURE 2: Judge0 Self-Healing Visualizer
        loop_history = judge0.get("loop_history", [])
        if loop_history:
            st.markdown("#### 🧪 Judge0 Self-Healing Compilation Timeline")
            t_cols = st.columns(len(loop_history))
            for i, rec in enumerate(loop_history):
                with t_cols[i]:
                    stat_badge = "✅ Passed" if rec.get("success") else "❌ Failed"
                    st.markdown(
                        f"""
                        <div class="glass-card" style="padding: 10px 14px; text-align: center; border-color: {'rgba(52, 211, 153, 0.4)' if rec.get('success') else 'rgba(239, 68, 68, 0.4)'};">
                            <div style="font-weight: 700; font-size: 0.85rem; color: #38bdf8;">Attempt #{rec.get('attempt')}</div>
                            <div style="font-size: 0.95rem; font-weight: 700; color: {'#34d399' if rec.get('success') else '#f87171'}; margin-top: 4px;">{stat_badge}</div>
                            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">{rec.get('status_description', '')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            if judge0.get("warning"):
                st.warning(f"⚠️ {judge0.get('warning')}")

            with st.expander("🔍 View Judge0 Compiler Logs & Output", expanded=False):
                st.write("**Status Description:**", judge0.get("status_description"))
                if judge0.get("stdout"):
                    st.write("**Stdout:**")
                    st.code(judge0.get("stdout"))
                if judge0.get("stderr") or judge0.get("compile_output"):
                    st.write("**Compiler Stderr / Output:**")
                    st.code(judge0.get("stderr") or judge0.get("compile_output"))

        # Complexity Metrics Bar
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            st.metric("Time Complexity", fixer.get("time_complexity", "O(N)"))
        with m_col2:
            st.metric("Space Complexity", fixer.get("space_complexity", "O(1)"))
        with m_col3:
            st.metric("Fixer & Compiler Duration", f"{telemetry.get('fixer_duration_sec', 0)}s")

        # Code View Tabs: Fixed Code vs. Unified Diff vs. Patches
        sub_tab_code, sub_tab_diff, sub_tab_patches = st.tabs(["✨ Fixed Code", "🔍 Unified Diff Viewer", "📋 Patch Breakdown"])

        with sub_tab_code:
            st.code(
                fixer.get("fixed_code", "// No code generated"),
                language=results.get("language", "python").lower(),
                line_numbers=True,
            )

        with sub_tab_diff:
            st.caption("Line-by-line diff comparison between original submission and clean patch:")
            diff_text = fixer.get("diff", "")
            st.markdown(render_diff_html(diff_text), unsafe_allow_html=True)

        with sub_tab_patches:
            st.markdown("#### 🔧 Specific Modifications Applied:")
            for p in fixer.get("patch_summary", []):
                st.markdown(f"- **{p}**")

            st.markdown("#### ⚡ Optimizations & Modernization:")
            for opt in fixer.get("optimizations_applied", []):
                st.markdown(f"- 🚀 {opt}")

    # ------------------------------------------
    # TAB 3: PARSER AGENT (DIAGNOSTICS & AST)
    # ------------------------------------------
    with tab_parser:
        st.markdown("### 🔍 Parser Agent Diagnostics & Code Inspection")
        
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            render_premium_card(
                title=f"Affected Scope: {parser.get('impacted_lines', 'Primary Execution Path')}",
                icon="📍",
                content=parser.get("trigger_mechanism", "Unhandled condition triggered at runtime."),
                subtitle="Trigger Mechanism & Line Scope",
                border_color="rgba(56, 189, 248, 0.35)",
            )

        with p_col2:
            sec_issues = "\n".join([f"• {s}" for s in parser.get("secondary_issues", [])]) or "No secondary anti-patterns found."
            render_premium_card(
                title="Secondary Anti-Patterns Detected",
                icon="⚠️",
                content=sec_issues,
                subtitle="Static Inspection Feedback",
                border_color="rgba(251, 191, 36, 0.35)",
            )

    # ------------------------------------------
    # TAB 4: EXPORT REPORT
    # ------------------------------------------
    with tab_export:
        st.markdown("### 📥 Export & Share Debug Report")
        st.caption("Download the complete multi-agent review report as a formatted Markdown or JSON document.")

        exp_col1, exp_col2 = st.columns(2)
        with exp_col1:
            st.download_button(
                label="📥 Download Markdown Report (.md)",
                data=generate_markdown_report(results),
                file_name="CodeRage_Debug_Report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with exp_col2:
            st.download_button(
                label="📥 Download Structured JSON Report (.json)",
                data=generate_json_report(results),
                file_name="CodeRage_Debug_Report.json",
                mime="application/json",
                use_container_width=True,
            )
