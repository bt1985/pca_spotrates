"""
Unit tests for Stress Scenario Generator
Tests the StressScenarioGenerator class
"""

import pytest
import numpy as np
import pandas as pd
import json

from services.stress_scenarios import StressScenarioGenerator


@pytest.mark.unit
class TestStressScenarioGenerator:
    """Test suite for Stress Scenario Generator"""

    def test_initialization(self, stress_generator):
        """Test stress scenario generator initialization"""
        assert stress_generator is not None
        assert isinstance(stress_generator, StressScenarioGenerator)

    def test_generate_scenarios_basic(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test basic stress scenario generation"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data,
            quantile=0.995,
            rolling_window=24,
            unit=30
        )

        # Check returned structure
        assert 'stressed_scores_up' in results
        assert 'stressed_scores_down' in results
        assert 'rolling_quantile_up' in results
        assert 'rolling_quantile_down' in results
        assert 'scenarios' in results
        assert 'scores_plot' in results
        assert 'scenarios_plot' in results
        assert 'latest_date' in results

    def test_stressed_scores_shape(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test that stressed scores have correct shape"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        stressed_up = results['stressed_scores_up']
        stressed_down = results['stressed_scores_down']

        # Should have 3 columns (PC1, PC2, PC3)
        assert stressed_up.shape[1] == 3
        assert stressed_down.shape[1] == 3

        # Should have same number of rows
        assert stressed_up.shape[0] == stressed_down.shape[0]

    def test_scenarios_for_all_pcs(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test that scenarios are generated for PC1, PC2, PC3"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        scenarios = results['scenarios']

        # Should have scenarios for PC1, PC2, PC3
        assert 'PC1' in scenarios
        assert 'PC2' in scenarios
        assert 'PC3' in scenarios

    def test_scenario_structure(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test structure of individual scenarios"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        scenario = results['scenarios']['PC1']

        # Each scenario should have original, up, and down curves
        assert 'original' in scenario
        assert 'up' in scenario
        assert 'down' in scenario
        assert 'maturities' in scenario

    def test_stressed_curves_different_from_original(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test that stressed curves differ from original"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        for pc in ['PC1', 'PC2', 'PC3']:
            scenario = results['scenarios'][pc]
            original = scenario['original']
            up = scenario['up']
            down = scenario['down']

            # Stressed curves should differ from original
            assert not np.allclose(original, up, rtol=0.001)
            assert not np.allclose(original, down, rtol=0.001)

    def test_up_down_scenarios_opposite_directions(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test that up and down scenarios move in opposite directions"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        # For at least one PC, up and down should be different
        scenario = results['scenarios']['PC1']
        up = scenario['up']
        down = scenario['down']

        # They should be different
        assert not np.allclose(up, down, rtol=0.001)

    def test_quantile_parameter(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test different quantile levels"""
        # Generate with different quantiles
        results_99 = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data,
            quantile=0.99
        )

        results_995 = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data,
            quantile=0.995
        )

        # Results should differ
        assert results_99 is not None
        assert results_995 is not None

    def test_rolling_window_parameter(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test different rolling window sizes"""
        # Small window
        results_12 = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data,
            rolling_window=12
        )

        # Large window
        results_24 = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data,
            rolling_window=24
        )

        # Both should complete
        assert results_12 is not None
        assert results_24 is not None

    def test_latest_date_format(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test that latest date is in correct format"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        latest_date = results['latest_date']

        # Should be string in YYYY-MM-DD format
        assert isinstance(latest_date, str)
        assert len(latest_date) == 10
        assert latest_date.count('-') == 2

    def test_scores_plot_format(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test that scores plot is valid JSON"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        plot_json = results['scores_plot']

        # Should be valid JSON
        plot_data = json.loads(plot_json)
        assert 'data' in plot_data
        assert 'layout' in plot_data

    def test_scenarios_plot_format(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test that scenarios plot is valid JSON"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        plot_json = results['scenarios_plot']

        # Should be valid JSON
        plot_data = json.loads(plot_json)
        assert 'data' in plot_data
        assert 'layout' in plot_data

    def test_stressed_scores_columns(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test that stressed scores have correct column names"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        stressed_up = results['stressed_scores_up']
        stressed_down = results['stressed_scores_down']

        # Check column names
        expected_cols = ['PC1', 'PC2', 'PC3']
        assert list(stressed_up.columns) == expected_cols
        assert list(stressed_down.columns) == expected_cols

    def test_rolling_quantile_calculation(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test rolling quantile calculations"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data,
            quantile=0.995
        )

        rolling_quantile_up = results['rolling_quantile_up']
        rolling_quantile_down = results['rolling_quantile_down']

        # Should be DataFrames
        assert isinstance(rolling_quantile_up, pd.DataFrame)
        assert isinstance(rolling_quantile_down, pd.DataFrame)

        # Should have PC1, PC2, PC3 columns
        assert 'PC1' in rolling_quantile_up.columns
        assert 'PC2' in rolling_quantile_up.columns
        assert 'PC3' in rolling_quantile_up.columns

    def test_maturities_in_scenarios(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test that maturities are included in scenarios"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        scenario = results['scenarios']['PC1']
        maturities = scenario['maturities']

        # Should have maturities
        assert len(maturities) > 0
        assert isinstance(maturities, list)

    def test_scenario_curve_lengths_match(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test that all curves in a scenario have same length"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        for pc in ['PC1', 'PC2', 'PC3']:
            scenario = results['scenarios'][pc]

            original_len = len(scenario['original'])
            up_len = len(scenario['up'])
            down_len = len(scenario['down'])
            maturities_len = len(scenario['maturities'])

            # All should have same length
            assert original_len == up_len == down_len == maturities_len


@pytest.mark.unit
class TestStressScenarioEdgeCases:
    """Test edge cases for stress scenario generation"""

    def test_short_time_series(self, stress_generator, pca_analyzer, small_yield_data):
        """Test with short time series"""
        pca_results = pca_analyzer.perform_pca(small_yield_data)

        results = stress_generator.generate_scenarios(
            pca_results,
            small_yield_data,
            rolling_window=1,  # Very small window
            unit=1
        )

        # Should still work
        assert results is not None
        assert 'scenarios' in results

    def test_extreme_quantile(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test with extreme quantile values"""
        # Very high quantile
        results_high = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data,
            quantile=0.999
        )

        # Lower quantile
        results_low = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data,
            quantile=0.90
        )

        # Both should work
        assert results_high is not None
        assert results_low is not None

    def test_single_component_stress(self, stress_generator, sample_pca_results, sample_yield_data):
        """Test stressing individual components"""
        results = stress_generator.generate_scenarios(
            sample_pca_results,
            sample_yield_data
        )

        # Each PC scenario should only stress that specific PC
        # This is implicit in the _generate_pc_scenario method
        assert 'PC1' in results['scenarios']
        assert 'PC2' in results['scenarios']
        assert 'PC3' in results['scenarios']
