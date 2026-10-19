# gcc-consumer-research-kit

An enterprise-grade, end-to-end consumer research toolkit demonstrating quantitative and qualitative research craft across the Gulf Cooperation Council (Kingdom of Saudi Arabia, United Arab Emirates, State of Kuwait).

---

## Overview

This repository provides a complete, reproducible reference implementation for commercial consumer research in the GCC. Built around an empirical category study on hair care rituals, scalp therapy, and premiumization, the kit spans the full research lifecycle: questionnaire routing logic, stratified sampling, automated quality control cleaning, iterative proportional fitting (rim weighting), pairwise significance testing with base-size governance, Van Westendorp price elasticity modeling, monadic concept testing, AI-assisted open-ended coding with human benchmark validation, and executive presentation artifacts.

---

## Core Capabilities

- **Questionnaire & Survey Specification:** 
  Multi-market screening, quota controls (market, age, gender, nationality), U&A battery, brand funnel hierarchy, 4-point Van Westendorp pricing, and a 50/50 randomized monadic concept test with full routing rules.
- **Automated Data Quality Control (QC):** 
  Modular cleaning engine flagging speeders (LOI under one-third median duration), straight-liners (zero variance across 6-item grids), duplicate fingerprints, and pricing logic inversions. Generates an itemized audit log with failure rationales.
- **Survey Weighting & Design Effect:** 
  Iterative Proportional Fitting (raking) calibrating sample marginals to national census benchmarks, with automated calculation of Kish's Design Effect (DEFF) and Effective Base Size (N_eff).
- **Statistical Significance & Base-Size Governance:** 
  Independent two-proportion z-tests and Welch's two-sample t-tests with column letter notation. Enforces a strict three-tier base-size reporting standard (n >= 50 unrestricted, 30 <= n < 50 flagged as directional, n < 30 strictly suppressed).
- **Pricing & Concept Analysis:** 
  Van Westendorp Price Sensitivity Meter computing Point of Marginal Cheapness (PMC), Optimal Price Point (OPP), Indifference Price Point (IPP), and Point of Marginal Expensiveness (PME). Monadic concept scorecard reporting Top-2-Box, Top-Box, and diagnostic profiles.
- **AI Open-End Coding with Human Benchmark Validation:** 
  Evaluation of three progressive LLM prompting strategies against a 150-response senior human researcher benchmark dataset, tracking Accuracy, Cohen's Kappa, Macro Precision, Recall, F1, and an adjudication discrepancy log.
- **Executive Communication:** 
  10-slide presentation deck with action headlines, strategic recommendations, and a dedicated "What We Do Not Know" slide outlining empirical field hypotheses to test. Includes a standalone interactive HTML slide deck.

---

## Methodological Summary

### 1. Research Universe & Quotas

- **Target Audience:** Adults aged 18 to 54 residing in urban centers of KSA (Riyadh, Jeddah, Eastern Province), UAE (Dubai, Abu Dhabi, Sharjah), and Kuwait (Kuwait City, Hawalli) using hair/scalp treatments at least once per month.
- **Geographic Quotas:** KSA (50.0%), UAE (35.0%), Kuwait (15.0%).
- **Demographic Quotas:** 65% Female / 35% Male; balanced age distribution (18-24, 25-34, 35-44, 45-54); National Citizens vs Expatriate residents.
- **Sample Precision:**
  - Total Study: N = 1,200 (Margin of Error = +/- 2.83% at 95% Confidence Level).
  - KSA Subsample: n = 600 (Margin of Error = +/- 4.00%).
  - UAE Subsample: n = 420 (Margin of Error = +/- 4.78%).
  - Kuwait Subsample: n = 180 (Margin of Error = +/- 7.30%).

### 2. Quality Control & Attrition Standards

| QC Failure Rule | Detection Threshold | Action Taken |
| :--- | :--- | :--- |
| Speeding | Total LOI < 240 seconds (Median = 711.5s) | Record eliminated from analytical sample |
| Straight-lining | StdDev = 0.00 across 6-item Q2 Likert battery | Record eliminated from analytical sample |
| Duplicate Submissions | Matching IP address, demographics, and verbatim | Primary record kept; repeat submission dropped |
| Pricing Logic Inversions | Price Too Cheap >= Price Too Expensive, or Non-monotonic | Record eliminated from analytical sample |
| Brand Funnel Contradictions | BUMO brand not present in Ever Used or Past 3M | Record eliminated from analytical sample |

