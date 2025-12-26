"""
Stress Scenario Generator
Generates stress scenarios for yield curves based on PCA scores
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

logger = logging.getLogger(__name__)


class StressScenarioGenerator:
    """Generates stress scenarios based on rolling quantiles of PCA scores"""

    def __init__(self):
        pass

    def generate_scenarios(
        self,
        pca_results: dict,
        yield_data: pd.DataFrame,
        quantile: float = 0.995,
        rolling_window: int = 24,
        unit: int = 30
    ) -> dict:
        """
        Generate stress scenarios based on rolling quantiles

        Args:
            pca_results: Results from PCA analysis
            yield_data: Original yield curve data
            quantile: Quantile level for stress (default 0.995 = 99.5%)
            rolling_window: Rolling window size in months (default 24)
            unit: Unit for rolling differences in days (default 30)

        Returns:
            Dictionary containing stress scenarios and visualizations
        """
        try:
            logger.info("Generating stress scenarios")

            scores = pca_results['scores']
            dates = pca_results['dates']
            pca_model = pca_results['pca_model']
            mean_curve = pca_results['mean_curve']

            # Calculate rolling differences
            df_scores = pd.DataFrame(
                scores[:, :3],
                columns=['PC1', 'PC2', 'PC3'],
                index=dates
            )
            df_scores = df_scores.sort_index()

            # Calculate monthly differences (approximate with unit days)
            rolling_diff = df_scores.diff(periods=unit)
            rolling_diff = rolling_diff.dropna()

            # Separate positive and negative differences
            rolling_diff_up = rolling_diff.copy()
            rolling_diff_up[rolling_diff_up < 0] = 0

            rolling_diff_down = rolling_diff.copy()
            rolling_diff_down[rolling_diff_down > 0] = 0

            # Calculate rolling quantiles
            window_size = rolling_window * unit
            rolling_quantile_up = rolling_diff_up.rolling(
                window=window_size,
                min_periods=1
            ).quantile(quantile)

            rolling_quantile_down = rolling_diff_down.rolling(
                window=window_size,
                min_periods=1
            ).quantile(1 - quantile)

            # Align with original scores
            valid_idx = rolling_quantile_up.index
            scores_aligned = df_scores.loc[valid_idx]

            # Calculate stressed scores
            stressed_scores_up = scores_aligned + rolling_quantile_up
            stressed_scores_down = scores_aligned + rolling_quantile_down

            # Create stressed score visualizations
            scores_plot = self._create_stressed_scores_plot(
                valid_idx,
                scores_aligned,
                stressed_scores_up,
                stressed_scores_down
            )

            # Generate stressed yield curves for the latest date
            latest_idx = valid_idx[-1]
            latest_scores = scores_aligned.loc[latest_idx].values
            latest_scores_up = stressed_scores_up.loc[latest_idx].values
            latest_scores_down = stressed_scores_down.loc[latest_idx].values

            # Get original yield curve for latest date
            maturity_cols = [col for col in yield_data.columns if col.startswith('SR_')]
            maturities = [col.replace('SR_', '') for col in maturity_cols]

            latest_date_mask = pd.to_datetime(yield_data['Date']) == latest_idx
            original_curve = yield_data.loc[latest_date_mask, maturity_cols].values.flatten()

            # Reconstruct stressed yield curves
            scenarios = {}
            for pc_num in range(1, 4):  # PC1, PC2, PC3
                scenarios[f'PC{pc_num}'] = self._generate_pc_scenario(
                    pc_num,
                    latest_scores,
                    latest_scores_up,
                    latest_scores_down,
                    pca_model,
                    mean_curve,
                    original_curve,
                    maturities
                )

            # Create combined scenario plot
            scenarios_plot = self._create_scenarios_plot(scenarios, maturities)

            return {
                'stressed_scores_up': stressed_scores_up,
                'stressed_scores_down': stressed_scores_down,
                'rolling_quantile_up': rolling_quantile_up,
                'rolling_quantile_down': rolling_quantile_down,
                'scenarios': scenarios,
                'scores_plot': scores_plot,
                'scenarios_plot': scenarios_plot,
                'latest_date': latest_idx.strftime('%Y-%m-%d')
            }

        except Exception as e:
            logger.error(f"Error generating stress scenarios: {str(e)}")
            raise

    def _generate_pc_scenario(
        self,
        pc_num: int,
        base_scores: np.ndarray,
        stressed_up: np.ndarray,
        stressed_down: np.ndarray,
        pca_model,
        mean_curve: np.ndarray,
        original_curve: np.ndarray,
        maturities: list
    ) -> dict:
        """Generate stress scenario for a specific principal component"""

        # Create modified scores (stress only one PC)
        scores_up = base_scores.copy()
        scores_up[pc_num - 1] = stressed_up[pc_num - 1]

        scores_down = base_scores.copy()
        scores_down[pc_num - 1] = stressed_down[pc_num - 1]

        # Reconstruct yield curves (using available components, max 4 as in R code)
        n_comp = min(4, pca_model.n_components_, len(base_scores))
        components = pca_model.components_[:n_comp]

        curve_up = scores_up[:n_comp] @ components + mean_curve
        curve_down = scores_down[:n_comp] @ components + mean_curve

        return {
            'original': original_curve,
            'up': curve_up,
            'down': curve_down,
            'maturities': maturities
        }

    def _create_stressed_scores_plot(
        self,
        dates,
        scores,
        scores_up,
        scores_down
    ) -> dict:
        """Create plot showing stressed scores with rolling quantiles"""
        try:
            fig = make_subplots(
                rows=3,
                cols=1,
                subplot_titles=('PC1 Stress', 'PC2 Stress', 'PC3 Stress'),
                vertical_spacing=0.1
            )

            for i, pc in enumerate(['PC1', 'PC2', 'PC3']):
                row = i + 1

                # Upper bound
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=scores_up[pc],
                        mode='lines',
                        name=f'{pc} Stress Up',
                        line=dict(color='red'),
                        legendgroup=pc,
                        showlegend=True,
                        hovertemplate='Date: %{x|%Y-%m-%d}<br>' +
                                      f'99.5% Quantile up {pc}: ' + '%{y:.4f}<br>' +
                                      '<extra></extra>'
                    ),
                    row=row,
                    col=1
                )

                # Lower bound
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=scores_down[pc],
                        mode='lines',
                        name=f'{pc} Stress Down',
                        line=dict(color='blue'),
                        fill='tonexty',
                        fillcolor='rgba(0,100,80,0.2)',
                        legendgroup=pc,
                        showlegend=True,
                        hovertemplate='Date: %{x|%Y-%m-%d}<br>' +
                                      f'99.5% Quantile down {pc}: ' + '%{y:.4f}<br>' +
                                      '<extra></extra>'
                    ),
                    row=row,
                    col=1
                )

                # Actual scores
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=scores[pc],
                        mode='lines',
                        name=f'{pc} Score',
                        line=dict(color='rgb(0,100,80)'),
                        legendgroup=pc,
                        showlegend=True,
                        hovertemplate='Date: %{x|%Y-%m-%d}<br>' +
                                      f'{pc} Score: ' + '%{y:.4f}<br>' +
                                      '<extra></extra>'
                    ),
                    row=row,
                    col=1
                )

            fig.update_layout(
                title='Stressed Scores with Rolling 99.5% Quantiles',
                height=800,
                hovermode='x unified'
            )

            return fig.to_json()

        except Exception as e:
            logger.error(f"Error creating stressed scores plot: {str(e)}")
            return {}

    def _create_scenarios_plot(self, scenarios: dict, maturities: list) -> dict:
        """Create plot showing stressed yield curve scenarios"""
        try:
            fig = make_subplots(
                rows=3,
                cols=1,
                subplot_titles=(
                    'PC1 Stress Scenario',
                    'PC2 Stress Scenario',
                    'PC3 Stress Scenario'
                ),
                vertical_spacing=0.1
            )

            for i, pc in enumerate(['PC1', 'PC2', 'PC3']):
                row = i + 1
                scenario = scenarios[pc]

                # Original curve
                fig.add_trace(
                    go.Scatter(
                        x=maturities,
                        y=scenario['original'],
                        mode='lines+markers',
                        name='Current Yield Curve',
                        line=dict(color='black'),
                        showlegend=False,
                        hovertemplate='Maturity: %{x}<br>' +
                                      'Yield: %{y:.2f}%<br>' +
                                      '<extra></extra>'
                    ),
                    row=row,
                    col=1
                )

                # Stressed up
                fig.add_trace(
                    go.Scatter(
                        x=maturities,
                        y=scenario['up'],
                        mode='lines+markers',
                        name=f'{pc} Stress Up',
                        line=dict(color='red', dash='dash'),
                        showlegend=False,
                        hovertemplate='Maturity: %{x}<br>' +
                                      'Stressed Yield Up: %{y:.2f}%<br>' +
                                      '<extra></extra>'
                    ),
                    row=row,
                    col=1
                )

                # Stressed down
                fig.add_trace(
                    go.Scatter(
                        x=maturities,
                        y=scenario['down'],
                        mode='lines+markers',
                        name=f'{pc} Stress Down',
                        line=dict(color='blue', dash='dash'),
                        showlegend=False,
                        hovertemplate='Maturity: %{x}<br>' +
                                      'Stressed Yield Down: %{y:.2f}%<br>' +
                                      '<extra></extra>'
                    ),
                    row=row,
                    col=1
                )

            fig.update_layout(
                title='Yield Curve Stress Scenarios',
                height=900,
                hovermode='x unified'
            )

            fig.update_xaxes(title_text='Maturity', row=3, col=1)
            fig.update_yaxes(title_text='Yield (%)')

            return fig.to_json()

        except Exception as e:
            logger.error(f"Error creating scenarios plot: {str(e)}")
            return {}
