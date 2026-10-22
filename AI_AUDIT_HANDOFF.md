# AI audit handoff for DeepCode

- Generated: `2026-08-27T17:55:42.720537+00:00`
- Source results: `D:\ai-code-audit\results-full-14b-16k-2026-08-27`
- Module cards read: **120**
- Manifest status: `{'failed': 8, 'ok': 120}`
- Risks: **253**
- Proposed tests: **253**
- Backlog candidates: **256**

## Mandatory instructions for DeepCode

This is an LLM-generated preliminary audit, not verified truth.
Do not modify source code and do not create GitHub issues yet.
For every proposed issue, inspect the referenced local file and lines.
Reject or downgrade any claim that cannot be supported by the current code.
Merge duplicates across modules and existing GitHub issues.
Do not make legal conclusions from license-related findings; create only
human-verification tasks with concrete package/version/license evidence.

## Requested output

Create `deepcode_audit_triage.md` in the repository root with:
1. A deduplicated ranked backlog: P0, P1, P2, P3.
2. For each accepted item: proposed GitHub Issue title, problem, code evidence,
   user/scientific impact, verification plan, Definition of Done, labels.
3. A `Rejected or insufficient evidence` section explaining exclusions.
4. A `Potential duplicates` section, including links/numbers of existing issues if found.
5. A final section `Ready for manual GitHub issue creation` containing only
   issues that are specific, independently verifiable, and non-duplicated.

## Priority summary

- P0: 0 risk findings
- P1: 4 risk findings
- P2: 87 risk findings
- P3: 162 risk findings

## P0/P1 risk candidates

### R1. [P1] license: src/core/chemistry/__init__.py

**Finding:** No license information is provided in the source file. This could lead to unclear usage rights and potential legal issues.

**Purpose of module:** Package documentation

**Evidence:** Нет; требуется ручная проверка.

**How to verify:** Check for a LICENSE file in the repository or a license header in the source code.

### R2. [P1] license: src/core/domain/__init__.py

**Finding:** No license information is provided in the file. This could lead to unclear usage rights and potential legal issues.

**Purpose of module:** Package documentation

**Evidence:** Нет; требуется ручная проверка.

**How to verify:** Check the repository for a LICENSE file or other licensing information.

### R3. [P1] license: src/core/io/__init__.py

**Finding:** No license information is provided in the source file. This could lead to unclear usage rights and potential legal issues.

**Purpose of module:** Package documentation for src.core.io

**Evidence:** Нет; требуется ручная проверка.

**How to verify:** Check the repository's root for a LICENSE file.

### R4. [P1] license: src/sim/__init__.py

**Finding:** The file contains a license note, but it is unclear if it is compliant with the project's licensing requirements. Further human verification is needed.

**Purpose of module:** R&D utilities: test set generation, PubChem search, candidate processing.

**Evidence:** Нет; требуется ручная проверка.

**How to verify:** Review the project's licensing documentation and ensure the license note in the file aligns with the required license.

## All backlog candidates

### B1. [P1] Add LICENSE file to the repository

- File: `src/core/domain/__init__.py`
- Rationale: To clarify usage rights and avoid legal issues.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A LICENSE file is added to the repository root.
  - The LICENSE file contains appropriate licensing information.

### B2. [P1] Add a LICENSE file to the repository

- File: `src/core/chemistry/__init__.py`
- Rationale: To clarify usage rights and avoid legal issues.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - LICENSE file is added to the repository root.

### B3. [P1] Add license information to src/core/io/__init__.py

- File: `src/core/io/__init__.py`
- Rationale: To clarify usage rights and avoid legal issues.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A LICENSE file is added to the repository's root.
  - The LICENSE file is referenced in src/core/io/__init__.py.

### B4. [P2] Add a LICENSE file to the repository.

- File: `src/__init__.py`
- Rationale: To clarify usage rights and avoid legal issues.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A LICENSE file is added to the root of the repository.
  - The LICENSE file contains a recognized open-source license.

### B5. [P2] Add a test to verify that the `project_root` fixture returns the correct path even if the repository root changes during the session.

- File: `tests/conftest.py`
- Rationale: This will ensure that the fixture remains reliable even if the repository structure changes during the session.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A test is added to verify the behavior of the `project_root` fixture.
  - The test is included in the test suite and passes successfully.

### B6. [P2] Add assertions for 'n_cooh' column computation in 'test_basic_computation'

- File: `tests/unit/test_van_krevelen.py`
- Rationale: Ensures the correctness of the 'n_cooh' column values.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add assertions to verify 'n_cooh' values in 'test_basic_computation'.
  - Run tests and confirm that the new assertions pass.

### B7. [P2] Add assertions to check for specific content within the generated PDF.

- File: `tests/unit/test_report.py`
- Rationale: This will ensure that the PDF generation produces the expected content.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add assertions to verify specific content in the PDF.

### B8. [P2] Add assertions to check the validity of the generated formulas in `test_cached_generation_is_consistent`.

- File: `tests/unit/test_generate_cache.py`
- Rationale: Ensures the correctness of the generated formulas, not just consistency and cache behavior.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Added assertions to validate the generated formulas.
  - Updated test documentation.

### B9. [P2] Add compatibility option for `time.time()` in `StageTimer`.

- File: `src/core/timer.py`
- Rationale: Improves compatibility across different environments.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Option to switch timing methods is implemented.
  - Documentation is updated to reflect the new option.

### B10. [P2] Add documentation for all public functions.

- File: `src/core/chemistry/_functional.py`
- Rationale: Improves code readability and maintainability.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Each public function has a docstring describing its purpose, parameters, and return value.

### B11. [P2] Add documentation for complex molecule creation functions.

- File: `src/core/chemistry/_factories.py`
- Rationale: Improves maintainability and reproducibility.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Inline comments added to complex functions.
  - Separate documentation file created for molecule creation logic.

### B12. [P2] Add error handling and logging around the `build_database` call.

- File: `src/core/formula_db/__main__.py`
- Rationale: This will improve the robustness of the application by capturing and reporting any issues that occur during the database build process.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Error handling is added around the `build_database` call.
  - Appropriate logging is added to capture and report any issues.

### B13. [P2] Add error handling for non-integer and missing values in 'carboxyl_count' and 'hydroxyl_count'.

- File: `tests/unit/test_chemical_validity.py`
- Rationale: Improves test robustness and prevents unexpected errors during execution.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Update lines 34 and 40 to handle non-integer and missing values gracefully.

### B14. [P2] Add exception handling in the benchmark function.

- File: `src/core/benchmark_assign.py`
- Rationale: Improves robustness and reliability of the benchmarking process.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Exception handling added to lines 00055-00058.
  - Unit tests added to verify exception handling.

### B15. [P2] Add exception handling to the benchmark function.

- File: `src/core/benchmark.py`
- Rationale: To ensure robust benchmarking and prevent incomplete results.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Try-except blocks added around file operations and pipeline execution.
  - Unit tests added to verify exception handling.

### B16. [P2] Add input validation for `df_dmet` and `df_dacet`.

- File: `src/core/spectrum/_build.py`
- Rationale: Ensure that the function handles missing columns gracefully.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Function raises a descriptive error when required columns are missing.
  - Unit tests cover scenarios with missing columns.

### B17. [P2] Add input validation for subprocess calls

- File: `tools/build_exe.py`
- Rationale: Prevent command injection vulnerabilities.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Input validation is added to `run` and `smoke_test_exe` functions.
  - Unit tests are written to verify the validation logic.

### B18. [P2] Add input validation to prevent directory traversal attacks.

- File: `src/cli.py`
- Rationale: Improves security by ensuring that input file paths are safe.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Input file paths are validated to prevent directory traversal attacks.
  - Unit tests are added to verify the validation.

### B19. [P2] Add integrity checks for DLLs

- File: `src/core/io/raw_thermo_adapter.py`
- Rationale: To prevent security vulnerabilities from malicious DLLs.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The `_check_dlls` function includes checks for DLL integrity and origin.
  - A test case is added to verify the integrity checks.

### B20. [P2] Add more test cases for the `_nom_distance` function.

- File: `tests/unit/test_nom_prioritize.py`
- Rationale: Ensure the NOM distance function is robust against various inputs.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - New test cases added to cover different H/C and O/C ratios.

### B21. [P2] Add performance benchmarks for the denoise function.

- File: `tests/unit/test_denoise.py`
- Rationale: To ensure the denoising process is efficient for large datasets.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Performance benchmarks are implemented and integrated into the test suite.
  - Benchmarks are run regularly to monitor performance.

### B22. [P2] Add schema validation for mzML files.

- File: `src/core/io/mzml_bridge.py`
- Rationale: Ensure compliance with mzML standards to prevent unexpected behavior.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Schema validation implemented.
  - Unit tests added for schema validation.

### B23. [P2] Add test for CSV export with default separator.

- File: `tests/unit/test_export.py`
- Rationale: Ensure the CSV export uses the correct default separator.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A new test case is added to verify the default separator.
  - The test case passes successfully.

### B24. [P2] Add tests for edge cases in Atom creation.

- File: `tests/unit/test_atoms.py`
- Rationale: Ensure robustness against unexpected inputs.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Tests for various formal charges and hybridizations added.
  - All tests pass.

### B25. [P2] Add tests for edge cases in fragment combination assembly.

- File: `tests/unit/test_fragment_combinations.py`
- Rationale: Ensure robustness against unexpected inputs.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - New test cases added for edge scenarios.
  - All new tests pass successfully.

### B26. [P2] Add tooltips to buttons for better user guidance.

- File: `src/ui/_tabs.py`
- Rationale: Improving user experience by providing tooltips for each button action.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Tooltips are added to all buttons in the TabsMixin class.
  - Tooltips are tested to ensure they display the correct information.

### B27. [P2] Add validation for `Path` fields to ensure they are valid file paths.

- File: `src/testing/report_models.py`
- Rationale: This will prevent errors related to invalid file paths.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Validation logic is implemented.
  - Unit tests are added to cover the validation logic.

### B28. [P2] Add version constraints to dependencies.

- File: `src/ui/_results.py`
- Rationale: Ensure compatibility and reproducibility of the application.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Version constraints added to the requirements file.
  - Dependencies updated to the specified versions.

### B29. [P2] Consolidate redundant test functions

- File: `tests/unit/test_pipeline.py`
- Rationale: Reduce redundancy and improve maintainability by consolidating similar test functions.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Identify and consolidate redundant test functions.
  - Update test documentation if necessary.

### B30. [P2] Develop initial functionality for src/core/io

- File: `src/core/io/__init__.py`
- Rationale: To provide a meaningful package with actual code.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - At least one function or class is added to src/core/io/__init__.py.
  - The functionality is documented and tested.

### B31. [P2] Document the license requirements for the project

- File: `src/sim/__init__.py`
- Rationale: To ensure all files, including this one, comply with the correct licensing, a clear document outlining the project's licensing requirements is needed.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A document detailing the project's licensing requirements is created and shared with the team.
  - All files in the project are reviewed and updated to comply with the documented licensing requirements.

### B32. [P2] Document the purpose and usage of `CONFIG_DIR`.

- File: `src/configs/__init__.py`
- Rationale: Clarify the intended use of `CONFIG_DIR` to prevent misuse.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add a docstring to `CONFIG_DIR` explaining its purpose and usage.

### B33. [P2] Document the purpose of the empty module

- File: `src/testing/__init__.py`
- Rationale: An empty module should have a clear purpose documented to avoid confusion for future developers.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A docstring is added to the module explaining its intended use or purpose.

### B34. [P2] Enhance error handling testing in `test_cli_missing_file_exit_1`

- File: `tests/unit/test_cli.py`
- Rationale: Ensure the test verifies both the exit code and the error message for missing files.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add assertions to check the error message and exit code.

### B35. [P2] Enhance logging and error messages

- File: `src/core/io/raw_thermo_adapter.py`
- Rationale: To improve debugging and troubleshooting.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The `_log` function provides detailed error messages and logs.
  - A test case is added to verify the enhanced logging.

### B36. [P2] Expand test cases for `detect_sample_triples`

- File: `tests/unit/test_batch.py`
- Rationale: Ensure robustness against various file naming patterns and edge cases.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add tests for files with missing components.
  - Add tests for files with incorrect naming conventions.

### B37. [P2] Implement CLI command for building the database.

- File: `src/core/formula_db/__init__.py`
- Rationale: The CLI command `python -m src.core.formula_db build` is mentioned but not implemented. Implementing this command will provide a convenient way to build the database.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - CLI command implemented and tested.
  - Documentation updated to include the new command.

### B38. [P2] Implement JSON schema validation for configuration files.

- File: `src/configs/loader.py`
- Rationale: Ensure that configuration files adhere to a predefined schema, reducing the risk of unexpected behavior due to malformed JSON structures.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A JSON schema is defined for each configuration file.
  - The `load_config` function validates the JSON data against the schema.
  - Unit tests are added to verify schema validation.

### B39. [P2] Implement a more sophisticated balancing algorithm for `split_into_sets`.

- File: `src/sim/process_pubchem_candidates.py`
- Rationale: The current round-robin approach may not ensure perfect balance in terms of the total mass or other critical properties across subsets.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A new balancing algorithm is implemented.
  - The new algorithm is tested with a large dataset.
  - The new algorithm is integrated into the module.

### B40. [P2] Implement core functionality in the chemistry package

- File: `src/core/chemistry/__init__.py`
- Rationale: To make the package useful and maintainable.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Functions or classes are added to the package.

### B41. [P2] Implement core functionality in the package

- File: `src/core/domain/__init__.py`
- Rationale: To move the package from an early development stage to a functional state.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Core classes and functions are implemented.
  - Unit tests are written for the implemented functionality.
  - Documentation for the implemented functionality is provided.

### B42. [P2] Implement dynamic cache size adjustment in LRUBlockCache.

- File: `src/core/formula_db/_reader.py`
- Rationale: Improves cache management and flexibility.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add a method to adjust the cache size.
  - Ensure the cache size does not exceed the new limit.

### B43. [P2] Implement error handling for binary decoding.

- File: `src/core/io/mzml_bridge.py`
- Rationale: Gracefully handle malformed binary data to improve robustness.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Error handling added for binary decoding.
  - Unit tests added for error handling scenarios.

### B44. [P2] Implement proper synchronization for threading and queue usage.

- File: `src/ui/_build.py`
- Rationale: To prevent race conditions and ensure thread safety.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add synchronization mechanisms where necessary.
  - Write unit tests to verify thread safety.

### B45. [P2] Implement rate limiting for log message processing in `_poll_log_queue`.

- File: `src/ui/_log.py`
- Rationale: Reduce CPU usage during high log activity.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Rate limiting is implemented and tested.
  - CPU usage is monitored and verified to be within acceptable limits.

### B46. [P2] Implement retry logic for network operations in the download method.

- File: `src/core/formula_db/_manager.py`
- Rationale: This will improve the robustness of the download process against transient network issues.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Error handling is added to the `download` method.
  - Retry logic is implemented with a configurable number of retries and backoff strategy.

### B47. [P2] Implement test_average_raw_to_df_delegates with actual test logic.

- File: `tests/integration/test_raw_integration.py`
- Rationale: Ensure the test verifies that average_raw_to_df delegates to average_raw_to_json.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add assertions to test_average_raw_to_df_delegates.
  - Run the test and confirm it passes.

### B48. [P2] Implement test_average_raw_to_json_smoke with actual test logic.

- File: `tests/integration/test_raw_integration.py`
- Rationale: Ensure the test verifies the correct behavior of average_raw_to_json.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add assertions to test_average_raw_to_json_smoke.
  - Run the test with a valid .raw file and confirm it passes.

### B49. [P2] Improve error handling in import blocks

- File: `src/ui/_deps.py`
- Rationale: Generic exception handling can obscure specific issues.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Specific error messages are logged.
  - Error handling is documented.

### B50. [P2] Increase `lru_cache` maxsize for `_generate_cached`

- File: `src/core/spectrum/_generate.py`
- Rationale: To improve memoization effectiveness and performance.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Increase `maxsize` to a value that covers the expected range of function calls.
  - Verify that cache hit rates improve with the new `maxsize`.

### B51. [P2] Make the test flexible to changes in the number of test sets.

- File: `tests/integration/test_app_smoke.py`
- Rationale: The test should not break if the number of test sets changes.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Update the test to assert the correct number of test sets based on the source data.
  - Add a comment explaining the reasoning behind the assertion.

### B52. [P2] Optimize RDKit imports in test_rdkit_bridge.py

- File: `tests/unit/test_rdkit_bridge.py`
- Rationale: Reduce redundant imports to improve test execution speed.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - RDKit modules are imported once at the top of the file.
  - Test execution time is measured and compared to the previous version.

### B53. [P2] Optimize UI construction in StructureDialog and StructureCard

- File: `src/structures/widgets.py`
- Rationale: Sequential UI construction can be slow with many structures. Consider using a more efficient method.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Profile the application with a large dataset to measure performance improvements.
  - Implement a more efficient UI construction method.

### B54. [P2] Optimize _compute_penalty for large datasets

- File: `tests/unit/test_isotope_filter.py`
- Rationale: Performance improvement for handling large input sizes.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Benchmarking with large input sizes shows improved performance.
  - Optimized code is reviewed and merged.

### B55. [P2] Optimize `_autofit_columns` for large DataFrames

- File: `src/core/pipeline/_export.py`
- Rationale: Improve performance by calculating column widths based on more rows or using a different method.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Performance tests show improved results for large DataFrames.
  - Documentation updated with new method.

### B56. [P2] Optimize `_enum_valid_cnosp` for large inputs

- File: `src/core/formula_db/_builder.py`
- Rationale: The function's nested loop structure could lead to performance issues with large `max_mass_u`. Investigate and implement optimizations to improve execution time.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Identify bottlenecks in the function.
  - Implement and test optimizations.
  - Verify improved performance with benchmarks.

### B57. [P2] Optimize `_measure_m1_ratio` for performance

- File: `src/core/spectrum/_chem.py`
- Rationale: Improve efficiency by reducing data passes and using more efficient algorithms.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Execution time is reduced by at least 50% on large datasets.
  - Code is refactored for better readability and maintainability.

### B58. [P2] Optimize `_safe_df` for frequent None inputs.

- File: `src/core/_safety.py`
- Rationale: Reduce performance overhead by reusing a single empty DataFrame instance.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Implement a singleton pattern for the empty DataFrame.
  - Update tests to verify the new behavior.

