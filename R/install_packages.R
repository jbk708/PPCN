#!/usr/bin/env Rscript
"""Install R dependencies for PedPanCancer-Networks.

Run once per environment:
    Rscript R/install_packages.R
"""

# --- CRAN packages ---
cran_packages <- c(
  # Background mutation model
  "dndscv",         # Actually from GitHub — handled below


  # Data wrangling
  "data.table",
  "dplyr",
  "tidyr",
  "readr",
  "stringr",

  # Statistics
  "survival",       # Survival analysis
  "broom",          # Tidy model outputs

  # Visualization
  "ggplot2",
  "pheatmap",       # Heatmaps
  "ComplexHeatmap", # Bioconductor — handled below
  "patchwork",      # Combine ggplots
  "ggrepel",        # Non-overlapping labels

  # I/O
  "jsonlite",
  "openxlsx",

  # Misc
  "foreach",        # Parallel iteration
  "doParallel",     # Parallel backend
  "optparse"        # CLI argument parsing
)

# Filter to CRAN-only (exclude Bioc and GitHub packages)
cran_only <- c(
  "data.table", "dplyr", "tidyr", "readr", "stringr",
  "survival", "broom",
  "ggplot2", "pheatmap", "patchwork", "ggrepel",
  "jsonlite", "openxlsx",
  "foreach", "doParallel", "optparse"
)

install.packages(
  cran_only[!cran_only %in% installed.packages()[, "Package"]],
  repos = "https://cloud.r-project.org"
)

# --- Bioconductor packages ---
if (!requireNamespace("BiocManager", quietly = TRUE)) {
  install.packages("BiocManager", repos = "https://cloud.r-project.org")
}

bioc_packages <- c(
  "GenomicRanges",     # Genomic interval operations
  "VariantAnnotation", # VCF/MAF parsing
  "biomaRt",           # Gene annotation via Ensembl
  "ComplexHeatmap",    # Advanced heatmaps
  "DESeq2",            # Differential expression (expression correlation phase)
  "maftools"           # MAF file utilities and visualization
)

BiocManager::install(
  bioc_packages[!bioc_packages %in% installed.packages()[, "Package"]],
  ask = FALSE,
  update = FALSE
)

# --- GitHub packages ---
if (!requireNamespace("remotes", quietly = TRUE)) {
  install.packages("remotes", repos = "https://cloud.r-project.org")
}

# dNdScv — core background mutation model
if (!"dndscv" %in% installed.packages()[, "Package"]) {
  remotes::install_github("im3sanger/dndscv")
}

cat("\n✓ All R packages installed.\n")
