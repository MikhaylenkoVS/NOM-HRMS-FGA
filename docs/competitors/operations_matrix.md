# Матрица операций: попадания по проектам

Числа — количество вхождений ключевых слов операции в исходный код (без фильтрации и без «избранного»). Прочерк — нет попаданий.

| Операция | corems | formultitude | icbmocean | mfassignr | msdial | mzmine | nomspectra | openms | pyc2mc | ume | xcms |
|---|---|---|---|---|---|---|---|---|---|---|---|
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

## Топ-файлы по операциям и проектам

### raw_vendor_io

* **corems** — 210 попаданий в 31 файлах; например: `conftest.py`, `corems/encapsulation/constant.py`, `corems/mass_spectra/factory/chromat_data.py`, `corems/mass_spectra/factory/lc_class.py`
* **formultitude** — 31 попаданий в 5 файлах; например: `CiaUi/FormultitudeUIForm.cs`, `FileReader/FileReader.cs`, `Support/CFileReader.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.Designer.cs`
* **msdial** — 416 попаданий в 70 файлах; например: `src/Common/ChartDrawing/Chart/MultiAreaChartControl.cs`, `src/Common/ChartDrawing/Chart/MultiLineChartControl.cs`, `src/Common/CommonStandard/Components/Chromatogram.cs`, `src/Common/CommonStandard/DataObj/RawDataMetadata.cs`
* **mzmine** — 1926 попаданий в 353 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/AbundanceMeasure.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/ImagingRawDataFile.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/ImagingScan.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/RawDataFile.java`
* **openms** — 4088 попаданий в 377 файлах; например: `doc/code_examples/Tutorial_FeatureFinder.cpp`, `doc/code_examples/Tutorial_FileIO.cpp`, `doc/code_examples/Tutorial_FileIO_Consumer.cpp`, `doc/code_examples/Tutorial_FileIO_mzML.cpp`
* **pyc2mc** — 12 попаданий в 5 файлах; например: `Image.py`, `main.py`, `modules/pyc2mc_ui.py`, `src/loading/loading_function.py`
* **ume** — 9 попаданий в 5 файлах; например: `R/calc_recalibrate_ms.R`, `R/classify_files.R`, `R/extract_aquisition_params.R`, `R/extract_aquisition_params_from_folder.R`
* **xcms** — 55 попаданий в 19 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/XcmsExperiment-plotting.R`, `R/XcmsExperiment.R`

### transient_ft

* **corems** — 448 попаданий в 32 файлах; например: `conftest.py`, `corems/encapsulation/factory/parameters.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/encapsulation/input/parameter_from_json.py`
* **formultitude** — 1 попаданий в 1 файлах; например: `CIA/FormultitudeProgram.cs`
* **msdial** — 19 попаданий в 12 файлах; например: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `src/Common/NCDK.Display/Renderers/Generators/Standards/StandardSgroupGenerator.cs`, `src/Common/NCDK/Fingerprints/CircularFingerprinter.cs`, `src/Common/NCDK/Fingerprints/Model/Bayesian.cs`
* **mzmine** — 99 попаданий в 31 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/identities/iontype/IonPartReference.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/chartutils/ColoredBubbleDatasetRenderer.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/framework/strokechooser/JStrokeChooserDialog.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/framework/strokechooser/SettingsBasicStroke.java`
* **nomspectra** — 2 попаданий в 1 файлах; например: `nomspectra/diff.py`
* **openms** — 469 попаданий в 86 файлах; например: `src/openms/extern/GTE/Mathematics/ApprPolynomial2.h`, `src/openms/extern/GTE/Mathematics/ApprPolynomial3.h`, `src/openms/extern/GTE/Mathematics/ApprPolynomial4.h`, `src/openms/extern/GTE/Mathematics/PdeFilter.h`
* **pyc2mc** — 1 попаданий в 1 файлах; например: `modules/pyc2mc_ui.py`
* **ume** — 177 попаданий в 26 файлах; например: `R/as_peaklist.R`, `R/assign_formulas.R`, `R/calc_data_summary.R`, `R/calc_eval_params.R`
* **xcms** — 8 попаданий в 5 файлах; например: `R/DataClasses.R`, `R/do_findChromPeaks-functions.R`, `R/functions-utils.R`, `R/functions-xcmsSet.R`

### profile_preprocessing

* **corems** — 457 попаданий в 35 файлах; например: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Calc.py`
* **formultitude** — 11 попаданий в 4 файлах; например: `FindChains/FindChainsForm.cs`, `FindChainsTest/FindChainsTestProgram.cs`, `Support/CChainBlocks.cs`, `TestFSDBSearch/TotalSupport/ttlStat.cs`
* **icbmocean** — 1 попаданий в 1 файлах; например: `fastjoin.R`
* **mfassignr** — 7 попаданий в 4 файлах; например: `MFAssignR/R/HistNoise.R`, `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/RecalFunctions.R`, `Supplemental MFAssign Scripts/Background Subtraction Guidelines.R`
* **msdial** — 4681 попаданий в 274 файлах; например: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/MsScanMatchingBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/DataStructure/PriorityQueueBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Tests.cs`
* **mzmine** — 1798 попаданий в 362 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/javafx/util/FxIconUtil.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/FeatureDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/FeatureFullDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/IonTimeSeriesUtils.java`
* **nomspectra** — 27 попаданий в 3 файлах; например: `nomspectra/recal.py`, `nomspectra/spectra.py`, `nomspectra/spectrum.py`
* **openms** — 2802 попаданий в 417 файлах; например: `doc/code_examples/Tutorial_AASequence.cpp`, `doc/code_examples/Tutorial_Element.cpp`, `doc/code_examples/Tutorial_EmpiricalFormula.cpp`, `doc/code_examples/Tutorial_GaussFilter.cpp`
* **pyc2mc** — 17 попаданий в 5 файлах; например: `modules/comparison.py`, `modules/data_views.py`, `modules/molecular_maps.py`, `modules/pyc2mc_ui.py`
* **ume** — 20 попаданий в 7 файлах; например: `R/calc_data_summary.R`, `R/calc_eval_params.R`, `R/color.palette.R`, `R/create_time_flattened_mfd.R`
* **xcms** — 223 попаданий в 21 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment.R`

### peak_picking_centroiding

* **corems** — 972 попаданий в 44 файлах; например: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`
* **formultitude** — 27 попаданий в 4 файлах; например: `CiaUi/FormultitudeUIForm.cs`, `FileReader/FileReader.cs`, `Support/CFileReader.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.cs`
* **mfassignr** — 2 попаданий в 1 файлах; например: `MFAssignR/R/HistNoise.R`
* **msdial** — 1088 попаданий в 174 файлах; например: `src/Common/ChartDrawing/DrawVisual/DrawVisualManualPeakModification.cs`, `src/Common/ChartDrawing/Legacy/ChromatogramXicViewModel.cs`, `src/Common/CommonStandard/Algorithm/PeakPick/SpectralCentroiding.cs`, `src/Common/CommonStandard/Components/Chromatogram.cs`
* **mzmine** — 1072 попаданий в 226 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureStatus.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MassSpectrum.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MassSpectrumType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/RawDataFile.java`
* **openms** — 2823 попаданий в 317 файлах; например: `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/GTE/Mathematics/AdaptiveSkeletonClimbing3.h`, `src/openms/extern/GTE/Mathematics/ContEllipsoid3MinCR.h`, `src/openms/extern/GTE/Mathematics/DistTetrahedron3Tetrahedron3.h`
* **pyc2mc** — 1 попаданий в 1 файлах; например: `src/loading/loading_function.py`
* **xcms** — 333 попаданий в 38 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/MsExperiment-functions.R`