### B59. [P2] Optimize `compute_distribution_metrics` for large DataFrames

- File: `src/core/statistics.py`
- Rationale: Replace `iterrows()` with vectorized operations to improve performance.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Implement vectorized operations.
  - Measure and document the performance improvement.

### B60. [P2] Optimize `fragment_to_rdkit` for large molecules.

- File: `src/structures/rdkit_utils.py`
- Rationale: Improve performance by exploring more efficient conversion methods.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Benchmarking results show improved performance.
  - Optimized code is merged and reviewed.

### B61. [P2] Optimize adjacency list construction.

- File: `src/core/chemistry/_fragment.py`
- Rationale: The current implementation of `_build_adjacency` could be optimized for performance.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Benchmark the current implementation.
  - Implement an optimized version.
  - Compare performance and verify correctness.

### B62. [P2] Optimize combination generation and assembly for large molecules.

- File: `src/core/chemistry/_visualize.py`
- Rationale: Improves performance for complex molecules.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Execution time for large input molecules is reduced by at least 50%.

### B63. [P2] Optimize data conversion process in `average_raw_to_df`

- File: `src/core/io/raw_bridge.py`
- Rationale: Reduce unnecessary I/O operations to improve performance.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Direct conversion from raw data to DataFrame without intermediate JSON file.
  - Performance benchmarks showing improvement.

### B64. [P2] Optimize figure closing in `clear_canvas`

- File: `src/ui/plots.py`
- Rationale: Closing all figures with `plt.close('all')` may lead to performance issues. Implement a more targeted approach to closing figures.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Identify and close only relevant figures instead of all figures.
  - Measure and document the performance improvement.

### B65. [P2] Optimize file listing in `_list_files`.

- File: `src/core/batch.py`
- Rationale: Using `os.walk` or `pathlib` can improve performance for large directories.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Refactor `_list_files` to use `os.walk` or `pathlib`.
  - Add performance benchmarks to verify improvements.

### B66. [P2] Optimize formula assignment and validation logic.

- File: `tests/unit/test_assign_formulas.py`
- Rationale: The current implementation of formula assignment and validation could be optimized to improve performance and reduce the number of iterations and lookups.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Optimized comparison logic to reduce the number of iterations and lookups.
  - Added performance benchmarks to measure the impact of the optimization.

### B67. [P2] Optimize formula generation and processing for large datasets.

- File: `src/core/spectrum/_assign.py`
- Rationale: Improving performance will enhance the usability of the function for large-scale applications.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Execution time is reduced by at least 50% for large input datasets.
  - Optimized code is reviewed and merged into the main branch.

### B68. [P2] Optimize regex parsing in _normalize_brutto

- File: `src/core/pipeline/_helpers.py`
- Rationale: Improve performance for large datasets.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Replace regex with a more efficient parsing method.
  - Add performance benchmarks before and after optimization.

### B69. [P2] Optimize series verification for large datasets.

- File: `src/core/pipeline/_test_verify.py`
- Rationale: The current implementation may not scale well with large input sizes.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Profile the function with large datasets.
  - Implement optimizations to reduce time complexity.
  - Verify that the optimized function performs as expected.

### B70. [P2] Parallelize test set processing in _run_test_mode

- File: `src/core/pipeline/_test.py`
- Rationale: To improve performance for a large number of test sets.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Measure the execution time for a large number of test sets before and after the change.
  - Ensure the results are consistent with the sequential processing.

### B71. [P2] Refactor FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS to use a more maintainable format.

- File: `src/core/chemistry/_fragment_data.py`
- Rationale: The current format of FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS is difficult to maintain and update. Refactoring to a more maintainable format will reduce the risk of errors and improve the maintainability of the code.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS are refactored to a more maintainable format.
  - All fragments and functional groups are correctly defined in the new format.
  - The new format is documented and easy to understand.

### B72. [P2] Refactor `ALL_FRAGMENTS` dictionary to remove commented-out entries.

- File: `src/core/chemistry/fragments.py`
- Rationale: This will improve maintainability and reduce the risk of bugs from uncommented entries.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - All commented-out entries are removed from the `ALL_FRAGMENTS` dictionary.
  - Documentation is updated to reflect any changes.

### B73. [P2] Refactor `PipelineStats` class to improve maintainability.

- File: `src/core/pipeline/_stats.py`
- Rationale: The `PipelineStats` class has a large number of attributes, which could make it difficult to maintain and understand. Consider breaking it down into smaller, more focused classes if possible.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Refactor the `PipelineStats` class into smaller, more focused classes.
  - Update all references to the `PipelineStats` class in the codebase.
  - Ensure that the refactored classes maintain the same functionality as the original class.

### B74. [P2] Refactor `_make_df` to generate data dynamically based on test parameters.

- File: `tests/unit/test_statistics.py`
- Rationale: This will make the tests more flexible and easier to maintain.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The `_make_df` function generates data dynamically.
  - All tests that use `_make_df` are updated to use the new function.

### B75. [P2] Refactor `_style` function for better maintainability

- File: `src/ui/theme.py`
- Rationale: The `_style` function configures a large number of ttk widgets, which could make the code difficult to maintain and update. Consider refactoring to use a more modular approach.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The `_style` function is refactored into smaller, more manageable functions.
  - All ttk widgets are still correctly configured with the expected styles.

### B76. [P2] Refactor availability checks to ensure reliability.

- File: `tests/unit/test_raw_bridge.py`
- Rationale: The availability checks in `is_available` might be incorrect or unreliable, leading to skipped tests.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Implement a more robust availability check.
  - Update tests to ensure they are not skipped unnecessarily.

### B77. [P2] Refactor private symbols to internal modules

- File: `src/core/pipeline/__init__.py`
- Rationale: Restricting access to private symbols can improve the maintainability and security of the codebase.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Private symbols are moved to internal modules.
  - Public API remains unchanged.

### B78. [P2] Resolve naming conflict between `StructureCard` classes.

- File: `src/structures/__init__.py`
- Rationale: Avoid confusion and potential bugs due to naming conflicts.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Rename one of the `StructureCard` classes to avoid conflict.
  - Update all references to the renamed class in the codebase.

### B79. [P2] Validate benchmark command before execution.

- File: `tools/run_benchmark.py`
- Rationale: To prevent execution of malicious commands if the script is extended in the future.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add validation logic for benchmark commands.
  - Update tests to cover validation scenarios.

### B80. [P2] Добавить валидацию параметров в функции `_apply_preset`.

- File: `src/ui/_presets.py`
- Rationale: Предотвращение некорректной работы приложения из-за некорректных параметров.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавление проверок значений параметров.
  - Обновление тестов для проверки валидации.

### B81. [P2] Добавить интеграционные тесты для функции embed_figure.

- File: `tests/unit/test_app_fallback.py`
- Rationale: Текущие тесты проверяют только сигнатуры, что не гарантирует корректное поведение функции.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Создать тесты, проверяющие поведение функции в различных сценариях.
  - Убедиться, что тесты покрывают все возможные исключения и ошибки.

### B82. [P2] Добавить лицензионные заметки в файл.

- File: `tests/unit/test_annotations_consistency.py`
- Rationale: Улучшение читаемости и поддержки кода.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавлены лицензионные заметки в начало файла.

### B83. [P2] Добавить поддержку дополнительных форматов файлов при импорте.

- File: `src/ui/_presets.py`
- Rationale: Увеличение гибкости приложения для работы с разными типами данных.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Поддержка форматов .txt и .dat.
  - Обновление документации.

### B84. [P2] Добавить проверку безопасности при чтении файлов в функции _read_table.

- File: `src/core/spectrum/_load.py`
- Rationale: Улучшение безопасности приложения от выполнения нежелательного кода из файлов.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавлена проверка целостности файла перед чтением.
  - Обновлены тесты для проверки безопасности.

### B85. [P2] Добавить проверку безопасности содержимого файла в функцию `load_preset`.

- File: `src/configs/presets_loader.py`
- Rationale: Уменьшить риск выполнения произвольного кода из вредоносных файлов.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавлены проверки безопасности содержимого файла.
  - Обновлены тесты для проверки безопасности.

### B86. [P2] Добавить тесты для других наборов данных

- File: `tests/unit/test_structural_validity.py`
- Rationale: Убедиться в корректности структуры файлов для всех наборов данных.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Тесты добавлены для всех наборов данных.
  - Тесты проходят успешно.

### B87. [P2] Оптимизация метода `add_bond` для повышения производительности при добавлении большого количества связей.

- File: `src/core/domain/atoms.py`
- Rationale: Уменьшение времени выполнения метода `add_bond` может повысить общую производительность приложения при работе с большими молекулярными графами.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавлен оптимизированный алгоритм для обновления списка двойных и тройных связей.
  - Добавлены тесты для проверки корректности работы нового алгоритма.

### B88. [P2] Оптимизация поиска пиков для улучшения производительности.

- File: `src/core/spectrum/_visualize.py`
- Rationale: Уменьшение времени выполнения при обработке больших данных.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Измерение времени выполнения до и после оптимизации.
  - Улучшение производительности на 20%.

### B89. [P2] Оптимизация предзагрузки структур

- File: `src/ui/_structures.py`
- Rationale: Улучшить производительность метода _preload_structures_worker, возможно, путем использования более эффективных алгоритмов или параллельной обработки.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Измерение времени выполнения метода уменьшено на 20%.
  - Использование CPU при предзагрузке уменьшено на 10%.

### B90. [P2] Оптимизация функции `plot_series_grid` для больших данных

- File: `src/testing/artifact_export.py`
- Rationale: Улучшение производительности при обработке больших наборов данных.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Измерить и улучшить время выполнения функции.
  - Добавить тесты с различными размерами входных данных.

### B91. [P2] Реализовать механизм очистки кэша по времени или размеру.

- File: `src/core/pipeline/_cache.py`
- Rationale: Предотвратить неограниченное увеличение потребления памяти.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавить параметры конфигурации для очистки кэша.
  - Реализовать периодическую очистку кэша.

### B92. [P2] Увеличить количество рабочих потоков в ThreadPoolExecutor.

- File: `src/testing/structure_export.py`
- Rationale: Улучшить производительность при обработке множества соединений одновременно.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Измерить время выполнения при обработке нескольких соединений одновременно и сравнить с использованием большего числа рабочих потоков.

### B93. [P3] Add a placeholder comment if the module is intended to be expanded

- File: `src/testing/__init__.py`
- Rationale: If the module is planned to be expanded in the future, a placeholder comment can help indicate this intention.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A comment is added to the module indicating that it is a placeholder for future development.

### B94. [P3] Add a test case to verify the correctness of the calculation 'hydroxyl_count = hydroxyl_count - carboxyl_count'.

- File: `tests/unit/test_chemical_validity.py`
- Rationale: Ensures the calculation is implemented correctly and tested.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Create a new test function to check the calculation.

### B95. [P3] Add comprehensive input validation for _beynon_m1_ratio

- File: `tests/unit/test_isotope_filter.py`
- Rationale: Ensure robustness against invalid input.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Test cases cover negative and non-integer element counts.
  - Code changes are reviewed and merged.

### B96. [P3] Add comprehensive logging for series verification.

- File: `src/core/pipeline/_test_verify.py`
- Rationale: Improved logging will aid in debugging and monitoring the verification process.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add detailed logging for each step in the verification process.
  - Ensure logs are clear and informative.
  - Verify that logs capture all relevant information for debugging.

### B97. [P3] Add documentation for public symbols in `structures/__init__.py`.

- File: `src/structures/__init__.py`
- Rationale: Improve maintainability and developer understanding.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add docstrings for each public symbol.
  - Update README or other documentation to reflect the new symbols.

### B98. [P3] Add documentation for the `main` function and its arguments.

- File: `src/core/formula_db/__main__.py`
- Rationale: This will improve the usability of the application by providing clear instructions on how to use the CLI.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Documentation is added to the `main` function and its arguments.
  - The documentation is clear and concise.

### B99. [P3] Add error handling to `average_raw_to_json`

- File: `src/core/io/raw_bridge.py`
- Rationale: Improve robustness by handling potential errors during conversion.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Error handling implemented in `average_raw_to_json`.
  - Unit tests covering various error scenarios.

### B100. [P3] Add exception handling in `StageTimer` methods.

- File: `src/core/timer.py`
- Rationale: Improves robustness against unexpected errors.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Exception handling is added in `__enter__` and `__exit__` methods.
  - Tests are updated to verify exception handling.
  - Documentation is updated to reflect the new behavior.

### B101. [P3] Add exception handling in `embed_figure`

- File: `src/ui/plots.py`
- Rationale: Lack of exception handling could lead to unhandled exceptions and application crashes. Implement robust error handling.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add try-except blocks around `FigureCanvasTkAgg` and `NavigationToolbar2Tk` initialization.
  - Update function documentation to reflect the added error handling.

### B102. [P3] Add input validation for molecule formulas.

- File: `src/core/chemistry/_visualize.py`
- Rationale: Ensures function handles invalid input gracefully.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Function raises exceptions for invalid molecule formulas.

### B103. [P3] Add logging to _run_test_mode for better traceability

- File: `src/core/pipeline/_test.py`
- Rationale: To improve debugging and monitoring.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add logging statements at key points in the function.
  - Verify that the logs provide useful information for debugging.

### B104. [P3] Add logging to `_make_df` to track data generation.

- File: `tests/unit/test_statistics.py`
- Rationale: This will help in debugging and understanding the data generation process.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Logging is added to `_make_df`.
  - Logs are verified to be informative and useful.

### B105. [P3] Add logging to the module for better traceability.

- File: `src/sim/process_pubchem_candidates.py`
- Rationale: Adding logging will help in debugging and understanding the flow of the module.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Logging is added to key functions.
  - Log messages are tested and verified.
  - Logging configuration is documented.

### B106. [P3] Add mock implementations for RawFileReader in tests.

- File: `tests/integration/test_raw_integration.py`
- Rationale: Ensure tests run in environments where RawFileReader is not available.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Implement mock RawFileReader in tests.
  - Run tests in environments without RawFileReader and confirm they pass.

### B107. [P3] Add more detailed logging and diagnostics to the test function.

- File: `tests/unit/test_assign_formulas.py`
- Rationale: The current implementation of the test function does not provide enough information about the test results and the reasons for failures. Adding more detailed logging and diagnostics will help to identify and fix issues more easily.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Added more detailed logging and diagnostics to the test function.
  - Updated the test function documentation to reflect the new logging and diagnostics.

### B108. [P3] Add more test cases for edge cases and invalid inputs.

- File: `tests/unit/test_assign_formulas.py`
- Rationale: The current implementation of the test function does not cover all edge cases and invalid inputs. Adding more test cases will help to ensure that the code is robust and handles all possible inputs correctly.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Added test cases for edge cases and invalid inputs.
  - Updated the test function documentation to reflect the new test cases.

### B109. [P3] Add progress feedback during pipeline execution.

- File: `src/cli.py`
- Rationale: Improves user experience by providing feedback on the execution progress.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Progress feedback is added during pipeline execution.
  - Unit tests are added to verify the feedback.

### B110. [P3] Add support for localization in the _report method.

- File: `src/core/formula_db/_manager.py`
- Rationale: This will enhance the user experience by providing progress reports in the user's preferred language.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The `_report` method is updated to support localization.
  - Progress messages are translated into at least one additional language.

### B111. [P3] Add support for non-English characters in step titles

- File: `tools/build_exe.py`
- Rationale: Ensure compatibility with internationalization.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Step titles are encoded in UTF-8.
  - Unit tests are written to verify the encoding behavior.

### B112. [P3] Add tests for invalid input parameters and large datasets.

- File: `tests/unit/test_report.py`
- Rationale: This will ensure that all code paths are tested.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add tests for invalid input parameters and large datasets.

### B113. [P3] Add validation for `total_signals` in `TestSetResult` class.

- File: `src/core/pipeline/_stats.py`
- Rationale: The `assign_recall` and `denoise_recall` properties in `TestSetResult` class may raise a ZeroDivisionError if `total_signals` is zero. This could happen if no ground-truth signals are present in the test set.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add validation for `total_signals` in the `assign_recall` and `denoise_recall` properties.
  - Update tests to cover the scenario where `total_signals` is zero.
  - Ensure that the properties return 0.0 without raising an error when `total_signals` is zero.

### B114. [P3] Add validation for molecular fragment creation.

- File: `src/core/chemistry/_functional.py`
- Rationale: Ensures the correctness of molecular fragment creation.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Validation checks for the number of atoms, bonds, and attachment points.

### B115. [P3] Add validation for the `ion_mode` parameter.

- File: `src/core/spectrum/_assign.py`
- Rationale: Ensuring the `ion_mode` parameter is valid will prevent incorrect mass shifts and formula assignments.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Validation logic is implemented and tested.
  - Documentation is updated to reflect the new validation requirements.

### B116. [P3] Analyze and mitigate performance impact of fallback imports

- File: `src/ui/_deps.py`
- Rationale: Performance overhead may affect application responsiveness.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Performance impact is measured and documented.
  - Optimization strategies are implemented if necessary.

### B117. [P3] Automate the discovery and update of the `_CONFIG_FILES` dictionary.

- File: `src/configs/loader.py`
- Rationale: Reduce the risk of manual errors by automatically maintaining the `_CONFIG_FILES` dictionary.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A script is written to scan the configuration directory and update the `_CONFIG_FILES` dictionary.
  - The script is integrated into the build process to ensure it runs before the application starts.
  - Documentation is updated to include instructions for using the script.

### B118. [P3] Cache Matplotlib style configuration

- File: `src/ui/theme.py`
- Rationale: The `_mpl_style` function updates multiple Matplotlib parameters, which could impact performance if called frequently. Consider caching the style configuration to avoid redundant updates.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A caching mechanism is implemented for the Matplotlib style configuration.
  - The `_mpl_style` function is updated to use the caching mechanism.
  - Performance tests are conducted to verify that the caching mechanism improves performance.

### B119. [P3] Capture environment variables and system state before running benchmarks.

- File: `tools/run_benchmark.py`
- Rationale: To ensure reproducibility of benchmark results.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Log environment variables and system state.
  - Update JSON and Markdown reports to include this information.
  - Update tests to verify the inclusion of environment data.

### B120. [P3] Clarify and handle ambiguous filename patterns in `_classify`.

