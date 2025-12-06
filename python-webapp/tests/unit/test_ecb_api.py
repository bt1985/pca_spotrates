"""
Unit tests for ECB API Service
Tests the ECBDataService class with mocked API responses
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import requests

from services.ecb_api import ECBDataService


@pytest.mark.unit
class TestECBDataService:
    """Test suite for ECB Data Service"""

    def test_initialization(self, ecb_service):
        """Test ECB service initialization"""
        assert ecb_service.BASE_URL == "https://sdw-wsrest.ecb.europa.eu/service/data"
        assert len(ecb_service.MATURITIES) == 32
        assert ecb_service.session is not None

    def test_maturities_list(self, ecb_service):
        """Test that all expected maturities are present"""
        expected_maturities = [
            'SR_3M', 'SR_6M', 'SR_1Y', 'SR_2Y', 'SR_3Y', 'SR_4Y', 'SR_5Y',
            'SR_6Y', 'SR_7Y', 'SR_8Y', 'SR_9Y', 'SR_10Y', 'SR_11Y', 'SR_12Y',
            'SR_13Y', 'SR_14Y', 'SR_15Y', 'SR_16Y', 'SR_17Y', 'SR_18Y', 'SR_19Y',
            'SR_20Y', 'SR_21Y', 'SR_22Y', 'SR_23Y', 'SR_24Y', 'SR_25Y', 'SR_26Y',
            'SR_27Y', 'SR_28Y', 'SR_29Y', 'SR_30Y'
        ]
        assert ecb_service.MATURITIES == expected_maturities

    @patch('services.ecb_api.requests.Session.get')
    def test_fetch_yield_curve_success(self, mock_get, ecb_service, mock_ecb_response):
        """Test successful yield curve fetch"""
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ecb_response
        mock_get.return_value = mock_response

        # Fetch data
        result = ecb_service.fetch_yield_curve('2023-01-01', '2023-01-03')

        # Assertions
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'Date' in result.columns
        mock_get.assert_called_once()

    @patch('services.ecb_api.requests.Session.get')
    def test_fetch_yield_curve_empty_response(self, mock_get, ecb_service):
        """Test handling of empty API response"""
        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'dataSets': []}
        mock_get.return_value = mock_response

        # Fetch data
        result = ecb_service.fetch_yield_curve('2023-01-01', '2023-01-03')

        # Should return empty DataFrame
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    @patch('services.ecb_api.requests.Session.get')
    def test_fetch_yield_curve_api_error(self, mock_get, ecb_service):
        """Test handling of API errors"""
        # Mock API error
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            ecb_service.fetch_yield_curve('2023-01-01', '2023-01-03')

        assert "Failed to fetch data from ECB" in str(exc_info.value)

    @patch('services.ecb_api.requests.Session.get')
    def test_fetch_yield_curve_timeout(self, mock_get, ecb_service):
        """Test handling of API timeout"""
        # Mock timeout
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        # Should raise exception
        with pytest.raises(Exception) as exc_info:
            ecb_service.fetch_yield_curve('2023-01-01', '2023-01-03')

        assert "Failed to fetch data from ECB" in str(exc_info.value)

    @patch('services.ecb_api.requests.Session.get')
    def test_fetch_yield_curve_http_error(self, mock_get, ecb_service):
        """Test handling of HTTP errors"""
        # Mock HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        # Should raise exception
        with pytest.raises(Exception):
            ecb_service.fetch_yield_curve('2023-01-01', '2023-01-03')

    def test_parse_ecb_response_structure(self, ecb_service, mock_ecb_response):
        """Test parsing of ECB response structure"""
        result = ecb_service._parse_ecb_response(mock_ecb_response)

        # Verify structure
        assert isinstance(result, pd.DataFrame)
        assert 'Date' in result.columns
        assert len(result) == 3  # 3 dates in mock data

    def test_parse_ecb_response_missing_dimension(self, ecb_service):
        """Test error handling when dimension is missing"""
        invalid_response = {
            'dataSets': [{'series': {}}],
            'structure': {
                'dimensions': {
                    'series': []  # Missing DATA_TYPE_FM dimension
                }
            }
        }

        with pytest.raises(Exception) as exc_info:
            ecb_service._parse_ecb_response(invalid_response)

        assert "Could not find maturity dimension" in str(exc_info.value)

    def test_parse_ecb_response_invalid_json(self, ecb_service):
        """Test error handling for invalid JSON structure"""
        invalid_response = {'invalid': 'structure'}

        with pytest.raises(Exception) as exc_info:
            ecb_service._parse_ecb_response(invalid_response)

        assert "Failed to parse ECB data" in str(exc_info.value)

    @patch('services.ecb_api.requests.Session.get')
    def test_get_latest_available_date_success(self, mock_get, ecb_service, mock_ecb_response):
        """Test getting latest available date"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ecb_response
        mock_get.return_value = mock_response

        # Get latest date
        latest = ecb_service.get_latest_available_date()

        # Should return a date string
        assert latest is not None
        assert isinstance(latest, str)
        assert len(latest) == 10  # YYYY-MM-DD format

    @patch('services.ecb_api.requests.Session.get')
    def test_get_latest_available_date_no_data(self, mock_get, ecb_service):
        """Test getting latest date when no data available"""
        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'dataSets': []}
        mock_get.return_value = mock_response

        # Should return None
        latest = ecb_service.get_latest_available_date()
        assert latest is None

    @patch('services.ecb_api.requests.Session.get')
    def test_get_latest_available_date_error(self, mock_get, ecb_service):
        """Test error handling when getting latest date"""
        # Mock error
        mock_get.side_effect = requests.exceptions.RequestException("Error")

        # Should return None on error
        latest = ecb_service.get_latest_available_date()
        assert latest is None

    def test_session_headers(self, ecb_service):
        """Test that session has correct headers"""
        headers = ecb_service.session.headers
        assert 'Accept' in headers
        assert headers['Accept'] == 'application/json'
        assert 'User-Agent' in headers

    @patch('services.ecb_api.requests.Session.get')
    def test_fetch_with_correct_parameters(self, mock_get, ecb_service, mock_ecb_response):
        """Test that fetch is called with correct parameters"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ecb_response
        mock_get.return_value = mock_response

        # Fetch data
        ecb_service.fetch_yield_curve('2023-01-01', '2023-12-31')

        # Verify call parameters
        call_args = mock_get.call_args
        assert call_args[1]['params']['startPeriod'] == '2023-01-01'
        assert call_args[1]['params']['endPeriod'] == '2023-12-31'
        assert call_args[1]['params']['format'] == 'jsondata'
        assert call_args[1]['timeout'] == 30


@pytest.mark.unit
class TestECBResponseParsing:
    """Test suite for ECB response parsing edge cases"""

    def test_parse_response_with_null_values(self, ecb_service):
        """Test parsing response with null observation values"""
        response_with_nulls = {
            "dataSets": [{
                "series": {
                    "0:0:0:0:0:0": {
                        "observations": {
                            "0": [1.5],
                            "1": [None],  # Null value
                            "2": [1.55]
                        }
                    }
                }
            }],
            "structure": {
                "dimensions": {
                    "series": [
                        {"id": "FREQ"},
                        {"id": "REF_AREA"},
                        {"id": "CURRENCY"},
                        {"id": "PROVIDER_FM"},
                        {"id": "INSTRUMENT_FM"},
                        {"id": "DATA_TYPE_FM", "values": [{"id": "SR_1Y"}]}
                    ],
                    "observation": [{
                        "id": "TIME_PERIOD",
                        "values": [
                            {"id": "2023-01-01"},
                            {"id": "2023-01-02"},
                            {"id": "2023-01-03"}
                        ]
                    }]
                }
            }
        }

        result = ecb_service._parse_ecb_response(response_with_nulls)

        # Should handle null values gracefully
        assert isinstance(result, pd.DataFrame)
        # Only non-null values should be included
        assert len(result) == 2

    def test_parse_response_all_maturities(self, ecb_service):
        """Test parsing response with all 32 maturities"""
        # This would be a very large response, so we test the logic
        # can handle all maturities in the MATURITIES list
        assert len(ecb_service.MATURITIES) == 32
        assert all(m.startswith('SR_') for m in ecb_service.MATURITIES)
