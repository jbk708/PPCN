# PedPanCancer-Networks

Identification of protein complexes under significant mutational selection across pediatric tumor types. Adapts the Δ-rank permutation framework from [Baron & Tagore et al. (2025)](https://doi.org/10.1038/s41588-025-02163-9) to pediatric cancers using somatic mutation data from St. Jude Cloud and CBTN/Kids First.

## Approach

1. **Background model** — dNdScv estimates per-gene expected mutation rates per tumor type
2. **Complex enrichment** — Per-gene Δ(observed − expected) ranks are averaged across complex members and compared against 100k permutations, with Benjamini-Hochberg correction
3. **Expression correlation** — Mutation burden vs. aggregate complex expression (Spearman), stratified by histology

## Data Sources

| Source | Description |
|---|---|
| [St. Jude Cloud](https://stjude.cloud) | PCGP somatic variants (WGS-predominant) |
| [CBTN / Kids First](https://cbtn.org) | OpenPBTA harmonized somatic MAFs (WGS + WES) |
| [CORUM](https://mips.helmholtz-muenchen.de/corum/) | ~4,000 curated mammalian protein complexes |
| [hu.MAP 2.0](http://humap2.proteincomplexes.org/) | Data-driven protein complex predictions |

## Setup

```bash
./setup.sh       # installs Python (uv or pip) and R packages in one step
```

Requires Python ≥ 3.11. R ≥ 4.0 is optional — the script will skip R packages if R is not available and print a warning.

## Usage

```bash
uv run ruff check scripts/   # lint
uv run ruff format scripts/  # auto-format
uv run ty check scripts/     # type check
uv run pytest tests/          # test
```

## Repo Structure

```
data/           Harmonized MAFs, complex membership tables (not committed)
scripts/        Analysis code (Python + R)
R/              R dependency management
results/        Per-tumor-type enrichment, expression, validation outputs
figures/        Plots and publication-ready figures
tests/          pytest suite
docs/           Research plan, reference paper, PoC report
```

## License

BSD 3-Clause. See [LICENSE](LICENSE).