### 3. Minimum Base-Size Discipline

```
Base Size (n)       Reporting Convention
-----------------------------------------------------------------------------------------
n >= 50             Standard reporting. Full pairwise z-tests and t-tests displayed.
30 <= n < 49        Cautionary reporting. Single asterisk (*) appended. Directional only.
n < 30              Statistical suppression. Double asterisk (**) appended. Percentages
                    enclosed in parentheses (XX%). Hypothesis tests disabled.
```

### 4. Survey Weighting Diagnostics

- **Method:** Iterative Proportional Fitting (Rim Weighting / Raking).
- **Target Dimensions:** Market (KSA 62%, UAE 28%, Kuwait 10%), Gender (Female 60%, Male 40%), Nationality Group (National 48%, Expat 52%).
- **Design Effect (DEFF):** 1.124
- **Effective Sample Size (N_eff):** 1,077.4 (89.0% statistical efficiency).
- **Weight Bounds:** Trimmed between 0.35 and 2.85; normalized to mean = 1.000.

---

## Key Findings

### 1. Environmental & Cultural Stressors

- **Desalinated Hard Water:** 84.2% of UAE and 81.3% of Kuwaiti consumers agree that tap water mineral buildup causes brittle hair and scalp buildup.
- **Hijab Scalp Microclimate:** 81.5% of female Saudi respondents report heat and sweat trapping under their sheyla during working hours, driving demand for breathable, non-greasy scalp tonics.
- **The Washout Penalty:** 51.4% of consumers cite difficulty washing out traditional oils in one rinse as their primary reason for abandoning legacy heavy oils.

### 2. Monadic Concept Test Scorecard

| Performance Metric | Concept A: Bio-Clinical | Concept B: Royal Heritage | Significance (p-value) |
| :--- | :---: | :---: | :---: |
| Top-2-Box Purchase Intent (%) | 62.1% | 57.9% | p = 0.1389 (Directional) |
| Top-Box (Definitely Would Buy) | 27.9% | 25.6% | p = 0.3654 (Parity) |
| Mean Purchase Intent (1 to 5) | 3.74 | 3.64 | p = 0.0977 (Directional) |
| Diagnostic: Uniqueness (1 to 5) | 4.12 | 3.81 | p < 0.001 (Concept A Win) |
| Diagnostic: Relevance (1 to 5) | 4.05 | 3.88 | p = 0.012 (Concept A Win) |
| Diagnostic: Believability (1 to 5) | 3.68 | 3.94 | p < 0.001 (Concept B Win) |
| Diagnostic: Value for Money | 3.54 | 3.48 | p = 0.384 (Parity) |

### 3. Van Westendorp Price Sensitivity (SAR/AED, N = 1,029)

- **Point of Marginal Cheapness (PMC):** 75.0 SAR/AED (threshold below which product quality is questioned).
- **Optimal Price Point (OPP):** 85.0 SAR/AED (intersection of Too Cheap and Too Expensive).
- **Indifference Price Point (IPP):** 105.0 SAR/AED (equal proportion view product as bargain vs expensive).
- **Point of Marginal Expensiveness (PME):** 120.0 SAR/AED (upper ceiling before steep adoption loss).
- **Commercial Corridor:** 75 to 120 SAR/AED. Recommended core 100ml SKU launch target: 95 to 110 SAR/AED (approx 8.5 to 9.5 KWD).

### 4. AI Open-End Coding Benchmark Evaluation

Evaluated against 148 human-coded gold standard verbatims across a 7-category master code frame:

| Metric | Prompt v1 (Zero-Shot) | Prompt v2 (Few-Shot) | Prompt v3 (CoT + GCC Rules) | Target Standard |
| :--- | :---: | :---: | :---: | :---: |
| Overall Accuracy | 83.8% | 94.6% | 100.0% | >= 90.0% |
| Cohen's Kappa (k) | 0.8107 | 0.9369 | 1.0000 | >= 0.8500 |
| Macro Precision | 87.5% | 95.1% | 100.0% | >= 88.0% |
| Macro Recall | 83.7% | 94.6% | 100.0% | >= 88.0% |
| Macro F1-Score | 83.9% | 94.7% | 100.0% | >= 88.0% |

*Key finding:* General zero-shot LLM prompts fail on regional vernacular and cultural context (e.g. confusing scalp acne/folliculitis under a hijab with standard product greasiness). Encoding regional domain rules into the prompt eliminates classification error.

---

## Repository Structure

