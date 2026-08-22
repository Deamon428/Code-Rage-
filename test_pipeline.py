"""
Automated unit and integration test suite for the upgraded Multi-Agent Pipeline.
Verifies GitHub Fetching, Judge0 Self-Healing Loop, Savage Roast Tutor, and Exporters.
"""

import sys
from agents.orchestrator import MultiAgentOrchestrator
from data.sample_presets import SAMPLE_PRESETS
from utils.github_fetcher import fetch_github_resource, parse_github_url
from utils.judge0_client import Judge0Compiler
from utils.ui_helpers import generate_markdown_report, generate_json_report


def test_github_ingestion():
    print("\n--- Testing Feature 1: GitHub Ingestion Engine ---")
    
    # 1. Test URL parser and blob to raw conversion
    from utils.github_fetcher import convert_blob_to_raw_url, DEFAULT_USER_AGENT, DEFAULT_TIMEOUT
    
    blob_url = "https://github.com/octocat/Hello-World/blob/master/file.py"
    raw_converted = convert_blob_to_raw_url(blob_url)
    assert raw_converted == "https://raw.githubusercontent.com/octocat/Hello-World/master/file.py", f"Conversion failed: {raw_converted}"
    print(f"  [Raw Converter] '{blob_url}' -> '{raw_converted}'")

    assert DEFAULT_USER_AGENT == "CodeRage-App", f"User-Agent should be CodeRage-App, got {DEFAULT_USER_AGENT}"
    assert DEFAULT_TIMEOUT == 10, f"Timeout should be 10, got {DEFAULT_TIMEOUT}"
    print(f"  [Config] Verified User-Agent: {DEFAULT_USER_AGENT}, Timeout: {DEFAULT_TIMEOUT}s")

    parsed_blob = parse_github_url(blob_url)
    assert parsed_blob["type"] == "file", f"Expected 'file', got {parsed_blob['type']}"
    assert parsed_blob["owner"] == "octocat"
    assert parsed_blob["repo"] == "Hello-World"
    assert parsed_blob["raw_url"] == "https://raw.githubusercontent.com/octocat/Hello-World/master/file.py"
    print("  [URL Parser] Successfully parsed GitHub blob URL with automatic raw conversion.")

    repo_url = "https://github.com/octocat/Hello-World"
    parsed_repo = parse_github_url(repo_url)
    assert parsed_repo["type"] == "repo_root", f"Expected 'repo_root', got {parsed_repo['type']}"
    print("  [URL Parser] Successfully parsed GitHub repo root URL.")

    # 2. Test Error handling for non-existent repo
    invalid_url = "https://github.com/octocat/non-existent-repo-123456789/blob/main/bad.py"
    res = fetch_github_resource(invalid_url)
    assert not res["success"], "Expected failure for non-existent repo"
    assert "error" in res and len(res["error"]) > 0, "Expected error message in response"
    print(f"  [Error Guard] Gracefully handled invalid/non-existent repository: {res['error'][:50]}...")

    # 3. Test 100k Character Limit Guard
    from utils.github_fetcher import MAX_FILE_SIZE_CHARS, FILE_TOO_LARGE_ERROR
    assert MAX_FILE_SIZE_CHARS == 100000
    assert "100,000 character limit" in FILE_TOO_LARGE_ERROR
    print(f"  [Size Limit Guard] Verified 100,000 char threshold: '{FILE_TOO_LARGE_ERROR}'")


