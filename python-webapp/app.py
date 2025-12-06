"""
Flask Web Application for PCA-based Yield Curve Stress Testing
Main application file
"""

from flask import Flask, render_template, request, jsonify, send_file, make_response
from flask_caching import Cache
from datetime import datetime, timedelta
import logging
import io
import pandas as pd

from services.ecb_api import ECBDataService
from services.pca_analysis import PCAAnalyzer
from services.stress_scenarios import StressScenarioGenerator
from config import Config

# Configure logging
log_level = getattr(logging, Config.LOG_LEVEL, logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if Config.LOG_FORMAT == 'detailed' else '%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize caching
cache = Cache(app, config={
    'CACHE_TYPE': Config.CACHE_TYPE,
    'CACHE_DEFAULT_TIMEOUT': Config.CACHE_TIMEOUT
})

# Initialize services
ecb_service = ECBDataService()
pca_analyzer = PCAAnalyzer()
stress_generator = StressScenarioGenerator()


@app.route('/')
def index():
    """Render main application page"""
    return render_template('index.html')


@cache.memoize(timeout=Config.CACHE_TIMEOUT)
def _perform_analysis_cached(start_date: str, end_date: str, n_components: int = None,
                              stress_quantile: float = None, rolling_window: int = None):
    """
    Internal cached function to perform analysis
    Cache key is based on all parameters
    """
    # Use defaults from config if not specified
    n_components = n_components or Config.N_COMPONENTS
    stress_quantile = stress_quantile or Config.STRESS_QUANTILE
    rolling_window = rolling_window or Config.ROLLING_WINDOW_MONTHS

    logger.info(f"📊 Performing analysis for period {start_date} to {end_date} (PCs={n_components}, quantile={stress_quantile}, window={rolling_window})")

    # Step 1: Fetch yield curve data from ECB
    yield_data = ecb_service.fetch_yield_curve(start_date, end_date)

    if yield_data.empty:
        raise ValueError('No data available for the selected period')

    # Step 2: Perform PCA analysis with specified number of components
    pca_analyzer_custom = PCAAnalyzer(n_components=n_components)
    pca_results = pca_analyzer_custom.perform_pca(yield_data)

    # Step 3: Generate stress scenarios with custom parameters
    stress_scenarios = stress_generator.generate_scenarios(
        pca_results,
        yield_data,
        quantile=stress_quantile,
        rolling_window=rolling_window
    )

    # Step 4: Prepare response with all visualizations and data
    response_data = {
        'yield_curve': pca_results['yield_curve_plot'],
        'principal_components': pca_results['pc_plot'],
        'explained_variance': pca_results['variance_plot'],
        'stressed_scores': stress_scenarios['scores_plot'],
        'stress_scenarios': stress_scenarios['scenarios_plot'],
        'statistics': {
            'n_observations': len(yield_data),
            'date_range': {
                'start': start_date,
                'end': end_date
            },
            'variance_explained': pca_results['variance_explained']
        }
    }

    logger.info("✅ Analysis completed successfully")
    return response_data


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint
    Performs PCA analysis and generates stress scenarios
    Results are cached based on date range
    """
    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Get optional advanced parameters
        n_components = data.get('n_components')
        stress_quantile = data.get('stress_quantile')
        rolling_window = data.get('rolling_window')

        # Validate and sanitize parameters
        if n_components is not None:
            n_components = int(n_components)
            if n_components < 1 or n_components > 10:
                return jsonify({'error': 'Number of components must be between 1 and 10'}), 400

        if stress_quantile is not None:
            stress_quantile = float(stress_quantile)
            if stress_quantile < 0.5 or stress_quantile > 0.999:
                return jsonify({'error': 'Stress quantile must be between 0.5 and 0.999'}), 400

        if rolling_window is not None:
            rolling_window = int(rolling_window)
            if rolling_window < 1 or rolling_window > 120:
                return jsonify({'error': 'Rolling window must be between 1 and 120 months'}), 400

        # Validate dates
        if not start_date or not end_date:
            return jsonify({'error': 'Start and end dates are required'}), 400

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        if start >= end:
            return jsonify({'error': 'Start date must be before end date'}), 400

        logger.info(f"Analysis requested for period {start_date} to {end_date}")

        # Perform analysis (will be cached) with custom parameters
        result_data = _perform_analysis_cached(start_date, end_date, n_components, stress_quantile, rolling_window)

        response = {
            'success': True,
            'data': result_data
        }

        return jsonify(response)

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'demo_mode': ecb_service.demo_mode,
        'cache_enabled': Config.CACHE_TIMEOUT > 0,
        'cache_type': Config.CACHE_TYPE
    }

    # Optional: Check ECB API connectivity
    if Config.HEALTH_CHECK_ECB_API and not ecb_service.demo_mode:
        try:
            # Try a minimal request to ECB
            test_response = ecb_service.session.get(
                f"{Config.ECB_API_BASE_URL}/service",
                timeout=5
            )
            health_data['ecb_api_status'] = 'reachable' if test_response.status_code < 500 else 'error'
        except Exception as e:
            health_data['ecb_api_status'] = 'unreachable'
            logger.warning(f"ECB API health check failed: {str(e)}")

    return jsonify(health_data)


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the application cache (admin endpoint)"""
    try:
        cache.clear()
        logger.info("Cache cleared successfully")
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/csv', methods=['POST'])
def export_csv():
    """Export analysis results as CSV"""
    if not Config.ENABLE_EXPORT:
        return jsonify({'error': 'Export functionality is disabled'}), 403

    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'Start and end dates are required'}), 400

        logger.info(f"CSV export requested for period {start_date} to {end_date}")

        # Fetch the data (use cache if available)
        result_data = _perform_analysis_cached(start_date, end_date)

        # Get original yield data
        yield_data = ecb_service.fetch_yield_curve(start_date, end_date)

        # Create CSV output
        output = io.StringIO()
        yield_data.to_csv(output, index=False)
        output.seek(0)

        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=yield_curve_{start_date}_{end_date}.csv'
        response.headers['Content-Type'] = 'text/csv'

        logger.info("CSV export completed successfully")
        return response

    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