- File: `src/core/batch.py`
- Rationale: Current implementation may lead to unexpected results if multiple patterns match a filename.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Define a clear strategy for resolving ambiguous filename patterns.
  - Update `_classify` to handle ambiguities according to the defined strategy.
  - Add tests to cover ambiguous pattern scenarios.

### B121. [P3] Clarify default behavior of `toolbar` parameter in `embed_figure`

- File: `src/ui/plots.py`
- Rationale: The default value of `toolbar` could lead to confusion. Improve parameter clarity and documentation.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Update function documentation to clearly explain the default behavior of the `toolbar` parameter.
  - Consider adding a more explicit parameter if necessary.

### B122. [P3] Complete `__repr__` method to include all attributes.

- File: `src/core/chemistry/_fragment.py`
- Rationale: Ensure that the `__repr__` method includes all attributes for better debugging.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Update the `__repr__` method to include all attributes.
  - Verify that the method returns a complete representation of the object.
  - Update tests to cover the new `__repr__` implementation.

### B123. [P3] Conduct a security audit of imported modules.

- File: `src/core/chemistry/fragments.py`
- Rationale: This will ensure the security of the module and its dependencies.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A security audit is conducted of all imported modules.
  - Any vulnerabilities are addressed and the module is updated accordingly.

### B124. [P3] Consider removing the empty module if not needed

- File: `src/testing/__init__.py`
- Rationale: An empty module that serves no purpose can be confusing and should be removed if it is not required.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The module is removed if it is not used or its purpose is clarified and documented.

### B125. [P3] Document RDKit usage and licensing in the project

- File: `tests/unit/test_rdkit_bridge.py`
- Rationale: Ensure compliance with RDKit's licensing requirements.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A LICENSE file is updated to include RDKit's licensing information.
  - A README section is added to explain RDKit's usage and licensing.

### B126. [P3] Document `_safe_df` function.

- File: `src/core/_safety.py`
- Rationale: Improve maintainability by providing clear usage instructions.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add a docstring to `_safe_df` explaining its purpose and usage.
  - Update README or relevant documentation to include `_safe_df`.

### B127. [P3] Document input requirements for `build_result_table`.

- File: `src/core/spectrum/_build.py`
- Rationale: Ensure that users understand the expected input format.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Function documentation includes a clear description of required columns.
  - Example usage is provided in the documentation.

### B128. [P3] Document public API

- File: `src/core/pipeline/__init__.py`
- Rationale: Clear documentation of the public API can improve the usability and maintainability of the module.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Public symbols are documented with clear descriptions and usage examples.
  - Documentation is reviewed and approved by stakeholders.

### B129. [P3] Document the UI component creation and layout in the module.

- File: `src/ui/_build.py`
- Rationale: To improve code readability and maintainability.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add comments or docstrings explaining the purpose and layout of each UI component.
  - Update the README or a dedicated documentation file.

### B130. [P3] Document the assumptions about the file location and add a test to verify that the constants are calculated correctly.

- File: `tests/conftest.py`
- Rationale: This will improve maintainability and ensure that the constants remain valid if the file location changes.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The assumptions about the file location are documented.
  - A test is added to verify that the constants are calculated correctly.
  - The test is included in the test suite and passes successfully.

### B131. [P3] Document the behavior of `aromaticity_index` for non-positive denominators

- File: `src/core/statistics.py`
- Rationale: Ensure that the function's behavior is clear and documented.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Update the function's docstring.
  - Review the logic and confirm the behavior.

### B132. [P3] Document the benchmark function and its usage.

- File: `src/core/benchmark.py`
- Rationale: To improve developer understanding and ease of use.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Detailed docstring added to the `benchmark` function.
  - Usage examples added to the module's docstring.

### B133. [P3] Document the default values for boolean fields in `SetSmokeResult` and `SmokeSuiteResult`.

- File: `src/testing/report_models.py`
- Rationale: This will improve the clarity of the codebase.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Documentation is updated.
  - Code review is completed.

### B134. [P3] Document the expected behavior of _run_test_mode when test_sets_root is None

- File: `src/core/pipeline/_test.py`
- Rationale: To improve reproducibility and user understanding.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add a section to the function's docstring explaining the behavior.
  - Verify that the behavior matches the documentation.

### B135. [P3] Enhance `compute_sample_summary` to handle more edge cases

- File: `tests/unit/test_batch.py`
- Rationale: Improve the function's resilience to unexpected input data.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Handle cases with missing columns.
  - Handle cases with non-numeric data in numeric columns.

### B136. [P3] Enhance error handling in `create_histograms_plot`

- File: `src/core/statistics.py`
- Rationale: Provide a more informative error message or handle empty DataFrames gracefully.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Update the error handling logic.
  - Test with empty DataFrames and verify the improved behavior.

### B137. [P3] Enhance error handling in `mol_to_pil`.

- File: `src/structures/rdkit_utils.py`
- Rationale: Ensure that rendering errors are logged and reported.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Logging or exception handling is added.
  - Test cases cover error scenarios.

### B138. [P3] Enhance file path validation in `_save_log` to prevent directory traversal attacks.

- File: `src/ui/_log.py`
- Rationale: Ensure secure file saving operations.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - File path validation logic is updated.
  - Security testing is performed to verify prevention of directory traversal attacks.

### B139. [P3] Enhance logging assertions in print_molecule_info tests

- File: `tests/unit/test_rdkit_bridge.py`
- Rationale: Ensure more comprehensive testing of molecule properties through logging.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Additional assertions are added to verify specific molecule properties in `test_smoke` and `test_no_index`.
  - Tests are re-run to confirm that the new assertions pass.

### B140. [P3] Enhance manifest validation in FormulaDatabaseReader.

- File: `src/core/formula_db/_reader.py`
- Rationale: Prevents issues due to tampered manifests.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add checks to ensure all expected blocks are present in the manifest.
  - Raise appropriate errors for missing or altered blocks.

### B141. [P3] Enhance security checks in the _download_file method.

- File: `src/core/formula_db/_manager.py`
- Rationale: This will protect against malicious content or redirects during file downloads.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Security checks are added to the `_download_file` method.
  - The method verifies the integrity and safety of the downloaded content.

### B142. [P3] Enhance the test to capture and assert specific error messages.

- File: `tests/integration/test_app_smoke.py`
- Rationale: Specific error messages can aid in debugging and improve the test's robustness.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Modify the test to capture specific error messages or detailed error information.
  - Add assertions to check for these specific error messages or detailed error information.
  - Add a comment explaining the purpose of the new assertions.

### B143. [P3] Enhance type checking and error handling in `compute_sample_summary`.

- File: `src/core/batch.py`
- Rationale: Current implementation assumes `table` is a `pandas.DataFrame` or `None`, which may lead to errors if assumptions are violated.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add type checking for the `table` parameter.
  - Implement robust error handling for unsupported types.
  - Update documentation to reflect the expected types for `table`.

### B144. [P3] Ensure comprehensive test coverage for `average_raw_to_json`.

- File: `tests/unit/test_raw_bridge.py`
- Rationale: The test `test_raises_runtime_error_when_unavailable` might skip the test if `RawFileReader` is available, leading to incomplete test coverage.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Implement additional tests to cover all possible error paths in `average_raw_to_json`.
  - Ensure that the tests are not skipped unnecessarily.

### B145. [P3] Ensure temporary files are deleted after each test.

- File: `tests/unit/test_report.py`
- Rationale: This will prevent a buildup of temporary files in the CI/CD environment.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Implement cleanup of temporary files after each test.

### B146. [P3] Expand documentation for the src/__init__.py module.

- File: `src/__init__.py`
- Rationale: To improve maintainability and understanding for other developers.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A README.md file is added to the src directory.
  - The README.md file includes a detailed description of the module's functionality.
  - The README.md file lists all public symbols and their purposes.

### B147. [P3] Expand output validation in `test_cli_stdout`

- File: `tests/unit/test_cli.py`
- Rationale: Capture and validate the full output to ensure complete testing.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Modify the test to capture and validate the full output.

### B148. [P3] Expand test cases to cover different noise and signal scenarios.

- File: `tests/unit/test_denoise.py`
- Rationale: To ensure comprehensive testing of the denoising function.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - New test cases are implemented for various noise and signal scenarios.
  - Test cases are validated and integrated into the test suite.

### B149. [P3] Handle None `default` in `safe` function.

- File: `src/core/_safety.py`
- Rationale: Ensure consistent behavior when `default` is also None.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Modify the `safe` function to handle None `default`.
  - Update documentation to reflect the new behavior.
  - Add tests to cover the new scenario.

### B150. [P3] Handle `src.__version__` import failure gracefully

- File: `src/core/pipeline/_export.py`
- Rationale: Ensure consistent JSON metadata by handling import failures.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Graceful handling of `src.__version__` import failure.
  - Unit tests cover import failure scenario.
  - Documentation updated with handling strategy.

### B151. [P3] Handle cases where `mass_min` or `mass_max` are not provided and `mass_series` is empty.

- File: `src/core/spectrum/_assign.py`
- Rationale: Graceful handling of these edge cases will improve the robustness of the function.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Edge case handling logic is implemented and tested.
  - Documentation is updated to reflect the new behavior.

### B152. [P3] Handle edge cases in search method.

- File: `src/core/formula_db/_reader.py`
- Rationale: Improves search accuracy and user experience.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add checks for target mass outside the block range.
  - Return appropriate messages for no results found.

### B153. [P3] Handle exceptions in file operations during export.

- File: `tests/unit/test_export.py`
- Rationale: Ensure robustness against file I/O errors.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add exception handling in the `export_result_table` function.
  - New test cases are added to verify exception handling.
  - All test cases pass successfully.

### B154. [P3] Handle missing columns in 'molecules' DataFrame gracefully.

- File: `src/core/pipeline/_test_verify.py`
- Rationale: The function should not fail if required columns are missing.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add checks for the presence of required columns in 'molecules'.
  - Implement fallback logic for missing columns.
  - Verify that the function handles missing columns without errors.

### B155. [P3] Handle non-numeric values in _match_row_by_mass

- File: `src/core/pipeline/_helpers.py`
- Rationale: Ensure robustness against invalid data.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Validate `mass_col` values before processing.
  - Add error handling for non-numeric values.

### B156. [P3] Implement a factory method for 'FormulaSearchConfig'.

- File: `src/core/spectrum/_constants.py`
- Rationale: The current default values for 'ranges' may become outdated if '_FS_RANGES' changes. A factory method can ensure that instances are always created with the latest defaults.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add a factory method to 'FormulaSearchConfig' that creates instances with the latest defaults.
  - Update the documentation to reflect the new factory method.

### B157. [P3] Implement a factory method for creating molecular fragments.

- File: `src/core/chemistry/_functional.py`
- Rationale: Reduces code duplication and improves maintainability.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A generic function that can create any molecular fragment based on a configuration.

### B158. [P3] Implement a loading indicator for batch processing.

- File: `src/ui/_tabs.py`
- Rationale: To provide feedback to the user during long-running batch operations.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A loading indicator is added to the batch tab.
  - The indicator is displayed when batch processing starts and hidden when it completes.

### B159. [P3] Implement caching and optimization mechanisms for FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS.

- File: `src/core/chemistry/_fragment_data.py`
- Rationale: The current implementation of FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS does not include any caching or optimization mechanisms. Implementing these mechanisms will improve the performance of the code.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Caching and optimization mechanisms are implemented for FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS.
  - The performance of the code is improved.
  - The implementation is documented and easy to understand.

### B160. [P3] Implement comprehensive error handling for `_ion_shift`

- File: `src/core/spectrum/_generate.py`
- Rationale: To ensure robustness against unrecognized `ion_mode` values.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add error handling for unrecognized `ion_mode` values.
  - Update documentation to reflect the new error handling behavior.

### B161. [P3] Implement comprehensive error handling for `_neutral_to_ion_mass`

- File: `src/core/spectrum/_generate.py`
- Rationale: To ensure robustness against unrecognized `ion_mode` values.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add error handling for unrecognized `ion_mode` values.
  - Update documentation to reflect the new error handling behavior.

### B162. [P3] Implement controlled timing mechanism in `build_database`

- File: `src/core/formula_db/_builder.py`
- Rationale: The function uses `time.perf_counter()` for timing, which might introduce variability in build times. Implement a more controlled timing mechanism to improve reproducibility.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Identify the current timing mechanism and its limitations.
  - Implement a more controlled timing mechanism.
  - Test with various scenarios to ensure reproducibility.
  - Update documentation to reflect changes.

### B163. [P3] Implement error handling for RDKit molecule sanitization.

- File: `src/core/chemistry/_visualize.py`
- Rationale: Prevents silent failures in visualization.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Assertions added to check RDKit molecule validity after sanitization.

### B164. [P3] Implement file path validation in _save_mol and _save_png

- File: `src/structures/widgets.py`
- Rationale: Ensure that file paths are validated and sanitized to prevent security issues.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add file path validation and sanitization in the methods.
  - Write unit tests to verify the validation logic.

### B165. [P3] Implement input validation and sanitization for FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS.

- File: `src/core/chemistry/_fragment_data.py`
- Rationale: The current implementation of FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS does not include any input validation or sanitization. Implementing these mechanisms will improve the security of the code.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Input validation and sanitization are implemented for FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS.
  - The security of the code is improved.
  - The implementation is documented and easy to understand.

### B166. [P3] Implement input validation for file paths and user inputs.

- File: `src/ui/_results.py`
- Rationale: Prevent potential security vulnerabilities.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Input validation added to methods like _on_formula_double_click.
  - Unit tests added to verify the validation logic.

### B167. [P3] Implement lazy loading for imported functions.

- File: `src/core/chemistry/fragments.py`
- Rationale: This will improve performance by reducing the initial import time.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Lazy loading is implemented for the imported functions.
  - Performance tests are conducted to verify the improvement.

### B168. [P3] Implement missing functionality in the src/__init__.py module.

- File: `src/__init__.py`
- Rationale: To ensure the module fulfills its intended purpose.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The module exports necessary functions or classes.
  - All required functionalities (deconvolution, formula assignment, homologous series detection) are implemented.
  - Unit tests are added to verify the correctness of the implemented functionalities.

### B169. [P3] Improve content validation in `test_cli_writes_output_file`

- File: `tests/unit/test_cli.py`
- Rationale: Thoroughly validate the content of the output file to ensure complete testing.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add more assertions to validate the content of the output file.

### B170. [P3] Improve error logging

- File: `tools/build_exe.py`
- Rationale: Enhance debugging capabilities.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Detailed error messages and stack traces are logged in all critical sections.
  - Unit tests are written to verify the logging behavior.

### B171. [P3] Limit the size of the `load_config` cache.

- File: `src/configs/loader.py`
- Rationale: Prevent excessive memory usage by setting a reasonable limit on the cache size.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The `maxsize` parameter of the `lru_cache` decorator is set to a reasonable value.
  - Memory usage is monitored to ensure it remains within acceptable limits.
  - Documentation is updated to reflect the cache size limit.

### B172. [P3] Log the exact command-line arguments used.

- File: `src/cli.py`
- Rationale: Improves reproducibility by logging the exact command-line arguments.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Command-line arguments are logged at the start of the execution.
  - Unit tests are added to verify the logging.

### B173. [P3] Optimize CSV file reading to handle large files efficiently.

- File: `tests/unit/test_chemical_validity.py`
- Rationale: Improves performance and scalability of the test.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Refactor lines 25-28 to use a streaming approach or generator.

### B174. [P3] Optimize LRU block cache in FormulaDatabaseReader.

- File: `src/core/formula_db/__init__.py`
- Rationale: The use of LRU block cache is mentioned but not detailed in the provided source. Optimizing the cache size and eviction policy will improve the performance of the database search.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Cache size and eviction policy optimized.
  - Performance tests conducted to verify improvements.

### B175. [P3] Optimize UUID generation for high-frequency benchmarks.

- File: `tools/run_benchmark.py`
- Rationale: To reduce performance overhead when running benchmarks frequently.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Profile UUID generation time.
  - Implement an alternative method if necessary.
  - Update tests to measure performance.

### B176. [P3] Optimize `_enrich` function for empty input.

- File: `src/core/spectrum/_build.py`
- Rationale: Reduce performance overhead when handling empty data.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Function returns an empty DataFrame without creating a new one.
  - Performance tests show improved execution time for empty input.

### B177. [P3] Optimize bond creation logic for large molecules.

- File: `src/core/chemistry/_factories.py`
- Rationale: Improves performance for large molecule creation.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Profiled the module with large molecule creation.
  - Optimized bond creation logic if necessary.

### B178. [P3] Optimize bond order calculation methods.

- File: `tests/unit/test_atoms.py`
- Rationale: Improve performance for large molecules.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Profiling done to identify bottlenecks.
  - Optimized methods implemented.
  - Performance tests added to verify improvements.

### B179. [P3] Optimize cache management in `test_cached_generation_is_consistent`.

- File: `tests/unit/test_generate_cache.py`
- Rationale: Improves performance in a larger test suite by reducing cache clear operations.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Implemented a fixture to manage cache state.
  - Updated test documentation.

### B180. [P3] Optimize centroiding algorithm for large datasets.

- File: `src/core/io/mzml_bridge.py`
- Rationale: Reduce computational overhead for large mzML files.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Optimized centroiding algorithm implemented.
  - Performance benchmarks updated.

### B181. [P3] Optimize dynamic configuration loading.

- File: `src/configs/__init__.py`
- Rationale: Reduce performance overhead associated with dynamic configuration loading.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Implement caching mechanism for frequently accessed configurations.

### B182. [P3] Optimize memory usage for large RAW files

- File: `src/core/io/raw_thermo_adapter.py`
- Rationale: To improve performance and prevent memory leaks.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The `average_raw_to_df` function is optimized to handle large files gracefully.
  - A performance test is added to verify the optimization.

### B183. [P3] Optimize module imports

- File: `src/core/pipeline/__init__.py`
- Rationale: Reducing the number of imports can improve the performance and maintainability of the module.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Redundant imports are removed.
  - Performance metrics are improved.

### B184. [P3] Optimize performance for large fragment libraries.

- File: `tests/unit/test_fragment_combinations.py`
- Rationale: Improve efficiency for real-world applications.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Performance analysis conducted.
  - Optimizations implemented and tested.

### B185. [P3] Optimize performance of imported functions in `structures/__init__.py`.

- File: `src/structures/__init__.py`
- Rationale: Ensure efficient execution of critical functions.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Profile the functions to identify performance issues.
  - Implement optimizations to address identified issues.

