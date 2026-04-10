# PedPanCancer-Networks

## Project Overview

Identify protein complexes under significant mutational selection across pediatric tumor types. Adapts the Baron & Tagore et al. (Nat. Genet. 2025) Δ-rank permutation framework — originally applied to desmosomes in melanoma — to pediatric cancers using somatic mutation data from St. Jude Cloud and CBTN/Kids First.

## Data Sources

- **Somatic mutations:** St. Jude Cloud (PCGP, WGS-predominant), CBTN/OpenPBTA (WGS+WES), optionally TARGET
- **Complex definitions:** CORUM (~4,000 curated complexes), hu.MAP 2.0
- **Expression:** Matched bulk RNA-seq from both platforms; scRNA-seq where available

## Key Methods

- **Background model:** dNdScv (preferred over MutSigCV for low-TMB pediatric genomes)
- **Enrichment:** Per-gene Δ(observed − expected) → rank → complex average rank vs. 100k permutations → BH-corrected P-values
- **Expression correlation:** Mutation burden vs. aggregate complex expression (Spearman), stratified by tumor type

## Repo Structure

```
data/                   # Harmonized MAFs, complex membership tables (not committed; .gitignore)
  stjude/               # St. Jude Cloud somatic MAFs
  cbtn/                 # CBTN / OpenPBTA somatic MAFs
  complexes/            # CORUM, hu.MAP 2.0 membership tables
scripts/                # Analysis code (Python + R)
  utils/                # Shared I/O, filtering, gene-mapping utilities
  sensitivity/          # Sensitivity analysis wrappers
results/                # Per-tumor-type outputs
  dndscv/               # Background model results
  enrichment/           # Complex enrichment tables
  expression/           # Expression correlation results
  validation/           # dN/dS, literature cross-ref
figures/                # Plots and summary figures
  final/                # Publication-ready figures
docs/                   # Research plan, reference paper, PoC report
```

## Conventions

- Python and R; Google docstring format for Python
- All coordinates hg38
- Gene symbols: HUGO
- Variant filtering: nonsynonymous coding only; gnomAD AF > 0.001 and PoN excluded
- Hypermutated samples flagged and handled via sensitivity analysis

## Development Workflow

1. Branch from main
2. Stub functions/classes with signatures and docstrings
3. Check `tests/` for existing coverage
4. Write tests before implementing; use fixtures where appropriate
5. Implement to pass tests
6. Run code simplifier
7. Run full test suite
8. Run linters

## Commands

```bash
uv sync                                        # install deps
uv sync --extra dev                            # install with dev deps
uv run --no-sync pytest tests/                 # run tests
uv run --no-sync pytest tests/test_foo.py      # single test file
uv run --no-sync pytest --cov=scripts tests/   # with coverage
uv run --no-sync ruff check .                  # lint
uv run --no-sync ruff format .                 # format
uv run --no-sync ty check                      # type check
```

**Note:** Always pass `--no-sync` to `uv run` to skip automatic dependency sync. Run `uv sync` explicitly when updating dependencies.

## Code Quality

- Always fix linter and type checker issues, even outside current ticket scope
- Self-documenting: clear naming and type hints; only comment non-obvious logic
- Test-driven: write tests before implementation
- Use pytest fixtures from `tests/conftest.py`; don't duplicate existing coverage

## Git Conventions

- No Co-Authored-By lines in commits or PRs
- Branch: `{prefix}-{ticket}-{name}` (prefixes: feat, fix, refactor, docs, test)
- Commit: `{PREFIX}-{ticket}: {description}`
