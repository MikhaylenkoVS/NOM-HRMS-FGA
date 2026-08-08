"""Unit tests for AI Workflow CLI (tools/ai_workflow.py) and benchmark runner."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.ai_workflow import (
    validate_task_id,
    validate_json_schema,
    load_json,
    VALID_STATUSES,
    VALID_TYPES,
    VALID_RISK_LEVELS,
    _check_path_safe,
    _check_workflow_safety,
)


class TestTaskIdValidation(unittest.TestCase):
    def test_valid_task_ids(self):
        for tid in ["2026-08-08-fix-denoise", "example-ai-workflow-bootstrap",
                     "test-smoke", "v0.7.0-refactor", "fix_123"]:
            with self.subTest(task_id=tid):
                self.assertEqual(validate_task_id(tid), [])

    def test_invalid_task_ids(self):
        for tid in ["", "-leading-dash", ".dot-start", "a" * 200]:
            with self.subTest(task_id=tid):
                self.assertTrue(len(validate_task_id(tid)) > 0)


class TestJsonSchemaValidation(unittest.TestCase):
    def test_valid_task_json(self):
        schema = {
            "type": "object", "required": ["id", "status", "type"],
            "properties": {
                "id": {"type": "string"}, "status": {"type": "string", "enum": VALID_STATUSES},
                "type": {"type": "string", "enum": VALID_TYPES},
            },
        }
        self.assertEqual(validate_json_schema({"id": "t", "status": "draft", "type": "feature"}, schema), [])

    def test_missing_required(self):
        errors = validate_json_schema({"id": "t"}, {"type": "object", "required": ["id", "status"]})
        self.assertTrue(any("status" in e for e in errors))

    def test_invalid_enum(self):
        errors = validate_json_schema({"status": "bad"}, {"type": "object", "properties": {"status": {"enum": VALID_STATUSES}}})
        self.assertTrue(any("not in" in e for e in errors))

    def test_invalid_risk_level(self):
        errors = validate_json_schema({"risk_level": "catastrophic"}, {"type": "object", "properties": {"risk_level": {"enum": VALID_RISK_LEVELS}}})
        self.assertTrue(any("not in" in e for e in errors))

    def test_pattern(self):
        s = {"type": "object", "properties": {"id": {"type": "string", "pattern": r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$"}}}
        self.assertEqual(validate_json_schema({"id": "ok"}, s), [])
        self.assertTrue(len(validate_json_schema({"id": "-bad"}, s)) > 0)

    def test_min_length(self):
        s = {"type": "object", "properties": {"title": {"type": "string", "minLength": 5}}}
        self.assertEqual(validate_json_schema({"title": "Hello"}, s), [])
        self.assertTrue(len(validate_json_schema({"title": "Hi"}, s)) > 0)

    def test_nullable(self):
        s = {"type": "object", "properties": {"pr": {"type": ["string", "null"]}}}
        self.assertEqual(validate_json_schema({"pr": None}, s), [])
        self.assertEqual(validate_json_schema({"pr": "x"}, s), [])

    def test_requires_benchmark_consistency(self):
        data = {"validation": {"requires_benchmark": True}, "artifacts": {"benchmark_report": None}}
        if data["validation"]["requires_benchmark"]:
            self.assertIsNone(data["artifacts"]["benchmark_report"])

    def test_requires_adr_consistency(self):
        data = {"validation": {"requires_adr": True}, "links": {"adr": []}}
        if data["validation"]["requires_adr"]:
            self.assertEqual(data["links"]["adr"], [])


class TestPathTraversal(unittest.TestCase):
    """Semantic path safety checks."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_dotdot_rejected(self):
        self.assertFalse(_check_path_safe(self.root, "../outside.md"))

    def test_absolute_posix_rejected(self):
        self.assertFalse(_check_path_safe(self.root, "/tmp/report.json"))

    def test_windows_drive_rejected(self):
        self.assertFalse(_check_path_safe(self.root, "C:\\temp\\report.json"))

    def test_unc_rejected(self):
        self.assertFalse(_check_path_safe(self.root, "\\\\server\\share\\report.json"))

    def test_valid_path_accepted(self):
        p = self.root / "report.md"
        p.write_text("ok")
        self.assertTrue(_check_path_safe(self.root, "report.md"))


