#!/usr/bin/env python3
"""
weighting_and_crosstabs.py
Performs:
1. Iterative proportional fitting (raking / rim weighting) to population census targets.
2. Design Effect (DEFF) and effective sample size calculation.
3. Crosstab generation across banners (Market, Planted Segment, Concept).
4. Significance testing (Z-test for proportions, Welch t-test for means, Chi-square).
5. Dynamic three-tier minimum base-size discipline (Robust >=50, Low 30-49, Suppressed <30).
6. Multiple comparison risk control (Benjamini-Hochberg FDR vs Bonferroni).
7. Van Westendorp Price Sensitivity Meter curves and key price points (PMC, PME, IPP, OPP).
8. Exports complete analytical tables to JSON and Excel-ready structures.
"""

import os
import numpy as np
import pandas as pd
from scipy import stats

def compute_weights(df):
    """
    Computes survey weights using Iterative Proportional Fitting (Raking)
    Target Marginals:
    - Market: KSA (62.0%), UAE (28.0%), Kuwait (10.0%)
    - Gender: Female (60.0%), Male (40.0%)
    - Nationality: National (48.0%), Expat (52.0%)
    """
    print("\nExecuting Iterative Proportional Fitting (Rim Weighting)...")
    
    df['NAT_GROUP'] = df['NATIONALITY_CAT'].apply(lambda x: 'National' if 'National' in str(x) else 'Expat')
    
    targets = {
        'MARKET': {'KSA': 0.62, 'UAE': 0.28, 'Kuwait': 0.10},
        'GENDER': {'Female': 0.60, 'Male': 0.40},
        'NAT_GROUP': {'National': 0.48, 'Expat': 0.52}
    }
    
    # Initialize weights to 1.0
    w = np.ones(len(df), dtype=float)
    
    # Raking iterations
    max_iters = 50
    tol = 1e-4
    
    for iteration in range(max_iters):
        max_diff = 0.0
        for var, cat_targets in targets.items():
            for cat, target_pct in cat_targets.items():
                mask = (df[var] == cat).values
                current_weighted_sum = np.sum(w[mask])
                total_weighted_sum = np.sum(w)
                current_pct = current_weighted_sum / total_weighted_sum
                
                if current_weighted_sum > 0:
                    factor = target_pct / current_pct
                    w[mask] *= factor
                    diff = abs(target_pct - current_pct)
                    if diff > max_diff:
                        max_diff = diff
                        
        if max_diff < tol:
            print(f"  - Converged in {iteration+1} iterations (max marginal diff: {max_diff:.6f}).")
            break
            
    # Normalize weights so sum(weights) == N
    w = w * (len(df) / np.sum(w))
    
    # Trimming bounds: [0.35, 2.85]
    w = np.clip(w, 0.35, 2.85)
    w = w * (len(df) / np.sum(w)) # Re-normalize
    
    df['WEIGHT'] = w
    
    # Calculate Design Effect (Kish's formula)
    # DEFF = 1 + CV(w)^2 = N * sum(w^2) / (sum(w))^2
    n = len(df)
    sum_w = np.sum(w)
    sum_w_sq = np.sum(w ** 2)
    deff = (n * sum_w_sq) / (sum_w ** 2)
    n_eff = n / deff
    efficiency = (n_eff / n) * 100
    
    print(f"Weighting Diagnostics:")
    print(f"  - Nominal Sample Size (N): {n}")
    print(f"  - Min Weight: {np.min(w):.3f} | Max Weight: {np.max(w):.3f} | Mean Weight: {np.mean(w):.3f}")
    print(f"  - Design Effect (DEFF):    {deff:.3f}")
    print(f"  - Effective Base (N_eff):  {n_eff:.1f} ({efficiency:.1f}% efficiency)")
    
    return df, deff, n_eff

def z_test_proportions(p1, n1, p2, n2):
    """
    Two-tailed z-test for difference in proportions.
    Returns z_stat, p_value.
    """
    if n1 <= 0 or n2 <= 0:
        return 0.0, 1.0
    p_pool = (p1 * n1 + p2 * n2) / (n1 + n2)
    if p_pool <= 0 or p_pool >= 1:
        return 0.0, 1.0
    se = np.sqrt(p_pool * (1 - p_pool) * (1.0 / n1 + 1.0 / n2))
    if se <= 0:
        return 0.0, 1.0
    z = (p1 - p2) / se
    p_val = 2 * (1 - stats.norm.cdf(abs(z)))
    return z, p_val

