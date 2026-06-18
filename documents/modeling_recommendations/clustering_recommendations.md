# Clustering Recommendations

## Recommended Framework
- Use clustering when the problem is exploratory, when target labels are absent, or when segmentation into homogeneous sub-populations is required.
- Prefer robust clustering methods that respect heterogeneity in operational data.

### Recommended algorithms
- Spectral clustering with a spectral-gap selection procedure.
- HDBSCAN as a fallback when spectral methods are not viable.

### Guidance
- Avoid flat pooling of the full dataset when distinct sub-populations exist.
- If the task is rare-event or anomaly-focused, consider hybrid pipelines that use anomaly scores as features for downstream supervised learning.