### B186. [P3] Optimize the 'ranges' data structure in 'FormulaSearchConfig'.

- File: `src/core/spectrum/_constants.py`
- Rationale: The current dictionary implementation may not be the most efficient for frequent lookups. Consider using a more efficient data structure if performance becomes an issue.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Profile the performance of the 'FormulaSearchConfig' class with the new data structure.
  - Ensure that the new data structure does not compromise the functionality of the class.

### B187. [P3] Optimize the `sample_table` fixture

- File: `tests/unit/test_pipeline.py`
- Rationale: Optimize the fixture to reduce performance overhead if it is complex or if there are many tests using it.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Analyze the fixture's complexity.
  - Implement optimizations if applicable.
  - Update test documentation if necessary.

### B188. [P3] Optimize the file reading process in the test.

- File: `tests/integration/test_app_smoke.py`
- Rationale: Efficient file reading can improve the performance of the test.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Profile the test to measure the time taken to read the CSV files.
  - Implement optimizations to reduce the time taken to read the CSV files.
  - Add a comment explaining the optimizations made.

### B189. [P3] Optimize the formula search in `assign_formulas`.

- File: `tests/unit/test_nom_prioritize.py`
- Rationale: Reduce the time taken by the formula search to improve test suite performance.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Profile the formula search and implement optimizations.
  - Update tests to use smaller datasets if necessary.

### B190. [P3] Optimize the handling of large datasets in `List[Path]` and `Optional[Path]` fields.

- File: `src/testing/report_models.py`
- Rationale: This will improve the performance of the application.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Optimization logic is implemented.
  - Performance benchmarks are conducted.
  - Unit tests are added to cover the optimization logic.

### B191. [P3] Parameterize similar tests

- File: `tests/unit/test_pipeline.py`
- Rationale: Reduce code duplication by parameterizing tests with similar logic.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Identify tests with similar logic.
  - Refactor these tests to use parameterization.
  - Update test documentation if necessary.

### B192. [P3] Parameterize the number of runs for benchmarking.

- File: `src/core/benchmark_assign.py`
- Rationale: Enhances the accuracy and flexibility of performance measurement.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Parameterize the `runs` variable in the benchmark function.
  - Update documentation to reflect the new parameter.

### B193. [P3] Refactor 'test_save_png' to use an in-memory file-like object

- File: `tests/unit/test_van_krevelen.py`
- Rationale: Improves performance and resource usage in testing.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Replace file creation with an in-memory file-like object in 'test_save_png'.
  - Run tests and confirm that the plot data is correctly saved in the in-memory object.

### B194. [P3] Refactor `PipelineTimings` to use a dictionary for dynamic stage names.

- File: `src/core/timer.py`
- Rationale: Reduces maintenance overhead when pipeline stages change.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Dynamic dictionary is implemented.
  - Existing tests are updated to accommodate the change.
  - Documentation is updated to reflect the new implementation.

### B195. [P3] Refactor `_beynon_m1_ratio_cached` for flexibility

- File: `src/core/spectrum/_chem.py`
- Rationale: Allow dynamic updates to isotope coefficients without code changes.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Coefficients are loaded from a configurable source.
  - Unit tests are updated to cover new functionality.

### B196. [P3] Refactor `_write` function for more flexible data writing

- File: `tests/unit/test_batch.py`
- Rationale: Allow `_write` to handle different data formats and contents.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add parameters for specifying data content.
  - Support writing different file formats (e.g., JSON, TSV).

### B197. [P3] Refactor import handling for 'StructureViewerTab'.

- File: `src/ui/_build.py`
- Rationale: To surface import errors during development and improve code reliability.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Remove the try-except block around the import.
  - Add a test to verify the import behavior.

### B198. [P3] Refactor module to group related symbols.

- File: `src/core/formula_db/__init__.py`
- Rationale: The module exports a large number of symbols, which can make the codebase harder to maintain. Grouping related symbols into submodules or classes will improve maintainability.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Symbols grouped into submodules or classes.
  - Documentation updated to reflect changes.

### B199. [P3] Refactor molecule creation module to use a factory pattern.

- File: `src/core/chemistry/_factories.py`
- Rationale: Simplifies future additions of new molecules.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Refactored the module to use a factory pattern.
  - All existing molecule creation functions updated to use the new pattern.

### B200. [P3] Refactor print statements for better logging and testing.

- File: `src/core/benchmark_assign.py`
- Rationale: Improves maintainability and support for automated testing.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Replace print statements with logging calls.
  - Update tests to capture and verify log outputs.

### B201. [P3] Refactor test cases to reduce duplication.

- File: `tests/unit/test_fragment_combinations.py`
- Rationale: Improve code readability and maintainability.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Code refactoring completed.
  - All tests pass without changes.

### B202. [P3] Refactor the `to_int_or_zero` function to handle more edge cases.

- File: `src/sim/process_pubchem_candidates.py`
- Rationale: The current implementation of `to_int_or_zero` may not handle all edge cases, such as non-numeric strings.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The function is refactored to handle more edge cases.
  - The refactored function is tested with various inputs.
  - The refactored function is integrated into the module.

### B203. [P3] Refactor the benchmark function to return structured results.

- File: `src/core/benchmark.py`
- Rationale: To improve maintainability and facilitate integration with automated testing frameworks.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Function refactored to return a structured object containing timing and result row information.
  - Unit tests updated to verify the new return structure.

### B204. [P3] Refactor the tab-building methods to reduce code duplication.

- File: `src/ui/_tabs.py`
- Rationale: Improving maintainability and reducing the risk of errors in tab construction.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Common tab-building logic is extracted into a separate method.
  - All tab-building methods are refactored to use the new common method.

### B205. [P3] Refactor threading usage for better synchronization.

- File: `src/ui/_results.py`
- Rationale: Ensure thread safety and prevent race conditions.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Thread-safe access to shared resources implemented.
  - Integration tests added to verify the correctness of background tasks.

### B206. [P3] Replace `_os._exit(0)` with a more graceful shutdown method in `_on_close`.

- File: `src/ui/_log.py`
- Rationale: Ensure proper resource cleanup and application state consistency.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Graceful shutdown method is implemented.
  - Resource cleanup is verified during application exit.

### B207. [P3] Review and sanitize `messages` attribute in `PipelineRunResult` class.

- File: `src/core/pipeline/_stats.py`
- Rationale: The `PipelineRunResult` class includes a `messages` attribute that stores human-readable status/diagnostic messages. Ensure that these messages do not contain sensitive information that could be exposed to unauthorized users.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Review the `messages` attribute in `PipelineRunResult` to ensure it does not store sensitive information.
  - Update the attribute to sanitize any sensitive information before storing it.
  - Update tests to cover scenarios where sensitive information is present in the `messages` attribute.

### B208. [P3] Review and secure traceback usage

- File: `src/ui/_deps.py`
- Rationale: Traceback information may expose sensitive data.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Traceback usage is reviewed for security risks.
  - Sensitive information is sanitized or removed.

### B209. [P3] Review and update `_nom_distance` logic

- File: `src/core/spectrum/_chem.py`
- Rationale: Ensure the function behaves correctly for all possible input scenarios.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Logic is reviewed and updated if necessary.
  - Unit tests are added to cover all edge cases.

### B210. [P3] Review and update configuration symbols in `__all__`.

- File: `src/configs/__init__.py`
- Rationale: Ensure that only intended symbols are exposed for public use.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Update `__all__` to include only symbols that are meant to be public.

### B211. [P3] Review and update package documentation

- File: `src/core/domain/__init__.py`
- Rationale: To ensure that the package documentation is clear and up-to-date.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The package's docstring is updated to reflect its current state.
  - Additional documentation files are added if necessary.
  - Documentation is reviewed for accuracy and completeness.

### B212. [P3] Review and update the licensing notes for 'src.configs.CHEM' and 'src.configs.PIPELINE'.

- File: `src/core/spectrum/_constants.py`
- Rationale: The module imports from 'src.configs.CHEM' and 'src.configs.PIPELINE', which are not specified in the static AST facts. Ensure these imports are compliant with the project's licensing requirements.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Review the licensing notes for 'src.configs.CHEM' and 'src.configs.PIPELINE'.
  - Update the licensing notes if necessary to ensure compliance.

### B213. [P3] Review the repository structure and ensure that the path calculation remains valid.

- File: `tests/conftest.py`
- Rationale: This will prevent unexpected behavior or security issues if the repository structure changes.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - The repository structure is reviewed.
  - The path calculation is verified to be valid.
  - Any necessary changes are made to the code or documentation.

### B214. [P3] Sanitize file path in `average_raw_to_df`

- File: `src/core/io/raw_bridge.py`
- Rationale: Prevent directory traversal attacks by validating file paths.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - File path validation implemented in `average_raw_to_df`.
  - Security tests covering malicious file paths.

### B215. [P3] Sanitize inputs for `_progress_bar`

- File: `src/core/formula_db/_builder.py`
- Rationale: The function writes directly to `sys.stderr` without sanitizing inputs, which could lead to security vulnerabilities if inputs are derived from untrusted sources.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Implement input validation and sanitization for `_progress_bar`.
  - Test with various inputs to ensure no security issues arise.
  - Update documentation to reflect changes.

### B216. [P3] Sanitize user input in `tkinter.messagebox`

- File: `src/ui/theme.py`
- Rationale: The module imports `tkinter.messagebox`, which could be used to display messages to the user. Ensure that any user input is properly sanitized to prevent injection attacks.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - A sanitization mechanism is implemented for user input in `tkinter.messagebox`.
  - Code review is conducted to ensure that all user input is properly sanitized.
  - Security tests are conducted to verify that the sanitization mechanism prevents injection attacks.

### B217. [P3] Standardize test method naming conventions.

- File: `tests/unit/test_atoms.py`
- Rationale: Improve code readability and maintainability.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Naming conventions documented.
  - All test methods renamed to follow conventions.
  - Code review completed without naming issues.

### B218. [P3] Update `test_create_histograms_plot` to verify histogram content.

- File: `tests/unit/test_statistics.py`
- Rationale: This will ensure that the histograms are plotted correctly.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Assertions are added to verify the content of the histograms.
  - Tests are updated to pass with the new assertions.

### B219. [P3] Update documentation for _compute_penalty

- File: `tests/unit/test_isotope_filter.py`
- Rationale: Clarify usage and edge cases.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Documentation includes detailed explanation of the method.
  - Documentation is reviewed and merged.

### B220. [P3] Update error messages for RDKit availability

- File: `src/structures/widgets.py`
- Rationale: The current error messages for RDKit availability are in Russian. Consider providing English messages for internationalization.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Update the error messages to be in English.
  - Ensure that the application supports internationalization for error messages.

### B221. [P3] Use temporary files for JSON data in tests.

- File: `tests/unit/test_raw_bridge.py`
- Rationale: Hardcoded JSON file paths might lead to issues if the path changes or if the file is not accessible.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Replace hardcoded JSON file paths with temporary files created by `tmp_path`.
  - Ensure that the tests are independent of external file paths.

### B222. [P3] Validate `generated_at` timestamp format in JSON export.

- File: `tests/unit/test_export.py`
- Rationale: Ensure the timestamp is in the expected format for consistency.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Modify the JSON export test to check the timestamp format.
  - The test case passes successfully.

### B223. [P3] Validate `metadata` input in `_write_json`

- File: `src/core/pipeline/_export.py`
- Rationale: Ensure robustness by validating and sanitizing the `metadata` input.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Input validation added to `_write_json`.
  - Unit tests cover various `metadata` inputs.
  - Documentation updated with validation rules.

### B224. [P3] Validate annotation data before running denoising tests.

- File: `tests/unit/test_denoise.py`
- Rationale: To ensure the accuracy of the denoising test results.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Annotation data validation tests are implemented.
  - Validation tests are run before each denoising test.

### B225. [P3] Validate bond order in `connect_to` method.

- File: `src/core/chemistry/_fragment.py`
- Rationale: Ensure that the bond order is within a reasonable range to prevent incorrect molecular structures.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add a check for bond order in the `connect_to` method.
  - Update tests to cover invalid bond orders.
  - Verify that the method raises an error for invalid bond orders.

### B226. [P3] Validate file paths in `save_png`.

- File: `src/structures/rdkit_utils.py`
- Rationale: Prevent directory traversal attacks by validating file paths.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Input validation is implemented.
  - Test cases cover invalid file paths.

### B227. [P3] Validate progress_callback in _make_sub_progress

- File: `src/core/pipeline/_helpers.py`
- Rationale: Prevent errors from invalid callbacks.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Check if `progress_callback` is callable.
  - Add error handling for non-callable callbacks.

### B228. [P3] Validate the `elements` argument to ensure it only contains expected characters.

- File: `src/core/formula_db/__main__.py`
- Rationale: This will prevent unexpected behavior if the input is not properly validated.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Validation is added to ensure the `elements` argument only contains expected characters.
  - Appropriate error handling is added for invalid input.

### B229. [P3] Validate the content of the tuples in `test_wrapper_returns_list_of_tuples`.

- File: `tests/unit/test_generate_cache.py`
- Rationale: Ensures the tuples contain valid and expected data, not just structure.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Added assertions to validate tuple contents.
  - Updated test documentation.

### B230. [P3] Validate the correctness of assigned formulas in `test_nom_prioritize_on_set_01`.

- File: `tests/unit/test_nom_prioritize.py`
- Rationale: Ensure that the assigned formulas are correct, not just that peaks are assigned.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add assertions to check the correctness of the assigned formulas.
  - Update the test to include expected formula values.

### B231. [P3] Verify fallback size in 'test_no_crash_on_equal_intensities'

- File: `tests/unit/test_van_krevelen.py`
- Rationale: Ensures the plot uses a fallback size when all intensities are equal.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Add assertions to check the plot size in 'test_no_crash_on_equal_intensities'.
  - Run tests and confirm that the plot has the expected fallback size.

### B232. [P3] Write tests for src/core/io/__init__.py

- File: `src/core/io/__init__.py`
- Rationale: To ensure the package's correctness and maintainability.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Unit tests are written for the package's functionality.
  - Integration tests are written to verify the package's importability.

### B233. [P3] Write unit tests for the chemistry package

- File: `src/core/chemistry/__init__.py`
- Rationale: To ensure the package's correctness and maintainability.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Test files are added to the tests directory.

### B234. [P3] Анализ зависимостей find_and_visualize_molecules

- File: `src/ui/_structures.py`
- Rationale: Проверить зависимости модуля find_and_visualize_molecules и убедиться, что они безопасны, чтобы избежать потенциальных проблем безопасности.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Анализ зависимостей завершен.
  - Убедиться, что зависимости безопасны и не содержат уязвимостей.

### B235. [P3] Добавить кэширование в функцию `list_presets`.

- File: `src/configs/presets_loader.py`
- Rationale: Улучшить производительность при повторных вызовах функции.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавлено кэширование результатов.
  - Обновлены тесты для проверки кэширования.

### B236. [P3] Добавить логирование для отслеживания использования кэша.

- File: `src/core/pipeline/_cache.py`
- Rationale: Помочь в диагностике проблем с производительностью и памятью.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавить логирование ключевых операций кэширования.
  - Проверить логи на наличие полезной информации.

### B237. [P3] Добавить обработку дублирующихся и некорректных значений в колонках 'mass' и 'intensity'.

- File: `src/core/spectrum/_load.py`
- Rationale: Улучшение корректности данных в объекте Spectrum.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавлена проверка на наличие дублирующихся или некорректных значений.
  - Обновлены тесты для проверки корректности данных.

### B238. [P3] Добавить обработку исключений и логирование в _save_png.

- File: `src/testing/structure_export.py`
- Rationale: Улучшить отслеживание ошибок при сохранении изображений.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавить обработку исключений и логирование в `_save_png` для отслеживания ошибок при сохранении изображений.

### B239. [P3] Добавить проверку наличия необходимых столбцов в CSV-файлах.

- File: `tests/unit/test_annotations_consistency.py`
- Rationale: Улучшение корректности тестов.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавлена проверка наличия необходимых столбцов в загруженных данных.

### B240. [P3] Добавить тестирование для различных фрагментов в _fragment_to_rdkit.

- File: `src/testing/structure_export.py`
- Rationale: Убедиться в корректной обработке различных фрагментов.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Провести тестирование с различными фрагментами и сравнить результаты обработки с использованием `to_rdkit_mol` и ручной сборки.

### B241. [P3] Добавление лицензионных заметок в начало файла.

- File: `src/core/domain/atoms.py`
- Rationale: Улучшение документации и соответствия стандартам открытия исходного кода.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавлены лицензионные заметки в начало файла.
  - Проверка соответствия лицензионных заметок стандартам открытия исходного кода.

### B242. [P3] Добавление обработки дополнительных колонок в `load_spectrum_csv`

- File: `src/testing/artifact_export.py`
- Rationale: Улучшение корректности обработки CSV файлов с дополнительными данными.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Обновить функцию для игнорирования ненужных колонок.
  - Добавить тесты с CSV файлами, содержащими дополнительные колонки.

### B243. [P3] Добавление обработки исключений при сохранении графиков.

- File: `src/core/spectrum/_visualize.py`
- Rationale: Улучшение устойчивости при работе с файлами.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавление блоков try-except в сохранение файлов.
  - Тестирование на различных сценариях ошибок.

### B244. [P3] Добавление обработки ситуации с одновременными двойными и тройными связями в метод `_update_hybridization`.

- File: `src/core/domain/atoms.py`
- Rationale: Улучшение корректности определения гибернизации для атомов углерода с сложными связями.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Обновлен метод `_update_hybridization` для корректного определения гибернизации при наличии одновременно двойных и тройных связей.
  - Добавлены тесты для проверки корректности работы обновленного метода.

### B245. [P3] Добавление проверки входных данных для функции visualize_series.

- File: `src/core/spectrum/_visualize.py`
- Rationale: Улучшение корректности работы функции.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавление проверок на корректность входных данных.
  - Тестирование на некорректных входных данных.

### B246. [P3] Использовать более надежный алгоритм хеширования для _hash.

- File: `src/core/pipeline/_cache.py`
- Rationale: Уменьшить вероятность коллизий и некорректного кэширования.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Выбрать и интегрировать надежный алгоритм хеширования.
  - Провести тестирование на отсутствие коллизий.

### B247. [P3] Обновить обработку ошибок в функции `list_presets`.

