# U.S. Thermoelectric Power Plant Water Consumption Benchmarking

A quantile regression benchmark model identifying thermoelectric power plants that overconsume water relative to their peer group, combined with spatial risk mapping of overconsumers against watershed stress across the continental United States.

---

## Overview

This project builds a data pipeline and statistical model to answer one question: **which U.S. thermoelectric power plants are consuming more water than their characteristics would predict, and where does that overconsumption threaten water security?**

We assemble a panel dataset of 2,251 plant-year observations (2021–2024) from six public data sources, train a quantile regression benchmark model at the 75th and 90th percentile of water consumption, and map overconsumers against WRI Aqueduct watershed stress scores. State-level policy implications are drawn from the composite risk scores.

The project also documents — as a methodological contribution — why individual data center water consumption cannot currently be predicted from public data, and what reporting changes would be needed to make that possible.

---

## Repository Structure

```
.
├── data/
│   ├── raw/                        # Source data files (not committed — see Data Sources)
│   │   ├── us_states.geojson       # US state boundaries for mapping
│   │   └── ...
│   ├── processed/
│   │   ├── Preprocessed_Power_Plant_Data.csv    # Master modeling dataset (2,251 rows)
│   │   └── Power_Plant_Benchmarked.csv          # Model output with ceilings and risk scores
│   └── figures/                    # All output figures
│
├── notebooks/
│   ├── 01_eda_feature_selection.ipynb     # EDA, VIF, Kruskal-Wallis, LASSO feature selection
│   ├── 02_quantile_regression.ipynb       # Benchmark model training and validation
│   ├── 03_spatial_risk_map.ipynb          # Choropleth risk map and top plant rankings
│   └── 04_state_policy_analysis.ipynb     # State exposure index and counterfactual analysis
│
├── README.md
└── requirements.txt
```

---

## Quickstart

```bash
# Create and activate a virtual environment
python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\activate
# On macOS/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Register the virtual environment as a Jupyter Kernel
python -m ipykernel install --user --name=thermo_env --display-name "Python (Thermo)"

# Run notebooks
# IMPORTANT: When the notebook opens, make sure the Kernel (top right in VS Code or Jupyter) is set to "Python (Thermo)"
jupyter notebook notebooks/01_eda_feature_selection.ipynb
jupyter notebook notebooks/02_quantile_regression.ipynb
jupyter notebook notebooks/03_spatial_risk_map.ipynb
jupyter notebook notebooks/04_state_policy_analysis.ipynb
```

Notebook 02 reads `Preprocessed_Power_Plant_Data.csv` and outputs `Power_Plant_Benchmarked.csv`. Notebooks 03 and 04 both read from `Power_Plant_Benchmarked.csv`. Run them in order.

---

## Dataset

The master dataset `Preprocessed_Power_Plant_Data.csv` contains **2,251 plant-year rows** across 2021–2024 after cleaning. It was assembled from six sources and joins plant-level operational data with climate observations and watershed stress scores.

| Cooling Category | Count |
|---|---|
| Closed (recirculating tower) | 1,752 |
| Dry-Hybrid (primarily air-cooled) | 278 |
| Open (once-through) | 221 |
| **Total** | **2,251** |

**Key columns:**

| Column | Description |
|---|---|
| `consumption_ML` | Annual net water consumption in megalitres |
| `net_gen_mwh` | Annual net electricity generated (MWh) |
| `capacity_mw` | Nameplate generating capacity (MW) |
| `cooling_category` | Cooling technology: Closed, Open, or Dry-Hybrid |
| `primary_fuel` | Primary fuel type (NUC, NG, BIT, SUB, etc.) |
| `mean_temp_f` | Annual mean air temperature (°F) from NOAA GSOY |
| `bws_raw` | WRI Aqueduct baseline water stress score |
| `state_water_intensity_L_per_MWh` | State grid water intensity (L/MWh) |
| `predicted_ceiling_90` | Model output: 90th percentile benchmark ceiling (ML) |
| `risk_score` | Composite: excess consumption × watershed stress |

**Data cleaning decisions:**
- Removed Columbia Energy Center 2023 (221,311 ML reported vs ~3,000 ML all other years — data error)
- Removed Gary Works (industrial steel plant misclassified as power plant, fuel = PRG)
- Removed 54 rows where `consumption_ML` > `withdrawal_ML` (physically impossible)
- Removed `RH_oa_pct`, `P_oa_pa`, `T_oa_celsius` (zero-variance hardcoded constants)
- Retained zero-consumption Dry-Hybrid rows as legitimate near-zero observations

---

## Methodology

### Notebook 01 — EDA & Feature Selection

- Log1p-transforms `consumption_ML` (raw skewness = 4.79, post-transform ≈ −1.2)
- VIF analysis removes collinear variables: three temperature columns → keep `mean_temp_f`
- Kruskal-Wallis tests confirm all categorical predictors significant (p < 0.001) except `year` (p = 0.31), which is excluded
- LASSO with 5-fold cross-validation identifies surviving features: `net_gen_mwh`, `capacity_mw`, `n_cooling_systems`, `mean_temp_f`, `state_water_intensity_L_per_MWh`, `cooling_category`, `primary_fuel`

