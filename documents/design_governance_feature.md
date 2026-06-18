------------------------------
## KMDS Design Governance Framework
Repository: rajivsam/kmds-modeling
Author: Rajiv Sambasivan
Architecture Status: Approved for LLM-Based Feature Implementation
## 1. Executive Summary & Philosophy
The KMDS Design Governance Framework is an opinionated, knowledge-driven governance layer designed to prevent machine learning pipeline degradation, data leakage, and algorithmic anti-patterns before code compilation or model training begins.

Unlike traditional black-box AutoML platforms, `kmds-modeling` acts as a **Design-Time Compiler**. It solves the "Too Many Knobs" problem for data scientists by constraining the design space based on the structural properties of the data and the explicit intent of the user. It generates tight, highly constrained architectural blueprints optimized for injection into AI Coding Assistants. [2, 3] 

### The Junior Data Scientist Persona
This tool is designed for practitioners with low-to-moderate experience. To prevent "Garbage-In/Garbage-Out" prompt engineering, the framework enforces a **Metadata Schema Contract**. The user does not "describe" their problem in prose; they provide a structured intent and a data sample, which the engine then uses to navigate the governance funnel.

### Advisory Service Scope
This modeling advisor is an independent service. Users may choose to accept its recommendations, refine them with independent research, or reject them entirely. It is intended as a starting point with structured frameworks for:
- Regression
- Classification
- Graph-based Analysis
- Clustering

If the user is unsure whether a use case is a fit for graph-based analysis, the advisor can offer a simple heuristic to help decide. In some cases, one or two additional interactions with data samples may refine the recommendation further.

## 2. Governance Guardrails: The Input Contract
The user is presented with an introductory statement such as:

> I can give you modeling suggestions for the following tasks: Classification, Regression, Graph-based Analysis, and Clustering. If you are not sure if your use case is a fit for a graph-based analysis, I can give you a simple heuristic. These are good starting points, and you are of course free to supplement them with independent research.

To ensure a narrow and accurate funnel of choices, the following constraints are mandatory for every governance session:

1.  **Task Intent Literals**: Users must select from a fixed list:
    *   `TABULAR_CLASSIFICATION`: Standard classification (e.g., Is this loan good or bad?).
    *   `TABULAR_REGRESSION`: Standard regression (e.g., What is the expected loss amount?).
    *   `GRAPH_NODE_CLASSIFICATION`: Predicting a category for an entity based on its connections (e.g., Is this borrower part of a fraud ring?).
    *   `GRAPH_NODE_REGRESSION`: Predicting a value for an entity based on its connections (e.g., Credit score based on social/business network).
    *   `GRAPH_DISCOVERY`: Unsupervised discovery of links or communities.
    *   `CLUSTERING`: Unsupervised grouping of similar rows.
2.  **Entity Mapping**: Users must explicitly tag columns representing unique entities (e.g., `borrower_id`, `loan_id`). 
    *   *Constraint*: Multiple entities with `TABULAR_CLASSIFICATION` trigger a prompt to switch to `GRAPH_NODE_CLASSIFICATION`.
3.  **Strategy Toggle**: For supervised tasks, the user must choose between:
    *   `MAX_ACCURACY`: High-capacity, non-linear models (XGBoost, TabPFN).
    *   `HIGH_INTERPRETABILITY`: Additive/Kernelized models (GAMs, GP).
4.  **Data Profile Validation**: The `Profiler` automatically checks:
    *   *Cardinality*: Prevents "classifying" targets with >20 unique values.
    *   *Imbalance*: Measures minority class ratios to select the correct Pillar Bucket.

## Scope Gateway
To keep maintenance low for a solo developer, the framework restricts its governance engine to exactly 4 core pillars. Each supported task has a recommended framework documented in the repository's `documents/` directory, and the advisor is intended as an independent guidance service. If an unsupported task type is requested, the system terminates execution with a standard boundaries notice:

[kmds-modeling System Notice]: Requested workflow is out of scope. System governance is strictly limited to: Classification, Regression, Graph-Based Analysis, and Clustering.

Using the advisor or rejecting its guidance is up to the user; the service exists to provide structured starting recommendations rather than dictate a final solution.

------------------------------
## 3. Core Governance Pillars & Prompt Blueprints

          +----------------------------------------------+

          |         kmds-modeling Data Profiler          |
          +----------------------------------------------+
                                 |
         (Extracts Schema, Ratios, Entities, and Priorities)
                                 |
                                 v
          +----------------------------------------------+

          |         KMDS LLM Governance Gateway          |
          +----------------------------------------------+
                                 |
        +------------------+-----+------------------+

        |                  |                        |
        v                  v                        v
 [Tabular Supervised] [Tabular Unsupervised]      [Graph]
  - Mild (20-30%)      - Interpretability     - Homogeneous
  - Moderate (1-10%)   - Pure Prediction      - Bipartite
  - Extreme (<1%)                             - Heterogeneous

## Pillar A: Classification (Class Imbalance Workflows)

* Trigger Condition: Selected task is classification. The engine measures the target variable vector distribution to compute the exact minority class ratio.
* Core Constraint: SMOTE and all synthetic data generation methods are strictly forbidden.