- File: `src/configs/presets_loader.py`
- Rationale: Улучшить отладку и обработку конкретных ошибок.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Заменены общие блоки `except Exception` на более специфичные.
  - Обновлены тесты для проверки обработки ошибок.

### B248. [P3] Обработка пустых колонок в `plot_histogram`

- File: `src/testing/artifact_export.py`
- Rationale: Улучшение корректности обработки пустых данных в колонках.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Обновить функцию для корректной обработки пустых колонок.
  - Добавить тесты с DataFrame, содержащими только NaN значения в указанной колонке.

### B249. [P3] Оптимизация загрузки данных для тестов.

- File: `tests/unit/test_annotations_consistency.py`
- Rationale: Ускорение выполнения тестов.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Использование фикстур для кэширования загруженных данных.

### B250. [P3] Оптимизация функции load_spectrum для обработки больших файлов.

- File: `src/core/spectrum/_load.py`
- Rationale: Улучшение производительности приложения при работе с большими данными.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Использование стратегий обработки больших файлов, таких как читание по частям.
  - Обновлены тесты для проверки производительности.

### B251. [P3] Оптимизировать алгоритм поиска файлов в функции `_import_folder`.

- File: `src/ui/_presets.py`
- Rationale: Улучшение производительности при обработке больших папок.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Измерение времени выполнения до и после оптимизации.
  - Обновление комментариев в коде.

### B252. [P3] Оптимизировать чтение заголовков CSV

- File: `tests/unit/test_structural_validity.py`
- Rationale: Улучшить производительность тестов путем кэширования заголовков CSV.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Кэширование заголовков CSV реализовано.
  - Производительность тестов улучшена.

### B253. [P3] Оптимизировать чтение и анализ исходного кода в тестах.

- File: `tests/unit/test_app_fallback.py`
- Rationale: Текущий подход может быть медленным для больших проектов.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Использовать более эффективные методы для чтения и анализа исходного кода.
  - Провести нагрузочное тестирование для проверки производительности.

### B254. [P3] Параметризовать тесты для повторяющихся проверок

- File: `tests/unit/test_structural_validity.py`
- Rationale: Упростить поддержку и уменьшить дублирование кода.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Тесты параметризованы.
  - Код тестов упрощен и более читаем.

### B255. [P3] Сделать тесты более гибкими к изменениям в структуре кода.

- File: `tests/unit/test_app_fallback.py`
- Rationale: Текущие тесты зависят от конкретного расположения и формата кода.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Изменить подход к поиску и анализу сигнатур функций.
  - Убедиться, что тесты продолжают работать после изменений в структуре кода.

### B256. [P3] Улучшение обработки ошибок в _load_structure_preview

- File: `src/ui/_structures.py`
- Rationale: Улучшить обработку исключений в методе _load_structure_preview, чтобы избежать непредсказуемого поведения приложения.
- Evidence: Нет; требуется ручная проверка.
- Definition of Done:
  - Добавлены тесты для проверки обработки исключений.
  - Метод корректно обрабатывает исключения и отображает сообщение об ошибке.

## Proposed tests

### T1. [unit] `__version__`

- File: `src/__init__.py`
- Scenario: Check if the __version__ variable is correctly set to '0.7.0'.
- Expected result: The __version__ variable should match the expected version string.
- Evidence: Нет; требуется ручная проверка.

### T2. [integration] `module`

- File: `src/__init__.py`
- Scenario: Verify that the module can be imported without raising any exceptions.
- Expected result: The module should import successfully without errors.
- Evidence: Нет; требуется ручная проверка.

### T3. [unit] `module`

- File: `src/__init__.py`
- Scenario: Test if the module's functionality aligns with its purpose statement.
- Expected result: The module should perform deconvolution, formula assignment, and homologous series detection as described.
- Evidence: Нет; требуется ручная проверка.

### T4. [unit] `_parse_element_ranges`

- File: `src/cli.py`
- Scenario: Test parsing of valid element ranges.
- Expected result: A dictionary with correct element ranges.
- Evidence: Нет; требуется ручная проверка.

### T5. [unit] `_resolve_input`

- File: `src/cli.py`
- Scenario: Test resolution of a RAW input file.
- Expected result: A JSON string representing the averaged data.
- Evidence: Нет; требуется ручная проверка.

### T6. [integration] `main`

- File: `src/cli.py`
- Scenario: Test the entire CLI with a valid input file and preset.
- Expected result: A successful execution with a valid output file.
- Evidence: Нет; требуется ручная проверка.

### T7. [unit] `CHEM, PIPELINE, PATHS`

- File: `src/configs/__init__.py`
- Scenario: Test access to public configuration symbols.
- Expected result: Symbols are accessible and return expected values.
- Evidence: `L14–L19` — Symbols `CHEM`, `PIPELINE`, `PATHS` are imported.

### T8. [unit] `load_config`

- File: `src/configs/__init__.py`
- Scenario: Test loading a valid configuration file.
- Expected result: Configuration object is returned without errors.
- Evidence: `L20–L20` — Function `load_config` is imported.

### T9. [unit] `load_config`

- File: `src/configs/__init__.py`
- Scenario: Test loading an invalid configuration file.
- Expected result: ConfigError is raised.
- Evidence: `L16–L16` — Class `ConfigError` is imported.

### T10. [unit] `load_config`

- File: `src/configs/loader.py`
- Scenario: Test loading a valid JSON configuration file.
- Expected result: A `ConfigNamespace` object is returned without raising an exception.
- Evidence: Нет; требуется ручная проверка.

### T11. [unit] `load_config`

- File: `src/configs/loader.py`
- Scenario: Test loading a non-existent configuration file.
- Expected result: A `ConfigError` is raised with a message indicating the file is missing.
- Evidence: Нет; требуется ручная проверка.

### T12. [unit] `load_config`

- File: `src/configs/loader.py`
- Scenario: Test loading a malformed JSON configuration file.
- Expected result: A `ConfigError` is raised with a message indicating the JSON is invalid.
- Evidence: Нет; требуется ручная проверка.

### T13. [unit] `list_presets`

- File: `src/configs/presets_loader.py`
- Scenario: Проверка возвращаемого списка пресетов при отсутствии директории с пресетами.
- Expected result: Возвращается пустой список.
- Evidence: Нет; требуется ручная проверка.

### T14. [unit] `load_preset`

- File: `src/configs/presets_loader.py`
- Scenario: Проверка загрузки пресета с существующим идентификатором.
- Expected result: Возвращается корректный словарь с данными пресета.
- Evidence: Нет; требуется ручная проверка.

### T15. [unit] `load_preset`

- File: `src/configs/presets_loader.py`
- Scenario: Проверка загрузки пресета с несуществующим идентификатором.
- Expected result: Возвращается None.
- Evidence: Нет; требуется ручная проверка.

### T16. [unit] `_safe_df`

- File: `src/core/_safety.py`
- Scenario: Input DataFrame is None.
- Expected result: Return an empty DataFrame.
- Evidence: Нет; требуется ручная проверка.

### T17. [unit] `safe`

- File: `src/core/_safety.py`
- Scenario: Both `obj` and `default` are None.
- Expected result: Return `default`.
- Evidence: Нет; требуется ручная проверка.

### T18. [unit] `safe`

- File: `src/core/_safety.py`
- Scenario: `obj` is not None and `default` is None.
- Expected result: Return `obj`.
- Evidence: Нет; требуется ручная проверка.

### T19. [unit] `_classify`

- File: `src/core/batch.py`
- Scenario: Test with filenames containing multiple pattern matches.
- Expected result: Returns the correct role and sample name based on the longest matching pattern.
- Evidence: Нет; требуется ручная проверка.

### T20. [unit] `_list_files`

- File: `src/core/batch.py`
- Scenario: Test with a directory containing files with various extensions.
- Expected result: Returns a list of all files with the specified extensions.
- Evidence: Нет; требуется ручная проверка.

### T21. [unit] `compute_sample_summary`

- File: `src/core/batch.py`
- Scenario: Test with a `pandas.DataFrame` containing various columns.
- Expected result: Returns a summary dictionary with correct statistics.
- Evidence: Нет; требуется ручная проверка.

### T22. [unit] `benchmark`

- File: `src/core/benchmark.py`
- Scenario: Test with a valid data set directory.
- Expected result: Successful benchmarking with timing and result row information printed.
- Evidence: `L60–L63` — The `benchmark` function is called with a valid directory path.

### T23. [unit] `benchmark`

- File: `src/core/benchmark.py`
- Scenario: Test with a missing source CSV file.
- Expected result: Error message printed indicating the missing file.
- Evidence: `L20–L22` — The function checks for the existence of the source CSV file and prints an error message if it is missing.

### T24. [unit] `benchmark`

- File: `src/core/benchmark.py`
- Scenario: Test with a missing deuteromethylated CSV file.
- Expected result: Benchmarking continues with the available files.
- Evidence: `L45–L46` — The function checks for the existence of the deuteromethylated CSV file and passes `None` if it is missing.

### T25. [unit] `benchmark`

- File: `src/core/benchmark_assign.py`
- Scenario: Test with a small, controlled dataset to ensure the function runs without exceptions.
- Expected result: No exceptions raised, benchmark completes successfully.
- Evidence: Нет; требуется ручная проверка.

### T26. [integration] `benchmark`

- File: `src/core/benchmark_assign.py`
- Scenario: Test with a range of input parameters to verify the function's performance consistency.
- Expected result: Consistent performance metrics across different input scenarios.
- Evidence: Нет; требуется ручная проверка.

### T27. [unit] `benchmark`

- File: `src/core/benchmark_assign.py`
- Scenario: Test the `_median` function with various input lists to ensure it calculates the median correctly.
- Expected result: Correct median values returned for different input lists.
- Evidence: Нет; требуется ручная проверка.

### T28. [unit] `license`

- File: `src/core/chemistry/__init__.py`
- Scenario: Verify that a LICENSE file exists in the repository root.
- Expected result: LICENSE file is present.
- Evidence: Нет; требуется ручная проверка.

### T29. [integration] `package_structure`

- File: `src/core/chemistry/__init__.py`
- Scenario: Check if the package contains other modules or files that indicate its current state.
- Expected result: Other modules or files are present.
- Evidence: Нет; требуется ручная проверка.

### T30. [unit] `test_coverage`

- File: `src/core/chemistry/__init__.py`
- Scenario: Ensure that there are corresponding test files for this module in the tests directory.
- Expected result: Test files are present.
- Evidence: Нет; требуется ручная проверка.

### T31. [integration] `create_anthracene`

- File: `src/core/chemistry/_factories.py`
- Scenario: Ensure the creation of anthracene with correct connectivity and aromaticity.
- Expected result: MoleculeFragment with 14 carbon atoms, 14 bonds, and aromaticity set to 10.
- Evidence: Нет; требуется ручная проверка.

### T32. [unit] `create_benzene`

- File: `src/core/chemistry/_factories.py`
- Scenario: Check the creation of benzene with correct atom count, bond count, and aromaticity.
- Expected result: MoleculeFragment with 6 carbon atoms, 6 bonds, and aromaticity set to 4.
- Evidence: Нет; требуется ручная проверка.

### T33. [unit] `create_cyclodecapentaene`

- File: `src/core/chemistry/_factories.py`
- Scenario: Verify the creation of cyclodecapentaene with alternating double bonds.
- Expected result: MoleculeFragment with 10 carbon atoms and alternating single and double bonds.
- Evidence: Нет; требуется ручная проверка.

### T34. [unit] `connect_to`

- File: `src/core/chemistry/_fragment.py`
- Scenario: Connecting two fragments with valid attachment points.
- Expected result: A new MoleculeFragment with updated attributes.
- Evidence: `L125–L172` — The method raises ValueError if attachment points are already occupied.

### T35. [unit] `get_free_attachment_points`

- File: `src/core/chemistry/_fragment.py`
- Scenario: Getting free attachment points for a fragment with multiple free bonds.
- Expected result: A list of atom indices with the correct multiplicity.
- Evidence: `L67–L76` — The method returns a list of atom indices with the correct multiplicity.

### T36. [unit] `has_free_attachment_point`

- File: `src/core/chemistry/_fragment.py`
- Scenario: Checking if an atom has a free attachment point.
- Expected result: True if the atom has a free bond, False otherwise.
- Evidence: `L78–L90` — The method returns True if the atom has at least one free bond available.

### T37. [unit] `FRAGMENT_LIBRARY`

- File: `src/core/chemistry/_fragment_data.py`
- Scenario: Test the presence and correctness of all fragments in FRAGMENT_LIBRARY.
- Expected result: All fragments should be present and correctly defined.
- Evidence: `L7–L202` — FRAGMENT_LIBRARY contains all fragments.

### T38. [integration] `FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS`

- File: `src/core/chemistry/_fragment_data.py`
- Scenario: Test the integration of FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS with other modules.
- Expected result: FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS should be correctly integrated with other modules.
- Evidence: `L7–L270` — FRAGMENT_LIBRARY and FUNCTIONAL_GROUPS are correctly defined.

### T39. [unit] `FUNCTIONAL_GROUPS`

- File: `src/core/chemistry/_fragment_data.py`
- Scenario: Test the presence and correctness of all functional groups in FUNCTIONAL_GROUPS.
- Expected result: All functional groups should be present and correctly defined.
- Evidence: `L205–L270` — FUNCTIONAL_GROUPS contains all functional groups.

### T40. [unit] `create_aminomethyl`

- File: `src/core/chemistry/_functional.py`
- Scenario: Check the creation of an aminomethyl group.
- Expected result: A MoleculeFragment object with the correct attributes.
- Evidence: Нет; требуется ручная проверка.

### T41. [unit] `create_cooh`

- File: `src/core/chemistry/_functional.py`
- Scenario: Check the creation of a carboxylic acid group.
- Expected result: A MoleculeFragment object with the correct attributes.
- Evidence: Нет; требуется ручная проверка.

### T42. [unit] `create_piperidine`

- File: `src/core/chemistry/_functional.py`
- Scenario: Check the creation of a piperidine ring.
- Expected result: A MoleculeFragment object with the correct attributes.
- Evidence: Нет; требуется ручная проверка.

### T43. [unit] `find_and_visualize_molecules`

- File: `src/core/chemistry/_visualize.py`
- Scenario: Test with a simple molecule formula.
- Expected result: Successful parsing, combination generation, assembly, and visualization.
- Evidence: `L13–L236` — Function handles simple molecules correctly.

### T44. [integration] `find_and_visualize_molecules`

- File: `src/core/chemistry/_visualize.py`
- Scenario: Test with a complex molecule formula.
- Expected result: Successful parsing, combination generation, assembly, and visualization.
- Evidence: `L13–L236` — Function handles complex molecules correctly.

### T45. [unit] `find_and_visualize_molecules`

- File: `src/core/chemistry/_visualize.py`
- Scenario: Test with an invalid molecule formula.
- Expected result: Exception raised for invalid input.
- Evidence: `L13–L236` — Function raises exception for invalid input.

### T46. [unit] `ALL_FRAGMENTS`

- File: `src/core/chemistry/fragments.py`
- Scenario: Test that all entries in the `ALL_FRAGMENTS` dictionary are callable and return expected results.
- Expected result: All entries should be callable and return valid molecule fragments.
- Evidence: Нет; требуется ручная проверка.

### T47. [unit] `FRAGMENT_LIBRARY`

- File: `src/core/chemistry/fragments.py`
- Scenario: Test that the `FRAGMENT_LIBRARY` contains the expected fragments and is accessible.
- Expected result: The library should contain all expected fragments and be accessible without errors.
- Evidence: Нет; требуется ручная проверка.

### T48. [unit] `MoleculeFragment`

- File: `src/core/chemistry/fragments.py`
- Scenario: Test the initialization and basic properties of the `MoleculeFragment` class.
- Expected result: The class should initialize correctly and properties should be set as expected.
- Evidence: Нет; требуется ручная проверка.

### T49. [integration] `license presence`

- File: `src/core/domain/__init__.py`
- Scenario: Check for the presence of a LICENSE file in the repository root.
- Expected result: A LICENSE file should be present.
- Evidence: Нет; требуется ручная проверка.

### T50. [unit] `package documentation`

- File: `src/core/domain/__init__.py`
- Scenario: Ensure that the package's docstring is clear and provides a brief description of the package's purpose.
- Expected result: The docstring should accurately describe the package.
- Evidence: Нет; требуется ручная проверка.

### T51. [unit] `package structure`

- File: `src/core/domain/__init__.py`
- Scenario: Verify that the package directory exists and contains the expected subdirectories and files.
- Expected result: The package directory should be correctly structured.
- Evidence: Нет; требуется ручная проверка.

### T52. [unit] `Atom._update_hybridization`

- File: `src/core/domain/atoms.py`
- Scenario: Обновление гибернизации для атома углерода с двойной связью и ароматическим флагом.
- Expected result: Метод должен установить гибернизацию в SP2.
- Evidence: Нет; требуется ручная проверка.

### T53. [unit] `Atom.add_bond`

- File: `src/core/domain/atoms.py`
- Scenario: Добавление связи с превышением допустимой валентности.
- Expected result: Метод должен вернуть False и не изменить состояние атома.
- Evidence: Нет; требуется ручная проверка.

### T54. [unit] `Atom.get_bond_order_to`

- File: `src/core/domain/atoms.py`
- Scenario: Получение порядка связи с несуществующим атомом.
- Expected result: Метод должен вернуть 0.
- Evidence: Нет; требуется ручная проверка.

### T55. [unit] `DatabaseManager`

- File: `src/core/formula_db/__init__.py`
- Scenario: Test the download and verification functionality with a sample database.
- Expected result: The database should be downloaded and verified successfully.
- Evidence: Нет; требуется ручная проверка.

### T56. [unit] `FormulaDatabaseReader`

- File: `src/core/formula_db/__init__.py`
- Scenario: Test the search functionality with a sample database.
- Expected result: The search should return the correct results based on the query.
- Evidence: Нет; требуется ручная проверка.

### T57. [unit] `pack_c_n_o_s_p`

- File: `src/core/formula_db/__init__.py`
- Scenario: Test the encoding functionality with sample data.
- Expected result: The encoded data should match the expected output.
- Evidence: Нет; требуется ручная проверка.

### T58. [unit] `main`

- File: `src/core/formula_db/__main__.py`
- Scenario: Test the `main` function with valid arguments to ensure it correctly calls `build_database` with the expected configuration.
- Expected result: The `build_database` function is called with a `BuildConfig` object containing the correct values.
- Evidence: Нет; требуется ручная проверка.

