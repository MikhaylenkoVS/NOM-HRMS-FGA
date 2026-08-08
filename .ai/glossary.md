# Glossary — AI Workflow Terminology

| Термин | Определение |
|--------|------------|
| **Task packet** | Набор файлов в `.ai/tasks/active/<task-id>/`, описывающий задачу: `task.json`, `design.md`, `acceptance.md`, `constraints.md`, `risks.md`, и т.д. |
| **ADR** | Architecture Decision Record — документ в `.ai/decisions/`, фиксирующий архитектурное решение. |
| **Handoff** | Файл `deepcode_handoff.md`, сгенерированный командой `render-handoff` для передачи задачи от Perplexity к DeepCode. |
| **Implementation report** | `implementation_report.md` — отчёт DeepCode о выполненной работе. |
| **Benchmark report** | `benchmark_report.md` — отчёт о производительности с сравнением с baseline. |
| **Reference equivalence** | Проверка, что научный результат идентичен эталонному (reference dataset или reference implementation). |
| **Human decisions** | `human_decisions.md` — журнал решений, принятых человеком в ходе задачи. |
| **Rollback plan** | `rollback_plan.md` — план отката изменений в случае проблем. |
| **Scope creep** | Неконтролируемое расширение scope задачи за пределы изначально согласованного. |
| **Check-repo** | Команда `python tools/ai_workflow.py check-repo`, выполняющая санитарные проверки репозитория. |
