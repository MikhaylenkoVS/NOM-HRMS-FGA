# GitHub Manual Setup

Действия, которые необходимо выполнить вручную в GitHub Settings.
DeepCode не может и не должен выполнять их через файлы репозитория.

## 1. Branch protection для main

Settings → Branches → Add branch protection rule:

- **Branch name pattern:** `main`
- [x] Require a pull request before merging
- [x] Require status checks to pass before merging
- [x] Block force pushes
- [x] Require conversation resolution before merging
- [ ] Require linear history (optional — рекомендуется)

## 2. Required status checks

После первого успешного запуска CI добавьте в required checks:

- `Lint (flake8 + black check)`
- `Test (Python 3.12)` (или последняя стабильная версия)
- `AI Workflow Checks`
- `AI Artifacts Validation` (если изменены `.ai/` файлы)

## 3. Actions permissions

Settings → Actions → General:

- **Actions permissions:** Allow all actions and reusable workflows
- **Workflow permissions:** Read repository contents and packages permissions only
- [x] Allow GitHub Actions to create and approve pull requests: **OFF**
  (DeepCode и CI не должны создавать PR автоматически)

## 4. Secrets

Settings → Secrets and variables → Actions:

Никогда не хранить секреты в репозитории. Добавить через GitHub UI:

| Secret | Назначение | Когда нужен |
|--------|-----------|------------|
| `PYPI_TOKEN` | Публикация в PyPI | Когда будет настроена публикация |
| `SIGNING_KEY` | Подпись `.exe` | Когда будет сертификат |

## 5. Dependabot alerts

Settings → Code security and analysis:

- [x] Dependabot alerts: **ON**
- [x] Dependabot security updates: **ON**
- [x] Dependabot version updates: через `.github/dependabot.yml` (уже настроен)

## 6. Code scanning / Secret scanning

Settings → Code security and analysis:

- [x] Secret scanning: **ON** (если доступно на плане)
- [x] Push protection: **ON** (рекомендуется)

## 7. Protected tags / Release branches

Settings → Branches → Add branch protection rule:

- **Branch name pattern:** `v*` (version tags)
- [x] Block force pushes
- [ ] Require pull request (опционально, если есть release-ветки)

## 8. Добавление GitHub username в CODEOWNERS

Файл `.github/CODEOWNERS` уже создан с указанием `@MikhaylenkoVS`.
Если username изменился, отредактируйте файл.

## 9. Включение required checks после первого CI

1. Открыть PR (любой тестовый)
2. Дождаться первого успешного запуска CI
3. Settings → Branches → Edit protection rule for `main`
4. В списке "Status checks that are required" выбрать:
   - `Lint (flake8 + black check)`
   - `Test (Python 3.12)`
   - `AI Workflow Checks`

## 10. Первый запуск

Перед первым PR с инфраструктурой:

```bash
# Проверить репозиторий
python tools/ai_workflow.py check-repo

# Создать тестовую задачу для проверки работоспособности
python tools/ai_workflow.py new-task test-smoke --title "Smoke test" --type test --risk low
python tools/ai_workflow.py validate-task test-smoke
python tools/ai_workflow.py task-status test-smoke
```
