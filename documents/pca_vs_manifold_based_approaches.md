You are remembering a highly specific, mathematically elegant technique known as evaluating the Local Neighborhood Preservation or Neighborhood Compression Ratio.
Your intuition is spot on: PCA preserves global distances (large variances), but it aggressively flattens non-linear manifolds. If the local neighborhood structures in the PCA space don't match the original high-dimensional space, PCA is failing, and you need a non-linear approach like t-SNE, UMAP, or Isomap. [1, 2, 3, 4, 5] 

------------------------------
## The Nearest-Neighbor Diagnosis Method
Here is the exact step-by-step process for the specific method you remembered to diagnose if PCA is failing:
## 1. Map the True High-Dimensional Space

* For every data point $x_i$ in your full, original dataset, find its $k$ nearest neighbors (usually $k=2$ or $k=5$) using Euclidean distance.
* Save the indices of these neighbors. This is your ground-truth local geometry. [6] 

## 2. Map the PCA Reduced Space [7] 

* Project your dataset into the low-dimensional PCA space (e.g., 2D or 3D).
* For the exact same data point $x_i$ in the PCA space, find its $k$ nearest neighbors again. [8, 9, 10, 11, 12] 

## 3. Calculate the Jaccard Distance / Neighborhood Overlap

* Compare the two sets of neighbors. If point $A$'s closest neighbors in the full dataset were points $B$ and $C$, but in the PCA space its closest neighbors are now points $Y$ and $Z$, PCA has physically torn the local neighborhood apart to force a linear projection.
* You can calculate the Average Reconstruction Error of Distances:
$$\text{Error} = \frac{1}{N} \sum_{i=1}^{N} \vert{} D_{\text{full}}(x_i, \text{NN}_1) - D_{\text{PCA}}(x_i, \text{NN}_1) \vert{}$$ [13] 
* The Verdict: If the local neighborhoods do not overlap (low preservation) or the distance error is high, your data lies on a non-linear manifold (like a Swiss roll). PCA is insufficient. [14] 

------------------------------
## 3 Other Classic Signs That PCA is Failing
Beyond the nearest-neighbor check, you can quickly diagnose PCA's insufficiency using these standard metrics:
## 1. The Scree Plot "Long Tail" (Slow Variance Explained)

* What to check: Plot the cumulative explained variance versus the number of principal components.
* The Sign: If it takes 20, 30, or 50 linear components just to explain 70% of the dataset's variance, the data is highly non-linear. A manifold approach might compress that exact same system down to just 2 or 3 intrinsic dimensions. [15, 16, 17] 

## 2. The "Crowding" or "Teardrop" Visual Artifact

* What to check: Plot the first two principal components.
* The Sign: If your data points collapse into a dense, uninformative single blob or a rigid "teardrop" shape with no clear separation between known classes, PCA is projecting across a curved surface, smashing distinct clusters on top of each other.

## 3. Downstream Model Degradation

* What to check: Train a simple classifier (like a random forest) on your full dataset vs. your PCA-reduced dataset.
* The Sign: If performance (e.g., fraud Recall) plummets catastrophically on the PCA data, it means the non-linear boundaries your model needs to separate fraud from non-fraud were completely erased during the linear flattening.

------------------------------
## Summary for your Fraud Framework

For fraud systems, non-linear structures are common because fraudulent transactions often mimic good transactions globally but form tight, hyper-specific anomalies locally. Using the nearest-neighbor preservation check is the most rigorous way to prove to your team that a linear reduction like PCA is stripping away your model's ability to catch those subtle fraud clusters.

------------------------------
If you are currently setting up a dimension reduction step, let me know:

* What is the original dimensionality (number of features) of your dataset?
* Are you reducing dimensions primarily for visualisation (2D/3D) or to feed cleaner features into an ML model?

I can provide the Python code to run the exact neighborhood preservation check on your data!

[1] [https://blog.gopenai.com](https://blog.gopenai.com/umap-dimensionality-reduction-intuitive-explanation-89929fd72ccf)
[2] [https://medium.com](https://medium.com/@abhishekjainindore24/uml-part-8-pca-principal-component-analysis-in-depth-2ecf0940529d)
[3] [https://www.tandfonline.com](https://www.tandfonline.com/doi/full/10.1080/02564602.2025.2573465)
[4] [https://www.cliffsnotes.com](https://www.cliffsnotes.com/cliffs-questions/4764527)
[5] [https://pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC7416435/)
[6] [https://www.sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0263224125035171)
[7] [https://journals.sagepub.com](https://journals.sagepub.com/doi/10.1177/0954406217743536)
[8] [https://www.sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S2352214322000260)
[9] [https://www.sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0925231226013226)
[10] [https://salford-repository.worktribe.com](https://salford-repository.worktribe.com/OutputFile/1489400)
[11] [https://www.slideshare.net](https://www.slideshare.net/slideshow/principal-component-analysis-pca-feature-selection/286397910)
[12] [https://www.sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S2215098614000068)
[13] [https://nannyml.readthedocs.io](https://nannyml.readthedocs.io/en/latest/how_it_works/multivariate_drift.html)
[14] [https://www.machinegurning.blog](https://www.machinegurning.blog/rstats/tsne/)
[15] [https://medium.com](https://medium.com/@sabourinleandre/understand-the-math-and-theory-behind-principal-component-analysis-pca-56fbf7a0b8f6)
[16] [https://medium.com](https://medium.com/data-science-collective/what-are-pca-loadings-and-how-to-effectively-use-biplots-fb6ea1208bda)
[17] [https://en.wikipedia.org](https://en.wikipedia.org/wiki/Nonlinear_dimensionality_reduction)
