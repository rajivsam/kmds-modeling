# Tabular Regression Recommendations

## Recommended Framework
- Use pre-filtered KMDS features from the featurization output.
- Decide whether the priority is interpretability or maximum predictive accuracy.

### Interpretability
- Prefer Generalized Additive Models (GAMs), Gaussian Processes (GP), or kernel regression.
- Use explicit visual diagnostics such as partial dependence curves.

### Maximum Predictive Accuracy
- Prefer non-linear ensembles such as XGBoost or Random Forest.
- Avoid simple linear models in this branch.
