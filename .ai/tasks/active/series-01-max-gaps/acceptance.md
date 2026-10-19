# Критерии приёмки

* [x] `find_series` по умолчанию допускает ровно 1 пропуск (`TestMaxGaps::test_default_value_is_one`)
* [x] `max_gaps=0` запрещает пропуски (`test_zero_gaps_disabled`)
* [x] Второй пропуск обрывает серию (`test_second_gap_truncates_series`)
* [x] Пользователь может расширить бюджет (`test_user_can_widen_budget`)
* [x] Синоним `allow_gaps=False` равен `max_gaps=0` (`test_allow_gaps_false_is_alias_for_zero`)
* [x] Инвариант `len(missing) <= max_gaps` (`test_budget_is_never_exceeded`)
* [x] Параметр протянут в `pipeline.json`, GUI и CLI
* [x] Отрицательное значение вызывает ValueError (`test_negative_raises`)