### Notebook 02 — Quantile Regression Benchmark

Fits `sklearn.linear_model.QuantileRegressor` at q=0.75 and q=0.90 on log1p(consumption_ML). Features are standardized; `primary_fuel` is one-hot encoded (15 total columns after dummies); `cooling_category` is ordinally encoded as Dry-Hybrid=0, Closed=1, Open=2.

**Model performance:**

| Quantile | Pinball Loss | Overconsumers | Alignment |
|---|---|---|---|
| q=0.75 | 0.3945 | 559 / 2,238 (25.0%) | 24.6% positive ✓ |
| q=0.90 | 0.2047 | 225 / 2,238 (10.1%) | 10.0% positive ✓ |

The predicted ceiling at q=0.90 is the primary benchmark. A plant exceeding its ceiling is in the top 10% of consumers among peers with similar generation volume, cooling technology, fuel type, and climate — and is flagged as an overconsumer.

### Notebook 03 — Spatial Risk Map

Computes a composite risk score per plant:

```
risk_score = excess_ratio × bws_raw
```

Where `excess_ratio` is how far above the q=0.90 ceiling actual consumption is (clipped to 0 for within-ceiling plants), and `bws_raw` is the WRI Aqueduct baseline water stress. The map uses a choropleth state background (YlOrBr scale, mean bws_raw per state) and overlaid plant dots (RdPu scale, risk score) so that high-stress states like California and Nevada are visually distinct from high-volume but lower-stress states like Michigan.

### Notebook 04 — State Policy Analysis

Aggregates plant-level risk scores to a consumption-weighted state exposure index. Includes a counterfactual estimating water savings if Open once-through cooling plants switched to Closed recirculating systems, computed from median intensity ratios (ML/MWh) between cooling categories.

**Top 5 states by consumption-weighted exposure index:**

| State | Exposure Index | Total ML | Overconsumers |
|---|---|---|---|
| NV | 1.559 | 30,004 | 4 |
| VA | 0.580 | 73,594 | 7 |
| MI | 0.519 | 534,792 | 9 |
| IL | 0.519 | 1,174,289 | 9 |
| CA | 0.311 | 138,835 | 3 |

Nevada's consumption-weighted exposure index is 6.9× higher than Texas (0.225) despite having 52× less total consumption — the composite score captures stress-adjusted risk rather than raw volume.

---

## Data Sources

| Source | Used For | URL |
|---|---|---|
| EIA Form 860 | Cooling equipment, plant metadata (2021–2024) | https://www.eia.gov/electricity/data/eia860/ |
| EIA Form 923 | Water consumption, withdrawal, net generation (2021–2024) | https://www.eia.gov/electricity/data/eia923/ |
| EPA eGRID | Capacity (MW), coordinates, emissions (2021–2023) | https://www.epa.gov/egrid |
| NOAA GSOY v1 | Annual mean/max/min temperature per station | https://doi.org/10.7289/JWPF-Y430 |
| WRI Aqueduct 4.0 | Baseline water stress scores (bws_raw) | https://doi.org/10.46830/writn.23.00061 |
| PNNL Building America | ASHRAE climate zones and moisture regimes | https://doi.org/10.2172/1893981 |
| Google 2024 Env. Report | WUE observations for data center comparison | https://www.gstatic.com/gumdrop/sustainability/google-2024-environmental-report.pdf |

---

## Key References

Siddik, M.A.B., Shehabi, A., and Marston, L. (2021). The environmental footprint of data centers in the United States. *Environmental Research Letters,* 16, 064017. https://doi.org/10.1088/1748-9326/abfba1

Lei, N. and Masanet, E. (2022). Climate- and technology-specific PUE and WUE estimations for U.S. data centers using a hybrid statistical and thermodynamics-based approach. *Resources, Conservation and Recycling,* 182, 106323. https://doi.org/10.1016/j.resconrec.2022.106323

Lei, N., Lu, J., Shehabi, A., and Masanet, E. (2025). The water use of data center workloads: A review and assessment of key determinants. *Resources, Conservation and Recycling,* 219, 108310. https://doi.org/10.1016/j.resconrec.2025.108310

Kuzma, S. et al. (2023). Aqueduct 4.0: Updated decision-relevant global water risk indicators. World Resources Institute. https://doi.org/10.46830/writn.23.00061

---

## Requirements

```
pandas
numpy
matplotlib
seaborn
scikit-learn
scipy
pathlib
json
```

Install with `pip install -r requirements.txt`.

Python 3.9+ recommended.

---

## Notes

- eGRID does not yet cover 2024; eGRID 2023 values are carried forward for 2024 plant rows.
- Dry-Hybrid plants have a median consumption of 0.000 ML (zero-consumption rows are legitimate for air-cooled systems). The 7.6% overconsumer rate for this category is driven by the small number of non-zero Dry-Hybrid plants such as Scattergood (CA) and Bridgeport Station (CT).
- The data center application of this benchmark framework is currently blocked by a public reporting gap: facility-level IT load (net_gen_mwh equivalent) is not disclosed by any major operator. This is documented in the project report as a finding and policy recommendation.

---

*STAT 420 Final Project — 2026*