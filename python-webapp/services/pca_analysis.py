"""
PCA Analysis Service
Performs Principal Component Analysis on yield curve data
"""

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

logger = logging.getLogger(__name__)


class PCAAnalyzer:
    """Performs PCA analysis on yield curve data"""

    def __init__(self, n_components: int = 5):
        """
        Initialize PCA Analyzer

        Args:
            n_components: Number of principal components to compute
        """
        self.n_components = n_components
        self.pca = None
        self.mean_curve = None
        self.maturities = None

    def perform_pca(self, yield_data: pd.DataFrame) -> dict:
        """
        Perform PCA on yield curve data

        Args:
            yield_data: DataFrame with Date column and maturity columns

        Returns:
            Dictionary containing PCA results and visualizations
        """
        try:
            logger.info("Starting PCA analysis")

            # Extract dates and yield curve matrix
            dates = pd.to_datetime(yield_data['Date'])
            maturity_cols = [col for col in yield_data.columns if col.startswith('SR_')]
            yield_matrix = yield_data[maturity_cols].values

            # Store maturities for later use
            self.maturities = [col.replace('SR_', '') for col in maturity_cols]

            # Calculate mean and center the data
            self.mean_curve = np.mean(yield_matrix, axis=0)
            centered_data = yield_matrix - self.mean_curve

            # Perform PCA
            self.pca = PCA(n_components=self.n_components)
            scores = self.pca.fit_transform(centered_data)

            # Calculate explained variance
            variance_explained = self.pca.explained_variance_ratio_
            cumulative_variance = np.cumsum(variance_explained)

            logger.info(f"PCA completed. Variance explained by PC1-3: {cumulative_variance[2]:.2%}")

            # Create visualizations
            yield_curve_plot = self._create_yield_curve_plot(dates, yield_matrix)
            pc_plot = self._create_pc_plot()
            variance_plot = self._create_variance_plot(variance_explained, cumulative_variance)

            return {
                'pca_model': self.pca,
                'scores': scores,
                'dates': dates,
                'yield_matrix': yield_matrix,
                'mean_curve': self.mean_curve,
                'variance_explained': variance_explained.tolist(),
                'cumulative_variance': cumulative_variance.tolist(),
                'yield_curve_plot': yield_curve_plot,
                'pc_plot': pc_plot,
                'variance_plot': variance_plot
            }

        except Exception as e:
            logger.error(f"Error during PCA analysis: {str(e)}")
            raise

    def _create_yield_curve_plot(self, dates, yield_matrix) -> dict:
        """Create 3D surface plot of yield curve"""
        try:
            # Create meshgrid for 3D plot
            x = dates
            y = self.maturities
            z = yield_matrix.T

            # Custom colorscale for a more wave-like appearance
            # Blue (low) -> Cyan -> Green -> Yellow -> Red (high)
            colorscale = [
                [0.0, '#0d47a1'],   # Dark Blue
                [0.2, '#1976d2'],   # Blue
                [0.35, '#42a5f5'],  # Light Blue
                [0.5, '#4dd0e1'],   # Cyan
                [0.65, '#66bb6a'],  # Green
                [0.8, '#fdd835'],   # Yellow
                [1.0, '#f4511e']    # Red-Orange
            ]

            fig = go.Figure(data=[go.Surface(
                x=x,
                y=y,
                z=z,
                colorscale=colorscale,
                showscale=False,
                name='Spot Rates',
                hovertemplate='Date: %{x|%Y-%m-%d}<br>' +
                              'Maturity: %{y}<br>' +
                              'Spot Rate: %{z:.2f}%<br>' +
                              '<extra></extra>',
                lighting=dict(
                    ambient=0.6,
                    diffuse=0.8,
                    specular=0.3,
                    roughness=0.5,
                    fresnel=0.2
                ),
                lightposition=dict(
                    x=10000,
                    y=10000,
                    z=10000
                ),
                contours=dict(
                    z=dict(
                        show=True,
                        usecolormap=True,
                        highlightcolor="white",
                        project=dict(z=True)
                    )
                )
            )])

            fig.update_layout(
                title={
                    'text': 'Yield Curve Evolution',
                    'font': {'size': 24, 'color': '#333'}
                },
                scene=dict(
                    xaxis=dict(
                        title='Date',
                        titlefont=dict(size=16, color='#555'),
                        tickfont=dict(size=12),
                        backgroundcolor='rgb(240, 240, 240)',
                        gridcolor='white',
                        showbackground=True
                    ),
                    yaxis=dict(
                        title='Maturity',
                        titlefont=dict(size=16, color='#555'),
                        tickfont=dict(size=12),
                        backgroundcolor='rgb(240, 240, 240)',
                        gridcolor='white',
                        showbackground=True
                    ),
                    zaxis=dict(
                        title='Yield (%)',
                        titlefont=dict(size=16, color='#555'),
                        tickfont=dict(size=12),
                        backgroundcolor='rgb(245, 245, 245)',
                        gridcolor='white',
                        showbackground=True
                    ),
                    camera=dict(
                        eye=dict(x=1.8, y=-1.8, z=1.3),
                        center=dict(x=0, y=0, z=-0.1)
                    ),
                    aspectmode='manual',
                    aspectratio=dict(x=1.5, y=1, z=0.6)
                ),
                autosize=True,
                height=900,
                margin=dict(l=20, r=20, b=20, t=70),
                paper_bgcolor='white',
                plot_bgcolor='white'
            )

            return fig.to_json()

        except Exception as e:
            logger.error(f"Error creating yield curve plot: {str(e)}")
            return {}

    def _create_pc_plot(self) -> dict:
        """Create plot of principal components (factor loadings)"""
        try:
            components = self.pca.components_

            fig = go.Figure()

            # Plot first 5 PCs
            for i in range(min(5, len(components))):
                fig.add_trace(go.Scatter(
                    x=self.maturities,
                    y=components[i],
                    mode='lines+markers',
                    name=f'PC{i+1}',
                    visible=True if i < 3 else 'legendonly',
                    hovertemplate='Maturity: %{x}<br>' +
                                  f'Factor loading PC{i+1}: ' + '%{y:.4f}<br>' +
                                  '<extra></extra>'
                ))

            fig.update_layout(
                title='Principal Components (Factor Loadings)',
                xaxis_title='Maturity',
                yaxis_title='Factor Loading',
                hovermode='x unified',
                height=400
            )

            return fig.to_json()

        except Exception as e:
            logger.error(f"Error creating PC plot: {str(e)}")
            return {}

    def _create_variance_plot(self, variance_explained, cumulative_variance) -> dict:
        """Create plot showing explained variance by component"""
        try:
            pc_labels = [f'PC{i+1}' for i in range(len(variance_explained))]

            fig = go.Figure()

            # Bar plot for individual variance
            fig.add_trace(go.Bar(
                x=pc_labels,
                y=variance_explained,
                name='Individual Variance',
                marker_color='lightblue',
                hovertemplate='%{x}<br>' +
                              'Individual variance: %{y:.2%}<br>' +
                              '<extra></extra>'
            ))

            # Line plot for cumulative variance (same y-axis)
            fig.add_trace(go.Scatter(
                x=pc_labels,
                y=cumulative_variance,
                mode='lines+markers',
                name='Cumulative Variance',
                marker=dict(color='red', size=10),
                line=dict(color='red', width=3),
                hovertemplate='%{x}<br>' +
                              'Cumulative variance: %{y:.2%}<br>' +
                              '<extra></extra>'
            ))

            fig.update_layout(
                title='Explained Variance by Principal Component',
                xaxis_title='Principal Component',
                yaxis=dict(
                    title='Variance Explained (%)',
                    tickformat='.0%',
                    range=[0, 1.05]  # Add 5% padding at top to prevent cutoff
                ),
                hovermode='x unified',
                height=450,  # Slightly taller for better visibility
                showlegend=True,
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                )
            )

            return fig.to_json()

        except Exception as e:
            logger.error(f"Error creating variance plot: {str(e)}")
            return {}

    def reconstruct_yield_curve(self, scores: np.ndarray, n_components: int = 3) -> np.ndarray:
        """
        Reconstruct yield curve from PCA scores

        Args:
            scores: PCA scores (n_observations x n_components)
            n_components: Number of components to use for reconstruction

        Returns:
            Reconstructed yield curve matrix
        """
        if self.pca is None or self.mean_curve is None:
            raise ValueError("PCA must be fitted before reconstruction")

        # Use only first n_components
        components = self.pca.components_[:n_components]
        scores_subset = scores[:, :n_components]

        # Reconstruct: X_reconstructed = scores @ components + mean
        reconstructed = scores_subset @ components + self.mean_curve

        return reconstructed
