# KMDS Modeling Contracts

This directory contains the KMDS task implementation contracts for supported modeling workflows.

## Purpose
Each document explains how to implement a task for `kmds-modeling`, including:
- required `model_config.yaml` fields
- data readiness expectations
- candidate and transformer interfaces
- runtime evaluation and export behavior
- implementation templates

## Files
- `tabular_classification_recommendations.md` — KMDS contract for tabular classification tasks
- `tabular_regression_recommendations.md` — KMDS contract for tabular regression tasks
- `graph_modeling_recommendations.md` — KMDS contract for graph modeling tasks
- `clustering_recommendations.md` — KMDS contract for clustering tasks

## Usage
Point agents at this directory when you need task-specific KMDS modeling guidance.

For a given task, use the corresponding file:
- `TABULAR_CLASSIFICATION` → `tabular_classification_recommendations.md`
- `TABULAR_REGRESSION` → `tabular_regression_recommendations.md`
- `SURVIVAL_ANALYSIS` → `survival_recommendations.md`
- `GRAPH_NODE_CLASSIFICATION`, `GRAPH_NODE_REGRESSION`, `GRAPH_DISCOVERY` → `graph_modeling_recommendations.md`
- `CLUSTERING` → `clustering_recommendations.md`

## Note
The package runtime currently supports tabular classification and regression evaluation/export. Graph and clustering documents are advisory-only until runtime support is added.
