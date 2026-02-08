# Task 1: Laying the Foundation for Analysis

## 1) Planned Analysis Workflow
1. **Data ingestion**: Load Brent oil daily prices from May 20, 1987 to Sep 30, 2022. Parse the `Date` column to datetime and sort chronologically.
2. **Initial quality checks**: Validate date coverage, check for missing prices, and confirm daily frequency.
3. **Exploratory analysis**:
   - Plot raw prices to identify trend shifts and large shocks.
   - Compute log returns $r_t = \log(P_t) - \log(P_{t-1})$ for stationarity analysis.
   - Visualize log returns to detect volatility clustering and structural breaks.
4. **Time series diagnostics**:
   - Stationarity testing on log returns (ADF test).
   - Trend and volatility characterization to guide modeling choices.
5. **Event dataset construction**:
   - Create a structured list of geopolitical/economic events with start dates.
6. **Bayesian change point modeling**:
   - Define a change point model (mean shift) on log returns in PyMC.
   - Fit with MCMC and validate convergence.
7. **Interpretation and mapping to events**:
   - Identify posterior change points and compare to event list.
   - Quantify mean shifts and express effects in percentage terms.
8. **Communication**:
   - Summarize results in a concise report and an interactive dashboard.

## 2) Event Data (structured list)
A structured CSV is provided in data/events.csv. It includes major events such as OPEC policy shifts, geopolitical conflicts, and sanctions that plausibly influence oil prices.

## 3) Assumptions and Limitations
**Assumptions**
- The Brent price series is accurately measured and reflects market information without systematic data errors.
- A single change point model can capture major structural breaks; additional breaks may exist.
- Log returns are a reasonable stationary transform for modeling shifts in mean.
- Event dates represent approximate start points and not necessarily the exact market reaction date.

**Limitations**
- **Correlation vs causation**: Detecting a change point near an event does not prove the event caused the change. The model identifies statistical shifts in the series, but causal attribution requires stronger identification strategies and additional covariates.
- **Model simplicity**: A single change point with constant variance may miss multi-regime dynamics, varying volatility, or short-lived shocks.
- **Event coverage**: The event list may be incomplete or imprecise in timing.
- **Exogenous factors**: Macro variables (FX rates, global demand indicators, inventories) are not included in the core model and may confound observed changes.

## 4) Communication Channels and Formats
- **Investors**: Executive summary with charts and quantified impacts, plus dashboard for interactive exploration.
- **Policymakers**: Policy brief with change point dates, uncertainty, and scenario implications.
- **Energy companies**: Operational memo with volatility and risk implications, backed by interactive visuals.

## 5) Key Concepts and Expected Outputs
**Change point models** detect structural breaks by estimating parameters before and after a latent switch point. In this context, they help identify periods where the average level of returns changes.

**Expected outputs**
- Posterior distribution of change point dates.
- Estimated means before and after the change.
- Probabilistic statements about the magnitude and direction of shifts.

**Limitations of outputs**
- The posterior distribution can be broad or multi-modal when evidence is weak.
- Estimated mean shifts are sensitive to model assumptions and data quality.

## 6) Time Series Properties and Modeling Implications
- **Trend**: Prices show long-term trends and large shocks; thus, modeling prices directly can be non-stationary.
- **Stationarity**: Log returns are expected to be closer to stationary, which is suitable for mean-shift change point modeling.
- **Volatility clustering**: Periods of high volatility suggest potential benefits from regime-switching or heteroskedastic models in future work.

## 7) References Reviewed
- Bayesian inference fundamentals, MCMC, and change point detection in time series.
- General data science workflow references for reproducible analytics.
