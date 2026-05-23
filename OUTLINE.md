**Abstract**

The abstract needs four things. Rationale/hypothesis: data center water consumption is growing rapidly alongside AI workloads, no individual-facility benchmark model exists in the literature, and the field lacks a tool for identifying which facilities overconsume relative to their peer group. Study design/methods: you assembled a six-source panel dataset of 2,251 U.S. thermoelectric plant-year observations, applied LASSO feature selection, and trained a quantile regression at the 75th and 90th percentile of log-transformed water consumption. Results with data: 225 plants flagged as overconsumers at q=0.90, California leads with a mean risk score of 0.459 despite 5.8 times less consumption than Texas, and the risk score meaningfully reorders state rankings compared to raw volume alone. Conclusion/implication: the benchmark framework is ready for thermoelectric plants; its application to data centers is currently blocked by a facility-level reporting gap that represents a clear policy intervention point.

---

**Introduction**

The five required elements and where your project covers each:

General background: data center water consumption is growing rapidly with AI workloads, it is less studied than energy use, and it has meaningful local watershed impacts. Your research journey document and the Siddik et al. and Lei & Masanet citations establish this.

The specific dilemma: no individual-facility predictive or benchmark model exists for data center water consumption. The field has relied on national accounting with assumed WUE values rather than facility-level regression.

Why unresolved: this is your strongest original contribution to the introduction. You document through four failed modeling paths exactly why the prediction is not feasible with current public data — generation volume dominates any regression on the EIA backbone, and corporate sustainability reports are portfolio-level rather than facility-level. The 2025 Lei et al. review paper explicitly confirms this gap exists at the frontier of the literature.

Your idea to resolve it: since direct data center prediction is blocked, you redirect the methodology to its most powerful available application — a quantile regression benchmark for thermoelectric plants that can identify peer-group overconsumers in water-stressed watersheds. You frame this as the obvious approach because the EIA data is exactly the right structure for a benchmark model.

Hypothesis or aim: your stated aim is to identify which U.S. thermoelectric plants consume more water than their peer group characteristics predict, and to map those overconsumers against watershed stress to produce a state-level policy relevance ranking.

---

**Methods**

Design: cross-sectional panel, four years (2021–2024), 2,251 plant-year observations, observational study using public administrative data.

Subjects: all U.S. thermoelectric power plants reporting to EIA-860 and EIA-923 with non-zero water consumption. Exclusion criteria explicitly documented — Columbia Energy Center 2023 (data error), Gary Works (misclassified industrial facility), 54 consumption-exceeds-withdrawal rows (physically impossible), zero-variance constant columns. Cooling category breakdown given in the dataset table.

Measurements: consumption in megalitres (converted from EIA million gallons at ×3.785), water stress in bws_raw from WRI Aqueduct, temperature in degrees Fahrenheit from NOAA GSOY, state water intensity in L/MWh from EIA-923. All units documented in the data sources section.

Analysis: log1p transformation of target (skewness 4.79 → −1.2), VIF analysis removing collinear features, Kruskal-Wallis tests on all categoricals, LASSO with 5-fold cross-validation for feature selection, QuantileRegressor at q=0.75 and q=0.90 with StandardScaler normalization, one-hot encoding for primary_fuel, ordinal encoding for cooling_category based on empirical water-use ladder.

Statistical power: quantile alignment validation — 24.6% positive residuals at q=0.75 (expect 25%) and 10.0% at q=0.90 (expect 10%). Pinball loss reported. This is your model validity check and belongs in methods.

---

**Results**

Baseline data: the cooling category breakdown table (Closed 1,752, Dry-Hybrid 278, Open 221) serves as your Table 1 equivalent. Add state and fuel distribution summaries here.

Main results: the four figures from Notebook 02 — coefficient chart, actual vs ceiling scatter, residual diagnostics, overconsumer breakdown by cooling category. The 225 q=0.90 overconsumers is your headline finding. The state risk table (CA 0.459, NV 0.285, TN 0.185, TX 0.128, NM 0.087) is your main results table. The choropleth risk map from Notebook 03 is your primary figure.

Secondary results: state-level exposure index rankings from Notebook 04. The counterfactual — estimated water savings from Open-to-Closed switching — is a secondary finding.

Unexpected observations: Dry-Hybrid median consumption of 0.000 ML (zero-consumption rows legitimate for air-cooled systems). Tennessee appearing third in risk score despite not being associated with water scarcity in public perception — driven by TVA nuclear facilities. These belong here as brief factual notes without interpretation.

