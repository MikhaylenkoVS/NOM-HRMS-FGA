# ADR-0001: AI-Assisted Development Workflow

- **Status:** accepted
- **Date:** 2026-08-08
- **Owners:** MikhaylenkoVS
- **Related task:** example-ai-workflow-bootstrap
- **Related issue/PR:** none
- **Supersedes:** none
- **Superseded by:** none

## Context

NOM-HRMS-FGA — научный инструмент с интерактивным рабочим процессом
(пользователь → GUI → pipeline → визуализация). Проект развивается одним
автором при поддержке AI-агентов:

- **Perplexity** — исследование, декомпозиция, архитектурные решения, review
- **DeepCode** — работа с репозиторием, код, тесты, benchmark, commit/PR
- **Человек** — постановка приоритетов, утверждение архитектурно важных
  решений, merge и релизы

Требуется формальный процесс, гарантирующий безопасность научного кода,
воспроизводимость результатов и качество изменений при полуавтоматической
совместной работе.

## Decision

1. **Task packet как system of record.** Каждая значимая задача оформляется
   как task packet в `.ai/tasks/active/<task-id>/`. Task packet содержит
   `task.json` (machine-readable) и набор markdown-артефактов.

2. **Git branch/PR workflow.** Каждая задача — отдельная feature-ветка от
   `main`. PR должен пройти CI, AI-ревью и ручное утверждение перед merge.

3. **Роли и границы:**
   - Perplexity: исследование, архитектура, code review. Не пишет код.
   - DeepCode: реализация, тесты, commit, PR. Не делает merge/release/push в main.
   - Человек: утверждение, merge, release. Единственный, кто может push в main.

4. **Запрет прямой записи в main.** Ни один AI-агент не выполняет push в main
   или merge PR. Это исключительная прерогатива человека.

5. **Обязательные проверки для high/critical задач:**
   - Task packet с полным набором артефактов
   - ADR (если затрагивает архитектуру или научную логику)
   - Benchmark report (для performance-задач)
   - Reference equivalence test (для scientific-задач)
   - Human approval

6. **Benchmark и scientific equivalence:**
   - Performance-задачи требуют benchmark report и сравнение с baseline
   - Scientific-задачи требуют проверки эквивалентности на reference dataset
   - Baseline хранятся в `.ai/baselines/`, обновляются только человеком

7. **Порядок ревью:**
   - DeepCode implementation → implementation report
   - Perplexity review → замечания в review_request.md
   - DeepCode fixes → обновление implementation report
   - Human approval → merge

8. **Инфраструктурные файлы:**
   - `AGENTS.md` — правила для AI-агентов
   - `CONTRIBUTING.md` — правила для контрибьюторов
   - `tools/ai_workflow.py` — CLI для управления задачами (stdlib only)
   - `docs/ai_workflow.md` — описание полного рабочего процесса

## Alternatives considered

| Alternative | Pros | Cons | Reason rejected |
|------------|------|------|-----------------|
| Без task packet (только PR) | Проще | Нет audit trail, нельзя автоматизировать проверки | Недостаточно для научного проекта |
| YAML-based task format | Человекочитаемо | Требует PyYAML dependency | JSON — часть stdlib |
| Полностью автоматический merge AI | Быстрее | Риск повреждения научного кода | Неприемлемо для production |

## Consequences

### Positive

- Чёткое разделение ролей и ответственности
- Машиночитаемый audit trail всех изменений
- Автоматическая валидация task packet через CLI
- Безопасность научного кода через обязательные проверки

### Negative

- Дополнительный overhead на создание и ведение task packet
- Более медленный процесс для простых изменений

### Risks

- **Overhead для мелких задач:** mitigated — task packet обязателен только
  для architecture/scientific/performance/formula-db/packaging/security задач
- **Накопление незавершённых task packet:** mitigated — `check-repo` и CI
  будут обнаруживать незавершённые пакеты

## Validation and rollback

- Валидация: `python tools/ai_workflow.py check-repo`
- Rollback: удалить `.ai/`, `AGENTS.md`, `CONTRIBUTING.md`, `tools/ai_workflow.py`

## Scientific/reproducibility impact

- Не затрагивает научную логику
- Обеспечивает audit trail для всех изменений, влияющих на результаты
- Требует reference equivalence для scientific-задач

## References

- [.ai/workflow.md](../workflow.md)
- [AGENTS.md](../../AGENTS.md)
- [CONTRIBUTING.md](../../CONTRIBUTING.md)
- [docs/ai_workflow.md](../../docs/ai_workflow.md)