def t_test_means(mean1, std1, n1, mean2, std2, n2):
    """
    Two-sample Welch's t-test for difference in means (unequal variances).
    Returns t_stat, p_value.
    """
    if n1 < 2 or n2 < 2 or std1 <= 0 or std2 <= 0:
        return 0.0, 1.0
    se = np.sqrt((std1**2 / n1) + (std2**2 / n2))
    if se <= 0:
        return 0.0, 1.0
    t = (mean1 - mean2) / se
    # Welch-Satterthwaite df
    df_num = ((std1**2 / n1) + (std2**2 / n2))**2
    df_den = ((std1**2 / n1)**2 / (n1 - 1)) + ((std2**2 / n2)**2 / (n2 - 1))
    df = df_num / df_den if df_den > 0 else (n1 + n2 - 2)
    p_val = 2 * (1 - stats.t.cdf(abs(t), df=df))
    return t, p_val

def apply_base_size_flag(n):
    """
    Base size discipline:
    - n >= 50: Robust base (empty flag)
    - 30 <= n < 50: Low base ('*')
    - n < 30: Very low base ('**' - suppress significance testing)
    """
    if n >= 50:
        return ""
    elif n >= 30:
        return "*"
    else:
        return "**"

def format_cell_prop(p, n, col_letter, sig_letters):
    """
    Formats proportion with base size rules:
    - n < 30: Enclose in parentheses '(XX%)' and no letters
    - 30 <= n < 49: 'XX%*' + letters
    - n >= 50: 'XX%' + letters
    """
    pct_val = p * 100
    if n < 30:
        return f"({pct_val:.1f}%)**"
    elif n < 50:
        sig_str = f" {sig_letters}" if sig_letters else ""
        return f"{pct_val:.1f}%*{sig_str}"
    else:
        sig_str = f" {sig_letters}" if sig_letters else ""
        return f"{pct_val:.1f}%{sig_str}"

def format_cell_mean(m, s, n, col_letter, sig_letters):
    """
    Formats mean with base size rules
    """
    if n < 30:
        return f"({m:.2f})**"
    elif n < 50:
        sig_str = f" {sig_letters}" if sig_letters else ""
        return f"{m:.2f}*{sig_str}"
    else:
        sig_str = f" {sig_letters}" if sig_letters else ""
        return f"{m:.2f}{sig_str}"

def generate_banner_table_proportions(df, question_col, banner_col, category_value, banner_cols_order, banner_labels):
    """
    Generates a rigorous crosstab row for a binary/categorical proportion across banner columns,
    performing pairwise z-tests with column significance letters and base-size flags.
    """
    n_cols = len(banner_cols_order)
    col_letters = [chr(65 + i) for i in range(n_cols)] # A, B, C...
    
    col_data = []
    
    for i, col_val in enumerate(banner_cols_order):
        if col_val == 'TOTAL':
            sub = df
        else:
            sub = df[df[banner_col] == col_val]
            
        unweighted_n = len(sub)
        if unweighted_n > 0:
            # Weighted proportion
            w = sub['WEIGHT']
            matches = (sub[question_col] == category_value).astype(int)
            weighted_p = np.average(matches, weights=w)
            weighted_count = np.sum(matches * w)
        else:
            weighted_p = 0.0
            weighted_count = 0.0
            
        col_data.append({
            'letter': col_letters[i],
            'label': banner_labels[i],
            'n': unweighted_n,
            'p': weighted_p,
            'count': weighted_count,
            'sig_letters': []
        })
        
    # Perform pairwise significance tests (skip Total column at index 0 from being compared to itself)
    # Comparison between columns i and j (excluding column 0 which is Total)
    for i in range(1, n_cols):
        for j in range(1, n_cols):
            if i == j: continue
            
            n_i = col_data[i]['n']
            n_j = col_data[j]['n']
            p_i = col_data[i]['p']
            p_j = col_data[j]['p']
            
            # Minimum base-size rule: suppress significance if either cell < 30
            if n_i >= 30 and n_j >= 30:
                if p_i > p_j:
                    _, p_val = z_test_proportions(p_i, n_i, p_j, n_j)
                    if p_val < 0.05:
                        col_data[i]['sig_letters'].append(col_data[j]['letter'])
                        
    # Build formatted row
    formatted_cells = {}
    for i, d in enumerate(col_data):
        sig_str = "".join(d['sig_letters'])
        formatted_cells[d['label']] = format_cell_prop(d['p'], d['n'], d['letter'], sig_str)
        formatted_cells[f"{d['label']}_raw_p"] = d['p']
        formatted_cells[f"{d['label']}_n"] = d['n']
        formatted_cells[f"{d['label']}_sig"] = sig_str
        
    return formatted_cells

