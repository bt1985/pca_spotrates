"""
Configuration for the PCA Yield Curve Application
"""

import os


class Config:
    """Base configuration"""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JSON_SORT_KEYS = False

    # PCA settings
    N_COMPONENTS = 5
    STRESS_QUANTILE = 0.995
    ROLLING_WINDOW_MONTHS = 24
    ROLLING_UNIT_DAYS = 30

    # ECB API settings
    ECB_BASE_URL = "https://sdw-wsrest.ecb.europa.eu/service/data"
    REQUEST_TIMEOUT = 30

    # Application settings
    MAX_DATE_RANGE_DAYS = 3650  # ~10 years max
    MIN_OBSERVATIONS = 30  # Minimum required for PCA


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
