"""
Unit tests for PCA Analysis Service
Tests the PCAAnalyzer class
"""

import pytest
import numpy as np
import pandas as pd
import json

from services.pca_analysis import PCAAnalyzer


@pytest.mark.unit
class TestPCAAnalyzer:
    """Test suite for PCA Analyzer"""

    def test_initialization(self):
        """Test PCA analyzer initialization"""
        analyzer = PCAAnalyzer(n_components=5)
        assert analyzer.n_components == 5
        assert analyzer.pca is None
        assert analyzer.mean_curve is None
        assert analyzer.maturities is None

    def test_initialization_default_components(self):
        """Test default number of components"""
        analyzer = PCAAnalyzer()
        assert analyzer.n_components == 5

    def test_perform_pca_with_sample_data(self, pca_analyzer, sample_yield_data):
        """Test PCA with sample yield curve data"""
        results = pca_analyzer.perform_pca(sample_yield_data)

        # Check returned structure
        assert 'pca_model' in results
        assert 'scores' in results
        assert 'dates' in results
        assert 'yield_matrix' in results
        assert 'mean_curve' in results
        assert 'variance_explained' in results
        assert 'cumulative_variance' in results
        assert 'yield_curve_plot' in results
        assert 'pc_plot' in results
        assert 'variance_plot' in results

    def test_pca_scores_shape(self, pca_analyzer, sample_yield_data):
        """Test that PCA scores have correct shape"""
        results = pca_analyzer.perform_pca(sample_yield_data)

        scores = results['scores']
        n_observations = len(sample_yield_data)
        n_components = pca_analyzer.n_components

        assert scores.shape == (n_observations, n_components)

    def test_pca_components_shape(self, pca_analyzer, sample_yield_data):
        """Test that PCA components have correct shape"""
        results = pca_analyzer.perform_pca(sample_yield_data)

        pca_model = results['pca_model']
        n_features = len([col for col in sample_yield_data.columns if col.startswith('SR_')])
        n_components = pca_analyzer.n_components

        assert pca_model.components_.shape == (n_components, n_features)

    def test_variance_explained_sum(self, pca_analyzer, sample_yield_data):
        """Test that explained variance sums to <= 1.0"""
        results = pca_analyzer.perform_pca(sample_yield_data)

        variance_explained = results['variance_explained']
        total_variance = sum(variance_explained)

        assert 0 < total_variance <= 1.0

    def test_variance_explained_order(self, pca_analyzer, sample_yield_data):
        """Test that variance explained is in descending order"""
        results = pca_analyzer.perform_pca(sample_yield_data)

        variance_explained = results['variance_explained']

        # Each component should explain less variance than the previous
        for i in range(len(variance_explained) - 1):
            assert variance_explained[i] >= variance_explained[i + 1]

    def test_cumulative_variance_increasing(self, pca_analyzer, sample_yield_data):
        """Test that cumulative variance is monotonically increasing"""
        results = pca_analyzer.perform_pca(sample_yield_data)

        cumulative_variance = results['cumulative_variance']

        # Should be strictly increasing
        for i in range(len(cumulative_variance) - 1):
            assert cumulative_variance[i] < cumulative_variance[i + 1]

    def test_mean_curve_calculation(self, pca_analyzer, sample_yield_data):
        """Test mean curve calculation"""
        results = pca_analyzer.perform_pca(sample_yield_data)

        mean_curve = results['mean_curve']
        yield_matrix = results['yield_matrix']

        # Mean should be close to numpy mean
        expected_mean = np.mean(yield_matrix, axis=0)
        np.testing.assert_allclose(mean_curve, expected_mean, rtol=1e-10)

    def test_maturities_extraction(self, pca_analyzer, sample_yield_data):
        """Test that maturities are correctly extracted"""
        results = pca_analyzer.perform_pca(sample_yield_data)

        # Check maturities stored
        assert pca_analyzer.maturities is not None
        assert len(pca_analyzer.maturities) > 0

        # Should match number of SR_ columns
        sr_columns = [col for col in sample_yield_data.columns if col.startswith('SR_')]
        assert len(pca_analyzer.maturities) == len(sr_columns)

    def test_reconstruct_yield_curve(self, pca_analyzer, sample_yield_data):
        """Test yield curve reconstruction from PCA scores"""
        results = pca_analyzer.perform_pca(sample_yield_data)
        scores = results['scores']

        # Reconstruct using first 3 components
        reconstructed = pca_analyzer.reconstruct_yield_curve(scores, n_components=3)

        # Shape should match original
        assert reconstructed.shape[0] == len(sample_yield_data)
        assert reconstructed.shape[1] == len(pca_analyzer.maturities)

    def test_reconstruct_without_fit_raises_error(self, pca_analyzer):
        """Test that reconstruction without fitting raises error"""
        dummy_scores = np.random.randn(10, 3)

        with pytest.raises(ValueError) as exc_info:
            pca_analyzer.reconstruct_yield_curve(dummy_scores, n_components=3)

        assert "PCA must be fitted" in str(exc_info.value)

    def test_reconstruction_accuracy(self, pca_analyzer, sample_yield_data):
        """Test accuracy of reconstruction with all components"""
        results = pca_analyzer.perform_pca(sample_yield_data)
        scores = results['scores']
        original = results['yield_matrix']

        # Reconstruct with all components
        n_comp = min(5, scores.shape[1])
        reconstructed = pca_analyzer.reconstruct_yield_curve(scores, n_components=n_comp)

        # With all components, reconstruction should be very close
        # Allow for numerical precision errors
        mean_error = np.mean(np.abs(original - reconstructed))
        assert mean_error < 0.01  # Less than 1bp average error

    def test_yield_curve_plot_format(self, pca_analyzer, sample_yield_data):
        """Test that yield curve plot is valid JSON"""
        results = pca_analyzer.perform_pca(sample_yield_data)
        plot_json = results['yield_curve_plot']

        # Should be valid JSON
        plot_data = json.loads(plot_json)
        assert 'data' in plot_data
        assert 'layout' in plot_data

    def test_pc_plot_format(self, pca_analyzer, sample_yield_data):
        """Test that principal components plot is valid JSON"""
        results = pca_analyzer.perform_pca(sample_yield_data)
        plot_json = results['pc_plot']

        # Should be valid JSON
        plot_data = json.loads(plot_json)
        assert 'data' in plot_data
        assert 'layout' in plot_data

    def test_variance_plot_format(self, pca_analyzer, sample_yield_data):
        """Test that variance plot is valid JSON"""
        results = pca_analyzer.perform_pca(sample_yield_data)
        plot_json = results['variance_plot']

        # Should be valid JSON
        plot_data = json.loads(plot_json)
        assert 'data' in plot_data
        assert 'layout' in plot_data

    def test_pca_with_small_dataset(self, pca_analyzer, small_yield_data):
        """Test PCA with small dataset"""
        results = pca_analyzer.perform_pca(small_yield_data)

        # Should still work
        assert results is not None
        assert 'scores' in results
        assert 'variance_explained' in results

    def test_first_pc_explains_most_variance(self, pca_analyzer, sample_yield_data):
        """Test that first PC explains most variance (typical for yield curves)"""
        results = pca_analyzer.perform_pca(sample_yield_data)

        variance_explained = results['variance_explained']

        # First PC should explain majority of variance (typically >90% for yield curves)
        assert variance_explained[0] > 0.5  # At least 50%

    def test_first_three_pcs_high_variance(self, pca_analyzer, sample_yield_data):
        """Test that first 3 PCs explain high cumulative variance"""
        results = pca_analyzer.perform_pca(sample_yield_data)

        cumulative_variance = results['cumulative_variance']

        # First 3 PCs should explain most variance for yield curves
        assert cumulative_variance[2] > 0.9  # At least 90%

    def test_scores_uncorrelated(self, pca_analyzer, sample_yield_data):
        """Test that PCA scores are uncorrelated (by construction)"""
        results = pca_analyzer.perform_pca(sample_yield_data)
        scores = results['scores']

        # Calculate correlation matrix
        correlation = np.corrcoef(scores, rowvar=False)

        # Off-diagonal elements should be close to zero
        np.fill_diagonal(correlation, 0)
        max_correlation = np.max(np.abs(correlation))

        # Allow for numerical precision
        assert max_correlation < 0.01

    def test_dates_preserved(self, pca_analyzer, sample_yield_data):
        """Test that dates are correctly preserved"""
        results = pca_analyzer.perform_pca(sample_yield_data)
        dates = results['dates']

        # Should have same number of dates
        assert len(dates) == len(sample_yield_data)

        # Should be datetime type
        assert isinstance(dates[0], pd.Timestamp)