### noise_estimation

* **corems** — 242 попаданий в 34 файлах; например: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`
* **formultitude** — 51 попаданий в 11 файлах; например: `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `FindChains/FindChainsForm.Designer.cs`, `FindChainsTest/FindChainsTestProgram.cs`
* **mfassignr** — 40 попаданий в 6 файлах; например: `MFAssignR/R/HistNoise.R`, `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`
* **msdial** — 116 попаданий в 31 файлах; например: `src/Common/CommonStandard/Algorithm/PeakPick/NoiseEstimateParameter.cs`, `src/Common/CommonStandard/Algorithm/PeakPick/PeakPick.cs`, `src/Common/CommonStandard/Components/Chromatogram.cs`, `src/Common/CommonStandard/Components/ExtractedIonChromatogram.cs`
* **mzmine** — 635 попаданий в 106 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/impl/SimplePseudoSpectrum.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/simplechart/providers/impl/FeatureImageProvider.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/simplechart/providers/impl/series/IMSIonTraceHeatmapProvider.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/simplechart/providers/impl/spectra/CachedFrame.java`
* **nomspectra** — 11 попаданий в 2 файлах; например: `nomspectra/recal.py`, `nomspectra/spectrum.py`
* **openms** — 552 попаданий в 115 файлах; например: `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `share/OpenMS/SCRIPTS/plot_trafo.R`, `src/openms/extern/IsoSpec/IsoSpec/isoSpec++.cpp`, `src/openms/include/OpenMS/ANALYSIS/ID/BayesianProteinInferenceAlgorithm.h`
* **pyc2mc** — 1 попаданий в 1 файлах; например: `src/loading/loading_function.py`
* **ume** — 37 попаданий в 12 файлах; например: `R/calc_eval_params.R`, `R/calc_norm_int.R`, `R/calc_recalibrate_ms.R`, `R/data.R`
* **xcms** — 65 попаданий в 11 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/do_adjustRtime-functions.R`, `R/do_findChromPeaks-functions.R`

### mass_calibration

* **corems** — 378 попаданий в 33 файлах; например: `conftest.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Calc.py`
* **formultitude** — 407 попаданий в 13 файлах; например: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`
* **mfassignr** — 42 попаданий в 2 файлах; например: `MFAssignR/R/RecalFunctions.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`
* **msdial** — 128 попаданий в 36 файлах; например: `src/Common/CommonStandard/DataObj/RawMeasurement.cs`, `src/Common/CommonStandard/FormulaGenerator/Parser/FormulaResultParcer.cs`, `src/Common/CommonStandard/Mathematics/Mathematics/RegressionMathematics.cs`, `src/Common/CommonStandard/Mathematics/Statistics/StatisticsMathematics.cs`
* **mzmine** — 1433 попаданий в 161 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/IMSRawDataFile.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/AcquisitionMzRangeType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/CalibrationDateTimeType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/CalibrationUserType.java`
* **nomspectra** — 1 попаданий в 1 файлах; например: `nomspectra/recal.py`
* **openms** — 2417 попаданий в 236 файлах; например: `doc/code_examples/Tutorial_SavitzkyGolayFilter.cpp`, `share/OpenMS/SCRIPTS/InternalCalibration_Residuals.R`, `src/openms/extern/GTE/Mathematics/ACosEstimate.h`, `src/openms/extern/GTE/Mathematics/ASinEstimate.h`
* **ume** — 59 попаданий в 7 файлах; например: `R/assign_formulas.R`, `R/calc_ma.R`, `R/calc_recalibrate_ms.R`, `R/data.R`
* **xcms** — 118 попаданий в 17 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MPI.R`, `R/XcmsExperiment-functions.R`

### rt_alignment

