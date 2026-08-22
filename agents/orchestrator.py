"""
Multi-Agent Orchestrator: Coordinates the self-healing pipeline between
Parser Agent, Fixer Agent (with Judge0 compiler verification & retries), and Tutor Agent.
"""

import time
from typing import Any, Callable, Dict, List, Optional

from agents.parser import ParserAgent
from agents.fixer import FixerAgent
from agents.tutor import TutorAgent
from utils.judge0_client import Judge0Compiler


class MultiAgentOrchestrator:
    """Coordinates execution across Parser, Fixer (self-healing), and Tutor agents."""

    MAX_RETRIES: int = 2

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-3.5-flash",
        judge0_url: Optional[str] = None,
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.parser_agent = ParserAgent(api_key=api_key, model_name=model_name)
        self.fixer_agent = FixerAgent(api_key=api_key, model_name=model_name)
        self.tutor_agent = TutorAgent(api_key=api_key, model_name=model_name)
        self.compiler = Judge0Compiler(api_url=judge0_url)

    def run_debug_workflow(
        self,
        code: str,
        language: str,
        error_log: str = "",
        progress_callback: Optional[Callable[[str, int, str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Executes the self-healing multi-agent pipeline:
        1. Stage 1: Parser Agent analyzes code and error logs.
        2. Stage 2: Fixer Agent generates initial code patch.
        3. Stage 2.5: Self-Healing Loop -> Compiles via Judge0.
           If errors occur, feeds stderr/compile_output back to Fixer (up to MAX_RETRIES=2).
        4. Stage 3: Tutor Agent generates Roast + 3-bullet explanation and teaching concepts.

        Returns aggregated results dictionary.
        """
        overall_start = time.perf_counter()

        def notify(stage_name: str, step_pct: int, status_msg: str):
            if progress_callback:
                progress_callback(stage_name, step_pct, status_msg)

        # ----------------------------------------------------
        # Stage 1: Parser Agent
        # ----------------------------------------------------
        notify("Parser Agent", 15, "🔍 Parser Agent analyzing syntax, AST, and error trace...")
        t0 = time.perf_counter()
        parser_result = self.parser_agent.parse_bug(
            code=code,
            language=language,
            error_log=error_log
        )
        parser_time = round(time.perf_counter() - t0, 2)
        notify("Parser Agent", 30, f"✅ Bug isolated: {parser_result.get('bug_title', 'Identified')}")

        # ----------------------------------------------------
        # Stage 2: Fixer Agent & Self-Healing Loop with Judge0
        # ----------------------------------------------------
        notify("Fixer Agent", 40, "🛠️ Fixer Agent synthesizing initial code patch...")
        t1 = time.perf_counter()
        
        loop_history: List[Dict[str, Any]] = []
        current_attempt = 0
        compilation_feedback: Optional[str] = None
        current_fixer_result: Dict[str, Any] = {}
        judge0_result: Dict[str, Any] = {}
        is_healed = False
        warning_msg: Optional[str] = None

        while current_attempt <= self.MAX_RETRIES:
            # Step A: Fixer Agent generates/refines patch
            current_fixer_result = self.fixer_agent.fix_code(
                code=code,
                language=language,
                parser_diagnosis=parser_result,
                error_log=error_log,
                compilation_feedback=compilation_feedback,
                retry_attempt=current_attempt,
            )

            candidate_code = current_fixer_result.get("fixed_code", "")
            
            # Step B: Test with Judge0 Compiler
            attempt_label = f"Attempt #{current_attempt + 1}"
            notify("Compiler Loop", 45 + (current_attempt * 10), f"⚡ Testing patch on Judge0 ({attempt_label})...")
            
            judge0_result = self.compiler.compile_and_run(
                source_code=candidate_code,
                language=language,
            )

            record = {
                "attempt": current_attempt + 1,
                "status_id": judge0_result.get("status_id"),
                "status_description": judge0_result.get("status_description"),
                "success": judge0_result.get("success"),
                "error_text": judge0_result.get("error_text"),
                "stdout": judge0_result.get("stdout"),
                "is_simulation": judge0_result.get("is_simulation", False),
            }
            loop_history.append(record)

            # Check if Judge0 verified the code
            if judge0_result.get("success", False):
                is_healed = (current_attempt > 0)
                notify("Compiler Loop", 70, f"✅ Compilation verified on Judge0 ({attempt_label}: {judge0_result.get('status_description')})")
                break

            # If failed, prepare retry feedback
            current_attempt += 1
            if current_attempt <= self.MAX_RETRIES:
                compilation_feedback = judge0_result.get("error_text") or judge0_result.get("status_description")
                notify(
                    "Self-Healing Fixer",
                    50 + (current_attempt * 10),
                    f"⚠️ Compilation failed. Triggering Self-Healing Retry #{current_attempt}..."
                )
            else:
                warning_msg = f"Self-healing limit reached ({self.MAX_RETRIES} retries). Returning latest candidate code."
                notify("Compiler Loop", 70, f"⚠️ {warning_msg}")

        fixer_time = round(time.perf_counter() - t1, 2)

        # ----------------------------------------------------
        # Stage 3: Tutor Agent (Roast + 3-Bullet Root Cause)
        # ----------------------------------------------------
        notify("Tutor Agent", 80, "🔥 Tutor Agent roasting code & crafting 3-bullet pedagogical breakdown...")
        t2 = time.perf_counter()
        tutor_result = self.tutor_agent.explain_root_cause(
            code=code,
            language=language,
            parser_diagnosis=parser_result,
            fixer_output=current_fixer_result,
            error_log=error_log
        )
        tutor_time = round(time.perf_counter() - t2, 2)
        notify("Completed", 100, "🚀 Multi-agent debugging, self-healing & roast complete!")

        total_elapsed = round(time.perf_counter() - overall_start, 2)

        return {
            "language": language,
            "original_code": code,
            "error_log": error_log,
            "parser": parser_result,
            "fixer": current_fixer_result,
            "tutor": tutor_result,
            "judge0": {
                "verified": judge0_result.get("success", False),
                "is_healed": is_healed,
                "total_attempts": len(loop_history),
                "status_id": judge0_result.get("status_id"),
                "status_description": judge0_result.get("status_description"),
                "stdout": judge0_result.get("stdout"),
                "stderr": judge0_result.get("stderr"),
                "compile_output": judge0_result.get("compile_output"),
                "warning": warning_msg,
                "loop_history": loop_history,
                "is_simulation": judge0_result.get("is_simulation", False),
            },
            "telemetry": {
                "total_duration_sec": total_elapsed,
                "parser_duration_sec": parser_time,
                "fixer_duration_sec": fixer_time,
                "tutor_duration_sec": tutor_time,
                "model_name": self.model_name,
                "has_api_key": bool(self.api_key),
            }
        }