## Rule Sets & LLM Code Prompts:

* Bucket 1: Mild Imbalance (20% – 30% or more minority class)
* Strategy: Train on baseline data. Enforce strictly stratified cross-validation splits to preserve stable real-world distributions across all folds. [4, 5] 
* Bucket 2: Moderate Imbalance (1% – 10% minority class)
* Strategy: Implement cost-sensitive learning via loss function weighting (e.g., class_weight='balanced' in scikit-learn or scale_pos_weight in XGBoost). Do not alter or resample raw rows. [6] 
* Bucket 3: Extreme Imbalance (Less than 1% minority class)
* Strategy: Pivot completely. Treat the system as an anomaly detection task (using Isolation Forests or One-Class SVMs) or implement advanced ensemble downsampling frameworks (e.g., EasyEnsemble / Balanced Random Forests) to train across parallel, balanced chunks of real data. [7, 8, 9, 10] 

------------------------------
## Pillar B: Regression (Featurization-Linked Workflows)

* Trigger Condition: Task is regression. This workflow integrates downstream from rajivsam/featurization, accepting non-parametric tree ensemble pre-filtered features.
* Strategic Branching: User indicates business priority: Interpretability or Maximum Prediction.

## Rule Sets & LLM Code Prompts:

* Branch 1: Strategic Interpretability
* Strategy: Apply dimensionality reduction or feature extraction to pre-emptively mitigate multi-collinearity. Mandate structural, additive, or kernelized methods: Generalized Additive Models (GAMs) with splines, Gaussian Processes (GP), or Kernel Regression. This allows stakeholders to directly inspect visual partial dependence curves.
* Branch 2: Maximum Predictive Accuracy
* Strategy: Bypass traditional scalar preprocessing and drop pre-filtered metrics directly into non-linear, high-capacity architectures. Mandate benchmarking of XGBoost, Random Forest, and TabPFN (leveraging its native tabular in-context learning transformer architecture). Simple linear models are explicitly barred from this branch. [11] 

------------------------------
## Pillar C: Graph Modeling (Relational Data-Linked Workflows)

* Trigger Condition: Task intent is `GRAPH_NODE_CLASSIFICATION`, `GRAPH_NODE_REGRESSION`, or `GRAPH_DISCOVERY`. This pipeline acts downstream from `dd-parser-cleaner`, utilizing extracted entity tags to define the topology.

* Tentative Graph Implementation Approach: Use the workspace `working_dir` and `dd-parser-cleaner` metadata mapping to build a node/edge schema, then instantiate a graph object in a graph-specific task runner. This can be implemented using graph frameworks such as PyTorch Geometric or DGL, where metadata-driven node and edge construction is performed before model training. The model runtime should remain isolated to `task_graph.py` so the tabular and graph flows do not interfere.

## Rule Sets & LLM Code Prompts:

* Topology 1: Homogeneous Graphs (1 Entity Type Extracted)
   * **Unsupervised**: Mandate Representation Learning (Node2Vec, DeepWalk) to uncover latent group configurations.
   * **Supervised**: Route to standard GCN or GraphSAGE pipelines to predict node labels/properties while aggregating local neighborhood features. [12] 
* Topology 2: Bipartite Graphs (Exactly 2 Entity Types Extracted)
   * **Unsupervised**: Guide user toward Non-negative Matrix Factorization (NMF) or Co-Clustering for link discovery. [13] 
   * **Supervised**: Implement a Message Passing Neural Network (MPNN) designed for bipartite projections (e.g., User-Item preference prediction).
* Topology 3: Heterogeneous Graphs (3 to 5 Entity Types Extracted, e.g., SBA Dataset)
   * **Strategic Advantage**: Mandate Heterogeneous GNNs (RGCN, HAN). 
   * **Pillar Logic**: For `GRAPH_NODE_CLASSIFICATION` (e.g., Default Prediction on a Loan connected to Borrowers and Banks), the explicit message-passing structure natively accounts for nested multi-level population variances. This bypasses the need for statistical Hierarchical Regression. 
   * **Constraint**: If class imbalance exists (Pillar A crossover), correct it via target loss reweighting inside the GNN layer rather than resampling the graph structure. [14, 15] 

------------------------------
## Pillar D: Unsupervised Learning (Operational Structure Workflows) [16] 

* Trigger Condition: Task requires exploration or preprocessing of operational business contexts where target fields are missing, raw, or require partitioning.

## Rule Sets & LLM Code Prompts:

* Branch 1: Understanding Heterogeneity & Sub-Population Structure
* Context: Multi-line business operations (e.g., contrasting a car insurance applicant profile with a boat insurance profile within the same database).
   * Strategy: Implement robust clustering frameworks to split distinct operational sub-populations before building downstream localized models. Forbid flat pool training; mandate isolating unique data segments so each sub-population receives its own contextual model path. [14] 