* **corems** — 436 попаданий в 31 файлах; например: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/calc/subset.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`
* **formultitude** — 116 попаданий в 6 файлах; например: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`
* **mfassignr** — 3 попаданий в 3 файлах; например: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssign_RMD.R`, `Supplemental MFAssign Scripts/Background Subtraction Guidelines.R`
* **msdial** — 10024 попаданий в 604 файлах; например: `src/Common/ChartDrawing/Adorner/ContentAdorner.cs`, `src/Common/ChartDrawing/Base/Utility.cs`, `src/Common/ChartDrawing/Behavior/ScatterFocusBehavior.cs`, `src/Common/ChartDrawing/Chart/Annotator.cs`
* **mzmine** — 1398 попаданий в 478 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/FilterableListView.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxComboBox.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxLabels.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxListViews.java`
* **openms** — 2302 попаданий в 372 файлах; например: `doc/code_examples/Tutorial_MSExperiment.cpp`, `doc/code_examples/Tutorial_MapAlignment.cpp`, `doc/code_examples/Tutorial_Precursor.cpp`, `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`
* **pyc2mc** — 477 попаданий в 7 файлах; например: `modules/comparison.py`, `modules/molecular_maps.py`, `modules/plots.py`, `modules/pyc2mc_ui.py`
* **ume** — 31 попаданий в 4 файлах; например: `R/calc_recalibrate_ms.R`, `R/create_time_flattened_mfd.R`, `R/remove_blanks.R`, `R/uplot_lcms.R`
* **xcms** — 897 попаданий в 53 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/MPI.R`

### chromatographic_features

* **corems** — 2263 попаданий в 31 файлах; например: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/calc/subset.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`
* **msdial** — 11267 попаданий в 676 файлах; например: `src/Common/ChartDrawing/Base/BasicClass.cs`, `src/Common/ChartDrawing/Base/Utility.cs`, `src/Common/ChartDrawing/DrawVisual/DrawVisual.cs`, `src/Common/ChartDrawing/DrawVisual/DrawVisualManualPeakModification.cs`
* **mzmine** — 26655 попаданий в 1976 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/javafx/util/FxIcons.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/AbundanceMeasure.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureInformation.java`
* **nomspectra** — 1 попаданий в 1 файлах; например: `nomspectra/spectra.py`
* **openms** — 23341 попаданий в 971 файлах; например: `cmake/Windows/Contrib/Inetc/inetc.cpp`, `doc/code_examples/Tutorial_FeatureFinder.cpp`, `doc/code_examples/Tutorial_FeatureMap.cpp`, `doc/code_examples/Tutorial_FileIO.cpp`
* **ume** — 62 попаданий в 6 файлах; например: `R/as_ume_matrix.R`, `R/calc_logratio.R`, `R/tools.R`, `R/uplot_cluster.R`
* **xcms** — 3129 попаданий в 57 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/MPI.R`

### gap_filling

* **corems** — 33 попаданий в 4 файлах; например: `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `support_code/nmdc/metabolomics/metabolomics_collection.py`
* **msdial** — 246 попаданий в 52 файлах; например: `src/Common/ChartDrawing/Legacy/ChromatogramBean.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdial.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialGcms.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialLcms.cs`
* **mzmine** — 296 попаданий в 74 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/FeatureFullDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/MissingValueType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/gapfilling/GapFillMzMatchDuplicateType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/statistics/DataTableProcessingHistory.java`
* **openms** — 59 попаданий в 24 файлах; например: `src/openms/include/OpenMS/ANALYSIS/ID/IDBoostGraph.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/ConfidenceScoring.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/MasstraceCorrelator.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/OpenSwathExportData.h`
* **ume** — 8 попаданий в 6 файлах; например: `R/assign_formulas.R`, `R/check_objects.R`, `R/create_time_flattened_mfd.R`, `R/search_mf_targets.R`
* **xcms** — 217 попаданий в 34 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MPI.R`, `R/MsExperiment-functions.R`

### isotope_detection

* **corems** — 392 попаданий в 23 файлах; например: `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/lc_calc.py`
* **formultitude** — 272 попаданий в 17 файлах; например: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.cs`
* **icbmocean** — 22 попаданий в 2 файлах; например: `create_homologous_series_network.R`, `isotope_ratio_deviance_function.R`
* **mfassignr** — 1112 попаданий в 11 файлах; например: `MFAssignR/R/FindCoreFormulae2.R`, `MFAssignR/R/FindCoreFormulae2_Halogen.R`, `MFAssignR/R/IsoFiltR.R`, `MFAssignR/R/MFAssign.R`
* **msdial** — 7795 попаданий в 400 файлах; например: `src/Common/CommonStandard/Algorithm/Function/SpectrumHandler.cs`, `src/Common/CommonStandard/Algorithm/IsotopeCalc/IsotopeCalc.cs`, `src/Common/CommonStandard/Algorithm/Scoring/MsScanMatching.cs`, `src/Common/CommonStandard/Alignment/AlignedPeakPropertyBean.cs`
* **mzmine** — 3564 попаданий в 325 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/IsotopePattern.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MergedMassSpectrum.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/Feature.java`
* **nomspectra** — 71 попаданий в 5 файлах; например: `nomspectra/brutto.py`, `nomspectra/diff.py`, `nomspectra/gui.py`, `nomspectra/gui_design.py`
* **openms** — 6010 попаданий в 420 файлах; например: `cmake/Windows/Contrib/Inetc/inetc.cpp`, `cmake/Windows/Contrib/Inetc/resource.h`, `doc/code_examples/Tutorial_AASequence.cpp`, `doc/code_examples/Tutorial_Element.cpp`
* **pyc2mc** — 107 попаданий в 14 файлах; например: `Image.py`, `main.py`, `modules/comparison.py`, `modules/file_operations.py`
* **ume** — 442 попаданий в 29 файлах; например: `R/assign_formulas.R`, `R/build_isotope_map.R`, `R/calc_dbe.R`, `R/calc_eval_params.R`
* **xcms** — 250 попаданий в 28 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment.R`

### adduct_ion_identity

