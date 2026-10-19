#!/usr/bin/env python3
"""
test_research_kit.py
Comprehensive unit test suite for the GCC Consumer Research Kit.
Validates:
1. Automated QC detection rules (speeders, straight-liners, duplicates, logic inversions).
2. Minimum base-size flagging discipline (>=50, 30-49, <30).
3. Statistical significance engines (z-test for proportions, Welch t-test for means).
4. Van Westendorp Price Sensitivity Meter calculation and curve monotonicity.
5. Cohen's Kappa and AI open-end classification metrics.
"""

import unittest
import numpy as np
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from qc_cleaning import run_quality_control
from weighting_and_crosstabs import (
    z_test_proportions,
    t_test_means,
    apply_base_size_flag,
    compute_weights,
    run_van_westendorp_analysis
)
from ai_open_end_coding import compute_classification_metrics

class TestGCCResearchKit(unittest.TestCase):
    
    def test_base_size_flagging_discipline(self):
        """Test that minimum base-size discipline rules strictly apply."""
        self.assertEqual(apply_base_size_flag(100), "", "Base >= 50 should have no flag.")
        self.assertEqual(apply_base_size_flag(50), "", "Base = 50 should have no flag.")
        self.assertEqual(apply_base_size_flag(49), "*", "Base 30-49 must have single asterisk (*).")
        self.assertEqual(apply_base_size_flag(30), "*", "Base = 30 must have single asterisk (*).")
        self.assertEqual(apply_base_size_flag(29), "**", "Base < 30 must have double asterisk (**).")
        self.assertEqual(apply_base_size_flag(5), "**", "Base < 30 must have double asterisk (**).")

    def test_z_test_proportions(self):
        """Test two-proportion pooled z-test against known analytical benchmarks."""
        # Significant difference case: 65% vs 45%, n=200 each
        z, p = z_test_proportions(0.65, 200, 0.45, 200)
        self.assertGreater(z, 3.8, "z-score should be > 3.8 for 65% vs 45% at n=200")
        self.assertLess(p, 0.001, "p-value should be highly significant (< 0.001)")
        
        # Parity case: 50% vs 51%, n=100 each
        z_null, p_null = z_test_proportions(0.50, 100, 0.51, 100)
        self.assertAlmostEqual(z_null, -0.14, delta=0.1)
        self.assertGreater(p_null, 0.8, "p-value should be non-significant for 50% vs 51%")
        
        # Boundary zero / small sample handling
        z_zero, p_zero = z_test_proportions(0.5, 0, 0.5, 50)
        self.assertEqual(p_zero, 1.0, "Zero base size should return p=1.0 safely without crashing.")

    def test_t_test_means(self):
        """Test Welch's two-sample t-test."""
        # Mean 4.2 (std 0.8) vs Mean 3.6 (std 0.9), n=300 each
        t, p = t_test_means(4.2, 0.8, 300, 3.6, 0.9, 300)
        self.assertGreater(t, 8.0, "t-stat should be > 8.0 for 0.6 difference at n=300")
        self.assertLess(p, 1e-10, "p-value should be extreme")

    def test_cohens_kappa_calculation(self):
        """Test pure-Python Cohen's Kappa implementation."""
        # Perfect agreement
        y_true = ["A", "B", "C", "A", "B"]
        y_pred = ["A", "B", "C", "A", "B"]
        res_perfect = compute_classification_metrics(y_true, y_pred, ["A", "B", "C"])
        self.assertAlmostEqual(res_perfect['Cohens_Kappa'], 1.0, places=4)
        self.assertAlmostEqual(res_perfect['Accuracy'], 1.0, places=4)
        
        # Chance agreement / complete disagreement
        y_opp = ["B", "C", "A", "B", "C"]
        res_opp = compute_classification_metrics(y_true, y_opp, ["A", "B", "C"])
        self.assertLessEqual(res_opp['Cohens_Kappa'], 0.0)

    def test_qc_cleaning_pipeline(self):
        """Test that QC cleaning script flags known defect rows and outputs clean dataset."""
        clean_df, removal_df = run_quality_control(
            raw_data_path="data/raw_survey_data.csv",
            clean_data_path="data/cleaned_survey_data.csv",
            removal_log_path="outputs/qc_removal_log.csv"
        )
        self.assertGreaterEqual(len(removal_df), 120, "Should catch >= 120 defect events")
        self.assertGreaterEqual(len(clean_df), 1150, "Should preserve >= 1,150 clean records")
        
        # Check that no speeder remains in clean dataset
        self.assertTrue((clean_df['LOI_SECONDS'] >= 240).all(), "No speeder (<240s) should remain in clean data.")
        
        # Check that no non-monotonic Van Westendorp remains in clean data
        tc = clean_df['VW_TOO_CHEAP']
        te = clean_df['VW_TOO_EXPENSIVE']
        self.assertTrue((tc < te).all(), "Every clean respondent must satisfy Too Cheap < Too Expensive.")

    def test_van_westendorp_logic(self):
        """Test that Van Westendorp price intersection relationships hold."""
        df_clean = pd.read_csv("data/cleaned_survey_data.csv")
        df_curves, vw_summary = run_van_westendorp_analysis(df_clean)
        
        pmc = vw_summary['Point_of_Marginal_Cheapness_PMC']
        pme = vw_summary['Point_of_Marginal_Expensiveness_PME']
        opp = vw_summary['Optimal_Price_Point_OPP']
        ipp = vw_summary['Indifference_Price_Point_IPP']
        
        self.assertLess(pmc, pme, "Point of Marginal Cheapness must be strictly lower than Point of Marginal Expensiveness.")
        self.assertGreaterEqual(opp, pmc, "Optimal Price Point must fall at or above Marginal Cheapness.")
        self.assertLessEqual(opp, pme, "Optimal Price Point must fall at or below Marginal Expensiveness.")

if __name__ == "__main__":
    unittest.main()
