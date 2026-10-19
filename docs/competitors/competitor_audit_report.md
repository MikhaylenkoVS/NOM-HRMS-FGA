# Конкурентный аудит открытых программ HRMS/NOM: полная версия

**Дата:** 15 октября 2026 · **Метод:** сплошной анализ исходного кода (не документации)
**Машиночитаемые данные:** `docs/competitors/raw/` (инвентарь, индекс символов, вхождения по операциям, матрицы)
**Подробное приложение «операция × проект»:** `docs/competitors/operations_detail.md`
**Краткая структурированная версия:** `docs/competitors/competitor_audit.json`

---

## 0. Ответы на три поставленных вопроса

### 1. Клоны собраны полностью

Все 11 проектов с открытым кодом склонированы **полными клонами** (`git clone --depth 1`,
без `--filter`, без sparse), включая ранее пропущенные крупные:

| Проект | Репозиторий | Размер на диске | Язык |
|---|---|---|---|
| OpenMS | `OpenMS/OpenMS` | **1.3 ГБ** | C++/Python |
| CoreMS | `EMSL-Computing/CoreMS` | 767 МБ | Python |
| MZmine | `mzmine/mzmine` | 629 МБ | Java |
| MS-DIAL | `systemsomicslab/MsdialWorkbench` | 231 МБ | C# |
| PyC2MC | `iC2MC/PyC2MC_viewer` | 107 МБ | Python |
| Formultitude | `PNNL-Comp-Mass-Spec/Formultitude` | 29 МБ | C# |
| NOMspectra | `NOMspectra/NOMspectra` | 26 МБ | Python |
| xcms | Bioconductor `xcms` | 7.1 МБ | R |
| UME | `boriskoch/ume` | 6.9 МБ | R |
| MFAssignR | `skschum/MFAssignR` | 3.8 МБ | R |
| **ICBM-OCEAN** | `JulianMerder/ICBM-OCEAN--Supplementary-Code-Modules` | 170 КБ | R |

**ICBM-OCEAN найден**: основное веб-приложение не опубликовано, но официальные
дополнительные модули с кодом есть на GitHub (найдено через GitHub API-поиск).
Это меняет статус проекта: раньше он был «без исходников», теперь — 5 файлов R
с ключевыми алгоритмами (см. §5.11).

### 2. Насколько полон аудит: честная оценка (было → стало)

**Первый проход** (тот, что показался вам подозрительно быстрым) был **выборочным**:
читались только ключевые места, остальное — имена файлов. Фактически:

| Проект | Что было прочитано в первом проходе | Объём прочитанного |
|---|---|---|
| NOMspectra | `spectrum.py` (assign, noise_filter, filter_by_C13, merge_isotopes), `recal.py`, `brutto.py`, `spectra.py`, `metadata.py` | ~8 файлов, ~25 % кода |
| MFAssignR | сигнатуры функций через grep (KMDNoise, IsoFiltR, MFAssign, MFAssignCHO, FindCoreFormulae2) | ~10 строк-сигнатур из 12 163 |
| CoreMS | списки классов методов в 10 модулях, без тел функций | ~200 строк из 53 720 |
| UME | 2 сигнатуры (`assign_formulas`, `calc_recalibrate_pro`…) | единицы строк из 13 322 |
| PyC2MC | списки методов молекулярных карт | ~20 строк из 492 616 |
| xcms | grep по именам функций | ~10 строк из 60 777 |
| Formultitude | только имена проектов и файлов | 0 строк кода |
| MZmine | только имена файлов (GitHub API) | 0 строк кода |
| OpenMS | только список каталога CHEMISTRY | 0 строк кода |
| MS-DIAL | только список каталога Algorithm | 0 строк кода |

То есть **содержательная проверка покрывала ~5 % кода**, а по четырём крупным проектам
была нулевой. Это и объясняет скорость.

**Сейчас** построена сплошная инвентаризация — она не «додумывает», а фиксирует всё:

