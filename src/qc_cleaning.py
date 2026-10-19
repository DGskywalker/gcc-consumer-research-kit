#!/usr/bin/env python3
"""
qc_cleaning.py
Automated survey data quality control engine.
Executes speeding detection, straight-lining detection, duplicate record filtering,
and logical consistency checks. Generates an itemized removal audit log and clean dataset.
"""

import os
import numpy as np
import pandas as pd

def run_quality_control(raw_data_path="data/raw_survey_data.csv",
                        clean_data_path="data/cleaned_survey_data.csv",
                        removal_log_path="outputs/qc_removal_log.csv"):
    print("=" * 70)
    print("STARTING AUTOMATED SURVEY DATA QUALITY CONTROL (QC)")
    print("=" * 70)
    
    if not os.path.exists(raw_data_path):
        raise FileNotFoundError(f"Raw data file not found at {raw_data_path}")
        
    df = pd.read_csv(raw_data_path)
    initial_count = len(df)
    print(f"Loaded raw dataset with {initial_count} records.")
    
    removal_log = []
    failed_resp_ids = set()
    
    # -------------------------------------------------------------
    # 1. SPEEDING DETECTION (LOI Threshold)
    # -------------------------------------------------------------
    # Rule: Standard MR guideline is 1/3 of the median LOI.
    # In this survey, median LOI is ~720 seconds (12 mins). LOI < 240 seconds is flagged.
    median_loi = df['LOI_SECONDS'].median()
    speeding_threshold = 240 # 4 minutes
    
    speeders = df[df['LOI_SECONDS'] < speeding_threshold]
    print(f"\n[QC Rule 1] Speeding Check:")
    print(f"  - Median LOI: {median_loi:.1f}s | Speeding Cutoff: < {speeding_threshold}s")
    print(f"  - Flagged records: {len(speeders)}")
    
    for _, row in speeders.iterrows():
        resp_id = row['RESP_ID']
        failed_resp_ids.add(resp_id)
        removal_log.append({
            'RESP_ID': resp_id,
            'FAIL_RULE': 'SPEEDING',
            'SEVERITY': 'CRITICAL',
            'VALUE_RECORDED': f"{row['LOI_SECONDS']} seconds",
            'THRESHOLD': f"< {speeding_threshold} seconds",
            'REASON': f"Survey completed in {row['LOI_SECONDS']}s (threshold: < 240s; median: {median_loi:.0f}s). Insufficient time to read questions."
        })

    # -------------------------------------------------------------
    # 2. STRAIGHT-LINING DETECTION (Grid Scales)
    # -------------------------------------------------------------
    # Rule: Check standard deviation across the 6-item Q2 stressors battery.
    # If StdDev == 0 (identical response across all 6 items), flag as straight-lining.
    q2_cols = [
        'Q2_1_HARD_WATER', 'Q2_2_AC_DRYNESS', 'Q2_3_SUMMER_HEAT',
        'Q2_4_HIJAB_SWEAT', 'Q2_5_CHEMICAL_DAMAGE', 'Q2_6_STRESS_FALL'
    ]
    
    print(f"\n[QC Rule 2] Straight-lining Check (Q2 Stressors Battery):")
    straightliners = []
    for _, row in df.iterrows():
        resp_id = row['RESP_ID']
        scores = [row[c] for c in q2_cols]
        score_std = np.std(scores)
        if score_std == 0:
            straightliners.append((resp_id, scores[0]))
            failed_resp_ids.add(resp_id)
            removal_log.append({
                'RESP_ID': resp_id,
                'FAIL_RULE': 'STRAIGHT_LINING',
                'SEVERITY': 'HIGH',
                'VALUE_RECORDED': f"Score={scores[0]} across all 6 items (StdDev=0.0)",
                'THRESHOLD': "StdDev > 0.0 across 6-item battery",
                'REASON': f"Identical rating of {scores[0]} across all 6 items in Q2 battery without reading individual statements."
            })
    print(f"  - Flagged records: {len(straightliners)}")

    # -------------------------------------------------------------
    # 3. DUPLICATE SUBMISSION DETECTION (IP / Fingerprint)
    # -------------------------------------------------------------
    # Rule: If multiple submissions originate from identical IP address with identical verbatims/demographics,
    # preserve the first submission and flag all subsequent submissions.
    print(f"\n[QC Rule 3] Duplicate Submissions Check:")
    dup_mask = df.duplicated(subset=['IP_ADDRESS', 'MARKET', 'GENDER', 'AGE_GROUP', 'VERBATIM_LIKES'], keep='first')
    duplicate_records = df[dup_mask]
    print(f"  - Flagged repeat duplicate records: {len(duplicate_records)}")
    
    for _, row in duplicate_records.iterrows():
        resp_id = row['RESP_ID']
        failed_resp_ids.add(resp_id)
        removal_log.append({
            'RESP_ID': resp_id,
            'FAIL_RULE': 'DUPLICATE_SUBMISSION',
            'SEVERITY': 'CRITICAL',
            'VALUE_RECORDED': f"IP: {row['IP_ADDRESS']}",
            'THRESHOLD': "Unique IP & Demographics per respondent",
            'REASON': f"Repeat duplicate submission matching prior respondent on IP address {row['IP_ADDRESS']}, demographic profile, and verbatim text."
        })

    # -------------------------------------------------------------
    # 4. LOGICAL CONSISTENCY & IMPOSSIBLE VALUES
    # -------------------------------------------------------------
    print(f"\n[QC Rule 4] Logical Consistency & Impossible Values:")
    logic_violations = 0
    
    for _, row in df.iterrows():
        resp_id = row['RESP_ID']
        
        # 4.1 Van Westendorp Price Monotonicity Check
        # Must strictly satisfy: 0 < Too Cheap < Cheap < Expensive < Too Expensive
        tc = row['VW_TOO_CHEAP']
        ch = row['VW_CHEAP']
        ex = row['VW_EXPENSIVE']
        te = row['VW_TOO_EXPENSIVE']
        
        vw_invalid = False
        vw_reason = ""
        if tc <= 0 or ch <= 0 or ex <= 0 or te <= 0:
            vw_invalid = True
            vw_reason = f"Negative or zero price detected (TC={tc}, CH={ch}, EX={ex}, TE={te})"
        elif not (tc < ch < ex < te):
            vw_invalid = True
            vw_reason = f"Non-monotonic pricing (TC={tc}, CH={ch}, EX={ex}, TE={te}). Expected TC < CH < EX < TE."
            
        if vw_invalid:
            failed_resp_ids.add(resp_id)
            logic_violations += 1
            removal_log.append({
                'RESP_ID': resp_id,
                'FAIL_RULE': 'LOGIC_PRICE_INVERSION',
                'SEVERITY': 'HIGH',
                'VALUE_RECORDED': f"TC={tc}, CH={ch}, EX={ex}, TE={te}",
                'THRESHOLD': "Strict Monotonic Order: TC < CH < EX < TE and values > 0",
                'REASON': vw_reason
            })
            
        # 4.2 Brand Funnel Hierarchy Violation
        # Brand Used Most Often (BUMO) must be present in Past 3 Months used brands
        bumo = str(row['BUMO_BRAND']).strip()
        p3m = str(row['P3M_USED_BRANDS']).strip()
        ever = str(row['EVER_USED_BRANDS']).strip()
        
        if bumo and bumo != 'nan':
            if bumo not in p3m or bumo not in ever:
                failed_resp_ids.add(resp_id)
                logic_violations += 1
                removal_log.append({
                    'RESP_ID': resp_id,
                    'FAIL_RULE': 'LOGIC_BRAND_FUNNEL',
                    'SEVERITY': 'HIGH',
                    'VALUE_RECORDED': f"BUMO='{bumo}', EverUsed='{ever}'",
                    'THRESHOLD': "BUMO brand must be subset of Ever Used and P3M Used",
                    'REASON': f"Respondent claimed '{bumo}' as Most Often Used, but it was not reported in Ever Used or Past 3M Used."
                })
                
    print(f"  - Flagged logic inconsistency violations: {logic_violations}")

    # -------------------------------------------------------------
    # 5. GENERATE REMOVAL AUDIT LOG & CLEAN DATASET
    # -------------------------------------------------------------
    df_removal = pd.DataFrame(removal_log)
    os.makedirs(os.path.dirname(removal_log_path), exist_ok=True)
    df_removal.to_csv(removal_log_path, index=False)
    print(f"\nSaved QC Removal Audit Log with {len(df_removal)} failure events to {removal_log_path}")
    
    unique_failed_respondents = len(failed_resp_ids)
    df_clean = df[~df['RESP_ID'].isin(failed_resp_ids)].copy()
    df_clean.to_csv(clean_data_path, index=False)
    
    attrition_rate = (unique_failed_respondents / initial_count) * 100
    
    print("\n" + "=" * 70)
    print("QC CLEANING SUMMARY & ATTRITION REPORT")
    print("=" * 70)
    print(f"Total Raw Records:             {initial_count:>6}")
    print(f"Total Unique Failed Records:   {unique_failed_respondents:>6} ({attrition_rate:.1f}% attrition)")
    print(f"Total Clean Qualified Records: {len(df_clean):>6}")
    print(f"Clean Dataset Saved:           {clean_data_path}")
    print("=" * 70)
    
    # Attrition breakdown by rule
    rule_counts = df_removal['FAIL_RULE'].value_counts()
    print("\nBreakdown of QC Failure Events by Rule:")
    for rule, count in rule_counts.items():
        print(f"  - {rule:<25}: {count:>4} events")
        
    return df_clean, df_removal

if __name__ == "__main__":
    run_quality_control()
