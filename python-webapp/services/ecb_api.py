"""
ECB Data Service
Fetches yield curve data from the European Central Bank Statistical Data Warehouse
"""

import requests
import pandas as pd
from datetime import datetime
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class ECBDataService:
    """Service to fetch yield curve data from ECB Data Portal API"""

    BASE_URL = "https://data-api.ecb.europa.eu/service/data"

    # ECB yield curve key for Euro area AAA-rated government bonds
    # Spot rates for maturities 3M to 30Y
    MATURITIES = [
        "SR_3M", "SR_6M", "SR_1Y", "SR_2Y", "SR_3Y", "SR_4Y", "SR_5Y",
        "SR_6Y", "SR_7Y", "SR_8Y", "SR_9Y", "SR_10Y", "SR_11Y", "SR_12Y",
        "SR_13Y", "SR_14Y", "SR_15Y", "SR_16Y", "SR_17Y", "SR_18Y", "SR_19Y",
        "SR_20Y", "SR_21Y", "SR_22Y", "SR_23Y", "SR_24Y", "SR_25Y", "SR_26Y",
        "SR_27Y", "SR_28Y", "SR_29Y", "SR_30Y"
    ]

    def __init__(self, demo_mode=None):
        """
        Initialize ECB Data Service

        Args:
            demo_mode: Use demo data instead of ECB API (default: from environment)
        """
        # Check demo mode from environment or parameter
        if demo_mode is None:
            demo_mode = os.environ.get('DEMO_MODE', 'false').lower() == 'true'

        self.demo_mode = demo_mode
        self.demo_data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'demo_data',
            'sample_yield_curve.csv'
        )

        if self.demo_mode:
            logger.info("🎭 DEMO MODE: Using sample data instead of ECB API")
        else:
            self.session = requests.Session()
            self.session.headers.update({
                'Accept': 'application/json',
                'User-Agent': 'PCA-Yield-Curve-App/1.0'
            })

    def fetch_yield_curve(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch yield curve data from ECB for the specified date range

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with dates as index and maturities as columns
        """
        # Use demo data if in demo mode
        if self.demo_mode:
            return self._fetch_demo_data(start_date, end_date)

        try:
            # Build the data key for all maturities
            maturities_str = "+".join(self.MATURITIES)
            data_key = f"YC/B.U2.EUR.4F.G_N_C.SV_C_YM.{maturities_str}"

            # Build the URL with parameters
            url = f"{self.BASE_URL}/{data_key}"
            params = {
                'startPeriod': start_date,
                'endPeriod': end_date,
                'format': 'jsondata'
            }

            logger.info(f"Fetching data from ECB: {start_date} to {end_date}")

            # Make the request
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Extract the data structure
            if 'dataSets' not in data or len(data['dataSets']) == 0:
                logger.warning("No data returned from ECB API")
                return pd.DataFrame()

            # Parse the ECB JSON structure
            df = self._parse_ecb_response(data)

            logger.info(f"Successfully fetched {len(df)} observations")
            return df

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from ECB: {str(e)}")
            raise Exception(f"Failed to fetch data from ECB: {str(e)}")

    def _parse_ecb_response(self, data: dict) -> pd.DataFrame:
        """
        Parse the ECB JSON response into a DataFrame

        Args:
            data: Raw JSON response from ECB API

        Returns:
            DataFrame with parsed yield curve data
        """
        try:
            # Extract dimensions and series
            structure = data.get('structure', {})
            dimensions = structure.get('dimensions', {}).get('series', [])
            dataset = data['dataSets'][0]

            # Find dimension indices
            maturity_idx = None
            for i, dim in enumerate(dimensions):
                if dim.get('id') == 'DATA_TYPE_FM':
                    maturity_idx = i
                    break

            if maturity_idx is None:
                raise ValueError("Could not find maturity dimension in ECB response")

            # Extract maturity labels
            maturity_values = dimensions[maturity_idx]['values']
            maturity_map = {i: val['id'] for i, val in enumerate(maturity_values)}

            # Extract time dimension
            obs_dimension = data['structure']['dimensions']['observation'][0]
            time_values = obs_dimension['values']
            time_map = {i: val['id'] for i, val in enumerate(time_values)}

            # Parse series data
            records = []
            series_data = dataset.get('series', {})

            for series_key, series_value in series_data.items():
                # Parse series key (e.g., "0:0:0:0:0:X" where X is maturity index)
                key_parts = series_key.split(':')
                mat_idx = int(key_parts[maturity_idx])
                maturity = maturity_map.get(mat_idx, f'SR_UNKNOWN_{mat_idx}')

                # Parse observations
                observations = series_value.get('observations', {})
                for obs_key, obs_value in observations.items():
                    time_idx = int(obs_key)
                    date_str = time_map.get(time_idx)
                    value = obs_value[0] if isinstance(obs_value, list) else obs_value

                    if date_str and value is not None:
                        records.append({
                            'Date': date_str,
                            'Maturity': maturity,
                            'Value': float(value)
                        })

            # Convert to DataFrame
            df = pd.DataFrame(records)

            if df.empty:
                return df

            # Pivot to wide format
            df_pivot = df.pivot(index='Date', columns='Maturity', values='Value')

            # Sort by date
            df_pivot.index = pd.to_datetime(df_pivot.index)
            df_pivot = df_pivot.sort_index()

            # Reorder columns to match expected maturity order
            existing_cols = [col for col in self.MATURITIES if col in df_pivot.columns]
            df_pivot = df_pivot[existing_cols]

            # Reset index to have Date as column
            df_pivot = df_pivot.reset_index()
            df_pivot.rename(columns={'index': 'Date'}, inplace=True)

            return df_pivot

        except Exception as e:
            logger.error(f"Error parsing ECB response: {str(e)}")
            raise Exception(f"Failed to parse ECB data: {str(e)}")

    def _fetch_demo_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch demo data from CSV file

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            DataFrame with dates and yield curve data
        """
        try:
            logger.info(f"📊 Loading demo data from {self.demo_data_path}")

            # Load demo data
            df = pd.read_csv(self.demo_data_path)

            # Convert Date column to datetime
            df['Date'] = pd.to_datetime(df['Date'])

            # Filter by date range
            mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
            df_filtered = df[mask].copy()

            # Convert Date back to string format for consistency
            df_filtered['Date'] = df_filtered['Date'].dt.strftime('%Y-%m-%d')

            logger.info(f"✅ Loaded {len(df_filtered)} observations from demo data")

            return df_filtered

        except Exception as e:
            logger.error(f"Error loading demo data: {str(e)}")
            raise Exception(f"Failed to load demo data: {str(e)}")

    def get_latest_available_date(self) -> Optional[str]:
        """
        Get the latest available date in the ECB database

        Returns:
            Latest date as string in YYYY-MM-DD format, or None if unavailable
        """
        try:
            # Fetch last 5 days to find the most recent available data
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - pd.Timedelta(days=5)).strftime('%Y-%m-%d')

            df = self.fetch_yield_curve(start_date, end_date)

            if not df.empty:
                latest = df['Date'].max()
                return latest.strftime('%Y-%m-%d')

            return None

        except Exception as e:
            logger.error(f"Error getting latest date: {str(e)}")
            return None
