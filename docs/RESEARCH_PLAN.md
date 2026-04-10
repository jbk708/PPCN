# Research Plan: Mutated Protein Complex Discovery in Pediatric Tumors

**Objective:** Identify protein complexes under significant mutational selection across pediatric tumor types using somatic mutation data from St. Jude Cloud and CBTN.

**Reference:** Baron & Tagore et al., *Nat. Genet.* 57, 1179–1188 (2025) — desmosome complex enrichment in melanoma via MutSigCV-based Δ-rank permutation testing across TCGA.

**Team:** 3 bioinformatics students (Person A, Person B, Person C) — equal skill level  
**Timeline:** ~5 weeks, ~10–15 hrs/week per person (~150–225 total person-hours)  
**Compute:**Pines 

---

## Week 1: Data Access, Harmonization & Complex Definitions

All three members work in parallel on independent data streams.

### Person A — St. Jude Cloud Data

- [ ] Retrieve somatic MAF/VCF files (PCGP, clinical genomics; predominantly WGS)
- [ ] Standardize variant format (chromosome naming, ensure hg38)
- [ ] Filter to nonsynonymous coding mutations (missense, nonsense, frameshift, splice-site)
- [ ] Apply germline filters (gnomAD AF > 0.001, panel of normals)
- [ ] Annotate with tumor type, sample purity estimates, sequencing platform (WGS vs. WES)
- [ ] Assess per-subtype sample sizes; flag subtypes with N < 30
- [ ] Deliver: harmonized St. Jude MAF (`data/stjude/`)

### Person B — CBTN / Kids First Data

- [ ] Retrieve OpenPBTA harmonized somatic MAFs from CAVATICA (WGS + WES mix)
- [ ] Apply identical standardization, filtering, and annotation pipeline as Person A
- [ ] Optional: pull TARGET MAFs for overlapping histologies to boost sample sizes
- [ ] Assess per-subtype sample sizes; flag subtypes with N < 30
- [ ] Deliver: harmonized CBTN MAF (`data/cbtn/`)

### Person C — Complex Definitions & Infrastructure

- [ ] Download and parse CORUM complex membership tables (~4,000 complexes)
- [ ] Download and parse hu.MAP 2.0 (secondary, broader coverage)
- [ ] Filter to complexes with ≥3 genes detected in mutation data
- [ ] Map gene identifiers to HUGO symbols consistent with MAF annotations
- [ ] Set up shared repo structure: `data/`, `scripts/`, `results/`, `figures/`
- [ ] Write utility functions for MAF I/O, gene-complex mapping, and shared filtering logic
- [ ] Deliver: complex membership tables (`data/complexes/`), shared utilities (`scripts/utils/`)

### End-of-Week 1 Sync

- [ ] **All:** Merge harmonized MAFs across St. Jude + CBTN; resolve any format discrepancies
- [ ] **All:** Agree on final tumor-type labels, minimum sample size thresholds, and hypermutator criteria

---

## Week 2: Background Mutation Model (dNdScv)

Parallelized by tumor type across all three members.

### All — dNdScv Runs

- [ ] Format merged MAFs into dNdScv input (one file per tumor type)
- [ ] Divide tumor types across team (suggested split):
  - **Person A:** medulloblastoma, HGG, DIPG
  - **Person B:** LGG, ependymoma, neuroblastoma
  - **Person C:** osteosarcoma, ATRT, remaining tumor types + pan-pediatric pooled
- [ ] Run dNdScv per assigned histology to obtain per-gene expected mutation rates
- [ ] Flag hypermutated samples (e.g., MMR-deficient HGGs) — exclude or model separately
- [ ] Validate: confirm known drivers show expected signals per tumor type:
  - BRAF in LGG
  - SMARCB1 in ATRT
  - H3F3A in DIPG
  - TP53 in osteosarcoma/HGG
- [ ] Deliver: per-gene observed vs. expected tables per tumor type (`results/dndscv/`)

### Pediatric-Specific Considerations (all members should verify)

- Lower TMB than adult cancers — dNdScv is preferred over MutSigCV for this reason
- Mutational spectra differ from adult (minimal UV/smoking; more structural variants not captured here)
- Germline predisposition variants (TP53, NF1) must be rigorously filtered

---

## Weeks 3–4: Complex-Level Enrichment Testing

### Week 3 — Implementation & Initial Runs

#### Person A — Enrichment Test Implementation

- [ ] Implement the enrichment test following Baron et al. methodology:
  1. For each gene: compute Δ = observed mutated tumors − expected mutated tumors
  2. Rank all genes by decreasing Δ
  3. For each complex: compute average rank of member genes
  4. Compare to average rank across 100,000 permutations (Mann-Whitney U analogue)
  5. Compute P-value per complex per tumor type
  6. Apply Benjamini-Hochberg correction across all complexes
- [ ] Write unit tests with synthetic data to validate permutation logic
- [ ] Deliver: enrichment test module (`scripts/enrichment.py` or `scripts/enrichment.R`)

#### Person B — Sensitivity Analysis Framework

- [ ] Implement sensitivity analysis variations:
  - Minimum complex size sweep (3, 5, 10 genes)
  - Hypermutator inclusion vs. exclusion
  - WGS-only vs. mixed WGS+WES
