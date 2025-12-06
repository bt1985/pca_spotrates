"""
Simple test script to verify the application works
Run this locally before deploying to Netcup
"""

import sys
from datetime import datetime, timedelta


def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        from flask import Flask
        from services.ecb_api import ECBDataService
        from services.pca_analysis import PCAAnalyzer
        from services.stress_scenarios import StressScenarioGenerator
        import numpy
        import pandas
        import sklearn
        import plotly
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_ecb_api():
    """Test ECB API connectivity"""
    print("\nTesting ECB API...")
    try:
        from services.ecb_api import ECBDataService

        service = ECBDataService()

        # Test with a small date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        print(f"Fetching data from {start_date} to {end_date}...")
        df = service.fetch_yield_curve(start_date, end_date)

        if df.empty:
            print("⚠️  No data returned (ECB might not have recent data)")
            return True  # Not a failure, just no data

        print(f"✅ Successfully fetched {len(df)} observations")
        print(f"   Columns: {list(df.columns)[:5]}... ({len(df.columns)} total)")
        return True

    except Exception as e:
        print(f"❌ ECB API test failed: {e}")
        return False


def test_pca_analysis():
    """Test PCA analysis with dummy data"""
    print("\nTesting PCA analysis...")
    try:
        import numpy as np
        import pandas as pd
        from services.pca_analysis import PCAAnalyzer

        # Create dummy yield curve data
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        maturities = [f'SR_{i}Y' for i in range(1, 11)]

        # Random yield curves
        np.random.seed(42)
        data = np.random.randn(100, 10) * 0.5 + 2.0  # Mean ~2%, std ~0.5%

        df = pd.DataFrame(data, columns=maturities)
        df.insert(0, 'Date', dates)

        analyzer = PCAAnalyzer(n_components=5)
        results = analyzer.perform_pca(df)

        print(f"✅ PCA analysis successful")
        print(f"   Variance explained by PC1: {results['variance_explained'][0]:.2%}")
        print(f"   Cumulative variance (PC1-3): {results['cumulative_variance'][2]:.2%}")
        return True

    except Exception as e:
        print(f"❌ PCA analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flask_app():
    """Test Flask application"""
    print("\nTesting Flask app...")
    try:
        from app import app

        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ Flask app runs successfully")
                print(f"   Health check: {response.json}")
                return True
            else:
                print(f"❌ Flask app health check failed: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("PCA Yield Curve App - Test Suite")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("ECB API", test_ecb_api()))
    results.append(("PCA Analysis", test_pca_analysis()))
    results.append(("Flask App", test_flask_app()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20s}: {status}")

    all_passed = all(result for _, result in results)

    print("=" * 60)
    if all_passed:
        print("✅ All tests passed! Ready for deployment.")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before deploying.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
