"""
Configuration for the PCA Yield Curve Application
Loads settings from environment variables with sensible defaults
"""

import os
from datetime import datetime


def get_bool_env(key: str, default: bool = False) -> bool:
    """Parse boolean environment variable"""
    value = os.environ.get(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def get_int_env(key: str, default: int) -> int:
    """Parse integer environment variable"""
    try:
        return int(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


def get_float_env(key: str, default: float) -> float:
    """Parse float environment variable"""
    try:
        return float(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


class Config:
    """Base configuration - loads from environment variables"""

    # -------------------------------------------------------------------------
    # Application Mode
    # -------------------------------------------------------------------------
    DEMO_MODE = get_bool_env('DEMO_MODE', False)
    DEBUG = get_bool_env('FLASK_DEBUG', False)

    # Flask settings
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JSON_SORT_KEYS = False

    # -------------------------------------------------------------------------
    # API Configuration
    # -------------------------------------------------------------------------
    ECB_API_TIMEOUT = get_int_env('ECB_API_TIMEOUT', 30)
    ECB_API_BASE_URL = os.environ.get('ECB_API_BASE_URL', 'https://data-api.ecb.europa.eu')
    ECB_BASE_URL = ECB_API_BASE_URL + '/service/data'  # Full URL for backward compatibility

    # Caching
    CACHE_TIMEOUT = get_int_env('CACHE_TIMEOUT', 3600)  # 1 hour default
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = CACHE_TIMEOUT

    # -------------------------------------------------------------------------
    # PCA Analysis Configuration
    # -------------------------------------------------------------------------
    N_COMPONENTS = get_int_env('N_COMPONENTS', 5)
    STRESS_QUANTILE = get_float_env('STRESS_QUANTILE', 0.995)
    ROLLING_WINDOW_MONTHS = get_int_env('ROLLING_WINDOW_MONTHS', 24)
    ROLLING_UNIT_DAYS = 30  # Fixed: days per month for calculations

    # -------------------------------------------------------------------------
    # Logging Configuration
    # -------------------------------------------------------------------------
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = os.environ.get('LOG_FORMAT', 'simple')
    LOG_FILE = os.environ.get('LOG_FILE', None)

    # -------------------------------------------------------------------------
    # Server Configuration
    # -------------------------------------------------------------------------
    SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = get_int_env('SERVER_PORT', 5000)
    MAX_WORKERS = get_int_env('MAX_WORKERS', 4)
    REQUEST_TIMEOUT = get_int_env('REQUEST_TIMEOUT', 120)

    # -------------------------------------------------------------------------
    # Data Configuration
    # -------------------------------------------------------------------------
    DEMO_DATA_PATH = os.environ.get('DEMO_DATA_PATH', 'demo_data/sample_yield_curve.csv')
    MIN_DATE = os.environ.get('MIN_DATE', '2000-01-01')
    MAX_DATE = os.environ.get('MAX_DATE', '2099-12-31')
    MIN_DATE_RANGE_DAYS = get_int_env('MIN_DATE_RANGE_DAYS', 30)

    # Application settings (backward compatibility)
    MAX_DATE_RANGE_DAYS = 3650  # ~10 years max
    MIN_OBSERVATIONS = MIN_DATE_RANGE_DAYS  # Minimum required for PCA

    # -------------------------------------------------------------------------
    # Security Configuration
    # -------------------------------------------------------------------------
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if os.environ.get('CORS_ALLOWED_ORIGINS') else []
    RATE_LIMIT = get_int_env('RATE_LIMIT', 60)  # requests per minute

    # -------------------------------------------------------------------------
    # Feature Flags
    # -------------------------------------------------------------------------
    ENABLE_EXPORT = get_bool_env('ENABLE_EXPORT', True)
    ENABLE_PDF_EXPORT = get_bool_env('ENABLE_PDF_EXPORT', False)
    ENABLE_ADVANCED_CONFIG = get_bool_env('ENABLE_ADVANCED_CONFIG', False)

    # -------------------------------------------------------------------------
    # Monitoring & Health Checks
    # -------------------------------------------------------------------------
    HEALTH_CHECK_ENABLED = get_bool_env('HEALTH_CHECK_ENABLED', True)
    HEALTH_CHECK_ECB_API = get_bool_env('HEALTH_CHECK_ECB_API', False)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
