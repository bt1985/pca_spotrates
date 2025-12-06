"""
Integration tests for Flask API endpoints
Tests the complete API workflow with mocked external dependencies
"""

import pytest
import json
from unittest.mock import patch, Mock
from datetime import datetime

from app import app


@pytest.mark.integration
class TestFlaskApp:
    """Test Flask application setup"""

    def test_app_exists(self, app):
        """Test that Flask app exists"""
        assert app is not None

    def test_app_is_testing(self, app):
        """Test that app is in testing mode"""
        assert app.config['TESTING'] is True

    def test_index_route(self, client):
        """Test index page loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'PCA Yield Curve' in response.data


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

    def test_health_check_timestamp_format(self, client):
        """Test that health check returns valid timestamp"""
        response = client.get('/api/health')
        data = json.loads(response.data)

        # Should be able to parse timestamp
        timestamp = data['timestamp']
        parsed_time = datetime.fromisoformat(timestamp)
        assert isinstance(parsed_time, datetime)


@pytest.mark.integration
class TestAnalyzeEndpoint:
    """Test main analyze endpoint"""

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_analyze_success(self, mock_fetch, client, sample_yield_data):
        """Test successful analysis request"""
        # Mock ECB data fetch
        mock_fetch.return_value = sample_yield_data

        # Make request
        response = client.post('/api/analyze',
                               json={
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-03-31'
                               },
                               content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['success'] is True
        assert 'data' in data

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_analyze_response_structure(self, mock_fetch, client, sample_yield_data):
        """Test that analyze response has correct structure"""
        mock_fetch.return_value = sample_yield_data

        response = client.post('/api/analyze',
                               json={
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31'
                               },
                               content_type='application/json')

        data = json.loads(response.data)['data']

        # Check all required fields
        assert 'yield_curve' in data
        assert 'principal_components' in data
        assert 'explained_variance' in data
        assert 'stressed_scores' in data
        assert 'stress_scenarios' in data
        assert 'statistics' in data

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_analyze_statistics(self, mock_fetch, client, sample_yield_data):
        """Test that statistics are included in response"""
        mock_fetch.return_value = sample_yield_data

        response = client.post('/api/analyze',
                               json={
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31'
                               },
                               content_type='application/json')

        stats = json.loads(response.data)['data']['statistics']

        assert 'n_observations' in stats
        assert 'date_range' in stats
        assert 'variance_explained' in stats

    def test_analyze_missing_dates(self, client):
        """Test analyze with missing dates"""
        response = client.post('/api/analyze',
                               json={},
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_analyze_missing_start_date(self, client):
        """Test analyze with missing start date"""
        response = client.post('/api/analyze',
                               json={'end_date': '2020-12-31'},
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_analyze_missing_end_date(self, client):
        """Test analyze with missing end date"""
        response = client.post('/api/analyze',
                               json={'start_date': '2020-01-01'},
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_analyze_invalid_date_format(self, client):
        """Test analyze with invalid date format"""
        response = client.post('/api/analyze',
                               json={
                                   'start_date': 'invalid-date',
                                   'end_date': '2020-12-31'
                               },
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Invalid date format' in data['error']

    def test_analyze_start_after_end(self, client):
        """Test analyze with start date after end date"""
        response = client.post('/api/analyze',
                               json={
                                   'start_date': '2020-12-31',
                                   'end_date': '2020-01-01'
                               },
                               content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'before end date' in data['error']

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_analyze_no_data_available(self, mock_fetch, client):
        """Test analyze when no data available"""
        # Mock empty DataFrame
        import pandas as pd
        mock_fetch.return_value = pd.DataFrame()

        response = client.post('/api/analyze',
                               json={
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-01-31'
                               },
                               content_type='application/json')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_analyze_ecb_api_error(self, mock_fetch, client):
        """Test analyze when ECB API fails"""
        # Mock API error
        mock_fetch.side_effect = Exception("ECB API Error")

        response = client.post('/api/analyze',
                               json={
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31'
                               },
                               content_type='application/json')

        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

    def test_analyze_wrong_method(self, client):
        """Test analyze endpoint with wrong HTTP method"""
        response = client.get('/api/analyze')
        assert response.status_code == 405  # Method Not Allowed

    def test_analyze_no_content_type(self, client):
        """Test analyze without content type"""
        response = client.post('/api/analyze',
                               data='{"start_date": "2020-01-01"}')
        # Should handle gracefully
        assert response.status_code in [400, 415]


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling"""

    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'error' in data

    def test_404_api_endpoint(self, client):
        """Test 404 for non-existent API endpoint"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404


@pytest.mark.integration
class TestCORS:
    """Test CORS and headers"""

    def test_json_content_type(self, client):
        """Test that API returns JSON"""
        response = client.get('/api/health')
        assert 'application/json' in response.content_type


@pytest.mark.integration
class TestAnalyzeIntegration:
    """Integration tests for complete analyze workflow"""

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_full_workflow(self, mock_fetch, client, sample_yield_data):
        """Test complete workflow from request to response"""
        mock_fetch.return_value = sample_yield_data

        # Make request
        request_data = {
            'start_date': '2020-01-01',
            'end_date': '2020-12-31'
        }

        response = client.post('/api/analyze',
                               json=request_data,
                               content_type='application/json')

        # Check response
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True

        # Verify plots are JSON
        plots = ['yield_curve', 'principal_components', 'explained_variance',
                 'stressed_scores', 'stress_scenarios']

        for plot_key in plots:
            plot_json = data['data'][plot_key]
            plot_data = json.loads(plot_json)
            assert 'data' in plot_data or 'layout' in plot_data

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_variance_explained_in_response(self, mock_fetch, client, sample_yield_data):
        """Test that variance explained is returned correctly"""
        mock_fetch.return_value = sample_yield_data

        response = client.post('/api/analyze',
                               json={
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31'
                               },
                               content_type='application/json')

        data = json.loads(response.data)
        variance = data['data']['statistics']['variance_explained']

        # Should be list of floats
        assert isinstance(variance, list)
        assert all(isinstance(v, (int, float)) for v in variance)
        assert all(0 <= v <= 1 for v in variance)

    @patch('services.ecb_api.ECBDataService.fetch_yield_curve')
    def test_date_range_in_statistics(self, mock_fetch, client, sample_yield_data):
        """Test that date range is correctly returned in statistics"""
        mock_fetch.return_value = sample_yield_data

        response = client.post('/api/analyze',
                               json={
                                   'start_date': '2020-01-01',
                                   'end_date': '2020-12-31'
                               },
                               content_type='application/json')

        data = json.loads(response.data)
        date_range = data['data']['statistics']['date_range']

        assert date_range['start'] == '2020-01-01'
        assert date_range['end'] == '2020-12-31'
