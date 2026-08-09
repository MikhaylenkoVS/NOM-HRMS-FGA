# Constraints: Harden AI-workflow gates

- Do not change scientific/application code
- Do not add secrets or real credentials
- Do not add cloud/SaaS dependencies
- Use existing project tools and Python stdlib where possible
- Do not convert advisory checks to blocking without controlled migration
- Do not add shell execution from workflow_dispatch inputs
- Do not perform automatic merge/release/push to main
- Do not add new external dependencies without strong justification
