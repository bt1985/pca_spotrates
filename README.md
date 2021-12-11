# R-shiny Web App for deriving stress scenarios from the yield curve
The web app itself can be found [here](https://bt1985.shinyapps.io/ycpca/). It uses the R-Shiny framework to perform a principal component analysis (PCA) of the yield curve, visualize the results and derive adverse scenarios for stress testing. The code for the app can be found in this repository. This document shall a give a overview over the used data, the regulatory context, the mathematical / technical setup, a brief discussion and an outlook for the further development. The web app provides interactive acess to the methodology discribed in this document.

# Deriving stress scenarios from the yield curve
In the reign of valuation of assets and liabilities via their future cashflows yield curves are of uttermost importance. The yield curve for a given time consists of multiple spot rates for different maturities. The movement of the spot rates over time for the maturities are highly correlated. To be able to create stress scenarios it is crucial to understand how the different spot rates move together. This understanding can be achieved via PCA. PCA reduces highly correlated and high dimensional data to lower dimensional data with reasonable approximation. 

## The data
The yield curve over the course of time can be plotted as a three-dimensional surface. The following plot shows on the x-axis the time, on the y-axis the maturity and on the z-axis the corresponding spot rate:

![Yield curve](/assets/yc.png)

One can clearly see that the curve flatted a lot after 2008, the short end of the curve is near or below 0.

## Regulatory context
Many regulatory approaches state the importance of the interest risk. For example, the definition of the interest rate risk in the Solvency II Guideline:

>Article 105 – Calculation of the Basic Solvency Capital Requirement

>5. The market risk module shall reflect the risk arising from the level or volatility of market prices of financial instruments which have an impact upon the value of assets and liabilities of the undertaking. It shall properly reflect the structural mismatch between assets and liabilities, in particular with respect to the duration thereof. It shall be calculated, in accordance with point 5 of Annex IV, as a combination of the capital requirements for at least the following submodules: (a) the sensitivity of the values of assets, liabilities and financial instruments to changes in the term structure of interest rates, or in the volatility of interest rates (interest rate risk); 

The Solvency II standard formula demands one up and one down scenarios of the yield curve; each leading to a revaluation of the future cashflows from assets and liabilities. The International Association of Insurance Supervisors suggests several stress scenarios which change the level, slope and curvature of the yield curve. Modelling the fluctuations in the yield curve is critical to quantify the interest risk. The 3d-surface plot above shows the spot rates fluctuates in time but the spot rates for the different maturities are highly correlated.

## Technical setup
The yield curve can be described as a matrix composed of <img src="https://render.githubusercontent.com/render/math?math=m"> historical observations, with each historical observation having <img src="https://render.githubusercontent.com/render/math?math=n"> dimensions. This leads to the following matrix <img src="https://render.githubusercontent.com/render/math?math=A_{m,n}">:<br />
![Yield curve](/assets/Matrix.png), each <img src="https://render.githubusercontent.com/render/math?math=a_{i,j}"> represents a specific spot rate. The goal is now to choose <img src="https://render.githubusercontent.com/render/math?math=k"> principal components with <img src="https://render.githubusercontent.com/render/math?math=k<m">. We can then approximate the centred yield curve matrix <img src="https://render.githubusercontent.com/render/math?math=\widehat{A}=A-\mu"> with the principal components of the following form:<br />
![Yield curve](/assets/MatrixPCA.png).  
The PCA computes the principal components of the covariance matrix. A detailed practice-oriented explanation of the PCA can be found [here](https://builtin.com/data-science/step-step-explanation-principal-component-analysis). A explanation with mathematical rigor can be found in the book "Quantitative Risk Management" p. 109. The main idea of the PCA is to form a new coordinate system with the principal components. The Principal Components are an orthonormal basis of this new coordinate system. Then <img src="https://render.githubusercontent.com/render/math?math=U^T"> is the transformation matrix: <br />
![Yield curve](/assets/ConstructionU.png) <br />
The  <img src="https://render.githubusercontent.com/render/math?math=m*n">-Matrix <img src="https://render.githubusercontent.com/render/math?math=U^T"> transforms the centred yield curve to the lower m-dimensional representation. This new representation with lower dimension approximates resonable the original data . The <img src="https://render.githubusercontent.com/render/math?math=n*m">-Matrix <img src="https://render.githubusercontent.com/render/math?math=U"> transforms the low dimensional representation back to a centred yield curve. 

The scores are the coordinates of the new coordinate system. When we have calculated our principal components, we can see how much of the variance is explained by each component. 
![Yield curve](/assets/ExplainedVariance.png)
Most of the variance in the yield curve is explained over the level. The first three principal components explain most of the variance. From this point of view it seems sufficient to only use the first three principal components. They have the following form:
![Yield curve](/assets/PC1-3.png)
PC1 is often associated with the level, PC2 with the slope and PC3 with the curvature of the yield curve. By building linear combinations of the first three principal combinations (as stated in the matrix <img src="https://render.githubusercontent.com/render/math?math=\widehat{A}_{m,n}">) we have now a good approximation of the yield curve in terms of the explained variance. We know that by construction the scores of the principal components are uncorrelated but not necessarily independent, they are independent if we assume there distribution is elliptical. The Kolmogorov-Smirnov test and the Shapiro-Wilk-Test both show that they are not elliptical distributed. We can still study the fluctuations of the scores of each principal component. The development of the scores including their rolling 99,5 % quantile is displayed bellow for the first three principal components: <br />
![Rolling quantile scores](/assets/scoresrollingquantile.png)

To construct a yield curve stress scenario from the scores, the PCA has to be reverted. By construction our Principal Components are a orthonormal basis, hence the inverse matrix is the transposed matrix. To approximate the initial yield curve only with the first three PC we can write: <br />
![AproximationPCA](/assets/AproximationPCA.png)<br />
To create a stressed yield curve scenario in one principal component we can replace the corresponding score, with a stressed score (e.g. 99,5% quantile): <br />
![Construction stressed Score.png](/assets/ConstructionstressedScore.png)

Then we can construct a stressed yield curve with the new scores by reverting the PCA: <br />
![Construction stressed Score.png](/assets/StressAproximation.png)

Here is a figure of the resulting yield curve scenarios, for the chosen rolling 99,5%-quantile: <br />
![Construction stressed Score.png](/assets/YC_StressScenario.png)

## Discussion:

### Pro:
- PCA derives effective models to represent high dimensional data with a low amount of explaining variables. 
- A simplified modelling of the yield curve using only a view uncorrelated random variables is achievable. 
- PCA itself is a non-parametric method so it is not necessary to make assumptions about the distribution of the yield curve. 
- Using the first the components it is possible to create up/down stress scenarios for the level, slope and curvature of the yield curve.

### Contra:
- PCA is still a correlation analysis, so a stationary timeseries is required. 
- The explained variance is the only criteria for choosing the principal components. As shown by Moody's to construct a yield curve from PCA which is stressed with a 100 basis points, we would need up to nine principal components to create a yield curve for this stress scenario. This parallel stress scenario was not part of the training data, so it is hard to reproduce for the model.
- By only allowing linear combinations of the principal components, the tail scenarios used for stress testing are all just linear combinations of the chosen principal components. The principal components were chosen by their explained variance, but not by likelihood to occur in tail events. By construction of PCA we could have smoothed the information of tail events out.
- The results itself are not stable over time. The different supervisory measures of the ecb can change and with them the shape of the yield curve. 
- By only taking the historical quantile for a given period, there is the implicit assumption that the future tail events will not exceed the past tail events

### technical specifications
- it is possible to choose different target variables. We could have chosen to model the difference of spot rates over time, forward rates, (log-) returns,…
- daily data was used, it is possible to choose monthly/hourly data
- a rolling timeframe of 24 month for calculating the 99,5 % quantile of the monthly changes was used. 
  - These past scenarios by definition only describe realizations of spot rates that have actually occurred, they can not be represent all future events  
  - In choosing the lenth of the timeframe there is a trade off: 
    - A short period of time the results will be very sensitive to outcomes of the recent past
    - A long period may include information that is no longer relevant to the current situation. 
- we did not take tail events into special account, by choosing the number of PC

## Further development
- to calculate the severity of the different stress scenarios different cashflow scenarios would be required and need to be generated, the cashflows itself can be dependent on the shape of the yield curve. 
- include the occurrence of tail events
- compare the results to other yield curve modelling techniques like the nelson-siegel model
- extend the model to a PC-GARCH model 

## Literature

Alexander, 2002, Principal component models for generating large GARCH covariance matrix

EIOPA, 2019. Consultation paper on the opinion on the 2020 review of Solvency II

European Commission, 2015. Regulation 2015/35 2014, Directive 2009/138/EC on the taking-up and pursuit of the business of Insurance and Reinsurance (Solvency II)

McNeil, Frey,Embrechts, 2005, Quantitative Risk Management

Redfern, McLean, 2014, Principal Component Analysis for Yield Curve Modelling Reproduction of out-of-sample yield curve

International Association of Insurance Supervisors (IAIS), 2020, ICS Version 2.0 for the monitoring period

Schlütter, 2020, Scenario-based Measurement of Interest Rate Risks