### T59. [unit] `main`

- File: `src/core/formula_db/__main__.py`
- Scenario: Test the `main` function with an invalid `--output` path to ensure it raises an appropriate error.
- Expected result: An error is raised indicating that the output path is invalid.
- Evidence: Нет; требуется ручная проверка.

### T60. [unit] `main`

- File: `src/core/formula_db/__main__.py`
- Scenario: Test the `main` function with an invalid `--max-mass` value to ensure it raises an appropriate error.
- Expected result: An error is raised indicating that the maximum mass value is invalid.
- Evidence: Нет; требуется ручная проверка.

### T61. [unit] `_enum_valid_cnosp`

- File: `src/core/formula_db/_builder.py`
- Scenario: Test with a small `max_mass_u` to ensure the function returns the correct number of valid formulas.
- Expected result: A list of tuples with the correct number of valid formulas.
- Evidence: Нет; требуется ручная проверка.

### T62. [integration] `build_database`

- File: `src/core/formula_db/_builder.py`
- Scenario: Test the entire build process with a small `max_mass` to verify that the database and manifest files are correctly generated.
- Expected result: Valid `.fdb` and `.manifest.json` files with expected contents.
- Evidence: Нет; требуется ручная проверка.

### T63. [unit] `generate_formulas`

- File: `src/core/formula_db/_builder.py`
- Scenario: Test with a known `max_mass` to ensure the function returns the correct list of formulas.
- Expected result: A list of tuples with the expected formulas.
- Evidence: Нет; требуется ручная проверка.

### T64. [unit] `DatabaseManager._verify_local`

- File: `src/core/formula_db/_manager.py`
- Scenario: Test the _verify_local method with a corrupted local database file.
- Expected result: The method should raise a RuntimeError indicating a SHA-256 mismatch.
- Evidence: Нет; требуется ручная проверка.

### T65. [unit] `DatabaseManager.download`

- File: `src/core/formula_db/_manager.py`
- Scenario: Test the download method with a mock server that simulates a partial download and resumption.
- Expected result: The method should correctly resume the download and complete it successfully.
- Evidence: Нет; требуется ручная проверка.

### T66. [integration] `DatabaseManager.fetch_release_info`

- File: `src/core/formula_db/_manager.py`
- Scenario: Test the fetch_release_info method with a mock server that returns a valid JSON response.
- Expected result: The method should return the JSON dict without raising any exceptions.
- Evidence: Нет; требуется ручная проверка.

### T67. [integration] `FormulaDatabaseReader`

- File: `src/core/formula_db/_reader.py`
- Scenario: Test SHA-256 verification with a tampered manifest.
- Expected result: RuntimeError should be raised for block SHA-256 mismatch.
- Evidence: Нет; требуется ручная проверка.

### T68. [unit] `FormulaDatabaseReader`

- File: `src/core/formula_db/_reader.py`
- Scenario: Test search with a target mass outside the block range.
- Expected result: Search should return an appropriate message indicating no results found.
- Evidence: Нет; требуется ручная проверка.

### T69. [unit] `LRUBlockCache`

- File: `src/core/formula_db/_reader.py`
- Scenario: Test cache size reduction and ensure it does not exceed the new limit.
- Expected result: Cache size should be adjusted without exceeding the new limit.
- Evidence: Нет; требуется ручная проверка.

### T70. [unit] `src/core/io/__init__.py`

- File: `src/core/io/__init__.py`
- Scenario: Check if the package documentation is correctly formatted.
- Expected result: The docstring should be present and correctly formatted.
- Evidence: Нет; требуется ручная проверка.

### T71. [integration] `src/core/io/__init__.py`

- File: `src/core/io/__init__.py`
- Scenario: Verify that the package can be imported without errors.
- Expected result: The import should succeed without raising any exceptions.
- Evidence: Нет; требуется ручная проверка.

### T72. [unit] `src/core/io/__init__.py`

- File: `src/core/io/__init__.py`
- Scenario: Ensure that the package does not contain any syntax errors.
- Expected result: The file should be syntactically correct.
- Evidence: Нет; требуется ручная проверка.

### T73. [unit] `is_available`

- File: `src/core/io/mzml_bridge.py`
- Scenario: Test when pymzml is installed and not installed.
- Expected result: True when installed, False otherwise.
- Evidence: Нет; требуется ручная проверка.

### T74. [unit] `mzml_to_json`

- File: `src/core/io/mzml_bridge.py`
- Scenario: Test with a small, well-defined mzML file.
- Expected result: Correct JSON output with expected data points.
- Evidence: Нет; требуется ручная проверка.

### T75. [integration] `mzml_to_json`

- File: `src/core/io/mzml_bridge.py`
- Scenario: Test with a large mzML file to measure performance.
- Expected result: Execution completes within a reasonable time frame.
- Evidence: Нет; требуется ручная проверка.

### T76. [unit] `average_raw_to_df`

- File: `src/core/io/raw_bridge.py`
- Scenario: Test with a valid ThermoRAW file and verify that the returned DataFrame has the correct columns and data types.
- Expected result: DataFrame with 'mass' and 'intensity' columns and correct data types.
- Evidence: Нет; требуется ручная проверка.

### T77. [integration] `average_raw_to_df`

- File: `src/core/io/raw_bridge.py`
- Scenario: Test with a large ThermoRAW file and verify that the function completes within an acceptable time frame.
- Expected result: Function completes within a specified time limit.
- Evidence: Нет; требуется ручная проверка.

### T78. [unit] `average_raw_to_json`

- File: `src/core/io/raw_bridge.py`
- Scenario: Test with invalid input parameters and verify that the function raises the appropriate error.
- Expected result: Error indicating invalid input parameters.
- Evidence: Нет; требуется ручная проверка.

### T79. [unit] `average_raw_to_df`

- File: `src/core/io/raw_thermo_adapter.py`
- Scenario: Test with a valid RAW file and a retention-time window.
- Expected result: A DataFrame is returned with the correct number of peaks.
- Evidence: `L152–L228` — The function should return a DataFrame with the correct number of peaks.

### T80. [unit] `average_raw_to_json`

- File: `src/core/io/raw_thermo_adapter.py`
- Scenario: Test with a valid RAW file and a retention-time window.
- Expected result: A JSON file is generated with the correct number of peaks.
- Evidence: `L105–L143` — The function should generate a JSON file with the correct number of peaks.

### T81. [unit] `is_available`

- File: `src/core/io/raw_thermo_adapter.py`
- Scenario: Test when the required DLLs are missing.
- Expected result: The function should return False and set an appropriate error message.
- Evidence: `L61–L85` — The function should return False and set an appropriate error message when the required DLLs are missing.

### T82. [unit] `PipelineCache`

- File: `src/core/pipeline/__init__.py`
- Scenario: Test the caching mechanism with various data inputs to ensure it behaves as expected.
- Expected result: The cache should store and retrieve data correctly without data loss or corruption.
- Evidence: Нет; требуется ручная проверка.

### T83. [unit] `PipelineTimings`

- File: `src/core/pipeline/__init__.py`
- Scenario: Test the timing functionality to ensure it accurately measures the execution time of the pipeline.
- Expected result: The timing should be accurate and consistent across multiple runs.
- Evidence: Нет; требуется ручная проверка.

### T84. [integration] `run_pipeline`

- File: `src/core/pipeline/__init__.py`
- Scenario: Run the pipeline with a sample dataset and verify that it completes successfully and produces the expected output.
- Expected result: The pipeline should execute without errors and produce the correct results.
- Evidence: Нет; требуется ручная проверка.

### T85. [unit] `PipelineCache`

- File: `src/core/pipeline/_cache.py`
- Scenario: Проверка корректности кэширования и извлечения объектов.
- Expected result: Возвращаемые объекты должны совпадать с кэшированными.
- Evidence: Нет; требуется ручная проверка.

### T86. [integration] `PipelineCache`

- File: `src/core/pipeline/_cache.py`
- Scenario: Проверка интеграции кэша с другими компонентами пайплайна.
- Expected result: Кэширование должно улучшить производительность без потери данных.
- Evidence: Нет; требуется ручная проверка.

### T87. [unit] `PipelineProgress`

- File: `src/core/pipeline/_cache.py`
- Scenario: Проверка корректности обновления прогресса и колбэка.
- Expected result: Колбэк должен получать правильные значения прогресса.
- Evidence: Нет; требуется ручная проверка.

### T88. [unit] `_autofit_columns`

- File: `src/core/pipeline/_export.py`
- Scenario: Test with a DataFrame larger than 200 rows to ensure column widths are calculated correctly.
- Expected result: Correct column widths for all columns.
- Evidence: Нет; требуется ручная проверка.

### T89. [unit] `_write_json`

- File: `src/core/pipeline/_export.py`
- Scenario: Test with various `metadata` inputs, including edge cases like empty dict and None.
- Expected result: JSON output with correct metadata and data sections.
- Evidence: Нет; требуется ручная проверка.

### T90. [integration] `export_result_table`

- File: `src/core/pipeline/_export.py`
- Scenario: Test exporting a DataFrame to CSV, XLSX, and JSON formats to ensure correct file contents.
- Expected result: Files with correct format and content.
- Evidence: Нет; требуется ручная проверка.

### T91. [unit] `_match_row_by_mass`

- File: `src/core/pipeline/_helpers.py`
- Scenario: Test with an empty DataFrame.
- Expected result: Function should return None.
- Evidence: `L112–L113` — If table is None or table.empty, return None.

### T92. [unit] `_normalize_brutto`

- File: `src/core/pipeline/_helpers.py`
- Scenario: Test with a complex formula string.
- Expected result: Function should return the formula in canonical order.
- Evidence: `L60–L67` — Function parses and sorts elements in the formula.

### T93. [unit] `_ppm_error`

- File: `src/core/pipeline/_helpers.py`
- Scenario: Test with theoretical mass equal to zero.
- Expected result: Function should return float('inf').
- Evidence: `L32–L33` — If theoretical == 0, return float('inf').

### T94. [integration] `PipelineStats`

- File: `src/core/pipeline/_stats.py`
- Scenario: Test the initialization and assignment of all attributes in `PipelineStats`.
- Expected result: All attributes are correctly initialized and assigned without errors.
- Evidence: Нет; требуется ручная проверка.

### T95. [unit] `assign_recall`

- File: `src/core/pipeline/_stats.py`
- Scenario: Test `assign_recall` property with `total_signals` equal to zero.
- Expected result: Return 0.0 without raising an error.
- Evidence: Нет; требуется ручная проверка.

### T96. [unit] `denoise_recall`

- File: `src/core/pipeline/_stats.py`
- Scenario: Test `denoise_recall` property with `total_signals` equal to zero.
- Expected result: Return 0.0 without raising an error.
- Evidence: Нет; требуется ручная проверка.

### T97. [unit] `_run_test_mode`

- File: `src/core/pipeline/_test.py`
- Scenario: Test with a known set of test sets and verify the output.
- Expected result: A list of TestSetResult objects with expected statistics.
- Evidence: Нет; требуется ручная проверка.

### T98. [integration] `_run_test_mode`

- File: `src/core/pipeline/_test.py`
- Scenario: Test with a mock test_sets_root that contains known test sets and verify the output.
- Expected result: A list of TestSetResult objects with expected statistics.
- Evidence: Нет; требуется ручная проверка.

### T99. [integration] `_run_test_mode`

- File: `src/core/pipeline/_test.py`
- Scenario: Test with a mock test_sets_root that does not exist and verify the error handling.
- Expected result: An empty list and an error log message.
- Evidence: Нет; требуется ручная проверка.

### T100. [unit] `_verify_series_against_annotations`

- File: `src/core/pipeline/_test_verify.py`
- Scenario: Test with empty 'sp_result' DataFrame.
- Expected result: Function logs a warning and continues without errors.
- Evidence: Нет; требуется ручная проверка.

### T101. [unit] `_verify_series_against_annotations`

- File: `src/core/pipeline/_test_verify.py`
- Scenario: Test with missing columns in 'sp_result'.
- Expected result: Function logs a warning and continues without errors.
- Evidence: Нет; требуется ручная проверка.

### T102. [unit] `_verify_series_against_annotations`

- File: `src/core/pipeline/_test_verify.py`
- Scenario: Test with 'molecules' DataFrame missing required columns.
- Expected result: Function handles missing columns gracefully and continues without errors.
- Evidence: Нет; требуется ручная проверка.

### T103. [unit] `assign_formulas`

- File: `src/core/spectrum/_assign.py`
- Scenario: Test with an empty mass series and no mass_min/mass_max provided.
- Expected result: Function should handle the empty mass series gracefully and return a Spectrum object with appropriate default values.
- Evidence: Нет; требуется ручная проверка.

### T104. [unit] `assign_formulas`

- File: `src/core/spectrum/_assign.py`
- Scenario: Test with a small dataset and known input parameters.
- Expected result: Function should return a Spectrum object with correct brutto formulas, assignments, and candidate lists.
- Evidence: Нет; требуется ручная проверка.

### T105. [integration] `assign_formulas`

- File: `src/core/spectrum/_assign.py`
- Scenario: Test with a large dataset and measure execution time.
- Expected result: Function should complete within an acceptable time frame and return correct results.
- Evidence: Нет; требуется ручная проверка.

### T106. [unit] `build_result_table`

- File: `src/core/spectrum/_build.py`
- Scenario: Test with empty `df_dmet` and `df_dacet`.
- Expected result: A DataFrame with all counts set to 0 and no missing values.
- Evidence: `L46–L54` — Function handles empty input correctly.

### T107. [unit] `build_result_table`

- File: `src/core/spectrum/_build.py`
- Scenario: Test with missing columns in `df_dmet` or `df_dacet`.
- Expected result: Function raises a KeyError or similar exception.
- Evidence: `L55–L62` — Function checks for required columns.

### T108. [unit] `build_result_table`

- File: `src/core/spectrum/_build.py`
- Scenario: Test with missing columns in `src.table`.
- Expected result: Function raises a KeyError or similar exception.
- Evidence: `L38–L41` — Function checks for required columns.

### T109. [integration] `_measure_m1_ratio`

- File: `src/core/spectrum/_chem.py`
- Scenario: Test with a synthetic spectrum containing known M+1 peaks.
- Expected result: Correct M+1/M ratio measurement.
- Evidence: Нет; требуется ручная проверка.

### T110. [unit] `_nom_distance`

- File: `src/core/spectrum/_chem.py`
- Scenario: Test with various HC and OC ratios, including edge cases.
- Expected result: Correct distance calculation.
- Evidence: Нет; требуется ручная проверка.

### T111. [unit] `exact_mass_from_counts`

- File: `src/core/spectrum/_chem.py`
- Scenario: Test with various element counts, including edge cases like zero or negative counts.
- Expected result: Correct monoisotopic mass calculation.
- Evidence: Нет; требуется ручная проверка.

### T112. [unit] `FormulaSearchConfig`

- File: `src/core/spectrum/_constants.py`
- Scenario: Test the initialization of 'FormulaSearchConfig' with a custom 'ranges' dictionary.
- Expected result: The 'ranges' attribute should be set to the custom dictionary provided.
- Evidence: `L71–L73` — The 'ranges' attribute is initialized with the provided dictionary.

### T113. [unit] `FormulaSearchConfig`

- File: `src/core/spectrum/_constants.py`
- Scenario: Test the initialization of 'FormulaSearchConfig' with a missing element in 'ranges'.
- Expected result: A ValueError should be raised with a message indicating the missing element.
- Evidence: `L80–L86` — The '__post_init__' method raises a ValueError if an element in 'elements' lacks a range in 'ranges'.

### T114. [unit] `FormulaSearchConfig`

- File: `src/core/spectrum/_constants.py`
- Scenario: Test the initialization of 'FormulaSearchConfig' with default 'ranges'.
- Expected result: The 'ranges' attribute should be set to the default values from '_FS_RANGES'.
- Evidence: `L80–L84` — The '__post_init__' method sets 'ranges' to a copy of '_FS_RANGES' if 'ranges' is None.

### T115. [unit] `_generate_cached`

- File: `src/core/spectrum/_generate.py`
- Scenario: Test with a small mass range and known input parameters.
- Expected result: Verify that the function returns the expected list of formulas.
- Evidence: Нет; требуется ручная проверка.

### T116. [unit] `_ion_shift`

- File: `src/core/spectrum/_generate.py`
- Scenario: Test with different `ion_mode` values, including edge cases.
- Expected result: Verify that the function returns the correct mass shift for each `ion_mode`.
- Evidence: Нет; требуется ручная проверка.

### T117. [unit] `_neutral_to_ion_mass`

- File: `src/core/spectrum/_generate.py`
- Scenario: Test with different `ion_mode` values, including edge cases.
- Expected result: Verify that the function returns the correct m/z value for each `ion_mode`.
- Evidence: Нет; требуется ручная проверка.

### T118. [unit] `load_spectrum`

- File: `src/core/spectrum/_load.py`
- Scenario: Загрузка файла CSV с корректными данными.
- Expected result: Объект Spectrum с корректными данными.
- Evidence: Нет; требуется ручная проверка.

### T119. [unit] `load_spectrum`

- File: `src/core/spectrum/_load.py`
- Scenario: Загрузка файла JSON с некорректными колонками.
- Expected result: Исключение KeyError.
- Evidence: Нет; требуется ручная проверка.

### T120. [integration] `load_spectrum`

- File: `src/core/spectrum/_load.py`
- Scenario: Загрузка файла XLSX с большим количеством данных.
- Expected result: Объект Spectrum с отфильтрованными данными.
- Evidence: Нет; требуется ручная проверка.

### T121. [unit] `visualize_series`

- File: `src/core/spectrum/_visualize.py`
- Scenario: Проверка визуализации с отсутствующими пиками.
- Expected result: График с отображением пропущенных пиков.
- Evidence: `L62–L71` — Функция должна возвращать None и выводить сообщение, если отсутствуют пропущенные пики.

### T122. [unit] `visualize_series`

- File: `src/core/spectrum/_visualize.py`
- Scenario: Проверка визуализации с большим количеством рядов.
- Expected result: График с отображением всех рядов.
- Evidence: `L66–L67` — Функция должна ограничивать количество отображаемых рядов до max_rows.

### T123. [integration] `visualize_series`

