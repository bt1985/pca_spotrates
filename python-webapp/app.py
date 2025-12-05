"""
Flask Web Application for PCA-based Yield Curve Stress Testing
Main application file
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import logging

from services.ecb_api import ECBDataService
from services.pca_analysis import PCAAnalyzer
from services.stress_scenarios import StressScenarioGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JSON_SORT_KEYS'] = False

# Initialize services
ecb_service = ECBDataService()
pca_analyzer = PCAAnalyzer()
stress_generator = StressScenarioGenerator()


@app.route('/')
def index():
    """Render main application page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint
    Performs PCA analysis and generates stress scenarios
    """
    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')

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

        # Step 1: Fetch yield curve data from ECB
        yield_data = ecb_service.fetch_yield_curve(start_date, end_date)

        if yield_data.empty:
            return jsonify({'error': 'No data available for the selected period'}), 404

        # Step 2: Perform PCA analysis
        pca_results = pca_analyzer.perform_pca(yield_data)

        # Step 3: Generate stress scenarios
        stress_scenarios = stress_generator.generate_scenarios(
            pca_results,
            yield_data,
            quantile=0.995,
            rolling_window=24
        )

        # Step 4: Prepare response with all visualizations and data
        response = {
            'success': True,
            'data': {
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
        }

        logger.info("Analysis completed successfully")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


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
    app.run(debug=True, host='0.0.0.0', port=5000)
