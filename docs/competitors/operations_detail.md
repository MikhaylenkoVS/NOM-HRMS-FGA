# Приложение: реализации по операциям (сырые данные, без фильтрации)

Сгенерировано из `docs/competitors/raw/*_operations.json`. Для каждой операции показаны все проекты, где встречаются соответствующие ключевые слова: число попаданий, число файлов, топ-файлы и примеры строк. Это первичный материал для доработки, а не отбор «важного».

## raw_vendor_io — Чтение сырых файлов приборов (RAW/MzML/…)

Всего попаданий по всем проектам: **6747**.

### corems — 210 попаданий в 31 файлах

Файлы: `conftest.py`, `corems/encapsulation/constant.py`, `corems/mass_spectra/factory/chromat_data.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/andiNetCDF.py`, `corems/mass_spectra/input/brukerSolarix.py`, `corems/mass_spectra/input/brukerSolarix_utils.py`, `corems/mass_spectra/input/corems_hdf5.py`, `corems/mass_spectra/input/mzml.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectrum/calc/Calibration.py`, `corems/mass_spectrum/calc/MassSpectrumCalc.py`

Примеры:

```
conftest.py:11: from corems.transient.input.brukerSolarix import ReadBrukerSolarix
conftest.py:13: from corems.mass_spectra.input.rawFileReader import ImportMassSpectraThermoMSFileReader
conftest.py:71: def mass_spectrum_ftms(bruker_transient):
conftest.py:74: mass_spectrum = bruker_transient.get_mass_spectrum(
conftest.py:97: def bruker_transient(ftms_file_location):
conftest.py:99: bruker_reader = ReadBrukerSolarix(ftms_file_location)
```

### formultitude — 31 попаданий в 5 файлах

Файлы: `CiaUi/FormultitudeUIForm.cs`, `FileReader/FileReader.cs`, `Support/CFileReader.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.Designer.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.cs`

Примеры:

```
CiaUi/FormultitudeUIForm.cs:989: //check Bruker instrument
CiaUi/FormultitudeUIForm.cs:992: if( Nodes [ 0 ].Attributes [ "appname" ].Value != "Bruker Compass DataAnalysis" ) { return; }
FileReader/FileReader.cs:67: //check Bruker instrument
FileReader/FileReader.cs:70: if( Nodes [ 0 ].Attributes [ "appname" ].Value != "Bruker Compass DataAnalysis" ) { throw new Exception( "Bruker Compass DataAnalysis" ); }
Support/CFileReader.cs:371: //check Bruker instrument
Support/CFileReader.cs:375: if (Nodes[0].Attributes["appname"].Value != "Bruker Compass DataAnalysis") { throw new Exception("Bruker Compass DataAnalysis"); }
```

### msdial — 416 попаданий в 70 файлах

Файлы: `src/Common/ChartDrawing/Chart/MultiAreaChartControl.cs`, `src/Common/ChartDrawing/Chart/MultiLineChartControl.cs`, `src/Common/CommonStandard/Components/Chromatogram.cs`, `src/Common/CommonStandard/DataObj/RawDataMetadata.cs`, `src/Common/CommonStandard/DataObj/RawMeasurement.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialLcms.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialMzML.cs`, `src/Common/CommonStandard/Parameters/CoefficientsForCcsCalculation.cs`, `src/Common/CommonStandard/Utility/IonMobilityUtility.cs`, `src/Common/NCDK.Display/Renderers/Elements/TextGroupElement.cs`, `src/Common/NCDK.Display/Renderers/Generators/Standards/HydrogenPosition.cs`, `src/Common/NCDK/Fingerprints/AtomPairs2DFingerprinter.cs`

Примеры:

```
src/RawDataApp/RawDataConverter/MainWindow.xaml.cs:81: if (extension != ".mzml" && extension != ".raw" && extension != ".d")
src/RawDataApp/RawDataViewer/View/MainWindow.xaml.cs:20: CommandBindings.Add(new CommandBinding(ApplicationCommands.Open, OpenRawFile));
src/RawDataApp/RawDataViewer/View/MainWindow.xaml.cs:33: private void OpenRawFile(object sender, ExecutedRoutedEventArgs e) {
src/MSFINDER/MSFINDER/MainWindow.xaml.cs:209: RefreshUtility.UpdataFiles(this.mainWindowVM, this.mainWindowVM.SelectedRawFileId);
src/MSFINDER/MSFINDER/MainWindow.xaml.cs:227: if (this.mainWindowVM.SelectedRawFileId < 0) return;
src/MSFINDER/MSFINDER/MainWindow.xaml.cs:251: RefreshUtility.StructureDataFileRefresh(this, this.mainWindowVM, this.mainWindowVM.SelectedRawFileId);
```

### mzmine — 1926 попаданий в 353 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/AbundanceMeasure.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/ImagingRawDataFile.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/ImagingScan.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/RawDataFile.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/BinningMobilogramDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/FeatureDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/MobilityScanDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/ScanDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/OtherFeatureUtils.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/impl/SimpleIonMobilogramTimeSeries.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeature.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/ModularCompoundFeature.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:99: public static final ExtensionFilter MZML = new ExtensionFilter("mzML MS data", "*.mzML",
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:100: "*.mzml");
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:101: public static final ExtensionFilter MZXML = new ExtensionFilter("mzXML MS data", "*.mzXML",
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:102: "*.mzxml");
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:103: public static final ExtensionFilter IMZML = new ExtensionFilter("imzML MS imaging data",
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:104: "*.imzML", "*.imzml");
```

### openms — 4088 попаданий в 377 файлах

Файлы: `doc/code_examples/Tutorial_FeatureFinder.cpp`, `doc/code_examples/Tutorial_FileIO.cpp`, `doc/code_examples/Tutorial_FileIO_Consumer.cpp`, `doc/code_examples/Tutorial_FileIO_mzML.cpp`, `doc/code_examples/Tutorial_GaussFilter.cpp`, `doc/code_examples/Tutorial_ImzMLFile.cpp`, `doc/code_examples/Tutorial_Labeled.cpp`, `doc/code_examples/Tutorial_MSExperiment.cpp`, `doc/code_examples/Tutorial_MorphologicalFilter.cpp`, `doc/code_examples/Tutorial_Precursor.cpp`, `doc/code_examples/Tutorial_Unlabeled.cpp`, `doc/openms/_ext/pathrole.py`

Примеры:

```
tools/scripts/plot_pasef_frames.py:14: $BUILD/bin/FileConverter -in $D -out /tmp/off.mzML
tools/scripts/plot_pasef_frames.py:15: $BUILD/bin/FileConverter -in $D -out /tmp/hill.mzML \\
tools/scripts/plot_pasef_frames.py:16: -bruker:ms1_centroid_algo hillbased \\
tools/scripts/plot_pasef_frames.py:17: -bruker:ms2_centroid_algo hillbased
tools/scripts/plot_pasef_frames.py:20: --mzml off=/tmp/off.mzML --mzml hill=/tmp/hill.mzML \\
tools/scripts/plot_pasef_frames.py:41: # Bruker parameters whose values matter for hill/centroiding interpretation
```

### pyc2mc — 12 попаданий в 5 файлах

Файлы: `Image.py`, `main.py`, `modules/pyc2mc_ui.py`, `src/loading/loading_function.py`, `src/pyc2mc_ui.py`

Примеры:

```
Image.py:18: img_str="iVBORw0KGgoAAAANSUhEUgAAAmwAAAGnCAYAAAAKUgvPAAAgAElEQVR4nMy9d5Bl53Undr573+scJ/XkATAYDDIGgEAikABIAiQIgABBSlpRDJLMXSq5pLV27a3aLatorWu9trVm2bJdG7Sl9aqkkpe
main.py:411: self.ui.btn_merge_xcalibur.clicked.connect(openCloseProcessBox)
main.py:909: self.ui.btn_merge_xcalibur.clicked.connect(self.merge_Multicsv)
modules/pyc2mc_ui.py:11947: self.btn_merge_xcalibur = QtWidgets.QPushButton(self.processButtons)
modules/pyc2mc_ui.py:11948: self.btn_merge_xcalibur.setMinimumSize(QtCore.QSize(0, 45))
modules/pyc2mc_ui.py:11954: self.btn_merge_xcalibur.setFont(font)
```

### ume — 9 попаданий в 5 файлах

Файлы: `R/calc_recalibrate_ms.R`, `R/classify_files.R`, `R/extract_aquisition_params.R`, `R/extract_aquisition_params_from_folder.R`, `R/read_xml_peaklist.R`

Примеры:

```
R/calc_recalibrate_ms.R:98: # Do the same process with a selected Bruker ref file (user input dialogue)
R/classify_files.R:39: #'   filename      = c("NS_blk_01.raw", "SRFA_20.raw", "Pool_A.raw",
R/classify_files.R:40: #'                     "Sample_01.raw", "Sample_02.raw", "MQ_blank.raw"),
R/classify_files.R:42: #'   link_rawdata  = c("NS_blk_01.raw", "SRFA_20.raw", "Pool_A.raw",
R/classify_files.R:43: #'                     "Sample_01.raw", "Sample_02.raw", "MQ_blank.raw")
R/extract_aquisition_params.R:2: #' Extract Acquisition Parameters from a Bruker PDF Report
```

### xcms — 55 попаданий в 19 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/XcmsExperiment-plotting.R`, `R/XcmsExperiment.R`, `R/XcmsExperimentHdf5.R`, `R/functions-IO.R`, `R/functions-OnDiskMSnExp.R`, `R/functions-xcmsRaw.R`, `R/functions-xcmsSet.R`, `R/methods-IO.R`, `R/methods-XCMSnExp.R`, `R/methods-xcmsFileSource.R`

Примеры:

```
longtests/testthat.R:17: fticrf <- c(MsDataHub::HAM004_641fE_14.11.07..Exp1.extracted.mzML(),
longtests/testthat.R:18: MsDataHub::HAM004_641fE_14.11.07..Exp2.extracted.mzML())
R/AllGenerics.R:206: #'     is `rtimeDifferenceThreshold = 5`. For Waters data with lockmass scans
R/AllGenerics.R:541: #' fl <- MsDataHub::PestMix1_DDA.mzML()
R/AllGenerics.R:1880: #' fls <- MsDataHub::PestMix1_DDA.mzML()
R/AllGenerics.R:2359: setGeneric("stitch.netCDF", function(object, lockMass) standardGeneric("stitch.netCDF"))
```

## transient_ft — Обработка транзиента и Фурье-преобразование

Всего попаданий по всем проектам: **1224**.

### corems — 448 попаданий в 32 файлах

Файлы: `conftest.py`, `corems/encapsulation/factory/parameters.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/encapsulation/input/parameter_from_json.py`, `corems/encapsulation/output/parameter_to_dict.py`, `corems/mass_spectra/calc/SignalProcessing.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/input/boosterHDF5.py`, `corems/mass_spectra/input/brukerSolarix.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectrum/calc/Calibration.py`, `corems/mass_spectrum/calc/CalibrationCalc.py`

Примеры:

```
conftest.py:11: from corems.transient.input.brukerSolarix import ReadBrukerSolarix
conftest.py:71: def mass_spectrum_ftms(bruker_transient):
conftest.py:74: mass_spectrum = bruker_transient.get_mass_spectrum(
conftest.py:97: def bruker_transient(ftms_file_location):
conftest.py:98: """Returns the transient object for the FTMS file"""
conftest.py:100: bruker_transient = bruker_reader.get_transient()
```

### formultitude — 1 попаданий в 1 файлах

Файлы: `CIA/FormultitudeProgram.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:867: //Original version of this algorithm published as: Kujawinski and Behn. 2006. Automated analysis of electrospray ionization Fourier-transform ion cyclotron reso
```

### msdial — 19 попаданий в 12 файлах

Файлы: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `src/Common/NCDK.Display/Renderers/Generators/Standards/StandardSgroupGenerator.cs`, `src/Common/NCDK/Fingerprints/CircularFingerprinter.cs`, `src/Common/NCDK/Fingerprints/Model/Bayesian.cs`, `src/Common/NCDK/ForceFields/Mmff.cs`, `src/Common/NCDK/IO/ShelXReader.cs`, `src/Common/NCDK/Layout/LayoutRefiner.cs`, `src/Common/NCDK/QSAR/Descriptors/Moleculars/SmallRingDescriptor.cs`, `src/Common/NCDK/QSAR/Descriptors/Moleculars/VAdjMaDescriptor.cs`, `src/Common/NCDK/Smiles/SmilesGenerator.cs`, `src/Common/NCDK/Tools/PeriodicTable.cs`, `src/MSDIAL4/MsDial/Utility/DataExportLcUtility.cs`

Примеры:

```
src/MSDIAL4/MsDial/Utility/DataExportLcUtility.cs:1965: ChromatogramCondition = "Reverse phase LC",
src/Common/NCDK.Display/Renderers/Generators/Standards/StandardSgroupGenerator.cs:323: // just draw the brackets - multiplied group parts have already been hidden in prep phase
src/Common/NCDK/Fingerprints/CircularFingerprinter.cs:943: continue; // valid for either phase
src/Common/NCDK/ForceFields/Mmff.cs:207: /// Clear all transient properties assigned by this class. Assigned charges
src/Common/NCDK/IO/ShelXReader.cs:277: /* 7.8 Fouriers, peak search and lineprinter plots */
src/Common/NCDK/Layout/LayoutRefiner.cs:338: // bond has already been tried in this phase so
```

### mzmine — 99 попаданий в 31 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/identities/iontype/IonPartReference.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/chartutils/ColoredBubbleDatasetRenderer.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/framework/strokechooser/JStrokeChooserDialog.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/framework/strokechooser/SettingsBasicStroke.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/adap_hierarchicalclustering/ADAP3DecompositionV1_5Parameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/adap_mcr/ADAP3DecompositionV2Parameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/adap_mcr/ADAP3DecompositionV2SetupDialog.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/featdet_chromatogramdeconvolution/Resolver.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/featdet_manualintegration/ManualIntegrationParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/engine/CarbonRatio.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/engine/ElementAutoDetector.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_lipidannotationcleanup/LipidAnnotationCleanupParameters.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/util/components/FormulaTextField.java:53: * order, brackets, transiently invalid states) is preserved. Setting the formula externally (e.g.
mzmine-community/src/main/java/io/github/mzmine/util/components/FormulaTextField.java:170: // decision: keep the last valid formula and only highlight the error so a transiently invalid
mzmine-community/src/main/java/io/github/mzmine/util/dialogs/PeriodicTableDialogController.java:90: + phaseTranslator(PeriodicTable.getPhase(handledSymbol)) + "\n" + "Electronegativity:" + " "
mzmine-community/src/main/java/io/github/mzmine/util/dialogs/PeriodicTableDialogController.java:103: + phaseTranslator(PeriodicTable.getPhase(handledSymbol)) + "<br> " + "Electronegativity:"
mzmine-community/src/main/java/io/github/mzmine/util/scans/similarity/impl/DreaMS/DreaMSSpectrumTensorizer.java:117: // If there are fewer peaks than nHighestPeaks, the remaining rows are already zero-filled
mzmine-community/src/main/java/io/github/mzmine/util/presets/manage/ManagePresetsViewBuilder.java:93: "(Presets are in beta phase) Selected preset group: ", model.selectedGroupStoreProperty()
```

### nomspectra — 2 попаданий в 1 файлах

Файлы: `nomspectra/diff.py`

Примеры:

```
nomspectra/diff.py:75: Fourier transform ion cyclotron mass spectrometry data
nomspectra/diff.py:157: Fourier transform ion cyclotron mass spectrometry data
```

### openms — 469 попаданий в 86 файлах

Файлы: `src/openms/extern/GTE/Mathematics/ApprPolynomial2.h`, `src/openms/extern/GTE/Mathematics/ApprPolynomial3.h`, `src/openms/extern/GTE/Mathematics/ApprPolynomial4.h`, `src/openms/extern/GTE/Mathematics/PdeFilter.h`, `src/openms/extern/GTE/Mathematics/RigidBody.h`, `src/openms/extern/GTE/Mathematics/SymmetricEigensolver3x3.h`, `src/openms/extern/SQLiteCpp/include/SQLiteCpp/Statement.h`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.h`, `src/openms/extern/SQLiteCpp/src/Statement.cpp`, `src/openms/extern/evergreen/src/BitReversedShuffle/RecursiveShuffle.hpp`, `src/openms/extern/evergreen/src/Convolution/fft_convolve.hpp`

Примеры:

```
src/topp/ClusterMassTracesByPrecursor.cpp:46: they use FFT to correlate and then use lag of at least 1 scan and pearson correlation of 0.7 to assign precursors to product ions
src/topp/FeatureLinkerUnlabeledKD.cpp:48: magnitudes faster than FLQT.
src/topp/ProSE.cpp:635: // receives; the HyperScore distribution and per-phase timing captured during the
src/topp/ProteomicsLFQ.cpp:444: bio_defaults.setValue("minlh", 3);      // require hills spanning >= 3 scans (default 2 keeps transient noise)
src/topp/ProteomicsLFQ.cpp:1189: changed costs more than a stat() by four orders of magnitude, on a path whose entire purpose
src/topp/OpenNuXL/include/NuXLFDR.h:137: -# Adds a deterministic score-range-normalised tie-breaker of magnitude
```

### pyc2mc — 1 попаданий в 1 файлах

Файлы: `modules/pyc2mc_ui.py`

Примеры:

```
modules/pyc2mc_ui.py:12921: self.PCA_ALL.setText(_translate("MainWindow", "All species (Zero filling will be applied for missing species)"))
```

### ume — 177 попаданий в 26 файлах

Файлы: `R/as_peaklist.R`, `R/assign_formulas.R`, `R/calc_data_summary.R`, `R/calc_eval_params.R`, `R/calc_indeces.R`, `R/calc_logratio.R`, `R/calc_norm_int.R`, `R/calc_recalibrate_ms.R`, `R/check_objects.R`, `R/create_time_flattened_mfd.R`, `R/create_ume_formula_library.R`, `R/data.R`

Примеры:

```
R/assign_formulas.R:16: #' @param pl Either a peaklist (`data.table`) with at least columns `mz`, `i_magnitude`,
R/assign_formulas.R:41: #'   \item All columns of the input peaklist `pl` (e.g. `mz`, `i_magnitude`, `file_id`).
R/as_peaklist.R:60: i_magnitude = 1L,
R/as_peaklist.R:84: i_magnitude = c("i_magnitude", "intensity", "I", "signal", "height"),
R/calc_data_summary.R:32: #'     \item{median(i_magnitude)}{Median intensity value.}
R/calc_data_summary.R:69: mfd[, i_magnitude:=as.numeric(i_magnitude)]
```

### xcms — 8 попаданий в 5 файлах

Файлы: `R/DataClasses.R`, `R/do_findChromPeaks-functions.R`, `R/functions-utils.R`, `R/functions-xcmsSet.R`, `R/methods-xcmsRaw.R`

Примеры:

```
R/DataClasses.R:460: #' LC/\{TOF,OrbiTrap,FTICR\}-MS data in centroid mode. In the first phase
R/do_findChromPeaks-functions.R:26: #' LC/\{TOF,OrbiTrap,FTICR\}-MS data in centroid mode. In the first phase
R/do_findChromPeaks-functions.R:1728: filt <- fft(filt, inverse = TRUE)/length(filt)
R/do_findChromPeaks-functions.R:1942: filt <- fft(filt, inverse = TRUE)/length(filt)
R/do_findChromPeaks-functions.R:3213: filt <- fft(filt, inverse = TRUE) / length(filt)
R/functions-utils.R:57: #' to be used mainly in the transition phase from xcms to xcms version 3.
```

## profile_preprocessing — Профильная обработка: baseline, сглаживание, усреднение

Всего попаданий по всем проектам: **10044**.

### corems — 457 попаданий в 35 файлах

Файлы: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Calc.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`, `corems/mass_spectra/calc/MZSearch.py`, `corems/mass_spectra/calc/SignalProcessing.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/factory/GC_Class.py`, `corems/mass_spectra/factory/chromat_data.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/rawFileReader.py`

Примеры:

```
support_code/windows_only_importers/ThermoMSFileReader.py:270: d_parameter["baseline_noise"] = np.average(array_noise_std)
support_code/windows_only_importers/ThermoMSFileReader.py:271: d_parameter["baseline_noise_std"] = np.std(array_noise_std)
support_code/nmdc/lipidomics/lipidomics_workflow.py:257: fig = myLCMSobj.mass_features[mf_id].plot(return_fig=True, plot_smoothed_eic=True, plot_eic_datapoints=True)
support_code/nmdc/lipidomics/lipidomics_workflow.py:273: fig = myLCMSobj.mass_features[mf_id].plot(return_fig=True, plot_smoothed_eic=True, plot_eic_datapoints=True)
support_code/nmdc/metabolomics/gcms_workflow.py:136: # gcms.plot_smoothed_chromatogram()
support_code/nmdc/metabolomics/gcms_workflow.py:138: # gcms.plot_baseline_subtraction()
```

### formultitude — 11 попаданий в 4 файлах

Файлы: `FindChains/FindChainsForm.cs`, `FindChainsTest/FindChainsTestProgram.cs`, `Support/CChainBlocks.cs`, `TestFSDBSearch/TotalSupport/ttlStat.cs`

Примеры:

```
FindChains/FindChainsForm.cs:921: var Text = "Filename,MatchedPeaks,BeforeErrorAverage,BeforeErrorStdDev,AfterErrorAverage,AfterStdDev";
FindChains/FindChainsForm.cs:941: var AverageErrorBeforeCal = Support.CArrayMath.Mean(ErrorsBeforeCal.ToArray());
FindChains/FindChainsForm.cs:942: var StdDevErrorBeforeCal = Support.CArrayMath.StandardDeviation(ErrorsBeforeCal.ToArray(), AverageErrorBeforeCal);
FindChains/FindChainsForm.cs:943: var AverageErrorAfterCal = Support.CArrayMath.Mean(ErrorsAfterCal.ToArray());
FindChains/FindChainsForm.cs:944: var StdDevErrorAfterCal = Support.CArrayMath.StandardDeviation(ErrorsAfterCal.ToArray(), AverageErrorAfterCal);
FindChains/FindChainsForm.cs:945: Text = Text + ',' + AverageErrorBeforeCal.ToString("F8") + ',' + StdDevErrorBeforeCal.ToString("F8")
```

### icbmocean — 1 попаданий в 1 файлах

Файлы: `fastjoin.R`

Примеры:

```
fastjoin.R:27: # calculate weighted average mass within each mass group or use arithmethic mean with mean()
```

### mfassignr — 7 попаданий в 4 файлах

Файлы: `MFAssignR/R/HistNoise.R`, `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/RecalFunctions.R`, `Supplemental MFAssign Scripts/Background Subtraction Guidelines.R`

Примеры:

```
Supplemental MFAssign Scripts/Background Subtraction Guidelines.R:1: ###Background Subtraction After Formula Assignment
Supplemental MFAssign Scripts/Background Subtraction Guidelines.R:70: #work through background subtraction.
MFAssignR/R/HistNoise.R:53: ValMin$Ave <- mean(ValMin$LogInt)                       #Average intensity of the minimum.
MFAssignR/R/KMDNoise.R:18: #'then be averaged to determine the signal to noise
MFAssignR/R/KMDNoise.R:34: #'the average intensity of the peaks in that region,
MFAssignR/R/KMDNoise.R:101: #Filtering the actual data within the S/N area and calculating the average intensity
```

### msdial — 4681 попаданий в 274 файлах

Файлы: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/MsScanMatchingBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/DataStructure/PriorityQueueBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Tests.cs`, `src/Common/ChartDrawing/Base/Utility.cs`, `src/Common/ChartDrawing/Chart/DendrogramControl.cs`, `src/Common/ChartDrawing/DrawVisual/DrawVisualManualPeakModification.cs`, `src/Common/ChartDrawing/IO/XamlToys.cs`, `src/Common/ChartDrawing/Legacy/ChromatogramBean.cs`, `src/Common/CommonStandard/Algorithm/ChromSmoothing/Smoothing.cs`, `src/Common/CommonStandard/Algorithm/PeakPick/BaseLineCorrecation.cs`, `src/Common/CommonStandard/Algorithm/PeakPick/NoiseEstimateParameter.cs`

Примеры:

```
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:28: var providerFactory = new MsdialImmsCore.Algorithm.ImmsAverageDataProviderFactory(massTolerance: 0.001, driftTolerance: 0.002);
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:38: var sChromPeaks = new Chromatogram(chromPeaks, ChromXType.Mz, ChromXUnit.Mz).ChromatogramSmoothing(parameter.SmoothingMethod, parameter.SmoothingLevel).AsPeakAr
src/MSDIAL5/MsdialDimsCore/ProcessFile.cs:83: var sChromPeaks = new Chromatogram(chromPeaks, ChromXType.Mz, ChromXUnit.Mz).ChromatogramSmoothing(param.SmoothingMethod, param.SmoothingLevel).AsPeakArray();
src/MSDIAL5/MsdialLcMsApi/Algorithm/LcmsDataAccessor.cs:33: var peakWidth = detected.Average(x => x.PeakWidth(ChromXType.RT));
src/MSDIAL5/MsdialLcMsApi/Algorithm/LcmsDataAccessor.cs:51: peak.FileID, peaklist.ChromatogramSmoothing(this.lcmsParameter.SmoothingMethod, this.lcmsParameter.SmoothingLevel).AsPeakArray(),
src/MSDIAL5/MsdialLcMsApi/Algorithm/Ms2Dec.cs:197: ExtractedIonChromatogram chromatogram = new ExtractedIonChromatogram(ms2Peaks, ChromXType.RT, ChromXUnit.Min, productMz).ChromatogramSmoothing(param.SmoothingMe
```