- File: `src/core/spectrum/_visualize.py`
- Scenario: Проверка сохранения графика в файл.
- Expected result: Файл с сохраненным графиком.
- Evidence: `L171–L173` — Функция должна сохранять график в указанный путь.

### T124. [unit] `aromaticity_index`

- File: `src/core/statistics.py`
- Scenario: Test with different combinations of atom counts to ensure the function handles all cases, including zero denominator.
- Expected result: Verify that the function returns the correct aromaticity index or `None` when appropriate.
- Evidence: Нет; требуется ручная проверка.

### T125. [unit] `compute_distribution_metrics`

- File: `src/core/statistics.py`
- Scenario: Test with a DataFrame containing various formulas, including edge cases like zero carbon atoms.
- Expected result: Verify that the function correctly computes metrics and skips invalid formulas.
- Evidence: Нет; требуется ручная проверка.

### T126. [integration] `create_histograms_plot`

- File: `src/core/statistics.py`
- Scenario: Test with a DataFrame containing valid formulas and verify the generated histogram plot.
- Expected result: Verify that the plot is generated correctly with the expected number of histograms and labels.
- Evidence: Нет; требуется ручная проверка.

### T127. [unit] `PipelineTimings`

- File: `src/core/timer.py`
- Scenario: Test the `as_dict` method to ensure it returns the correct dictionary format.
- Expected result: Dictionary should match the expected format with correct values.
- Evidence: `L44–L52` — Returns dictionary with correct keys and values.

### T128. [unit] `PipelineTimings`

- File: `src/core/timer.py`
- Scenario: Test the `summary` method to ensure it returns a formatted string with correct values.
- Expected result: String should match the expected format with correct values.
- Evidence: `L54–L59` — Returns formatted string with correct values.

### T129. [unit] `StageTimer`

- File: `src/core/timer.py`
- Scenario: Test the `__enter__` and `__exit__` methods to ensure they correctly measure elapsed time.
- Expected result: Elapsed time should be a positive number.
- Evidence: `L25–L31` — Measures elapsed time accurately.

### T130. [unit] `license compliance`

- File: `src/sim/__init__.py`
- Scenario: Verify that the license note in the file is compliant with the project's licensing requirements.
- Expected result: The license note should match the project's licensing requirements.
- Evidence: Нет; требуется ручная проверка.

### T131. [unit] `is_chno_only`

- File: `src/sim/process_pubchem_candidates.py`
- Scenario: Test with a malformed formula.
- Expected result: The function should return False without raising an error.
- Evidence: Нет; требуется ручная проверка.

### T132. [unit] `parse_formula`

- File: `src/sim/process_pubchem_candidates.py`
- Scenario: Test with a formula that has an unparsed trailing segment.
- Expected result: The function should return an empty dictionary without raising an error.
- Evidence: Нет; требуется ручная проверка.

### T133. [integration] `split_into_sets`

- File: `src/sim/process_pubchem_candidates.py`
- Scenario: Test with a large dataset to verify mass distribution across subsets.
- Expected result: The mass distribution across subsets should be balanced.
- Evidence: Нет; требуется ручная проверка.

### T134. [unit] `StructureDialog`

- File: `src/structures/__init__.py`
- Scenario: Test the creation and display of a structure dialog.
- Expected result: Dialog is displayed with the correct structure.
- Evidence: Нет; требуется ручная проверка.

### T135. [integration] `StructureViewerTab`

- File: `src/structures/__init__.py`
- Scenario: Test the creation and display of a structure viewer tab.
- Expected result: Tab is displayed with the correct structure.
- Evidence: Нет; требуется ручная проверка.

### T136. [unit] `save_mol`

- File: `src/structures/__init__.py`
- Scenario: Test saving a molecule to a file.
- Expected result: File is created with the correct molecular data.
- Evidence: Нет; требуется ручная проверка.

### T137. [unit] `fragment_to_rdkit`

- File: `src/structures/rdkit_utils.py`
- Scenario: Test conversion of a simple molecule fragment.
- Expected result: A valid RDKit molecule with 2D coordinates.
- Evidence: Нет; требуется ручная проверка.

### T138. [unit] `mol_to_pil`

- File: `src/structures/rdkit_utils.py`
- Scenario: Test rendering of a valid RDKit molecule.
- Expected result: A PIL image object.
- Evidence: Нет; требуется ручная проверка.

### T139. [integration] `save_png`

- File: `src/structures/rdkit_utils.py`
- Scenario: Test saving a molecule as a PNG file.
- Expected result: A PNG file with the correct molecule depiction.
- Evidence: Нет; требуется ручная проверка.

### T140. [integration] `StructureDialog`

- File: `src/structures/widgets.py`
- Scenario: Test the entire dialog for displaying a structure.
- Expected result: The dialog displays all the expected information and buttons.
- Evidence: `L38–L101` — The dialog initializes with the correct parameters and builds the UI elements.

### T141. [unit] `_save_mol`

- File: `src/structures/widgets.py`
- Scenario: Test saving a molecule in .mol format.
- Expected result: A .mol file is saved with the correct content.
- Evidence: `L102–L118` — The method checks if RDKit is available and the molecule is not None before saving.

### T142. [unit] `_save_png`

- File: `src/structures/widgets.py`
- Scenario: Test saving a molecule in .png format.
- Expected result: A .png file is saved with the correct content.
- Evidence: `L121–L138` — The method checks if RDKit is available and the molecule is not None before saving.

### T143. [unit] `load_spectrum_csv`

- File: `src/testing/artifact_export.py`
- Scenario: CSV файл с неправильными именами колонок
- Expected result: ValueError
- Evidence: Нет; требуется ручная проверка.

### T144. [unit] `plot_histogram`

- File: `src/testing/artifact_export.py`
- Scenario: Построение гистограммы с пустой колонкой
- Expected result: Ничего не сохраняется в файл
- Evidence: Нет; требуется ручная проверка.

### T145. [integration] `plot_three_spectra`

- File: `src/testing/artifact_export.py`
- Scenario: Построение графика с пустыми CSV файлами
- Expected result: Пустой график сохраняется в файл
- Evidence: Нет; требуется ручная проверка.

### T146. [unit] `CompoundExportResult`

- File: `src/testing/report_models.py`
- Scenario: Test initialization with default values.
- Expected result: All fields are initialized correctly.
- Evidence: Нет; требуется ручная проверка.

### T147. [unit] `SetSmokeResult`

- File: `src/testing/report_models.py`
- Scenario: Test initialization with default values.
- Expected result: All fields are initialized correctly.
- Evidence: Нет; требуется ручная проверка.

### T148. [unit] `SmokeSuiteResult`

- File: `src/testing/report_models.py`
- Scenario: Test initialization with default values.
- Expected result: All fields are initialized correctly.
- Evidence: Нет; требуется ручная проверка.

### T149. [unit] `_fragment_to_rdkit`

- File: `src/testing/structure_export.py`
- Scenario: Конвертация фрагмента без RDKit.
- Expected result: Вернуть None.
- Evidence: `L150–L151` — Возвращает None, если RDKit недоступен.

### T150. [unit] `_save_png`

- File: `src/testing/structure_export.py`
- Scenario: Сохранение PNG без RDKit.
- Expected result: Не сохраняет файл.
- Evidence: `L190–L191` — Не выполняет сохранение, если RDKit недоступен.

### T151. [unit] `export_structures_for_compound`

- File: `src/testing/structure_export.py`
- Scenario: Обработка соединения с таймаутом.
- Expected result: Вернуть пустой список.
- Evidence: `L91–L95` — Возвращает пустой список при таймауте.

### T152. [unit] `BuildMixin._build_ui`

- File: `src/ui/_build.py`
- Scenario: Test the creation of UI components and their layout.
- Expected result: All UI components should be created and packed correctly.
- Evidence: `L35–L97` — UI components are created and packed.

### T153. [integration] `BuildMixin._build_ui`

- File: `src/ui/_build.py`
- Scenario: Test the integration of 'StructureViewerTab' if it is available.
- Expected result: If 'StructureViewerTab' is available, it should be initialized and added to the notebook.
- Evidence: `L67–L71` — StructureViewerTab is initialized and added to the notebook.

### T154. [unit] `BuildMixin._build_ui`

- File: `src/ui/_build.py`
- Scenario: Test the creation of status label and progress bar.
- Expected result: Status label and progress bar should be created and packed at the bottom.
- Evidence: `L85–L97` — Status label and progress bar are created and packed.

### T155. [unit] `Error handling`

- File: `src/ui/_deps.py`
- Scenario: Trigger an import exception and verify error message.
- Expected result: Specific error message is logged.
- Evidence: Нет; требуется ручная проверка.

### T156. [unit] `Fallback imports`

- File: `src/ui/_deps.py`
- Scenario: Simulate import failure and verify fallback behavior.
- Expected result: Fallback values are correctly assigned.
- Evidence: Нет; требуется ручная проверка.

### T157. [integration] `Import performance`

- File: `src/ui/_deps.py`
- Scenario: Measure import times with and without exceptions.
- Expected result: No significant performance degradation with exceptions.
- Evidence: Нет; требуется ручная проверка.

### T158. [unit] `_on_close`

- File: `src/ui/_log.py`
- Scenario: Simulate a graceful shutdown and verify that all resources are properly released.
- Expected result: Application exits cleanly without resource leaks.
- Evidence: Нет; требуется ручная проверка.

### T159. [unit] `_poll_log_queue`

- File: `src/ui/_log.py`
- Scenario: Simulate a high volume of log messages and measure CPU usage.
- Expected result: CPU usage remains within acceptable limits.
- Evidence: Нет; требуется ручная проверка.

### T160. [unit] `_save_log`

- File: `src/ui/_log.py`
- Scenario: Test file path validation by attempting to save a log with a malicious file path.
- Expected result: File path validation prevents directory traversal attacks.
- Evidence: Нет; требуется ручная проверка.

### T161. [integration] `_export_pdf`

- File: `src/ui/_presets.py`
- Scenario: Экспорт данных в PDF при наличии результатов анализа.
- Expected result: PDF-файл создан и содержит корректные данные.
- Evidence: Нет; требуется ручная проверка.

### T162. [unit] `_import_csv`

- File: `src/ui/_presets.py`
- Scenario: Загрузка корректного CSV файла.
- Expected result: Файл успешно загружен и данные отображены в таблице.
- Evidence: Нет; требуется ручная проверка.

### T163. [unit] `_import_folder`

- File: `src/ui/_presets.py`
- Scenario: Импорт папки с корректными файлами.
- Expected result: Файлы успешно распознаны и соответствующие поля заполнены.
- Evidence: Нет; требуется ручная проверка.

### T164. [unit] `_apply_formula_change`

- File: `src/ui/_results.py`
- Scenario: Test with a valid and an invalid formula change.
- Expected result: The formula should be updated in the DataFrame and displayed in the GUI for a valid change, and no changes should be made for an invalid change.
- Evidence: Нет; требуется ручная проверка.

### T165. [unit] `_fill_result_table`

- File: `src/ui/_results.py`
- Scenario: Test with a DataFrame containing missing columns.
- Expected result: The missing columns should be filled with default values, and a warning should be logged.
- Evidence: Нет; требуется ручная проверка.

### T166. [integration] `_on_result_row_select`

- File: `src/ui/_results.py`
- Scenario: Test with a valid and an invalid row selection.
- Expected result: The structure preview should be displayed for a valid selection, and nothing should happen for an invalid selection.
- Evidence: Нет; требуется ручная проверка.

### T167. [unit] `_load_structure_preview`

- File: `src/ui/_structures.py`
- Scenario: Проверка обработки исключений при отсутствии структуры для формулы.
- Expected result: Метод должен корректно обрабатывать исключения и отображать сообщение об ошибке.
- Evidence: Нет; требуется ручная проверка.

### T168. [unit] `_preload_structures_worker`

- File: `src/ui/_structures.py`
- Scenario: Проверка корректности кэширования структур при предзагрузке.
- Expected result: Структуры должны быть корректно кэшированы без повторных вызовов find_and_visualize_molecules для уже загруженных формул.
- Evidence: Нет; требуется ручная проверка.

### T169. [integration] `_refresh_structures_tab`

- File: `src/ui/_structures.py`
- Scenario: Проверка обновления выпадающего списка в вкладке Структуры.
- Expected result: Выпадающий список должен быть обновлен корректно, отображая актуальные данные.
- Evidence: Нет; требуется ручная проверка.

### T170. [unit] `_build_batch_tab`

- File: `src/ui/_tabs.py`
- Scenario: Test the construction of the batch tab to ensure all buttons and controls are present.
- Expected result: Buttons for selecting a folder, running batch processing, and exporting a summary, along with a treeview for displaying batch results.
- Evidence: `L166–L195` — The method initializes the batch tab with buttons and a treeview.

### T171. [unit] `_build_histograms_tab`

- File: `src/ui/_tabs.py`
- Scenario: Ensure that the histograms tab is constructed with the correct buttons and canvas frame.
- Expected result: Buttons for plotting and saving histograms, and a canvas frame for displaying plots.
- Evidence: `L146–L163` — The method sets up the histograms tab with buttons and a canvas frame.

### T172. [unit] `_build_result_tab`

- File: `src/ui/_tabs.py`
- Scenario: Verify that the result tab is built correctly with all necessary components.
- Expected result: All buttons and the treeview are present and correctly configured.
- Evidence: `L71–L126` — The method initializes the result tab with buttons and a treeview.

### T173. [unit] `clear_canvas`

- File: `src/ui/plots.py`
- Scenario: Clear a frame with multiple widgets and open figures.
- Expected result: All child widgets are destroyed and all figures are closed.
- Evidence: `L36–L52` — The function iterates over all child widgets and destroys them, then closes all Matplotlib figures.

### T174. [unit] `embed_figure`

- File: `src/ui/plots.py`
- Scenario: Embed a simple figure with toolbar enabled.
- Expected result: The figure is embedded with a toolbar below it.
- Evidence: `L9–L34` — The function initializes a `FigureCanvasTkAgg` and optionally a `NavigationToolbar2Tk`.

### T175. [unit] `embed_figure`

- File: `src/ui/plots.py`
- Scenario: Embed a simple figure with toolbar disabled.
- Expected result: The figure is embedded without a toolbar.
- Evidence: `L9–L34` — The function initializes a `FigureCanvasTkAgg` and optionally a `NavigationToolbar2Tk` based on the `toolbar` parameter.

### T176. [unit] `_mpl_style`

- File: `src/ui/theme.py`
- Scenario: Test the `_mpl_style` function to ensure that it correctly updates the Matplotlib parameters with the expected values.
- Expected result: All Matplotlib parameters should be updated with the correct values.
- Evidence: Нет; требуется ручная проверка.

### T177. [unit] `_style`

- File: `src/ui/theme.py`
- Scenario: Test the `_style` function to ensure that it correctly configures the ttk widgets with the expected styles.
- Expected result: All ttk widgets should be configured with the correct styles.
- Evidence: Нет; требуется ручная проверка.

### T178. [integration] `theme.py`

- File: `src/ui/theme.py`
- Scenario: Test the integration of the `_style` and `_mpl_style` functions to ensure that they work together correctly in a complete application.
- Expected result: The application should display the UI with the correct styles and Matplotlib plots with the correct appearance.
- Evidence: Нет; требуется ручная проверка.

### T179. [unit] `project_root`

- File: `tests/conftest.py`
- Scenario: Verify that the `project_root` fixture returns the correct path to the repository root.
- Expected result: The fixture should return the correct absolute path to the repository root.
- Evidence: Нет; требуется ручная проверка.

### T180. [integration] `project_root`

- File: `tests/conftest.py`
- Scenario: Verify that the `project_root` fixture returns the correct path even if the repository root changes during the session.
- Expected result: The fixture should return the correct absolute path to the repository root, even if the root changes during the session.
- Evidence: Нет; требуется ручная проверка.

### T181. [unit] `test_sets_root`

- File: `tests/conftest.py`
- Scenario: Verify that the `test_sets_root` fixture returns the correct path to the `data/test_sets/` directory.
- Expected result: The fixture should return the correct absolute path to the `data/test_sets/` directory.
- Evidence: Нет; требуется ручная проверка.

### T182. [unit] `test_smoke_all_sets`

- File: `tests/integration/test_app_smoke.py`
- Scenario: Test with a different number of test sets to ensure the test is flexible.
- Expected result: The test should pass without asserting the exact number of test sets.
- Evidence: Нет; требуется ручная проверка.

### T183. [integration] `test_smoke_all_sets`

- File: `tests/integration/test_app_smoke.py`
- Scenario: Test with an empty result table CSV file to ensure the test handles this case correctly.
- Expected result: The test should fail with an appropriate error message.
- Evidence: Нет; требуется ручная проверка.

### T184. [integration] `test_smoke_all_sets`

- File: `tests/integration/test_app_smoke.py`
- Scenario: Test with a result table CSV file containing no connections to ensure the test handles this case correctly.
- Expected result: The test should fail with an appropriate error message.
- Evidence: Нет; требуется ручная проверка.

### T185. [integration] `TestRawIntegration`

- File: `tests/integration/test_raw_integration.py`
- Scenario: Test the end-to-end functionality of averaging a .raw file and converting it to a DataFrame.
- Expected result: The DataFrame should contain the expected averaged data.
- Evidence: Нет; требуется ручная проверка.

### T186. [unit] `test_average_raw_to_df_delegates`

- File: `tests/integration/test_raw_integration.py`
- Scenario: Verify that average_raw_to_df calls average_raw_to_json with the correct parameters.
- Expected result: average_raw_to_json should be called with the expected arguments.
- Evidence: Нет; требуется ручная проверка.

### T187. [unit] `test_average_raw_to_json_smoke`

- File: `tests/integration/test_raw_integration.py`
- Scenario: Test with a valid .raw file to ensure no exceptions are raised.
- Expected result: No exceptions should be raised.
- Evidence: Нет; требуется ручная проверка.

### T188. [unit] `_load_spectrum_csv`

- File: `tests/unit/test_annotations_consistency.py`
- Scenario: Загрузка CSV-файла с некорректными данными.
- Expected result: Исключение ValueError.
- Evidence: `L15–L19` — Функция _load_spectrum_csv должна выбросить исключение ValueError при некорректных данных.

### T189. [unit] `_to_float`

- File: `tests/unit/test_annotations_consistency.py`
- Scenario: Преобразование None и пустой строки в float.
- Expected result: Возврат значения 0.0.
- Evidence: `L21–L23` — Функция _to_float должна возвращать 0.0 для None и пустой строки.