| Проект | Файлов | Строк | Символов (классы/функции) | Лицензия | Операций с попаданиями |
|---|---:|---:|---:|---|---:|
| OpenMS | 3 446 | 1 418 370 | 13 579 | BSD | 29/29 |
| MS-DIAL | 3 668 | 839 441 | 42 985 | LGPL-2.1 (см. §9) | 28/29 |
| MZmine | 4 110 | 658 745 | 55 157 | MIT | 29/29 |
| PyC2MC | 48 | 492 616 | 244 | GPL-3 | 21/29 |
| xcms | 115 | 60 777 | 1 404 | GPL-2 | 24/29 |
| CoreMS | 124 | 53 720 | 1 599 | BSD | 26/29 |
| Formultitude | 70 | 24 301 | 721 | **файла лицензии нет** | 23/29 |
| UME | 82 | 13 322 | 163 | не подтверждена | 25/29 |
| MFAssignR | 15 | 12 163 | 33 | GPL-2 | 20/29 |
| NOMspectra | 14 | 6 738 | 180 | GPL-3 | 18/29 |
| ICBM-OCEAN | 5 | 343 | 3 | GPL-3 | 11/29 |
| **Итого** | **11 697** | **3 580 536** | **116 068** | — | — |

Что именно сохраняется по каждому проекту (в `docs/competitors/raw/`):

* `<project>_index.json` — **все** исходные файлы с числом строк/непустых строк/байт по
  каждому файлу и **полный индекс символов** (класс/функция/метод + файл + строка + текст);
* `<project>_operations.json` — по каждой из **29 операций**: общее число вхождений
  (точное), список файлов и примеры вхождений `файл:строка: текст`;
* `_combined_summary.json` — метрики по всем проектам;
* `_operations_matrix.json` / `_operations_matrix.md` — матрица «операция × проект»;
* `operations_detail.md` — подробное приложение с топ-файлами и примерами кода.

**Что осталось за рамками сканирования** (фиксируется явно, а не умалчивается):
каталоги `tests/test/data/docs/examples/build/dist/target/bin/obj/node_modules/packages`.
Это тесты, данные и сборочные артефакты, а не реализация операций. Их количество
по каждому каталогу сохранено в поле `skipped_source_files_by_dir` каждого
`<project>_index.json` — то есть при необходимости можно посчитать и их.

**Чего в аудите по-прежнему нет** (объективные ограничения):

* закрытый код: Composer, PetroOrg, Bruker DataAnalysis/SmartFormula, Thermo FreeStyle,
  Compound Discoverer — исходников нет ни у кого, кроме производителя;
* у ICBM-OCEAN опубликованы только дополнительные модули: назначения формул и
  веб-пайплайна в них нет;
* MS-DIAL/OpenMS/MZmine — это гигантские платформы (до 1.4 млн строк каждая); я
  проиндексировал их **полностью**, но глубокое чтение конкретных алгоритмов
  (построчное) в этом объёме не выполнялось: для каждой операции в JSON есть
  конкретные файлы и строки-примеры, дальше можно углубляться точечно.

### 3. Информация собрана обо всех операциях — без «избранного»

Задано **29 наборов операций** (от чтения RAW и транзиента до молекулярных сетей и
провенанса), и по каждому проекту зафиксированы **все** вхождения ключевых слов, а не
отобранные. Ничего не выброшено: если операция дала ноль попаданий, это тоже зафиксировано
(прочерк в матрице). Полная матрица — ниже (§4), подробные примеры — в приложении
`docs/competitors/operations_detail.md`.

---

## 1. Как устроен аудит (воспроизводимо)

