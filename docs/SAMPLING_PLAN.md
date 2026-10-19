# GCC Consumer Research Kit: Sampling Plan & Statistical Framework

## 1. Target Universe & Eligibility Criteria

### 1.1 Universe Definition
The target universe comprises adult consumers residing in urban centers of the Kingdom of Saudi Arabia (KSA), United Arab Emirates (UAE), and State of Kuwait.
- **Age Scope:** 18–54 years old.
- **Category Incidence:** Monthly or more frequent users of hair oils, leave-in scalp treatment serums, or hair care therapies.
- **Purchase Decision Role:** Primary or joint decision-maker for personal grooming / beauty purchases.
- **Urban Concentration:**
  - KSA: Riyadh, Jeddah/Makkah, Dammam/Khobar (Eastern Province).
  - UAE: Dubai, Abu Dhabi, Sharjah.
  - Kuwait: Kuwait City and Hawalli governorates.

### 1.2 Representativeness & Quota Controls
The sampling strategy employs **disproportionate stratified quota sampling** to ensure robust analytical bases for individual country cut-offs while maintaining representative internal demographic balances (gender, age, nationality) within each market. Post-survey **rim weighting (iterative proportional fitting)** is applied to bring aggregate metrics back to true adult population parameters.

---

## 2. Sample Size Determination & Margin of Error

### 2.1 Theoretical Formula
Under simple random sampling (SRS), the required sample size $n$ for estimating a population proportion $p$ with a margin of error $e$ at confidence level $1 - \alpha$ is given by:

$$n = \frac{Z_{1 - \alpha/2}^2 \cdot p(1 - p)}{e^2}$$

Where:
- $Z_{1 - \alpha/2}$ is the standard normal critical value (1.96 for 95% confidence level; 1.645 for 90%; 2.576 for 99%).
- $p$ is the assumed baseline proportion. To maintain a conservative (maximum variance) design, we set $p = 0.50$, where $p(1 - p) = 0.25$.
- $e$ is the acceptable margin of error (half-width of the confidence interval).

Conversely, the margin of error (MoE) for a realized sample size $n$ at a $95\%$ confidence level is:

$$\text{MoE}_{95\%} = \pm 1.96 \times \sqrt{\frac{0.25}{n}} = \pm \frac{0.98}{\sqrt{n}}$$

### 2.2 Finite Population Correction (FPC) Consideration
Given that the adult target population in the GCC urban centers exceeds 15 million individuals, the sampling fraction $\frac{n}{N} \ll 0.05$. Therefore, the finite population correction factor $\sqrt{\frac{N - n}{N - 1}} \approx 1.000$, and infinite population formulas are applied without distortion.

### 2.3 Sample Stratification & Margins of Error

| Stratum (Market) | Target Sample ($n$) | Share of Total | MoE @ 90% CI ($Z=1.645$) | MoE @ 95% CI ($Z=1.96$) | MoE @ 99% CI ($Z=2.576$) | Primary Subgroup Feasibility |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **KSA** | **600** | 50.0% | $\pm 3.36\%$ | **$\pm 4.00\%$** | $\pm 5.26\%$ | Reliable cuts by Gender, Age, Nat |
| **UAE** | **420** | 35.0% | $\pm 4.01\%$ | **$\pm 4.78\%$** | $\pm 6.29\%$ | Reliable cuts by Gender & Nat |
| **Kuwait** | **180** | 15.0% | $\pm 6.13\%$ | **$\pm 7.30\%$** | $\pm 9.60\%$ | Broad cuts only; flag small cells |
| **Total Study** | **1,200** | **100.0%** | $\pm 2.37\%$ | **$\pm 2.83\%$** | $\pm 3.72\%$ | High precision across all cuts |

### 2.4 Monadic Concept Test Split
For the randomized monadic concept evaluation (50/50 split):
- **Concept A (Bio-Clinical):** $n = 600 \implies \text{MoE}_{95\%} = \pm 4.00\%$
- **Concept B (Royal Heritage):** $n = 600 \implies \text{MoE}_{95\%} = \pm 4.00\%$
- **Statistical Power:** With $n=600$ per arm, the two-tailed z-test for comparing Top-2-Box purchase intent proportions has $> 85\%$ statistical power ($\beta < 0.15$) to detect a true difference of $\Delta \ge 8.0$ percentage points at $\alpha = 0.05$.

---

## 3. Minimum Base-Size Discipline & Reporting Conventions

Market research decision-makers frequently fall into the trap of over-interpreting percentages derived from micro-samples (e.g., claiming "66% of Kuwaiti male expats aged 18-24 prefer Brand X" when $n=3$). This kit enforces a formal three-tier base-size governance rule across all crosstabs and reports.

```
       Base Size (n)                    Reporting Action
+--------------------------+  --->  [ Standard Reporting & Testing ]
|       n >= 50            |        Unrestricted z-test & t-test column letters
+--------------------------+
+--------------------------+  --->  [ Cautionary Reporting: Flagged with * ]
|     30 <= n < 50         |        Significance letters displayed with warning;
+--------------------------+        indicative directional trends only
+--------------------------+  --->  [ Suppressed / Severe Warning: Flagged with ** ]
|       n < 30             |        Statistical significance tests suppressed;
+--------------------------+        percentages enclosed in parentheses (XX%) or masked
```

### Detailed Rules:
1. **Unrestricted / Robust Base ($n \ge 50$):**
   - Full reporting of percentages, means, standard deviations.
   - Column letters (A, B, C...) displayed for two-tailed tests at $p < 0.05$.