* **corems** — 303 попаданий в 22 файлах; например: `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/andiNetCDF.py`
* **formultitude** — 203 попаданий в 9 файлах; например: `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`
* **mfassignr** — 367 попаданий в 10 файлах; например: `MFAssignR/R/FindCoreFormulae2.R`, `MFAssignR/R/FindCoreFormulae2_Halogen.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`
* **msdial** — 16395 попаданий в 650 файлах; например: `src/Common/ChartDrawing/Helper/ExpressionHelper.cs`, `src/Common/ChartDrawing/IO/XamlToys.cs`, `src/Common/CommonMVVM/ChemView/ChemOntologyColor.cs`, `src/Common/CommonMVVM/Converter/AdductIonConverter.cs`
* **mzmine** — 2098 попаданий в 416 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/FilterableListView.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxListViews.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/MenuItems.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/dialogs/FilterableMenuPopup.java`
* **openms** — 3203 попаданий в 301 файлах; например: `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/GTE/Mathematics/IndexAttribute.h`, `src/openms/extern/GTE/Mathematics/Quaternion.h`, `src/openms/extern/GTE/Mathematics/VertexAttribute.h`
* **pyc2mc** — 45 попаданий в 4 файлах; например: `main.py`, `modules/pyc2mc_ui.py`, `modules/ui_main.py`, `src/pyc2mc_ui.py`
* **ume** — 4 попаданий в 2 файлах; например: `R/calc_recalibrate_ms.R`, `R/search_mf_targets.R`
* **xcms** — 74 попаданий в 5 файлах; например: `R/DataClasses.R`, `R/do_findChromPeaks-functions.R`, `R/methods-IO.R`, `R/methods-group-features.R`

### charge_state

* **corems** — 42 попаданий в 15 файлах; например: `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectrum/factory/MassSpectrumClasses.py`
* **formultitude** — 33 попаданий в 6 файлах; например: `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`, `TestFSDBSearch/Form1.cs`
* **icbmocean** — 2 попаданий в 2 файлах; например: `fastjoin.R`, `precisejoin.R`
* **mfassignr** — 22 попаданий в 6 файлах; например: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`
* **msdial** — 1231 попаданий в 359 файлах; например: `src/Common/ChartDrawing/Chart/HeatmapControl.cs`, `src/Common/CommonStandard/Algorithm/Function/SpectrumHandler.cs`, `src/Common/CommonStandard/Algorithm/Scoring/MsScanMatching.cs`, `src/Common/CommonStandard/Components/Chromatogram.cs`
* **mzmine** — 5315 попаданий в 3938 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/gui/DefaultHeadlessDesktop.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/Desktop.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/DesktopService.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/JavaFxDesktop.java`
* **nomspectra** — 21 попаданий в 3 файлах; например: `nomspectra/gui.py`, `nomspectra/gui_design.py`, `nomspectra/spectrum.py`
* **openms** — 4557 попаданий в 848 файлах; например: `doc/code_examples/Tutorial_AASequence.cpp`, `doc/code_examples/Tutorial_MSSpectrum.cpp`, `doc/code_examples/Tutorial_ProForma.cpp`, `src/openms/extern/GTE/Mathematics/AdaptiveSkeletonClimbing3.h`
* **pyc2mc** — 6 попаданий в 3 файлах; например: `src/processing/merge_function.py`, `src/processing/merge_unattributed.py`, `src/stats/PCA_function.py`
* **ume** — 14 попаданий в 9 файлах; например: `R/assign_formulas.R`, `R/check_neutral_mf.R`, `R/check_objects.R`, `R/data.R`
* **xcms** — 388 попаданий в 38 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MPI.R`, `R/MsExperiment-functions.R`

### formula_assignment

* **corems** — 860 попаданий в 39 файлах; например: `conftest.py`, `corems/encapsulation/constant.py`, `corems/encapsulation/factory/parameters.py`, `corems/encapsulation/factory/processingSetting.py`
* **formultitude** — 43 попаданий в 7 файлах; например: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`
* **icbmocean** — 1 попаданий в 1 файлах; например: `create_homologous_series_network.R`
* **mfassignr** — 44 попаданий в 11 файлах; например: `MFAssignR/R/IsoFiltR.R`, `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`
* **msdial** — 6504 попаданий в 476 файлах; например: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `src/Common/CommonStandard/Algorithm/Function/SpectrumHandler.cs`, `src/Common/CommonStandard/Algorithm/IsotopeCalc/IsotopeCalc.cs`, `src/Common/CommonStandard/Algorithm/PeakPick/PeakPick.cs`
* **mzmine** — 1749 попаданий в 256 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MZmineProject.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureListRow.java`
* **nomspectra** — 69 попаданий в 6 файлах; например: `nomspectra/brutto.py`, `nomspectra/diff.py`, `nomspectra/draw.py`, `nomspectra/gui.py`
* **openms** — 2748 попаданий в 282 файлах; например: `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/GTE/Mathematics/ApprCylinder3.h`, `src/openms/extern/GTE/Mathematics/ApprQuadratic2.h`, `src/openms/extern/GTE/Mathematics/ApprQuadratic3.h`
* **pyc2mc** — 261 попаданий в 19 файлах; например: `main.py`, `modules/comparison.py`, `modules/data_views.py`, `modules/molecular_maps.py`
* **ume** — 335 попаданий в 53 файлах; например: `R/add_known_mf.R`, `R/as_mfd.R`, `R/as_peaklist.R`, `R/as_ume_matrix.R`
* **xcms** — 22 попаданий в 6 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/XcmsExperiment-functions.R`, `R/functions-XCMSnExp.R`

### formula_scoring

* **corems** — 211 попаданий в 30 файлах; например: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/MZSearch.py`
* **formultitude** — 76 попаданий в 13 файлах; например: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`
* **mfassignr** — 24 попаданий в 7 файлах; например: `MFAssignR/R/IsoFiltR.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`
* **msdial** — 2956 попаданий в 340 файлах; например: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/MsScanMatchingBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/DataStructure/PriorityQueueBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Program.cs`
* **mzmine** — 2038 попаданий в 422 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxTextFlows.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/util/FxLayout.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/dialogs/FilterableMenuPopup.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/mvci/LatestTaskScheduler.java`
* **nomspectra** — 44 попаданий в 6 файлах; например: `nomspectra/diff.py`, `nomspectra/draw.py`, `nomspectra/gui.py`, `nomspectra/gui_design.py`
* **openms** — 6287 попаданий в 618 файлах; например: `doc/code_examples/Tutorial_IdentificationClasses.cpp`, `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `share/OpenMS/SCRIPTS/InternalCalibration_Residuals.R`, `src/openms/extern/GTE/Mathematics/IncrementalDelaunay2.h`
* **pyc2mc** — 12 попаданий в 7 файлах; например: `modules/file_operations.py`, `modules/plot_helpers.py`, `modules/plots.py`, `modules/pyc2mc_ui.py`
* **ume** — 144 попаданий в 24 файлах; например: `R/as_mfd.R`, `R/assign_formulas.R`, `R/build_isotope_map.R`, `R/calc_data_summary.R`
* **xcms** — 370 попаданий в 41 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/MsExperiment.R`

### ambiguity_handling

* **corems** — 40 попаданий в 5 файлах; например: `corems/encapsulation/constant.py`, `corems/mass_spectrum/calc/Calibration.py`, `corems/mass_spectrum/calc/MassSpectrumCalc.py`, `corems/mass_spectrum/output/export.py`
* **mfassignr** — 174 попаданий в 5 файлах; например: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`
* **msdial** — 54 попаданий в 23 файлах; например: `src/Common/CommonStandard/DataObj/Result/MsScanMatchResult.cs`, `src/Common/CommonStandard/Lipidomics/LipidomicsConverter.cs`, `src/Common/CommonStandard/Lipidomics/LipoqualityDatabaseManagerUtility.cs`, `src/Common/NCDK.Display/Depict/DepictionGenerator.cs`
* **mzmine** — 15 попаданий в 11 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/correlation/RowGroup.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/engine/ElementAutoDetector.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_compoundgrouper/CompoundGrouperParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_compoundgrouper/SimpleSeederComponentizer.java`
* **nomspectra** — 33 попаданий в 5 файлах; например: `nomspectra/diff.py`, `nomspectra/draw.py`, `nomspectra/gui.py`, `nomspectra/recal.py`
* **openms** — 1372 попаданий в 256 файлах; например: `src/openms/extern/GTE/Mathematics/AdaptiveSkeletonClimbing2.h`, `src/openms/extern/GTE/Mathematics/AdaptiveSkeletonClimbing3.h`, `src/openms/extern/GTE/Mathematics/MarchingCubes.h`, `src/openms/extern/GTE/Mathematics/SurfaceExtractorCubes.h`
* **ume** — 2 попаданий в 2 файлах; например: `R/get_isotope_info.R`, `R/tools.R`

### chemical_rules

* **corems** — 102 попаданий в 12 файлах; например: `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectrum/output/export.py`
* **formultitude** — 26 попаданий в 5 файлах; например: `CIA/FormultitudeProgram.cs`, `CiaUi/FormultitudeUIForm.cs`, `Support/CIsotope.cs`, `TestFSDBSearch/TotalSupport/CannonMF.cs`
* **mfassignr** — 232 попаданий в 7 файлах; например: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`
* **msdial** — 656 попаданий в 85 файлах; например: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/MsScanMatchingBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/DataStructure/PriorityQueueBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Program.cs`
* **mzmine** — 281 попаданий в 50 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/RdbeType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/formula/FormulaListType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/iin/IonIdentityListType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/identities/MolecularFormulaIdentity.java`
* **nomspectra** — 46 попаданий в 3 файлах; например: `nomspectra/brutto.py`, `nomspectra/gui_design.py`, `nomspectra/spectrum.py`
* **openms** — 67 попаданий в 15 файлах; например: `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/include/OpenMS/ANALYSIS/ID/ProSEAlgorithm.h`, `src/openms/include/OpenMS/ANALYSIS/QUANTITATION/PeptideAndProteinQuant.h`, `src/openms/include/OpenMS/ANALYSIS/TOPDOWN/SpectralDeconvolution.h`
* **pyc2mc** — 369 попаданий в 14 файлах; например: `Image.py`, `main.py`, `modules/comparison.py`, `modules/data_views.py`
* **ume** — 110 попаданий в 16 файлах; например: `R/calc_data_summary.R`, `R/calc_dbe.R`, `R/calc_eval_params.R`, `R/check_neutral_mf.R`

