"""Pull and filter samples from the CCDI ecDNA Catalog API.

Fetches Medulloblastoma (MBL) and ATRT biosamples, removes ICGC-cohort
samples, and retains only SHH-subgroup MBL and all ATRT records.

Output: data/ccdi-pull/shh_mbl_atrt_final.csv

Usage:
    uv run --no-sync scripts/pull_ccdi_samples.py
    uv run --no-sync scripts/pull_ccdi_samples.py --out-dir data/ccdi-pull
"""

from __future__ import annotations

import argparse
import ast
import logging
from pathlib import Path

import pandas as pd

from scripts.utils.ecdna_client import EcdnaClient

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def pull_patients(client: EcdnaClient, cancer_types: list[str]) -> pd.DataFrame:
    """Fetch patients for each cancer type and concatenate.

    Args:
        client: Instantiated EcdnaClient.
        cancer_types: List of cancer type codes to fetch.

    Returns:
        Combined DataFrame with a parsed ``cohort`` string column.
    """
    frames = []
    for ct in cancer_types:
        df = client.get_patients_df(cancer_type=ct)
        log.info("  patients  %-6s %d rows", ct, len(df))
        frames.append(df)
    patients = pd.concat(frames, ignore_index=True)
    patients["cohort"] = patients["cohorts"].apply(
        lambda v: ",".join(c["name"] for c in (v if isinstance(v, list) else ast.literal_eval(v)))
    )
    return patients


def pull_biosamples(client: EcdnaClient, cancer_types: list[str]) -> pd.DataFrame:
    """Fetch biosamples for each cancer type and concatenate.

    Args:
        client: Instantiated EcdnaClient.
        cancer_types: List of cancer type codes to fetch.

    Returns:
        Combined DataFrame of biosample records.
    """
    frames = []
    for ct in cancer_types:
        df = client.get_biosamples_df(cancer_type=ct)
        log.info("  biosamples %-6s %d rows", ct, len(df))
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def merge_and_filter(patients: pd.DataFrame, biosamples: pd.DataFrame) -> pd.DataFrame:
    """Merge patients into biosamples, remove ICGC, keep SHH MBL and ATRT.

    Args:
        patients: Patient DataFrame with ``cohort`` column.
        biosamples: Biosample DataFrame.

    Returns:
        Filtered DataFrame at biosample granularity.
    """
    merged = biosamples.merge(
        patients[["patient_id", "cohort", "sex", "OS_status", "OS_months", "no_of_biosamples"]],
        on="patient_id",
        how="left",
    )

    no_icgc = merged[~merged["cohort"].str.contains("ICGC", na=False)]
    log.info("Removed ICGC: %d → %d rows", len(merged), len(no_icgc))

    is_shh_mbl = (no_icgc["cancer_type"] == "MBL") & (no_icgc["cancer_subclass"] == "SHH")
    is_atrt = no_icgc["cancer_type"] == "ATRT"
    final = no_icgc[is_shh_mbl | is_atrt].reset_index(drop=True)
    log.info("Kept SHH MBL + ATRT: %d rows", len(final))

    return final


def main(out_dir: Path) -> None:
    """Run the full pull-and-filter pipeline.

    Args:
        out_dir: Directory to write output CSVs.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    client = EcdnaClient()

    log.info("Fetching patients...")
    patients = pull_patients(client, ["MBL", "ATRT"])

    log.info("Fetching biosamples...")
    biosamples = pull_biosamples(client, ["MBL", "ATRT"])

    # Persist raw pulls
    patients.to_csv(out_dir / "patients_mbl_atrt.csv", index=False)
    biosamples.to_csv(out_dir / "biosamples_mbl_atrt.csv", index=False)

    log.info("Filtering...")
    final = merge_and_filter(patients, biosamples)

    out_path = out_dir / "shh_mbl_atrt_final.csv"
    final.to_csv(out_path, index=False)
    log.info("Saved → %s", out_path)

    # Summary
    summary = final.groupby(["cancer_type", "cancer_subclass"], dropna=False).size()
    log.info("\n%s", summary.to_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/ccdi-pull"),
        help="Output directory (default: data/ccdi-pull)",
    )
    args = parser.parse_args()
    main(args.out_dir)
