# Критерии приёмки

* [x] Совпадение по m/z удаляет пик независимо от интенсивности (`test_intensities_are_ignored`)
* [x] Пики за пределами ppm-окна сохраняются (`test_within_ppm_removed_outside_kept`)
* [x] Пустые входы обрабатываются корректно (`test_empty_derivative`, `test_empty_source_keeps_everything`)
* [x] Порядок пиков сохраняется (`test_order_is_preserved`)
* [x] Отрицательное окно вызывает ошибку (`test_negative_ppm_raises`)
* [x] Опции протянуты в GUI, CLI, `pipeline.json`
* [ ] A/B на F16 подтверждает отсутствие потери настоящих серий (в работе)
