"""
Pytest configuration and fixtures
Shared fixtures for all tests
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

from app import app as flask_app, cache
from services.ecb_api import ECBDataService
from services.pca_analysis import PCAAnalyzer
from services.stress_scenarios import StressScenarioGenerator


@pytest.fixture
def app():
    """Create and configure Flask app for testing"""
    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'CACHE_TYPE': 'SimpleCache',  # Use simple cache for tests
        'CACHE_DEFAULT_TIMEOUT': 0  # Disable timeout in tests
    })

    # Clear cache before each test
    with flask_app.app_context():
        cache.clear()

    yield flask_app

    # Clear cache after each test
    with flask_app.app_context():
        cache.clear()


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create Flask CLI test runner"""
    return app.test_cli_runner()


@pytest.fixture
def sample_yield_data():
    """Generate sample yield curve data for testing"""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')

    # Create 32 maturities (3M to 30Y)
    maturities = [
        'SR_3M', 'SR_6M', 'SR_1Y', 'SR_2Y', 'SR_3Y', 'SR_4Y', 'SR_5Y',
        'SR_6Y', 'SR_7Y', 'SR_8Y', 'SR_9Y', 'SR_10Y', 'SR_11Y', 'SR_12Y',
        'SR_13Y', 'SR_14Y', 'SR_15Y', 'SR_16Y', 'SR_17Y', 'SR_18Y', 'SR_19Y',
        'SR_20Y', 'SR_21Y', 'SR_22Y', 'SR_23Y', 'SR_24Y', 'SR_25Y', 'SR_26Y',
        'SR_27Y', 'SR_28Y', 'SR_29Y', 'SR_30Y'
    ]

    # Generate realistic yield curve data
    # Base curve: upward sloping with some curvature
    np.random.seed(42)
    base_curve = np.array([0.5 + i * 0.1 for i in range(len(maturities))])

    # Add random variations over time
    data = []
    for _ in range(len(dates)):
        # Random shift (level)
        level_shift = np.random.normal(0, 0.3)
        # Random slope change
        slope_shift = np.random.normal(0, 0.1) * np.arange(len(maturities))
        # Random curvature change
        curvature = np.random.normal(0, 0.05) * (np.arange(len(maturities)) ** 2)

        curve = base_curve + level_shift + slope_shift * 0.01 + curvature * 0.0001
        data.append(curve)

    df = pd.DataFrame(data, columns=maturities)
    df.insert(0, 'Date', dates)

    return df


@pytest.fixture
def small_yield_data():
    """Generate small yield curve dataset for quick tests"""
    dates = pd.date_range('2023-01-01', periods=30, freq='D')
    maturities = ['SR_1Y', 'SR_2Y', 'SR_5Y', 'SR_10Y', 'SR_30Y']

    np.random.seed(42)
    data = np.random.randn(30, 5) * 0.5 + 2.0

    df = pd.DataFrame(data, columns=maturities)
    df.insert(0, 'Date', dates)

    return df


@pytest.fixture
def ecb_service():
    """Create ECB API service instance"""
    return ECBDataService()


@pytest.fixture
def pca_analyzer():
    """Create PCA analyzer instance"""
    return PCAAnalyzer(n_components=5)


@pytest.fixture
def stress_generator():
    """Create stress scenario generator instance"""
    return StressScenarioGenerator()


@pytest.fixture
def mock_ecb_response():
    """Mock ECB API response data"""
    return {
        "dataSets": [{
            "series": {
                "0:0:0:0:0:0": {
                    "observations": {
                        "0": [1.5],
                        "1": [1.6],
                        "2": [1.55]
                    }
                },
                "0:0:0:0:0:1": {
                    "observations": {
                        "0": [2.0],
                        "1": [2.1],
                        "2": [2.05]
                    }
                }
            }
        }],
        "structure": {
            "dimensions": {
                "series": [
                    {
                        "id": "FREQ",
                        "values": [{"id": "B"}]
                    },
                    {
                        "id": "REF_AREA",
                        "values": [{"id": "U2"}]
                    },
                    {
                        "id": "CURRENCY",
                        "values": [{"id": "EUR"}]
                    },
                    {
                        "id": "PROVIDER_FM",
                        "values": [{"id": "4F"}]
                    },
                    {
                        "id": "INSTRUMENT_FM",
                        "values": [{"id": "G_N_C"}]
                    },
                    {
                        "id": "DATA_TYPE_FM",
                        "values": [
                            {"id": "SR_1Y"},
                            {"id": "SR_2Y"}
                        ]
                    }
                ],
                "observation": [
                    {
                        "id": "TIME_PERIOD",
                        "values": [
                            {"id": "2023-01-01"},
                            {"id": "2023-01-02"},
                            {"id": "2023-01-03"}
                        ]
                    }
                ]
            }
        }
    }


@pytest.fixture
def sample_pca_results(pca_analyzer, sample_yield_data):
    """Generate sample PCA results for testing"""
    return pca_analyzer.perform_pca(sample_yield_data)


@pytest.fixture
def api_request_data():
    """Sample API request data"""
    return {
        'start_date': '2020-01-01',
        'end_date': '2020-12-31'
    }


@pytest.fixture
def advanced_api_request_data():
    """Sample API request data with advanced parameters"""
    return {
        'start_date': '2020-01-01',
        'end_date': '2020-12-31',
        'n_components': 3,
        'stress_quantile': 0.99,
        'rolling_window': 12
    }
