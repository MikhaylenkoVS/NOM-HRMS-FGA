# Risks: DOC-01 — Черновик user guide

## Technical risks
| Риск | Вероятность | Влияние | Митигация |
|---|---:|---:|---|
| UI labels не совпадут с текущей версией | Medium | High | Ручная сверка перед merge |
| CSV schema описана по предположению | Medium | High | Проверить reader-код и тестовые CSV |
| pip-инструкция устарела | Medium | Medium | Использовать только подтверждённый путь |
| Presets изменятся | Medium | Medium | Проверить JSON и version target |
| Ссылки Markdown будут битые | Low | Medium | Проверить rendering и ссылки |

## Scientific risks
| Риск | Вероятность | Влияние | Митигация |
|---|---:|---:|---|
| Formula assignment примут за доказательство структуры | High | High | Явно описать ограничение |
| Preset применят как универсальную настройку | High | Medium | Указать, что это стартовая точка |
| Некорректный CSV приведёт к интерпретации артефактов | Medium | High | Примеры и troubleshooting |
| VK plot примут за структурное доказательство | Medium | High | Описать назначение и ограничения |

## Escalation conditions
Остановить работу и запросить human decision, если CSV schema, фактический UI, pip installation или назначение presets нельзя подтвердить по текущему проекту.
