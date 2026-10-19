# Дизайн: вычитание исходника из производных спектров

1. `_overlap.match_mask(deriv_mz, src_mz_sorted, ppm_tol)` — векторная маска
   совпадений: `searchsorted` + два соседа, отклонение в ppm.
2. `_overlap.subtract_matching_peaks(deriv, src, ppm_tol)` — новый `Spectrum` без
   совпавших пиков + статистика (`total`, `removed`, `kept`, `removed_frac`).
3. В `_denoise_triple` — после шумоподавления: при `subtract_source=True`
   применяется к dmet и dacet против отшумоподавлённого src.
4. Счётчики в `PipelineStats`, сообщение в лог.