### halogen_support

* **corems** — 485 попаданий в 50 файлах; например: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`
* **formultitude** — 122 попаданий в 17 файлах; например: `CIA/FormultitudeProgram.cs`, `CiaUi/FormultitudeUIForm.cs`, `FileReader/FileReader.cs`, `FindChains/FindChainsForm.cs`
* **icbmocean** — 2 попаданий в 2 файлах; например: `ResPow_outlier.R`, `create_homologous_series_network.R`
* **mfassignr** — 336 попаданий в 9 файлах; например: `MFAssignR/R/FindCoreFormulae2.R`, `MFAssignR/R/FindCoreFormulae2_Halogen.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`
* **msdial** — 4903 попаданий в 1039 файлах; например: `src/Common/ChartDrawing/AxisManager/Generic/CategoryAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/PercentLabelGenerator.cs`, `src/Common/ChartDrawing/Behavior/ItemSelectBehavior.cs`, `src/Common/ChartDrawing/Chart/BarControl.cs`
* **mzmine** — 13818 попаданий в 3951 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/gui/DefaultHeadlessDesktop.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/Desktop.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/DesktopService.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/JavaFxDesktop.java`
* **nomspectra** — 25 попаданий в 6 файлах; например: `nomspectra/brutto.py`, `nomspectra/diff.py`, `nomspectra/gui.py`, `nomspectra/recal.py`
* **openms** — 27342 попаданий в 3336 файлах; например: `cmake/Windows/Contrib/Inetc/afxres.h`, `cmake/Windows/Contrib/Inetc/crt.cpp`, `cmake/Windows/Contrib/Inetc/inetc.cpp`, `cmake/Windows/Contrib/Inetc/nsis_tchar.h`
* **pyc2mc** — 324 попаданий в 18 файлах; например: `Image.py`, `main.py`, `modules/comparison.py`, `modules/data_views.py`
* **ume** — 67 попаданий в 25 файлах; например: `R/as_peaklist.R`, `R/calc_data_summary.R`, `R/calc_dbe.R`, `R/calc_eval_params.R`
* **xcms** — 745 попаданий в 87 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MPI.R`, `R/MsExperiment-functions.R`

### internal_recalibration_series

* **formultitude** — 8 попаданий в 5 файлах; например: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.cs`, `TestFSDBSearch/Form1.cs`
* **icbmocean** — 1 попаданий в 1 файлах; например: `create_homologous_series_network.R`
* **mfassignr** — 43 попаданий в 2 файлах; например: `MFAssignR/R/RecalFunctions.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`
* **mzmine** — 1 попаданий в 1 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/gui/preferences/VendorImportParameters.java`
* **openms** — 75 попаданий в 17 файлах; например: `src/openms/include/OpenMS/ANALYSIS/QUANTITATION/DDAWorkflowCommons.h`, `src/openms/include/OpenMS/FORMAT/HANDLERS/AcqusHandler.h`, `src/openms/include/OpenMS/PROCESSING/CALIBRATION/InternalCalibration.h`, `src/openms/source/ANALYSIS/QUANTITATION/DDAWorkflowCommons.cpp`

### kendrick

* **corems** — 198 попаданий в 12 файлах; например: `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectrum/calc/KendrickGroup.py`, `corems/mass_spectrum/factory/MassSpectrumClasses.py`, `corems/molecular_formula/calc/MolecularFormulaCalc.py`
* **formultitude** — 42 попаданий в 5 файлах; например: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.cs`
* **icbmocean** — 1 попаданий в 1 файлах; например: `create_homologous_series_network.R`
* **mfassignr** — 111 попаданий в 7 файлах; например: `MFAssignR/R/IsoFiltR.R`, `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`
* **msdial** — 8 попаданий в 4 файлах; например: `src/MSDIAL5/MsdialGuiApp/Model/DataObj/AlignmentSpotPropertyModel.cs`, `src/MSDIAL5/MsdialGuiApp/Model/DataObj/ChromatogramPeakFeatureModel.cs`, `src/MSDIAL5/MsdialGuiApp/Model/Dims/DimsAlignmentModel.cs`, `src/MSDIAL5/MsdialGuiApp/Model/Dims/DimsAnalysisModel.cs`
* **mzmine** — 637 попаданий в 60 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/ArticleReferences.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/chartutils/ColoredBubbleDatasetRenderer.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/chartutils/XYBlockPixelSizePaintScales.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/mainwindow/workspace/AbstractWorkspace.java`
* **nomspectra** — 12 попаданий в 2 файлах; например: `nomspectra/gui_design.py`, `nomspectra/spectrum.py`
* **openms** — 1 попаданий в 1 файлах; например: `src/openms/include/OpenMS/FEATUREFINDER/FeatureFindingMetabo.h`
* **pyc2mc** — 436 попаданий в 9 файлах; например: `main.py`, `modules/comparison.py`, `modules/data_views.py`, `modules/file_operations.py`
* **ume** — 36 попаданий в 8 файлах; например: `R/as_mfd.R`, `R/calc_eval_params.R`, `R/create_time_flattened_mfd.R`, `R/data.R`

### descriptors

* **corems** — 66 попаданий в 7 файлах; например: `corems/mass_spectrum/factory/MassSpectrumClasses.py`, `corems/mass_spectrum/input/coremsHDF5.py`, `corems/mass_spectrum/input/massList.py`, `corems/mass_spectrum/output/export.py`
* **formultitude** — 2 попаданий в 2 файлах; например: `CiaUi/FormultitudeUIForm.Designer.cs`, `TestFSDBSearch/Form1.cs`
* **mfassignr** — 26 попаданий в 4 файлах; например: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`
* **msdial** — 2847 попаданий в 233 файлах; например: `src/Common/CommonMVVM/ChemView/ChemOntologyColor.cs`, `src/Common/CommonStandard/DataObj/NodeEdge/MolecularNetworkObj.cs`, `src/Common/CommonStandard/Lipidomics/LipidEieioMsmsCharacterization.cs`, `src/Common/CommonStandard/Lipidomics/LipidOadMsmsCharacterization.cs`
* **mzmine** — 167 попаданий в 32 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/compounddb/MolecularClassType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/structures/HarmonizationOptions.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/structures/StructureHarmonizer.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/structures/StructureUtils.java`
* **nomspectra** — 112 попаданий в 6 файлах; например: `nomspectra/brutto.py`, `nomspectra/draw.py`, `nomspectra/gui.py`, `nomspectra/gui_design.py`
* **openms** — 110 попаданий в 47 файлах; например: `src/openms/extern/GTE/Mathematics/ApprCone3.h`, `src/openms/extern/GTE/Mathematics/HashCombine.h`, `src/openms/extern/GTE/Mathematics/MinimumAreaBox2.h`, `src/openms/extern/GTE/Mathematics/MinimumWidthPoints2.h`
* **pyc2mc** — 236 попаданий в 15 файлах; например: `Image.py`, `main.py`, `modules/comparison.py`, `modules/data_views.py`
* **ume** — 74 попаданий в 17 файлах; например: `R/calc_data_summary.R`, `R/calc_eval_params.R`, `R/create_time_flattened_mfd.R`, `R/create_ume_formula_library.R`
* **xcms** — 4 попаданий в 3 файлах; например: `src/fastMatch.c`, `src/massifquant/TrMgr.cpp`, `src/massifquant/TrMgr.h`

### similarity

* **corems** — 428 попаданий в 28 файлах; например: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`
* **msdial** — 4178 попаданий в 277 файлах; например: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `src/Common/ChartDrawing/Legacy/ChromatogramBean.cs`, `src/Common/CommonStandard/Algorithm/CowAlignment/CowAlignment.cs`, `src/Common/CommonStandard/Algorithm/Function/FrameBinnedSpectrum.cs`
* **mzmine** — 2781 попаданий в 358 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxPopOvers.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/formatters/FormatDoubleRangeStringConverter.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/formatters/FormatDoubleStringConverter.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/util/color/ColorsFX.java`
* **nomspectra** — 25 попаданий в 4 файлах; например: `nomspectra/gui.py`, `nomspectra/gui_design.py`, `nomspectra/spectra.py`, `nomspectra/spectrum.py`
* **openms** — 1581 попаданий в 276 файлах; например: `doc/code_examples/Tutorial_Clustering.cpp`, `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/GTE/Mathematics/ContLozenge3.h`, `src/openms/extern/GTE/Mathematics/DistCircle3Circle3.h`
* **ume** — 6 попаданий в 2 файлах; например: `R/calc_indeces.R`, `R/uplot_cluster.R`
* **xcms** — 173 попаданий в 19 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MsExperiment-functions.R`, `R/XcmsExperiment-functions.R`