---

**Discussion**

Bottom line: a consumption-weighted composite risk score combining peer-group benchmark exceedance with watershed stress produces meaningfully different state rankings than raw consumption volume alone. California ranks first by risk despite sixth in total consumption. This is the core message.

Comparison with earlier work: Siddik et al. (2021) mapped water footprints spatially but used assumed WUE values rather than peer-group benchmarking. Your model adds the normative benchmark layer — not just where consumption is high, but where it is high relative to what it should be given plant characteristics. Lei & Masanet (2022) showed simulation-based WUE ranges but did not connect those to overconsumption flagging or watershed risk scoring. Your framework is the first to combine all three: peer benchmarking, spatial risk, and state policy implications from the same dataset.

Weakness/strength: be honest here. Dry-Hybrid thin training data (278 rows, most zero-consumption), eGRID does not cover 2024 so 2024 rows carry forward 2023 values, `year` was not a significant predictor suggesting limited temporal inference, the counterfactual assumes median intensity ratios hold across heterogeneous plants. Strengths: largest publicly assembled thermoelectric panel dataset with this covariate coverage, quantile alignment near-perfect (10.0% vs expected 10%), methodology is fully reproducible from public data.

Interpretation and mechanisms: the dominance of `net_gen_mwh` in the model (log-log coefficient ~0.97) is not a weakness but a physical reality — heat rejection scales with generation. The benchmark model accounts for this correctly by conditioning all peer comparisons on generation volume, capacity, cooling technology, and fuel type. Plants above the 90th percentile ceiling are overconsumers after controlling for legitimate size differences.

Practical/policy relevance: the five highest-risk states by exposure index are natural targets for water efficiency regulation of thermoelectric cooling. The Open-to-Closed cooling counterfactual provides a concrete, quantified policy lever. The data center gap finding — that facility-level IT load reporting would unlock the same framework for hyperscale operators — is a direct policy recommendation with a clear implementation path.

Conclusion: the benchmark framework is functional and produces actionable state-level rankings. The data center application requires mandatory facility-level WUE reporting, which is the single most important policy recommendation from the project.


Meta data comparision with the power plant data

The numbers are clean and the story they tell is strong. Here is what the data shows and how to use it in the introduction paragraph.

**The key findings from this calculation:**

Meta's 13 U.S. data center facilities collectively consumed 6.46 million MWh of grid electricity in 2021 and 8.35 million MWh in 2022 — 100% from the grid per their report. Applying your `state_water_intensity_L_per_MWh` values from the EIA backbone, that electricity required approximately **4,501 ML of water in 2021 and 5,837 ML in 2022** to generate — water consumed by the thermoelectric plants in your dataset, not by Meta directly.

**The grid intensity contrast is the most compelling finding for the introduction:**

Prineville, Oregon consumes nearly as much electricity as Fort Worth, Texas (982k vs 959k MWh in 2022), but its indirect water cost is less than one third — 215 ML versus 716 ML. Oregon's grid runs heavily on hydropower (218.6 L/MWh) while Texas relies heavily on thermoelectric generation (745.8 L/MWh). Two data centers with similar electricity appetite have radically different embedded water footprints depending purely on where they connect to the grid. That is the argument for why your thermoelectric benchmark model is directly relevant to data center water accountability.

Newton County, Georgia is the single highest indirect water consumer in 2022 at 1,147 ML — driven by Georgia's grid water intensity of 1,802.5 L/MWh, the highest in this set, reflecting heavy reliance on coal and nuclear generation in the Southeast.

**How the introduction paragraph writes itself:**

Meta's 13 U.S. facilities consumed 8.35 million MWh of grid electricity in 2022. At the state-level water intensities of the grids supplying those facilities — ranging from 218.6 L/MWh in Oregon to 1,802.5 L/MWh in Georgia — that electricity embedded approximately 5,837 ML of water consumed by thermoelectric power plants to produce it. That volume, invisible to any direct facility-level water audit, is the indirect water footprint your thermoelectric benchmark model is designed to identify and flag. Even where direct facility-level WUE reporting is unavailable, the indirect water cost of data center electricity is calculable from operator-reported consumption matched to grid water intensity — and it varies by a factor of eight across otherwise comparable facilities depending solely on grid composition.