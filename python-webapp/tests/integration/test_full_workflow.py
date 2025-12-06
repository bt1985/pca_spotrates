"""
End-to-end integration tests
Tests complete workflows with all components integrated
"""

import pytest
import json
from unittest.mock import patch

from services.ecb_api import ECBDataService
from services.pca_analysis import PCAAnalyzer
from services.stress_scenarios import StressScenarioGenerator


@pytest.mark.integration
@pytest.mark.slow
class TestFullPCAWorkflow:
    """Test complete PCA analysis workflow"""

    def test_complete_pca_pipeline(self, sample_yield_data):
        """Test complete pipeline: data -> PCA -> stress scenarios"""

        # Step 1: PCA Analysis
        analyzer = PCAAnalyzer(n_components=5)
        pca_results = analyzer.perform_pca(sample_yield_data)

        assert pca_results is not None
        assert 'scores' in pca_results
        assert 'variance_explained' in pca_results

        # Step 2: Stress Scenario Generation
        generator = StressScenarioGenerator()
        stress_results = generator.generate_scenarios(
            pca_results,
            sample_yield_data
        )

        assert stress_results is not None
        assert 'scenarios' in stress_results
        assert 'PC1' in stress_results['scenarios']
        assert 'PC2' in stress_results['scenarios']
        assert 'PC3' in stress_results['scenarios']

    def test_pca_to_stress_scenarios_consistency(self, sample_yield_data):
        """Test consistency between PCA and stress scenarios"""

        # Perform PCA
        analyzer = PCAAnalyzer(n_components=5)
        pca_results = analyzer.perform_pca(sample_yield_data)

        # Generate stress scenarios
        generator = StressScenarioGenerator()
        stress_results = generator.generate_scenarios(
            pca_results,
            sample_yield_data
        )

        # Number of maturities should match
        n_maturities = len([col for col in sample_yield_data.columns if col.startswith('SR_')])

        for pc in ['PC1', 'PC2', 'PC3']:
            scenario = stress_results['scenarios'][pc]
            assert len(scenario['original']) == n_maturities
            assert len(scenario['up']) == n_maturities
            assert len(scenario['down']) == n_maturities

    def test_variance_explained_high_for_yield_curves(self, sample_yield_data):
        """Test that first few PCs explain most variance (typical for yield curves)"""

        analyzer = PCAAnalyzer(n_components=5)
        pca_results = analyzer.perform_pca(sample_yield_data)

        variance_explained = pca_results['variance_explained']
        cumulative_variance = pca_results['cumulative_variance']

        # First PC should explain significant variance
        assert variance_explained[0] > 0.5  # At least 50%

        # First 3 PCs should explain most variance
        assert cumulative_variance[2] > 0.9  # At least 90%


@pytest.mark.integration
class TestAPIWorkflow:
    """Test complete API workflow with mocked ECB"""

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_api_request_to_response(self, mock_fetch, client, sample_yield_data):
        """Test complete API request to response flow"""

        # Mock ECB data
        mock_fetch.return_value = sample_yield_data

        # Make API request
        response = client.post('/api/analyze',
                               json={
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31'
                               },
                               content_type='application/json')

        # Verify response structure
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True

        # Verify all components are present
        result_data = data['data']
        required_keys = [
            'yield_curve',
            'principal_components',
            'explained_variance',
            'stressed_scores',
            'stress_scenarios',
            'statistics'
        ]

        for key in required_keys:
            assert key in result_data, f"Missing key: {key}"

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_multiple_requests_consistency(self, mock_fetch, client, sample_yield_data):
        """Test that multiple requests with same data return consistent results"""

        mock_fetch.return_value = sample_yield_data

        # First request
        response1 = client.post('/api/analyze',
                                json={
                                    'start_date': '2020-01-01',
                                    'end_date': '2020-12-31'
                                },
                                content_type='application/json')

        # Second request with same parameters
        response2 = client.post('/api/analyze',
                                json={
                                    'start_date': '2020-01-01',
                                    'end_date': '2020-12-31'
                                },
                                content_type='application/json')

        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)

        # Statistics should be identical
        assert data1['data']['statistics']['n_observations'] == \
               data2['data']['statistics']['n_observations']

        # Variance explained should be the same
        assert data1['data']['statistics']['variance_explained'] == \
               data2['data']['statistics']['variance_explained']