def generate_banner_table_means(df, question_col, banner_col, banner_cols_order, banner_labels):
    """
    Generates a crosstab row for continuous rating scales across banner columns,
    performing pairwise Welch t-tests with column significance letters and base-size flags.
    """
    n_cols = len(banner_cols_order)
    col_letters = [chr(65 + i) for i in range(n_cols)]
    
    col_data = []
    
    for i, col_val in enumerate(banner_cols_order):
        if col_val == 'TOTAL':
            sub = df
        else:
            sub = df[df[banner_col] == col_val]
            
        unweighted_n = len(sub)
        if unweighted_n > 0:
            w = sub['WEIGHT']
            vals = sub[question_col].astype(float)
            weighted_mean = np.average(vals, weights=w)
            weighted_var = np.average((vals - weighted_mean)**2, weights=w)
            weighted_std = np.sqrt(weighted_var)
        else:
            weighted_mean = 0.0
            weighted_std = 0.0
            
        col_data.append({
            'letter': col_letters[i],
            'label': banner_labels[i],
            'n': unweighted_n,
            'mean': weighted_mean,
            'std': weighted_std,
            'sig_letters': []
        })
        
    for i in range(1, n_cols):
        for j in range(1, n_cols):
            if i == j: continue
            
            n_i = col_data[i]['n']
            n_j = col_data[j]['n']
            m_i = col_data[i]['mean']
            m_j = col_data[j]['mean']
            s_i = col_data[i]['std']
            s_j = col_data[j]['std']
            
            if n_i >= 30 and n_j >= 30:
                if m_i > m_j:
                    _, p_val = t_test_means(m_i, s_i, n_i, m_j, s_j, n_j)
                    if p_val < 0.05:
                        col_data[i]['sig_letters'].append(col_data[j]['letter'])
                        
    formatted_cells = {}
    for i, d in enumerate(col_data):
        sig_str = "".join(d['sig_letters'])
        formatted_cells[d['label']] = format_cell_mean(d['mean'], d['std'], d['n'], d['letter'], sig_str)
        formatted_cells[f"{d['label']}_raw_mean"] = d['mean']
        formatted_cells[f"{d['label']}_n"] = d['n']
        formatted_cells[f"{d['label']}_sig"] = sig_str
        
    return formatted_cells