### T190. [integration] `test_annotations_have_matching_peaks_in_spectra_and_ppm_limits`

- File: `tests/unit/test_annotations_consistency.py`
- Scenario: Аннотации без соответствующих пиков в спектрах.
- Expected result: Сбой теста с сообщением об отсутствии соответствующего пика.
- Evidence: `L90–L94` — Тест должен упасть, если не найден соответствующий пик в спектре.

### T191. [unit] `test_call_sites_match_signature`

- File: `tests/unit/test_app_fallback.py`
- Scenario: Проверка совместимости аргументов вызовов embed_figure с сигнатурой.
- Expected result: Все вызовы должны использовать совместимые аргументы.
- Evidence: Нет; требуется ручная проверка.

### T192. [unit] `test_fallback_signature_matches_real`

- File: `tests/unit/test_app_fallback.py`
- Scenario: Проверка совпадения сигнатуры fallback функции с реальной.
- Expected result: Сигнатуры должны совпадать.
- Evidence: Нет; требуется ручная проверка.

### T193. [unit] `test_real_signature_is_correct`

- File: `tests/unit/test_app_fallback.py`
- Scenario: Проверка корректности сигнатуры реальной функции embed_figure.
- Expected result: Сигнатура должна соответствовать ожидаемым параметрам.
- Evidence: Нет; требуется ручная проверка.

### T194. [unit] `brutto_within_dict`

- File: `tests/unit/test_assign_formulas.py`
- Scenario: Test validation of chemical formulas against a dictionary.
- Expected result: Correct validation of formulas against a dictionary of element ranges.
- Evidence: `L63–L69` — The function `brutto_within_dict` correctly validates formulas against a dictionary of element ranges.

### T195. [unit] `normalize_brutto`

- File: `tests/unit/test_assign_formulas.py`
- Scenario: Test normalization of chemical formulas.
- Expected result: Correct normalization of formulas with multiple elements and numbers.
- Evidence: `L31–L60` — The function `normalize_brutto` correctly normalizes formulas with multiple elements and numbers.

### T196. [unit] `parse_formula`

- File: `tests/unit/test_assign_formulas.py`
- Scenario: Test parsing of simple chemical formulas.
- Expected result: Correct parsing of formulas with single elements and numbers.
- Evidence: `L23–L28` — The function `parse_formula` correctly parses formulas with single elements and numbers.

### T197. [unit] `Atom`

- File: `tests/unit/test_atoms.py`
- Scenario: Creating an Atom with a formal charge that exceeds valence.
- Expected result: Raises ValueError.
- Evidence: `L104–L106` — Test for unsupported element raises ValueError.

### T198. [unit] `Atom`

- File: `tests/unit/test_atoms.py`
- Scenario: Adding a bond to an Atom that exceeds its valence.
- Expected result: Returns False.
- Evidence: `L120–L124` — Test for exceeding valence returns False.

### T199. [unit] `Atom`

- File: `tests/unit/test_atoms.py`
- Scenario: Getting bond order to a non-existent atom.
- Expected result: Returns 0.
- Evidence: `L157–L159` — Test for getting bond order to non-existent returns 0.

### T200. [unit] `build_batch_summary`

- File: `tests/unit/test_batch.py`
- Scenario: Handling of multiple samples with varying data
- Expected result: Correct batch summary DataFrame
- Evidence: `L89–L96` — Test for multiple samples.

### T201. [unit] `compute_sample_summary`

- File: `tests/unit/test_batch.py`
- Scenario: Handling of an empty DataFrame
- Expected result: Correct summary with zero counts and averages
- Evidence: `L80–L86` — Test for empty DataFrame input.

### T202. [unit] `detect_sample_triples`

- File: `tests/unit/test_batch.py`
- Scenario: Handling of files with different naming conventions
- Expected result: Correct detection of sample triples
- Evidence: `L19–L38` — Test for standard naming conventions.

### T203. [unit] `test_carboxyl_and_hydroxyl_counts_in_range_if_present`

- File: `tests/unit/test_chemical_validity.py`
- Scenario: Test with 'carboxyl_count' and 'hydroxyl_count' as non-integer values.
- Expected result: Test should fail with a ValueError.
- Evidence: Нет; требуется ручная проверка.

### T204. [unit] `test_carboxyl_and_hydroxyl_counts_in_range_if_present`

- File: `tests/unit/test_chemical_validity.py`
- Scenario: Test with 'carboxyl_count' and 'hydroxyl_count' as missing values.
- Expected result: Test should pass without errors.
- Evidence: Нет; требуется ручная проверка.

### T205. [unit] `test_carboxyl_and_hydroxyl_counts_in_range_if_present`

- File: `tests/unit/test_chemical_validity.py`
- Scenario: Test with 'carboxyl_count' and 'hydroxyl_count' as values outside the range [0, 10].
- Expected result: Test should fail with an assertion error.
- Evidence: Нет; требуется ручная проверка.

### T206. [unit] `test_cli_missing_file_exit_1`

- File: `tests/unit/test_cli.py`
- Scenario: Verify the error message and exit code for missing files.
- Expected result: The test should assert the specific error message and exit code.
- Evidence: Нет; требуется ручная проверка.

### T207. [unit] `test_cli_stdout`

- File: `tests/unit/test_cli.py`
- Scenario: Capture and validate the full output of the CLI.
- Expected result: The test should capture the full output and assert its correctness.
- Evidence: Нет; требуется ручная проверка.

### T208. [unit] `test_cli_writes_output_file`

- File: `tests/unit/test_cli.py`
- Scenario: Thoroughly validate the content of the output file.
- Expected result: The test should add more assertions to validate the content of the output file.
- Evidence: Нет; требуется ручная проверка.

### T209. [unit] `denoise`

- File: `tests/unit/test_denoise.py`
- Scenario: Test denoising with different noise levels.
- Expected result: Denoised output should have reduced noise levels.
- Evidence: `L21–L63` — The test checks if the denoised output has reduced noise levels.

### T210. [unit] `denoise`

- File: `tests/unit/test_denoise.py`
- Scenario: Test denoising with different signal characteristics.
- Expected result: Denoised output should preserve signal characteristics.
- Evidence: `L21–L63` — The test checks if the denoised output preserves signal characteristics.

### T211. [unit] `denoise`

- File: `tests/unit/test_denoise.py`
- Scenario: Test denoising performance with large datasets.
- Expected result: Denoising should complete within a specified time frame.
- Evidence: `L21–L63` — The test does not currently measure performance.

### T212. [unit] `test_export_csv`

- File: `tests/unit/test_export.py`
- Scenario: Test CSV export with default separator.
- Expected result: The CSV file should be correctly written with a comma as the default separator.
- Evidence: Нет; требуется ручная проверка.

### T213. [unit] `test_export_json_with_metadata`

- File: `tests/unit/test_export.py`
- Scenario: Test JSON export with invalid metadata.
- Expected result: The function should raise an exception or handle the invalid metadata gracefully.
- Evidence: Нет; требуется ручная проверка.

### T214. [unit] `test_export_xlsx`

- File: `tests/unit/test_export.py`
- Scenario: Test XLSX export with an empty DataFrame.
- Expected result: The XLSX file should be correctly written with no data rows.
- Evidence: Нет; требуется ручная проверка.

### T215. [unit] `test_assemble_all_combinations`

- File: `tests/unit/test_fragment_combinations.py`
- Scenario: Test with combinations that include errors.
- Expected result: Correct handling of errors and successful assembly of valid combinations.
- Evidence: Нет; требуется ручная проверка.

### T216. [unit] `test_assemble_molecule_from_combination`

- File: `tests/unit/test_fragment_combinations.py`
- Scenario: Test assembly with multiple functional groups.
- Expected result: Successful assembly with correct atom count and formula.
- Evidence: Нет; требуется ручная проверка.

### T217. [unit] `test_find_fragment_combinations`

- File: `tests/unit/test_fragment_combinations.py`
- Scenario: Test with varying numbers of COOH and OH groups.
- Expected result: Correct combinations returned based on functional group constraints.
- Evidence: Нет; требуется ручная проверка.

### T218. [unit] `test_cached_generation_is_consistent`

- File: `tests/unit/test_generate_cache.py`
- Scenario: Verify the correctness of generated formulas.
- Expected result: All generated formulas should be valid and meet the specified criteria.
- Evidence: Нет; требуется ручная проверка.

### T219. [unit] `test_generate_candidate_formulas`

- File: `tests/unit/test_generate_cache.py`
- Scenario: Test the behavior of the `_generate_candidate_formulas` function with different input parameters.
- Expected result: The function should return a list of tuples with the correct structure and content.
- Evidence: Нет; требуется ручная проверка.

### T220. [unit] `test_wrapper_returns_list_of_tuples`

- File: `tests/unit/test_generate_cache.py`
- Scenario: Validate the content of the generated tuples.
- Expected result: Each tuple should contain valid and expected data.
- Evidence: Нет; требуется ручная проверка.

### T221. [unit] `_beynon_m1_ratio`

- File: `tests/unit/test_isotope_filter.py`
- Scenario: Negative element counts
- Expected result: ValueError or similar exception
- Evidence: `L12–L17` — Test cases should include negative element counts.

### T222. [unit] `_beynon_m1_ratio`

- File: `tests/unit/test_isotope_filter.py`
- Scenario: Non-integer element counts
- Expected result: ValueError or similar exception
- Evidence: `L12–L17` — Test cases should include non-integer element counts.

### T223. [unit] `_compute_penalty`

- File: `tests/unit/test_isotope_filter.py`
- Scenario: Zero theoretical M+1/M ratio
- Expected result: Zero penalty
- Evidence: `L61–L63` — Test cases should include scenarios with zero theoretical M+1/M ratio.

### T224. [unit] `_nom_distance`

- File: `tests/unit/test_nom_prioritize.py`
- Scenario: Test NOM distance with various H/C and O/C ratios.
- Expected result: NOM distance should be calculated correctly for different ratios.
- Evidence: `L17–L22` — assert dist_lignin < dist_aromatics

### T225. [integration] `assign_formulas`

- File: `tests/unit/test_nom_prioritize.py`
- Scenario: Test formula assignment with different configurations.
- Expected result: Formulas should be assigned correctly based on the configuration.
- Evidence: `L32–L43` — assign_formulas(src, rel_error_ppm=0.5, mass_min=0, mass_max=1000, search_config=cfg, ion_mode="[M-H]-", brutto_generation_mode="nom_like", nom_weight=1.0)

### T226. [unit] `test_nom_prioritize_on_set_01`

- File: `tests/unit/test_nom_prioritize.py`
- Scenario: Check the correctness of assigned formulas.
- Expected result: All assigned formulas should match expected values.
- Evidence: `L44–L45` — assert n_assigned > 0

### T227. [unit] `test_match_row_by_mass`

- File: `tests/unit/test_pipeline.py`
- Scenario: Test the behavior when the observed mass is exactly equal to the theoretical mass with a high ppm tolerance.
- Expected result: The function should return the row with the exact mass match.
- Evidence: `L171–L178` — Exact mass → closest row returned.

### T228. [unit] `test_match_row_by_mass`

- File: `tests/unit/test_pipeline.py`
- Scenario: Test the behavior when the observed mass is within the ppm tolerance but not exactly equal to any mass in the table.
- Expected result: The function should return the row with the closest mass match.
- Evidence: `L179–L186` — Mass within tolerance → closest row returned.

### T229. [unit] `test_match_row_by_mass`

- File: `tests/unit/test_pipeline.py`
- Scenario: Test the behavior when the observed mass is outside the ppm tolerance of all masses in the table.
- Expected result: The function should return None.
- Evidence: `L187–L193` — Mass outside tolerance → None.

### T230. [unit] `test_is_available_returns_bool`

- File: `tests/unit/test_raw_bridge.py`
- Scenario: Test that `is_available` returns a boolean value when called with different configurations.
- Expected result: The function should always return a boolean value.
- Evidence: Нет; требуется ручная проверка.

### T231. [unit] `test_returns_dataframe_with_correct_columns`

- File: `tests/unit/test_raw_bridge.py`
- Scenario: Test that `average_raw_to_df` returns a DataFrame with the correct columns ('mass', 'intensity') when called with a valid JSON file.
- Expected result: The DataFrame should have the columns 'mass' and 'intensity' with the correct data types and values.
- Evidence: Нет; требуется ручная проверка.

### T232. [unit] `test_value_error_when_rt_invalid`

- File: `tests/unit/test_raw_bridge.py`
- Scenario: Test that `average_raw_to_json` raises a `ValueError` when `rt_min` is greater than `rt_max`.
- Expected result: The function should raise a `ValueError` with a message containing 'rt_min'.
- Evidence: Нет; требуется ручная проверка.

### T233. [unit] `test_benzene_conversion`

- File: `tests/unit/test_rdkit_bridge.py`
- Scenario: Test benzene conversion with different configurations.
- Expected result: Ensure the benzene molecule is correctly converted with varying atom and bond configurations.
- Evidence: Нет; требуется ручная проверка.

### T234. [unit] `test_visualize_connection_sequence`

- File: `tests/unit/test_rdkit_bridge.py`
- Scenario: Test connection sequence visualization with multiple fragments.
- Expected result: Ensure that the connection sequence is visualized correctly with multiple fragments and connections.
- Evidence: Нет; требуется ручная проверка.

### T235. [unit] `test_visualize_fragment`

- File: `tests/unit/test_rdkit_bridge.py`
- Scenario: Test fragment visualization with different highlight settings.
- Expected result: Verify that the fragment is visualized correctly with and without highlighting attachment points.
- Evidence: Нет; требуется ручная проверка.

### T236. [unit] `generate_pdf_report`

- File: `tests/unit/test_report.py`
- Scenario: Test with invalid input parameters.
- Expected result: The function should raise an appropriate exception.
- Evidence: Нет; требуется ручная проверка.

### T237. [unit] `test_generate_pdf_report`

- File: `tests/unit/test_report.py`
- Scenario: Check for specific content within the PDF.
- Expected result: The PDF should contain expected text or data.
- Evidence: `L34–L35` — The test checks only the file signature.

### T238. [unit] `test_generate_pdf_report_empty_table`

- File: `tests/unit/test_report.py`
- Scenario: Check for specific content within the PDF when the table is empty.
- Expected result: The PDF should contain a message indicating that the table is empty.
- Evidence: `L43–L44` — The test checks only the file signature.

### T239. [unit] `test_aromaticity_index`

- File: `tests/unit/test_statistics.py`
- Scenario: Test with a compound that has no aromatic rings.
- Expected result: The function should return 0.0.
- Evidence: Нет; требуется ручная проверка.

### T240. [unit] `test_compute_distribution_metrics`

- File: `tests/unit/test_statistics.py`
- Scenario: Test with a DataFrame that has missing values.
- Expected result: The function should handle missing values gracefully.
- Evidence: Нет; требуется ручная проверка.

### T241. [unit] `test_create_histograms_plot`

- File: `tests/unit/test_statistics.py`
- Scenario: Test with a DataFrame that has a single column.
- Expected result: The function should raise an exception or handle the case gracefully.
- Evidence: Нет; требуется ручная проверка.

### T242. [unit] `test_molecules_csv_header_structure`

- File: `tests/unit/test_structural_validity.py`
- Scenario: Проверка структуры заголовка molecules.csv для других наборов данных.
- Expected result: Заголовок должен соответствовать ожидаемым полям.
- Evidence: Нет; требуется ручная проверка.

### T243. [unit] `test_required_files_exist_in_set_01`

- File: `tests/unit/test_structural_validity.py`
- Scenario: Проверка наличия всех необходимых файлов в других наборах данных.
- Expected result: Все необходимые файлы должны существовать.
- Evidence: Нет; требуется ручная проверка.

### T244. [unit] `test_spectra_csv_headers_use_mass_and_intensity`

- File: `tests/unit/test_structural_validity.py`
- Scenario: Проверка заголовков CSV для других наборов данных.
- Expected result: Заголовки должны соответствовать ожидаемым значениям.
- Evidence: Нет; требуется ручная проверка.

### T245. [unit] `test_basic_computation`

- File: `tests/unit/test_van_krevelen.py`
- Scenario: Verify the computation of the 'n_cooh' column in the 'compute_van_krevelen_data' function.
- Expected result: The 'n_cooh' column should have the correct values.
- Evidence: Нет; требуется ручная проверка.

### T246. [unit] `test_no_crash_on_equal_intensities`

- File: `tests/unit/test_van_krevelen.py`
- Scenario: Verify that the plot uses a fallback size when all intensities are equal.
- Expected result: The plot should have a specific fallback size.
- Evidence: Нет; требуется ручная проверка.

### T247. [unit] `test_save_png`

- File: `tests/unit/test_van_krevelen.py`
- Scenario: Test saving the plot to a PNG file using an in-memory file-like object.
- Expected result: The in-memory file should contain the plot data.
- Evidence: Нет; требуется ручная проверка.

### T248. [unit] `generate_icon`

- File: `tools/build_exe.py`
- Scenario: Test with a mock image generation to ensure icon creation is handled correctly.
- Expected result: Icon is generated without errors.
- Evidence: Нет; требуется ручная проверка.

### T249. [unit] `run`

- File: `tools/build_exe.py`
- Scenario: Test with a mock subprocess call to ensure command execution is handled correctly.
- Expected result: Subprocess call is executed with the correct arguments.
- Evidence: Нет; требуется ручная проверка.

### T250. [integration] `smoke_test_exe`

- File: `tools/build_exe.py`
- Scenario: Test with a mock executable to ensure the smoke test logic is correct.
- Expected result: Executable is launched and terminated correctly.
- Evidence: Нет; требуется ручная проверка.

### T251. [unit] `run_benchmark`

- File: `tools/run_benchmark.py`
- Scenario: Test with a valid benchmark ID and task ID.
- Expected result: Benchmark runs successfully and generates a report.
- Evidence: Нет; требуется ручная проверка.

### T252. [unit] `run_benchmark`

- File: `tools/run_benchmark.py`
- Scenario: Test with an invalid benchmark ID.
- Expected result: Script returns an error and does not generate a report.
- Evidence: Нет; требуется ручная проверка.

### T253. [unit] `run_benchmark`

- File: `tools/run_benchmark.py`
- Scenario: Test with an invalid task ID.
- Expected result: Script returns an error and does not generate a report.
- Evidence: Нет; требуется ручная проверка.