### statistics

* **corems** — 641 попаданий в 14 файлах; например: `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`, `corems/mass_spectra/calc/lc_calc.py`
* **formultitude** — 199 попаданий в 4 файлах; например: `FindChains/FindChainsForm.cs`, `FindChainsTest/FindChainsTestProgram.cs`, `Support/CChainBlocks.cs`, `Support/CFileReader.cs`
* **icbmocean** — 2 попаданий в 1 файлах; например: `fastjoin.R`
* **msdial** — 377 попаданий в 66 файлах; например: `src/Common/CommonMVVM/ChemView/ChemOntologyColor.cs`, `src/Common/CommonStandard/Alignment/AlignmentPropertyBean.cs`, `src/Common/CommonStandard/DataObj/NodeEdge/MolecularNetworkObj.cs`, `src/Common/CommonStandard/Enum/CommonEnums.cs`
* **mzmine** — 1067 попаданий в 173 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/CompoundNameIdentifier.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/DataTypes.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/GNPSClusterUrlType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/GNPSSpectralLibraryMatchesType.java`
* **openms** — 2206 попаданий в 159 файлах; например: `doc/code_examples/Tutorial_Clustering.cpp`, `doc/code_examples/Tutorial_MapAlignment.cpp`, `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `doc/doxygen/parameters/TOPPDocumenter.cpp`
* **pyc2mc** — 90 попаданий в 11 файлах; например: `main.py`, `modules/controller_dependencies.py`, `modules/data_views.py`, `modules/plots.py`
* **ume** — 38 попаданий в 5 файлах; например: `R/calc_logratio.R`, `R/main_docu.R`, `R/tools.R`, `R/uplot_cluster.R`
* **xcms** — 40 попаданий в 12 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/do_groupChromPeaks-functions.R`

### visualization

* **corems** — 296 попаданий в 23 файлах; например: `conftest.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`
* **formultitude** — 69 попаданий в 3 файлах; например: `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.Designer.cs`
* **icbmocean** — 13 попаданий в 2 файлах; например: `ResPow_outlier.R`, `isotope_ratio_deviance_function.R`
* **mfassignr** — 67 попаданий в 8 файлах; например: `MFAssignR/R/HistNoise.R`, `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`
* **msdial** — 3594 попаданий в 548 файлах; например: `src/Common/ChartDrawing/Adorner/ChartSelectionRubberAdorner.cs`, `src/Common/ChartDrawing/Adorner/RangeSelectAdorner.cs`, `src/Common/ChartDrawing/Adorner/ScatterFocusAdorner.cs`, `src/Common/ChartDrawing/AxisManager/FreezableAxisManager.cs`
* **mzmine** — 9197 попаданий в 671 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/impl/IonMobilogramTimeSeriesFactory.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeature.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/annotationpriority/AnnotationSummary.java`
* **nomspectra** — 122 попаданий в 6 файлах; например: `nomspectra/draw.py`, `nomspectra/gui.py`, `nomspectra/gui_design.py`, `nomspectra/recal.py`
* **openms** — 1349 попаданий в 207 файлах; например: `cmake/Windows/Contrib/Inetc/inetc.cpp`, `cmake/Windows/Contrib/Inetc/pluginapi.c`, `share/OpenMS/SCRIPTS/InternalCalibration_Models.R`, `share/OpenMS/SCRIPTS/InternalCalibration_Residuals.R`
* **pyc2mc** — 380 попаданий в 13 файлах; например: `main.py`, `modules/comparison.py`, `modules/molecular_maps.py`, `modules/plot_helpers.py`
* **ume** — 141 попаданий в 32 файлах; например: `R/calc_eval_params.R`, `R/calc_recalibrate_ms.R`, `R/data.R`, `R/export_ume_results.R`
* **xcms** — 279 попаданий в 35 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/XcmsExperiment-plotting.R`

### msms

* **corems** — 966 попаданий в 23 файлах; например: `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/parameters.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/MZSearch.py`
* **formultitude** — 4 попаданий в 2 файлах; например: `TestFSDBSearch/TotalSupport/CannonMF.cs`, `TestFSDBSearch/TotalSupport/ttlAI.cs`
* **mfassignr** — 12 попаданий в 4 файлах; например: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`
* **msdial** — 17658 попаданий в 780 файлах; например: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `src/Common/ChartDrawing/Base/Utility.cs`, `src/Common/ChartDrawing/Legacy/ChromatogramBean.cs`, `src/Common/CommonMVVM/Converter/MethodTypeDdMsmsEnumToBoolConverter.cs`
* **mzmine** — 11037 попаданий в 785 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/ArticleReferences.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/util/color/ColorsFX.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/Frame.java`
* **openms** — 16890 попаданий в 669 файлах; например: `doc/code_examples/Tutorial_FileIO.cpp`, `doc/code_examples/Tutorial_MSChromatogram.cpp`, `doc/code_examples/Tutorial_MSExperiment.cpp`, `doc/code_examples/Tutorial_Precursor.cpp`
* **pyc2mc** — 1 попаданий в 1 файлах; например: `Image.py`
* **ume** — 1 попаданий в 1 файлах; например: `R/calc_isotope_pattern.R`
* **xcms** — 280 попаданий в 23 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MsExperiment-functions.R`, `R/MsExperiment.R`