2. **Low Base / Directional Only ($30 \le n < 49$):**
   - Percentage figures are displayed with a single asterisk (`*`).
   - Crosstab footers must explicitly state: `* Caution: Low base size (n = 30-49). Interpret differences as directional indicators rather than conclusive evidence.`
3. **Very Low / Unreliable Base ($n < 30$):**
   - In automated tables, proportions must either be enclosed in parentheses `( % )` or suppressed completely.
   - Statistical hypothesis testing (z-tests and t-tests) is **strictly disabled** for columns with $n < 30$, as standard normal asymptotic approximations breakdown and small-cell volatility produces extreme false discovery rates.
   - Flagged with double asterisks (`**`).

---

## 4. Weighting Methodology: Rim Weighting (Raking)

Because Kuwait is intentionally over-sampled relative to its natural population share in the GCC (15% in sample vs ~7% of GCC urban adult population), and UAE is sampled at 35%, post-stratification survey weighting is required.

### 4.1 Weighting Variables & Population Targets
1. **Market Distribution Target:**
   - KSA: 62.0%
   - UAE: 28.0%
   - Kuwait: 10.0%
2. **Gender Distribution Target:**
   - Female: 60.0%
   - Male: 40.0%
3. **Nationality Distribution Target:**
   - Nationals (Saudi / Emirati / Kuwaiti): 48.0%
   - Expats (Arab, Asian, Western): 52.0%

### 4.2 Algorithm: Iterative Proportional Fitting (IPF)
Weights $w_i$ are calculated iteratively until marginal weighted sample totals converge within $0.001$ of the benchmark population marginal distributions:

$$w_{i}^{(t+1)} = w_i^{(t)} \times \frac{T_k}{\sum_{j \in k} w_j^{(t)}}$$

Where $T_k$ is the target population total for category $k$.

### 4.3 Weight Trimming & Efficiency Controls
To prevent extreme individual respondent leverage:
- **Minimum Weight Bound:** $w_{min} = 0.35$
- **Maximum Weight Bound:** $w_{max} = 2.85$
- Weights exceeding these boundaries are trimmed and redistributed across remaining cases.

### 4.4 Design Effect (DEFF) & Effective Sample Size
Weighting reduces statistical efficiency because unequal weights inflate the variance of estimators. The **Design Effect (Kish's approximation)** is defined as:

$$\text{DEFF} = 1 + \text{CV}(w)^2 = \frac{n \sum_{i=1}^n w_i^2}{\left(\sum_{i=1}^n w_i\right)^2}$$

The **Effective Sample Size ($n_{eff}$)** represents the equivalent sample size under simple random sampling:

$$n_{eff} = \frac{n}{\text{DEFF}}$$

*Target Quality Metric:* $\text{DEFF} \le 1.25$, ensuring that an $n=1,200$ sample delivers an effective base $n_{eff} \ge 960$ ($> 80\%$ efficiency).

---

## 5. Statistical Significance Testing & Multiple-Comparison Risk

### 5.1 Pairwise Column Comparisons (Proportions)
To test whether the proportion in Column $A$ ($p_A$) differs significantly from Column $B$ ($p_B$), a pooled two-proportion z-test is conducted:

$$z = \frac{p_A - p_B}{\sqrt{p_p (1 - p_p) \left(\frac{1}{n_A} + \frac{1}{n_B}\right)}}$$

Where $p_p = \frac{n_A p_A + n_B p_B}{n_A + n_B}$.
If $|z| \ge 1.96$, the higher column is tagged with the corresponding capital letter at the $95\%$ confidence level ($p < 0.05$).

### 5.2 Pairwise Column Comparisons (Means)
For continuous rating scales (e.g., 5-point agreement, purchase intent mean), Welch's two-sample t-test (accounting for unequal variances) is computed:

$$t = \frac{\bar{x}_A - \bar{x}_B}{\sqrt{\frac{s_A^2}{n_A} + \frac{s_B^2}{n_B}}}$$

Degrees of freedom are computed via the Welch–Satterthwaite equation.

### 5.3 Multiple-Comparison Risk & Mitigation Strategy
In a standard commercial survey crosstab banner with 15 columns and 80 survey questions, an analyst runs over 1,200 individual significance tests. At a nominal significance level of $\alpha = 0.05$:

$$\text{Expected False Discoveries} = 1,200 \times 0.05 = 60 \text{ spurious "significant" differences!}$$

#### Governance Protocol:
1. **Family-Wise Error Rate (FWER) Caution:** The classic **Bonferroni correction** ($\alpha_{adj} = \frac{\alpha}{m}$) is overly conservative for survey exploratory research, resulting in severe Type II error (masking real market shifts).
2. **Benjamini-Hochberg (BH) False Discovery Rate (FDR):** For academic or confirmatory claims, rank $p$-values $p_{(1)} \le p_{(2)} \le \dots \le p_{(m)}$ and identify the largest $k$ such that:
   $$p_{(k)} \le \frac{k}{m} \cdot Q$$
   Where $Q = 0.10$ (10% false discovery threshold).
3. **Standard Commercial Practice in this Kit:**
   - Primary crosstabs report unadjusted $p < 0.05$ column letters for routine category exploration, flagged prominently with a methodology footnote:
     > *"Significance letters denote independent pairwise z/t-tests at $\alpha=0.05$. Because multiple comparisons are not omnibus-corrected, isolated differences should be validated against overall pattern coherence before making capital-allocation decisions."*