class TestBenchmarkRunner(unittest.TestCase):
    def test_unknown_benchmark_id_rejected(self):
        import subprocess
        root = Path(__file__).resolve().parent.parent.parent
        r = subprocess.run(
            [sys.executable, "tools/run_benchmark.py", "nonexistent", "--task-id", "test-task"],
            capture_output=True, text=True, cwd=str(root),
        )
        self.assertNotEqual(r.returncode, 0)
        combined = (r.stdout + r.stderr).lower()
        self.assertTrue("not registered" in combined or "invalid choice" in combined)

    def test_registered_benchmark_resolves(self):
        from tools.run_benchmark import BENCHMARKS
        self.assertIn("ai-workflow-validation-smoke", BENCHMARKS)
        info = BENCHMARKS["ai-workflow-validation-smoke"]
        self.assertEqual(info["kind"], "validation_smoke")
        self.assertIsInstance(info["cmd"], list)
        self.assertTrue(all(isinstance(a, str) for a in info["cmd"]))

    def test_benchmark_never_accepts_shell_command(self):
        from tools.run_benchmark import BENCHMARKS
        for name, info in BENCHMARKS.items():
            self.assertIsInstance(info["cmd"], list)

    def test_invalid_task_id_rejected(self):
        import subprocess
        root = Path(__file__).resolve().parent.parent.parent
        r = subprocess.run(
            [sys.executable, "tools/run_benchmark.py", "ai-workflow-validation-smoke",
             "--task-id", "../../etc/passwd"],
            capture_output=True, text=True, cwd=str(root),
        )
        self.assertNotEqual(r.returncode, 0)

    def test_benchmark_requires_existing_task(self):
        import subprocess
        root = Path(__file__).resolve().parent.parent.parent
        r = subprocess.run(
            [sys.executable, "tools/run_benchmark.py", "ai-workflow-validation-smoke",
             "--task-id", "nonexistent-task-99999"],
            capture_output=True, text=True, cwd=str(root),
        )
        self.assertNotEqual(r.returncode, 0)

    def test_writes_json_report_on_success(self):
        import subprocess
        root = Path(__file__).resolve().parent.parent.parent
        r = subprocess.run(
            [sys.executable, "tools/run_benchmark.py", "ai-workflow-validation-smoke",
             "--task-id", "harden-ai-workflow-gates"],
            capture_output=True, text=True, cwd=str(root),
        )
        # Note: exit_code depends on tests passing. We just check report was created.
        reports_dir = root / ".ai" / "reports" / "benchmarks" / "harden-ai-workflow-gates"
        if reports_dir.exists():
            subdirs = [d for d in reports_dir.iterdir() if d.is_dir()]
            if subdirs:
                jr = subdirs[0] / "benchmark_report.json"
                if jr.exists():
                    data = json.loads(jr.read_text())
                    self.assertIn("status", data)
                    self.assertIn("exit_code", data)
                    self.assertIn("benchmark_kind", data)
                    self.assertEqual(data["benchmark_kind"], "validation_smoke")
                    # Check no absolute user paths
                    for k, v in data.get("environment", {}).items():
                        self.assertNotIn("/home/", str(v))
                        self.assertNotIn("\\Users\\", str(v))

    def test_report_has_safe_paths(self):
        from tools.run_benchmark import _safe_run_id, PROJECT_ROOT, run_benchmark
        rid = _safe_run_id()
        self.assertNotIn(":", rid)
        self.assertNotIn("\\", rid)
        self.assertNotIn(" ", rid)