### ion_mobility_ccs

* **formultitude** — 2 попаданий в 1 файлах; например: `TestFSDBSearch/TotalSupport/ttlAI.cs`
* **msdial** — 4436 попаданий в 264 файлах; например: `src/Common/CommonStandard/Algorithm/Scoring/MsScanMatching.cs`, `src/Common/CommonStandard/Algorithm/Scoring/RetentionMatchPolicy.cs`, `src/Common/CommonStandard/Alignment/AlignedPeakPropertyBean.cs`, `src/Common/CommonStandard/Alignment/AlignmentPropertyBean.cs`
* **mzmine** — 1677 попаданий в 404 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/Frame.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MobilityScan.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MobilityType.java`
* **openms** — 2714 попаданий в 268 файлах; например: `src/openms/include/OpenMS/ANALYSIS/ID/IDBoostGraph.h`, `src/openms/include/OpenMS/ANALYSIS/ID/MetaboliteSpectralMatching.h`, `src/openms/include/OpenMS/ANALYSIS/ID/ProSEAlgorithm.h`, `src/openms/include/OpenMS/ANALYSIS/MAPMATCHING/MapAlignmentAlgorithmKD.h`
* **xcms** — 6 попаданий в 3 файлах; например: `R/functions-OnDiskMSnExp.R`, `R/methods-xcmsSet.R`, `R/plotQC.R`

### molecular_networking

* **msdial** — 27 попаданий в 16 файлах; например: `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialGcms.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialLcms.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsfinder.cs`, `src/Common/CommonStandard/Parameters/AnalysisParamOfMsfinder.cs`
* **mzmine** — 77 попаданий в 52 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/networking/NetworkStatsType.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataanalysis/spec_chimeric_precursor/HandleChimericMsMsParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataanalysis/spec_chimeric_precursor/PrecursorPurityCheckerParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/MainSpectralNetworkingModule.java`
* **openms** — 15 попаданий в 7 файлах; например: `src/openms/include/OpenMS/ANALYSIS/ID/IonIdentityMolecularNetworking.h`, `src/openms/include/OpenMS/FORMAT/GNPSMGFFile.h`, `src/openms/include/OpenMS/FORMAT/GNPSMetaValueFile.h`, `src/openms/include/OpenMS/FORMAT/GNPSQuantificationFile.h`