@pytest.mark.unit
class TestPCAEdgeCases:
    """Test edge cases for PCA analysis"""

    def test_minimum_observations(self):
        """Test PCA with minimum number of observations"""
        # Create minimal dataset
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        data = np.random.randn(10, 5) * 0.5 + 2.0
        df = pd.DataFrame(data, columns=['SR_1Y', 'SR_2Y', 'SR_5Y', 'SR_10Y', 'SR_30Y'])
        df.insert(0, 'Date', dates)

        analyzer = PCAAnalyzer(n_components=3)
        results = analyzer.perform_pca(df)

        # Should still work
        assert results is not None

    def test_more_components_than_features(self):
        """Test PCA when requesting more components than features"""
        # Create dataset with few features
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        data = np.random.randn(50, 3) * 0.5 + 2.0
        df = pd.DataFrame(data, columns=['SR_1Y', 'SR_5Y', 'SR_10Y'])
        df.insert(0, 'Date', dates)

        # Request more components than features
        analyzer = PCAAnalyzer(n_components=5)
        results = analyzer.perform_pca(df)

        # Should cap at number of features
        assert results['scores'].shape[1] <= 3

    def test_constant_maturity(self):
        """Test PCA when one maturity is constant"""
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        data = np.random.randn(50, 4) * 0.5 + 2.0

        # Make one column constant
        data[:, 2] = 2.0

        df = pd.DataFrame(data, columns=['SR_1Y', 'SR_2Y', 'SR_5Y', 'SR_10Y'])
        df.insert(0, 'Date', dates)

        analyzer = PCAAnalyzer(n_components=3)
        results = analyzer.perform_pca(df)

        # Should still work (PCA handles this)
        assert results is not None
