# Design: Fix artifact contracts and semantic validation

## Problem
Benchmark runner produced no structured reports. requires_* checks were
warnings, not errors. Path traversal check was string-based, not resolve()-based.
Workflow safety scan had weak pattern matching.

## Solution
- Structured JSON+MD+raw benchmark reports in .ai/reports/benchmarks/
- Strict requires_benchmark/adr/reference checks (blocking errors)
- _check_path_safe() with resolve() + is_relative_to()
- Stricter workflow safety: forbidden inputs, || true, if-no-files-found