1. `tools/diagnostics/audit_competitors.py` — обход всех исходных файлов, подсчёт строк,
   построение индекса символов (Python, R с S4, Java, C#, C/C++), поиск по 29 наборам
   ключевых слов, запись JSON;
2. `tools/diagnostics/merge_competitor_audit.py` — сводные матрицы;
3. `tools/diagnostics/gen_operations_detail.py` — читаемое приложение.

Перегенерация (в корне проекта):

```bash
python tools/diagnostics/audit_competitors.py --root D:/Temp/User/competitors \
    --out docs/competitors/raw --hit-cap 5000
python tools/diagnostics/merge_competitor_audit.py
python tools/diagnostics/gen_operations_detail.py
```

Ограничение по объёму: на каждую пару «операция × проект» сохраняются первые
5 000 вхождений (общее число вхождений при этом точное, флаг `truncated` показывает,
что список урезан). Для всех 11 проектов снимок укладывается в 77 МБ JSON.

---

## 2. Матрица операций (попадания ключевых слов в код)

Полная таблица — `docs/competitors/raw/_operations_matrix.md` (там же топ-файлы по
каждой паре). Числа — количество вхождений; прочерк — нет попаданий.

| Операция | corems | formult. | icbmocean | mfassignr | msdial | mzmine | nomspectra | openms | pyc2mc | ume | xcms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| raw_vendor_io | 210 | 31 | — | — | 416 | 1926 | — | 4088 | 12 | 9 | 55 |
| transient_ft | 448 | 1 | — | — | 19 | 99 | 2 | 469 | 1 | 177 | 8 |
| profile_preprocessing | 457 | 11 | 1 | 7 | 4681 | 1798 | 27 | 2802 | 17 | 20 | 223 |
| peak_picking_centroiding | 972 | 27 | — | 2 | 1088 | 1072 | — | 2823 | 1 | — | 333 |
| noise_estimation | 242 | 51 | — | 40 | 116 | 635 | 11 | 552 | 1 | 37 | 65 |
| mass_calibration | 378 | 407 | — | 42 | 128 | 1433 | 1 | 2417 | — | 59 | 118 |
| rt_alignment | 436 | 116 | — | 3 | 10024 | 1398 | — | 2302 | 477 | 31 | 897 |
| chromatographic_features | 2263 | — | — | — | 11267 | 26655 | 1 | 23341 | — | 62 | 3129 |
| gap_filling | 33 | — | — | — | 246 | 296 | — | 59 | — | 8 | 217 |
| isotope_detection | 392 | 272 | 22 | 1112 | 7795 | 3564 | 71 | 6010 | 107 | 442 | 250 |
| adduct_ion_identity | 303 | 203 | — | 367 | 16395 | 2098 | — | 3203 | 45 | 4 | 74 |
| charge_state | 42 | 33 | 2 | 22 | 1231 | 5315 | 21 | 4557 | 6 | 14 | 388 |
| formula_assignment | 860 | 43 | 1 | 44 | 6504 | 1749 | 69 | 2748 | 261 | 335 | 22 |
| formula_scoring | 211 | 76 | — | 24 | 2956 | 2038 | 44 | 6287 | 12 | 144 | 370 |
| ambiguity_handling | 40 | — | — | 174 | 54 | 15 | 33 | 1372 | — | 2 | — |
| chemical_rules | 102 | 26 | — | 232 | 656 | 281 | 46 | 67 | 369 | 110 | — |
| halogen_support | 485 | 122 | 2 | 336 | 4903 | 13818 | 25 | 27342 | 324 | 67 | 745 |
| internal_recalibration_series | — | 8 | 1 | 43 | — | 1 | — | 75 | — | — | — |
| kendrick | 198 | 42 | 1 | 111 | 8 | 637 | 12 | 1 | 436 | 36 | — |
| descriptors | 66 | 2 | — | 26 | 2847 | 167 | 112 | 110 | 236 | 74 | 4 |
| similarity | 428 | — | — | — | 4178 | 2781 | 25 | 1581 | — | 6 | 173 |
| statistics | 641 | 199 | 2 | — | 377 | 1067 | — | 2206 | 90 | 38 | 40 |
| visualization | 296 | 69 | 13 | 67 | 3594 | 9197 | 122 | 1349 | 380 | 141 | 279 |
| msms | 966 | 4 | — | 12 | 17658 | 11037 | — | 16890 | 1 | 1 | 280 |
| ion_mobility_ccs | — | 2 | — | — | 4436 | 1677 | — | 2714 | — | — | 6 |
| molecular_networking | — | — | — | — | 27 | 77 | — | 15 | — | — | — |
| qc_metrics | 19 | — | 4 | 55 | 4176 | 972 | — | 2938 | 4 | 94 | 80 |
| provenance_workflow | 896 | 1 | — | — | 1711 | 3866 | 142 | 4021 | 3 | 25 | 369 |
| io_export | 581 | 88 | 1 | 3 | 215 | 567 | 30 | 2336 | 182 | 15 | 64 |

*Строка `halogen_support` пересчитана после уточнения шаблонов (однобуквенные «F/Cl/Br/I»
давали ложные срабатывания на переменных); актуальные числа — в файле матрицы.*

---

## 3. Реализации по проектам (что именно найдено в коде)

### 3.1 NOMspectra (Python, GPL-3.0) — самый удобный для импорта

Ядро: `spectrum.py` 1 812, `brutto.py` 477, `recal.py` 455, `spectra.py` 364, `diff.py` 352,
`metadata.py` 112, `draw.py` 531; GUI 2 568 строк.

* **Назначение формул** — `spectrum.py:272 assign()`: таблица из `brutto_gen` (C 4–50,
  H 4–100, O 0–25, N 0–3, S 0–2; флаг `rules`), `np.searchsorted` по массам, ближайшая
  формула в пределах `rel_error` (0.5 ppm) или `abs_error`, допуск делится на заряд,
  сдвиги по режимам `-`/`+`/`0` (`±m(e)`, `+m(H)`), **цикл по зарядам** `charge_max`,
  фильтры по массе/интенсивности; результат — **одно** значение `assign` + элементы + `charge`.
* **Шум** — `:426 noise_filter(force=1.5, intensity, quantile)`: жёсткий порог, квантиль
  или авторежим (100 порогов по `linspace(0, mean(intensity))`, точка минимума градиента
  кривой выживания × `force`).
* **Изотопы** — `:525 filter_by_C13(rel_error=0.5, remove=False)`: бинарный флаг наличия
  пика `+1.003355`; `:609 merge_isotopes()` сворачивает «изотопные элементы» (`C_13`) в базовые.
* **Рекалибровка** — `recal.py`: `recallibrate()`, `ErrorTable` (`md_error_map`, `fit_kernel`,
  `kernel_density_map`, `assign_error`, `massdiff_error`, `etalon_error`, `extrapolate`) —
  **KDE-модель ошибки масс** с экстраполяцией за пределы калибрантов.
* **Алгебра спектров** — `:754–1005`: `__or__`, `__xor__`, `__and__`, `__add__`, `__sub__`,
  `intens_sub`, `simmilarity(mode='cosine'|Callable)`.
* **Дескрипторы** — `:1005–1727`: `brutto`, `cram`, `ai`, `cai`, `dbe_ai`, `dbe`, `dbe_o`,
  `dbe_oc`, `hc_oc`, `kendrick`, `nosc`, `mol_class`, `get_dbe_vs_o`, `get_squares_vk`,
  `get_mol_metrics`, `calc_all_metrics`.
* **Наборы** — `spectra.py` `SpectrumList`: матрица близости, метрики, плотности Ван-Кревелена.
* **Метаданные** — `metadata.py`: журнал операций (`metadata.add`) сохраняется с данными.
* **Нет**: RAW/транзиент, хроматография, MS/MS, аддукты, ионная подвижность.

### 3.2 MFAssignR (R, GPL-2.0) — 15 файлов, 12 163 строки, 33 функции

* `KMDNoise.R:82 KMDNoise(df, upper.y=0.2, lower.y=0.05, upper.x=NA, lower.x=NA)` — шум по
  разделению в координатах Kendrick mass defect; `:157 SNplot(df, cut, mass, window.x=0.5,
  window.y=10)` — диагностический график порога.
* `HistNoise.R:36 HistNoise(df, SN=0, bin=0.01)` — оценка шума по гистограмме.
* `IsoFiltR.R:54 IsoFiltR(peaks, SN=0, Carbrat=60, Sulfrat=30, Sulferr=5, Carberr=5)` —
  разделение на моноизотопные и изотопные пики по 13C/34S с отдельными допусками.
* `MFAssignCHO.R:108 MFAssignCHO(..., ionMode, POEx, NOEx, Ex, Mx, NH4x, Zx=1, Ox=30, ...)` —
  быстрое CHO-назначение для поиска калибрантных серий.
* `MFAssign.R:154 MFAssign(..., Nx, Sx, Px, S34x, ...)` — полное многоэлементное назначение
  с изотопными осями и аддуктами; явные `C13_mass`, `S34_mass`, `Iso_mass`;
  разделение результатов на однозначные/неоднозначные/неназначенные.
* `FindCoreFormulae2.R:20`, `FindCoreFormulae2_Halogen.R:20` — ядровые формулы, в т. ч. галогены.
* `RecalFunctions.R` — гомологические серии-калибранты (`RecalList`/`FindRecalSeries`/`Recal`).

### 3.3 CoreMS (Python, BSD-2) — 124 файла, 53 720 строк, 1 599 символов

* Транзиент: `corems/transient/calc/TransientCalc.py` — `zero_fill` (`:88`), `truncation` (`:126`),
  `apodization` (`:157`), `calculate_frequency_domain` (`:216`), `cut_freq_domain` (`:244`),
  `phase_and_absorption_mode_ft` (`:295`).
* Шум: `mass_spectrum/calc/NoiseCalc.py` — `NoiseThresholdCalc.get_noise_threshold` (`:59`),
  `run_log_noise_threshold_calc` (`:278`), `get_abundance_minima_centroid` (`:245`);
  отдельный `NoiseCalc_Bayes.py`.
* Пики: `PeakPicking.py` — `do_peak_picking` (`:270`), `find_minima(..., right=True)` (`:295`).
* Калибровка: `Calibration.py` — `gen_ref_mass_list_from_assigned(min_conf=0.7)` (`:158`),
  `find_calibration_points` (`:190`), `robust_calib` (`:347`), `recalibrate_mass_spectrum` (`:409`);
  плюс `AutoRecalibration.py`.
* Формулы: `molecular_id/search/molecularFormulaSearch.py` — `SearchMolecularFormulas` (`:26`),
  `SearchMolecularFormulaWorker(find_isotopologues=True)` (`:495`), `find_formulas` (`:665`),
  `mass_by_ion_type` (`:721`), `calc_error(..., method="ppm")` (`:622`).
* Приоритетное назначение: `priorityAssignment.py` — `OxygenPriorityAssignment` (`:20`),
  `check_adduct_class` (`:163`), `set_min_max_dbe_by_oxygen` (`:183`), `add_adducts` (`:656`);
  `findOxygenPeaks.py`.
* Kendrick: `mass_spectrum/calc/KendrickGroup.py` — `KendrickGrouping` (`:1`),
  `populate_kendrick_index_dict_error` (`:59`), `..._rounding` (`:127`).

### 3.4 UME (R-пакет, 82 файла, 13 322 строки)

`assign_formulas(pl, formula_library, ...)` (`ume/R/assign_formulas.R:82`) — назначение по
**предварительно построенной библиотеке формул**; `calc_isotope_pattern` (`:121`),
`build_isotope_map`; `calc_recalibrate_ms` (`:70`); метрики: `calc_dbe`, `calc_indeces`,
`calc_exact_mass`, `calc_neutral_mass`, `calc_norm_int`, `calc_number_assignment`,
`calc_number_occurrence`, `calc_eval_params`.

### 3.5 PyC2MC (Python, GPL-3) — 48 файлов, 492 616 строк (включая сгенерированные UI)

`modules/molecular_maps.py` — карты DBE (`:4`), Ван-Кревелена (`:388`), KMD (`:672`),
mass defect (`:1032`), сравнения (`:1374`, `:1645`, `:2003`), индексы ACOS (`:2305`),
MAI (`:2531`), MCR (`:2821`); `modules/comparison.py` — сравнение образцов (`:4`, `:326`) и
Kendrick-мотивы (`:623`, `:641`, `:661`). Назначения формул в коде нет — вход внешний.

### 3.6 Formultitude (C#/.NET) — 70 файлов, 24 301 строка, лицензии нет

Проекты `CIA/` (`CIAProgramStart.cs`, `FormultitudeProgram.cs`), `CiaUi/`, `FileReader/FileReader.cs`,
`Support/CFileReader.cs`, `FindChains/`, `Data/`. Это реальный код CIA (поиск по библиотеке
формул CHONSP с tie-break по числу гетероатомов) и IPA (изотопные паттерны), но **файла
лицензии в репозитории нет** → переиспользование кода юридически невозможно.

### 3.7 xcms (R/Bioconductor, GPL-2) — 115 файлов, 60 777 строк, 1 404 символа

`functions-OnDiskMSnExp.R:95 findPeaks_MSW_OnDiskMSnExp`, `MPI.R:10 findPeaksPar`,
`MPI.R:76 fillPeaksChromPar`, `functions-utils.R:704 groupOverlaps`,
`functions-xcmsSet.R:6 xcmsSet` — эталон параметров LC-MS обработки.

### 3.8 MZmine (Java, MIT для исходников) — 4 110 файлов, 658 745 строк, 55 157 символов

Реальные файлы (из полного клона): формула — `FormulaType`, `FormulaListType`,
`ConsensusFormulaListType` (60 файлов по теме Formula); ионные формы — `IonIdentity.java`,
`MSMSIonIdentity.java`, `MSMSIonRelationIdentity.java` (28 файлов); изотопы — `IsotopePattern.java`,
`SimpleIsotopePattern.java`, `MultiChargeStateIsotopePattern.java`, `IsotopePatternScoreType.java`
(115 файлов); пропуски — `GapFill*` (18), `Gap.java`, `GapDataPoint.java`, `PeakFinderModule.java`;
Kendrick — `KendrickMassDefectFilter*`, `KendrickFalseNegativeDetector`,
`KendrickFalsePositiveUtils` (30).

### 3.9 OpenMS (C++/pyOpenMS, BSD-3) — 3 446 файлов, 1 418 370 строк

`src/openms/source/CHEMISTRY/`: `Element.cpp`, `ElementDB.cpp`, `EmpiricalFormula.cpp`,
`AdductInfo.cpp`, каталоги `ISOTOPEDISTRIBUTION/` (изотопные распределения) и
`MASSDECOMPOSITION/` (разложение масс на составы), `AASequence.cpp`, `ModificationsDB.cpp` и др.
Это готовые подсистемы: формула как класс с арифметикой, база элементов с изотопами,
аддукты как объекты.

### 3.10 MS-DIAL (C#/.NET, 3 668 файлов, 839 441 строка, 42 985 символов)

`src/MSDIAL5/MsdialCore/Algorithm/`: `IsotopeEstimator.cs`, `IsotopeTracking.cs`,
`CcsEstimator.cs`, `PeakSpottingCore.cs`, `PeakCharacterEstimator.cs`,
`MolecularNetworking.cs`, `CytoscapeMolecularNetworkClient.cs`, `FragmentSearcher.cs`,
каталоги `Alignment/`, `Annotation/`. Лицензия проекта в репозитории не заявлена
(есть только файл лицензий сторонних компонентов).

### 3.11 ICBM-OCEAN (R, GPL-3) — 5 файлов, 341 строка (найдено доп. модулями)

* `fastjoin.R` — «sample junction», быстрый вариант: `tolp <- 0.5`, сортировка по mz,
  жадная группировка масс в кластеры в пределах допуска (49 строк).
* `precisejoin.R` — точный вариант: `tolp <- 0.5`, цикл слияния масс с индексом уже
  объединённых, внутри кластера **взвешенное среднее mz** `weighted.mean(dxg[x,], dg[x,]^1)`
  и `sd`, отбрасывание строк без измерений (75 строк).
* `isotope_ratio_deviance_function.R` — `isotope_deviance(intensity_parent, intensity_child,
  number_of_atoms, q=0.0108, p=0.9892, number_of_isotopes=1, ...)`: **биномиальное отклонение**
  измеренного отношения 13C/12C от природного (q = 1.08 %, p = 98.92 %) — статистическая
  проверка, а не порог по отношению (68 строк).
* `create_homologous_series_network.R` — `get_network(i, r, B, indexf, homcheck)`: сеть
  гомологических серий (81 строка).
* `ResPow_outlier.R` — `ResPow_outlier(dataset, column_mass=1, column_respow=4, method=1)`:
  выбросы по зависимости массы и разрешающей способности (68 строк).

---

## 4. Где мой функционал меньше, чем у аналогов (8 пунктов)

| Операция | У меня | У аналогов (по коду) |
|---|---|---|
| Неоднозначные кандидаты | `assign` + `all_candidates` (список в колонке) | MFAssignR: раздельные unambiguous/ambiguous/unassigned; CoreMS: `OxygenPriorityAssignment` |
| Изотопы | теоретические паттерны M+1/M+2, статусы, сателлиты, измеримость | CoreMS: `find_isotopologues` + fine structure; MFAssignR: `IsoFiltR` (Mono/Iso); MZmine: `IsotopePattern` + `MultiChargeStateIsotopePattern`; UME: `calc_isotope_pattern`; ICBM-OCEAN: `isotope_deviance` (биномиальная значимость) |
| Аддукты/ионные формы | один `[M-H]-`, таблица аддуктов `status='future'` | MFAssignR: POE/NOE/E/M/NH4/Z/O; CoreMS: `mass_by_ion_type` + `add_adducts`; MZmine: `IonIdentity`; OpenMS: `AdductInfo` |
| Заряды | один заряд | NOMspectra: `charge_max`; MZmine: `MultiChargeStateIsotopePattern`; CoreMS: `ion_charge` |
| Дескрипторы и карты | DBE, AI, H/C, O/C, Ван-Кревелен | NOMspectra: `kendrick`, `cai`, `dbe_ai`, `mol_class`, `get_squares_vk`; PyC2MC: KMD/MD/ACOS/MAI/MCR; UME: набор `calc_*` |
| Provenance | логи, `PipelineStats`, параметры в xlsx, кэш | NOMspectra: журнал операций; CoreMS: HDF5+JSON; OpenMS: CTD/TOPP |
| QC-диагностика | счётчики стадий, предупреждения, PDF, материалы статьи | OpenMS: mzQC/QcML; MFAssignR: `SNplot`; ICBM-OCEAN: `ResPow_outlier` |
| Наборы образцов | один образец + производные, `core/batch.py` | ICBM-OCEAN: sample junction (fast/precise); NOMspectra: `SpectrumList`; PyC2MC: сравнения образцов |

## 5. Чего у меня нет вообще (16 пунктов)

1. Транзиент/FFT: CoreMS `TransientCalc` (`apodization`, `zero_fill`, `calculate_frequency_domain`).
2. Профильная обработка/центроидирование: CoreMS `PeakPicking`, OpenMS, MZmine, MS-DIAL.
3. **Пост-рекалибровка масс**: NOMspectra `recal.py` (KDE), CoreMS `robust_calib`, MFAssignR `Recal*`, UME `calc_recalibrate_ms` — самый значимый пробел.
4. Mono/Iso как раздельные таблицы: MFAssignR `IsoFiltR`.
5. Хроматографические признаки, RT-выравнивание, gap filling: MZmine `GapFill*`, xcms `findPeaks`/`groupOverlaps`/`fillPeaksChromPar`, MS-DIAL `Alignment/`.
6. Ионная подвижность/CCS: MS-DIAL `CcsEstimator.cs`, MZmine (IMS).
7. MS/MS-скоринг: MZmine (formula prediction + MS/MS), MS-DIAL `FragmentSearcher`, OpenMS.
8. Молекулярные сети: MZmine `MolecularNetworking`, MS-DIAL `MolecularNetworking.cs`.
9. Объекты Feature/Scan/Experiment: OpenMS (`EmpiricalFormula`, PSI-форматы), MZmine, MS-DIAL.
10. Kendrick как рабочий инструмент: CoreMS `KendrickGrouping`, MZmine `KendrickMassDefectFilter`, MFAssignR `KMDNoise`.
11. Роли образцов blank/QC, детекция дрейфа: MZmine/xcms/MS-DIAL, ICBM-OCEAN `ResPow_outlier`.
12. Воспроизводимый pipeline-recipe: OpenMS (TOPP/CTD), MZmine (batch steps).
13. Шум как объект с диагностическим графиком: MFAssignR `SNplot`, CoreMS `NoiseThresholdCalc`.
14. **Выравнивание масс между образцами до назначения (sample junction)**: ICBM-OCEAN `fastjoin.R`/`precisejoin.R`.
15. **Статистическая значимость изотопного отклонения**: ICBM-OCEAN `isotope_deviance(...)`.
16. **Диагностика разрешающей способности**: ICBM-OCEAN `ResPow_outlier(...)`.

---

## 6. Лицензии (проверено по файлам в репозиториях)

| Проект | Лицензия | Нюанс | Можно ли брать код |
|---|---|---|---|
| OpenMS | BSD-3-Clause | copyright OpenMS Inc./Tuebingen/ETH/FU Berlin | да (attribution) |
| CoreMS | BSD-2-Clause | слова «BSD» в файле нет — определена по формуле текста | да (attribution) |
| MZmine | MIT (исходники) | официальные сборки — отдельные условия | да для кода |
| NOMspectra | GPL-3.0 | — | только идеи |
| PyC2MC | GPL-3.0 | — | только идеи |
| MFAssignR | GPL-2.0 | — | только идеи |
| xcms | GPL-2 | + отдельный LICENSE (Scripps) | только идеи |
| ICBM-OCEAN | GPL-3.0 | только доп. модули | идеи/алгоритмы |
| UME | не подтверждена | в файле LICENSE текста нет (заглушка R-пакета) | идеи |
| MS-DIAL | LGPL-2.1 в файле сторонних лицензий | **своего файла лицензии в репозитории нет**; заявлено на странице проекта | уточнять |
| **Formultitude** | **файла лицензии нет** | по умолчанию «все права защищены» | **нельзя** |

---

## 7. Приоритеты доработки (по итогам кода)

**A. Научная надёжность:** пост-рекалибровка (робастная подгонка + калибранты из назначений
с высоким confidence, диагностика residual'ов); шум как объект с диагностическим графиком
порога; candidate-таблица с компонентами оценки; изотопный кластер как объект + значимость
отклонения (биномиальная, как в ICBM-OCEAN); разделение Mono/Iso; Kendrick-группировка.

**B. Данные серии:** выравнивание масс между образцами (sample junction) до назначения;
роли blank/QC/sample; detection-frequency; матрица с пропусками; pipeline-recipe + CLI.

**C. Расширенная химия:** аддукты/ионные формы как объект; fine isotope simulation;
многосвидетельский скоринг; MS/MS (когда появятся данные).

**D. Raw/profile:** модель скана/эксперимента с метаданными; усреднение с контролем RT;
baseline/centroid/FWHM/area; транзиент/FFT — только при реальной необходимости.

---

## 8. Артефакты этого аудита

| Файл | Что внутри |
|---|---|
| `docs/competitors/raw/<project>_index.json` | все исходные файлы (строки/байты) + полный индекс символов |
| `docs/competitors/raw/<project>_operations.json` | вхождения по 29 операциям (файл:строка: текст) |
| `docs/competitors/raw/_combined_summary.json` | метрики по 11 проектам |
| `docs/competitors/raw/_operations_matrix.json` / `.md` | матрица «операция × проект» + топ-файлы |
| `docs/competitors/operations_detail.md` | подробное читаемое приложение по операциям |
| `docs/competitors/competitor_audit.json` | краткая структурированная версия + сравнение с моим проектом |
| `docs/competitors/competitor_audit_report.md` | этот отчёт |
| `tools/diagnostics/audit_competitors.py` | сканер (инвентарь + символы + операции) |
| `tools/diagnostics/merge_competitor_audit.py` | сводные матрицы |
| `tools/diagnostics/gen_operations_detail.py` | генератор приложения |