@pytest.mark.integration
class TestDataFlow:
    """Test data flow through all components"""

    def test_yield_data_to_pca_to_plots(self, sample_yield_data):
        """Test data transformation from yield data to plots"""

        # Step 1: PCA
        analyzer = PCAAnalyzer(n_components=5)
        pca_results = analyzer.perform_pca(sample_yield_data)

        # Verify plots are generated
        assert pca_results['yield_curve_plot'] != ''
        assert pca_results['pc_plot'] != ''
        assert pca_results['variance_plot'] != ''

        # Verify plots are valid JSON
        yield_plot = json.loads(pca_results['yield_curve_plot'])
        assert 'data' in yield_plot or 'layout' in yield_plot

        pc_plot = json.loads(pca_results['pc_plot'])
        assert 'data' in pc_plot

        variance_plot = json.loads(pca_results['variance_plot'])
        assert 'data' in variance_plot

    def test_pca_to_stress_to_plots(self, sample_yield_data):
        """Test data transformation from PCA to stress plots"""

        # PCA
        analyzer = PCAAnalyzer(n_components=5)
        pca_results = analyzer.perform_pca(sample_yield_data)

        # Stress scenarios
        generator = StressScenarioGenerator()
        stress_results = generator.generate_scenarios(
            pca_results,
            sample_yield_data
        )

        # Verify plots
        assert stress_results['scores_plot'] != ''
        assert stress_results['scenarios_plot'] != ''

        # Verify valid JSON
        scores_plot = json.loads(stress_results['scores_plot'])
        assert 'data' in scores_plot

        scenarios_plot = json.loads(stress_results['scenarios_plot'])
        assert 'data' in scenarios_plot


@pytest.mark.integration
class TestErrorPropagation:
    """Test that errors propagate correctly through the system"""

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_ecb_error_propagates_to_api(self, mock_fetch, client):
        """Test that ECB API errors propagate to Flask API"""

        # Mock ECB error
        mock_fetch.side_effect = Exception("ECB API unavailable")

        # Make request
        response = client.post('/api/analyze',
                               json={
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31'
                               },
                               content_type='application/json')

        # Should return error
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

    def test_invalid_data_handled_gracefully(self, client):
        """Test that invalid input data is handled gracefully"""

        # Invalid date format
        response = client.post('/api/analyze',
                               json={
                                   'start_date': 'not-a-date',
                                   'end_date': '2020-12-31'
                               },
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Test performance characteristics"""

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_reasonable_response_time(self, mock_fetch, client, sample_yield_data):
        """Test that API responds in reasonable time"""

        import time

        mock_fetch.return_value = sample_yield_data

        start = time.time()

        response = client.post('/api/analyze',
                               json={
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31'
                               },
                               content_type='application/json')

        end = time.time()
        duration = end - start

        assert response.status_code == 200

        # Should complete in reasonable time (excluding actual ECB API call)
        # With mocked data, should be under 5 seconds
        assert duration < 5.0

    def test_memory_efficient_with_large_dataset(self, pca_analyzer):
        """Test memory efficiency with larger dataset"""

        import pandas as pd
        import numpy as np

        # Create larger dataset (1000 observations)
        dates = pd.date_range('2000-01-01', periods=1000, freq='D')
        maturities = [f'SR_{i}Y' for i in range(1, 31)]

        np.random.seed(42)
        data = np.random.randn(1000, 30) * 0.5 + 2.0

        df = pd.DataFrame(data, columns=maturities)
        df.insert(0, 'Date', dates)

        # Should complete without memory errors
        results = pca_analyzer.perform_pca(df)

        assert results is not None
        assert len(results['scores']) == 1000


@pytest.mark.integration
class TestRobustness:
    """Test system robustness"""

    def test_handles_missing_maturities(self):
        """Test handling of yield data with missing maturities"""

        import pandas as pd
        import numpy as np
        from services.pca_analysis import PCAAnalyzer

        # Create data with only some maturities
        dates = pd.date_range('2020-01-01', periods=50, freq='D')
        maturities = ['SR_1Y', 'SR_5Y', 'SR_10Y']  # Only 3 maturities

        data = np.random.randn(50, 3) * 0.5 + 2.0

        df = pd.DataFrame(data, columns=maturities)
        df.insert(0, 'Date', dates)

        # Use PCA analyzer with fewer components
        analyzer = PCAAnalyzer(n_components=3)
        results = analyzer.perform_pca(df)

        assert results is not None
        assert len(results['variance_explained']) <= 3

    def test_handles_data_with_nans(self, pca_analyzer):
        """Test handling of data with NaN values"""

        import pandas as pd
        import numpy as np

        dates = pd.date_range('2020-01-01', periods=50, freq='D')
        maturities = ['SR_1Y', 'SR_2Y', 'SR_5Y', 'SR_10Y']

        data = np.random.randn(50, 4) * 0.5 + 2.0

        # Introduce some NaN values
        data[10, 2] = np.nan
        data[20, 1] = np.nan

        df = pd.DataFrame(data, columns=maturities)
        df.insert(0, 'Date', dates)

        # Should handle NaN (sklearn's PCA will fail, so we expect an error)
        # This tests that errors are raised appropriately
        with pytest.raises(Exception):
            pca_analyzer.perform_pca(df)