@app.route('/api/export/excel', methods=['POST'])
def export_excel():
    """Export analysis results as Excel with multiple sheets"""
    if not Config.ENABLE_EXPORT:
        return jsonify({'error': 'Export functionality is disabled'}), 403

    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'Start and end dates are required'}), 400

        logger.info(f"Excel export requested for period {start_date} to {end_date}")

        # Perform analysis (use cache if available)
        result_data = _perform_analysis_cached(start_date, end_date)

        # Get original yield data
        yield_data = ecb_service.fetch_yield_curve(start_date, end_date)

        # Perform PCA to get components and loadings
        pca_results = pca_analyzer.perform_pca(yield_data)

        # Create Excel workbook with multiple sheets
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Original Yield Curve Data
            yield_data.to_excel(writer, sheet_name='Yield Curve Data', index=False)

            # Sheet 2: Principal Components (Factor Loadings)
            pc_loadings = pca_results['pca_model'].components_.T
            pc_df = pd.DataFrame(
                pc_loadings,
                columns=[f'PC{i+1}' for i in range(pc_loadings.shape[1])],
                index=yield_data.columns[1:]  # Exclude Date column
            )
            pc_df.index.name = 'Maturity'
            pc_df.to_excel(writer, sheet_name='Principal Components')

            # Sheet 3: Explained Variance
            variance_df = pd.DataFrame({
                'Component': [f'PC{i+1}' for i in range(len(pca_results['variance_explained']))],
                'Explained Variance': pca_results['variance_explained'],
                'Cumulative Variance': pca_results['cumulative_variance']
            })
            variance_df.to_excel(writer, sheet_name='Explained Variance', index=False)

            # Sheet 4: PCA Scores (transformed data)
            scores_df = pd.DataFrame(
                pca_results['pca_model'].transform(yield_data.iloc[:, 1:]),
                columns=[f'PC{i+1}' for i in range(pca_results['pca_model'].n_components_)]
            )
            scores_df.insert(0, 'Date', yield_data['Date'].values)
            scores_df.to_excel(writer, sheet_name='PCA Scores', index=False)

            # Sheet 5: Summary Statistics
            stats_df = pd.DataFrame({
                'Metric': ['Start Date', 'End Date', 'Number of Observations',
                          'PC1 Variance Explained', 'PC1-3 Cumulative Variance'],
                'Value': [
                    start_date,
                    end_date,
                    len(yield_data),
                    f"{pca_results['variance_explained'][0]*100:.2f}%",
                    f"{sum(pca_results['variance_explained'][:3])*100:.2f}%"
                ]
            })
            stats_df.to_excel(writer, sheet_name='Summary', index=False)

        output.seek(0)

        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=pca_analysis_{start_date}_{end_date}.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        logger.info("Excel export completed successfully")
        return response

    except Exception as e:
        logger.error(f"Error exporting Excel: {str(e)}", exc_info=True)
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # This is only used for local development
    # Passenger will use passenger_wsgi.py
    logger.info(f"Starting Flask application in {'DEMO' if Config.DEMO_MODE else 'PRODUCTION'} mode")
    logger.info(f"Caching: {Config.CACHE_TYPE} (timeout: {Config.CACHE_TIMEOUT}s)")
    app.run(debug=Config.DEBUG, host=Config.SERVER_HOST, port=Config.SERVER_PORT)