def test_judge0_compiler():
    print("\n--- Testing Feature 2: Judge0 Compiler & Self-Healing ---")
    compiler = Judge0Compiler()
    
    # Test valid Python code compilation
    py_code = "print('Hello Judge0!')"
    res = compiler.compile_and_run(py_code, "Python")
    assert res["success"], f"Judge0 compilation failed: {res}"
    print(f"  [Judge0 Client] Compilation Test -> Status: {res['status_description']} (Success: {res['success']})")

    # Test Judge0 SIGKILL / OOM edge case fallback handling
    sim_oom = compiler._offline_validation("while True: pass", "Python", "Runtime Error (SIGKILL)")
    assert sim_oom is not None
    print(f"  [Judge0 OOM/SIGKILL Guard] Verified resilient fallback: {sim_oom['status_description']}")

    # Test Parser Agent with NoneType error log
    from agents.parser import ParserAgent
    parser = ParserAgent()
    none_diag = parser.parse_bug("def foo(): return 1", "Python", error_log=None)
    assert none_diag is not None
    assert "bug_title" in none_diag
    print(f"  [Parser NoneType Guard] Successfully parsed bug with error_log=None: '{none_diag['bug_title']}'")


def test_multi_agent_pipeline_with_roast_and_self_healing():
    print("\n--- Testing Feature 2 & 3: End-to-End Pipeline with Roast & Self-Healing ---")
    orchestrator = MultiAgentOrchestrator()

    for lang in ["Python", "C++", "Java"]:
        print(f"\n--- Testing Language: {lang} ---")
        presets = SAMPLE_PRESETS[lang]
        first_preset_name = list(presets.keys())[0]
        preset_data = presets[first_preset_name]

        print(f"Scenario: {first_preset_name}")
        results = orchestrator.run_debug_workflow(
            code=preset_data["code"],
            language=lang,
            error_log=preset_data["error_log"]
        )

        # 1. Verify Parser Agent
        parser = results.get("parser", {})
        assert "bug_title" in parser, "Parser output missing 'bug_title'"
        assert "severity" in parser, "Parser output missing 'severity'"
        print(f"  [Parser Agent] Isolated Bug: '{parser['bug_title']}' (Severity: {parser['severity']})")

        # 2. Verify Fixer Agent & Judge0 Loop
        fixer = results.get("fixer", {})
        judge0 = results.get("judge0", {})
        assert "fixed_code" in fixer, "Fixer output missing 'fixed_code'"
        assert "diff" in fixer, "Fixer output missing 'diff'"
        assert "total_attempts" in judge0, "Judge0 telemetry missing 'total_attempts'"
        print(f"  [Fixer & Judge0] Attempts: {judge0['total_attempts']}, Verified: {judge0['verified']}, Status: {judge0.get('status_description')}")

        # 3. Verify Tutor Agent (Savage Roast + Strict 3-bullet rule)
        tutor = results.get("tutor", {})
        assert "code_roast" in tutor and len(tutor["code_roast"]) > 30, "Tutor output missing or too short 'code_roast'"
        assert "three_bullet_root_cause" in tutor, "Tutor output missing 'three_bullet_root_cause'"
        bullets = tutor["three_bullet_root_cause"]
        assert len(bullets) == 3, f"Expected exactly 3 bullet points from Tutor, got {len(bullets)}"
        
        roast_snippet = tutor['code_roast'][:80].replace('\n', ' ') + '...'
        print(f"  [Tutor Roast] {roast_snippet}")
        print(f"  [Tutor 3-Bullet] Generated {len(bullets)} root cause bullets & Concept: '{tutor.get('core_concept_title')}'")

        # 4. Verify Enhanced Report Generators
        md_report = generate_markdown_report(results)
        json_report = generate_json_report(results)
        assert "Savage Code Roast" in md_report, "Markdown report missing Roast section"
        assert "Judge0 Verification" in md_report, "Markdown report missing Judge0 section"
        print(f"  [Reports] Generated Markdown ({len(md_report)} chars) and JSON ({len(json_report)} chars)")


if __name__ == "__main__":
    print("================================================================")
    print("🧪 Running Comprehensive Test Suite (Features 1, 2, and 3)")
    print("================================================================")
    try:
        test_github_ingestion()
        test_judge0_compiler()
        test_multi_agent_pipeline_with_roast_and_self_healing()
        print("\n================================================================")
        print("✅ ALL TESTS PASSED SUCCESSFULLY! All 3 Features Verified.")
        print("================================================================")
    except Exception as e:
        import traceback
        print(f"\n❌ Test Failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)