### qc_metrics

* **corems** — 19 попаданий в 6 файлах; например: `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectra/output/export.py`, `corems/mass_spectrum/calc/Calibration.py`
* **icbmocean** — 4 попаданий в 1 файлах; например: `isotope_ratio_deviance_function.R`
* **mfassignr** — 55 попаданий в 7 файлах; например: `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`
* **msdial** — 4176 попаданий в 247 файлах; например: `src/Common/ChartDrawing/Chart/AreaChartControl.cs`, `src/Common/ChartDrawing/Chart/BarControl.cs`, `src/Common/ChartDrawing/Chart/DendrogramControl.cs`, `src/Common/ChartDrawing/Chart/LineSpectrumControl.cs`
* **mzmine** — 972 попаданий в 336 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxTextFields.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/skins/DynamicTextFieldSkin.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/dialogs/DialogLoggerUtil.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/properties/PropertyUtils.java`
* **openms** — 2938 попаданий в 352 файлах; например: `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/SQLiteCpp/cpplint.py`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/extern/evergreen/src/Utility/graph_to_dot.hpp`
* **pyc2mc** — 4 попаданий в 2 файлах; например: `Image.py`, `modules/resources_rc.py`
* **ume** — 94 попаданий в 9 файлах; например: `R/calc_recalibrate_ms.R`, `R/classify_files.R`, `R/data.R`, `R/filter.R`
* **xcms** — 80 попаданий в 9 файлах; например: `R/AllGenerics.R`, `R/do_adjustRtime-functions.R`, `R/functions-OnDiskMSnExp.R`, `R/functions-XCMSnExp.R`

### provenance_workflow

* **corems** — 896 попаданий в 34 файлах; например: `conftest.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/lc_calc.py`
* **formultitude** — 1 попаданий в 1 файлах; например: `CIA/FormultitudeProgram.cs`
* **msdial** — 1711 попаданий в 206 файлах; например: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/MsScanMatchingBenchmark.cs`, `src/Common/ChartDrawing/Adorner/ChartSelectionRubberAdorner.cs`, `src/Common/ChartDrawing/Adorner/RangeSelectAdorner.cs`, `src/Common/ChartDrawing/Adorner/RubberAdorner.cs`
* **mzmine** — 3866 попаданий в 557 файлах; например: `javafx-framework/src/main/java/io/github/mzmine/gui/JavaFxDesktop.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/converters/OptionsStringConverter.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxComboBox.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/dialogs/DialogLoggerUtil.java`
* **nomspectra** — 142 попаданий в 7 файлах; например: `nomspectra/diff.py`, `nomspectra/draw.py`, `nomspectra/gui.py`, `nomspectra/metadata.py`
* **openms** — 4021 попаданий в 787 файлах; например: `doc/code_examples/Tutorial_IdentificationClasses.cpp`, `doc/code_examples/Tutorial_ImzMLFile.cpp`, `doc/code_examples/Tutorial_MSChromatogram.cpp`, `doc/code_examples/Tutorial_MetaInfo.cpp`
* **pyc2mc** — 3 попаданий в 1 файлах; например: `modules/resources_rc.py`
* **ume** — 25 попаданий в 9 файлах; например: `R/add_known_mf.R`, `R/assign_formulas.R`, `R/convert_data_table_to_molecular_formulas.R`, `R/convert_molecular_formula_to_data_table.R`
* **xcms** — 369 попаданий в 12 файлах; например: `R/AllGenerics.R`, `R/DataClasses.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment.R`

### io_export

* **corems** — 581 попаданий в 34 файлах; например: `corems/encapsulation/factory/processingSetting.py`, `corems/encapsulation/input/parameter_from_json.py`, `corems/encapsulation/output/parameter_to_json.py`, `corems/mass_spectra/calc/lc_calc.py`
* **formultitude** — 88 попаданий в 11 файлах; например: `CIA/FormultitudeProgram.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`, `FileReader/FileReader.cs`
* **icbmocean** — 1 попаданий в 1 файлах; например: `ResPow_outlier.R`
* **mfassignr** — 3 попаданий в 2 файлах; например: `Supplemental MFAssign Scripts/Formula Assignment Reader.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`
* **msdial** — 215 попаданий в 59 файлах; например: `src/Common/CommonStandard/Algorithm/Function/MolecularNetworkInstance.cs`, `src/Common/CommonStandard/ClassyfireApiStandard/ClassfireProtocol.cs`, `src/Common/CommonStandard/Lipidomics/LipidClassDictionary.cs`, `src/Common/CommonStandard/Lipidomics/LipidEieioMsmsCharacterization.cs`
* **mzmine** — 567 попаданий в 198 файлах; например: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/CompoundDBAnnotation.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/CompoundMemberDTO.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/CompoundMembers.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/CompoundMembersDTO.java`
* **nomspectra** — 30 попаданий в 3 файлах; например: `nomspectra/gui.py`, `nomspectra/spectra.py`, `nomspectra/spectrum.py`
* **openms** — 2336 попаданий в 170 файлах; например: `doc/code_examples/Tutorial_ProForma.cpp`, `share/OpenMS/SCRIPTS/InternalCalibration_Models.R`, `share/OpenMS/SCRIPTS/InternalCalibration_Residuals.R`, `src/openms/extern/GTE/Mathematics/Torus3.h`
* **pyc2mc** — 182 попаданий в 15 файлах; например: `main.py`, `modules/comparison.py`, `modules/data_views.py`, `modules/file_operations.py`
* **ume** — 15 попаданий в 5 файлах; например: `R/as_peaklist.R`, `R/check_objects.R`, `R/export_ume_results.R`, `R/load_ume_results.R`
* **xcms** — 64 попаданий в 8 файлах; например: `R/XcmsExperimentHdf5-functions.R`, `R/XcmsExperimentHdf5.R`, `R/databases.R`, `R/functions-XCMSnExp.R`