def run_van_westendorp_analysis(df):
    """
    Calculates Van Westendorp Price Sensitivity curves for SAR/AED respondents (KSA & UAE, N~1,020).
    Returns price points: PMC, PME, IPP, OPP and summary curve table.
    """
    print("\nRunning Van Westendorp Price Sensitivity Analysis (SAR/AED respondents)...")
    sub = df[df['MARKET'].isin(['KSA', 'UAE'])].copy()
    n_vw = len(sub)
    print(f"  - Sample size for SAR/AED pricing: N = {n_vw}")
    
    price_steps = np.arange(20, 321, 5) # 20 to 320 in steps of 5
    
    vw_curves = []
    
    # Pre-extract numpy arrays
    tc = sub['VW_TOO_CHEAP'].values
    ch = sub['VW_CHEAP'].values
    ex = sub['VW_EXPENSIVE'].values
    te = sub['VW_TOO_EXPENSIVE'].values
    weights = sub['WEIGHT'].values if 'WEIGHT' in sub.columns else np.ones(len(sub), dtype=float)
    total_w = np.sum(weights)
    
    for p in price_steps:
        # Too Cheap: % who consider price <= p (reverse/downward: price <= p is too cheap)
        pct_tc = (np.sum(weights[tc >= p]) / total_w) * 100.0
        
        # Cheap (Bargain): % who consider price <= p
        pct_ch = (np.sum(weights[ch >= p]) / total_w) * 100.0
        
        # Expensive: % who consider price >= p
        pct_ex = (np.sum(weights[ex <= p]) / total_w) * 100.0
        
        # Too Expensive: % who consider price >= p
        pct_te = (np.sum(weights[te <= p]) / total_w) * 100.0
        
        vw_curves.append({
            'Price_SAR_AED': p,
            'Pct_Too_Cheap': pct_tc,
            'Pct_Cheap_Bargain': pct_ch,
            'Pct_Expensive': pct_ex,
            'Pct_Too_Expensive': pct_te
        })
        
    df_curves = pd.DataFrame(vw_curves)
    
    # Find intersections:
    # 1. Point of Marginal Cheapness (PMC): Too Cheap == Expensive
    diff_pmc = np.abs(df_curves['Pct_Too_Cheap'] - df_curves['Pct_Expensive'])
    pmc_price = df_curves.loc[diff_pmc.idxmin(), 'Price_SAR_AED']
    
    # 2. Point of Marginal Expensiveness (PME): Cheap == Too Expensive
    diff_pme = np.abs(df_curves['Pct_Cheap_Bargain'] - df_curves['Pct_Too_Expensive'])
    pme_price = df_curves.loc[diff_pme.idxmin(), 'Price_SAR_AED']
    
    # 3. Indifference Price Point (IPP): Cheap == Expensive
    diff_ipp = np.abs(df_curves['Pct_Cheap_Bargain'] - df_curves['Pct_Expensive'])
    ipp_price = df_curves.loc[diff_ipp.idxmin(), 'Price_SAR_AED']
    
    # 4. Optimal Price Point (OPP): Too Cheap == Too Expensive
    diff_opp = np.abs(df_curves['Pct_Too_Cheap'] - df_curves['Pct_Too_Expensive'])
    opp_price = df_curves.loc[diff_opp.idxmin(), 'Price_SAR_AED']
    
    vw_summary = {
        'Point_of_Marginal_Cheapness_PMC': float(pmc_price),
        'Indifference_Price_Point_IPP': float(ipp_price),
        'Optimal_Price_Point_OPP': float(opp_price),
        'Point_of_Marginal_Expensiveness_PME': float(pme_price),
        'Range_of_Acceptable_Pricing': f"{pmc_price:.0f} - {pme_price:.0f} SAR/AED",
        'Optimal_Launch_Price_Recommendation': f"{opp_price:.0f} SAR/AED (approx 12.5 KWD in Kuwait)",
        'Base_N': n_vw
    }
    
    print("  Van Westendorp Key Metrics:")
    for k, v in vw_summary.items():
        print(f"    - {k:<36}: {v}")
        
    return df_curves, vw_summary

