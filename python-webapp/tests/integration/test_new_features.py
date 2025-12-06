"""
Tests for new features: Export, Caching, Advanced Parameters
"""

import pytest
import json
import io
from unittest.mock import patch, MagicMock


class TestExportEndpoints:
    """Test CSV and Excel export functionality"""

    def test_csv_export_success(self, client, sample_yield_data):
        """Test successful CSV export"""
        with patch('app.ecb_service.fetch_yield_curve') as mock_fetch:
            mock_fetch.return_value = sample_yield_data

            response = client.post('/api/export/csv',
                                   data=json.dumps({
                                       'start_date': '2020-01-01',
                                       'end_date': '2020-12-31'
                                   }),
                                   content_type='application/json')

            assert response.status_code == 200
            assert response.headers['Content-Type'] == 'text/csv'
            assert 'attachment' in response.headers['Content-Disposition']
            assert '.csv' in response.headers['Content-Disposition']

    def test_csv_export_missing_dates(self, client):
        """Test CSV export with missing dates"""
        response = client.post('/api/export/csv',
                               data=json.dumps({}),
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_excel_export_success(self, client, sample_yield_data):
        """Test successful Excel export"""
        with patch('app.ecb_service.fetch_yield_curve') as mock_fetch, \
             patch('app.pca_analyzer.perform_pca') as mock_pca:

            mock_fetch.return_value = sample_yield_data

            # Mock PCA results with correct shapes
            n_maturities = len(sample_yield_data.columns) - 1  # Exclude Date column
            n_components = 5

            mock_pca_model = MagicMock()
            # components_ should be (n_components, n_features)
            # After transpose, it's (n_features, n_components) = (32, 5)
            import numpy as np
            mock_pca_model.components_ = np.random.randn(n_components, n_maturities)
            mock_pca_model.n_components_ = n_components
            # transform returns (n_observations, n_components) = (100, 5)
            mock_pca_model.transform.return_value = np.random.randn(len(sample_yield_data), n_components)

            mock_pca.return_value = {
                'pca_model': mock_pca_model,
                'variance_explained': [0.95, 0.03, 0.01, 0.005, 0.005],
                'cumulative_variance': [0.95, 0.98, 0.99, 0.995, 1.0]
            }

            response = client.post('/api/export/excel',
                                   data=json.dumps({
                                       'start_date': '2020-01-01',
                                       'end_date': '2020-12-31'
                                   }),
                                   content_type='application/json')

            assert response.status_code == 200
            assert 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in response.headers['Content-Type']
            assert 'attachment' in response.headers['Content-Disposition']
            assert '.xlsx' in response.headers['Content-Disposition']

    def test_excel_export_missing_dates(self, client):
        """Test Excel export with missing dates"""
        response = client.post('/api/export/excel',
                               data=json.dumps({'start_date': '2020-01-01'}),
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestAdvancedParameters:
    """Test advanced parameter configuration"""

    def test_analyze_with_custom_n_components(self, client, sample_yield_data):
        """Test analysis with custom number of components"""
        with patch('app.ecb_service.fetch_yield_curve') as mock_fetch:
            mock_fetch.return_value = sample_yield_data

            response = client.post('/api/analyze',
                                   data=json.dumps({
                                       'start_date': '2020-01-01',
                                       'end_date': '2020-12-31',
                                       'n_components': 3
                                   }),
                                   content_type='application/json')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

    def test_analyze_with_custom_stress_quantile(self, client, sample_yield_data):
        """Test analysis with custom stress quantile"""
        with patch('app.ecb_service.fetch_yield_curve') as mock_fetch:
            mock_fetch.return_value = sample_yield_data

            response = client.post('/api/analyze',
                                   data=json.dumps({
                                       'start_date': '2020-01-01',
                                       'end_date': '2020-12-31',
                                       'stress_quantile': 0.99
                                   }),
                                   content_type='application/json')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

    def test_analyze_with_custom_rolling_window(self, client, sample_yield_data):
        """Test analysis with custom rolling window"""
        with patch('app.ecb_service.fetch_yield_curve') as mock_fetch:
            mock_fetch.return_value = sample_yield_data

            response = client.post('/api/analyze',
                                   data=json.dumps({
                                       'start_date': '2020-01-01',
                                       'end_date': '2020-12-31',
                                       'rolling_window': 12
                                   }),
                                   content_type='application/json')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

    def test_analyze_with_all_advanced_params(self, client, sample_yield_data, advanced_api_request_data):
        """Test analysis with all advanced parameters"""
        with patch('app.ecb_service.fetch_yield_curve') as mock_fetch:
            mock_fetch.return_value = sample_yield_data

            response = client.post('/api/analyze',
                                   data=json.dumps(advanced_api_request_data),
                                   content_type='application/json')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

    def test_invalid_n_components_too_low(self, client):
        """Test analysis with invalid n_components (too low)"""
        response = client.post('/api/analyze',
                               data=json.dumps({
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31',
                                   'n_components': 0
                               }),
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'components must be between 1 and 10' in data['error']

    def test_invalid_n_components_too_high(self, client):
        """Test analysis with invalid n_components (too high)"""
        response = client.post('/api/analyze',
                               data=json.dumps({
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31',
                                   'n_components': 15
                               }),
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'components must be between 1 and 10' in data['error']

    def test_invalid_stress_quantile_too_low(self, client):
        """Test analysis with invalid stress_quantile (too low)"""
        response = client.post('/api/analyze',
                               data=json.dumps({
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31',
                                   'stress_quantile': 0.3
                               }),
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'quantile must be between' in data['error']

    def test_invalid_stress_quantile_too_high(self, client):
        """Test analysis with invalid stress_quantile (too high)"""
        response = client.post('/api/analyze',
                               data=json.dumps({
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31',
                                   'stress_quantile': 1.5
                               }),
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'quantile must be between' in data['error']

    def test_invalid_rolling_window_too_low(self, client):
        """Test analysis with invalid rolling_window (too low)"""
        response = client.post('/api/analyze',
                               data=json.dumps({
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31',
                                   'rolling_window': 0
                               }),
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Rolling window must be between' in data['error']

    def test_invalid_rolling_window_too_high(self, client):
        """Test analysis with invalid rolling_window (too high)"""
        response = client.post('/api/analyze',
                               data=json.dumps({
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31',
                                   'rolling_window': 150
                               }),
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Rolling window must be between' in data['error']


class TestCacheEndpoint:
    """Test cache management endpoint"""

    def test_clear_cache_success(self, client):
        """Test successful cache clearing"""
        response = client.post('/api/cache/clear')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'message' in data


class TestHealthCheckEnhancements:
    """Test enhanced health check endpoint"""

    def test_health_check_includes_demo_mode(self, client):
        """Test health check includes demo_mode status"""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'demo_mode' in data
        assert isinstance(data['demo_mode'], bool)

    def test_health_check_includes_cache_info(self, client):
        """Test health check includes cache information"""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'cache_enabled' in data
        assert 'cache_type' in data
        assert isinstance(data['cache_enabled'], bool)