- [ ] Prepare batch submission scripts for SLURM
- [ ] Deliver: sensitivity wrapper scripts (`scripts/sensitivity/`)

#### Person C — Visualization & QC Pipeline

- [ ] Build plotting functions: volcano plots per tumor type, ranked complex bar charts
- [ ] Build cross-tumor-type heatmap of complex enrichment scores
- [ ] Implement QC checks for batch effects between St. Jude and CBTN samples
- [ ] Deliver: visualization module (`scripts/plotting.py` or `scripts/plotting.R`)

### Week 4 — Enrichment Runs & Interpretation

#### All — Run enrichment per assigned tumor types (same split as Week 2)

- [ ] Run enrichment test per tumor type
- [ ] Run pan-pediatric pooled analysis
- [ ] Run sensitivity analyses per tumor type
- [ ] Sanity checks — do known complexes emerge?
  - SWI/SNF in ATRT / rhabdoid tumors
  - Cohesin complex
  - Polycomb (PRC2) in HGG/DIPG
- [ ] Generate ranked complex tables and figures per tumor type
- [ ] Deliver: enrichment results (`results/enrichment/`), figures (`figures/`)

### End-of-Week 4 Deliverables

- [ ] Table of significantly enriched complexes (q < 0.05) per tumor type
- [ ] Comparison of top hits: shared vs. type-specific complexes
- [ ] Sensitivity analysis summary

---

## Week 5: Expression Correlation, QC & Synthesis

### Person A — Expression–Mutation Correlation

- [ ] Retrieve matched RNA-seq (bulk) from St. Jude Cloud and CBTN
- [ ] For each significant complex: compute aggregate expression score (median TPM of member genes)
- [ ] Test association between complex mutation burden and complex expression (Spearman)
- [ ] Stratify by tumor type; test for inverse correlation (cf. Baron et al. desmosome result)
- [ ] Correct for tumor purity as covariate if estimates available
- [ ] Deliver: expression correlation results (`results/expression/`)

### Person B — Extended Validation & dN/dS Analysis

- [ ] Check dN/dS ratios for top enriched complexes to assess positive selection signal
- [ ] Test whether complex mutation correlates with proliferative gene signatures
- [ ] If scRNA-seq available for any subtype (St. Jude has some), check cell-type specificity
- [ ] Cross-reference top complexes against existing pediatric cancer literature
- [ ] Deliver: validation results (`results/validation/`)

### Person C — Synthesis, Figures & Write-up

- [ ] Review all results for batch effects (St. Jude vs. CBTN origin)
- [ ] Generate summary figures:
  - Heatmap of complex enrichment across tumor types
  - Expression–mutation correlation plots for top complexes
  - Comparison to Baron et al. adult cancer results where applicable
- [ ] Draft PoC findings document (internal report or preprint outline)
- [ ] Deliver: final figures (`figures/final/`), write-up (`docs/poc_report.md`)

### End-of-Week 5 Sync — PoC Review

- [ ] Review all results as a team
- [ ] Assess success criteria (see below)
- [ ] Identify follow-up priorities

---

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Small N per subtype | Underpowered enrichment | Merge St. Jude + CBTN + TARGET; complex-level aggregation |
| Germline contamination | False positive enrichment | Strict gnomAD + PoN filtering |
| WGS/WES mixing | Differential mutation sensitivity | Normalize by callable bases; WGS-only sensitivity analysis |
| Hypermutators | Dominate enrichment signals | Flag and exclude or model separately |
| Batch effects (St. Jude vs. CBTN) | Spurious cross-cohort signals | QC checks in Week 5; cohort-stratified analyses |
| Scope creep into network reconstruction | Timeline slip | Stick to curated complexes; NeST-style discovery is post-PoC |

---

## Tools & Infrastructure

| Component | Tool/Resource |
|---|---|
| Background mutation model | dNdScv (R) |
| Alternative enrichment | OncodriveFML |
| Complex databases | CORUM, hu.MAP 2.0 |
| Expression analysis | Python (scanpy, pandas), R (DESeq2) |
| Compute | TSCC/Pines or SDSC Cosmos (SLURM) |
| Data access | St. Jude Cloud, CAVATICA (CBTN/Kids First) |
| Version control | This repo (GitHub) |

---

## Success Criteria

1. ≥3 pediatric tumor types analyzed with N ≥ 50
2. Enrichment results generated for ≥500 curated complexes per tumor type
3. ≥1 novel significantly enriched complex identified (not previously reported in pediatric cancer)
4. Expression–mutation anticorrelation demonstrated for ≥1 top complex
5. Known biology recapitulated (e.g., SWI/SNF in rhabdoid tumors) as positive control

---

## Beyond PoC (Future Directions)

- Network-derived complex discovery (NeST-style hierarchical integration)
- Independent cohort validation (TARGET, INFORM, institutional cohorts)
- dN/dS evolutionary selection analysis per complex
- Single-cell or spatial transcriptomics for cell-type specificity
- Functional validation of top candidate complexes
- Integration with microbiome signatures (overlap with existing R03 aims)
