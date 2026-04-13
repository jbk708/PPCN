"""Client for the CCDI Childhood Cancer ecDNA Catalog API.

API docs: https://ccdi-ecdna.org/api/schemas/
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://ccdi-ecdna.org/api"


class EcdnaClient:
    """Thin wrapper around the CCDI ecDNA REST API.

    Args:
        base_url: Override the default API base URL.
        timeout: Request timeout in seconds.
    """

    def __init__(self, base_url: str = BASE_URL, timeout: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, endpoint: str, **params: Any) -> list[dict]:
        """Send a GET request and return the JSON list response.

        Args:
            endpoint: API path relative to base_url (e.g. "/patients/").
            **params: Query-string parameters forwarded to requests.get.

        Returns:
            Parsed JSON response as a list of dicts.

        Raises:
            requests.HTTPError: On non-2xx status codes.
        """
        url = f"{self.base_url}{endpoint}"
        params = {k: v for k, v in params.items() if v is not None}
        logger.debug("GET %s params=%s", url, params)
        resp = requests.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _filter(
        records: list[dict],
        cancer_type: str | None = None,
        cancer_subclass: str | None = None,
    ) -> list[dict]:
        """Filter records by cancer_type and/or cancer_subclass (case-insensitive)."""
        filtered = records
        if cancer_type is not None:
            ct_lower = cancer_type.lower()
            filtered = [r for r in filtered if r.get("cancer_type", "").lower() == ct_lower]
        if cancer_subclass is not None:
            cs_lower = cancer_subclass.lower()
            filtered = [r for r in filtered if (r.get("cancer_subclass") or "").lower() == cs_lower]
        return filtered

    def get_patients(
        self,
        cancer_type: str | None = None,
        cancer_subclass: str | None = None,
    ) -> list[dict]:
        """Fetch patients, optionally filtered by cancer type/subclass.

        Args:
            cancer_type: Case-insensitive cancer type filter.
            cancer_subclass: Case-insensitive cancer subclass filter.

        Returns:
            List of patient dicts matching the filters.
        """
        patients = self._get("/patients/")
        return self._filter(patients, cancer_type=cancer_type, cancer_subclass=cancer_subclass)

    def get_patients_df(
        self,
        cancer_type: str | None = None,
        cancer_subclass: str | None = None,
    ) -> pd.DataFrame:
        """Fetch patients as a DataFrame, optionally filtered.

        Args:
            cancer_type: Case-insensitive cancer type filter.
            cancer_subclass: Case-insensitive cancer subclass filter.

        Returns:
            DataFrame of patient records.
        """
        return pd.DataFrame(
            self.get_patients(cancer_type=cancer_type, cancer_subclass=cancer_subclass)
        )

    def get_biosamples(
        self,
        cancer_type: str | None = None,
        cancer_subclass: str | None = None,
    ) -> list[dict]:
        """Fetch biosamples, optionally filtered by cancer type/subclass.

        Args:
            cancer_type: Case-insensitive cancer type filter.
            cancer_subclass: Case-insensitive cancer subclass filter.

        Returns:
            List of biosample dicts matching the filters.
        """
        biosamples = self._get("/biosamples/")
        return self._filter(biosamples, cancer_type=cancer_type, cancer_subclass=cancer_subclass)

    def get_biosamples_df(
        self,
        cancer_type: str | None = None,
        cancer_subclass: str | None = None,
    ) -> pd.DataFrame:
        """Fetch biosamples as a DataFrame, optionally filtered.

        Args:
            cancer_type: Case-insensitive cancer type filter.
            cancer_subclass: Case-insensitive cancer subclass filter.

        Returns:
            DataFrame of biosample records.
        """
        return pd.DataFrame(
            self.get_biosamples(cancer_type=cancer_type, cancer_subclass=cancer_subclass)
        )

    def get_amplicons(
        self,
        biosample_id: str | None = None,
        patient_id: str | None = None,
    ) -> list[dict]:
        """Fetch amplicons with optional server-side filtering.

        Args:
            biosample_id: Filter by biosample ID (server-side).
            patient_id: Filter by patient ID (server-side).

        Returns:
            List of amplicon dicts.
        """
        return self._get("/amplicons/", biosample_id=biosample_id, patient_id=patient_id)

    def get_amplified_genes(self) -> list[dict]:
        """Fetch the full list of amplified genes.

        Returns:
            List of amplified-gene dicts.
        """
        return self._get("/amplified-genes/")

    def get_gene_annotated_patients(self, gene_name: str) -> list[dict]:
        """Fetch patients annotated with amplification status for a gene.

        Args:
            gene_name: HUGO gene symbol.

        Returns:
            List of annotated patient dicts.
        """
        url = f"{self.base_url}/gene-annotate-patient/"
        resp = requests.post(url, json={"gene_name": gene_name}, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
