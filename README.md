# Optimization Output Analysis

This repository contains analysis code and outputs for discretization-discovery optimization algorithms, developed as part of research work with Carnegie Mellon University and Optym.

## Project Overview

This project analyzes the performance of discretization-discovery algorithms for Vehicle Routing Problems with Time Windows (VRPTW). The analysis includes:

- **Algorithm Performance**: Comparative analysis of different initialization strategies (empty vs full initialization)
- **Graph Analysis**: Network structure analysis of time and capacity graphs
- **Visualization**: Data visualization of optimization convergence and solution quality
- **Data Processing**: Tools for parsing JSON optimization outputs and converting to analyzable formats

## File Structure

### Analysis Scripts
- `disc_squared.qmd` - Main Quarto analysis document with comprehensive algorithm analysis
- `data_analysis.R` - Core R script for processing optimization outputs
- `CM_2.R` - Secondary analysis script
- `repl.R` - REPL-style experimentation script
- `map_practice.R` - Spatial analysis and mapping code
- `Input_Data.py` - Python script for creating SlinkLPy input data structures

### Data Files
- `jy_c102.csv` - Customer data for the C102 Solomon benchmark instance
- `sample_routes.csv` - Sample route data for testing
- `yuck_solution.csv` - Example optimization solution output
- `location_time_graph.csv` - Processed graph data for spatial-temporal analysis

### Analysis Outputs
- `disc_squared.md` - Rendered markdown from analysis
- Various CSV files with processed results
- JSON files with optimization data

## Key Features

### Algorithm Analysis
- **Iteration Tracking**: Analysis of lower bound progression across optimization iterations
- **Problem Size Evolution**: Tracking of graph compression and problem complexity
- **Convergence Analysis**: Statistical analysis of algorithm performance

### Graph Analysis
- **Network Metrics**: Calculation of graph density, clustering coefficients, and centrality measures
- **Temporal Analysis**: Time-based network evolution analysis
- **Spatial Visualization**: Geographic plotting of routes and customer locations

### Comparative Studies
- **Initialization Strategies**: Comparison of empty vs full graph initialization
- **Delta Analysis**: Impact of different algorithmic parameters
- **Performance Benchmarking**: Cross-instance performance comparison

## Dependencies

### R Packages
```r
library(readr)
library(ggalt)
library(janitor)
library(tidyverse)
library(patchwork)
library(jsonlite)
library(fs)
library(glue)
library(igraph)
```

### Python Packages
```python
import csv
import math
import json
```

## Usage

1. **Basic Analysis**: Run `disc_squared.qmd` to generate the complete analysis report
2. **Data Processing**: Use `Input_Data.py` to create input structures from CSV data
3. **Custom Analysis**: Modify `data_analysis.R` for specific analytical needs

## Research Context

This work was conducted as part of optimization research focusing on:
- **Discretization-Discovery Algorithms**: Novel approaches to solving large-scale routing problems
- **Graph Compression Techniques**: Methods for reducing problem complexity while maintaining solution quality
- **Hybrid Optimization**: Combining exact and heuristic approaches for practical scalability

The algorithms analyzed here are designed for real-world logistics applications where traditional exact methods become computationally intractable.

## Data Sources

- **Solomon Instances**: Using standard VRPTW benchmark instances (C102)
- **Synthetic Data**: Generated test cases for algorithm validation
- **Optimization Outputs**: JSON-formatted results from discretization-discovery algorithm runs

## Contact

This research was conducted in collaboration with Carnegie Mellon University and Optym Inc.