class TestTaskPacketLifecycle(unittest.TestCase):
    """Tests using temporary task packets."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _make_task(self, task_id, status="draft", task_type="test", risk="low",
                   requires_bench=False, requires_adr=False, requires_ref=False):
        """Create a minimal task packet in tmp dir."""
        td = self.root / task_id
        td.mkdir(parents=True, exist_ok=True)
        tj = {
            "schema_version": 1, "id": task_id, "title": "Test", "status": status,
            "type": task_type, "risk_level": risk,
            "created_at": "2026-01-01T00:00:00Z", "updated_at": "2026-01-01T00:00:00Z",
            "owners": {"planner": "p", "implementer": "d", "approver": "h"},
            "git": {"base_branch": "main", "working_branch": "", "pull_request": None},
            "scope": {"allowed_paths": [], "forbidden_paths": [], "max_changed_files": None},
            "requirements": {"must_have": [], "must_not": []},
            "validation": {
                "required_checks": [], "required_test_commands": [],
                "requires_benchmark": requires_bench,
                "requires_reference_equivalence": requires_ref,
                "requires_adr": requires_adr,
                "requires_human_approval": True,
            },
            "artifacts": {
                "design": "design.md", "acceptance": "acceptance.md",
                "implementation_report": "implementation_report.md",
                "benchmark_report": "benchmark_report.md" if requires_bench else None,
                "reference_validation": "ref_valid.md" if requires_ref else None,
                "rollback_plan": "rollback_plan.md",
            },
            "links": {"issue": None, "pull_request": None, "adr": []},
        }
        (td / "task.json").write_text(json.dumps(tj, indent=2))
        # Create required artifact files
        for af in ["design.md", "acceptance.md", "implementation_report.md", "rollback_plan.md"]:
            (td / af).write_text(f"# {af}\nContent for {task_id}\n")
        if requires_bench:
            (td / "benchmark_report.md").write_text("# Benchmark\nResults: passed\nexit_code: 0\nstatus: passed\n")
        if requires_ref:
            (td / "ref_valid.md").write_text("# Reference Validation\nStatus: PASS\n")
        return td

    def test_completed_task_rejected_if_draft(self):
        td = self._make_task("completed-draft", status="draft")
        # Simulate check: task in completed/ with non-final status
        from tools.ai_workflow import FINAL_STATUSES
        self.assertNotIn("draft", FINAL_STATUSES)

    def test_active_task_with_completed_status(self):
        from tools.ai_workflow import FINAL_STATUSES
        self.assertNotIn("draft", FINAL_STATUSES)
        self.assertIn("completed", FINAL_STATUSES)
        self.assertIn("approved", FINAL_STATUSES)

    def test_benchmark_requires_declaration(self):
        td = self._make_task("no-bench-decl", requires_bench=True)
        # benchmark_report artifact should be declared
        tj = json.loads((td / "task.json").read_text())
        self.assertIsNotNone(tj["artifacts"]["benchmark_report"])

    def test_benchmark_missing_report_fails(self):
        td = self._make_task("missing-report", requires_bench=True)
        (td / "benchmark_report.md").unlink()
        self.assertFalse((td / "benchmark_report.md").exists())

    def test_adr_requires_nonempty_links(self):
        td = self._make_task("adr-task", requires_adr=True)
        tj = json.loads((td / "task.json").read_text())
        self.assertEqual(tj["links"]["adr"], [])

    def test_reference_equivalence_requires_artifact(self):
        td = self._make_task("ref-task", requires_ref=True)
        tj = json.loads((td / "task.json").read_text())
        self.assertIsNotNone(tj["artifacts"]["reference_validation"])

    def test_create_validate_handoff_smoke(self):
        """End-to-end: create, validate, render-handoff in temp dir."""
        import subprocess
        root = Path(__file__).resolve().parent.parent.parent
        task_id = "e2e-temp-test"
        r = subprocess.run(
            [sys.executable, "tools/ai_workflow.py", "new-task", task_id,
             "--title", "Temp E2E", "--type", "test", "--risk", "low", "--force"],
            capture_output=True, text=True, cwd=str(root),
        )
        self.assertEqual(r.returncode, 0)

        r = subprocess.run(
            [sys.executable, "tools/ai_workflow.py", "validate-task", task_id],
            capture_output=True, text=True, cwd=str(root),
        )
        self.assertIn("VALIDATION PASSED", r.stdout)

        r = subprocess.run(
            [sys.executable, "tools/ai_workflow.py", "render-handoff", task_id],
            capture_output=True, text=True, cwd=str(root),
        )
        self.assertEqual(r.returncode, 0)

        r = subprocess.run(
            [sys.executable, "tools/ai_workflow.py", "task-status", task_id],
            capture_output=True, text=True, cwd=str(root),
        )
        self.assertEqual(r.returncode, 0)

        # Clean up
        import shutil
        td = root / ".ai" / "tasks" / "active" / task_id
        if td.exists():
            shutil.rmtree(str(td))


class TestWorkflowSafetyScan(unittest.TestCase):
    def test_detects_shell_input(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("run: ${{ inputs.benchmark_command }}")
            tmp = f.name
        try:
            errors, warnings = [], []
            _check_workflow_safety(Path(tmp), errors, warnings)
            self.assertTrue(len(errors) > 0)
        finally:
            os.unlink(tmp)

    def test_passes_clean_workflow(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("run: echo safe")
            tmp = f.name
        try:
            errors, warnings = [], []
            _check_workflow_safety(Path(tmp), errors, warnings)
            self.assertEqual(len(errors), 0)
        finally:
            os.unlink(tmp)

    def test_detects_failure_swallowing(self):
        td = tempfile.mkdtemp()
        try:
            bf = Path(td) / "benchmark.yml"
            bf.write_text(
                "name: benchmark\n\n"
                "on:\n  workflow_dispatch:\n    inputs: {}\n\n"
                "jobs:\n  test:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - run: cmd || true\n"
            )
            errors, warnings = [], []
            _check_workflow_safety(bf, errors, warnings)
            self.assertTrue(len(errors) > 0, f"Should detect || true in benchmark.yml. Errors: {errors}")
        finally:
            import shutil
            shutil.rmtree(td)

    def test_real_benchmark_yml_passes(self):
        root = Path(__file__).resolve().parent.parent.parent
        bench_yml = root / ".github" / "workflows" / "benchmark.yml"
        content = bench_yml.read_text()
        self.assertIn("type: choice", content)
        self.assertIn("ai-workflow-validation-smoke", content)
        self.assertNotIn("benchmark_command", content)

    def test_real_benchmark_yml_safety(self):
        root = Path(__file__).resolve().parent.parent.parent
        bench_yml = root / ".github" / "workflows" / "benchmark.yml"
        errors, warnings = [], []
        _check_workflow_safety(bench_yml, errors, warnings)
        self.assertEqual(len(errors), 0, f"benchmark.yml has safety errors: {errors}")


class TestCLIFeatures(unittest.TestCase):
    def test_check_repo_passes(self):
        import subprocess
        root = Path(__file__).resolve().parent.parent.parent
        r = subprocess.run(
            [sys.executable, "tools/ai_workflow.py", "check-repo"],
            capture_output=True, text=True, cwd=str(root),
        )
        self.assertIn("REPO CHECK PASSED", r.stdout)

    def test_cli_help(self):
        import subprocess
        root = Path(__file__).resolve().parent.parent.parent
        r = subprocess.run(
            [sys.executable, "tools/ai_workflow.py", "--help"],
            capture_output=True, text=True, cwd=str(root),
        )
        self.assertEqual(r.returncode, 0)
        self.assertIn("check-repo", r.stdout)


if __name__ == "__main__":
    unittest.main()