```
gcc-consumer-research-kit/
|
|-- docs/
|   |-- QUESTIONNAIRE.md             Master questionnaire, routing logic, and programming specs
|   |-- SAMPLING_PLAN.md             Sampling formulas, margins of error, quotas, and weighting math
|   |-- QUAL_DISCUSSION_GUIDE.md     FGD (90m) and IDI (60m) discussion guides with projective tools
|   |-- SYNTHETIC_QUAL_EXCERPTS.md   Compendium of 30 simulated qualitative excerpts
|   `-- EXECUTIVE_PRESENTATION_DECK.md 10-slide executive presentation deck with action headlines
|
|-- data/
|   |-- raw_survey_data.csv          Raw survey dataset (N = 1,350: 1,200 valid + 150 planted defects)
|   |-- cleaned_survey_data.csv      Clean post-QC dataset (N = 1,211 valid completes with weights)
|   |-- human_benchmark_coding.csv   148 human-coded open-end responses (ground truth reference)
|   `-- synthetic_qual_excerpts.json Structured JSON of 30 simulated qualitative excerpts
|
|-- src/
|   |-- generate_synthetic_data.py   Deterministic synthetic survey and qual data generator
|   |-- qc_cleaning.py               Automated quality control engine producing audit logs
|   |-- weighting_and_crosstabs.py   Rim weighting, significance testing, and pricing engine
|   |-- export_excel_report.py       OpenPyXL generator building formatted multi-tab Excel reports
|   `-- ai_open_end_coding.py        LLM open-end classification evaluation and agreement pipeline
|
|-- outputs/
|   |-- GCC_Hair_Care_Crosstabs_and_Analysis.xlsx Multi-tab formatted corporate Excel workbook
|   |-- qc_removal_log.csv           Detailed removal log of 179 defect events across 139 records
|   |-- open_end_validation_report.md Formal LLM agreement validation report and error analysis
|   `-- presentation_deck.html       Interactive standalone HTML presentation deck
|
|-- tests/
|   `-- test_research_kit.py         Automated unit tests (QC rules, base sizes, stats, pricing)
|
`-- README.md                        Master project documentation
```

---

## Quickstart & Reproduction

### Prerequisites

- Python 3.9+
- Python packages: `pandas`, `numpy`, `scipy`, `openpyxl`

### Step-by-Step Execution

1. **Run Unit Tests:**
   ```bash
   python3 tests/test_research_kit.py
   ```

2. **Regenerate Synthetic Data & Qualitative Excerpts:**
   ```bash
   python3 src/generate_synthetic_data.py
   ```

3. **Execute Automated Quality Control Cleaning:**
   ```bash
   python3 src/qc_cleaning.py
   ```
   Generates `outputs/qc_removal_log.csv` and `data/cleaned_survey_data.csv`.

4. **Calculate Survey Weights, Crosstabs, and Excel Report:**
   ```bash
   python3 src/weighting_and_crosstabs.py
   python3 src/export_excel_report.py
   ```
   Generates `outputs/GCC_Hair_Care_Crosstabs_and_Analysis.xlsx`.

5. **Run AI Open-End Coding Benchmark:**
   ```bash
   python3 src/ai_open_end_coding.py
   ```
   Generates `outputs/open_end_validation_report.md`.

6. **View Interactive Presentation:**
   Open `outputs/presentation_deck.html` in any browser. Navigate between slides using the on-screen buttons or arrow keys.

---

## Methodological Governance & Disclosures

### Simulation Disclosure
All survey responses, respondent profiles, pricing curves, diagnostic scores, and qualitative quotations in this repository are simulated research artifacts. They are designed exclusively to demonstrate quantitative and qualitative market research methodology, statistical discipline, data cleaning, and validation craft.

### External Citations for Real Consumer Context
All macro context claims regarding GCC consumer behavior, demographic shifts, and environmental realities cite public industry authorities:
- **Euromonitor International:** Beauty and Personal Care in the Middle East and Africa (2023/2024 reports on premium haircare growth).
- **McKinsey & Company:** Middle East Consumer Sentiment Survey (2023 reports on digital beauty and grooming spending).
- **General Authority for Statistics (GASTAT), Saudi Arabia:** Labor Force Survey Q4 2023 (female workforce participation rates surpassing 35%).
- **International Journal of Trichology (2018) / Journal of Cosmetic Dermatology (2021):** Clinical studies on thermal desalination water hardness, mineral crust accumulation, and scalp microclimates under headwear.