* Branch 2: Dimension Reduction & Manifold Exploration
* Context: Sifting through ambient observable dimensions to clean background noise and map the dataset's true intrinsic dimensionality.
   * Strategy: Isolate variance patterns. If the linear global structure dominates, prescribe Principal Component Analysis (PCA) with explicit variance threshold checks. If the data displays non-linear geometric scaling along a curved manifold, strictly mandate Manifold Learning / Graph Modeling representation techniques (e.g., Autoencoders with restrictive bottlenecks) to extract compressed representations without stripping signal. [17, 18, 19] 
* Branch 3: Pure Anomaly Detection & Hybrid Solutions
* Context: Extremely rare event detection (e.g., financial fraud patterns where class observations are near zero).
   * Strategy: Configure pure semi-supervised/unsupervised outlier extraction models. If a predictive layer is required, explicitly direct the user to engineer a hybrid pipeline: wrap the anomaly score out-of-fold as a structural continuous feature and inject it directly into a secondary cost-sensitive supervised learning engine.

------------------------------
## 3. Operational Integration Workflow
To ensure high developer adoption, the Python package runtime must execute with zero manual typing configuration from the user, outputting actionable text templates ready for the clipboard.

This advisory output is intended to live inside the KMDS workspace under `working_dir/documents`, where `working_dir` is the installed project root provided in `model_config.yaml`.

The package should use the `PathCoordinator` abstraction for all workspace path resolution so that the KMDS project layout is established once the working directory is known. In practice, this means the advisor or runtime helper functions should resolve recommendation storage through `PathCoordinator.modeling_recommendations_path` rather than hardcoding package-local paths.

Currently, the runtime supports classification and regression task execution via dedicated task modules. Graph-based analysis and clustering are supported as advisory task paths, with separate runtime modules prepared for future implementation.

The Governance Engine produces a "Design Blueprint" structured as an expert prompt.

**Example Output for Path 1:**
```text
================== [KMDS DESIGN GUIDANCE: PATH 1] ==================
PROBLEM CHARACTERISTICS:
- Task: Graph Node Classification (Heterogeneous Topology)
- Imbalance: Extreme (<1% minority class)
- Priority: Max Accuracy

DESIGN GUIDELINES:
1. Topology: Use a Heterogeneous GNN (RGCN or HAN) to preserve multi-level population variance.
2. Validation: Use Stratified Group K-Fold split on 'borrower_id' to prevent leakage.
3. Loss Function: Use focal loss or class-weighting in the GNN layer. Do NOT use SMOTE.

SUGGESTED AI ASSISTANT PROMPT:
"I am building a Graph Node Classification model for loan default prediction.
I have 3 entities [borrower, loan, bank]. The class imbalance is extreme.
Based on KMDS Governance, I need to implement a Heterogeneous GNN using 
PyTorch Geometric that uses weighted loss instead of resampling. 
Please draft a modular training script following these constraints..."
====================================================================
```
   
   
------------------------------
## Propose Next Step
This layout completely formalizes your core framework, locking your domain logic safely into place. Since you are saving this summary for iteration inside kmds-modeling, would you like to review or design the exact folder architecture (e.g., where the prompt templates and utility scripts live in your package tree) to make coding this feature straightforward?

[1] [https://www.geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/machine-learning/)
[2] [https://letsdatascience.com](https://letsdatascience.com/blog/aws-vs-gcp-vs-azure-for-machine-learning-the-practical-decision-guide)
[3] [https://www.scaler.com](https://www.scaler.com/blog/machine-learning-models/)
[4] [https://www.sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S1568494626009865)
[5] [https://link.springer.com](https://link.springer.com/chapter/10.1007/978-3-030-16946-6_63)
[6] [https://www.mdpi.com](https://www.mdpi.com/2673-4001/6/3/69)
[7] [https://www.sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S2542660526000533)
[8] [https://www.crestinfotech.com](https://www.crestinfotech.com/supervised-vs-unsupervised-learning-key-differences-and-use-cases/)
[9] [https://www.kdnuggets.com](https://www.kdnuggets.com/2020/12/machine-learning-anomaly-detection-conditional-monitoring.html)
[10] [https://link.springer.com](https://link.springer.com/article/10.1007/s43926-026-00305-x)
[11] [https://www.emergentmind.com](https://www.emergentmind.com/topics/tabular-foundation-model-tabpfn)
[12] [https://www.youtube.com](https://www.youtube.com/watch?v=IGEHHrGnnGk&t=27)
[13] [https://sandipanweb.wordpress.com](https://sandipanweb.wordpress.com/2023/12/06/non-negative-matrix-factorization-to-solve-text-classification-and-recommendation-problems/)
[14] [https://www.sciencedirect.com](https://www.sciencedirect.com/topics/computer-science/unsupervised-learning)
[15] [https://www.cet.ac.in](https://www.cet.ac.in/hpc-projects/)
[16] [https://www.meegle.com](https://www.meegle.com/en_us/topics/machine-learning/unsupervised-learning-applications)
[17] [https://medium.com](https://medium.com/@data4v/supervised-vs-unsupervised-learning-whats-the-difference-1b8fa2f16baf)
[18] [https://pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC12333287/)
[19] [https://pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC8659648/)