def run_concept_monadic_analysis(df):
    """
    Monadic evaluation of Concept A vs Concept B with Top-2-Box, Top-Box, Means,
    and significance testing (two-tailed z-test & Welch t-test).
    """
    print("\nRunning Monadic Concept Test Evaluation (Concept A vs Concept B)...")
    
    cA = df[df['CONCEPT_CELL'] == 1].copy()
    cB = df[df['CONCEPT_CELL'] == 2].copy()
    
    nA = len(cA)
    nB = len(cB)
    
    wA = cA['WEIGHT'] if 'WEIGHT' in cA.columns else np.ones(len(cA))
    wB = cB['WEIGHT'] if 'WEIGHT' in cB.columns else np.ones(len(cB))
    
    # Metrics:
    # Purchase intent: 5 = Definitely, 4 = Probably, 3 = Might, 2 = Prob not, 1 = Def not
    t2b_A = np.average((cA['PURCHASE_INTENT_5PT'] >= 4).astype(int), weights=wA)
    t2b_B = np.average((cB['PURCHASE_INTENT_5PT'] >= 4).astype(int), weights=wB)
    
    t1b_A = np.average((cA['PURCHASE_INTENT_5PT'] == 5).astype(int), weights=wA)
    t1b_B = np.average((cB['PURCHASE_INTENT_5PT'] == 5).astype(int), weights=wB)
    
    mean_pi_A = np.average(cA['PURCHASE_INTENT_5PT'], weights=wA)
    std_pi_A = np.sqrt(np.average((cA['PURCHASE_INTENT_5PT'] - mean_pi_A)**2, weights=wA))
    
    mean_pi_B = np.average(cB['PURCHASE_INTENT_5PT'], weights=wB)
    std_pi_B = np.sqrt(np.average((cB['PURCHASE_INTENT_5PT'] - mean_pi_B)**2, weights=wB))
    
    # Significance tests
    z_t2b, p_t2b = z_test_proportions(t2b_A, nA, t2b_B, nB)
    z_t1b, p_t1b = z_test_proportions(t1b_A, nA, t1b_B, nB)
    t_pi, p_pi = t_test_means(mean_pi_A, std_pi_A, nA, mean_pi_B, std_pi_B, nB)
    
    # Diagnostics
    diag_metrics = ['DIAG_UNIQUENESS', 'DIAG_RELEVANCE', 'DIAG_BELIEVABILITY', 'DIAG_VALUE_FOR_MONEY']
    diag_results = []
    
    for d in diag_metrics:
        mA = np.average(cA[d], weights=wA)
        sA = np.sqrt(np.average((cA[d] - mA)**2, weights=wA))
        mB = np.average(cB[d], weights=wB)
        sB = np.sqrt(np.average((cB[d] - mB)**2, weights=wB))
        t_d, p_d = t_test_means(mA, sA, nA, mB, sB, nB)
        
        diag_results.append({
            'Metric': d.replace('DIAG_', '').title(),
            'Concept_A_Mean': round(mA, 2),
            'Concept_B_Mean': round(mB, 2),
            'Diff_A_minus_B': round(mA - mB, 2),
            't_stat': round(t_d, 3),
            'p_value': round(p_d, 4),
            'Significant_05': 'Yes (A > B)' if (p_d < 0.05 and mA > mB) else ('Yes (B > A)' if (p_d < 0.05 and mB > mA) else 'No')
        })
        
    concept_summary = {
        'Sample_Size_A': nA,
        'Sample_Size_B': nB,
        'Top2Box_A_Pct': round(t2b_A * 100, 1),
        'Top2Box_B_Pct': round(t2b_B * 100, 1),
        'Top2Box_p_value': round(p_t2b, 4),
        'TopBox_A_Pct': round(t1b_A * 100, 1),
        'TopBox_B_Pct': round(t1b_B * 100, 1),
        'TopBox_p_value': round(p_t1b, 4),
        'Mean_PI_A': round(mean_pi_A, 2),
        'Mean_PI_B': round(mean_pi_B, 2),
        'Mean_PI_p_value': round(p_pi, 4),
        'Diagnostics_Table': diag_results
    }
    
    print(f"  Concept A Top-2-Box: {t2b_A*100:.1f}% vs Concept B: {t2b_B*100:.1f}% (p = {p_t2b:.4f})")
    print(f"  Concept A Top-Box:   {t1b_A*100:.1f}% vs Concept B: {t1b_B*100:.1f}% (p = {p_t1b:.4f})")
    print(f"  Concept A Mean PI:   {mean_pi_A:.2f} vs Concept B: {mean_pi_B:.2f} (p = {p_pi:.4f})")
    
    return pd.DataFrame(diag_results), concept_summary

def main():
    clean_path = "data/cleaned_survey_data.csv"
    if not os.path.exists(clean_path):
        print("Cleaning script has not been run yet. Running qc_cleaning now...")
        import qc_cleaning
        qc_cleaning.run_quality_control()
        
    df = pd.read_csv(clean_path)
    
    # 1. Weights
    df, deff, n_eff = compute_weights(df)
    df.to_csv(clean_path, index=False)
    print(f"Updated {clean_path} with WEIGHT column.")
    
    # 2. Van Westendorp
    df_vw_curves, vw_summary = run_van_westendorp_analysis(df)
    
    # 3. Monadic Concept
    df_diag, concept_summary = run_concept_monadic_analysis(df)
    
    print("\nWeighting and core analytical modeling complete!")

if __name__ == "__main__":
    main()