### mzmine — 1798 попаданий в 362 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/javafx/util/FxIconUtil.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/FeatureDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/FeatureFullDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/IonTimeSeriesUtils.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/impl/IonMobilogramTimeSeriesFactory.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/impl/SummedIntensityMobilitySeries.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureListRow.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureListRow.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/SimpleRowBinding.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/annotationpriority/AnnotationSummary.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/main/StartupSplash.java:164: logoView.setSmooth(true);
mzmine-community/src/main/java/io/github/mzmine/main/StartupSplash.java:196: mzioLogo.setSmooth(true);
mzmine-community/src/main/java/io/github/mzmine/main/StartupSplash.java:225: communityLogo.setSmooth(true);
mzmine-community/src/main/java/io/github/mzmine/util/CorrelationGroupingUtils.java:140: groups.sort(Comparator.comparing(RowGroup::calcAverageRetentionTime,
mzmine-community/src/main/java/io/github/mzmine/util/FeatureConvertors.java:299: "Smoothing is not yet supported for this kind of data. " + originalData.getClass()
mzmine-community/src/main/java/io/github/mzmine/util/FeatureListRowSorter.java:37: * Compare feature list rows either by ID, average m/z or median area of peaks
```

### nomspectra — 27 попаданий в 3 файлах

Файлы: `nomspectra/recal.py`, `nomspectra/spectra.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/recal.py:205: #smooth data
nomspectra/spectra.py:192: Get average molecular metrics
nomspectra/spectra.py:199: How calculate average. My be "weight" (default - weight average on intensity),
nomspectra/spectra.py:222: def get_square_vk(self, how_average: str = 'weight') -> pd.DataFrame:
nomspectra/spectra.py:228: how_average: {"count", "weight"}
nomspectra/spectra.py:229: How calculate average. My be "count" or "weight" ((default))
```

### openms — 2802 попаданий в 417 файлах

Файлы: `doc/code_examples/Tutorial_AASequence.cpp`, `doc/code_examples/Tutorial_Element.cpp`, `doc/code_examples/Tutorial_EmpiricalFormula.cpp`, `doc/code_examples/Tutorial_GaussFilter.cpp`, `doc/code_examples/Tutorial_MorphologicalFilter.cpp`, `doc/code_examples/Tutorial_Residue.cpp`, `doc/code_examples/Tutorial_SavitzkyGolayFilter.cpp`, `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `share/OpenMS/SCRIPTS/InternalCalibration_Residuals.R`, `src/openms/extern/GTE/Mathematics/APConversion.h`, `src/openms/extern/GTE/Mathematics/AdaptiveSkeletonClimbing3.h`, `src/openms/extern/GTE/Mathematics/ApprCircle2.h`

Примеры:

```
tools/scripts/plot_pasef_frames.py:227: # noise still lights up its pixel (sum would average it down).
src/topp/BaselineFilter.cpp:13: #include <OpenMS/PROCESSING/BASELINE/MorphologicalFilter.h>
src/topp/BaselineFilter.cpp:25: @page TOPP_BaselineFilter BaselineFilter
src/topp/BaselineFilter.cpp:27: @brief Executes the top-hat filter to remove the baseline of an MS experiment.
src/topp/BaselineFilter.cpp:33: <td VALIGN="middle" ROWSPAN=2> &rarr; BaselineFilter &rarr;</td>
src/topp/BaselineFilter.cpp:45: of the underlying baseline shape.  It is able to detect an over brightness
```

### pyc2mc — 17 попаданий в 5 файлах

Файлы: `modules/comparison.py`, `modules/data_views.py`, `modules/molecular_maps.py`, `modules/pyc2mc_ui.py`, `src/pre_processing_function.py`

Примеры:

```
modules/comparison.py:1543: Average carbon oxydation plot
modules/comparison.py:1692: "Average carbon oxidation state vs #C",
modules/data_views.py:397: def weighted_average_m1(to_mean, norm_I):
modules/data_views.py:411: mean_DBE = weighted_average_m1(
modules/molecular_maps.py:2307: Average carbon oxydation plot
modules/molecular_maps.py:2479: "Average carbon oxidation state vs #C",
```

### ume — 20 попаданий в 7 файлах

Файлы: `R/calc_data_summary.R`, `R/calc_eval_params.R`, `R/color.palette.R`, `R/create_time_flattened_mfd.R`, `R/uplot_cluster.R`, `R/uplot_isotope_precision.R`, `R/uplot_n_mf_per_sample.R`

Примеры:

```
R/calc_data_summary.R:3: #' @description Generates a data summary table that provides intensity-weighted averages for element ratios,
R/calc_data_summary.R:9: #' @details This function computes a variety of weighted averages and summary statistics for mass spectrometry data
R/calc_data_summary.R:10: #'   using the provided peak list (`mfd`). Calculated values include weighted averages for elemental counts
R/calc_data_summary.R:23: #'     \item{wa(mz)}{Weighted average m/z value.}
R/calc_data_summary.R:24: #'     \item{wa(DBE)}{Weighted average Double Bond Equivalent (DBE).}
R/calc_data_summary.R:25: #'     \item{wa(element)}{Weighted averages for elements (C, H, N, O, P, S) and ratios (O/C, H/C, N/C, S/C).}
```

### xcms — 223 попаданий в 21 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment.R`, `R/cwTools.R`, `R/do_adjustRtime-functions.R`, `R/do_findChromPeaks-functions.R`, `R/functions-Chromatogram.R`, `R/functions-OnDiskMSnExp.R`, `R/functions-Params.R`, `R/functions-XChromatograms.R`, `R/methods-Params.R`

Примеры:

```
R/AllGenerics.R:47: #'   polynomial (`smooth = "loess"`) or a linear (`smooth = "linear"`) function
R/AllGenerics.R:87: #' The second, default, option is `subsetAdjust = "average"` in which case
R/AllGenerics.R:88: #' each non subset sample is adjusted based on the average retention time
R/AllGenerics.R:89: #' adjustment from the previous and following subset sample. For the average,
R/AllGenerics.R:147: #'     loess smoothing. Allowed values are `"gaussian"` and `"symmetric"`. See
R/AllGenerics.R:211: #' @param smooth For `PeakGroupsParam`: `character(1)` defining the function to
```

## peak_picking_centroiding — Пикинг пиков и центроидирование

Всего попаданий по всем проектам: **6318**.

### corems — 972 попаданий в 44 файлах

Файлы: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Calc.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`, `corems/mass_spectra/calc/SignalProcessing.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `corems/mass_spectra/factory/GC_Class.py`, `corems/mass_spectra/factory/chromat_data.py`, `corems/mass_spectra/factory/lc_class.py`

Примеры:

```
support_code/windows_only_importers/ThermoMSFileReader.py:8: from corems.mass_spectrum.factory.MassSpectrumClasses import MassSpecProfile, MassSpecCentroid
support_code/windows_only_importers/ThermoMSFileReader.py:377: d_params["label"] = Labels.thermo_centroid
support_code/windows_only_importers/ThermoMSFileReader.py:387: mass_spec = MassSpecCentroid(data_dict, d_params)
support_code/nmdc/lipidomics/lipidomics_workflow.py:4: Assumes that ms1 are collected in profile mode, persistent homology not applicable for centroided data.
support_code/nmdc/lipidomics/lipidomics_workflow.py:151: This includes peak picking, adding and processing associated ms1 spectra,
support_code/nmdc/lipidomics/lipidomics_workflow.py:186: # If the ms1 data are centroided and the parser if MZMLSpectraParser, set spectrum_mode to centroided but use_parser to False (mzml doesn't have resolving power
```

### formultitude — 27 попаданий в 4 файлах

Файлы: `CiaUi/FormultitudeUIForm.cs`, `FileReader/FileReader.cs`, `Support/CFileReader.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.cs`

Примеры:

```
CiaUi/FormultitudeUIForm.cs:1003: //<pk res="930674.5" algo="FTMS" fwhm="0.000218" a="102.53" sn="7.15" i="646225.1" mz="203.034719"/>
FileReader/FileReader.cs:82: //<pk res="930674.5" algo="FTMS" fwhm="0.000218" a="102.53" sn="7.15" i="646225.1" mz="203.034719"/>
Support/CFileReader.cs:390: //<pk res="930674.5" algo="FTMS" fwhm="0.000218" a="102.53" sn="7.15" i="646225.1" mz="203.034719"/>
TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.cs:56: Spectrum.ConvertProfileToCentroid( MZs, Abundances, out NoiseMZs, out MinNoiseAbundances, out MeanNoiseAbundances );
TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.cs:228: enum Datatype { Profile, Centroid };
TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.cs:236: public bool ValleyPeak;
```

### mfassignr — 2 попаданий в 1 файлах

Файлы: `MFAssignR/R/HistNoise.R`

Примеры:

```
MFAssignR/R/HistNoise.R:51: Valley <- Freqdf[(LogInt > mode & LogInt < (mode+2)),]  #Finds the valley between the noise max and the analyte
MFAssignR/R/HistNoise.R:52: ValMin <- Valley[Valley$Count == min(Valley$Count),]    #Finds the minimum point of the valley
```

### msdial — 1088 попаданий в 174 файлах

Файлы: `src/Common/ChartDrawing/DrawVisual/DrawVisualManualPeakModification.cs`, `src/Common/ChartDrawing/Legacy/ChromatogramXicViewModel.cs`, `src/Common/CommonStandard/Algorithm/PeakPick/SpectralCentroiding.cs`, `src/Common/CommonStandard/Components/Chromatogram.cs`, `src/Common/CommonStandard/Components/PeakOfChromatogram.cs`, `src/Common/CommonStandard/DataObj/RawData.cs`, `src/Common/CommonStandard/DataObj/RawMeasurement.cs`, `src/Common/CommonStandard/Enum/CommonEnums.cs`, `src/Common/CommonStandard/FormulaGenerator/FormulaGenerator.cs`, `src/Common/CommonStandard/FormulaGenerator/Function/FragmentAssigner.cs`, `src/Common/CommonStandard/FormulaGenerator/Parser/RawDataParcer.cs`, `src/Common/CommonStandard/Lipidomics/MsmsCharacterization.cs`

Примеры:

```
src/MSFINDER/MsfinderCommonStandard/Process/PeakAssigner.cs:41: var centroidSpectrum = FragmentAssigner.GetCentroidMsMsSpectrum(rawData);
src/MSFINDER/MsfinderCommonStandard/Process/PeakAssigner.cs:42: var refinedPeaklist = FragmentAssigner.GetRefinedPeaklist(centroidSpectrum, param.RelativeAbundanceCutOff,
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:375: var centroidSpectrum = FragmentAssigner.GetCentroidMsMsSpectrum(rawData);
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:376: var refinedPeaklist = FragmentAssigner.GetRefinedPeaklist(centroidSpectrum, analysisParam.RelativeAbundanceCutOff,
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:394: var centroidSpectrum = FragmentAssigner.GetCentroidMsMsSpectrum(rawData);
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:395: var refinedPeaklist = FragmentAssigner.GetRefinedPeaklist(centroidSpectrum, analysisParam.RelativeAbundanceCutOff,
```

### mzmine — 1072 попаданий в 226 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureStatus.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MassSpectrum.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MassSpectrumType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/RawDataFile.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/EfficientDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/MobilityScanDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/ScanDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/FeatureDataUtils.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/Feature.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeature.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/graphicalnodes/ChromatogramFeatureShapeCell.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/numbers/FwhmType.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureStatus.java:45: * Peak was found in primary peak picking
mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureStatus.java:50: * Peak was estimated in secondary peak picking
mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureStatus.java:117: case DETECTED -> "Feature was found in primary peak picking";
mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureStatus.java:118: case ESTIMATED -> "Feature was estimated in secondary peak picking (gap-filling)";
mzmine-community/src/main/java/io/github/mzmine/datamodel/MassSpectrum.java:57: * Centroid / profile / thresholded
mzmine-community/src/main/java/io/github/mzmine/datamodel/MassSpectrumType.java:49: * Centroided mass spectrum = discrete data points, one for each detected ion.
```

### openms — 2823 попаданий в 317 файлах

Файлы: `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/GTE/Mathematics/AdaptiveSkeletonClimbing3.h`, `src/openms/extern/GTE/Mathematics/ContEllipsoid3MinCR.h`, `src/openms/extern/GTE/Mathematics/DistTetrahedron3Tetrahedron3.h`, `src/openms/extern/GTE/Mathematics/ExtremalQuery3PRJ.h`, `src/openms/extern/GTE/Mathematics/Tetrahedron3.h`, `src/openms/extern/IsoSpec/IsoSpec/isoSpec++.h`, `src/openms/extern/SQLiteCpp/include/SQLiteCpp/Assertion.h`, `src/openms/extern/SQLiteCpp/include/SQLiteCpp/Database.h`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/extern/SQLiteCpp/src/Database.cpp`, `src/openms/extern/tool_description_lib/src/tdl/convertToCTD.h`

Примеры:

```
tools/scripts/plot_pasef_frames.py:2: """Render N MS1 and N MS2 PASEF frames side-by-side across centroiding settings.
tools/scripts/plot_pasef_frames.py:4: Companion to ``visualize_pasef_centroiding.py``: instead of one frame, this
tools/scripts/plot_pasef_frames.py:7: between e.g. off / greedy / hill centroiding.
tools/scripts/plot_pasef_frames.py:16: -bruker:ms1_centroid_algo hillbased \\
tools/scripts/plot_pasef_frames.py:17: -bruker:ms2_centroid_algo hillbased
tools/scripts/plot_pasef_frames.py:41: # Bruker parameters whose values matter for hill/centroiding interpretation
```

### pyc2mc — 1 попаданий в 1 файлах

Файлы: `src/loading/loading_function.py`

Примеры:

```
src/loading/loading_function.py:416: ["pid", "resolving_power", "frequency", "SN", "n_candidates", "z"], axis=1
```

### xcms — 333 попаданий в 38 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/MsExperiment-functions.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment.R`, `R/XcmsExperimentHdf5-functions.R`, `R/XcmsExperimentHdf5.R`, `R/cwTools.R`, `R/do_findChromPeaks-functions.R`, `R/do_groupChromPeaks-functions.R`, `R/functions-Chromatogram.R`

Примеры:

```
R/AllGenerics.R:150: #' @param gapExtend For `ObiwarpParam`: `numeric(1)` defining the penalty for
R/AllGenerics.R:151: #'     gap enlargement. The default value for `gapExtend` depends on the value
R/AllGenerics.R:433: #'   closest to the peak's retention time (at apex).
R/AllGenerics.R:435: #'   closest to the peaks's m/z (at apex); only supported for `msLevel > 1`.
R/AllGenerics.R:441: #'   spectrum with the sum of intensities most similar to the peak's apex
R/AllGenerics.R:574: #' ## chromatographic peak's apex position. Alternatively it would also be
```

## noise_estimation — Оценка шума (не только порог)

Всего попаданий по всем проектам: **1750**.

### corems — 242 попаданий в 34 файлах

Файлы: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Calc.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/factory/GC_Class.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectrum/calc/Calibration.py`, `corems/mass_spectrum/calc/MassErrorPrediction.py`, `corems/mass_spectrum/calc/MassSpectrumCalc.py`

Примеры:

```
support_code/windows_only_importers/ThermoMSFileReader.py:269: l_signal_to_noise = np.array(magnitude) / array_noise_std
support_code/windows_only_importers/ThermoMSFileReader.py:276: Labels.s2n: l_signal_to_noise,
support_code/nmdc/lipidomics/lipidomics_workflow.py:449: "noise_threshold": 0,
support_code/nmdc/lipidomics/lipidomics_workflow.py:556: "noise_threshold": 0,
support_code/nmdc/lipidomics/lipidomics_workflow.py:581: "noise_threshold": 0,
support_code/nmdc/metabolomics/lcms_metabolomics_targeted_search.py:21: lcms_obj.parameters.mass_spectrum['ms2'].mass_spectrum.noise_threshold_method = "relative_abundance"
```

### formultitude — 51 попаданий в 11 файлах

Файлы: `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `FindChains/FindChainsForm.Designer.cs`, `FindChainsTest/FindChainsTestProgram.cs`, `TestFSDBSearch/Form1.cs`, `TestSpectrumNoiseLevel/Properties/AssemblyInfo.cs`, `TestSpectrumNoiseLevel/Properties/Resources.Designer.cs`, `TestSpectrumNoiseLevel/Properties/Settings.Designer.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.Designer.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelProgram.cs`

Примеры:

```
CiaUi/CiaAdvancedForm.Designer.cs:360: this.label32.Text = "Min S/N";
CiaUi/FormultitudeUIForm.Designer.cs:783: this.label56.Text = "Minor peaks min s/n";
CiaUi/FormultitudeUIForm.Designer.cs:792: this.label57.Text = "Major peaks min s/n";
CiaUi/FormultitudeUIForm.Designer.cs:1772: this.label32.Text = "Min S/N";
FindChains/FindChainsForm.Designer.cs:524: this.label11.Text = "S/N >=";
FindChains/FindChainsForm.Designer.cs:543: this.checkBoxS2N.Text = "Use S/N";
```

### mfassignr — 40 попаданий в 6 файлах

Файлы: `MFAssignR/R/HistNoise.R`, `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`

Примеры:

```
MFAssignR/R/HistNoise.R:1: #'Estimates the noise level
MFAssignR/R/HistNoise.R:6: #'is used to determine the noise level for the data being analyzed.
MFAssignR/R/HistNoise.R:11: #'The value reported in the console will be the estimated noise level
MFAssignR/R/HistNoise.R:23: #' @return List containing numeric noise level ("Noise")
MFAssignR/R/HistNoise.R:29: #' HistNoise(df, SN = 0, bin = 0.01)
MFAssignR/R/HistNoise.R:30: #' HistNoise(df)
```

### msdial — 116 попаданий в 31 файлах

Файлы: `src/Common/CommonStandard/Algorithm/PeakPick/NoiseEstimateParameter.cs`, `src/Common/CommonStandard/Algorithm/PeakPick/PeakPick.cs`, `src/Common/CommonStandard/Components/Chromatogram.cs`, `src/Common/CommonStandard/Components/ExtractedIonChromatogram.cs`, `src/Common/NCDK/Fingerprints/Model/Bayesian.cs`, `src/MSDIAL4/DataProcessingStandard/Peak detection/PeakDetection.cs`, `src/MSDIAL4/MsdialGcmsProcessStandard/Utility/ResultExportGcUtility.cs`, `src/MSDIAL4/MsdialGcmsProcessStandard/Utility/Writers/GCDecWriterVer1.cs`, `src/MSDIAL4/MsdialLcmsProcessStandard/Utility/DatabaseLcUtility.cs`, `src/MSDIAL4/MsdialLcmsProcessStandard/Utility/ResultExportLcUtility.cs`, `src/MSDIAL4/MsdialPrivateConsoleApp/MspManager.cs`, `src/MSDIAL5/MsdialCore/Export/ChromatogramShapeMetadataAccessorDecorator.cs`

Примеры:

```
src/MSDIAL5/MsdialLcMsApi/Export/LcmsAnalysisMetadataAccessor.cs:57: "S/N",
src/MSDIAL5/MsdialLcMsApi/Export/LcmsMetadataAccessor.cs:59: "S/N average",
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/AutomaticAlignmentRetentionTimeCorrection.cs:466: if (parameter.IntensityQuantile < 0d || parameter.IntensityQuantile > 1d) throw new ArgumentOutOfRangeException(nameof(parameter.IntensityQuantile));
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/AutomaticAlignmentRetentionTimeCorrection.cs:467: if (parameter.MaximumPeakWidthQuantile < 0d || parameter.MaximumPeakWidthQuantile > 1d) throw new ArgumentOutOfRangeException(nameof(parameter.MaximumPeakWidthQ
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/AutomaticAlignmentRetentionTimeCorrection.cs:482: var intensityThreshold = Quantile(peaks.Select(peak => peak.Height), parameter.IntensityQuantile);
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/AutomaticAlignmentRetentionTimeCorrection.cs:484: var widthThreshold = widths.Count == 0 ? double.PositiveInfinity : Quantile(widths, parameter.MaximumPeakWidthQuantile);
```

### mzmine — 635 попаданий в 106 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/impl/SimplePseudoSpectrum.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/simplechart/providers/impl/FeatureImageProvider.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/simplechart/providers/impl/series/IMSIonTraceHeatmapProvider.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/simplechart/providers/impl/spectra/CachedFrame.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/simplechart/providers/impl/spectra/CachedMobilityScan.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/simplechart/providers/impl/spectra/FrameHeatmapProvider.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/mainwindow/MainWindowController.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/align_join/JoinRowAlignScorer.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/align_path/scorer/RTScore.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/featdet_chromatogrambuilder/Chromatogram.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/featdet_chromatogramdeconvolution/ADAPpeakpicking/ADAPResolverParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/featdet_chromatogramdeconvolution/minimumsearch/MinimumSearchFeatureResolver.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/util/DataPointUtils.java:168: public static SimpleSpectralArrays getDatapointsAboveNoiseLevel(SimpleSpectralArrays data,
mzmine-community/src/main/java/io/github/mzmine/util/DataPointUtils.java:169: double noiseLevel) {
mzmine-community/src/main/java/io/github/mzmine/util/DataPointUtils.java:170: return data.filterGreaterNoise(noiseLevel);
mzmine-community/src/main/java/io/github/mzmine/util/FeatureListRowSorter.java:80: double medianArea = MathUtils.calcQuantile(peakAreas, 0.5);
mzmine-community/src/main/java/io/github/mzmine/util/FeatureListRowSorter.java:89: double medianIntensity = MathUtils.calcQuantile(peakIntensities, 0.5);
mzmine-community/src/main/java/io/github/mzmine/util/FeatureListRowSorter.java:98: double medianHeight = MathUtils.calcQuantile(peakHeights, 0.5);
```

### nomspectra — 11 попаданий в 2 файлах

Файлы: `nomspectra/recal.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/recal.py:200: max_kernel = df[i].quantile(q=0.95)
nomspectra/recal.py:389: treshold = df['intensity'].quantile(quart)
nomspectra/spectrum.py:94: Example: ["index", "s/n"]
nomspectra/spectrum.py:429: quantile: Optional[float] = None
nomspectra/spectrum.py:439: quantile: float
nomspectra/spectrum.py:440: Cut by quantile. For example 0.1 mean that 10%
```

### openms — 552 попаданий в 115 файлах

Файлы: `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `share/OpenMS/SCRIPTS/plot_trafo.R`, `src/openms/extern/IsoSpec/IsoSpec/isoSpec++.cpp`, `src/openms/include/OpenMS/ANALYSIS/ID/BayesianProteinInferenceAlgorithm.h`, `src/openms/include/OpenMS/ANALYSIS/ID/FIAMSDataProcessor.h`, `src/openms/include/OpenMS/ANALYSIS/ID/MessagePasserFactory.h`, `src/openms/include/OpenMS/ANALYSIS/ID/PeptDeepRescoring.h`, `src/openms/include/OpenMS/ANALYSIS/MAPMATCHING/ConsensusMapNormalizerAlgorithmQuantile.h`, `src/openms/include/OpenMS/ANALYSIS/MAPMATCHING/TransformationDescription.h`, `src/openms/include/OpenMS/ANALYSIS/MAPMATCHING/TransformationModelLowess.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/MRMFeaturePicker.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/MRMScoring.h`

Примеры:

```
tools/scripts/plot_pasef_frames.py:25: picked at evenly spaced TIC quantiles by default (for ``--n-ms1 10`` the rows
tools/scripts/plot_pasef_frames.py:105: def pick_by_tic_quantile(exp, indices, n):
tools/scripts/plot_pasef_frames.py:106: """Pick n frames at evenly spaced TIC quantiles (10%, 20%, ..., 100% for
tools/scripts/plot_pasef_frames.py:121: rank = int(round(k * m / n)) - 1  # 1-based quantile → 0-based index
tools/scripts/plot_pasef_frames.py:124: # Return ordered by quantile (low → high TIC) so the grid reads
tools/scripts/plot_pasef_frames.py:397: picks = pick_by_tic_quantile(first_exp, pool, n_frames)
```

### pyc2mc — 1 попаданий в 1 файлах

Файлы: `src/loading/loading_function.py`

Примеры:

```
src/loading/loading_function.py:225: names = ["m/z", "absolute_intensity", "S/N ratio"]
```

### ume — 37 попаданий в 12 файлах

Файлы: `R/calc_eval_params.R`, `R/calc_norm_int.R`, `R/calc_recalibrate_ms.R`, `R/data.R`, `R/filter.R`, `R/filter_multi_assignments.R`, `R/get_isotope_info.R`, `R/uplot_freq_ma.R`, `R/uplot_freq_vs_ppm.R`, `R/uplot_isotope_precision.R`, `R/uplot_ma_vs_mz.R`, `R/ustats_outlier.R`

Примеры:

```
R/calc_eval_params.R:171: abs(stats::quantile(ppm, .975)), abs(stats::quantile(ppm, .025))
R/calc_norm_int.R:129: # quantile(mfd$ri, probs=c(0.25, 0.75), names=TRUE)
R/calc_norm_int.R:172: # f_norm_ipr_e <- function(x, lower_quantile=0.1, upper_quantile=0.9){
R/calc_norm_int.R:173: #   q <- quantile(x,probs = c(lower_quantile, upper_quantile)) # Calculate percentile
R/calc_recalibrate_ms.R:93: # this throws an error: quantile(NA, 0.975)
R/calc_recalibrate_ms.R:94: # this is na: quantile(NULL, 0.975)
```

### xcms — 65 попаданий в 11 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/do_adjustRtime-functions.R`, `R/do_findChromPeaks-functions.R`, `R/functions-Params.R`, `R/functions-xcmsRaw.R`, `R/methods-Params.R`, `R/methods-group-features.R`, `R/methods-xcmsRaw.R`, `R/methods-xcmsSet.R`, `src/massifquant/dpq.h`

Примеры:

```
R/AllGenerics.R:1260: #'    integrated. Defaults to  `mzmax = function(z) quantile(z, probs = 0.75)`
R/AllGenerics.R:1261: #'    hence using the 75% quantile of all values.
R/AllGenerics.R:1266: #'     integrated. Defaults to `mzmin = function(z) quantile(z, probs = 0.25)`
R/AllGenerics.R:1267: #'     hence using the 25% quantile of all values.
R/AllGenerics.R:1288: #'     integrated. Defaults to `rtmax = function(z) quantile(z, probs = 0.75)`
R/AllGenerics.R:1289: #'     hence using the 75% quantile of all values.
```

## mass_calibration — Калибровка/рекалибровка масс

Всего попаданий по всем проектам: **4983**.

### corems — 378 попаданий в 33 файлах

Файлы: `conftest.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Calc.py`, `corems/mass_spectra/calc/GC_RI_Calibration.py`, `corems/mass_spectra/calc/SignalProcessing.py`, `corems/mass_spectra/factory/GC_Class.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectra/output/export.py`, `corems/mass_spectrum/calc/AutoRecalibration.py`, `corems/mass_spectrum/calc/Calibration.py`, `corems/mass_spectrum/calc/CalibrationCalc.py`

Примеры:

```
conftest.py:86: """Returns the location of the reference file for calibration for the tests"""
support_code/nmdc/metabolomics/gcms_workflow.py:15: from corems.mass_spectra.calc.GC_RI_Calibration import get_rt_ri_pairs
support_code/nmdc/metabolomics/gcms_workflow.py:40: def get_reference_dict(calibration_file_path=False):
support_code/nmdc/metabolomics/gcms_workflow.py:45: if not calibration_file_path:
support_code/nmdc/metabolomics/gcms_workflow.py:53: file_path = calibration_file_path
support_code/nmdc/metabolomics/gcms_workflow.py:77: gcms.calibrate_ri(ref_dict, cal_file_path)
```

### formultitude — 407 попаданий в 13 файлах

Файлы: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`, `FindChains/FindChainsForm.Designer.cs`, `FindChains/FindChainsForm.cs`, `FindChains/_Unused/FindChains.cs`, `FindChainsTest/FindChainsTestProgram.cs`, `Support/CChainBlocks.cs`, `Support/CFileReader.cs`, `TestFSDBSearch/Form1.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:176: //Calibration
CIA/FormultitudeProgram.cs:178: public TestFSDBSearch.TotalCalibration oTotalCalibration = new TotalCalibration();
CIA/FormultitudeProgram.cs:180: void Calibrate() {
CIA/FormultitudeProgram.cs:185: oTotalCalibration.cal_log.Clear();
CIA/FormultitudeProgram.cs:186: oData.CalMasses [ FileIndex ] = oTotalCalibration.ttl_LQ_InternalCalibration( ref oData.Masses [ FileIndex ], ref Abundances, ref oData.SNs [ FileIndex ], MaxAb
CIA/FormultitudeProgram.cs:188: oStreamLogWriter.WriteLine( "Calibration of " + Path.GetFileName( Filenames [ FileIndex]) );
```

### mfassignr — 42 попаданий в 2 файлах

Файлы: `MFAssignR/R/RecalFunctions.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`

Примеры:

```
Supplemental MFAssign Scripts/Full MFAssignR Example.R:51: #Highlighting possible recalibrant series
Supplemental MFAssign Scripts/Full MFAssignR Example.R:55: #Qualitative check of recalibrant series and mass recalibration.
MFAssignR/R/RecalFunctions.R:1: #' Generates a plot to visualize recalibrant series, recalibrates two mass lists,
MFAssignR/R/RecalFunctions.R:2: #' and produces a list of the chosen recalibrants.
MFAssignR/R/RecalFunctions.R:6: #' IsoFiltR(), and the chosen recalibrant series to generate a plot for the qualitative
MFAssignR/R/RecalFunctions.R:7: #' assessment of the recalibrants, recalibrate the "Mono" and "Iso" outputs from IsoFiltR,
```

### msdial — 128 попаданий в 36 файлах

Файлы: `src/Common/CommonStandard/DataObj/RawMeasurement.cs`, `src/Common/CommonStandard/FormulaGenerator/Parser/FormulaResultParcer.cs`, `src/Common/CommonStandard/Mathematics/Mathematics/RegressionMathematics.cs`, `src/Common/CommonStandard/Mathematics/Statistics/StatisticsMathematics.cs`, `src/Common/CommonStandard/Parameters/CoefficientsForCcsCalculation.cs`, `src/Common/CommonStandard/StructureFinder/Property/PeakFragmentPair.cs`, `src/Common/CommonStandard/StructureFinder/RtPrediction/RtPrediction.cs`, `src/Common/CommonStandard/Utility/RetentionIndexHandler.cs`, `src/Common/NCDK/Aromaticities/Aromaticity.cs`, `src/Common/NCDK/Common/Hash/Crc32.cs`, `src/Common/NCDK/Fingerprints/Model/Bayesian.cs`, `src/Common/NCDK/Graphs/Cycles.cs`

Примеры:

```
src/MSFINDER/MsfinderConsoleAppCore/Process/PredictProcess.cs:278: "Mass error\tFormula score\tDatabases");
src/MSFINDER/MSFINDER/Utility/ExportUtility.cs:541: sw.WriteLine("Rank\tFormula\tMass\tMass error\tScore\tResources");
src/MSFINDER/MSFINDER/Utility/ExportUtility.cs:645: sw.Write("Mass error\t");
src/MSFINDER/MassSpectrogramMsfinder/MassSpectrogram/MassSpectrogramFE.cs:167: // 5-3. Draw datapoints of reference mass spectrogram if needed
src/MSFINDER/MassSpectrogramMsfinder/MassSpectrogramWithReference/MassSpectrogramWithReferenceFE.cs:189: // 5.4. Draw datapoints and label of reference mass spectrogram
src/MSDIAL5/MsdialGuiApp/ViewModel/DataObj/CcsCalibrationInfoVS.cs:7: public sealed class CcsCalibrationInfoVS : BindableBase
```

### mzmine — 1433 попаданий в 161 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/IMSRawDataFile.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/AcquisitionMzRangeType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/CalibrationDateTimeType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/CalibrationUserType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/MobilityCalibrationDateTimeType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/MobilityCalibrationReferencePressureType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/MobilityCalibrationStdDevPercentType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/MobilityCalibrationUserType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/MzCalibrationModeType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/MzCalibrationStdDevPpmType.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/mainwindow/workspace/AcademicWorkspace.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/preferences/MZminePreferences.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/datamodel/IMSRawDataFile.java:29: import io.github.mzmine.modules.dataprocessing.id_ccscalibration.CCSCalibration;
mzmine-community/src/main/java/io/github/mzmine/datamodel/IMSRawDataFile.java:128: @Nullable CCSCalibration getCCSCalibration();
mzmine-community/src/main/java/io/github/mzmine/datamodel/IMSRawDataFile.java:130: void setCCSCalibration(@Nullable CCSCalibration calibration);
mzmine-community/src/main/java/io/github/mzmine/util/ParsingUtils.java:63: import org.apache.commons.math3.analysis.polynomials.PolynomialFunction;
mzmine-community/src/main/java/io/github/mzmine/util/ParsingUtils.java:64: import org.apache.commons.math3.analysis.polynomials.PolynomialSplineFunction;
mzmine-community/src/main/java/io/github/mzmine/util/ParsingUtils.java:622: public static PolynomialSplineFunction loadSplineFunctionFromParentXmlElement(Element parent) {
```

### nomspectra — 1 попаданий в 1 файлах

Файлы: `nomspectra/recal.py`

Примеры:

```
nomspectra/recal.py:337: recalibration of mass spectrometric data in nontargeted metabolomics.
```

### openms — 2417 попаданий в 236 файлах

Файлы: `doc/code_examples/Tutorial_SavitzkyGolayFilter.cpp`, `share/OpenMS/SCRIPTS/InternalCalibration_Residuals.R`, `src/openms/extern/GTE/Mathematics/ACosEstimate.h`, `src/openms/extern/GTE/Mathematics/ASinEstimate.h`, `src/openms/extern/GTE/Mathematics/ATanEstimate.h`, `src/openms/extern/GTE/Mathematics/ApprCone3.h`, `src/openms/extern/GTE/Mathematics/ApprEllipse2.h`, `src/openms/extern/GTE/Mathematics/ApprEllipsoid3.h`, `src/openms/extern/GTE/Mathematics/ApprParallelLines2.h`, `src/openms/extern/GTE/Mathematics/ApprPolynomial2.h`, `src/openms/extern/GTE/Mathematics/ApprPolynomial3.h`, `src/openms/extern/GTE/Mathematics/ApprPolynomial4.h`

Примеры:

```
tools/scripts/plot_pasef_frames.py:43: # bruker params like `calibrate`, `export_mode`, IO flags etc. are omitted.
src/topp/AssayGeneratorMetabo.cpp:15: #include <OpenMS/PROCESSING/CALIBRATION/PrecursorCorrection.h>
src/topp/AssayGeneratorMetabo.cpp:129: registerDoubleOption_("precursor_recalibration_window", "<num>", 0.01, "Tolerance window for precursor selection (Annotation of precursor mz and intensity)", fa
src/topp/AssayGeneratorMetabo.cpp:130: registerStringOption_("precursor_recalibration_window_unit", "<choice>", "Da", "Unit of the precursor_mz_tolerance_annotation", false, true);
src/topp/AssayGeneratorMetabo.cpp:131: setValidStrings_("precursor_recalibration_window_unit", ListUtils::create<std::string>("Da,ppm"));
src/topp/AssayGeneratorMetabo.cpp:185: double pre_recal_win = getDoubleOption_("precursor_recalibration_window");
```

### ume — 59 попаданий в 7 файлах

Файлы: `R/assign_formulas.R`, `R/calc_ma.R`, `R/calc_recalibrate_ms.R`, `R/data.R`, `R/filter_multi_assignments.R`, `R/main_docu.R`, `R/read_xml_peaklist.R`

Примеры:

```
R/assign_formulas.R:47: #'       \item `del` — absolute mass error (Da).
R/assign_formulas.R:48: #'       \item `ppm` — mass error in parts per million.
R/assign_formulas.R:232: # Calculate absolute and relative mass error
R/calc_ma.R:75: m_min <- m - (m * ma_dev / 1000000) # lower limit of mass error
R/calc_ma.R:76: m_max <- m + (m * ma_dev / 1000000) # upper limit of mass error
R/calc_recalibrate_ms.R:1: #' @title Recalibrate mass spectra
```

### xcms — 118 попаданий в 17 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MPI.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment.R`, `R/XcmsExperimentHdf5-functions.R`, `R/XcmsExperimentHdf5.R`, `R/do_adjustRtime-functions.R`, `R/functions-Params.R`, `R/functions-XCMSnExp.R`, `R/functions-xcmsSet.R`, `R/matchpeaks.R`

Примеры:

```
R/AllGenerics.R:47: #'   polynomial (`smooth = "loess"`) or a linear (`smooth = "linear"`) function
R/AllGenerics.R:206: #'     is `rtimeDifferenceThreshold = 5`. For Waters data with lockmass scans
R/AllGenerics.R:285: setGeneric("AutoLockMass", function(object) standardGeneric("AutoLockMass"))
R/AllGenerics.R:296: setGeneric("calibrate", function(object, ...) standardGeneric("calibrate"))
R/AllGenerics.R:2357: setGeneric("stitch", function(object, lockMass, ...) standardGeneric("stitch"))
R/AllGenerics.R:2358: setGeneric("stitch.xml", function(object, lockMass) standardGeneric("stitch.xml"))
```

## rt_alignment — Выравнивание по времени удержания

Всего попаданий по всем проектам: **15684**.

### corems — 436 попаданий в 31 файлах

Файлы: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/calc/subset.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`, `corems/mass_spectra/calc/GC_RI_Calibration.py`, `corems/mass_spectra/calc/SignalProcessing.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `corems/mass_spectra/factory/GC_Class.py`, `corems/mass_spectra/factory/chromat_data.py`, `corems/mass_spectra/factory/lc_class.py`

Примеры:

```
support_code/windows_only_importers/BrukerCompassXtract.py:48: get_bruker_retention_time() -> array:
support_code/windows_only_importers/BrukerCompassXtract.py:49: Get the retention time array from the file.
support_code/windows_only_importers/BrukerCompassXtract.py:128: def get_bruker_retention_time(self) -> array:
support_code/windows_only_importers/BrukerCompassXtract.py:156: list_rt = self.get_bruker_retention_time()
support_code/windows_only_importers/BrukerCompassXtract.py:172: self.lcms.retention_time = list_rt
support_code/windows_only_importers/ThermoMSFileReader.py:74: Get the retention time and TIC for the given scan number.
```

### formultitude — 116 попаданий в 6 файлах

Файлы: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`, `TestFSDBSearch/Form1.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:195: //Alignment
CIA/FormultitudeProgram.cs:197: public bool Alignment = true;
CIA/FormultitudeProgram.cs:198: public bool GetAlignment() { return Alignment; }
CIA/FormultitudeProgram.cs:199: public void SetAlignment( bool Alignment ) { this.Alignment = Alignment; }
CIA/FormultitudeProgram.cs:200: double AlignmentPPMTolerance = 1;//default
CIA/FormultitudeProgram.cs:201: public double GetAlignmentPpmTolerance() { return AlignmentPPMTolerance; }
```

### mfassignr — 3 попаданий в 3 файлах

Файлы: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssign_RMD.R`, `Supplemental MFAssign Scripts/Background Subtraction Guidelines.R`

Примеры:

```
Supplemental MFAssign Scripts/Background Subtraction Guidelines.R:7: #renaming a couple columns to make alignment easier
MFAssignR/R/MFAssign.R:2041: #########C13 Isotope Alignment
MFAssignR/R/MFAssign_RMD.R:2044: #########C13 Isotope Alignment
```

### msdial — 10024 попаданий в 604 файлах

Файлы: `src/Common/ChartDrawing/Adorner/ContentAdorner.cs`, `src/Common/ChartDrawing/Base/Utility.cs`, `src/Common/ChartDrawing/Behavior/ScatterFocusBehavior.cs`, `src/Common/ChartDrawing/Chart/Annotator.cs`, `src/Common/ChartDrawing/Chart/SpotLinkedAnnotator.cs`, `src/Common/ChartDrawing/DrawVisual/DrawVisual.cs`, `src/Common/ChartDrawing/IO/HeaderConverter.cs`, `src/Common/ChartDrawing/UI/NumericUpDown.cs`, `src/Common/ChartDrawing/UI/ResizableItemsControl.cs`, `src/Common/ChartDrawing/Window/SelectFolderDialog.cs`, `src/Common/CommonStandard/Algorithm/ChromSmoothing/Smoothing.cs`, `src/Common/CommonStandard/Algorithm/CowAlignment/CowAlignment.cs`

Примеры:

```
src/MSFINDER/MsfinderCommonStandard/Utility/FileStorageUtility.cs:173: errorMessage = "A library containing the list of retention time and InChIKey should be selected if you select the RT option for structure elucidation.";
src/MSFINDER/MsfinderCommonStandard/Utility/FileStorageUtility.cs:174: //  MessageBox.Show("A library containing the list of retention time and InChIKey should be selected if you select the RT option for structure elucidation."
src/MSFINDER/MsfinderCommonStandard/Utility/MsFinderIniParcer.cs:762: sw.WriteLine("#Retention time setting for structure elucidation");
src/MSFINDER/MsfinderCommonStandard/Utility/MsFinderIniParcer.cs:777: sw.WriteLine("#Retention time setting for spectral searching");
src/MSFINDER/MSFINDER/Export/MsFinderValidation.cs:110: var results = new List<MsFinderValidationResultTemp>(); //[0] alignment ID [1] formula [2] inchikey [3] Ontology
src/MSFINDER/MSFINDER/Export/MsFinderValidation.cs:203: sw.WriteLine("Alignment ID\tCarbon count\tFormula\tOntology\tInChIKey");
```

### mzmine — 1398 попаданий в 478 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/FilterableListView.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxComboBox.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxLabels.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxListViews.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxTextFlows.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/TableColumns.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/TreeTableColumns.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/util/FxLayout.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/util/FxIconUtil.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/validation/IconValidationDecoration.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/IMSRawDataFile.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MergedMassSpectrum.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/datamodel/IMSRawDataFile.java:105: * @param rt the retention time (in minutes)
mzmine-community/src/main/java/io/github/mzmine/datamodel/IMSRawDataFile.java:106: * @return The frame closest to the specified retention time. null if the given time is outside of
mzmine-community/src/main/java/io/github/mzmine/datamodel/IMSRawDataFile.java:113: * @param rt the retention time (in seconds)
mzmine-community/src/main/java/io/github/mzmine/datamodel/IMSRawDataFile.java:115: * @return The frame closest to the given retention time at the specified ms level. null if the
mzmine-community/src/main/java/io/github/mzmine/datamodel/MergedMassSpectrum.java:89: * retention time or shape
mzmine-community/src/main/java/io/github/mzmine/datamodel/MobilityScan.java:73: * @return The retention time of the frame when this spectrum was acquired.
```

### openms — 2302 попаданий в 372 файлах

Файлы: `doc/code_examples/Tutorial_MSExperiment.cpp`, `doc/code_examples/Tutorial_MapAlignment.cpp`, `doc/code_examples/Tutorial_Precursor.cpp`, `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `share/OpenMS/SCRIPTS/plot_trafo.R`, `src/openms/extern/GTE/Mathematics/VertexAttribute.h`, `src/openms/extern/IsoSpec/IsoSpec/dirtyAllocator.cpp`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/extern/evergreen/src/Tensor/alloc.hpp`, `src/openms/extern/simde/simde/simde-align.h`, `src/openms/extern/simde/simde/wasm/simd128.h`, `src/openms/extern/simde/simde/x86/avx.h`

Примеры:

```
src/topp/AssayGeneratorMetabo.cpp:400: // group ambiguous identification based on precursor_mz and feature retention time
src/topp/ClusterMassTraces.cpp:85: registerDoubleOption_("max_rt_apex_difference", "<double>", 5.0, "Maximal difference of the apex in retention time", false);
src/topp/ClusterMassTracesByPrecursor.cpp:97: registerDoubleOption_("max_rt_apex_difference", "<double>", 5.0, "Maximal difference of the apex in retention time (in seconds). This is a hard parameter, all p
src/topp/ClusterMassTracesByPrecursor.cpp:265: feature_arr.push_back(rt_cache_ms2[j]);  // MS2 retention time
src/topp/ConsensusID.cpp:89: @li idXML: A file containing multiple identification runs, typically from different search engines. Use @ref TOPP_IDMerger to merge individual idXML files from 
src/topp/ConsensusID.cpp:135: registerDoubleOption_("rt_delta", "<value>", 0.1, "[idXML input only] Maximum allowed retention time deviation between identifications belonging to the same spe
```

### pyc2mc — 477 попаданий в 7 файлах

Файлы: `modules/comparison.py`, `modules/molecular_maps.py`, `modules/plots.py`, `modules/pyc2mc_ui.py`, `modules/ui_main.py`, `src/pyc2mc_ui.py`, `venn/_venn.py`

Примеры:

```
modules/comparison.py:1232: horizontalalignment="left",
modules/comparison.py:1233: verticalalignment="center",
modules/comparison.py:1680: horizontalalignment="left",
modules/comparison.py:1681: verticalalignment="center",
modules/comparison.py:1923: horizontalalignment="left",
modules/comparison.py:1924: verticalalignment="center",
```

### ume — 31 попаданий в 4 файлах

Файлы: `R/calc_recalibrate_ms.R`, `R/create_time_flattened_mfd.R`, `R/remove_blanks.R`, `R/uplot_lcms.R`

Примеры:

```
R/calc_recalibrate_ms.R:367: if(verbose){message("Only spectra with identical retention time are considered.")}
R/create_time_flattened_mfd.R:7: #' across the retention time dimension. This creates a
R/create_time_flattened_mfd.R:22: #' @param ret_time_col Character string. Name of the retention time column.
R/create_time_flattened_mfd.R:25: #'   a chromatographic retention time dimension. Defaults to `TRUE`.
R/create_time_flattened_mfd.R:65: # Check whether the input has a chromatographic retention time dimension.
R/create_time_flattened_mfd.R:69: "No retention time column found. Expected column: `",
```

### xcms — 897 попаданий в 53 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/MPI.R`, `R/MsExperiment-functions.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment-plotting.R`, `R/XcmsExperiment.R`, `R/XcmsExperimentHdf5-functions.R`, `R/XcmsExperimentHdf5.R`, `R/cwTools.R`, `R/do_adjustRtime-functions.R`

Примеры:

```
longtests/testthat.R:31: ## Doing also the retention time correction etc
longtests/testthat.R:40: xod_r <- adjustRtime(as(od_x, "XCMSnExp"), param = ObiwarpParam())
R/AllGenerics.R:17: #' @title Alignment: Retention time correction methods.
R/AllGenerics.R:21: #' The `adjustRtime` method(s) perform retention time correction (alignment)
R/AllGenerics.R:22: #' between chromatograms of different samples/dataset. Alignment is performed
R/AllGenerics.R:23: #' by default on MS level 1 data. Retention times of spectra from other MS
```

## chromatographic_features — Хроматографические признаки (XIC/деконволюция)

Всего попаданий по всем проектам: **66718**.

### corems — 2263 попаданий в 31 файлах

Файлы: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/calc/subset.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/encapsulation/input/parameter_from_json.py`, `corems/encapsulation/output/parameter_to_dict.py`, `corems/mass_spectra/calc/GC_Calc.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`, `corems/mass_spectra/calc/SignalProcessing.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `corems/mass_spectra/factory/GC_Class.py`

Примеры:

```
support_code/nmdc/lipidomics/lipidomics_workflow.py:148: def add_mass_features(myLCMSobj, scan_translator):
support_code/nmdc/lipidomics/lipidomics_workflow.py:152: integration of mass features, annotation of c13 mass features, deconvolution of ms1 mass features,
support_code/nmdc/lipidomics/lipidomics_workflow.py:153: and adding of peak shape metrics of mass features to the mass feature dataframe.
support_code/nmdc/lipidomics/lipidomics_workflow.py:166: print("Finding mass features")
support_code/nmdc/lipidomics/lipidomics_workflow.py:167: myLCMSobj.find_mass_features()
support_code/nmdc/lipidomics/lipidomics_workflow.py:168: print("Found ", len(myLCMSobj.mass_features), " mass features")
```

### msdial — 11267 попаданий в 676 файлах

Файлы: `src/Common/ChartDrawing/Base/BasicClass.cs`, `src/Common/ChartDrawing/Base/Utility.cs`, `src/Common/ChartDrawing/DrawVisual/DrawVisual.cs`, `src/Common/ChartDrawing/DrawVisual/DrawVisualManualPeakModification.cs`, `src/Common/ChartDrawing/Legacy/ChromatogramBean.cs`, `src/Common/ChartDrawing/Legacy/ChromatogramXicViewModel.cs`, `src/Common/ChartDrawing/Legacy/PlainChromatogramXicForTableViewerLegacy.cs`, `src/Common/ChartDrawing/default/DefaultFE.cs`, `src/Common/ChartDrawing/default/DefaultUC.xaml.cs`, `src/Common/CommonStandard/Algorithm/ChromSmoothing/Smoothing.cs`, `src/Common/CommonStandard/Algorithm/CowAlignment/CowAlignment.cs`, `src/Common/CommonStandard/Algorithm/Function/MoleculerNetworking.cs`

Примеры:

```
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:36: var chromPeaks = DataAccess.ConvertRawPeakElementToChromatogramPeakList(ms1Spectrum.Spectrum);
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:38: var sChromPeaks = new Chromatogram(chromPeaks, ChromXType.Mz, ChromXUnit.Mz).ChromatogramSmoothing(parameter.SmoothingMethod, parameter.SmoothingLevel).AsPeakAr
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:42: return (new MsPeakSpotsSummary(new DataPoint[0]), new MsSnDistribution(Array.Empty<ChromatogramPeakFeature>()));
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:44: var peaks = MsdialDimsCore.ProcessFile.ConvertPeaksToPeakFeatures(peakPickResults, ms1Spectrum, provider, dataModel.AnalysisFile.AcquisitionType);
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:56: var peaks = new MsdialLcImMsApi.Algorithm.PeakSpotting(0, 100, parameter).Execute4DFeatureDetection(dataModel.AnalysisFile, provider, accProvider, parameter.Num
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:57: var flatten = peaks.SelectMany(peak => peak.DriftChromFeatures).ToList();
```

### mzmine — 26655 попаданий в 1976 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/javafx/util/FxIcons.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/AbundanceMeasure.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureInformation.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureStatus.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/Frame.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MZmineProject.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MobilityScan.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MobilityType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/RawDataFile.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/Scan.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/BinningMobilogramDataAccess.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/io/CountingInputStream.java:39: * want to be able to drop and commons-io deprecated theirs in 2.18. This is the whole feature.
utils/src/main/java/io/github/mzmine/util/io/JsonUtils.java:30: import com.fasterxml.jackson.core.StreamReadFeature;
utils/src/main/java/io/github/mzmine/util/io/JsonUtils.java:43: * {@link StreamReadFeature#USE_FAST_DOUBLE_PARSER} swaps {@link Double#parseDouble} for the
utils/src/main/java/io/github/mzmine/util/io/JsonUtils.java:48: JsonFactory.builder().enable(StreamReadFeature.USE_FAST_DOUBLE_PARSER).build());
taskcontroller/src/main/java/io/github/mzmine/taskcontrol/AbstractTask.java:71: *                       RawDataFiles, MassLists, FeatureLists). May be null if results shall be
taskcontroller/src/main/java/io/github/mzmine/taskcontrol/AbstractTask.java:81: *                       RawDataFiles, MassLists, FeatureLists). May be null if results shall be
```

### nomspectra — 1 попаданий в 1 файлах

Файлы: `nomspectra/spectra.py`

Примеры:

```
nomspectra/spectra.py:36: inheritan from list class with some extra features.
```

### openms — 23341 попаданий в 971 файлах

Файлы: `cmake/Windows/Contrib/Inetc/inetc.cpp`, `doc/code_examples/Tutorial_FeatureFinder.cpp`, `doc/code_examples/Tutorial_FeatureMap.cpp`, `doc/code_examples/Tutorial_FileIO.cpp`, `doc/code_examples/Tutorial_FileIO_Consumer.cpp`, `doc/code_examples/Tutorial_ImzMLFile.cpp`, `doc/code_examples/Tutorial_Labeled.cpp`, `doc/code_examples/Tutorial_MSChromatogram.cpp`, `doc/code_examples/Tutorial_MSExperiment.cpp`, `doc/code_examples/Tutorial_MapAlignment.cpp`, `doc/code_examples/Tutorial_ProForma.cpp`, `doc/code_examples/Tutorial_RangeManager.cpp`

Примеры:

```
tools/scripts/create_testdata_flqt.py:4: Producing the test data for TOPP_FeatureLinkerUnlabeledQT_5 and TOPP_FeatureLinkerUnlabeledQT_6
tools/scripts/create_testdata_flqt.py:7: fmaps = [ pyopenms.FeatureMap() for i in range(3)]
tools/scripts/create_testdata_flqt.py:22: # add 3 features to each map, but with a twist (adding different peptide ids to different maps)
tools/scripts/create_testdata_flqt.py:24: f = pyopenms.Feature()
tools/scripts/create_testdata_flqt.py:31: pyopenms.FeatureXMLFile().store("output_%s.featureXML" % i, fmap)
src/topp/AccurateMassSearch.cpp:20: #include <OpenMS/KERNEL/FeatureMap.h>
```

### ume — 62 попаданий в 6 файлах

Файлы: `R/as_ume_matrix.R`, `R/calc_logratio.R`, `R/tools.R`, `R/uplot_cluster.R`, `R/uplot_pca.R`, `R/zero_filling.R`

Примеры:

```
R/as_ume_matrix.R:1: #' Convert molecular formula data to a feature matrix
R/as_ume_matrix.R:4: #' Converts long molecular formula data into a wide sample-by-feature matrix
R/as_ume_matrix.R:7: #' Rows are defined by `grp`, columns by `feature_col`, and values by
R/as_ume_matrix.R:8: #' `value_col`. Duplicate group-feature combinations are aggregated.
R/as_ume_matrix.R:11: #' @param feature_col Character. Column defining features. Default is `"mf"`.
R/as_ume_matrix.R:18: #' @return A numeric matrix or data.frame with groups as rows and features as columns.
```

### xcms — 3129 попаданий в 57 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/MPI.R`, `R/MsExperiment-functions.R`, `R/MsExperiment.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment-plotting.R`, `R/XcmsExperiment.R`, `R/XcmsExperimentHdf5-functions.R`, `R/XcmsExperimentHdf5.R`, `R/do_adjustRtime-functions.R`

Примеры:

```
longtests/testthat.R:34: od_chrs <- chromatogram(od_x, mz = mzr)
R/AllGenerics.R:22: #' between chromatograms of different samples/dataset. Alignment is performed
R/AllGenerics.R:44: #'   alignment of features defined in all/most samples (corresponding to
R/AllGenerics.R:46: #'   retention time deviation of these features is described by fitting either a
R/AllGenerics.R:51: #'   based on features (i.e. chromatographic peaks grouped across samples) a
R/AllGenerics.R:59: #'   function identifies peak groups (features) for alignment in `object`
```

## gap_filling — Заполнение пропусков (gap filling)

Всего попаданий по всем проектам: **859**.

### corems — 33 попаданий в 4 файлах

Файлы: `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `support_code/nmdc/metabolomics/metabolomics_collection.py`

Примеры:

```
support_code/nmdc/metabolomics/metabolomics_collection.py:66: # Gap filling - check for induced mass features
support_code/nmdc/metabolomics/metabolomics_collection.py:71: print(f"\nGap Filling: ✓ Complete")
support_code/nmdc/metabolomics/metabolomics_collection.py:516: perform_gap_filling=True,
corems/mass_spectra/calc/lc_calc.py:1107: raise ValueError(f"No {mf_type} found, run {'gap filling' if induced_features else 'find_mass_features()'} first")
corems/mass_spectra/calc/lc_calc.py:5026: - gap_fill_expand_on_miss: If True, expands search window when no peak is found
corems/mass_spectra/calc/lc_calc.py:5060: expand_on_miss = self.parameters.lcms_collection.gap_fill_expand_on_miss
```

### msdial — 246 попаданий в 52 файлах

Файлы: `src/Common/ChartDrawing/Legacy/ChromatogramBean.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdial.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialGcms.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialLcms.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialMzML.cs`, `src/MSDIAL4/ChromatogramUI/ChromatogramAlignedEic/ChromatogramAlignedEicFE.cs`, `src/MSDIAL4/ChromatogramUI/ChromatogramBean.cs`, `src/MSDIAL4/MsDial/Parameter for GC/AnalysisParamSetForGcVM.cs`, `src/MSDIAL4/MsDial/Parameter for LC/AnalysisParamSetForLcVM.cs`, `src/MSDIAL4/MsDial/Parameter for LC/AnalysisParametersSettingVM.cs`, `src/MSDIAL4/MsDial/Process for GC/JointAlignerProcessGC.cs`, `src/MSDIAL4/MsDial/Process for GC/QuantAndGapFillingProcessForGC.cs`

Примеры:

```
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/LcmsAlignmentProcessFactory.cs:35: public override IGapFiller CreateGapFiller() {
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/LcmsAlignmentProcessFactory.cs:36: return new LcmsGapFiller(LcmsParameter, AlignmentRtCorrection);
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/LcmsGapFiller.cs:14: public class LcmsGapFiller : IGapFiller
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/LcmsGapFiller.cs:22: public LcmsGapFiller(double rtTol, double mzTol, SmoothingMethod smoothingMethod, int smoothingLevel, bool isForceInsert) {
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/LcmsGapFiller.cs:30: public LcmsGapFiller(
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/LcmsGapFiller.cs:34: param.SmoothingLevel, param.IsForceInsertForGapFilling) {
```

### mzmine — 296 попаданий в 74 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/FeatureFullDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/MissingValueType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/gapfilling/GapFillMzMatchDuplicateType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/statistics/DataTableProcessingHistory.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/statistics/DataTableUtils.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/statistics/FeatureListRowAbundances.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/mainwindow/workspace/AcademicWorkspace.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/MZmineModuleCategory.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/batchmode/BatchModeModulesList.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataanalysis/pca_new/PCAController.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataanalysis/pca_new/PCALoadingsExtractionParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataanalysis/pca_new/PCALoadingsExtractionTask.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/collections/BinarySearch.java:264: * @param noMatchDefault option to handle a missing value
utils/src/main/java/io/github/mzmine/util/collections/BinarySearch.java:282: * @param noMatchDefault option to handle a missing value
utils/src/main/java/io/github/mzmine/util/collections/BinarySearch.java:301: * @param noMatchDefault option to handle a missing value
utils/src/main/java/io/github/mzmine/util/collections/BinarySearch.java:318: * @param noMatchDefault option to handle a missing value
utils/src/main/java/io/github/mzmine/util/collections/BinarySearch.java:338: * @param noMatchDefault option to handle a missing value
utils/src/main/java/io/github/mzmine/util/collections/BinarySearch.java:358: * @param noMatchDefault       option to handle a missing value
```

### openms — 59 попаданий в 24 файлах

Файлы: `src/openms/include/OpenMS/ANALYSIS/ID/IDBoostGraph.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/ConfidenceScoring.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/MasstraceCorrelator.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/OpenSwathExportData.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/OpenSwathPercolatorScoring.h`, `src/openms/include/OpenMS/ANALYSIS/QUANTITATION/IsobaricChannelExtractor.h`, `src/openms/include/OpenMS/PROCESSING/NOISEESTIMATION/SignalToNoiseEstimatorMedianRapid.h`, `src/openms/source/ANALYSIS/ID/IDBoostGraph.cpp`, `src/openms/source/ANALYSIS/OPENSWATH/ConfidenceScoring.cpp`, `src/openms/source/ANALYSIS/QUANTITATION/IsotopeLabelingMDVs.cpp`, `src/openms/source/ANALYSIS/TARGETED/TargetedExperiment.cpp`, `src/openms/source/FEATUREFINDER/ElutionModelFitter.cpp`

Примеры:

```
src/topp/ProteinQuantifier.cpp:325: For @p aggregate, there is a qualitative difference between @p (intensity weighted) mean/median and @p sum in the effect that missing peptide abundances have (o
src/topp/SageAdapter.cpp:238: // impute values into config_template
src/topp/SageAdapter.cpp:240: std::string imputeConfigIntoTemplate()
src/topp/SageAdapter.cpp:611: std::string config = imputeConfigIntoTemplate();
src/topp/TextExporter.cpp:65: Missing values are represented by "-1" or "nan" in numeric fields and by blanks in character/text fields.
src/topp/OpenNuXL/OpenNuXL.cpp:993: setValidStrings_("filter", {"filter_pc_mass_error", "impute_decoy_medians", "filter_bad_partial_loss_scores", "autotune", "idfilter", "spectrumclusterfilter", "
```

### ume — 8 попаданий в 6 файлах

Файлы: `R/assign_formulas.R`, `R/check_objects.R`, `R/create_time_flattened_mfd.R`, `R/search_mf_targets.R`, `R/tools.R`, `R/uplot_pca.R`

Примеры:

```
R/assign_formulas.R:103: # Make sure that library has no missing values and that "vkey" exists
R/check_objects.R:11: #' Remove rows having missing values for either m/z (mz) or peak magnitude (i_magnitude).
R/check_objects.R:314: #' Remove rows having missing values for either m/z (mz) or peak magnitude (i_magnitude).
R/create_time_flattened_mfd.R:13: #' or contains only one distinct non-missing value, the function stops unless
R/create_time_flattened_mfd.R:85: "` contains only one distinct non-missing value. ",
R/search_mf_targets.R:45: stop("Column '", formula_col, "' contains missing values.")
```

### xcms — 217 попаданий в 34 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MPI.R`, `R/MsExperiment-functions.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment.R`, `R/XcmsExperimentHdf5-functions.R`, `R/c.R`, `R/do_findChromPeaks-functions.R`, `R/do_groupChromPeaks-functions.R`, `R/functions-Params.R`, `R/functions-XCMSnExp.R`

Примеры:

```
longtests/testthat.R:46: faahko_grouped_filled <- fillPeaks(xcms::group(faahko))
longtests/testthat.R:48: fillPeaks(xcms::group(retcor(xcms::group(updateObject(faahko)))))
R/AllGenerics.R:1123: #' @title Gap Filling
R/AllGenerics.R:1129: #' Gap filling integrate signal in the m/z-rt area of a feature (i.e., a
R/AllGenerics.R:1135: #' The method for gap filling along with its settings can be defined with
R/AllGenerics.R:1342: #' ## How many missing values do we have after peak filling?
```

## isotope_detection — Изотопы: паттерны, изотопологи, 13C/34S

Всего попаданий по всем проектам: **20037**.

### corems — 392 попаданий в 23 файлах

Файлы: `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/output/export.py`, `corems/mass_spectrum/calc/AutoRecalibration.py`, `corems/mass_spectrum/calc/CalibrationCalc.py`, `corems/mass_spectrum/input/coremsHDF5.py`, `corems/mass_spectrum/input/massList.py`, `corems/mass_spectrum/output/export.py`, `corems/molecular_formula/calc/MolecularFormulaCalc.py`

Примеры:

```
support_code/atom_parsers/AtomsDescription.py:17: "13C": Atom(atomic_number=6, symbol='C', mass_number='13', atomic_mass=13.0033548350723, natural_abundance=0.01078),
support_code/atom_parsers/AtomsDescription.py:39: "34S": Atom(atomic_number=16, symbol='S', mass_number='34', atomic_mass=33.96786700447, natural_abundance=0.042524),
support_code/atom_parsers/CreateAtomsDescription.py:8: filepath = str(path)+'/AtomicWeightsAndIsotopicCompNIST2019.txt'
support_code/nmdc/lipidomics/lipidomics_workflow.py:152: integration of mass features, annotation of c13 mass features, deconvolution of ms1 mass features,
support_code/nmdc/lipidomics/lipidomics_workflow.py:202: print("Annotating C13 mass features")
support_code/nmdc/lipidomics/lipidomics_workflow.py:203: myLCMSobj.find_c13_mass_features()
```

### formultitude — 272 попаданий в 17 файлах

Файлы: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.cs`, `FindChainsTest/FindChainsTestProgram.cs`, `Support/CChainBlocks.cs`, `Support/CElements.cs`, `Support/CFileReader.cs`, `Support/CIsotope.cs`, `TestFSDBSearch/Form1.cs`, `TestFSDBSearch/TotalDeclarations.cs`, `TestFSDBSearch/TotalIPDBSearch.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:66: public const double C13 = 13.0033548378;
CIA/FormultitudeProgram.cs:77: public enum EElemNumber { C = 0, H, O, N, C13, S, P, Na};
CIA/FormultitudeProgram.cs:78: double [] ElementMasses = new double [ Elements ] { C, H, O, N, C13, S, P, Na };
CIA/FormultitudeProgram.cs:458: //C13
CIA/FormultitudeProgram.cs:459: bool UseC13 = true;
CIA/FormultitudeProgram.cs:460: public bool GetUseC13() { return UseC13; }
```

### icbmocean — 22 попаданий в 2 файлах

Файлы: `create_homologous_series_network.R`, `isotope_ratio_deviance_function.R`

Примеры:

```
create_homologous_series_network.R:48: #isotope
create_homologous_series_network.R:60: #create B, a dataset that represents the summed abundance of all isotopes of the respective element
create_homologous_series_network.R:61: B<-data.frame(C=D$C+D$C13,H=D$H,Br=D$Br79+D$Br81,Cl=D$Cl+D$Cl37,Co=D$Co,Cu=D$Cu.i+D$Cu.ii+D$Cu65.i+D$Cu65.ii,Fe=D$Fe.ii+D$Fe.iii+D$Fe54.ii+D$Fe54.iii,I=D$I,N=D$
isotope_ratio_deviance_function.R:1: ### function to calculate isotope ratio deviances
isotope_ratio_deviance_function.R:3: isotope_deviance<-function(intensity_parent,intensity_child,number_of_atoms,q=0.0108,p=0.9892,number_of_isotopes=1,group=as.character(" "),color_by=as.character
isotope_ratio_deviance_function.R:4: #intensity_parent: intensity of the isotope free peak (e.g. pure C-12); can be a vector
```

### mfassignr — 1112 попаданий в 11 файлах

Файлы: `MFAssignR/R/FindCoreFormulae2.R`, `MFAssignR/R/FindCoreFormulae2_Halogen.R`, `MFAssignR/R/IsoFiltR.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`, `MFAssignR/R/RecalFunctions.R`, `MFAssignR/R/Utilities.R`, `MFAssignR/R/Utilities_Halogen.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`

Примеры:

```
Supplemental MFAssign Scripts/Full MFAssignR Example.R:27: #Isotope prescreening
Supplemental MFAssign Scripts/Full MFAssignR Example.R:28: Isotope <- IsoFiltR(Data)  #Input for IsoFiltR
Supplemental MFAssign Scripts/Full MFAssignR Example.R:30: Mono <- Isotope[["Mono"]]
Supplemental MFAssign Scripts/Full MFAssignR Example.R:31: Iso <- Isotope[["Iso"]]
MFAssignR/R/FindCoreFormulae2.R:71: S34 = env$loop[CompFactorToInt("S34")], N15 = env$loop[CompFactorToInt("N15")],
MFAssignR/R/FindCoreFormulae2_Halogen.R:71: S34 = env$loop[CompFactorToInt2("S34")], N15 = env$loop[CompFactorToInt2("N15")],
```

### msdial — 7795 попаданий в 400 файлах

Файлы: `src/Common/CommonStandard/Algorithm/Function/SpectrumHandler.cs`, `src/Common/CommonStandard/Algorithm/IsotopeCalc/IsotopeCalc.cs`, `src/Common/CommonStandard/Algorithm/Scoring/MsScanMatching.cs`, `src/Common/CommonStandard/Alignment/AlignedPeakPropertyBean.cs`, `src/Common/CommonStandard/Alignment/AlignmentPropertyBean.cs`, `src/Common/CommonStandard/Components/MoleculeMsReference.cs`, `src/Common/CommonStandard/Components/SpectrumPeak.cs`, `src/Common/CommonStandard/DataObj/Database/IupacDatabase.cs`, `src/Common/CommonStandard/DataObj/Ion/ProductIon.cs`, `src/Common/CommonStandard/DataObj/MspRecord.cs`, `src/Common/CommonStandard/DataObj/Property/AdductIon.cs`, `src/Common/CommonStandard/DataObj/Property/Formula.cs`

Примеры:

```
src/MSFINDER/MSFINDER/MainWindow.xaml.cs:271: this.ToggleButton_ShowIsotopeSpectrum.IsChecked = false;
src/MSFINDER/MSFINDER/MainWindow.xaml.cs:276: private void ToggleButton_ShowIsotopeSpectrum_Checked(object sender, RoutedEventArgs e)
src/MSFINDER/MSFINDER/MainWindow.xaml.cs:514: var exportFolder = @"D:\PROJECT_Plant Specialized Metabolites Annotations\Msfinder annotation results Plant C12-C13 manual curation−VS2";
src/MSFINDER/MsfinderConsoleAppCore/Process/SpectrumCuration.cs:112: NominalIsotopicPeakList = new List<Peak>() {
src/MSFINDER/MsfinderConsoleAppCore/Test/MergeMsdialMsfinderResult.cs:26: public string IsotopeNumber { get; set; }
src/MSFINDER/MsfinderConsoleAppCore/Test/MergeMsdialMsfinderResult.cs:63: Smiles = lineArray[11], IsotopeNumber = lineArray[14], Ms1Spectrum = lineArray[19],
```

### mzmine — 3564 попаданий в 325 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/IsotopePattern.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MergedMassSpectrum.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/Feature.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureListRow.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeature.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureListRow.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/annotationpriority/AnnotationSummary.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/CompoundDBAnnotation.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/FeatureAnnotation.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/SimpleCompoundDBAnnotation.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:60: //  NAME1("[M+2H-NH3]2+", "H2", "NH3", -15.0120166, PolarityType.POSITIVE, -3.51290442213519, 1, 2),//
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:68: NAME5("[M+2H]2+", "H2", "", PolarityType.POSITIVE, -1.81393441779917, 1, 2),//
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:72: NAME7("[M+2H+Na]3+", "NaH2", "", PolarityType.POSITIVE, -3.81393441779917, 1, 3),//
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:76: NAME9("[M+2Na]2+", "Na2", "", PolarityType.POSITIVE, -2.66780638212093, 1, 2),//
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:192: this.addedFormula != null ? FormulaUtils.getMonoisotopicMass(this.addedFormula) : 0d;
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:194: this.removedFormula != null ? FormulaUtils.getMonoisotopicMass(this.removedFormula) : 0d;
```

### nomspectra — 71 попаданий в 5 файлах

Файлы: `nomspectra/brutto.py`, `nomspectra/diff.py`, `nomspectra/gui.py`, `nomspectra/gui_design.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/brutto.py:47: Example: {'C':(1,60),'O_18':(0,3)} - content of carbon (main isotope) from 1 to 59,
nomspectra/brutto.py:48: conent of isotope 18 oxygen from 0 to 2.
nomspectra/brutto.py:73: temp = elems_mass_table.loc[elems_mass_table['element_isotop']==el].reset_index(drop=True)
nomspectra/brutto.py:83: temp=_merge_isotopes(temp)
nomspectra/brutto.py:86: raise Exception('For applying rules in brutto must be CHO elements or their isotopes')
nomspectra/brutto.py:111: def _merge_isotopes(gdf: pd.DataFrame) -> pd.DataFrame:
```

### openms — 6010 попаданий в 420 файлах

Файлы: `cmake/Windows/Contrib/Inetc/inetc.cpp`, `cmake/Windows/Contrib/Inetc/resource.h`, `doc/code_examples/Tutorial_AASequence.cpp`, `doc/code_examples/Tutorial_Element.cpp`, `doc/code_examples/Tutorial_EmpiricalFormula.cpp`, `doc/code_examples/Tutorial_ProForma.cpp`, `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/GTE/Mathematics/APConversion.h`, `src/openms/extern/GTE/Mathematics/NURBSSphere.h`, `src/openms/extern/GTE/Mathematics/Torus3.h`, `src/openms/extern/IsoSpec/IsoSpec/cwrapper.cpp`, `src/openms/extern/IsoSpec/IsoSpec/cwrapper.h`

Примеры:

```
src/topp/AssayGeneratorMetabo.cpp:16: #include <OpenMS/PROCESSING/DEISOTOPING/Deisotoper.h>
src/topp/AssayGeneratorMetabo.cpp:135: registerFlag_("deisotoping_use_deisotoper", "Use Deisotoper (if no fragment annotation is used)", false);
src/topp/AssayGeneratorMetabo.cpp:136: registerDoubleOption_("deisotoping_fragment_tolerance", "<num>", 1, "Tolerance used to match isotopic peaks", false);
src/topp/AssayGeneratorMetabo.cpp:137: registerStringOption_("deisotoping_fragment_unit", "<choice>", "ppm", "Unit of the fragment tolerance", false);
src/topp/AssayGeneratorMetabo.cpp:138: setValidStrings_("deisotoping_fragment_unit", ListUtils::create<std::string>("ppm,Da"));
src/topp/AssayGeneratorMetabo.cpp:139: registerIntOption_("deisotoping_min_charge", "<num>", 1, "The minimum charge considered", false);
```

### pyc2mc — 107 попаданий в 14 файлах

Файлы: `Image.py`, `main.py`, `modules/comparison.py`, `modules/file_operations.py`, `modules/resources_rc.py`, `src/loading/loading_function.py`, `src/pre_treatment_petroOrg.py`, `src/processing/fuse_replicates.py`, `src/processing/merge_function.py`, `src/processing/merge_merged_function.py`, `src/pyc2mc_ui.py`, `src/splitFinder/isotopes.py`

Примеры:

```
Image.py:18: img_str="iVBORw0KGgoAAAANSUhEUgAAAmwAAAGnCAYAAAAKUgvPAAAgAElEQVR4nMy9d5Bl53Undr573+scJ/XkATAYDDIGgEAikABIAiQIgABBSlpRDJLMXSq5pLV27a3aLatorWu9trVm2bJdG7Sl9aqkkpe
main.py:80: # Dict of most abundant isotopes and corresponding exact masses
main.py:82: df = pandas.read_csv("Isotopes.csv", sep=";")
main.py:84: self.isotopes_dict = dict(zip(df["Atom"], df["Mass"]))
modules/comparison.py:635: mass = mass + form[atom] * self.isotopes_dict[atom]
modules/comparison.py:653: mass = mass + form[atom] * self.isotopes_dict[atom]
```

### ume — 442 попаданий в 29 файлах

Файлы: `R/assign_formulas.R`, `R/build_isotope_map.R`, `R/calc_dbe.R`, `R/calc_eval_params.R`, `R/calc_exact_mass.R`, `R/calc_indeces.R`, `R/calc_isotope_pattern.R`, `R/calc_nm.R`, `R/calc_norm_int.R`, `R/calc_number_occurrence.R`, `R/calc_recalibrate_ms.R`, `R/check_neutral_mf.R`

Примеры:

```
R/assign_formulas.R:34: #' based on mass accuracy thresholds. If 13C, 15N, or 34S isotope information
R/assign_formulas.R:51: #'   \item Added isotope columns (`13C`, `15N`, `34S`) if missing in the library.
R/assign_formulas.R:96: '13C'  <- '15N' <- '34S' <- NULL
R/assign_formulas.R:223: # Add columns for heavy isotopes if not yet existing
R/assign_formulas.R:224: x <- c("13C", "15N", "34S")
R/assign_formulas.R:240: x <- mfd[, .N, list(file_id, mf, `13C`, `34S`, `15N`)][order(N)][N>1]
```

### xcms — 250 попаданий в 28 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment.R`, `R/cwTools.R`, `R/do_findChromPeaks-functions.R`, `R/functions-Chromatogram.R`, `R/functions-Params.R`, `R/functions-XCMSnExp.R`, `R/functions-XChromatogram.R`, `R/functions-XChromatograms.R`, `R/functions-xcmsFragments.R`

Примеры:

```
R/AllGenerics.R:442: #'   signal (`"maxo"`); only supported for `msLevel = 2L`.
R/AllGenerics.R:846: #'     `"maxo"` (the default) or `"into"` to use the maximal peak intensity
R/AllGenerics.R:1395: #' - [CentWavePredIsoParam()]: *centWave* with predicted isotopes. Peak
R/AllGenerics.R:1397: #'   isotopes.
R/AllGenerics.R:1560: setGeneric("findPeaks.addPredictedIsotopeFeatures", function(object, ...)
R/AllGenerics.R:1561: standardGeneric("findPeaks.addPredictedIsotopeFeatures"))
```

## adduct_ion_identity — Аддукты и ионные формы (ion identity)

Всего попаданий по всем проектам: **22692**.

### corems — 303 попаданий в 22 файлах

Файлы: `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/andiNetCDF.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectra/output/export.py`, `corems/mass_spectrum/calc/AutoRecalibration.py`, `corems/mass_spectrum/input/massList.py`, `corems/mass_spectrum/output/export.py`, `corems/molecular_formula/calc/MolecularFormulaCalc.py`, `corems/molecular_formula/factory/MolecularFormulaFactory.py`, `corems/molecular_formula/input/masslist_ref.py`

Примеры:

```
support_code/nmdc/filefinder.py:80: file_view.setSelectionMode(QAbstractItemView.MultiSelection)
support_code/nmdc/filefinder.py:83: f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
support_code/nmdc/nom/nom_workflow.py:167: mass_spectrum.molecular_search_settings.isProtonated = True
support_code/nmdc/nom/nom_workflow.py:169: mass_spectrum.molecular_search_settings.isAdduct = False
corems/encapsulation/constant.py:30: protonated_de_ion = "DE_OR_PROTONATED"
corems/encapsulation/constant.py:31: protonated = "protonated"
```

### formultitude — 203 попаданий в 9 файлах

Файлы: `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`, `TestFSDBSearch/Form1.cs`, `TestFSDBSearch/My/MyApplication.cs`, `TestFSDBSearch/TotalIPDBSearch.cs`, `TestFSDBSearch/TotalSupport/TotalMFMonoPeakCalculator.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.Designer.cs`

Примеры:

```
CiaUi/CiaAdvancedForm.cs:34: comboBoxCalRegressionModel.DataSource = Enum.GetValues( typeof( TotalCalibration.ttlRegressionType ) );
CiaUi/CiaAdvancedForm.cs:84: private void textBoxAdduct_KeyDown( object sender, KeyEventArgs e ) {
CiaUi/CiaAdvancedForm.cs:87: oCCia.Ipa.Adduct = textBoxAdduct.Text;
CiaUi/CiaAdvancedForm.cs:94: private void textBoxAdduct_Leave( object sender, EventArgs e ) {
CiaUi/CiaAdvancedForm.cs:96: oCCia.Ipa.Adduct = textBoxAdduct.Text;
CiaUi/CiaAdvancedForm.cs:136: oCCia.Ipa.Adduct = textBoxAdduct.Text;
```

### mfassignr — 367 попаданий в 10 файлах

Файлы: `MFAssignR/R/FindCoreFormulae2.R`, `MFAssignR/R/FindCoreFormulae2_Halogen.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`, `MFAssignR/R/RecalFunctions.R`, `MFAssignR/R/Utilities.R`, `MFAssignR/R/Utilities_Halogen.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`

Примеры:

```
Supplemental MFAssign Scripts/Full MFAssignR Example.R:35: Assign <- MFAssignCHO(Mono, Iso, ionMode = "neg", lowMW =50, highMW = 1000, ppm_err = 3, H_Cmin = 0.3,
Supplemental MFAssign Scripts/Full MFAssignR Example.R:71: Assign <- MFAssign(Mono2, Iso2, ionMode = "neg", lowMW =50, highMW = 1000,  Nx = 3, Sx = 1,  ppm_err = 3, H_Cmin = 0.3,
MFAssignR/R/FindCoreFormulae2.R:75: NH4 = env$loop[CompFactorToInt("NH4")], POE = env$loop[CompFactorToInt("POE")],
MFAssignR/R/FindCoreFormulae2_Halogen.R:77: NH4 = env$loop[CompFactorToInt2("NH4")], POE = env$loop[CompFactorToInt2("POE")],
MFAssignR/R/MFAssign.R:5: #' C, H, O, N, S, P, sodium (M), C13 (E), S34, N15, Deuterium (D), Cl, F, Cl37, NH4, and Z.
MFAssignR/R/MFAssign.R:7: #' There are user inputs for heteroatoms, adducts, and charge.
```

### msdial — 16395 попаданий в 650 файлах

Файлы: `src/Common/ChartDrawing/Helper/ExpressionHelper.cs`, `src/Common/ChartDrawing/IO/XamlToys.cs`, `src/Common/CommonMVVM/ChemView/ChemOntologyColor.cs`, `src/Common/CommonMVVM/Converter/AdductIonConverter.cs`, `src/Common/CommonStandard/Algorithm/Scoring/MsScanMatching.cs`, `src/Common/CommonStandard/Alignment/AlignedPeakPropertyBean.cs`, `src/Common/CommonStandard/Alignment/AlignmentPropertyBean.cs`, `src/Common/CommonStandard/Annotation info/LipidAnnotation.cs`, `src/Common/CommonStandard/Components/Interfaces/IIonProperty.cs`, `src/Common/CommonStandard/Components/Interfaces/IMSProperty.cs`, `src/Common/CommonStandard/Components/MSIonProperty.cs`, `src/Common/CommonStandard/Components/MSProperty.cs`

Примеры:

```
src/RawDataApp/RawDataViewer/Model/AnalysisDataModel.cs:15: public AnalysisDataModel(AnalysisFileBean analysisFile, MachineCategory machineCategory, IonMode ionMode, bool useProfile) {
src/RawDataApp/RawDataViewer/Model/AnalysisDataModel.cs:18: IonMode = ionMode;
src/RawDataApp/RawDataViewer/Model/AnalysisDataModel.cs:24: public IonMode IonMode { get; }
src/RawDataApp/RawDataViewer/Model/MainWindowModel.cs:28: public IonMode IonMode {
src/RawDataApp/RawDataViewer/Model/MainWindowModel.cs:29: get => _ionMode;
src/RawDataApp/RawDataViewer/Model/MainWindowModel.cs:30: set => SetProperty(ref _ionMode, value);
```

### mzmine — 2098 попаданий в 416 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/FilterableListView.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxListViews.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/MenuItems.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/dialogs/FilterableMenuPopup.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MergedMassSpectrum.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureListRow.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/CannotDetermineMassException.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/CompoundDBAnnotation.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/FeatureAnnotation.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/SimpleCompoundDBAnnotation.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/StringUtils.java:227: * M+H+2 will return the index of the last + so length -2
mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java:64: String PROPERTY_ADDUCT = "Adduct";
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:50: POSITIVE_HYDROGEN("[M+H]+", "H", "", PolarityType.POSITIVE, -0.268998651917666, 1, 1), //
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:58: AMMONIUM("[M+NH4]+", "NH4", "", PolarityType.POSITIVE, -2.49171512306525, 1, 1), //
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:66: NAME4("[M+H]2+", "H", "", PolarityType.POSITIVE, -3.33681316307951, 1, 2),//
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:70: NAME6("[M+H+Na]2+", "NaH", "", PolarityType.POSITIVE, -2.69999106549233, 1, 2),//
```

### openms — 3203 попаданий в 301 файлах

Файлы: `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/GTE/Mathematics/IndexAttribute.h`, `src/openms/extern/GTE/Mathematics/Quaternion.h`, `src/openms/extern/GTE/Mathematics/VertexAttribute.h`, `src/openms/extern/IsoSpec/IsoSpec/element_tables.cpp`, `src/openms/extern/SQLiteCpp/cpplint.py`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.h`, `src/openms/extern/nlohmann_json/tools/amalgamate/amalgamate.py`, `src/openms/extern/nlohmann_json/tools/serve_header/serve_header.py`, `src/openms/include/OpenMS/ANALYSIS/DECHARGING/FeatureDeconvolution.h`, `src/openms/include/OpenMS/ANALYSIS/DECHARGING/ILPDCWrapper.h`

Примеры:

```
tools/scripts/check_for_unused_testdata.py:49: test_files_not_in_sources = []
tools/scripts/check_for_unused_testdata.py:54: for source_file in source_files:
tools/scripts/check_for_unused_testdata.py:59: test_files_not_in_sources.append(test_file)
tools/scripts/check_for_unused_testdata.py:62: #for file in test_files_not_in_sources:
tools/scripts/check_for_unused_testdata.py:66: tracked = filter_tracked_files(test_files_not_in_sources) # print tracked files not referenced in sources
tools/scripts/check_for_unused_testdata.py:91: # file names in test data will be checked for existance in source file
```

### pyc2mc — 45 попаданий в 4 файлах

Файлы: `main.py`, `modules/pyc2mc_ui.py`, `modules/ui_main.py`, `src/pyc2mc_ui.py`

Примеры:

```
main.py:818: self.ui.list_loaded_file_compare.setSelectionMode(
main.py:821: self.ui.list_classes_distrib.setSelectionMode(
main.py:824: self.ui.list_compare_sample_1.setSelectionMode(
main.py:827: self.ui.list_compare_sample_2.setSelectionMode(
main.py:830: self.ui.list_sample_1_stats.setSelectionMode(
main.py:833: self.ui.list_sample_2_stats.setSelectionMode(
```

### ume — 4 попаданий в 2 файлах

Файлы: `R/calc_recalibrate_ms.R`, `R/search_mf_targets.R`

Примеры:

```
R/calc_recalibrate_ms.R:16: #' recalibration model.
R/search_mf_targets.R:16: #' @param adduct_mass Mass of the proton to convert neutral mass to measured
R/search_mf_targets.R:28: adduct_mass = 1.0072763) {
R/search_mf_targets.R:57: lib[, mz := mass - adduct_mass]
```

### xcms — 74 попаданий в 5 файлах

Файлы: `R/DataClasses.R`, `R/do_findChromPeaks-functions.R`, `R/methods-IO.R`, `R/methods-group-features.R`, `R/writemztab.R`

Примеры:

```
R/DataClasses.R:657: #'     of the matched filtration model peak.
R/do_findChromPeaks-functions.R:2338: ##   addNewAdductROIs  <- FALSE
R/do_findChromPeaks-functions.R:2362: ##   resultObj <- createAdditionalROIs(object, presentROIs.list, ppm, addNewIsotopeROIs, maxcharge, maxiso, mzIntervalExtension, addNewAdductROIs, polarity)
R/do_findChromPeaks-functions.R:2365: ##   numberOfAdditionalAdductROIs <- resultObj$numberOfAdditionalAdductROIs
R/do_findChromPeaks-functions.R:2382: ##   cat("Predicted ROIs: ", length(newROI.list), " new ROIs (", numberOfAdditionalIsotopeROIs, " isotope ROIs, ", numberOfAdditionalAdductROIs, " adduct ROIs) 
R/do_findChromPeaks-functions.R:2444: #' Reference for considered adduct distances:
```

## charge_state — Зарядовые состояния

Всего попаданий по всем проектам: **11631**.

### corems — 42 попаданий в 15 файлах

Файлы: `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectrum/factory/MassSpectrumClasses.py`, `corems/mass_spectrum/input/coremsHDF5.py`, `corems/mass_spectrum/input/massList.py`, `corems/mass_spectrum/output/export.py`, `corems/molecular_formula/calc/MolecularFormulaCalc.py`, `corems/molecular_formula/factory/MolecularFormulaFactory.py`, `corems/molecular_formula/input/masslist_ref.py`, `corems/molecular_id/calc/math_distance.py`, `corems/molecular_id/factory/MolecularLookupTable.py`

Примеры:

```
corems/ms_peak/factory/MSPeakClasses.py:19: The ion charge of the peak.
corems/molecular_id/calc/math_distance.py:334: #    z = 1 / 2 * (v + y)
corems/molecular_id/factory/MolecularLookupTable.py:116: Calculates the mass-to-charge ratio (m/z) of a molecular formula.
corems/molecular_id/factory/MolecularLookupTable.py:588: """Calculate the mass-to-charge ratio (m/z) of a molecular formula.
corems/molecular_id/factory/MolecularLookupTable.py:600: The mass-to-charge ratio (m/z) of a molecular formula.
corems/molecular_id/factory/molecularSQL.py:459: The ion charge.
```

### formultitude — 33 попаданий в 6 файлах

Файлы: `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`, `TestFSDBSearch/Form1.cs`, `TestFSDBSearch/TotalIPDBSearch.cs`, `TestFSDBSearch/TotalSupport/ROX_List.cs`

Примеры:

```
CiaUi/CiaAdvancedForm.Designer.cs:192: this.label51.Text = "Charge";
CiaUi/FormultitudeUIForm.cs:1106: xmlWriter.WriteStartElement( "Charge" );
CiaUi/FormultitudeUIForm.cs:1302: XmlNode = XmlDocRoot.SelectSingleNode( "//DefaultParameters/InputFilesTab/Charge" );
CiaUi/FormultitudeUIForm.Designer.cs:1945: this.label51.Text = "Charge";
TestFSDBSearch/Form1.cs:86: [AccessedThroughProperty("txtIPDBChargeState")]
TestFSDBSearch/Form1.cs:87: private TextBox _txtIPDBChargeState;
```

### icbmocean — 2 попаданий в 2 файлах

Файлы: `fastjoin.R`, `precisejoin.R`

Примеры:

```
fastjoin.R:4: #column mz = mass to charge ratio
precisejoin.R:4: #column mz = mass to charge ratio
```

### mfassignr — 22 попаданий в 6 файлах

Файлы: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`, `MFAssignR/R/Utilities.R`, `MFAssignR/R/Utilities_Halogen.R`

Примеры:

```
MFAssignR/R/MFAssign.R:7: #' There are user inputs for heteroatoms, adducts, and charge.
MFAssignR/R/MFAssign.R:78: #' Sets the amount of charge to be used in assignment. Default is 1.
MFAssignR/R/MFAssign.R:864: M = 0, NH4 = 0, Z= 0, POE = 0,
MFAssignR/R/MFAssign.R:880: M = 0, NH4 = 0, Z= 0, POE = 0, NOE = 0, D = 0, E = 0, KM_O = -42,
MFAssignR/R/MFAssignCHO.R:54: #' Sets the amount of charge to be used in assignment. Default is 1.
MFAssignR/R/MFAssignCHO.R:623: S34 = 0, P = 0, N15 = 0, Cl = 0, Fl = 0, Cl37 = 0, M = 0, NH4 = 0, Z= 0, POE = 0,
```

### msdial — 1231 попаданий в 359 файлах

Файлы: `src/Common/ChartDrawing/Chart/HeatmapControl.cs`, `src/Common/CommonStandard/Algorithm/Function/SpectrumHandler.cs`, `src/Common/CommonStandard/Algorithm/Scoring/MsScanMatching.cs`, `src/Common/CommonStandard/Components/Chromatogram.cs`, `src/Common/CommonStandard/Components/ExtractedIonChromatogram.cs`, `src/Common/CommonStandard/Components/MoleculeMsReference.cs`, `src/Common/CommonStandard/Components/SpectrumPeak.cs`, `src/Common/CommonStandard/DataObj/MgfRecord.cs`, `src/Common/CommonStandard/DataObj/Property/AdductIon.cs`, `src/Common/CommonStandard/FormulaData/AdductIonInformationBean.cs`, `src/Common/CommonStandard/Lipidomics/BMPEidSpectrumGenerator.cs`, `src/Common/CommonStandard/Lipidomics/BMPSpectrumGenerator.cs`

Примеры:

```
src/MSFINDER/MSFINDER/ViewModel/UserDefinedAdductVM.cs:80: Charge = adductIon.ChargeNumber;
src/MSFINDER/MSFINDER/ViewModel/UserDefinedAdductVM.cs:102: public int Charge
src/MSFINDER/MSFINDER/ViewModel/UserDefinedAdductVM.cs:107: OnPropertyChanged("Charge");
src/MSDIAL5/MsdialLcMsApi/Algorithm/Ms2Dec.cs:162: return MSDecObjectHandler.GetAndromedaSpectrum(chromPeakFeature, curatedSpectra, param, iupac, Math.Abs(chromPeakFeature.PeakCharacter.Charge));
src/MSDIAL5/MsdialLcMsApi/Algorithm/Ms2Dec.cs:224: return MSDecObjectHandler.GetAndromedaSpectrum(chromPeakFeature, curatedSpectra, param, iupac, Math.Abs(chromPeakFeature.PeakCharacter.Charge));
src/MSDIAL5/MsdialLcMsApi/Algorithm/Ms2Dec.cs:230: msdecResult.Spectrum = DataAccess.GetAndromedaMS2Spectrum(msdecResult.Spectrum, param, iupac, Math.Abs(chromPeakFeature.PeakCharacter.Charge));
```

### mzmine — 5315 попаданий в 3938 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/gui/DefaultHeadlessDesktop.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/Desktop.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/DesktopService.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/JavaFxDesktop.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/FilterableListView.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/FilterableListViewEvent.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/FilterableListViewEventHandler.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/GridRow.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/LabeledProgressBar.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/LabeledProgressBarCell.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/MappingListCell.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/NumberTextField.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/ExitCode.java:4: * Permission is hereby granted, free of charge, to any person
utils/src/main/java/io/github/mzmine/util/LayoutToRecordGenerator.java:4: * Permission is hereby granted, free of charge, to any person
utils/src/main/java/io/github/mzmine/util/StringUtils.java:4: * Permission is hereby granted, free of charge, to any person
utils/src/main/java/io/github/mzmine/util/StringUtils.java:164: // handle charge sign at the end like 2+
utils/src/main/java/io/github/mzmine/util/collections/BinarySearch.java:4: * Permission is hereby granted, free of charge, to any person
utils/src/main/java/io/github/mzmine/util/collections/CollectionUtils.java:4: * Permission is hereby granted, free of charge, to any person
```

### nomspectra — 21 попаданий в 3 файлах

Файлы: `nomspectra/gui.py`, `nomspectra/gui_design.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/gui.py:297: charge = int(self.cahrge_max.text())
nomspectra/gui.py:315: self.spec = self.spec.assign(generated_bruttos_table=self.gdf, rel_error=ppm, sign=sign, charge_max=charge)
nomspectra/gui_design.py:903: self.label_19.setText(_translate("MainWindow", "Max Charge"))
nomspectra/spectrum.py:283: charge_max: int = 1
nomspectra/spectrum.py:318: charge_max: int
nomspectra/spectrum.py:319: Maximum charge in m/z. Default 1.
```

### openms — 4557 попаданий в 848 файлах

Файлы: `doc/code_examples/Tutorial_AASequence.cpp`, `doc/code_examples/Tutorial_MSSpectrum.cpp`, `doc/code_examples/Tutorial_ProForma.cpp`, `src/openms/extern/GTE/Mathematics/AdaptiveSkeletonClimbing3.h`, `src/openms/extern/GTE/Mathematics/ApprPolynomial4.h`, `src/openms/extern/GTE/Mathematics/CLODPolyline.h`, `src/openms/extern/GTE/Mathematics/ContEllipsoid3MinCR.h`, `src/openms/extern/GTE/Mathematics/FastGaussianBlur3.h`, `src/openms/extern/GTE/Mathematics/FastMarch3.h`, `src/openms/extern/GTE/Mathematics/GradientAnisotropic3.h`, `src/openms/extern/GTE/Mathematics/Image3.h`, `src/openms/extern/GTE/Mathematics/ImageUtility3.h`

Примеры:

```
src/topp/AssayGeneratorMetabo.cpp:139: registerIntOption_("deisotoping_min_charge", "<num>", 1, "The minimum charge considered", false);
src/topp/AssayGeneratorMetabo.cpp:141: registerIntOption_("deisotoping_max_charge", "<num>", 1, "The maximum charge considered", false);
src/topp/AssayGeneratorMetabo.cpp:148: registerFlag_("deisotoping_annotate_charge", "Annotate the charge to the peaks", false);
src/topp/AssayGeneratorMetaboSirius.cpp:220: cmp_info.charge = stoi(row_data[8]);
src/topp/ClusterMassTraces.cpp:34: - clustering of features in an MS1 map (isotope traces, charge states etc)
src/topp/ClusterMassTraces.cpp:35: - clustering of features in an SWATH map (fragment ions from the same precursor, isotope traces, charge states etc)
```

### pyc2mc — 6 попаданий в 3 файлах

Файлы: `src/processing/merge_function.py`, `src/processing/merge_unattributed.py`, `src/stats/PCA_function.py`

Примеры:

```
src/processing/merge_function.py:164: The merge is working using the calculated mass-to-charge ratio
src/processing/merge_unattributed.py:14: The merge is working using the mass-to-charge ratio with a given tolerance in Dalton
src/stats/PCA_function.py:63: z = 2
src/stats/PCA_function.py:67: z = 0
src/stats/PCA_function.py:71: z = 1
src/stats/PCA_function.py:75: z = 2
```

### ume — 14 попаданий в 9 файлах

Файлы: `R/assign_formulas.R`, `R/check_neutral_mf.R`, `R/check_objects.R`, `R/data.R`, `R/filter.R`, `R/main_docu.R`, `R/read_xml_peaklist.R`, `R/uplot_ma_vs_mz.R`, `R/uplot_ms.R`

Примеры:

```
R/assign_formulas.R:127: Charge state: %s \n",
R/check_neutral_mf.R:25: #'   \item{has_charge}{Logical; `TRUE` if the formula ends with charge notation
R/check_neutral_mf.R:30: #'   resemble an InChIKey, has no terminal charge notation, and can be fully
R/check_neutral_mf.R:38: #' valence rules, isotope natural abundance, charge balance, or whether the
R/check_objects.R:344: if (!"mz" %in% names(mfd)) stop("No mass to charge (mz) values in mfd.")
R/data.R:13: #'   \item{mz}{Mass to charge ratio of the singly charged molecular ion (numeric)}
```

### xcms — 388 попаданий в 38 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MPI.R`, `R/MsExperiment-functions.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment-plotting.R`, `R/XcmsExperiment.R`, `R/XcmsExperimentHdf5-functions.R`, `R/XcmsExperimentHdf5.R`, `R/cwTools.R`, `R/do_adjustRtime-functions.R`, `R/do_findChromPeaks-functions.R`

Примеры:

```
R/AllGenerics.R:69: #'   mass-to-charge ratio (m/z) and retention time. see [LamaParama()] for more
R/AllGenerics.R:334: #'     `chromPeaks[, "mzmax"] + expandMz`. The default is `expandMz = 0`.
R/AllGenerics.R:810: #' @param mzmax `function` defining how the upper boundary of the m/z region
R/AllGenerics.R:812: #'     `mzmax = max` thus the largest `"mzmax"` value for all chromatographic
R/AllGenerics.R:938: #'     mzmin = min, mzmax = max, rtmin = min, rtmax = max)
R/AllGenerics.R:1141: #'   `"rtmin"`, `"rtmax"`, `"mzmin"` and `"mzmax"`. This method is not
```

## formula_assignment — Назначение брутто-формул

Всего попаданий по всем проектам: **12636**.

### corems — 860 попаданий в 39 файлах

Файлы: `conftest.py`, `corems/encapsulation/constant.py`, `corems/encapsulation/factory/parameters.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/encapsulation/input/parameter_from_json.py`, `corems/encapsulation/output/parameter_to_dict.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `corems/mass_spectra/factory/GC_Class.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/output/export.py`, `corems/mass_spectrum/calc/AutoRecalibration.py`

Примеры:

```
conftest.py:33: help="Skip tests that require the molecular formula database (postgres).",
conftest.py:44: "molecular_db: mark test as requiring the molecular formula database",
support_code/nmdc/lipidomics/lipidomics_workflow.py:23: from corems.molecular_id.search.molecularFormulaSearch import (
support_code/nmdc/lipidomics/lipidomics_workflow.py:24: SearchMolecularFormulas,
support_code/nmdc/lipidomics/lipidomics_workflow.py:25: SearchMolecularFormulasLC,
support_code/nmdc/lipidomics/lipidomics_workflow.py:79: # This cuts down on the number of molecular formulas searched hugely
```

### formultitude — 43 попаданий в 7 файлах

Файлы: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`, `Support/CIsotope.cs`, `TestFSDBSearch/TotalSupport/CannonMF.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:50: public short [] [] Candidates;
CIA/FormultitudeProgram.cs:58: public short [] Candidates;
CIA/FormultitudeProgram.cs:321: oAlignData.Candidates = new short [ oAlignData.AlignMasses.Length ];
CIA/FormultitudeProgram.cs:357: oAlignData.Candidates = new short [ AlignDict.Count ];
CIA/FormultitudeProgram.cs:367: int Candidates = 0;
CIA/FormultitudeProgram.cs:372: Candidates = Candidates + oData.Candidates[ Index][ oAlignData.Indexes [ PeakIndex][ Index] ];
```

### icbmocean — 1 попаданий в 1 файлах

Файлы: `create_homologous_series_network.R`

Примеры:

```
create_homologous_series_network.R:1: # create homologous series network : here, not from Kendricks mass defekt, but from molecular formulas directly
```

### mfassignr — 44 попаданий в 11 файлах

Файлы: `MFAssignR/R/IsoFiltR.R`, `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`, `MFAssignR/R/Utilities.R`, `MFAssignR/R/Utilities_Halogen.R`, `Supplemental MFAssign Scripts/Background Subtraction Guidelines.R`, `Supplemental MFAssign Scripts/Formula Assignment Reader.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`

Примеры:

```
Supplemental MFAssign Scripts/Background Subtraction Guidelines.R:1: ###Background Subtraction After Formula Assignment
Supplemental MFAssign Scripts/Formula Assignment Reader.R:23: render("Formula Assignment Markdown.rmd",output_file = paste0(substr(file_list[i],1,nchar(file_list[i])-4),".html"),
Supplemental MFAssign Scripts/Full MFAssignR Example.R:68: #Final formula assignment
Supplemental MFAssign Scripts/Full MFAssignR Example.R:69: #Parameters for both positive and negative mode formula assignment. This uses the formula extension version
MFAssignR/R/IsoFiltR.R:6: #' masses. This should be done prior to formula assignment in order
MFAssignR/R/KMDNoise.R:41: #'signal to noise cut for formula assignment.
```

### msdial — 6504 попаданий в 476 файлах

Файлы: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `src/Common/CommonStandard/Algorithm/Function/SpectrumHandler.cs`, `src/Common/CommonStandard/Algorithm/IsotopeCalc/IsotopeCalc.cs`, `src/Common/CommonStandard/Algorithm/PeakPick/PeakPick.cs`, `src/Common/CommonStandard/Algorithm/PeakPick/SpectralCentroiding.cs`, `src/Common/CommonStandard/Algorithm/Scoring/MsScanMatching.cs`, `src/Common/CommonStandard/Algorithm/Scoring/RetentionMatchPolicy.cs`, `src/Common/CommonStandard/Components/ChromatogramGlobalProperty_temp2.cs`, `src/Common/CommonStandard/DataObj/Ion/NeutralLoss.cs`, `src/Common/CommonStandard/DataObj/Ion/ProductIon.cs`, `src/Common/CommonStandard/DataObj/Property/Formula.cs`, `src/Common/CommonStandard/DataObj/Result/CandidatePopulation.cs`

Примеры:

```
src/MSFINDER/MSFINDER/MainWindow.xaml.cs:644: private void menuItem_AllStructureCandidateGenerateCheck_Click(object sender, RoutedEventArgs e)
src/MSFINDER/MSFINDER/MainWindow.xaml.cs:651: MsFinderValidation.AllStructureCandidateReports(this, this.mainWindowVM, filePath);
src/MSFINDER/MSFINDER/MainWindowVM.cs:242: FormulaFinderCurrentSearch.Process(this);
src/MSFINDER/MsfinderConsoleAppCore/Program.cs:80: //  .CombineDuplicatesBasedOnMolecularFormulaAssignment(
src/MSFINDER/MsfinderConsoleAppCore/Program.cs:85: //  .CombineDuplicatesBasedOnMolecularFormulaAssignment(
src/MSFINDER/MsfinderConsoleAppCore/Process/PredictProcess.cs:200: if (this.param.IsFormulaFinder) {
```

### mzmine — 1749 попаданий в 256 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MZmineProject.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureListRow.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/CompoundDBAnnotation.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/FeatureAnnotation.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/SimpleCompoundDBAnnotation.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/CompoundContradiction.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/CompoundRepresentativeSelector.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/CompoundRowUtils.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/LipidMatchListType.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java:58: String PROPERTY_FORMULA = "Molecular formula";
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:36: import org.openscience.cdk.interfaces.IMolecularFormula;
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:171: private final IMolecularFormula addedFormula;
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:172: private final IMolecularFormula removedFormula;
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:236: * See {@link FormulaUtils#neutralizeFormulaWithHydrogen(IMolecularFormula)} for formula
mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java:241: * ionization cannot be applied, see {@link #ionizeFormula(IMolecularFormula)}
```

### nomspectra — 69 попаданий в 6 файлах

Файлы: `nomspectra/brutto.py`, `nomspectra/diff.py`, `nomspectra/draw.py`, `nomspectra/gui.py`, `nomspectra/recal.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/brutto.py:39: def brutto_gen(elems: Optional[dict] = None, rules: bool = True) -> pd.DataFrame:
nomspectra/brutto.py:41: Generete brutto formula dataframe
nomspectra/brutto.py:46: Dictonary with elements and their range for generate brutto table
nomspectra/brutto.py:86: raise Exception('For applying rules in brutto must be CHO elements or their isotopes')
nomspectra/brutto.py:157: def gen_from_brutto(table: pd.DataFrame) -> pd.DataFrame:
nomspectra/brutto.py:159: Generate mass from brutto table
```

### openms — 2748 попаданий в 282 файлах

Файлы: `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/GTE/Mathematics/ApprCylinder3.h`, `src/openms/extern/GTE/Mathematics/ApprQuadratic2.h`, `src/openms/extern/GTE/Mathematics/ApprQuadratic3.h`, `src/openms/extern/GTE/Mathematics/ApprQuery.h`, `src/openms/extern/GTE/Mathematics/BandedMatrix.h`, `src/openms/extern/GTE/Mathematics/CholeskyDecomposition.h`, `src/openms/extern/GTE/Mathematics/ConstrainedDelaunay2.h`, `src/openms/extern/GTE/Mathematics/ContEllipse2MinCR.h`, `src/openms/extern/GTE/Mathematics/Delaunay2.h`, `src/openms/extern/GTE/Mathematics/Delaunay3.h`, `src/openms/extern/GTE/Mathematics/DistCircle3Circle3.h`

Примеры:

```
tools/ci/collect_wheel_licenses.py:179: candidate = os.path.join(rpath, reference[len("@rpath/"):])
tools/ci/collect_wheel_licenses.py:180: if os.path.exists(candidate):
tools/ci/collect_wheel_licenses.py:181: return candidate
tools/ci/collect_wheel_licenses.py:184: candidate = os.path.join(os.path.dirname(loader_path), reference.split("/", 1)[1])
tools/ci/collect_wheel_licenses.py:185: return candidate if os.path.exists(candidate) else None
tools/scripts/export_peptdeep_models_to_onnx.py:50: def get_model_class(module_name, candidate_names):
```

### pyc2mc — 261 попаданий в 19 файлах

Файлы: `main.py`, `modules/comparison.py`, `modules/data_views.py`, `modules/molecular_maps.py`, `modules/plot_helpers.py`, `modules/plots.py`, `modules/pyc2mc_ui.py`, `modules/window_actions.py`, `src/loading/loading_function.py`, `src/pre_processing_function.py`, `src/pre_treatment_petroOrg.py`, `src/processing/fuse_replicates.py`

Примеры:

```
main.py:504: # Displays composition page
main.py:505: self.ui.radio_composition.clicked.connect(
main.py:507: self.ui.page_composition
main.py:660: # Displays Composition widget
main.py:661: self.ui.radio_composition_compare.clicked.connect(
main.py:663: self.ui.page_composition_compare
```

### ume — 335 попаданий в 53 файлах

Файлы: `R/add_known_mf.R`, `R/as_mfd.R`, `R/as_peaklist.R`, `R/as_ume_matrix.R`, `R/assign_formulas.R`, `R/build_isotope_map.R`, `R/calc_data_summary.R`, `R/calc_dbe.R`, `R/calc_eval_params.R`, `R/calc_exact_mass.R`, `R/calc_indeces.R`, `R/calc_isotope_pattern.R`

Примеры:

```
R/add_known_mf.R:7: #' @family Formula assignment
R/add_known_mf.R:10: #' Annotate molecular formulas using metadata from `ume::known_mf`.
R/add_known_mf.R:12: #' The function joins molecular formulas with predefined molecular formula
R/add_known_mf.R:35: #'   \item character vectors of molecular formulas,
R/add_known_mf.R:41: #' Molecular formulas are matched against `known_mf`.
R/add_known_mf.R:51: #' known molecular formula categories.
```

### xcms — 22 попаданий в 6 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/XcmsExperiment-functions.R`, `R/functions-XCMSnExp.R`, `R/matchpeaks.R`, `src/massifquant/SegProc.cpp`

Примеры:

```
R/AllGenerics.R:2027: #' - Correlate the peak shapes of the candidate MS2 chromatographic peaks with
R/AllGenerics.R:2049: #'     representing candidate fragments of the original ion.
R/AllGenerics.R:2143: #' sets of merge candidates if they are (after expansion) overlapping in both
R/AllGenerics.R:2148: #' first ordered by their `"rtmin"` and merge candidates are defined iteratively
R/AllGenerics.R:2150: #' Candidate peaks are merged if the
R/AllGenerics.R:2157: #' between the apexes is used instead. Candidate peaks are not merged if all 3
```

## formula_scoring — Скоринг формул (ppm, confidence, ранжирование)

Всего попаданий по всем проектам: **12162**.

### corems — 211 попаданий в 30 файлах

Файлы: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/MZSearch.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `corems/mass_spectra/factory/GC_Class.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectra/output/export.py`, `corems/mass_spectrum/calc/AutoRecalibration.py`, `corems/mass_spectrum/calc/Calibration.py`

Примеры:

```
support_code/nmdc/metabolomics/lcms_metabolomics_targeted_search.py:58: # Here could do some post-processing to report the "best hit" per target and include confidence metrics
support_code/nmdc/nom/nom_workflow.py:23: from corems.molecular_id.search.priorityAssignment import OxygenPriorityAssignment
corems/ms_peak/calc/MSPeakCalc.py:85: Return the molecular formula with the highest confidence score.
corems/ms_peak/calc/MSPeakCalc.py:414: objective score (rmse)
corems/ms_peak/calc/MSPeakCalc.py:766: """Return the molecular formula with the highest confidence score score"""
corems/ms_peak/calc/MSPeakCalc.py:768: return max(self.molecular_formulas, key=lambda m: abs(m.confidence_score))
```

### formultitude — 76 попаданий в 13 файлах

Файлы: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`, `FindChains/FindChainsForm.Designer.cs`, `FindChainsTest/FindChainsTestProgram.cs`, `Support/CChainBlocks.cs`, `Support/CFileReader.cs`, `Support/CPpmError.cs`, `TestFSDBSearch/Form1.cs`, `TestFSDBSearch/TotalIPDBSearch.cs`, `TestFSDBSearch/TotalSupport/MF_BRW.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:165: const double PPM = 1e6;//parts per million
CIA/FormultitudeProgram.cs:166: public double PpmToError( double Mass, double ErrorPPM ) { return Mass * ErrorPPM / PPM; }
CIA/FormultitudeProgram.cs:167: public double SignedMassErrorPPM( double ReferenceMass, double Mass ) { return ( Mass - ReferenceMass ) / ReferenceMass * PPM; }
CIA/FormultitudeProgram.cs:168: public double AbsMassErrorPPM( double ReferenceMass, double Mass ) { return Math.Abs( ( Mass - ReferenceMass ) / ReferenceMass * PPM ); }
CIA/FormultitudeProgram.cs:395: public enum RelationshipErrorType { AMU, PPM, GapPPM };
CIA/FormultitudeProgram.cs:438: //formula score
```

### mfassignr — 24 попаданий в 7 файлах

Файлы: `MFAssignR/R/IsoFiltR.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`, `MFAssignR/R/RecalFunctions.R`, `Supplemental MFAssign Scripts/Background Subtraction Guidelines.R`

Примеры:

```
Supplemental MFAssign Scripts/Background Subtraction Guidelines.R:55: #You can decide what error limit you want to allow, though 3 ppm is typically pretty good.
MFAssignR/R/IsoFiltR.R:37: #' Sets the maximum allowed error (ppm) for 34S mass matching, default is 5
MFAssignR/R/IsoFiltR.R:40: #' Sets the maximum allowed error (ppm) for 13C mass matching, default is 5
MFAssignR/R/MFAssign.R:92: #' ppm_err parameter sets the error tolerance (ppm) for formula assignment. Default is 3.
MFAssignR/R/MFAssign.R:94: #' iso_err parameter sets the error tolerance (ppm) for polyisotope matching. Default is 3.
MFAssignR/R/MFAssign.R:185: fitMode <- "ppm"
```

### msdial — 2956 попаданий в 340 файлах

Файлы: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/MsScanMatchingBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/DataStructure/PriorityQueueBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Program.cs`, `src/Common/ChartDrawing/UI/DockItemsControl.cs`, `src/Common/CommonMVVM/Common/DisposableCollection.cs`, `src/Common/CommonStandard/Algorithm/CowAlignment/CowAlignment.cs`, `src/Common/CommonStandard/Algorithm/CowAlignment/FunctionElement.cs`, `src/Common/CommonStandard/Algorithm/Function/MolecularNetworkInstance.cs`, `src/Common/CommonStandard/Algorithm/Function/MoleculerNetworking.cs`, `src/Common/CommonStandard/Algorithm/Function/SpectrumHandler.cs`, `src/Common/CommonStandard/Algorithm/Scoring/Ms2ScanMatching.cs`

Примеры:

```
src/MSFINDER/MsfinderConsoleAppCore/Process/MsSearchProcess.cs:130: "Precursor mz\tPrecursor type\tRank\tInChIKey\tSMILES\tTotal score");
src/MSFINDER/MsfinderConsoleAppCore/Process/PredictProcess.cs:278: "Mass error\tFormula score\tDatabases");
src/MSFINDER/MsfinderConsoleAppCore/Process/PredictProcess.cs:309: "Precursor mz\tPrecursor type\tStructure rank\tTotal score\tDatabases\tFormula\tOntology\tInChIKey\tSMILES");
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:1: ﻿using Msdial.Lcms.Dataprocess.Scoring;
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:210: if (param.MassTolType == MassToleranceType.Ppm) ms1tol = (float)MolecularFormulaUtility.ConvertPpmToMassAccuracy(200.0000, param.Mass1Tolerance); // use 200.000
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:212: var ppm = Math.Abs(MolecularFormulaUtility.PpmCalculator(500.00, 500.00 + ms1tol));
```

### mzmine — 2038 попаданий в 422 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxTextFlows.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/util/FxLayout.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/dialogs/FilterableMenuPopup.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/mvci/LatestTaskScheduler.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/IsotopePattern.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureListRow.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularDataRecord.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureListRow.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/annotationpriority/AnnotationSummary.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/annotationpriority/AnnotationSummaryOrder.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/math/ScoreAccumulator.java:30: private double score;
utils/src/main/java/io/github/mzmine/util/math/ScoreAccumulator.java:34: * Add a score multiplied by weight and keep track of weights
utils/src/main/java/io/github/mzmine/util/math/ScoreAccumulator.java:36: public void add(double score, double weight) {
utils/src/main/java/io/github/mzmine/util/math/ScoreAccumulator.java:37: this.score += score * weight;
utils/src/main/java/io/github/mzmine/util/math/ScoreAccumulator.java:41: * Add a score multiplied by weight and keep track of weights
utils/src/main/java/io/github/mzmine/util/math/ScoreAccumulator.java:43: public void add(float score, double weight) {
```

### nomspectra — 44 попаданий в 6 файлах

Файлы: `nomspectra/diff.py`, `nomspectra/draw.py`, `nomspectra/gui.py`, `nomspectra/gui_design.py`, `nomspectra/recal.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/diff.py:56: Optional, default 1 ppm. Relative error for assign peaks by massdif
nomspectra/draw.py:478: ax.set_ylabel('error, ppm')
nomspectra/gui.py:296: ppm = float(self.assign_error_ppm.text())
nomspectra/gui.py:315: self.spec = self.spec.assign(generated_bruttos_table=self.gdf, rel_error=ppm, sign=sign, charge_max=charge)
nomspectra/gui_design.py:900: self.label_10.setText(_translate("MainWindow", "Err ppm"))
nomspectra/recal.py:47: ErrorTable object contain table error in ppm for mass, default 100 string
```

### openms — 6287 попаданий в 618 файлах

Файлы: `doc/code_examples/Tutorial_IdentificationClasses.cpp`, `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `share/OpenMS/SCRIPTS/InternalCalibration_Residuals.R`, `src/openms/extern/GTE/Mathematics/IncrementalDelaunay2.h`, `src/openms/extern/GTE/Mathematics/MinHeap.h`, `src/openms/extern/GTE/Mathematics/SymmetricEigensolver.h`, `src/openms/extern/GTE/Mathematics/SymmetricEigensolver3x3.h`, `src/openms/extern/GTE/Mathematics/VertexCollapseMesh.h`, `src/openms/extern/IsoSpec/IsoSpec/isoSpec++.cpp`, `src/openms/extern/IsoSpec/IsoSpec/isoSpec++.h`, `src/openms/extern/IsoSpec/IsoSpec/marginalTrek++.h`, `src/openms/extern/SQLiteCpp/cpplint.py`

Примеры:

```
tools/scripts/plot_pasef_frames.py:121: rank = int(round(k * m / n)) - 1  # 1-based quantile → 0-based index
tools/scripts/plot_pasef_frames.py:122: rank = max(0, min(m - 1, rank))
tools/scripts/plot_pasef_frames.py:123: picks.append(tics[rank])
src/topp/AssayGeneratorMetabo.cpp:104: registerStringOption_("ambiguity_resolution_mz_tolerance_unit", "<choice>", "ppm", "Unit of the ambiguity_resolution_mz_tolerance", false, true);
src/topp/AssayGeneratorMetabo.cpp:105: setValidStrings_("ambiguity_resolution_mz_tolerance_unit", ListUtils::create<std::string>("ppm,Da"));
src/topp/AssayGeneratorMetabo.cpp:131: setValidStrings_("precursor_recalibration_window_unit", ListUtils::create<std::string>("Da,ppm"));
```

### pyc2mc — 12 попаданий в 7 файлах

Файлы: `modules/file_operations.py`, `modules/plot_helpers.py`, `modules/plots.py`, `modules/pyc2mc_ui.py`, `src/loading/loading_function.py`, `src/processing/merge_unattributed.py`, `src/pyc2mc_ui.py`

Примеры:

```
modules/file_operations.py:419: "Tolerance in ppm (min = 0.01 max : 50): ",
modules/plots.py:199: ### ppm vs m/z ###
modules/plots.py:246: plt.ylabel("Error (ppm)", fontsize=font_size + 2)
modules/plots.py:275: plt.ylabel("Error (ppm)", fontsize=font_size)
modules/plot_helpers.py:73: ):  # Scatter plot for DBE, Van krevelen, Kendricks and ppm vs mz plots.
modules/pyc2mc_ui.py:12242: self.radio_ppm.setText(_translate("MainWindow", "Ppm vs mz"))
```

### ume — 144 попаданий в 24 файлах

Файлы: `R/as_mfd.R`, `R/assign_formulas.R`, `R/build_isotope_map.R`, `R/calc_data_summary.R`, `R/calc_eval_params.R`, `R/calc_ma.R`, `R/calc_norm_int.R`, `R/calc_recalibrate_ms.R`, `R/check_objects.R`, `R/create_time_flattened_mfd.R`, `R/data.R`, `R/filter.R`

Примеры:

```
R/assign_formulas.R:6: #' molecular formulas based on the mass accuracy (`ma_dev`) provided [calc_ma_abs()].
R/assign_formulas.R:19: # @param ma_dev Mass accuracy in +/- parts per million (ppm)
R/assign_formulas.R:34: #' based on mass accuracy thresholds. If 13C, 15N, or 34S isotope information
R/assign_formulas.R:48: #'       \item `ppm` — mass error in parts per million.
R/assign_formulas.R:55: #' mass accuracy threshold.
R/assign_formulas.R:115: # Check peaklist, calculate neutral mass and mass accuracy thresholds
```

### xcms — 370 попаданий в 41 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/MsExperiment.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment-plotting.R`, `R/XcmsExperiment.R`, `R/XcmsExperimentHdf5-functions.R`, `R/XcmsExperimentHdf5.R`, `R/databases.R`, `R/do_adjustRtime-functions.R`, `R/do_findChromPeaks-functions.R`

Примеры:

```
R/AllGenerics.R:475: #' @param ppm `numeric(1)` to expand the m/z range of each peak (on each side)
R/AllGenerics.R:1158: #'   guaranteed m/z width expressed in ppm of the features' m/z and centered
R/AllGenerics.R:1162: #'   `"mzmin"`, and the feature's m/z *minus* `minMzWidthPpm / 2` ppm of its
R/AllGenerics.R:1237: #'     expansion is applied *after* `expandMz` and `ppm`.
R/AllGenerics.R:1246: #'     minimal guaranteed m/z width (expressed in ppm of the feature's m/z)
R/AllGenerics.R:1275: #' @param ppm for `FillChromPeaksParam`: `numeric(1)` optionally specifying
```

## ambiguity_handling — Неоднозначные/неназначенные результаты

Всего попаданий по всем проектам: **1690**.

### corems — 40 попаданий в 5 файлах

Файлы: `corems/encapsulation/constant.py`, `corems/mass_spectrum/calc/Calibration.py`, `corems/mass_spectrum/calc/MassSpectrumCalc.py`, `corems/mass_spectrum/output/export.py`, `corems/molecular_id/factory/classification.py`

Примеры:

```
corems/encapsulation/constant.py:27: unassigned = "unassigned"
corems/molecular_id/factory/classification.py:107: self._ms_grouped_class[Labels.unassigned] = list()
corems/molecular_id/factory/classification.py:134: self._ms_grouped_class.get(Labels.unassigned).append(ms_peak)
corems/molecular_id/factory/classification.py:184: if classe != Labels.unassigned:
corems/molecular_id/factory/classification.py:186: if classe != Labels.unassigned:
corems/molecular_id/factory/classification.py:279: if self.choose_mf or classe == Labels.unassigned:
```

### mfassignr — 174 попаданий в 5 файлах

Файлы: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`

Примеры:

```
Supplemental MFAssign Scripts/Full MFAssignR Example.R:40: Unassigned1 <- Assign[["None"]]
Supplemental MFAssign Scripts/Full MFAssignR Example.R:77: Unassigned2 <- Assign[["None"]]
MFAssignR/R/MFAssign.R:12: #' Additionally, an option to remove ambiguous assignments based on choosing
MFAssignR/R/MFAssign.R:127: #' Turns on or off increased ambiguity for assignments. Default is "off".
MFAssignR/R/MFAssign.R:136: #' @return list(Unambig = Unambig, Ambig = Ambigout, None = unassigned, MSAssign = MZ,
MFAssignR/R/MFAssign.R:139: #'   Unambig - data frame containing unambiguous assignments
```

### msdial — 54 попаданий в 23 файлах

Файлы: `src/Common/CommonStandard/DataObj/Result/MsScanMatchResult.cs`, `src/Common/CommonStandard/Lipidomics/LipidomicsConverter.cs`, `src/Common/CommonStandard/Lipidomics/LipoqualityDatabaseManagerUtility.cs`, `src/Common/NCDK.Display/Depict/DepictionGenerator.cs`, `src/Common/NCDK/Aromaticities/Kekulization.cs`, `src/Common/NCDK/Fingerprints/CircularFingerprinter.cs`, `src/Common/NCDK/Graphs/Invariant/Canon.cs`, `src/Common/NCDK/IO/MDLV3000Writer.cs`, `src/Common/NCDK/QSAR/Descriptors/Moleculars/ALOGPDescriptor.cs`, `src/Common/NCDK/QSAR/Descriptors/Moleculars/SmallRingDescriptor.cs`, `src/Common/NCDK/SMARTS/Smarts.cs`, `src/Common/NCDK/Stereo/CyclicCarbohydrateRecognition.cs`

Примеры:

```
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/AutomaticAlignmentRetentionTimeCorrection.cs:609: if (candidates.Count > 1) return new AnchorMatch(reference, null, "Ambiguous");
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/AutomaticAlignmentRetentionTimeCorrection.cs:628: // quality as a tie breaker. This keeps the configured anchor count while still spanning
src/MSDIAL5/MsdialCore/Algorithm/RetentionTimeCorrectionPeakSelector.cs:48: /// Multiple candidates passed the filters, and the highest peak height was selected.
src/MSDIAL5/MsdialCore/Algorithm/RetentionTimeCorrectionPeakSelector.cs:52: /// Multiple candidates passed the filters, and the candidate closest to the reference RT was selected.
src/MSDIAL5/MsdialCore/Algorithm/RetentionTimeCorrectionPeakSelector.cs:56: /// Multiple candidates passed the filters, and the best weighted intensity/RT score was selected.
src/MSDIAL5/MsdialCore/Export/AnnotationCandidates.cs:16: /// reader could not tell an unambiguous match from one where the search did not choose between two
```

### mzmine — 15 попаданий в 11 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/correlation/RowGroup.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/engine/ElementAutoDetector.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_compoundgrouper/CompoundGrouperParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_compoundgrouper/SimpleSeederComponentizer.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/id_ion_identity_networking/ionidnetworking/IonNetworkingTask.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/id_lipidid/scoring/LipidQcScoringUtils.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/norm_intensity/StandardCompoundNormalizationTypeModule.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/io/import_rawdata_bruker_baf/library/tables/Ms2Table.java`, `mzmine-community/src/main/java/io/github/mzmine/parameters/parametertypes/OffDefaultOn.java`, `mzmine-community/src/main/java/io/github/mzmine/util/CorrelationGroupingUtils.java`, `mzmine-community/src/main/java/io/github/mzmine/util/FeatureTableFXUtil.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/util/CorrelationGroupingUtils.java:53: * identify each edge unambiguously.
mzmine-community/src/main/java/io/github/mzmine/util/FeatureTableFXUtil.java:187: *           ambiguous {@code resolveCompoundRow} result through downstream bindings.</li>
mzmine-community/src/main/java/io/github/mzmine/parameters/parametertypes/OffDefaultOn.java:31: * ambiguity. This is meant to replace a
mzmine-community/src/main/java/io/github/mzmine/modules/io/import_rawdata_bruker_baf/library/tables/Ms2Table.java:54: // need to create aliases, otherwise it is ambiguous for sql
mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_compoundgrouper/CompoundGrouperParameters.java:53: + "single-adduct forms in a tier order (M+H / M-H first), with an intensity tiebreak "
mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_compoundgrouper/SimpleSeederComponentizer.java:298: * Greedy density-first detector. While unassigned residual nodes remain, pick the highest-degree
```

### nomspectra — 33 попаданий в 5 файлах

Файлы: `nomspectra/diff.py`, `nomspectra/draw.py`, `nomspectra/gui.py`, `nomspectra/recal.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/diff.py:225: spec = spec.drop_unassigned()
nomspectra/diff.py:226: spec2 = spec2.drop_unassigned()
nomspectra/diff.py:283: mass = self.spec.drop_unassigned().calc_error().table['calc_mass'].values
nomspectra/diff.py:340: res = super().assign(generated_bruttos_table=generated_bruttos_table, abs_error=error, sign='0').drop_unassigned().table
nomspectra/draw.py:159: spec = spec.copy().drop_unassigned()
nomspectra/draw.py:194: title = f'{spec.metadata["name"]}, {len(spec.drop_unassigned())} formulas'
```

### openms — 1372 попаданий в 256 файлах

Файлы: `src/openms/extern/GTE/Mathematics/AdaptiveSkeletonClimbing2.h`, `src/openms/extern/GTE/Mathematics/AdaptiveSkeletonClimbing3.h`, `src/openms/extern/GTE/Mathematics/MarchingCubes.h`, `src/openms/extern/GTE/Mathematics/SurfaceExtractorCubes.h`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.h`, `src/openms/extern/evergreen/src/BitReversedShuffle/SemiRecursiveShuffle.hpp`, `src/openms/extern/nlohmann_json/include/nlohmann/detail/json_pointer.hpp`, `src/openms/extern/nlohmann_json/include/nlohmann/json.hpp`, `src/openms/extern/nlohmann_json/single_include/nlohmann/json.hpp`, `src/openms/extern/simde/simde/simde-detect-clang.h`, `src/openms/extern/simde/simde/simde-diagnostic.h`

Примеры:

```
src/topp/AssayGeneratorMetabo.cpp:103: registerDoubleOption_("ambiguity_resolution_mz_tolerance", "<num>", 10.0, "Mz tolerance for the resolution of identification ambiguity over multiple files", fal
src/topp/AssayGeneratorMetabo.cpp:104: registerStringOption_("ambiguity_resolution_mz_tolerance_unit", "<choice>", "ppm", "Unit of the ambiguity_resolution_mz_tolerance", false, true);
src/topp/AssayGeneratorMetabo.cpp:105: setValidStrings_("ambiguity_resolution_mz_tolerance_unit", ListUtils::create<std::string>("ppm,Da"));
src/topp/AssayGeneratorMetabo.cpp:106: registerDoubleOption_("ambiguity_resolution_rt_tolerance", "<num>", 10.0, "RT tolerance in seconds for the resolution of identification ambiguity over multiple 
src/topp/AssayGeneratorMetabo.cpp:174: double ar_mz_tol = getDoubleOption_("ambiguity_resolution_mz_tolerance");
src/topp/AssayGeneratorMetabo.cpp:175: std::string ar_mz_tol_unit_res = getStringOption_("ambiguity_resolution_mz_tolerance_unit");
```

### ume — 2 попаданий в 2 файлах

Файлы: `R/get_isotope_info.R`, `R/tools.R`

Примеры:

```
R/get_isotope_info.R:38: # Remove column names that can be ambiguous
R/tools.R:455: "[UME] Ambiguous alias mapping for canonical name '", canon,
```

## chemical_rules — Химические правила (DBE, валентность, диапазоны)

Всего попаданий по всем проектам: **1889**.

### corems — 102 попаданий в 12 файлах

Файлы: `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectrum/output/export.py`, `corems/molecular_formula/calc/MolecularFormulaCalc.py`, `corems/molecular_formula/factory/MolecularFormulaFactory.py`, `corems/molecular_formula/input/masslist_ref.py`, `corems/molecular_id/factory/MolecularLookupTable.py`, `corems/molecular_id/factory/classification.py`, `corems/molecular_id/factory/molecularSQL.py`, `corems/molecular_id/search/molecularFormulaSearch.py`, `corems/molecular_id/search/priorityAssignment.py`

Примеры:

```
corems/encapsulation/constant.py:49: This class includes key properties of atoms (and the electron) and isotopes, including their exact masses, relative abundances, and covalences.
corems/encapsulation/constant.py:713: atoms_covalence = {
corems/molecular_id/factory/classification.py:68: * dbe(classe).
corems/molecular_id/factory/classification.py:69: Returns a list of DBE for specified class.
corems/molecular_id/factory/classification.py:256: def dbe(self, classe):
corems/molecular_id/factory/classification.py:257: """Return a list of DBE for specified class"""
```

### formultitude — 26 попаданий в 5 файлах

Файлы: `CIA/FormultitudeProgram.cs`, `CiaUi/FormultitudeUIForm.cs`, `Support/CIsotope.cs`, `TestFSDBSearch/TotalSupport/CannonMF.cs`, `TestFSDBSearch/TotalSupport/Isotope.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:79: short [] ElemValences = { 4, 1, 2, 3, 4, 2, 3, 1};
CIA/FormultitudeProgram.cs:469: "Valence rules",
CIA/FormultitudeProgram.cs:473: "Integer DBE"
CIA/FormultitudeProgram.cs:1304: //Golden rule 2 "Valence rule"
CIA/FormultitudeProgram.cs:1307: //Filter 2. Valence rules
CIA/FormultitudeProgram.cs:1310: //short [] ElemValences = { 4, 1, 2, 3, 4, 2, 3, 1 };
```

### mfassignr — 232 попаданий в 7 файлах

Файлы: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`, `MFAssignR/R/RecalFunctions.R`, `MFAssignR/R/Utilities.R`, `MFAssignR/R/Utilities_Halogen.R`

Примеры:

```
MFAssignR/R/MFAssign.R:80: #' Sets the valence of Sulfur. Default is 2.
MFAssignR/R/MFAssign.R:82: #' Sets the valence of Nitrogen. Default is 3.
MFAssignR/R/MFAssign.R:84: #' Sets the valence of Sulfur 34. Default is 2.
MFAssignR/R/MFAssign.R:86: #' Sets the valence of Nitrogen 15. Default is 3.
MFAssignR/R/MFAssign.R:88: #' Sets the valence of Phosphorus. Default is 5.
MFAssignR/R/MFAssign.R:107: #' DBEOmin parameter sets lower limit for DBE minus oxygen QA parameter. Default is -13.
```

### msdial — 656 попаданий в 85 файлах

Файлы: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/MsScanMatchingBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/DataStructure/PriorityQueueBenchmark.cs`, `benchmark/CompMs/CommonStandardBenchmark/Program.cs`, `benchmark/CompMs/CommonStandardBenchmark/Tests.cs`, `src/Common/CommonStandard/FormulaGenerator/DataObj/ValenceDictionary.cs`, `src/Common/CommonStandard/FormulaGenerator/FormulaGenerator.cs`, `src/Common/CommonStandard/FormulaGenerator/Function/FragmentAssigner.cs`, `src/Common/CommonStandard/FormulaGenerator/Function/SevenGoldenRulesCheck.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsfinder.cs`, `src/Common/CommonStandard/Parameters/AnalysisParamOfMsfinder.cs`, `src/Common/CommonStandard/Parser/MsFinderIniParser.cs`

Примеры:

```
src/MSFINDER/MsfinderCommonStandard/Utility/MsFinderIniParcer.cs:45: if (Regex.IsMatch(line, "LewisAndSeniorCheck=", RegexOptions.IgnoreCase)) {
src/MSFINDER/MsfinderCommonStandard/Utility/MsFinderIniParcer.cs:47: if (ans.Length > 0 && ans.Contains("F")) param.IsLewisAndSeniorCheck = false;
src/MSFINDER/MsfinderCommonStandard/Utility/MsFinderIniParcer.cs:48: else param.IsLewisAndSeniorCheck = true;
src/MSFINDER/MsfinderCommonStandard/Utility/MsFinderIniParcer.cs:654: sw.WriteLine("LewisAndSeniorCheck=" + param.IsLewisAndSeniorCheck);
src/MSFINDER/MSFINDER/ViewModel/AnalysisParameterSettingVM.cs:33: IsLewisAndSeniorCheck = param.IsLewisAndSeniorCheck,
src/MSFINDER/MSFINDER/ViewModel/AnalysisParameterSettingVM.cs:276: if (this.copyParam.CoverRange != param.CoverRange || this.copyParam.IsElementProbabilityCheck != param.IsElementProbabilityCheck || this.copyParam.IsLewisAndSen
```

### mzmine — 281 попаданий в 50 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/RdbeType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/formula/FormulaListType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/iin/IonIdentityListType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/identities/MolecularFormulaIdentity.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/structures/CounterIons.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/structures/StructureHarmonizer.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/CarbonModelAlgorithmParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/IsotopeFinderParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/engine/CarbonRatio.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/engine/ChargeScore.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/engine/CrossScanRefiner.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/engine/ElementAutoDetector.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/util/XMLUtils.java:484: @Nullable Element rangeElement) {
mzmine-community/src/main/java/io/github/mzmine/util/XMLUtils.java:501: @Nullable Element rangeElement) {
mzmine-community/src/main/java/io/github/mzmine/parameters/parametertypes/mztochargeparameter/MzToChargeParameter.java:99: Element rangeElement = (Element) ranges.item(i);
mzmine-community/src/main/java/io/github/mzmine/parameters/parametertypes/mztochargeparameter/MzToChargeParameter.java:114: Element rangeElement = doc.createElement(RANGE_ELEMENT);
mzmine-community/src/main/java/io/github/mzmine/modules/visualization/dash_lipidqc/LipidQcAnnotationSelectionUtils.java:86: * Extracts the number of double bond equivalents (DBE) from a lipid annotation at species level.
mzmine-community/src/main/java/io/github/mzmine/modules/visualization/equivalentcarbonnumberplot/EquivalentCarbonNumberChartPane.java:45: + ": ECN model for DBE: " + numberOfDes, "white-larger-label");
```

### nomspectra — 46 попаданий в 3 файлах

Файлы: `nomspectra/brutto.py`, `nomspectra/gui_design.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/brutto.py:51: Rules: 0.25<H/C<2.2, O/C < 1, nitogen parity, DBE-O <= 10.
nomspectra/brutto.py:95: temp['DBE-O'] = 1.0 + temp["C"] - 0.5 * temp["H"] + 0.5 * temp['N'] - temp['O']
nomspectra/brutto.py:96: gdf = gdf.loc[temp['DBE-O'] <= 10]
nomspectra/gui_design.py:976: self.cut_box.setItemText(13, _translate("MainWindow", "DBE"))
nomspectra/gui_design.py:978: self.cut_box.setItemText(15, _translate("MainWindow", "DBE-O"))
nomspectra/gui_design.py:979: self.cut_box.setItemText(16, _translate("MainWindow", "DBE-OC"))
```

### openms — 67 попаданий в 15 файлах

Файлы: `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/include/OpenMS/ANALYSIS/ID/ProSEAlgorithm.h`, `src/openms/include/OpenMS/ANALYSIS/QUANTITATION/PeptideAndProteinQuant.h`, `src/openms/include/OpenMS/ANALYSIS/TOPDOWN/SpectralDeconvolution.h`, `src/openms/include/OpenMS/CHEMISTRY/AdductInfo.h`, `src/openms/include/OpenMS/DATASTRUCTURES/KDTree.h`, `src/openms/include/OpenMS/FEATUREFINDER/FeatureFindingMetabo.h`, `src/openms/include/OpenMS/FORMAT/HANDLERS/ThermoRawFileMetadata.h`, `src/openms/include/OpenMS/FORMAT/MSExperimentArrowExport.h`, `src/openms/source/ANALYSIS/ID/ProSEAlgorithm.cpp`, `src/openms/source/ANALYSIS/QUANTITATION/PeptideAndProteinQuant.cpp`, `src/openms/source/FEATUREFINDER/FeatureFindingMetabo.cpp`

Примеры:

```
src/topp/FeatureFinderIdentification.cpp:95: The fitted models are checked for plausibility before they are accepted.
src/topp/OpenNuXL/source/NuXLAnnotateAndLocate.cpp:728: // Rules 2 and 3 are checked per ion series: implausible prefix (a/b) evidence must not
src/openms/source/FEATUREFINDER/FeatureFindingMetabo.cpp:346: use_mz_scoring_by_element_range_ = param_.getValue("mz_scoring_by_elements").toBool();
src/openms/source/FEATUREFINDER/FeatureFindingMetabo.cpp:523: if (use_mz_scoring_by_element_range_)
src/openms/source/FEATUREFINDER/FeatureFindingMetabo.cpp:872: if (use_mz_scoring_by_element_range_ && isotope_filtering_model_ != "none")
src/openms/source/FORMAT/ProteinGroupArrowExport.cpp:118: /// silently continuing on it would turn malformed metadata into a plausible-looking export.
```

### pyc2mc — 369 попаданий в 14 файлах

Файлы: `Image.py`, `main.py`, `modules/comparison.py`, `modules/data_views.py`, `modules/molecular_maps.py`, `modules/plot_helpers.py`, `modules/plots.py`, `modules/pyc2mc_ui.py`, `modules/resources_rc.py`, `modules/window_actions.py`, `src/loading/loading_function.py`, `src/pre_processing_function.py`

Примеры:

```
Image.py:18: img_str="iVBORw0KGgoAAAANSUhEUgAAAmwAAAGnCAYAAAAKUgvPAAAgAElEQVR4nMy9d5Bl53Undr573+scJ/XkATAYDDIGgEAikABIAiQIgABBSlpRDJLMXSq5pLV27a3aLatorWu9trVm2bJdG7Sl9aqkkpe
main.py:460: # DBE
main.py:516: # Displays Intensity vs DBE plots page
main.py:592: # DBE maps
main.py:671: # Displays DBE widget
modules/comparison.py:241: # plot_fun("scatter",x=frames.data_extract["C"],y=frames.data_extract["DBE"],d_color=frames.data_extract["fc"],dot_type=self.dot_type,edge=self.edge,cmap="RdYlG
```

### ume — 110 попаданий в 16 файлах

Файлы: `R/calc_data_summary.R`, `R/calc_dbe.R`, `R/calc_eval_params.R`, `R/check_neutral_mf.R`, `R/create_time_flattened_mfd.R`, `R/create_ume_formula_library.R`, `R/data.R`, `R/filter.R`, `R/global.R`, `R/remove_blanks.R`, `R/tools.R`, `R/uplot_dbe_minus_o_freq.R`

Примеры:

```
R/calc_data_summary.R:24: #'     \item{wa(DBE)}{Weighted average Double Bond Equivalent (DBE).}
R/calc_data_summary.R:75: , "wa(DBE)"=round(stats::weighted.mean(dbe, i_magnitude),1)
R/calc_data_summary.R:106: cols <- c(grp, "n(mf)", "wa(mz)", "wa(DBE)", "wa(AI)"
R/calc_dbe.R:1: #' @title Calculate Double Bond Equivalent (DBE)
R/calc_dbe.R:3: #' @description Calculates the Double Bond Equivalent (DBE) for a given
R/calc_dbe.R:5: #' DBE is a measure of unsaturation, representing the total number of rings
```

## halogen_support — Поддержка галогенов

Всего попаданий по всем проектам: **48169**.

### corems — 485 попаданий в 50 файлах

Файлы: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/constant.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/encapsulation/output/parameter_to_dict.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`, `corems/mass_spectra/calc/SignalProcessing.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/brukerSolarix_utils.py`, `corems/mass_spectra/input/corems_hdf5.py`

Примеры:

```
support_code/atom_parsers/AtomsDescription.py:24: "F": Atom(atomic_number=9, symbol='F', mass_number='19', atomic_mass=18.9984031627392, natural_abundance=1.0),
support_code/atom_parsers/AtomsDescription.py:41: "35Cl": Atom(atomic_number=17, symbol='Cl', mass_number='35', atomic_mass=34.96885268237, natural_abundance=0.75761),
support_code/atom_parsers/AtomsDescription.py:42: "37Cl": Atom(atomic_number=17, symbol='Cl', mass_number='37', atomic_mass=36.96590260255, natural_abundance=0.24241),
support_code/atom_parsers/AtomsDescription.py:73: "58Ni": Atom(atomic_number=28, symbol='Ni', mass_number='58', atomic_mass=57.9353424152, natural_abundance=0.6807719),
support_code/atom_parsers/AtomsDescription.py:74: "60Ni": Atom(atomic_number=28, symbol='Ni', mass_number='60', atomic_mass=59.9307858852, natural_abundance=0.2622315),
support_code/atom_parsers/AtomsDescription.py:75: "61Ni": Atom(atomic_number=28, symbol='Ni', mass_number='61', atomic_mass=60.9310555752, natural_abundance=0.01139913),
```

### formultitude — 122 попаданий в 17 файлах

Файлы: `CIA/FormultitudeProgram.cs`, `CiaUi/FormultitudeUIForm.cs`, `FileReader/FileReader.cs`, `FindChains/FindChainsForm.cs`, `FindChainsTest/FindChainsTestProgram.cs`, `Support/CChainBlocks.cs`, `Support/CFileReader.cs`, `Support/CIsotope.cs`, `TestFSDBSearch/Form1.cs`, `TestFSDBSearch/My/MyApplication.cs`, `TestFSDBSearch/My/MySettings.cs`, `TestFSDBSearch/TotalDeclarations.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:471: "Heteroatom counts",
CIA/FormultitudeProgram.cs:861: //    This iteration % of the program uses only chemical relationships that are common to refractory DOM such as humic acids. It does not include many biologica
CIA/FormultitudeProgram.cs:876: //KL 1/2/09 - change the list sorting to consider both the minimum number of non-oxygen heteroatoms AND the lowest error - get around the case where
CIA/FormultitudeProgram.cs:877: //    can have different formulas with the same number of non-oxygen heteroatoms
CIA/FormultitudeProgram.cs:985: //improvement on sub-ppm level is not that easy to evaluate; keep brute force formula if heteroatom evaluation makes it better choice
CIA/FormultitudeProgram.cs:1186: //1/2/09 - can have the case where multiple compounds have the same number of non-oxygen heteroatoms, so that isn't always the best way to sort.
```

### icbmocean — 2 попаданий в 2 файлах

Файлы: `ResPow_outlier.R`, `create_homologous_series_network.R`

Примеры:

```
create_homologous_series_network.R:61: B<-data.frame(C=D$C+D$C13,H=D$H,Br=D$Br79+D$Br81,Cl=D$Cl+D$Cl37,Co=D$Co,Cu=D$Cu.i+D$Cu.ii+D$Cu65.i+D$Cu65.ii,Fe=D$Fe.ii+D$Fe.iii+D$Fe54.ii+D$Fe54.iii,I=D$I,N=D$
ResPow_outlier.R:35: if(is.na(e)){e<-Inf}
```

### mfassignr — 336 попаданий в 9 файлах

Файлы: `MFAssignR/R/FindCoreFormulae2.R`, `MFAssignR/R/FindCoreFormulae2_Halogen.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`, `MFAssignR/R/RecalFunctions.R`, `MFAssignR/R/Utilities.R`, `MFAssignR/R/Utilities_Halogen.R`

Примеры:

```
MFAssignR/R/FindCoreFormulae2.R:72: D = env$loop[CompFactorToInt("D")], Cl = env$loop[CompFactorToInt("Cl")],
MFAssignR/R/FindCoreFormulae2_Halogen.R:72: D = env$loop[CompFactorToInt2("D")], Cl = env$loop[CompFactorToInt2("Cl")],
MFAssignR/R/FindCoreFormulae2_Halogen.R:74: Cl37 = env$loop[CompFactorToInt2("Cl37")], Br = env$loop[CompFactorToInt2("Br")],
MFAssignR/R/FindCoreFormulae2_Halogen.R:75: Br81 = env$loop[CompFactorToInt2("Br81")], I = env$loop[CompFactorToInt2("I")],
MFAssignR/R/MFAssign.R:7: #' There are user inputs for heteroatoms, adducts, and charge.
MFAssignR/R/MFAssign.R:9: #' Clx, Fx, Cl37x, Mx, NH4x, and Zx. Basic QA steps are included within the
```

### msdial — 4903 попаданий в 1039 файлах

Файлы: `src/Common/ChartDrawing/AxisManager/Generic/CategoryAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/PercentLabelGenerator.cs`, `src/Common/ChartDrawing/Behavior/ItemSelectBehavior.cs`, `src/Common/ChartDrawing/Chart/BarControl.cs`, `src/Common/ChartDrawing/Chart/DendrogramControl.cs`, `src/Common/ChartDrawing/Chart/HeatmapControl.cs`, `src/Common/ChartDrawing/Chart/LineChartControl.cs`, `src/Common/ChartDrawing/Chart/LineSpectrumControl.cs`, `src/Common/ChartDrawing/Chart/MultiAreaChartControl.cs`, `src/Common/ChartDrawing/Chart/MultiLineChartControl.cs`, `src/Common/ChartDrawing/Chart/ScatterControl.cs`, `src/Common/ChartDrawing/Chart/ScatterControlSlim.cs`

Примеры:

```
src/RawDataApp/RawDataConverter/MainWindow.xaml.cs:52: var includedFiles = new List<string>();
src/RawDataApp/RawDataConverter/MainWindow.xaml.cs:58: includedFiles.Add(files[i]);
src/RawDataApp/RawDataConverter/MainWindow.xaml.cs:73: if (includedFiles.Count > 0) {
src/RawDataApp/RawDataConverter/MainWindow.xaml.cs:75: vm.FilePathes = new ObservableCollection<string>(includedFiles);
src/MSFINDER/MSFINDER/MainWindow.xaml.cs:172: if (ExtensionMethods.OpenClipboard(((IWin32Window)this.OwnerAsWin32()).Handle))
src/MSFINDER/MSFINDER/MainWindow.xaml.cs:225: private void contextMenu_SaveImageForPublication_Click(object sender, RoutedEventArgs e) {
```

### mzmine — 13818 попаданий в 3951 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/gui/DefaultHeadlessDesktop.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/Desktop.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/DesktopService.java`, `javafx-framework/src/main/java/io/github/mzmine/gui/JavaFxDesktop.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/FilterableListView.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/FilterableListViewEvent.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/FilterableListViewEventHandler.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/GridRow.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/LabeledProgressBar.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/LabeledProgressBarCell.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/MappingListCell.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/NumberTextField.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/ExitCode.java:7: * restriction, including without limitation the rights to use,
utils/src/main/java/io/github/mzmine/util/ExitCode.java:14: * included in all copies or substantial portions of the Software.
utils/src/main/java/io/github/mzmine/util/ExitCode.java:17: * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
utils/src/main/java/io/github/mzmine/util/LayoutToRecordGenerator.java:7: * restriction, including without limitation the rights to use,
utils/src/main/java/io/github/mzmine/util/LayoutToRecordGenerator.java:14: * included in all copies or substantial portions of the Software.
utils/src/main/java/io/github/mzmine/util/LayoutToRecordGenerator.java:16: * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
```

### nomspectra — 25 попаданий в 6 файлах

Файлы: `nomspectra/brutto.py`, `nomspectra/diff.py`, `nomspectra/gui.py`, `nomspectra/recal.py`, `nomspectra/spectrum.py`, `setup.py`

Примеры:

```
setup.py:25: include_package_data=True,
nomspectra/brutto.py:209: ["Br", 78.918338, 50.69, 79, "Br_79"],
nomspectra/brutto.py:210: ["Br", 80.916291, 49.31, 81, "Br_81"],
nomspectra/brutto.py:232: ["Cl", 34.968853, 75.78, 35, "Cl_35"],
nomspectra/brutto.py:233: ["Cl", 36.965903, 24.22, 37, "Cl_37"],
nomspectra/brutto.py:256: ["F", 18.998403, 100.0, 19, "F_19"],
```

### openms — 27342 попаданий в 3336 файлах

Файлы: `cmake/Windows/Contrib/Inetc/afxres.h`, `cmake/Windows/Contrib/Inetc/crt.cpp`, `cmake/Windows/Contrib/Inetc/inetc.cpp`, `cmake/Windows/Contrib/Inetc/nsis_tchar.h`, `cmake/Windows/Contrib/Inetc/pluginapi.c`, `cmake/Windows/Contrib/Inetc/pluginapi.h`, `cmake/Windows/Contrib/Inetc/resource.h`, `doc/code_examples/Tutorial_AASequence.cpp`, `doc/code_examples/Tutorial_Clustering.cpp`, `doc/code_examples/Tutorial_DPosition.cpp`, `doc/code_examples/Tutorial_DRange.cpp`, `doc/code_examples/Tutorial_Element.cpp`

Примеры:

```
tools/ci/check_macos_wheel_target.py:53: ncmds = struct.unpack(endian + "I", blob[16:20])[0]
tools/ci/check_macos_wheel_target.py:62: best = max(best or (0, 0, 0), decode(struct.unpack(endian + "I", blob[offset + 12:offset + 16])[0]))
tools/ci/check_macos_wheel_target.py:64: best = max(best or (0, 0, 0), decode(struct.unpack(endian + "I", blob[offset + 8:offset + 12])[0]))
tools/scripts/export_peptdeep_models_to_onnx.py:93: OpenMS mirrors it in src/openms/include/OpenMS/ML/PEPTDEEP/PeptDeepUtils.h; a peptdeep release
tools/scripts/plot_pasef_frames.py:100: # n evenly spaced positions across the available indices, inclusive of ends
tools/scripts/plot_pasef_frames.py:460: li_lo, li_hi = np.inf, -np.inf
```

### pyc2mc — 324 попаданий в 18 файлах

Файлы: `Image.py`, `main.py`, `modules/comparison.py`, `modules/data_views.py`, `modules/molecular_maps.py`, `modules/plots.py`, `modules/pyc2mc_ui.py`, `modules/resources_rc.py`, `modules/ui_main.py`, `src/graphics/select_classe.py`, `src/loading/loading_function.py`, `src/pre_processing_function.py`

Примеры:

```
Image.py:18: img_str="iVBORw0KGgoAAAANSUhEUgAAAmwAAAGnCAYAAAAKUgvPAAAgAElEQVR4nMy9d5Bl53Undr573+scJ/XkATAYDDIGgEAikABIAiQIgABBSlpRDJLMXSq5pLV27a3aLatorWu9trVm2bJdG7Sl9aqkkpe
main.py:239: def openCloseSettingsBox():
main.py:243: def openCloseProcessBox():
main.py:247: def openCloseViewBox():
main.py:257: def openCloseCompareBox():
main.py:267: def openCloseStatsBox():
```

### ume — 67 попаданий в 25 файлах

Файлы: `R/as_peaklist.R`, `R/calc_data_summary.R`, `R/calc_dbe.R`, `R/calc_eval_params.R`, `R/calc_recalibrate_ms.R`, `R/check_objects.R`, `R/classify_files.R`, `R/convert_molecular_formula_to_data_table.R`, `R/create_custom_formula_library.R`, `R/create_isotope_expanded_table.R`, `R/create_ume_formula_library.R`, `R/data.R`

Примеры:

```
R/as_peaklist.R:84: i_magnitude = c("i_magnitude", "intensity", "I", "signal", "height"),
R/calc_data_summary.R:10: #'   using the provided peak list (`mfd`). Calculated values include weighted averages for elemental counts
R/calc_data_summary.R:18: #' @return A `data.table` containing the summarized results, with columns including:
R/calc_dbe.R:13: #' \mathrm{DBE} = 1 + \frac{1}{2} \sum_i n_i (v_i - 2)
R/calc_dbe.R:18: #'   \item \eqn{n_i}: number of atoms of element \eqn{i}
R/calc_dbe.R:103: elements_included <- isotope_info[!is.na(valence) & valence != 2, ]
```

### xcms — 745 попаданий в 87 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MPI.R`, `R/MsExperiment-functions.R`, `R/MsExperiment.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment-plotting.R`, `R/XcmsExperiment.R`, `R/XcmsExperimentHdf5-functions.R`, `R/XcmsExperimentHdf5.R`, `R/cwTools.R`, `R/do_adjustRtime-functions.R`

Примеры:

```
R/AllGenerics.R:93: #' See also section *Alignment of experiments including blanks* in the
R/AllGenerics.R:478: #' @param method `character(1)` specifying which spectra to include in the
R/AllGenerics.R:715: #'   m/z - rt region that includes all chromatographic peaks for a feature. The
R/AllGenerics.R:726: #'   parameter `include` allows also to return all chromatographic peaks with
R/AllGenerics.R:727: #'   their apex position within the selected region (`include = "apex_within"`)
R/AllGenerics.R:729: #'   (`include = "any"`).
```

## internal_recalibration_series — Внутренняя рекалибровка по гомологическим сериям

Всего попаданий по всем проектам: **128**.

### formultitude — 8 попаданий в 5 файлах

Файлы: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.cs`, `TestFSDBSearch/Form1.cs`, `TestFSDBSearch/TotalCalibration.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:186: oData.CalMasses [ FileIndex ] = oTotalCalibration.ttl_LQ_InternalCalibration( ref oData.Masses [ FileIndex ], ref Abundances, ref oData.SNs [ FileIndex ], MaxAb
CiaUi/CiaAdvancedForm.cs:163: CalMasses [ FileIndex ] = oCCia.oTotalCalibration.ttl_LQ_InternalCalibration( ref Masses [ FileIndex ], ref Abundances [ FileIndex ], ref SNs [ FileIndex ], Max
CiaUi/FormultitudeUIForm.cs:175: richTextBoxAbout.SelectedText = "\rNikola Tolic (Internal calibration, IPA function and DB)";
CiaUi/FormultitudeUIForm.cs:373: CalMasses [ FileIndex ] = oCCia.oTotalCalibration.ttl_LQ_InternalCalibration( ref Masses [ FileIndex ], ref Abundances [ FileIndex ], ref SNs [ FileIndex ], Max
TestFSDBSearch/Form1.cs:2078: this.peak_m_cal = this.my_cal.ttl_LQ_InternalCalibration(ref this.peak_m, ref this.peak_a, ref this.peak_sn, this.max_a);
TestFSDBSearch/TotalCalibration.cs:328: public double[] ttl_LQ_InternalCalibration(ref double[] m, ref double[] a, ref double[] sn, double max_abu)
```

### icbmocean — 1 попаданий в 1 файлах

Файлы: `create_homologous_series_network.R`

Примеры:

```
create_homologous_series_network.R:1: # create homologous series network : here, not from Kendricks mass defekt, but from molecular formulas directly
```

### mfassignr — 43 попаданий в 2 файлах

Файлы: `MFAssignR/R/RecalFunctions.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`

Примеры:

```
Supplemental MFAssign Scripts/Full MFAssignR Example.R:51: #Highlighting possible recalibrant series
Supplemental MFAssign Scripts/Full MFAssignR Example.R:55: #Qualitative check of recalibrant series and mass recalibration.
MFAssignR/R/RecalFunctions.R:1: #' Generates a plot to visualize recalibrant series, recalibrates two mass lists,
MFAssignR/R/RecalFunctions.R:2: #' and produces a list of the chosen recalibrants.
MFAssignR/R/RecalFunctions.R:6: #' IsoFiltR(), and the chosen recalibrant series to generate a plot for the qualitative
MFAssignR/R/RecalFunctions.R:7: #' assessment of the recalibrants, recalibrate the "Mono" and "Iso" outputs from IsoFiltR,
```

### mzmine — 1 попаданий в 1 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/gui/preferences/VendorImportParameters.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/gui/preferences/VendorImportParameters.java:87: Internal calibration signals may be present in spectra of all MS-levels (MS1-MSn) from Thermo Orbitraps.
```

### openms — 75 попаданий в 17 файлах

Файлы: `src/openms/include/OpenMS/ANALYSIS/QUANTITATION/DDAWorkflowCommons.h`, `src/openms/include/OpenMS/FORMAT/HANDLERS/AcqusHandler.h`, `src/openms/include/OpenMS/PROCESSING/CALIBRATION/InternalCalibration.h`, `src/openms/source/ANALYSIS/QUANTITATION/DDAWorkflowCommons.cpp`, `src/openms/source/PROCESSING/CALIBRATION/InternalCalibration.cpp`, `src/pyOpenMS/bindings/bind_misc.cpp`, `src/pyOpenMS/bindings/bind_processing.cpp`, `src/topp/ExternalCalibration.cpp`, `src/topp/InternalCalibration.cpp`, `src/topp/IsobaricAnalyzer.cpp`, `src/topp/IsobaricWorkflow.cpp`, `src/topp/OpenNuXL/OpenNuXL.cpp`

Примеры:

```
src/topp/ExternalCalibration.cpp:12: #include <OpenMS/PROCESSING/CALIBRATION/InternalCalibration.h>
src/topp/ExternalCalibration.cpp:128: InternalCalibration ic;
src/topp/InternalCalibration.cpp:11: #include <OpenMS/PROCESSING/CALIBRATION/InternalCalibration.h>
src/topp/InternalCalibration.cpp:34: @page TOPP_InternalCalibration InternalCalibration
src/topp/InternalCalibration.cpp:42: <td VALIGN="middle" ROWSPAN=3> &rarr; InternalCalibration &rarr;</td>
src/topp/InternalCalibration.cpp:123: @verbinclude TOPP_InternalCalibration.cli
```

## kendrick — Kendrick mass defect

Всего попаданий по всем проектам: **1482**.

### corems — 198 попаданий в 12 файлах

Файлы: `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectrum/calc/KendrickGroup.py`, `corems/mass_spectrum/factory/MassSpectrumClasses.py`, `corems/molecular_formula/calc/MolecularFormulaCalc.py`, `corems/molecular_formula/factory/MolecularFormulaFactory.py`, `corems/molecular_id/calc/ClusterFilter.py`, `corems/molecular_id/calc/MolecularFilter.py`, `corems/molecular_id/search/findOxygenPeaks.py`, `corems/molecular_id/search/molecularFormulaSearch.py`, `corems/molecular_id/search/priorityAssignment.py`, `corems/ms_peak/calc/MSPeakCalc.py`, `corems/ms_peak/factory/MSPeakClasses.py`

Примеры:

```
corems/ms_peak/calc/MSPeakCalc.py:35: This class provides methods to perform various calculations on MSPeak objects, such as calculating Kendrick Mass Defect (KMD) and Kendrick Mass (KM), calculatin
corems/ms_peak/calc/MSPeakCalc.py:57: Calculate the Kendrick Mass Defect (KMD) and Kendrick Mass (KM) for a given base formula.
corems/ms_peak/calc/MSPeakCalc.py:100: """Calculate the Kendrick Mass Defect (KMD) and Kendrick Mass (KM) for a given base formula
corems/ms_peak/calc/MSPeakCalc.py:112: kendrick_rounding_method = (
corems/ms_peak/calc/MSPeakCalc.py:113: self._ms_parent.mspeaks_settings.kendrick_rounding_method
corems/ms_peak/calc/MSPeakCalc.py:117: kendrick_rounding_method = MSParameters.ms_peak.kendrick_rounding_method
```

### formultitude — 42 попаданий в 5 файлах

Файлы: `CIA/FormultitudeProgram.cs`, `CiaUi/CiaAdvancedForm.Designer.cs`, `CiaUi/CiaAdvancedForm.cs`, `CiaUi/FormultitudeUIForm.cs`, `TestFSDBSearch/TotalDeclarations.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:453: //Kendrick
CIA/FormultitudeProgram.cs:454: bool UseKendrick = true;
CIA/FormultitudeProgram.cs:455: public bool GetUseKendrick() { return UseKendrick; }
CIA/FormultitudeProgram.cs:456: public void SetUseKendrick( bool UseKendrick ) { this.UseKendrick = UseKendrick; }
CIA/FormultitudeProgram.cs:1122: //Kendrick mass stuff
CIA/FormultitudeProgram.cs:1123: if( UseKendrick == true ) {
```

### icbmocean — 1 попаданий в 1 файлах

Файлы: `create_homologous_series_network.R`

Примеры:

```
create_homologous_series_network.R:1: # create homologous series network : here, not from Kendricks mass defekt, but from molecular formulas directly
```

### mfassignr — 111 попаданий в 7 файлах

Файлы: `MFAssignR/R/IsoFiltR.R`, `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`

Примеры:

```
Supplemental MFAssign Scripts/Full MFAssignR Example.R:20: plot <- Noise[["KMD"]]  #Extracting the plot from the KMDNoise function
MFAssignR/R/IsoFiltR.R:111: Data$KMD <- round((round(Data$Exp_mass) - Data$KM),3)
MFAssignR/R/IsoFiltR.R:121: Data$KMDdiff <- Data$KMD - Data$KMD1
MFAssignR/R/IsoFiltR.R:246: Data$KMD <- round((round(Data$Exp_mass) - Data$KM), 3)
MFAssignR/R/IsoFiltR.R:256: Data$KMDdiff <- Data$KMD - Data$KMD1
MFAssignR/R/KMDNoise.R:4: #'based on the separation of Kendrick mass
```

### msdial — 8 попаданий в 4 файлах

Файлы: `src/MSDIAL5/MsdialGuiApp/Model/DataObj/AlignmentSpotPropertyModel.cs`, `src/MSDIAL5/MsdialGuiApp/Model/DataObj/ChromatogramPeakFeatureModel.cs`, `src/MSDIAL5/MsdialGuiApp/Model/Dims/DimsAlignmentModel.cs`, `src/MSDIAL5/MsdialGuiApp/Model/Dims/DimsAnalysisModel.cs`

Примеры:

```
src/MSDIAL5/MsdialGuiApp/Model/DataObj/AlignmentSpotPropertyModel.cs:312: public double KMD => NominalKM - KM;
src/MSDIAL5/MsdialGuiApp/Model/DataObj/ChromatogramPeakFeatureModel.cs:211: public double KMD => NominalKM - KM;
src/MSDIAL5/MsdialGuiApp/Model/Dims/DimsAlignmentModel.cs:110: PlotModel = new AlignmentPeakPlotModel(spotsSource, spot => spot.MassCenter, spot => spot.KMD, target, labelSource, brushMapDataSelector.SelectedBrush, brushMap
src/MSDIAL5/MsdialGuiApp/Model/Dims/DimsAlignmentModel.cs:114: VerticalProperty = nameof(AlignmentSpotPropertyModel.KMD),
src/MSDIAL5/MsdialGuiApp/Model/Dims/DimsAlignmentModel.cs:116: VerticalTitle = "Kendrick mass defect"
src/MSDIAL5/MsdialGuiApp/Model/Dims/DimsAnalysisModel.cs:87: PlotModel = new AnalysisPeakPlotModel(Ms1Peaks, peak => peak.Mass, peak => peak.KMD, Target, labelSource, brushSelector.SelectedBrush, brushSelector.Brushes, Pe
```

### mzmine — 637 попаданий в 60 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/ArticleReferences.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/chartutils/ColoredBubbleDatasetRenderer.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/chartutils/XYBlockPixelSizePaintScales.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/mainwindow/workspace/AbstractWorkspace.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/batchmode/BatchModeModulesList.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/CarbonModelAlgorithmParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/engine/ElementAutoDetector.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_isotopefinder/engine/IsotopeFinderEngineConfig.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_rowsfilter/Isotope13CFilterParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_rowsfilter/KendrickMassDefectFilterParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_rowsfilter/RowsFilterParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/filter_rowsfilter/RowsFilterTask.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/util/IsotopePatternUtils.java:716: // only possible if mass defect is too high (e.g., for multiply charged)
mzmine-community/src/main/java/io/github/mzmine/util/IsotopePatternUtils.java:774: // linear equation for mass defect only below 0.5
mzmine-community/src/main/java/io/github/mzmine/parameters/parametertypes/massdefect/MassDefectFilter.java:45: throw new IllegalArgumentException("Lower mass defect range must be between 0 and 1.");
mzmine-community/src/main/java/io/github/mzmine/parameters/parametertypes/massdefect/MassDefectFilter.java:48: throw new IllegalArgumentException("Upper mass defect range must be between 0 and 1.");
mzmine-community/src/main/java/io/github/mzmine/modules/batchmode/BatchModeModulesList.java:189: import io.github.mzmine.modules.visualization.kendrickmassplot.KendrickMassPlotModule;
mzmine-community/src/main/java/io/github/mzmine/modules/batchmode/BatchModeModulesList.java:190: import io.github.mzmine.modules.visualization.kendrickmassplot.regionextraction.RegionExtractionModule;
```

### nomspectra — 12 попаданий в 2 файлах

Файлы: `nomspectra/gui_design.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/gui_design.py:966: self.cut_box.setItemText(3, _translate("MainWindow", "KMD"))
nomspectra/gui_design.py:1002: self.scatter_box_1.setItemText(3, _translate("MainWindow", "KMD"))
nomspectra/gui_design.py:1019: self.sactter_box_2.setItemText(2, _translate("MainWindow", "KMD"))
nomspectra/gui_design.py:1038: self.sactter_box_3.setItemText(3, _translate("MainWindow", "KMD"))
nomspectra/gui_design.py:1060: self.density_box.setItemText(4, _translate("MainWindow", "KMD"))
nomspectra/spectrum.py:1246: def kendrick(self) -> 'Spectrum':
```

### openms — 1 попаданий в 1 файлах

Файлы: `src/openms/include/OpenMS/FEATUREFINDER/FeatureFindingMetabo.h`

Примеры:

```
src/openms/include/OpenMS/FEATUREFINDER/FeatureFindingMetabo.h:182: * Calculate the maximal and minimal mass defects of isotopes for a given set of elements.
```

### pyc2mc — 436 попаданий в 9 файлах

Файлы: `main.py`, `modules/comparison.py`, `modules/data_views.py`, `modules/file_operations.py`, `modules/molecular_maps.py`, `modules/plot_helpers.py`, `modules/pyc2mc_ui.py`, `modules/window_actions.py`, `src/pyc2mc_ui.py`

Примеры:

```
main.py:301: self.ui.list_classes_Kendrick_comp.sortItems()
main.py:303: self.ui.list_classes_Kendrick_univ_comp.sortItems()
main.py:309: self.ui.list_classes_Kendrick.sortItems()
main.py:311: self.ui.list_classes_Kendrick_univ.sortItems()
main.py:480: # Kendrick
main.py:481: self.ui.btn_kendricks.clicked.connect(
```

### ume — 36 попаданий в 8 файлах

Файлы: `R/as_mfd.R`, `R/calc_eval_params.R`, `R/create_time_flattened_mfd.R`, `R/data.R`, `R/filter_multi_assignments.R`, `R/global.R`, `R/tools.R`, `R/uplot_kmd.R`

Примеры:

```
R/as_mfd.R:12: #' Kendrick mass defect (`kmd`), validates required columns, and returns a
R/as_mfd.R:21: #' @param add_kmd Logical. If `TRUE`, add `kmd` if missing and column `m`
R/as_mfd.R:23: #' @param kmd_digits Integer. Number of digits used for KMD rounding.
R/as_mfd.R:24: #' @param kmd_base_mass Numeric. Kendrick base mass. Default is CH2.
R/as_mfd.R:98: # Add KMD if missing -----------------------------------------------------
R/as_mfd.R:99: # KMD is only calculated if a formula mass column is available.
```

## descriptors — Дескрипторы (Ван-Кревелен, DBE, AI, NOSC)

Всего попаданий по всем проектам: **3644**.

### corems — 66 попаданий в 7 файлах

Файлы: `corems/mass_spectrum/factory/MassSpectrumClasses.py`, `corems/mass_spectrum/input/coremsHDF5.py`, `corems/mass_spectrum/input/massList.py`, `corems/mass_spectrum/output/export.py`, `corems/molecular_formula/calc/MolecularFormulaCalc.py`, `corems/molecular_formula/factory/MolecularFormulaFactory.py`, `corems/molecular_id/factory/classification.py`

Примеры:

```
corems/molecular_id/factory/classification.py:701: def plot_van_krevelen(
corems/molecular_id/factory/classification.py:705: """Plot Van Krevelen Diagram for a single class or all assigned classes
corems/molecular_id/factory/classification.py:712: Max H/C ratio, by default 2.5
corems/molecular_id/factory/classification.py:714: Max O/C ratio, by default 2
corems/molecular_id/factory/classification.py:780: ax.set_title("Van Krevelen Diagram - All Assigned Classes")
corems/molecular_id/factory/classification.py:784: ax.set_xlabel("O/C", fontsize=16)
```

### formultitude — 2 попаданий в 2 файлах

Файлы: `CiaUi/FormultitudeUIForm.Designer.cs`, `TestFSDBSearch/Form1.cs`

Примеры:

```
CiaUi/FormultitudeUIForm.Designer.cs:733: this.textBoxIpaFilter.Text = "r/C,r/H,o/Cl,o/Br,o/F,x/N,x/S,x/P,e/CHNOP";
TestFSDBSearch/Form1.cs:581: this.txtIPDB_EC_Filter.Text = "r/C,r/H,o/Cl,o/Br,o/F,x/N,x/S,x/P,e/CHNOP";
```

### mfassignr — 26 попаданий в 4 файлах

Файлы: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`

Примеры:

```
MFAssignR/R/MFAssign.R:145: #'   VK - ggplot of van Krevelen plot, colored by molecular group
MFAssignR/R/MFAssign.R:2496: AI <- isopeaks2[c(1,2)]
MFAssignR/R/MFAssign.R:2497: names(AI)[2] <- "mass"
MFAssignR/R/MFAssign.R:2498: names(AI)[1] <- "RA"
MFAssignR/R/MFAssign.R:2499: AI$Test <- paste(AI$mass, AI$RA, sep = "_")
MFAssignR/R/MFAssign.R:2505: AP <- rbind(AM, AI)
```

### msdial — 2847 попаданий в 233 файлах

Файлы: `src/Common/CommonMVVM/ChemView/ChemOntologyColor.cs`, `src/Common/CommonStandard/DataObj/NodeEdge/MolecularNetworkObj.cs`, `src/Common/CommonStandard/Lipidomics/LipidEieioMsmsCharacterization.cs`, `src/Common/CommonStandard/Lipidomics/LipidOadMsmsCharacterization.cs`, `src/Common/CommonStandard/Molecular spectrum networking/MolecularSpectrumNetworkingCommon.cs`, `src/Common/CommonStandard/Ontology/ChemOntologyColorConverter.cs`, `src/Common/CommonStandard/StructureFinder/Descriptor/MassFragmentFingerprint.cs`, `src/Common/CommonStandard/StructureFinder/Descriptor/MolecularDescriptor.cs`, `src/Common/CommonStandard/StructureFinder/Descriptor/NcdkDescriptor.cs`, `src/Common/CommonStandard/StructureFinder/Descriptor/PubChemFingerprint.cs`, `src/Common/CommonStandard/StructureFinder/Fragmenter/FragmentGenerator.cs`, `src/Common/CommonStandard/StructureFinder/Mapper/BondRecognition.cs`

Примеры:

```
src/MSDIAL5/MsdialGuiApp/ViewModel/Core/MainWindowVM.cs:226: System.Diagnostics.Process.Start("https://systemsomicslab.github.io/compms/license/main.html");
src/MSDIAL4/MolViewer/AppearanceViewModel.cs:23: using NCDK.Aromaticities;
src/MSDIAL4/MolViewer/AppearanceViewModel.cs:269: Aromaticity.CDKLegacy.Apply(arm);
src/MSDIAL4/MolViewer/AppearanceViewModel.cs:275: if (arm.Atoms[i].IsAromatic)
src/MSDIAL4/StructureFinderConsoleApp/StructureRecognitionTest.cs:58: var descriptor = structure.MolecularDescriptor;
src/MSDIAL4/StructureFinderStandard/Descriptor/MassFragmentFingerprint.cs:3093: && RingtypeChecker(atom2, ringDictionary, RingFunctionType.AromaticPyran, out ring2ID)
```

### mzmine — 167 попаданий в 32 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/compounddb/MolecularClassType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/structures/HarmonizationOptions.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/structures/StructureHarmonizer.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/structures/StructureUtils.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/chartutils/XYBlockPixelSizePaintScales.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/simplechart/SimpleChart.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/simplechart/SimpleXYChart.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/chartbasics/simplechart/SimpleXYZScatterPlot.java`, `mzmine-community/src/main/java/io/github/mzmine/gui/mainwindow/workspace/AbstractWorkspace.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/batchmode/BatchModeModulesList.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/dreams/DreaMSNetworkingTask.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/ms2deepscore/MS2DeepscoreNetworkingTask.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/util/IsotopePatternUtils.java:761: // highly aromatic rings C + 0.1 H (just an estimate)
mzmine-community/src/main/java/io/github/mzmine/util/IsotopePatternUtils.java:762: // Kind and Fiehn 7 golden rules 0.1 <= H/C <= 6
mzmine-community/src/main/java/io/github/mzmine/util/spectraldb/entry/AnalogCompoundGrouper.java:260: // between SMILES strings that differ only in atom case (e.g. "n" aromatic vs. "N"), but the
mzmine-community/src/main/java/io/github/mzmine/util/scans/similarity/impl/DreaMS/DreaMSModel.java:28: import ai.djl.MalformedModelException;
mzmine-community/src/main/java/io/github/mzmine/util/scans/similarity/impl/DreaMS/DreaMSModel.java:29: import ai.djl.inference.Predictor;
mzmine-community/src/main/java/io/github/mzmine/util/scans/similarity/impl/DreaMS/DreaMSModel.java:30: import ai.djl.ndarray.NDArray;
```

### nomspectra — 112 попаданий в 6 файлах

Файлы: `nomspectra/brutto.py`, `nomspectra/draw.py`, `nomspectra/gui.py`, `nomspectra/gui_design.py`, `nomspectra/spectra.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/brutto.py:51: Rules: 0.25<H/C<2.2, O/C < 1, nitogen parity, DBE-O <= 10.
nomspectra/brutto.py:79: #do rules H/C, O/C, and parity
nomspectra/brutto.py:88: temp['H/C'] = temp['H']/temp['C']
nomspectra/brutto.py:89: temp['O/C'] = temp['O']/temp['C']
nomspectra/brutto.py:90: gdf = gdf.loc[(temp['H/C'] < 2.2) & (temp['H/C'] > 0.25) & (temp['O/C'] < 1)]
nomspectra/draw.py:426: Scatter Van-Krevelin diagramm (O/C vs H/C)
```

### openms — 110 попаданий в 47 файлах

Файлы: `src/openms/extern/GTE/Mathematics/ApprCone3.h`, `src/openms/extern/GTE/Mathematics/HashCombine.h`, `src/openms/extern/GTE/Mathematics/MinimumAreaBox2.h`, `src/openms/extern/GTE/Mathematics/MinimumWidthPoints2.h`, `src/openms/extern/GTE/Mathematics/RotatingCalipers.h`, `src/openms/extern/SQLiteCpp/cpplint.py`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/extern/nlohmann_json/tools/amalgamate/amalgamate.py`, `src/openms/extern/simde/simde/x86/sse.h`, `src/openms/extern/simde/simde/x86/sse2.h`, `src/openms/extern/simde/simde/x86/ssse3.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/ChromatogramExtractor.h`

Примеры:

```
src/topp/FeatureFinderMetaboIdent.cpp:11: #include <OpenMS/ANALYSIS/OPENSWATH/ChromatogramExtractor.h>
src/topp/MSFraggerAdapter.cpp:199: {"Kong AT, Leprevost FV, Avtonomov DM, Mellacheruvu D, Nesvizhskii AI",
src/topp/OpenDIA.cpp:9: #include <OpenMS/ANALYSIS/OPENSWATH/CalibrationWorkflow.h>
src/topp/OpenSwathChromatogramExtractor.cpp:10: #include <OpenMS/ANALYSIS/OPENSWATH/ChromatogramExtractor.h>
src/topp/OpenSwathConfidenceScoring.cpp:9: #include <OpenMS/ANALYSIS/OPENSWATH/ConfidenceScoring.h>
src/topp/CometAdapter/CometAdapter.cpp:87: For a detailed description of all available parameters check the Comet documentation at https://uwpr.github.io/Comet/parameters/
```

### pyc2mc — 236 попаданий в 15 файлах

Файлы: `Image.py`, `main.py`, `modules/comparison.py`, `modules/data_views.py`, `modules/molecular_maps.py`, `modules/plot_helpers.py`, `modules/plots.py`, `modules/pyc2mc_ui.py`, `modules/resources_rc.py`, `modules/window_actions.py`, `src/graphics/select_axes_VK.py`, `src/loading/loading_function.py`

Примеры:

```
Image.py:18: img_str="iVBORw0KGgoAAAANSUhEUgAAAmwAAAGnCAYAAAAKUgvPAAAgAElEQVR4nMy9d5Bl53Undr573+scJ/XkATAYDDIGgEAikABIAiQIgABBSlpRDJLMXSq5pLV27a3aLatorWu9trVm2bJdG7Sl9aqkkpe
main.py:471: self.ui.btn_van_krevelen.clicked.connect(
main.py:474: self.ui.btn_van_krevelen.clicked.connect(
main.py:477: self.ui.btn_van_krevelen.clicked.connect(self.buttonColor)
main.py:478: self.ui.btn_van_krevelen.clicked.connect(openCloseViewBox)
main.py:479: self.ui.btn_van_krevelen.clicked.connect(lambda: self.colorTab("View"))
```

### ume — 74 попаданий в 17 файлах

Файлы: `R/calc_data_summary.R`, `R/calc_eval_params.R`, `R/create_time_flattened_mfd.R`, `R/create_ume_formula_library.R`, `R/data.R`, `R/global.R`, `R/inchi_to_mf.R`, `R/tools.R`, `R/uplot_dbe_vs_c.R`, `R/uplot_dbe_vs_ma.R`, `R/uplot_dbe_vs_o.R`, `R/uplot_diff_ms.R`

Примеры:

```
R/calc_data_summary.R:11: #'   (e.g., Carbon, Hydrogen), elemental ratios (e.g., O/C, H/C), and additional parameters such as the base peak intensity
R/calc_data_summary.R:12: #'   and summed intensities. It also calculates the aromaticity index (`wa(AI)`) based on the elemental composition.
R/calc_data_summary.R:25: #'     \item{wa(element)}{Weighted averages for elements (C, H, N, O, P, S) and ratios (O/C, H/C, N/C, S/C).}
R/calc_data_summary.R:26: #'     \item{wa(NOSC)}{Weighted average nominal oxidation state of carbon.}
R/calc_data_summary.R:28: #'     \item{wa(AI)}{Weighted average aromaticity index.}
R/calc_data_summary.R:39: #' an aromaticity index for high-resolution mass data of natural organic matter.
```

### xcms — 4 попаданий в 3 файлах

Файлы: `src/fastMatch.c`, `src/massifquant/TrMgr.cpp`, `src/massifquant/TrMgr.h`

Примеры:

```
src/fastMatch.c:32: Rf_error("fastMatch/calloc: memory could not be allocated ! (%lu bytes)\n", nx  * sizeof(struct idxStruct) );
src/massifquant/TrMgr.cpp:58: void TrMgr::setActIdx(const std::vector<int> & ai) {
src/massifquant/TrMgr.cpp:59: actIdx = ai;
src/massifquant/TrMgr.h:78: void setActIdx(const std::vector<int> & ai);
```

## similarity — Сходство/расстояния между спектрами

Всего попаданий по всем проектам: **9172**.

### corems — 428 попаданий в 28 файлах

Файлы: `corems/chroma_peak/calc/ChromaPeakCalc.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`, `corems/mass_spectra/calc/GC_RI_Calibration.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `corems/mass_spectra/factory/GC_Class.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/corems_hdf5.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectra/output/export.py`

Примеры:

```
support_code/nmdc/metabolomics/lcms_metabolomics_targeted_search.py:49: # Here we could do formula searching and MS2 search against a MSP database with MS2s of the search targets (similar to test_lcms_metabolomics.py)
support_code/nmdc/metabolomics/metabolomics_collection.py:131: if hasattr(mf, 'ms2_similarity_results') and mf.ms2_similarity_results:
support_code/nmdc/metabolomics/metabolomics_collection.py:133: total_spectral_matches += len(mf.ms2_similarity_results)
corems/ms_peak/calc/MSPeakCalc.py:738: # we assume a linear correlation for m/z and datapoits
corems/molecular_id/calc/math_distance.py:6: """ Collection of spectral similarity methods.
corems/molecular_id/calc/math_distance.py:9: and paper: Li, Y., Kind, T., Folz, J. et al. Spectral entropy outperforms MS/MS dot product similarity for small-molecule compound identification. Nat Methods 1
```

### msdial — 4178 попаданий в 277 файлах

Файлы: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `src/Common/ChartDrawing/Legacy/ChromatogramBean.cs`, `src/Common/CommonStandard/Algorithm/CowAlignment/CowAlignment.cs`, `src/Common/CommonStandard/Algorithm/Function/FrameBinnedSpectrum.cs`, `src/Common/CommonStandard/Algorithm/Function/MoleculerNetworking.cs`, `src/Common/CommonStandard/Algorithm/Function/SpectrumHandler.cs`, `src/Common/CommonStandard/Algorithm/PeakPick/PeakPick.cs`, `src/Common/CommonStandard/Algorithm/Scoring/MsScanMatching.cs`, `src/Common/CommonStandard/Algorithm/Scoring/RetentionMatchPolicy.cs`, `src/Common/CommonStandard/Alignment/AlignedPeakPropertyBean.cs`, `src/Common/CommonStandard/Alignment/AlignmentPropertyBean.cs`, `src/Common/CommonStandard/Components/ChromatogramGlobalProperty_temp2.cs`

Примеры:

```
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:226: var dotProduct = LcmsScoring.GetMassSpectraSimilarity(eSpectrum, lSpectrum, ms2tol, (float)param.MassRangeMin, (float)param.MassRangeMax);
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:227: var revDotProduct = LcmsScoring.GetReverseSearchSimilarity(eSpectrum, lSpectrum, ms2tol, (float)param.MassRangeMin, (float)param.MassRangeMax);
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:228: var mzSimilarity = LcmsScoring.GetGaussianSimilarity((float)rawData.PrecursorMz, mspRecord.PrecursorMz, ms1tol);
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:231: var rtSimilarity = FragmenterScoring.RetentionTimeSimilairty(rawData, mspRecord, param);
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:232: var ccsSimilarity = mspRecord.CollisionCrossSection >= 0 && rawData.Ccs >= 0 ? LcmsScoring.GetGaussianSimilarity((float)rawData.Ccs, mspRecord.CollisionCrossSec
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:256: if (rtSimilarity > 0) rtFactor = 2.0;
```

### mzmine — 2781 попаданий в 358 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxPopOvers.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/formatters/FormatDoubleRangeStringConverter.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/formatters/FormatDoubleStringConverter.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/util/color/ColorsFX.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MergedMassSpectrum.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/PseudoSpectrumType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/CachedFeatureDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureListRow.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureListRow.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/annotationpriority/AnnotationSummary.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/collections/StreamUtils.java:124: * Process all pairs in items. The processor could make use of a ConcurrentHashMap or similar to
utils/src/main/java/io/github/mzmine/util/collections/StreamUtils.java:140: * Process all pairs in items. The processor could make use of a ConcurrentHashMap or similar to
utils/src/main/java/io/github/mzmine/util/collections/StreamUtils.java:168: * Similar but different to: {@link Collectors#joining(CharSequence, CharSequence, CharSequence)}
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:164: * @param filter usually *.csv and similar
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:175: * @param filters usually *.csv and similar
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:187: * @param filter usually *.csv and similar
```

### nomspectra — 25 попаданий в 4 файлах

Файлы: `nomspectra/gui.py`, `nomspectra/gui_design.py`, `nomspectra/spectra.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/gui.py:1073: sim = self.similarity_metric.currentText()
nomspectra/gui_design.py:546: self.similarity_metric = QtWidgets.QComboBox(self.layoutWidget1)
nomspectra/gui_design.py:547: self.similarity_metric.setObjectName("similarity_metric")
nomspectra/gui_design.py:548: self.similarity_metric.addItem("")
nomspectra/gui_design.py:549: self.similarity_metric.addItem("")
nomspectra/gui_design.py:550: self.similarity_metric.addItem("")
```

### openms — 1581 попаданий в 276 файлах

Файлы: `doc/code_examples/Tutorial_Clustering.cpp`, `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/GTE/Mathematics/ContLozenge3.h`, `src/openms/extern/GTE/Mathematics/DistCircle3Circle3.h`, `src/openms/extern/GTE/Mathematics/ETManifoldMesh.h`, `src/openms/extern/GTE/Mathematics/Hyperellipsoid.h`, `src/openms/extern/GTE/Mathematics/ImageUtility2.h`, `src/openms/extern/GTE/Mathematics/IntpBSplineUniform.h`, `src/openms/extern/GTE/Mathematics/MassSpringSurface.h`, `src/openms/extern/GTE/Mathematics/MassSpringVolume.h`, `src/openms/extern/GTE/Mathematics/MinimumVolumeBox3.h`, `src/openms/extern/GTE/Mathematics/Sector2.h`

Примеры:

```
src/topp/AssayGeneratorMetabo.cpp:120: registerDoubleOption_("cosine_similarity_threshold", "<num>", 0.98, "Threshold for cosine similarity of MS2 spectra from the same precursor used in consensus sp
src/topp/AssayGeneratorMetabo.cpp:189: double cosine_sim_threshold = getDoubleOption_("cosine_similarity_threshold");
src/topp/AssayGeneratorMetabo.cpp:389: cosine_sim_threshold,
src/topp/AssayGeneratorMetaboSirius.cpp:254: // Combine ambigous identifications (derived from consensus features with similar m/z and RT)
src/topp/AssayGeneratorMetaboSirius.cpp:292: // based on the TransitionGroupID (similar for targets "0_Acephate_[M+H]+_0" and decoys "0_Acephate_decoy_[M+H]+_0")
src/topp/ClusterMassTraces.cpp:9: #include <OpenMS/ANALYSIS/OPENSWATH/MasstraceCorrelator.h>
```

### ume — 6 попаданий в 2 файлах

Файлы: `R/calc_indeces.R`, `R/uplot_cluster.R`

Примеры:

```
R/calc_indeces.R:7: #' (i.e., a higher contribution of peaks that correlate negatively with delta14C), while low values indicate 'younger' DOM
R/calc_indeces.R:8: #' (i.e., a higher contribution of peaks that correlate positively with delta14C)./
R/calc_indeces.R:104: #' of peaks that correlate positively with delta13C) while low values represent less terrestrial
R/calc_indeces.R:105: #' material (i.e. higher contribution of peaks that correlate negatively with delta13C).
R/uplot_cluster.R:12: #' [as_ume_matrix()]. A dissimilarity matrix is then calculated with
R/uplot_cluster.R:161: "jaccard", "gower",
```

### xcms — 173 попаданий в 19 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MsExperiment-functions.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperimentHdf5-functions.R`, `R/XcmsExperimentHdf5.R`, `R/do_findChromPeaks-functions.R`, `R/functions-XCMSnExp.R`, `R/functions-xcmsSwath.R`, `R/methods-Chromatogram.R`, `R/methods-MChromatograms.R`, `R/methods-XCMSnExp.R`

Примеры:

```
R/AllGenerics.R:125: #'     function to be used. Allowed values are `"cor"` (Pearson's correlation),
R/AllGenerics.R:126: #'     `"cor_opt"` (calculate only 10% diagonal band of distance matrix;
R/AllGenerics.R:441: #'   spectrum with the sum of intensities most similar to the peak's apex
R/AllGenerics.R:606: #'   (correlation) test of similarity (using Pearson's correlation coefficient)
R/AllGenerics.R:654: setGeneric("correlate", function(x, y, ...) standardGeneric("correlate"))
R/AllGenerics.R:1068: #' See also [chromPeakSpectra()], as it supports a similar parameter for
```

## statistics — Статистика (PCA, PLS, кластеризация)

Всего попаданий по всем проектам: **4660**.

### corems — 641 попаданий в 14 файлах

Файлы: `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/corems_hdf5.py`, `corems/mass_spectra/output/export.py`, `corems/molecular_id/calc/ClusterFilter.py`, `corems/molecular_id/calc/MolecularFilter.py`, `corems/molecular_id/search/findOxygenPeaks.py`, `corems/molecular_id/search/priorityAssignment.py`

Примеры:

```
support_code/nmdc/metabolomics/metabolomics_collection.py:54: # Cluster count
support_code/nmdc/metabolomics/metabolomics_collection.py:55: if 'cluster' in lcms_collection.mass_features_dataframe.columns:
support_code/nmdc/metabolomics/metabolomics_collection.py:56: n_clusters = lcms_collection.mass_features_dataframe['cluster'].nunique()
support_code/nmdc/metabolomics/metabolomics_collection.py:58: n_clusters = 0
support_code/nmdc/metabolomics/metabolomics_collection.py:63: if n_clusters > 0:
support_code/nmdc/metabolomics/metabolomics_collection.py:64: print(f"Consensus clusters: {n_clusters}")
```

### formultitude — 199 попаданий в 4 файлах

Файлы: `FindChains/FindChainsForm.cs`, `FindChainsTest/FindChainsTestProgram.cs`, `Support/CChainBlocks.cs`, `Support/CFileReader.cs`

Примеры:

```
FindChains/FindChainsForm.cs:150: //find clusters based on chains
FindChains/FindChainsForm.cs:151: oCChainBlocks.FindClusters(RawData);
FindChains/FindChainsForm.cs:152: var IsInChainCluster = new bool[RawData.Chains.Length];
FindChains/FindChainsForm.cs:154: var ChainClusters = new List<List<int>>();
FindChains/FindChainsForm.cs:158: if (IsInChainCluster[LeftChainIndex]) { continue; }
FindChains/FindChainsForm.cs:159: var ChainCluster = new List<int>();
```

### icbmocean — 2 попаданий в 1 файлах

Файлы: `fastjoin.R`

Примеры:

```
fastjoin.R:16: # Start with the smallest mass and check if the next mass is the tolerance range defined by 'tolp'. If Yes group togetherinto a mass cluster, if not start a new
fastjoin.R:18: # Group by found mass cluster and check for duplicate samples within a mass cluster
```

### msdial — 377 попаданий в 66 файлах

Файлы: `src/Common/CommonMVVM/ChemView/ChemOntologyColor.cs`, `src/Common/CommonStandard/Alignment/AlignmentPropertyBean.cs`, `src/Common/CommonStandard/DataObj/NodeEdge/MolecularNetworkObj.cs`, `src/Common/CommonStandard/Enum/CommonEnums.cs`, `src/Common/CommonStandard/Mathematics/Statistics/MultivariateAnalysisResult.cs`, `src/Common/CommonStandard/Mathematics/Statistics/StatisticsMathematics.cs`, `src/Common/CommonStandard/Molecular spectrum networking/MolecularSpectrumNetworkingCommon.cs`, `src/Common/CommonStandard/Ontology/ChemOntologyColorConverter.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdial.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialGcms.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialLcms.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialMzML.cs`

Примеры:

```
src/MSFINDER/MSFINDER/Molecular networking/MolecularNetworking.cs:13: using Msdial.Lcms.Dataprocess.Algorithm.Clustering;
src/MSFINDER/MSFINDER/Molecular networking/MolecularNetworking.cs:86: msmsEdges = MsmsClustering.GetEdgeInformations(targetQuery, mspQueries, param.MmnRelativeCutoff, param.MmnMassTolerance, param.MmnMassSimilarityCutOff, this.bgW
src/MSFINDER/MSFINDER/Molecular networking/MolecularNetworking.cs:88: ontologyEdges = OntologyClustering.GetEdgeInformations(targetQuery, mspQueries, param.MmnOntologySimilarityCutOff, 25.0, 50.0, this.bgWorker);
src/MSFINDER/MSFINDER/Molecular networking/MolecularNetworking.cs:90: reactionEdges = FormulaClustering.GetEdgeInformations(targetQuery, mspQueries, reactionFiles[0], 25.0, 75.0, this.bgWorker);
src/MSFINDER/MSFINDER/Molecular networking/MolecularNetworking.cs:93: msmsEdges = MsmsClustering.GetEdgeInformations(mspQueries, param.MmnRelativeCutoff, param.MmnMassTolerance, param.MmnMassSimilarityCutOff, this.bgWorker, 25.0, 
src/MSFINDER/MSFINDER/Molecular networking/MolecularNetworking.cs:95: ontologyEdges = OntologyClustering.GetEdgeInformations(mspQueries, param.MmnOntologySimilarityCutOff, 25.0, 50.0, this.bgWorker);
```

### mzmine — 1067 попаданий в 173 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/CompoundNameIdentifier.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/DataTypes.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/GNPSClusterUrlType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/annotations/GNPSSpectralLibraryMatchesType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/graphicalnodes/CompoundHierarchyTreeTableRow.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/graphicalnodes/CompoundHierarchyTreeTableRowSkin.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/graphicalnodes/CompoundIdTreeCell.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/networking/MolNetClusterIdType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/networking/MolNetClusterSizeType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/networking/NetworkStats.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/numbers/stats/AnovaFValueType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/numbers/stats/AnovaPValueType.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/collections/CollectionUtils.java:212: for (T test : haystack) {
mzmine-community/src/main/java/io/github/mzmine/util/DataTypeUtils.java:163: * according to the hierarchy of the specified types.
mzmine-community/src/main/java/io/github/mzmine/util/DataTypeUtils.java:199: * according to the hierarchy of the specified types.
mzmine-community/src/main/java/io/github/mzmine/util/FeatureTableFXUtil.java:254: // Defensive: parent claims this row but the TreeItem hierarchy doesn't expose it as a
mzmine-community/src/main/java/io/github/mzmine/util/GraphStreamUtils.java:29: import io.github.mzmine.modules.dataprocessing.group_spectral_networking.NetworkCluster;
mzmine-community/src/main/java/io/github/mzmine/util/GraphStreamUtils.java:147: public static @NotNull List<NetworkCluster> detectCommunities(final MultiGraph graph) {
```

### openms — 2206 попаданий в 159 файлах

Файлы: `doc/code_examples/Tutorial_Clustering.cpp`, `doc/code_examples/Tutorial_MapAlignment.cpp`, `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `doc/doxygen/parameters/TOPPDocumenter.cpp`, `src/openms/extern/GTE/Mathematics/ApprCircle2.h`, `src/openms/extern/GTE/Mathematics/ApprParallelLines2.h`, `src/openms/extern/GTE/Mathematics/ApprSphere3.h`, `src/openms/extern/GTE/Mathematics/ConformalMapGenus0.h`, `src/openms/extern/GTE/Mathematics/IntrSphere3Cone3.h`, `src/openms/extern/GTE/Mathematics/PolygonTree.h`, `src/openms/extern/SQLiteCpp/cpplint.py`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`

Примеры:

```
src/topp/AssayGeneratorMetabo.cpp:143: registerIntOption_("deisotoping_min_isopeaks", "<num>", 2, "The minimum number of isotopic peaks (at least 2) required for an isotopic cluster", false);
src/topp/AssayGeneratorMetabo.cpp:145: registerIntOption_("deisotoping_max_isopeaks", "<num>", 3, "The maximum number of isotopic peaks (at least 2) considered for an isotopic cluster", false);
src/topp/ClusterMassTraces.cpp:22: @page TOPP_ClusterMassTraces ClusterMassTraces
src/topp/ClusterMassTraces.cpp:24: @brief Cluster mass traces occurring in the same map together
src/topp/ClusterMassTraces.cpp:26: Cluster mass traces together found in a mass spectrometric map (MS1 or MS2).
src/topp/ClusterMassTraces.cpp:28: spectra containing all clustered features.
```

### pyc2mc — 90 попаданий в 11 файлах

Файлы: `main.py`, `modules/controller_dependencies.py`, `modules/data_views.py`, `modules/plots.py`, `modules/pyc2mc_ui.py`, `modules/window_actions.py`, `src/pre_processing_function.py`, `src/pyc2mc_ui.py`, `src/stats/HCA_function.py`, `src/stats/PCA_function.py`, `src/stats/volcano_function.py`

Примеры:

```
main.py:741: # Displays PCA page
main.py:763: # Displays volcano page
main.py:764: self.ui.btn_Volcano.clicked.connect(
main.py:767: self.ui.btn_Volcano.clicked.connect(
main.py:768: lambda: self.ui.stats_stacked_widget.setCurrentWidget(self.ui.page_Volcano)
main.py:770: self.ui.btn_Volcano.clicked.connect(self.buttonColor)
```

### ume — 38 попаданий в 5 файлах

Файлы: `R/calc_logratio.R`, `R/main_docu.R`, `R/tools.R`, `R/uplot_cluster.R`, `R/uplot_pca.R`

Примеры:

```
R/calc_logratio.R:20: #' combinations present in the transformed matrix. This is useful for PCA and
R/calc_logratio.R:21: #' clustering based on `logratio_value`.
R/main_docu.R:66: #' to be used (e.g. for clustering or color coding). Default usually is "norm_int" for normalized intensity values.
R/tools.R:83: #' This functions removes columns ID columns ('_id') and hierarchical search columns ('_lft', '_rgt') from a table.
R/uplot_cluster.R:1: #' Plot Cluster Analysis and Multi-Dimensional Scaling
R/uplot_cluster.R:3: #' @title uplot_cluster
```

### xcms — 40 попаданий в 12 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/do_groupChromPeaks-functions.R`, `R/functions-xcmsSet.R`, `R/methods-group-features.R`, `R/methods-xcmsSet.R`, `R/mzClust.R`, `longtests/testthat/test_old_methods-xcmsSet.R`, `src/massifquant/SegProc.cpp`, `src/massifquant/SegProc.h`, `src/mzClust_hclust.c`

Примеры:

```
R/AllGenerics.R:1702: #'     error for the clustering/grouping (in parts per million).
R/DataClasses.R:844: #' @param unions `integer(1)` set to `1` if apply t-test union on
R/DataClasses.R:845: #'     segmentation; set to `0` if no t-test to be applied on
R/DataClasses.R:853: #'     into one with a two sample t-test. The potential danger of this option
R/Deprecated.R:32: cat("Starting snow cluster with",nSlaves,"local sockets.\n")
R/Deprecated.R:33: snowclust <- makeCluster(nSlaves, type = "SOCK")
```

## visualization — Визуализация (графики, карты, сети)

Всего попаданий по всем проектам: **15507**.

### corems — 296 попаданий в 23 файлах

Файлы: `conftest.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/GC_Deconvolution.py`, `corems/mass_spectra/calc/SignalProcessing.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/factory/GC_Class.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectrum/calc/AutoRecalibration.py`, `corems/mass_spectrum/calc/MeanResolvingPowerFilter.py`, `corems/mass_spectrum/calc/NoiseCalc.py`

Примеры:

```
conftest.py:37: def pytest_configure(config):
support_code/nmdc/lipidomics/lipidomics_workflow.py:219: """Filter mass features based on peak shape metrics and plot composite feature map
support_code/nmdc/lipidomics/lipidomics_workflow.py:245: # Plot 50 random "good" mass features
support_code/nmdc/lipidomics/lipidomics_workflow.py:257: fig = myLCMSobj.mass_features[mf_id].plot(return_fig=True, plot_smoothed_eic=True, plot_eic_datapoints=True)
support_code/nmdc/lipidomics/lipidomics_workflow.py:273: fig = myLCMSobj.mass_features[mf_id].plot(return_fig=True, plot_smoothed_eic=True, plot_eic_datapoints=True)
support_code/nmdc/metabolomics/lcms_metabolomics_targeted_search.py:56: lcms_obj.mass_features[0].plot(return_fig = False)
```

### formultitude — 69 попаданий в 3 файлах

Файлы: `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.Designer.cs`

Примеры:

```
CiaUi/FormultitudeUIForm.cs:117: //chartError tab`
CiaUi/FormultitudeUIForm.cs:674: //Error plot tab
CiaUi/FormultitudeUIForm.cs:677: private void chartError_DragEnter( object sender, DragEventArgs e ) {
CiaUi/FormultitudeUIForm.cs:682: private void chartError_DragDrop( object sender, DragEventArgs e ) {
CiaUi/FormultitudeUIForm.cs:712: chartError.Series [ 0 ].Name = string.Empty;//SeriesName;
CiaUi/FormultitudeUIForm.cs:713: chartError.Series [ 0 ].Points.Clear();
```

### icbmocean — 13 попаданий в 2 файлах

Файлы: `ResPow_outlier.R`, `isotope_ratio_deviance_function.R`

Примеры:

```
isotope_ratio_deviance_function.R:41: P<-ggplot(data.frame(x=1:10,y=1:10),aes(x,y))+annotate("text",x=1,y=2,label="Dear Geochemist, you have not enough ratios to plot a density",size=5)+labs(title="
isotope_ratio_deviance_function.R:45: return(list(deviance=rdeviance,weighted_mean_deviance=rdeviance_weighted,plot=P))
isotope_ratio_deviance_function.R:53: #isotope_deviance(A$intensity_parent,A$intensity_child,number_of_atoms=A$C,q,p,number_of_isotopes=1,color_by=A$color_by)$plot
isotope_ratio_deviance_function.R:54: #isotope_deviance(A$intensity_parent,A$intensity_child,number_of_atoms=A$C,q,p,number_of_isotopes=1,color_by=c(1,2,3))$plot
isotope_ratio_deviance_function.R:56: #isotope_deviance(C$intensity_parent,C$intensity_child,number_of_atoms=C$C,q,p,number_of_isotopes=1,color_by=c(1,2))$plot
isotope_ratio_deviance_function.R:59: #isotope_deviance(B$intensity_parent,B$intensity_child,number_of_atoms=B$C,q,p,number_of_isotopes=1,group=B$group,color_by=B$color_by,add_points=T)$plot
```

### mfassignr — 67 попаданий в 8 файлах

Файлы: `MFAssignR/R/HistNoise.R`, `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`, `MFAssignR/R/RecalFunctions.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`

Примеры:

```
Supplemental MFAssign Scripts/Full MFAssignR Example.R:20: plot <- Noise[["KMD"]]  #Extracting the plot from the KMDNoise function
Supplemental MFAssign Scripts/Full MFAssignR Example.R:21: plot                    #Printing the plot
Supplemental MFAssign Scripts/Full MFAssignR Example.R:60: Plot <- Test[["Plot"]]
Supplemental MFAssign Scripts/Full MFAssignR Example.R:61: Plot      #This plot is slow to generate
MFAssignR/R/HistNoise.R:5: #'It uses the natural log of the intensity to create a histogram which then
MFAssignR/R/HistNoise.R:12: #'and the plot will demonstrate where the cut is being applied to the
```

### msdial — 3594 попаданий в 548 файлах

Файлы: `src/Common/ChartDrawing/Adorner/ChartSelectionRubberAdorner.cs`, `src/Common/ChartDrawing/Adorner/RangeSelectAdorner.cs`, `src/Common/ChartDrawing/Adorner/ScatterFocusAdorner.cs`, `src/Common/ChartDrawing/AxisManager/FreezableAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/Generic/AbsoluteAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/Generic/BaseAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/Generic/CategoryAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/Generic/ContinuousAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/Generic/DefectAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/Generic/LogScaleAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/Generic/ReactiveAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/Generic/RelativeAxisManager.cs`

Примеры:

```
src/RawDataApp/RawDataViewer/Model/AnalysisDataModel.cs:30: dataProvider = Task.Run(async () => (IDataProvider)new StandardDataProvider(await rawMeasurementTask.ConfigureAwait(false)), token);
src/RawDataApp/RawDataViewer/Model/AnalysisDataModel.cs:38: accumulatedDataProvider = Task.Run(async () => (IDataProvider)new MsdialLcImMsApi.Algorithm.LcimmsAccumulateDataProvider(await rawMeasurementTask.ConfigureAwait
src/RawDataApp/RawDataViewer/Model/AnalysisDataModel.cs:45: var measurement = await rawMeasurementTask.ConfigureAwait(false);
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsCheckModel.cs:28: var (summary, distribution) = await detector.DetectAsync(dataModel, token).ConfigureAwait(false);
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:23: var provider = await dataModel.CreateDataProvider(token).ConfigureAwait(false);
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:29: var provider = await dataModel.CreateDataProviderByFactory(providerFactory, token).ConfigureAwait(false);
```

### mzmine — 9197 попаданий в 671 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/impl/IonMobilogramTimeSeriesFactory.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeature.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/annotationpriority/AnnotationSummary.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/CompoundComponentizerModule.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/CompoundRepresentativeSelectorModule.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/AbstractBoxPlotType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/AreaBoxPlotType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/AreaShareType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/DataTypes.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/FeatureShapeIonMobilityRetentionTimeHeatMapType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/FeatureShapeMobilogramType.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/web/HttpUtils.java:116: "Default proxy may be misconfigured. Open mzmine preferences and change proxy settings. Using NO proxy worked for this request");
utils/src/main/java/io/github/mzmine/util/web/HttpUtils.java:123: "Failed HTTP request. Either the web host is unavailable or both the configured proxy and NO proxy failed.");
utils/src/main/java/io/github/mzmine/util/web/ProxyUtils.java:139: * @return true if proxy was configured, false otherwise
utils/src/main/java/io/github/mzmine/util/web/ProxyUtils.java:152: * @return true if proxy was configured, false otherwise
utils/src/main/java/io/github/mzmine/util/web/ProxyUtils.java:188: logger.info("HTTP/HTTPS proxy configured: " + host + ":" + port);
utils/src/main/java/io/github/mzmine/util/web/ProxyUtils.java:193: logger.info("SOCKS proxy configured: " + host + ":" + port);
```

### nomspectra — 122 попаданий в 6 файлах

Файлы: `nomspectra/draw.py`, `nomspectra/gui.py`, `nomspectra/gui_design.py`, `nomspectra/recal.py`, `nomspectra/spectra.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/draw.py:46: spectrum for plot
nomspectra/draw.py:54: send here ax to plot in your own condition
nomspectra/draw.py:56: Title of plot. Default None - Take name from metadata and number of peaks.
nomspectra/draw.py:58: additinal parameters to matplotlib plot method
nomspectra/draw.py:88: ax.plot(M, I, color=color, linewidth=0.2, **kwargs)
nomspectra/draw.py:89: ax.plot([xlim[0], xlim[1]], [0, 0], color=color, linewidth=0.2, **kwargs)
```

### openms — 1349 попаданий в 207 файлах

Файлы: `cmake/Windows/Contrib/Inetc/inetc.cpp`, `cmake/Windows/Contrib/Inetc/pluginapi.c`, `share/OpenMS/SCRIPTS/InternalCalibration_Models.R`, `share/OpenMS/SCRIPTS/InternalCalibration_Residuals.R`, `share/OpenMS/SCRIPTS/plot_trafo.R`, `src/openms/extern/GTE/Mathematics/CircleThroughPointSpecifiedTangentAndRadius.h`, `src/openms/extern/GTE/Mathematics/Histogram.h`, `src/openms/extern/GTE/Mathematics/IntrTriangle3Cylinder3.h`, `src/openms/extern/SQLiteCpp/cpplint.py`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.h`, `src/openms/extern/evergreen/src/Engine/RandomSubtreeScheduler.hpp`

Примеры:

```
tools/scripts/plot_pasef_frames.py:42: # and that should be shown in the figure's params banner. Other (boilerplate)
tools/scripts/plot_pasef_frames.py:228: # Bin counts come from the figure's per-panel pixel dims so detail
tools/scripts/plot_pasef_frames.py:258: # (matplotlib scatter z-orders by array position → last = on top).
tools/scripts/plot_pasef_frames.py:264: sc = ax.scatter(mz, im, s=sizes, c=log_int, cmap="viridis",
tools/scripts/plot_pasef_frames.py:311: # last so they pop above the datashade/scatter background. Uses the
tools/scripts/plot_pasef_frames.py:315: ax.scatter(top_mz, top_im, s=14.0, c=top_log, cmap="viridis",
```

### pyc2mc — 380 попаданий в 13 файлах

Файлы: `main.py`, `modules/comparison.py`, `modules/molecular_maps.py`, `modules/plot_helpers.py`, `modules/plots.py`, `modules/pyc2mc_ui.py`, `modules/window_actions.py`, `src/graphics/select_axes_VK.py`, `src/plotinator.py`, `src/pyc2mc_ui.py`, `src/stats/HCA_function.py`, `src/stats/PCA_function.py`

Примеры:

```
main.py:230: # matplotlib.rcParams['savefig.dpi'] = self.ui.saveDPI.text() #res figures
main.py:605: # VK plot
main.py:618: # KMD plot
main.py:631: # EV plot
main.py:802: # Plot buttons
main.py:837: # Plot View
```

### ume — 141 попаданий в 32 файлах

Файлы: `R/calc_eval_params.R`, `R/calc_recalibrate_ms.R`, `R/data.R`, `R/export_ume_results.R`, `R/main_docu.R`, `R/theme_uplots.R`, `R/tools.R`, `R/uplot_cluster.R`, `R/uplot_cvm.R`, `R/uplot_dbe_minus_o_freq.R`, `R/uplot_dbe_vs_c.R`, `R/uplot_dbe_vs_ma.R`

Примеры:

```
R/calc_eval_params.R:161: mfd[, co_tot := `12C` + `16O`] # sum of carbon and oxygen atoms (required for island plots and dev_n_c plot)
R/calc_recalibrate_ms.R:54: #'   \item{`fig_*`}{Interactive \pkg{plotly} figures comparing mass accuracy
R/calc_recalibrate_ms.R:140: # plot(cal_peaks[, .N, .(ret_time_min)])
R/calc_recalibrate_ms.R:284: # Plot calibration for calibrants before and after recalibration ####
R/calc_recalibrate_ms.R:316: type = "scatter",
R/calc_recalibrate_ms.R:327: type = "scatter",
```

### xcms — 279 попаданий в 35 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/Deprecated.R`, `R/XcmsExperiment-plotting.R`, `R/XcmsExperiment.R`, `R/XcmsExperimentHdf5.R`, `R/do_adjustRtime-functions.R`, `R/do_findChromPeaks-functions.R`, `R/do_groupChromPeaks-functions.R`, `R/functions-Chromatogram.R`, `R/functions-OnDiskMSnExp.R`, `R/functions-XCMSnExp.R`

Примеры:

```
R/AllGenerics.R:31: #' The alignment method can be specified (and configured) using a dedicated
R/AllGenerics.R:375: #' ## Plot the first 4 EICs
R/AllGenerics.R:378: #' ## Plot the first 4 EICs into the same plot
R/AllGenerics.R:400: #' plot(res[1, ])
R/AllGenerics.R:597: #' depending upon (and configured by) using dedicated *parameter* classes. As a
R/AllGenerics.R:902: #' ## Plot the data for the first feature
```

## msms — MS/MS: фрагменты, нейтральные потери, библиотеки

Всего попаданий по всем проектам: **46849**.

### corems — 966 попаданий в 23 файлах

Файлы: `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/parameters.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/MZSearch.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/corems_hdf5.py`, `corems/mass_spectra/input/mzml.py`, `corems/mass_spectra/input/parserbase.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectra/output/export.py`

Примеры:

```
support_code/windows_only_importers/BrukerCompassXtract.py:160: if spectra[scan_number].MSMSStage == 1:
support_code/nmdc/lipidomics/lipidomics_workflow.py:104: scan_translator_dict = {"ms2": {"scan_filter": "", "resolution": "high"}}
support_code/nmdc/lipidomics/lipidomics_workflow.py:207: print("Adding associated ms2 spectra")
support_code/nmdc/lipidomics/lipidomics_workflow.py:213: myLCMSobj.add_associated_ms2_dda(
support_code/nmdc/lipidomics/lipidomics_workflow.py:377: def process_ms2(myLCMSobj, metadata, scan_translator):
support_code/nmdc/lipidomics/lipidomics_workflow.py:378: """Process ms2 spectra and perform molecular search
```

### formultitude — 4 попаданий в 2 файлах

Файлы: `TestFSDBSearch/TotalSupport/CannonMF.cs`, `TestFSDBSearch/TotalSupport/ttlAI.cs`

Примеры:

```
TestFSDBSearch/TotalSupport/CannonMF.cs:71: NewIsotope.ReAtMa = double.Parse(ttlAI.FragmentOfChoice(strArray2[1].Trim(), 0, "(", true, "0", "-1", "0"));
TestFSDBSearch/TotalSupport/CannonMF.cs:73: NewIsotope.ComPct = double.Parse(ttlAI.FragmentOfChoice(strArray2[1].Trim(), 0, "(", true, "0", "-1", "0")) / 100.0;
TestFSDBSearch/TotalSupport/CannonMF.cs:77: this.Els[index].StAtWe = double.Parse(ttlAI.FragmentOfChoice(strArray2[1].Trim(), 0, "(", true, "0", "-1", "0"));
TestFSDBSearch/TotalSupport/ttlAI.cs:1022: public static string FragmentOfChoice(string s, int pos, string deli, bool ErrorValueIfNotNumeric, string ValueIfEmpty = "0", string ValueIfError = "-1", string
```

### mfassignr — 12 попаданий в 4 файлах

Файлы: `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`

Примеры:

```
MFAssignR/R/MFAssign.R:128: #' @param MSMS character:
MFAssignR/R/MFAssign.R:160: Ambig = "off", MSMS = "off", S34_abund = 30, C13_abund = 60, N3corr = "on") {
MFAssignR/R/MFAssign.R:241: if(MSMS == "off"){
MFAssignR/R/MFAssignCHO.R:90: #' @param MSMS character:
MFAssignR/R/MFAssignCHO.R:110: Omin = 0, max_def = 0.9, min_def = 0.5, HetCut = "off", NMScut = "on", DeNovo = 1000, nLoop = 5, Ambig = "off", MSMS = "off") {
MFAssignR/R/MFAssignCHO.R:190: if(MSMS == "off"){
```

### msdial — 17658 попаданий в 780 файлах

Файлы: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/SpectralEntropyBenchmark.cs`, `src/Common/ChartDrawing/Base/Utility.cs`, `src/Common/ChartDrawing/Legacy/ChromatogramBean.cs`, `src/Common/CommonMVVM/Converter/MethodTypeDdMsmsEnumToBoolConverter.cs`, `src/Common/CommonMVVM/Converter/MethodTypeDiMsmsEnumToBoolConverter.cs`, `src/Common/CommonStandard/Algorithm/Function/MolecularNetworkInstance.cs`, `src/Common/CommonStandard/Algorithm/Function/MoleculerNetworking.cs`, `src/Common/CommonStandard/Algorithm/Function/SpectrumHandler.cs`, `src/Common/CommonStandard/Algorithm/Scoring/Ms2ScanMatching.cs`, `src/Common/CommonStandard/Algorithm/Scoring/MsScanMatching.cs`, `src/Common/CommonStandard/Algorithm/Scoring/RetentionMatchPolicy.cs`, `src/Common/CommonStandard/Alignment/AlignedPeakPropertyBean.cs`

Примеры:

```
src/RawDataApp/RawDataViewer/Model/MsSnDistribution.cs:24: Brush = new KeyBrushMapper<ChromatogramPeakFeature, bool>(new Dictionary<bool, Brush> { [false] = Brushes.Blue, [true] = Brushes.Red }, peak => peak.IsMsmsConta
src/RawDataApp/RawDataViewer/Model/MsSpectrumIntensitySummarizer.cs:16: (var ms1, var ms2) = new RawDataAccess().ParseRawdataForStatistics(spectra);
src/RawDataApp/RawDataViewer/Model/MsSpectrumIntensitySummarizer.cs:20: new MsSpectrumSummary(ConvertFreqToDataPoint(ms2), "Histogram of ms2 spectrum intensity"),
src/MSFINDER/MassSpectrogramMsfinder/MassSpectrogramDisplayLabel.cs:14: private PeakFragmentPair peakFragmentPair;
src/MSFINDER/MassSpectrogramMsfinder/MassSpectrogramDisplayLabel.cs:35: public PeakFragmentPair PeakFragmentPair
src/MSFINDER/MassSpectrogramMsfinder/MassSpectrogramDisplayLabel.cs:37: get { return peakFragmentPair; }
```

### mzmine — 11037 попаданий в 785 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/ArticleReferences.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/util/color/ColorsFX.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/Frame.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MZmineProject.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MergedMassSpectrum.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MergedMsMsSpectrum.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/PrecursorIonTree.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/PrecursorIonTreeNode.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/Scan.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/MobilityScanDataAccess.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/LayoutToRecordGenerator.java:142: MassLynxLib.C_FLOAT.withName("precursorMz"),
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:87: * Spectral library formats
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:153: private static final ExtensionFilter ALL_SPECTRAL_LIBRARY_FILTER = new ExtensionFilter(
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:154: "All spectral libraries", "*.json", "*.msp", "*.mgf", "*.jdx");
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:156: public static final List<ExtensionFilter> ALL_LIBRARY = List.of(ALL_SPECTRAL_LIBRARY_FILTER,
mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java:70: String PROPERTY_PRECURSORMZ = "Precursor mz";
```

### openms — 16890 попаданий в 669 файлах

Файлы: `doc/code_examples/Tutorial_FileIO.cpp`, `doc/code_examples/Tutorial_MSChromatogram.cpp`, `doc/code_examples/Tutorial_MSExperiment.cpp`, `doc/code_examples/Tutorial_Precursor.cpp`, `doc/code_examples/Tutorial_ProForma.cpp`, `doc/code_examples/Tutorial_TheoreticalSpectrumGenerator.cpp`, `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/SQLiteCpp/cpplint.py`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.h`, `src/openms/extern/simde/simde/x86/mmx.h`, `src/openms/include/OpenMS/ANALYSIS/ID/AScore.h`

Примеры:

```
tools/scripts/export_peptdeep_models_to_onnx.py:24: # The instrument reaches the MS2 model as a one-hot of width MAX_INSTRUMENT_NUM, so the position of
tools/scripts/export_peptdeep_models_to_onnx.py:33: description="Export PeptDeep RT, MS2, and CCS pretrained PyTorch models to ONNX."
tools/scripts/export_peptdeep_models_to_onnx.py:39: help=f"Directory containing rt.pth, ms2.pth, and ccs.pth. Default: {DEFAULT_PRETRAINED_DIR}",
tools/scripts/export_peptdeep_models_to_onnx.py:64: """Width of the instrument one-hot baked into an exported MS2 graph.
tools/scripts/export_peptdeep_models_to_onnx.py:124: if task == "ms2":
tools/scripts/export_peptdeep_models_to_onnx.py:194: def export_ms2(pretrained_dir, out_dir):
```

### pyc2mc — 1 попаданий в 1 файлах

Файлы: `Image.py`

Примеры:

```
Image.py:18: img_str="iVBORw0KGgoAAAANSUhEUgAAAmwAAAGnCAYAAAAKUgvPAAAgAElEQVR4nMy9d5Bl53Undr573+scJ/XkATAYDDIGgEAikABIAiQIgABBSlpRDJLMXSq5pLV27a3aLatorWu9trVm2bJdG7Sl9aqkkpe
```

### ume — 1 попаданий в 1 файлах

Файлы: `R/calc_isotope_pattern.R`

Примеры:

```
R/calc_isotope_pattern.R:208: # --- helper: convert composition row to mf_iso fragment -------------------
```

### xcms — 280 попаданий в 23 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/MsExperiment-functions.R`, `R/MsExperiment.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment-plotting.R`, `R/XcmsExperiment.R`, `R/functions-IO.R`, `R/functions-OnDiskMSnExp.R`, `R/functions-XCMSnExp.R`, `R/functions-XChromatogram.R`, `R/functions-utils.R`

Примеры:

```
R/AllGenerics.R:207: #'     or LC-MS/MS data this might however be a too low threshold and it should
R/AllGenerics.R:418: #' Extract (MS1 or MS2) spectra from an [XcmsExperiment] or [XCMSnExp] object
R/AllGenerics.R:425: #' `msLevel = 2L` MS2 spectra are returned for a chromatographic
R/AllGenerics.R:426: #' peak if their precursor m/z is within the retention time and m/z range of
R/AllGenerics.R:434: #' - `method = "closest_mz"`: return the spectrum with the precursor m/z
R/AllGenerics.R:461: #' See also the *LC-MS/MS data analysis* vignette for more details and examples.
```

## ion_mobility_ccs — Ионная подвижность / CCS

Всего попаданий по всем проектам: **8835**.

### formultitude — 2 попаданий в 1 файлах

Файлы: `TestFSDBSearch/TotalSupport/ttlAI.cs`

Примеры:

```
TestFSDBSearch/TotalSupport/ttlAI.cs:43: public static IonizationMethod AI_IonizationMethod_String2Enum(string ims)
TestFSDBSearch/TotalSupport/ttlAI.cs:45: string Left = ims.Trim();
```

### msdial — 4436 попаданий в 264 файлах

Файлы: `src/Common/CommonStandard/Algorithm/Scoring/MsScanMatching.cs`, `src/Common/CommonStandard/Algorithm/Scoring/RetentionMatchPolicy.cs`, `src/Common/CommonStandard/Alignment/AlignedPeakPropertyBean.cs`, `src/Common/CommonStandard/Alignment/AlignmentPropertyBean.cs`, `src/Common/CommonStandard/Components/BaseChromatogramPeakFeature.cs`, `src/Common/CommonStandard/Components/ChromX.cs`, `src/Common/CommonStandard/Components/ChromXs.cs`, `src/Common/CommonStandard/Components/Chromatogram.cs`, `src/Common/CommonStandard/Components/Interfaces/ITimes.cs`, `src/Common/CommonStandard/Components/SpecificExperimentChromatogram.cs`, `src/Common/CommonStandard/DataObj/MspRecord.cs`, `src/Common/CommonStandard/DataObj/RawData.cs`

Примеры:

```
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:28: var providerFactory = new MsdialImmsCore.Algorithm.ImmsAverageDataProviderFactory(massTolerance: 0.001, driftTolerance: 0.002);
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:57: var flatten = peaks.SelectMany(peak => peak.DriftChromFeatures).ToList();
src/MSFINDER/MsfinderConsoleAppCore/Process/SpectrumCuration.cs:105: Ccs = storage.CollisionCrossSection,
src/MSFINDER/MsfinderConsoleAppCore/Process/SpectrumCuration.cs:229: sw.WriteLine("CCS: " + rawdata.Ccs);
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:232: var ccsSimilarity = mspRecord.CollisionCrossSection >= 0 && rawData.Ccs >= 0 ? LcmsScoring.GetGaussianSimilarity((float)rawData.Ccs, mspRecord.CollisionCrossSec
src/MSFINDER/MsfinderCommonStandard/Process/StructureFinder.cs:356: if (isUseCcsForFilter && mspDB[i].CollisionCrossSection > 0.0 && rawData.Ccs > 0 && Math.Abs(mspDB[i].CollisionCrossSection - rawData.Ccs) > ccsTol) continue;
```

### mzmine — 1677 попаданий в 404 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/FeatureIdentity.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/Frame.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MobilityScan.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MobilityType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/BinningMobilogramDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/FeatureDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/FeatureFullDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/MobilogramDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/ScanDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/FeatureDataUtils.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/IonMobilitySeries.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/featuredata/IonMobilogramTimeSeries.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/LayoutToRecordGenerator.java:141: MassLynxLib.C_INT.withName("driftScanCount"), MassLynxLib.C_INT.withName("isProfile"),
utils/src/main/java/io/github/mzmine/util/collections/CollectionUtils.java:449: //          logger.fine("REUSING OLD MASTER LIST FOR IMS DATA");
reports/src/main/java/io/mzmine/reports/FeatureSummary.java:8: private final String ccs;
reports/src/main/java/io/mzmine/reports/FeatureSummary.java:15: public FeatureSummary(String id, String mz, String rtInMinutes, String ccs, String height,
reports/src/main/java/io/mzmine/reports/FeatureSummary.java:20: this.ccs = ccs;
reports/src/main/java/io/mzmine/reports/FeatureSummary.java:41: return ccs;
```

### openms — 2714 попаданий в 268 файлах

Файлы: `src/openms/include/OpenMS/ANALYSIS/ID/IDBoostGraph.h`, `src/openms/include/OpenMS/ANALYSIS/ID/MetaboliteSpectralMatching.h`, `src/openms/include/OpenMS/ANALYSIS/ID/ProSEAlgorithm.h`, `src/openms/include/OpenMS/ANALYSIS/MAPMATCHING/MapAlignmentAlgorithmKD.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/CalibrationWorkflow.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/ChromatogramExtractor.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/ChromatogramExtractorAlgorithm.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/DIAPrescoring.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/DIAScoring.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/IonMobilityScoring.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/MRMFeatureFinderScoring.h`, `src/openms/include/OpenMS/ANALYSIS/OPENSWATH/OpenSwathExportData.h`

Примеры:

```
tools/scripts/export_peptdeep_models_to_onnx.py:33: description="Export PeptDeep RT, MS2, and CCS pretrained PyTorch models to ONNX."
tools/scripts/export_peptdeep_models_to_onnx.py:39: help=f"Directory containing rt.pth, ms2.pth, and ccs.pth. Default: {DEFAULT_PRETRAINED_DIR}",
tools/scripts/export_peptdeep_models_to_onnx.py:121: if task == "ccs":
tools/scripts/export_peptdeep_models_to_onnx.py:234: "peptdeep.model.ccs",
tools/scripts/export_peptdeep_models_to_onnx.py:239: model = warmup_and_load(model, pretrained_dir / "ccs.pth", "ccs")
tools/scripts/export_peptdeep_models_to_onnx.py:243: args=make_dummy_inputs("ccs"),
```

### xcms — 6 попаданий в 3 файлах

Файлы: `R/functions-OnDiskMSnExp.R`, `R/methods-xcmsSet.R`, `R/plotQC.R`

Примеры:

```
R/functions-OnDiskMSnExp.R:463: ## Drift of measured scan times - expected to be largest at the end.
R/functions-OnDiskMSnExp.R:466: ## If the drift is larger than the threshold, cut the matrix up to the
R/methods-xcmsSet.R:955: ## Drift of measured scan times - expected to be largest at the end.
R/methods-xcmsSet.R:958: ## If the drift is larger than the threshold, cut the matrix up to the
R/plotQC.R:19: #'                   of measurement to detect time drift
R/plotQC.R:24: #'  "mzdevtime": Shows whether m/z deviations are RT dependent, could indicate instrument drift
```

## molecular_networking — Молекулярные сети

Всего попаданий по всем проектам: **119**.

### msdial — 27 попаданий в 16 файлах

Файлы: `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialGcms.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsdialLcms.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsfinder.cs`, `src/Common/CommonStandard/Parameters/AnalysisParamOfMsfinder.cs`, `src/Common/CommonStandard/Parser/MsFinderIniParser.cs`, `src/Common/CommonStandard/Utility/AnnotationName.cs`, `src/MSDIAL4/MsDial/Molecular networking/MolecularNetworkExportWin.xaml.cs`, `src/MSDIAL4/MsDial/Molecular networking/MolecularNetworkSettingWin.xaml.cs`, `src/MSDIAL4/MsdialMolecularNetworkingConsoleApp/Test/MoleculerNetworkTest.cs`, `src/MSDIAL4/MsdialPrivateConsoleApp/Program.cs`, `src/MSDIAL5/MsdialCore/Parameter/ParameterBase.cs`, `src/MSDIAL5/MsdialGuiApp/Model/Core/AnalysisModelBase.cs`

Примеры:

```
src/MSFINDER/MsfinderCommonStandard/Utility/MsFinderIniParcer.cs:813: sw.WriteLine("#Msfinder molecular networking (mmn)");
src/MSFINDER/MSFINDER/Molecular networking/MolecularNetworking.cs:48: this.pbw.Title = "Generating nodes and edges for molecular network";
src/MSDIAL5/MsdialGuiApp/ViewModel/DataObj/ParameterBaseVM.cs:1300: // molecular networking
src/MSDIAL5/MsdialGuiApp/Model/Core/AnalysisModelBase.cs:94: _broker.Publish(new ShortMessageRequest("Failed to calculate molecular network.\nPlease check selected peak spot."));
src/MSDIAL5/MsdialGuiApp/Model/Lcimms/LcimmsAnalysisModel.cs:445: _broker.Publish(new ShortMessageRequest("Failed to calculate molecular network.\nPlease check selected peak spot."));
src/MSDIAL5/MsdialCore/Parameter/ParameterBase.cs:416: // molecular networking
```

### mzmine — 77 попаданий в 52 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/networking/NetworkStatsType.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataanalysis/spec_chimeric_precursor/HandleChimericMsMsParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataanalysis/spec_chimeric_precursor/PrecursorPurityCheckerParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/MainSpectralNetworkingModule.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/MainSpectralNetworkingParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/NetworkCluster.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/cosine_no_precursor/NoPrecursorCosineSpectralNetworkingParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/dreams/DreaMSNetworkingModule.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/dreams/DreaMSNetworkingParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/modified_cosine/ModifiedCosineSpectralNetworkingParameters.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/ms2deepscore/MS2DeepscoreNetworkingModule.java`, `mzmine-community/src/main/java/io/github/mzmine/modules/dataprocessing/group_spectral_networking/ms2deepscore/MS2DeepscoreNetworkingParameters.java`

Примеры:

```
mzmine-community/src/main/java/io/github/mzmine/modules/visualization/featurelisttable_modular/FeatureTableContextMenu.java:926: * Open molecular network and center on node
mzmine-community/src/main/java/io/github/mzmine/modules/visualization/networking/AnnotationNetworkModule.java:43: private static final String MODULE_NAME = "Ion Identity Molecular Networks";
mzmine-community/src/main/java/io/github/mzmine/modules/visualization/network_overview/FeatureNetworkOverviewModule.java:41: private static final String MODULE_NAME = "Feature overview / Interactive Ion Identity Molecular Networks";
mzmine-community/src/main/java/io/github/mzmine/modules/visualization/networking/visual/FeatureNetworkPane.java:131: super("Molecular Networks", false, fullGraph);
mzmine-community/src/main/java/io/github/mzmine/modules/tools/batchwizard/subparameters/WorkflowDdaWizardParameters.java:40: Applies feature-based molecular networking/ion identity molecular networking
mzmine-community/src/main/java/io/github/mzmine/modules/tools/batchwizard/subparameters/WorkflowDdaWizardParameters.java:52: "Export for molecular networking (e.g., GNPS, FBMN, IIMN, MetGem)",
```

### openms — 15 попаданий в 7 файлах

Файлы: `src/openms/include/OpenMS/ANALYSIS/ID/IonIdentityMolecularNetworking.h`, `src/openms/include/OpenMS/FORMAT/GNPSMGFFile.h`, `src/openms/include/OpenMS/FORMAT/GNPSMetaValueFile.h`, `src/openms/include/OpenMS/FORMAT/GNPSQuantificationFile.h`, `src/openms/source/FORMAT/GNPSQuantificationFile.cpp`, `src/pyOpenMS/bindings/bind_analysis.cpp`, `src/topp/GNPSExport.cpp`

Примеры:

```
src/topp/GNPSExport.cpp:29: GNPS (Global Natural Products Social Molecular Networking, http://gnps.ucsd.edu) is an open-access knowledge base for community-wide organization and sharing of
src/topp/GNPSExport.cpp:30: This tool was developed for the Feature Based Molecular Networking (FBMN) (https://ccms-ucsd.github.io/GNPSDocumentation/featurebasedmolecularnetworking/) and I
src/topp/GNPSExport.cpp:33: Nothias, L.-F., Petras, D., Schmid, R. et al. [Feature-based molecular networking in the GNPS analysis environment](https://www.nature.com/articles/s41592-020-0
src/topp/GNPSExport.cpp:45: - Run MetaboliteAdductDecharger on the featureXML files (optional, for Ion Identity Molecular Networking).
src/topp/GNPSExport.cpp:74: - Upload your files to GNPS and run the Feature-Based Molecular Networking workflow. Instructions can be found here: https://ccms-ucsd.github.io/GNPSDocumentati
src/topp/GNPSExport.cpp:93: "Feature-based Molecular Networking in the GNPS Analysis Environment", // title
```

## qc_metrics — QC-метрики (blank, CV, дрейф)

Всего попаданий по всем проектам: **8342**.

### corems — 19 попаданий в 6 файлах

Файлы: `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/input/rawFileReader.py`, `corems/mass_spectra/output/export.py`, `corems/mass_spectrum/calc/Calibration.py`, `corems/molecular_formula/input/masslist_ref.py`, `corems/molecular_id/search/database_interfaces.py`

Примеры:

```
corems/molecular_id/search/database_interfaces.py:610: # Add last spectrum if file doesn't end with blank line
corems/molecular_formula/input/masslist_ref.py:302: If you need to use heavy isotopes please use another reference file format that separate the formula string by a blank space and parse it using the function cor
corems/mass_spectrum/calc/Calibration.py:114: # We assume header lines start with '#' (or '##') and ignore blank lines.
corems/mass_spectrum/calc/Calibration.py:134: # Join the lines from the beginning of data (this might include a blank line)
corems/mass_spectra/input/rawFileReader.py:978: It will also not return Labels (keys) where the value is blank
corems/mass_spectra/input/rawFileReader.py:1031: It will also not return Labels (keys) where the value is blank
```

### icbmocean — 4 попаданий в 1 файлах

Файлы: `isotope_ratio_deviance_function.R`

Примеры:

```
isotope_ratio_deviance_function.R:29: P<-ggplot(data.frame(x=group,y=rdeviance),aes(x=x,y=y))+geom_violin(scale="area",trim=FALSE,adjust=1.2,position=position_dodge(width = 0.7))+geom_boxplot(aes(gr
isotope_ratio_deviance_function.R:32: P<-ggplot(data.frame(x=group,y=rdeviance),aes(x=x,y=y))+geom_violin(scale="area",trim=FALSE,adjust=1.2,position=position_dodge(width = 0.7))+geom_boxplot(aes(gr
isotope_ratio_deviance_function.R:37: P<-ggplot(data.frame(x=group,y=rdeviance),aes(x=x,y=y))+geom_violin(scale="area",trim=FALSE,adjust=1.2,position=position_dodge(width = 0.7))+geom_boxplot(aes(gr
isotope_ratio_deviance_function.R:41: P<-ggplot(data.frame(x=1:10,y=1:10),aes(x,y))+annotate("text",x=1,y=2,label="Dear Geochemist, you have not enough ratios to plot a density",size=5)+labs(title="
```

### mfassignr — 55 попаданий в 7 файлах

Файлы: `MFAssignR/R/KMDNoise.R`, `MFAssignR/R/MFAssign.R`, `MFAssignR/R/MFAssignCHO.R`, `MFAssignR/R/MFAssignCHO_RMD.R`, `MFAssignR/R/MFAssign_RMD.R`, `MFAssignR/R/RecalFunctions.R`, `Supplemental MFAssign Scripts/Background Subtraction Guidelines.R`

Примеры:

```
Supplemental MFAssign Scripts/Background Subtraction Guidelines.R:3: #For the purpose of this example, "Blank" corresponds to the assigned mass list for the blank sample
Supplemental MFAssign Scripts/Background Subtraction Guidelines.R:6: #First I would recommend selecting only a few columns from the blank and
Supplemental MFAssign Scripts/Background Subtraction Guidelines.R:9: Blank2 <- Blank2 %>% select(formula, exp_mass, abundance) %>%
Supplemental MFAssign Scripts/Background Subtraction Guidelines.R:10: rename(blank_mass = exp_mass, blank_abund = abundance)
Supplemental MFAssign Scripts/Background Subtraction Guidelines.R:12: #Next you can align this Blank subset to the actual sample dataframe
Supplemental MFAssign Scripts/Background Subtraction Guidelines.R:14: Combo <- left_join(Sample, Blank2, by = "formula")
```

### msdial — 4176 попаданий в 247 файлах

Файлы: `src/Common/ChartDrawing/Chart/AreaChartControl.cs`, `src/Common/ChartDrawing/Chart/BarControl.cs`, `src/Common/ChartDrawing/Chart/DendrogramControl.cs`, `src/Common/ChartDrawing/Chart/LineSpectrumControl.cs`, `src/Common/ChartDrawing/Chart/ScatterControl.cs`, `src/Common/ChartDrawing/UI/ListColorPicker.cs`, `src/Common/CommonStandard/Alignment/AlignedPeakPropertyBean.cs`, `src/Common/CommonStandard/Alignment/AlignmentPropertyBean.cs`, `src/Common/CommonStandard/Components/BaseChromatogramPeakFeature.cs`, `src/Common/CommonStandard/Components/ChromX.cs`, `src/Common/CommonStandard/Components/ChromXs.cs`, `src/Common/CommonStandard/Components/Chromatogram.cs`

Примеры:

```
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:28: var providerFactory = new MsdialImmsCore.Algorithm.ImmsAverageDataProviderFactory(massTolerance: 0.001, driftTolerance: 0.002);
src/RawDataApp/RawDataViewer/Model/MsPeakSpotsDetector.cs:57: var flatten = peaks.SelectMany(peak => peak.DriftChromFeatures).ToList();
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/AlignmentRetentionTimeCorrection.cs:118: /// Interpolates two correction models by analytical order. This is used for Blank files that do
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/AlignmentRetentionTimeCorrection.cs:215: foreach (var driftFeature in feature.DriftChromFeatures ?? Enumerable.Empty<ChromatogramPeakFeature>()) {
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/AlignmentRetentionTimeCorrection.cs:216: Correct(driftFeature, model);
src/MSDIAL5/MsdialLcMsApi/Algorithm/Alignment/AlignmentRetentionTimeCorrection.cs:227: value.Drift,
```

### mzmine — 972 попаданий в 336 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxTextFields.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/skins/DynamicTextFieldSkin.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/dialogs/DialogLoggerUtil.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/properties/PropertyUtils.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/validation/FxValidation.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/IonizationType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MobilityType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/BinningMobilogramDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/preferences/FeatureListPreferences.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/CvTermType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/rawfiletypes/RawFileMetadataTypes.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/LayoutToRecordGenerator.java:141: MassLynxLib.C_INT.withName("driftScanCount"), MassLynxLib.C_INT.withName("isProfile"),
utils/src/main/java/io/github/mzmine/util/StringUtils.java:53: if (input == null || input.isBlank()) {
utils/src/main/java/io/github/mzmine/util/StringUtils.java:68: if (isBlank(word)) {
utils/src/main/java/io/github/mzmine/util/StringUtils.java:90: if (StringUtils.isBlank(str)) {
utils/src/main/java/io/github/mzmine/util/StringUtils.java:160: if (str == null || str.isBlank()) {
utils/src/main/java/io/github/mzmine/util/StringUtils.java:203: if (str == null || str.isBlank()) {
```

### openms — 2938 попаданий в 352 файлах

Файлы: `doc/doxygen/parameters/DefaultParamHandlerDocumenter.cpp`, `src/openms/extern/SQLiteCpp/cpplint.py`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/extern/evergreen/src/Utility/graph_to_dot.hpp`, `src/openms/extern/nlohmann_json/include/nlohmann/detail/meta/type_traits.hpp`, `src/openms/extern/nlohmann_json/single_include/nlohmann/json.hpp`, `src/openms/include/OpenMS/ANALYSIS/ID/IDBoostGraph.h`, `src/openms/include/OpenMS/ANALYSIS/ID/MetaboliteSpectralMatching.h`, `src/openms/include/OpenMS/ANALYSIS/ID/Percolator.h`, `src/openms/include/OpenMS/ANALYSIS/ID/PercolatorTypes.h`, `src/openms/include/OpenMS/ANALYSIS/ID/ProSEAlgorithm.h`, `src/openms/include/OpenMS/ANALYSIS/ID/Scores.h`

Примеры:

```
tools/scripts/visualize_pasef_centroiding.py:91: spectrum has no per-peak IM array (e.g. DDA MS2 with scalar drift_time).
src/pyOpenMS/fix_stubs.py:8: 4. RST ``.. code-block::`` directives need blank line + indented body
src/pyOpenMS/fix_stubs.py:117: examples lack the blank line and extra indentation required by RST::
src/pyOpenMS/fix_stubs.py:139: # Check if the next line is already blank (already formatted)
src/pyOpenMS/fix_stubs.py:140: next_is_blank = (i + 1 < len(lines) and lines[i + 1].strip() == '')
src/pyOpenMS/fix_stubs.py:141: if not next_is_blank:
```

### pyc2mc — 4 попаданий в 2 файлах

Файлы: `Image.py`, `modules/resources_rc.py`

Примеры:

```
Image.py:18: img_str="iVBORw0KGgoAAAANSUhEUgAAAmwAAAGnCAYAAAAKUgvPAAAgAElEQVR4nMy9d5Bl53Undr573+scJ/XkATAYDDIGgEAikABIAiQIgABBSlpRDJLMXSq5pLV27a3aLatorWu9trVm2bJdG7Sl9aqkkpe
modules/resources_rc.py:364: \xb8\xd7\x85Z|cV\xf91\xae\x147\xab6\xae\xbc\
modules/resources_rc.py:9311: cket end=\x22r\x22?>cv\
modules/resources_rc.py:19160: Z\xfe]Qc-\xc6A\xbc\xe1\x1b\x9d\xb2A\xd9/\
```

### ume — 94 попаданий в 9 файлах

Файлы: `R/calc_recalibrate_ms.R`, `R/classify_files.R`, `R/data.R`, `R/filter.R`, `R/remove_blanks.R`, `R/theme_uplots.R`, `R/ume_utilities.R`, `R/uplot_freq_vs_ppm.R`, `R/uplot_ms.R`

Примеры:

```
R/calc_recalibrate_ms.R:96: # Assign different calibration lists to file_id (i.e. blanks with cal_fa_neg, samples with other)
R/calc_recalibrate_ms.R:97: # assign file_ids to either sample or blank
R/classify_files.R:6: #' Classifies entries into categories (blank, standard, pool, sample, …)
R/classify_files.R:12: #' - `"blank"`: `blank_check == "blank"` or pattern `"blk"`
R/classify_files.R:27: #' @param include_blank_check Logical; if TRUE and `blank_check` exists, it is
R/classify_files.R:28: #'   used to assign `"blank"`.
```

### xcms — 80 попаданий в 9 файлах

Файлы: `R/AllGenerics.R`, `R/do_adjustRtime-functions.R`, `R/functions-OnDiskMSnExp.R`, `R/functions-XCMSnExp.R`, `R/method-filterFeatures.R`, `R/methods-xcmsSet.R`, `R/plotQC.R`, `R/write.mzquantML.R`, `R/writemztab.R`

Примеры:

```
R/AllGenerics.R:75: #' user-selected subset of samples (e.g. QC samples) after which all samples
R/AllGenerics.R:93: #' See also section *Alignment of experiments including blanks* in the
R/AllGenerics.R:1631: #'   to exclude certain samples or groups (e.g. blanks) from the feature
R/AllGenerics.R:1730: #'     all blanks in an experiment will for example avoid features to be
R/AllGenerics.R:1731: #'     defined for signals (chrom peaks) present only in blank samples.
R/do_adjustRtime-functions.R:34: #' subset. This allows to e.g. exclude blank samples from the alignment process
```

## provenance_workflow — Workflow, provenance, параметры, batch

Всего попаданий по всем проектам: **11034**.

### corems — 896 попаданий в 34 файлах

Файлы: `conftest.py`, `corems/chroma_peak/factory/chroma_peak_classes.py`, `corems/encapsulation/factory/processingSetting.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `corems/mass_spectra/factory/GC_Class.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/boosterHDF5.py`, `corems/mass_spectra/input/corems_hdf5.py`, `corems/mass_spectra/input/mzml.py`, `corems/mass_spectra/input/parserbase.py`, `corems/mass_spectra/input/rawFileReader.py`

Примеры:

```
conftest.py:17: "https://nmdcdemo.emsl.pnnl.gov/minio/lipidomics/parameter_files/"
conftest.py:140: return "postgresql://coremsdb:coremsmolform@postgres:5432/molformula"  ## Git CI/CD Build Pipeline
setup.py:3: All project metadata and dependencies are defined in pyproject.toml.
support_code/nmdc/lipidomics/lipidomics_workflow.py:19: from corems.mass_spectra.input.corems_hdf5 import ReadCoreMSHDFMassSpectra
support_code/nmdc/lipidomics/lipidomics_workflow.py:301: def export_results(myLCMSobj, out_path, molecular_metadata=None, final=False):
support_code/nmdc/lipidomics/lipidomics_workflow.py:302: """Export results to hdf5 and csv as a lipid report
```

### formultitude — 1 попаданий в 1 файлах

Файлы: `CIA/FormultitudeProgram.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:848: //AFTER AUTOMATION THIS DILEMA SHOULD BE RESOLVED ON A PARAMETER FILE LEVEL(N.T.)
```

### msdial — 1711 попаданий в 206 файлах

Файлы: `benchmark/CompMs/CommonStandardBenchmark/Algorithm/Scoring/MsScanMatchingBenchmark.cs`, `src/Common/ChartDrawing/Adorner/ChartSelectionRubberAdorner.cs`, `src/Common/ChartDrawing/Adorner/RangeSelectAdorner.cs`, `src/Common/ChartDrawing/Adorner/RubberAdorner.cs`, `src/Common/ChartDrawing/AxisManager/AutoContinuousAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/CategoryAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/ContinuousAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/DependencyContinuousAxisManager.cs`, `src/Common/ChartDrawing/AxisManager/FreezableAxisManager.cs`, `src/Common/ChartDrawing/Base/ChartBaseControl.cs`, `src/Common/ChartDrawing/Behavior/AddMovabilityBehavior.cs`, `src/Common/ChartDrawing/Behavior/AreaSelectBehavior.cs`

Примеры:

```
src/MSFINDER/MSFINDER/MainWindow.xaml.cs:447: //InSilicoFragmenter.FragmentGenerator(@"C:\Users\tensa_000\Documents\Metabolomics project\Small Molecular SDFs\20150106_Downloaded_Sdfs\IntegratedMetaData\Exis
src/MSFINDER/MsfinderCommonStandard/Utility/MsFinderIniParcer.cs:797: sw.WriteLine("#Batch job");
src/MSFINDER/MSFINDER/Process/FormulaFinderBatchProcess.cs:100: MessageBox.Show("Batch job was desorbed by the following error: "
src/MSFINDER/MSFINDER/Process/FormulaFinderBatchProcess.cs:129: MessageBox.Show("Batch job finished! total time(min): " + minutes, "Success", MessageBoxButton.OK, MessageBoxImage.Information);
src/MSFINDER/MSFINDER/Process/PeakAssignerBatchProcess.cs:110: MessageBox.Show("Batch job finished!", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
src/MSFINDER/MSFINDER/Process/StructureFinderBatchProcess.cs:92: MessageBox.Show("Batch job was desorbed by the following error: "
```

### mzmine — 3866 попаданий в 557 файлах

Файлы: `javafx-framework/src/main/java/io/github/mzmine/gui/JavaFxDesktop.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/converters/OptionsStringConverter.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/components/factories/FxComboBox.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/dialogs/DialogLoggerUtil.java`, `javafx-framework/src/main/java/io/github/mzmine/javafx/util/FxIcons.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MZmineProject.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/MetadataOnlyScan.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/RawDataFile.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/data_access/FeatureFullDataAccess.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/FeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/ModularFeatureList.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/CompoundDBAnnotation.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/StringUtils.java:491: * values of the mzmine_sample_type metadata column. Leading and trailing whitespace is removed
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:41: public static final ExtensionFilter MZ_BATCH = new ExtensionFilter("mzmine batch", "*.mzbatch");
utils/src/main/java/io/github/mzmine/util/files/FileAndPathUtil.java:262: * @return the parameter file if it is a directory, otherwise its parent directory
mzmine-community/src/main/java/io/github/mzmine/datamodel/MetadataOnlyScan.java:32: * Only used to build scans and contain metadata, e.g., during loading of scans
mzmine-community/src/main/java/io/github/mzmine/datamodel/MetadataOnlyScan.java:34: public abstract class MetadataOnlyScan implements Scan {
mzmine-community/src/main/java/io/github/mzmine/datamodel/MetadataOnlyScan.java:39: "This scan contains no data, only metadata and is only used to build a scan while reading data.");
```

### nomspectra — 142 попаданий в 7 файлах

Файлы: `nomspectra/diff.py`, `nomspectra/draw.py`, `nomspectra/gui.py`, `nomspectra/metadata.py`, `nomspectra/recal.py`, `nomspectra/spectra.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/diff.py:27: from .metadata import MetaData
nomspectra/diff.py:142: spec.metadata.add({'assigned_by_tmds':True})
nomspectra/diff.py:170: metadata: MetaData
nomspectra/diff.py:171: Metadata object that consist dictonary of metadata
nomspectra/diff.py:175: self.metadata = MetaData()
nomspectra/diff.py:179: self.metadata = spec.metadata
```

### openms — 4021 попаданий в 787 файлах

Файлы: `doc/code_examples/Tutorial_IdentificationClasses.cpp`, `doc/code_examples/Tutorial_ImzMLFile.cpp`, `doc/code_examples/Tutorial_MSChromatogram.cpp`, `doc/code_examples/Tutorial_MetaInfo.cpp`, `doc/code_examples/Tutorial_Precursor.cpp`, `doc/code_examples/Tutorial_TOPP.cpp`, `doc/doxygen/parameters/TOPPDocumenter.cpp`, `src/openms/extern/GTE/Mathematics/FPInterval.h`, `src/openms/extern/GTE/Mathematics/FastMarch2.h`, `src/openms/extern/GTE/Mathematics/FastMarch3.h`, `src/openms/extern/GTE/Mathematics/VETManifoldMeshNR.h`, `src/openms/extern/SQLiteCpp/include/SQLiteCpp/Column.h`

Примеры:

```
tools/scripts/plot_pasef_frames.py:9: Typical workflow::
tools/scripts/plot_pasef_frames.py:352: return "(no bruker:* params in mzML metadata)"
tools/scripts/visualize_pasef_centroiding.py:9: Typical workflow:
src/topp/AssayGeneratorMetabo.cpp:21: #include <OpenMS/METADATA/ProteinIdentification.h>
src/topp/AssayGeneratorMetabo.cpp:43: <td VALIGN="middle" ALIGN = "center" ROWSPAN=1> OpenSWATH pipeline </td>
src/topp/AssayGeneratorMetaboSirius.cpp:49: <td VALIGN="middle" ALIGN = "center" ROWSPAN=1> OpenSWATH pipeline </td>
```

### pyc2mc — 3 попаданий в 1 файлах

Файлы: `modules/resources_rc.py`

Примеры:

```
modules/resources_rc.py:12037: \x22 xmp:MetadataDa\
modules/resources_rc.py:21322: \x22 xmp:MetadataDa\
modules/resources_rc.py:22656: \x22 xmp:MetadataDa\
```

### ume — 25 попаданий в 9 файлах

Файлы: `R/add_known_mf.R`, `R/assign_formulas.R`, `R/convert_data_table_to_molecular_formulas.R`, `R/convert_molecular_formula_to_data_table.R`, `R/create_isotope_expanded_table.R`, `R/create_ume_formula_library.R`, `R/export_ume_results.R`, `R/filter.R`, `R/load_ume_results.R`

Примеры:

```
R/add_known_mf.R:10: #' Annotate molecular formulas using metadata from `ume::known_mf`.
R/assign_formulas.R:10: #'         and additional metadata
R/assign_formulas.R:12: #'   \item A numeric vector of m/z values or neutral masses without additional metadata
R/convert_data_table_to_molecular_formulas.R:143: # Join isotope metadata
R/convert_molecular_formula_to_data_table.R:308: # --- add mass metadata ----------------------------------------------------
R/create_isotope_expanded_table.R:9: #' downstream workflows:
```

### xcms — 369 попаданий в 12 файлах

Файлы: `R/AllGenerics.R`, `R/DataClasses.R`, `R/XcmsExperiment-functions.R`, `R/XcmsExperiment.R`, `R/XcmsExperimentHdf5-functions.R`, `R/XcmsExperimentHdf5.R`, `R/functions-Chromatogram.R`, `R/functions-XCMSnExp.R`, `R/functions-xcmsRaw.R`, `R/method-filterFeatures.R`, `R/methods-XCMSnExp.R`, `R/methods-group-features.R`

Примеры:

```
R/AllGenerics.R:138: #'     [XcmsExperimentHdf5()].
R/AllGenerics.R:453: #' Parameter `chromPeakColumns` allows the user to add specific metadata
R/AllGenerics.R:459: #' to the spectra object as a metadata column named `"chrom_peak_id"`.
R/AllGenerics.R:515: #'   Metadata column `"peak_id"` provides the ID of the respective peak
R/AllGenerics.R:526: #'   spectra for all peaks. Metadata column `"peak_id"` provides the ID of the
R/AllGenerics.R:1066: #' as a metadata column named `"feature_id"`.
```

## io_export — Экспорт результатов (CSV/XLSX/JSON/HDF5)

Всего попаданий по всем проектам: **4082**.

### corems — 581 попаданий в 34 файлах

Файлы: `corems/encapsulation/factory/processingSetting.py`, `corems/encapsulation/input/parameter_from_json.py`, `corems/encapsulation/output/parameter_to_json.py`, `corems/mass_spectra/calc/lc_calc.py`, `corems/mass_spectra/calc/lc_calc_operations.py`, `corems/mass_spectra/factory/GC_Class.py`, `corems/mass_spectra/factory/lc_class.py`, `corems/mass_spectra/input/boosterHDF5.py`, `corems/mass_spectra/input/corems_hdf5.py`, `corems/mass_spectra/input/massList.py`, `corems/mass_spectra/output/export.py`, `corems/mass_spectrum/calc/Calibration.py`

Примеры:

```
support_code/atom_parsers/CreateAtomsDescription.py:1: import pprint, json
support_code/atom_parsers/CreateAtomsDescription.py:52: #print(json.dumps(atoms_dict, indent=4))
support_code/nmdc/lipidomics/lipidomics_workflow.py:255: mf_df.to_csv(good_mf_dir / "good_mass_features.csv", index=True)
support_code/nmdc/lipidomics/lipidomics_workflow.py:271: mf_df_dropped.to_csv(dropped_mf_dir / "dropped_mass_features.csv", index=True)
support_code/nmdc/lipidomics/lipidomics_workflow.py:302: """Export results to hdf5 and csv as a lipid report
support_code/nmdc/lipidomics/lipidomics_workflow.py:317: None, exports results to hdf5 and csv as a lipid report
```

### formultitude — 88 попаданий в 11 файлах

Файлы: `CIA/FormultitudeProgram.cs`, `CiaUi/FormultitudeUIForm.Designer.cs`, `CiaUi/FormultitudeUIForm.cs`, `FileReader/FileReader.cs`, `FindChains/FindChainsForm.cs`, `FindChainsTest/FindChainsTestProgram.cs`, `Support/CChainBlocks.cs`, `Support/CFileReader.cs`, `Support/CIsotope.cs`, `TestFSDBSearch/TotalIPDBSearch.cs`, `TestSpectrumNoiseLevel/TestSpectrumNoiseLevelForm.cs`

Примеры:

```
CIA/FormultitudeProgram.cs:14: using Microsoft.Office.Interop.Excel;
CIA/FormultitudeProgram.cs:27: //    if( Path.GetExtension( Filename ) != ".csv" ) { continue; }
CIA/FormultitudeProgram.cs:646: oStreamWriter = new StreamWriter( Filenames [ FileIndex ].Substring( 0, Filenames [ FileIndex ].Length - FileExtentionLength ) + "CShOut.csv" );
CIA/FormultitudeProgram.cs:708: oStreamWriter = new StreamWriter( Path.GetDirectoryName( Filenames [ 0 ] ) + "\\Report.csv" );
CIA/FormultitudeProgram.cs:1704: //file types: csv, txt, xls, xlsx
CIA/FormultitudeProgram.cs:1710: //read file of text and csv files
```

### icbmocean — 1 попаданий в 1 файлах

Файлы: `ResPow_outlier.R`

Примеры:

```
ResPow_outlier.R:56: D<-read.csv("mydata.csv")
```

### mfassignr — 3 попаданий в 2 файлах

Файлы: `Supplemental MFAssign Scripts/Formula Assignment Reader.R`, `Supplemental MFAssign Scripts/Full MFAssignR Example.R`

Примеры:

```
Supplemental MFAssign Scripts/Formula Assignment Reader.R:10: #IF YOU HAVE MULTIPLE SUB-FOLDERS CONTAINING .CSV FILES WITHIN YOUR DATA FOLDER, THIS FUNCTION WILL PULL ALL OF THEM
Supplemental MFAssign Scripts/Formula Assignment Reader.R:16: file_list=list.files(path=folder, pattern="*_MS.csv")
Supplemental MFAssign Scripts/Full MFAssignR Example.R:14: Data <- read.csv("Your data.csv")
```

### msdial — 215 попаданий в 59 файлах

Файлы: `src/Common/CommonStandard/Algorithm/Function/MolecularNetworkInstance.cs`, `src/Common/CommonStandard/ClassyfireApiStandard/ClassfireProtocol.cs`, `src/Common/CommonStandard/Lipidomics/LipidClassDictionary.cs`, `src/Common/CommonStandard/Lipidomics/LipidEieioMsmsCharacterization.cs`, `src/Common/CommonStandard/Lipidomics/LipidOadMsmsCharacterization.cs`, `src/Common/CommonStandard/Lipidomics/MsmsCharacterization.cs`, `src/Common/CommonStandard/Paramerter/AnalysisParamOfMsfinder.cs`, `src/Common/CommonStandard/Parameters/AnalysisParamOfMsfinder.cs`, `src/Common/CommonStandard/PugRestApiStandard/PubRestProtocol.cs`, `src/Common/NCDK/IO/Formats/MoSSOutputFormat.cs`, `src/Common/spectra-hash/splash/SplashRunner.cs`, `src/Common/spectra-hash/splash/impl/AbstractSpectrum.cs`

Примеры:

```
src/MSFINDER/MSFINDER/Molecular networking/MolecularNetworking.cs:14: using Newtonsoft.Json;
src/MSFINDER/MSFINDER/Molecular networking/MolecularNetworking.cs:243: var json = JsonConvert.SerializeObject(rootObj, Formatting.Indented);
src/MSFINDER/MSFINDER/Molecular networking/MolecularNetworking.cs:246: var exportpath = curDir + "CytoscapeLocal/elements.json";
src/MSFINDER/MSFINDER/Molecular networking/MolecularNetworking.cs:248: sw.WriteLine(json.ToString());
src/MSFINDER/MSFINDER/Version update/VersionUpdateNotificationService.cs:3: using System.Runtime.Serialization.Json;
src/MSFINDER/MSFINDER/Version update/VersionUpdateNotificationService.cs:58: client.Headers.Add(HttpRequestHeader.ContentType, "application/json");
```

### mzmine — 567 попаданий в 198 файлах

Файлы: `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundannotations/CompoundDBAnnotation.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/CompoundMemberDTO.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/CompoundMembers.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/compoundlist/CompoundMembersDTO.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/correlation/project_io/R2RDtoConverter.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/correlation/project_io/R2RNetworkingMapsDto.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/correlation/project_io/R2RNetworkingMapsLoader.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/correlation/project_io/R2RNetworkingMapsSaver.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/correlation/project_io/R2RRelationshipDto.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/DataType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/JsonStringType.java`, `mzmine-community/src/main/java/io/github/mzmine/datamodel/features/types/abstr/StringListType.java`

Примеры:

```
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:70: * CSV and TSV import export
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:72: public static final ExtensionFilter CSV = new ExtensionFilter("comma-separated data", "*.csv");
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:76: public static final ExtensionFilter CSV_OR_TSV = new ExtensionFilter("CSV or TSV data", "*.csv",
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:80: public static final List<ExtensionFilter> CSV_TSV_IMPORT = List.of(CSV_OR_TSV, CSV, TSV,
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:82: public static final List<ExtensionFilter> CSV_TSV_EXPORT = List.of(CSV, TSV);
utils/src/main/java/io/github/mzmine/util/files/ExtensionFilters.java:84: // general json format
```

### nomspectra — 30 попаданий в 3 файлах

Файлы: `nomspectra/gui.py`, `nomspectra/spectra.py`, `nomspectra/spectrum.py`

Примеры:

```
nomspectra/gui.py:259: self.spec.to_csv(file)
nomspectra/gui.py:584: self.err.table.to_csv(file, index=False)
nomspectra/gui.py:691: spec.to_csv(f'{file}/out/{spec.metadata["name"]}.txt')
nomspectra/gui.py:1097: file, _ = QFileDialog.getSaveFileName(self, 'Save File', f"data.csv")
nomspectra/gui.py:1100: self.temp_df.to_csv(file)
nomspectra/spectra.py:23: import json
```

### openms — 2336 попаданий в 170 файлах

Файлы: `doc/code_examples/Tutorial_ProForma.cpp`, `share/OpenMS/SCRIPTS/InternalCalibration_Models.R`, `share/OpenMS/SCRIPTS/InternalCalibration_Residuals.R`, `src/openms/extern/GTE/Mathematics/Torus3.h`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.c`, `src/openms/extern/SQLiteCpp/sqlite3/sqlite3.h`, `src/openms/extern/nlohmann_json/include/nlohmann/adl_serializer.hpp`, `src/openms/extern/nlohmann_json/include/nlohmann/byte_container_with_subtype.hpp`, `src/openms/extern/nlohmann_json/include/nlohmann/detail/abi_macros.hpp`, `src/openms/extern/nlohmann_json/include/nlohmann/detail/conversions/from_json.hpp`, `src/openms/extern/nlohmann_json/include/nlohmann/detail/conversions/to_chars.hpp`, `src/openms/extern/nlohmann_json/include/nlohmann/detail/conversions/to_json.hpp`

Примеры:

```
src/topp/AssayGeneratorMetaboSirius.cpp:206: CsvFile csv(compoundinfo_file, '\t');
src/topp/AssayGeneratorMetaboSirius.cpp:207: size_t row_count = csv.rowCount();
src/topp/AssayGeneratorMetaboSirius.cpp:210: csv.getRow(i, row_data);
src/topp/EICExtractor.cpp:49: <td VALIGN="middle" ALIGN = "center" ROWSPAN=1> statistical tools, e.g., Excel, R, ... </td>
src/topp/EICExtractor.cpp:174: registerStringOption_("out_separator", "<sep>", ",", "Separator character for output CSV file.", false, true);
src/topp/EICExtractor.cpp:178: setValidFormats_("out", ListUtils::create<std::string>("csv"));
```

### pyc2mc — 182 попаданий в 15 файлах

Файлы: `main.py`, `modules/comparison.py`, `modules/data_views.py`, `modules/file_operations.py`, `modules/molecular_maps.py`, `modules/plots.py`, `modules/pyc2mc_ui.py`, `modules/window_actions.py`, `src/loading/loading_function.py`, `src/processing/fuse_replicates.py`, `src/processing/merge_csv_from_same_spectrum.py`, `src/processing/merge_function.py`

Примеры:

```
main.py:82: df = pandas.read_csv("Isotopes.csv", sep=";")
main.py:410: # Merge csv from same sepctrum
modules/comparison.py:79: leg_1 = leg_1.replace(".csv", "")
modules/comparison.py:80: leg_2 = leg_2.replace(".csv", "")
modules/comparison.py:81: leg_1 = leg_1.replace(".xlsx", "")
modules/comparison.py:82: leg_2 = leg_2.replace(".xlsx", "")
```

### ume — 15 попаданий в 5 файлах

Файлы: `R/as_peaklist.R`, `R/check_objects.R`, `R/export_ume_results.R`, `R/load_ume_results.R`, `R/tools.R`

Примеры:

```
R/as_peaklist.R:9: #' - file paths (csv, txt, tsv, rds)
R/check_objects.R:143: #' - **CSV** (`.csv`)
R/check_objects.R:193: # ----------- Delimited text files (csv, tsv, txt, etc.) --------------------
R/check_objects.R:194: if (ext %in% c("csv", "tsv", "txt", "dat", "peaklist")) {
R/check_objects.R:212: "Supported extensions: csv, tsv, txt, dat, peaklist, rds"
R/export_ume_results.R:7: #' The function writes the following objects to CSV (if provided):
```

### xcms — 64 попаданий в 8 файлах

Файлы: `R/XcmsExperimentHdf5-functions.R`, `R/XcmsExperimentHdf5.R`, `R/databases.R`, `R/functions-XCMSnExp.R`, `R/functions-xcmsFragments.R`, `R/functions-xcmsSet.R`, `R/methods-xcmsSet.R`, `R/writemztab.R`

Примеры:

```
R/databases.R:13: read.mascot<-function(file, type="csv"){
R/databases.R:17: if(type=="csv"){
R/databases.R:21: myDF <-read.csv(textConnection(x), header=T)
R/databases.R:23: stop("Noncompatable csv file\n")
R/functions-xcmsFragments.R:318: write.csv(distances,file=filename)
R/functions-XCMSnExp.R:1307: write.table(fv, file = file, sep = ",",
```
