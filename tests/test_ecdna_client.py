"""Tests for the CCDI ecDNA API client."""

import json
from unittest.mock import patch

import pytest
from scripts.utils.ecdna_client import EcdnaClient


@pytest.fixture()
def sample_patients() -> list[dict]:
    """Minimal patient records covering several cancer types."""
    return [
        {
            "patient_id": "P001",
            "sex": "M",
            "cohorts": [{"name": "PBTA"}],
            "age_at_diagnosis": 5,
            "cancer_type": "Neuroblastoma",
            "cancer_subclass": "MYCN-amplified",
            "amplicon_class": "ecDNA",
            "OS_status": "A",
            "OS_months": 24.0,
            "no_of_biosamples": 1,
        },
        {
            "patient_id": "P002",
            "sex": "F",
            "cohorts": [{"name": "PBTA"}],
            "age_at_diagnosis": 8,
            "cancer_type": "Neuroblastoma",
            "cancer_subclass": "Non-MYCN",
            "amplicon_class": "BFB",
            "OS_status": "A",
            "OS_months": 36.0,
            "no_of_biosamples": 2,
        },
        {
            "patient_id": "P003",
            "sex": "M",
            "cohorts": [{"name": "PCGP"}],
            "age_at_diagnosis": 12,
            "cancer_type": "Medulloblastoma",
            "cancer_subclass": "SHH",
            "amplicon_class": "ecDNA",
            "OS_status": "D",
            "OS_months": 18.0,
            "no_of_biosamples": 1,
        },
    ]


class _FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, data: list[dict], status_code: int = 200) -> None:
        self.status_code = status_code
        self.text = json.dumps(data)

    def json(self) -> list[dict]:
        return json.loads(self.text)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            from requests.exceptions import HTTPError

            raise HTTPError(response=self)


class TestGetPatients:
    """Tests for EcdnaClient.get_patients."""

    @patch("scripts.utils.ecdna_client.requests.get")
    def test_returns_all_when_no_filters(self, mock_get, sample_patients):
        mock_get.return_value = _FakeResponse(sample_patients)
        client = EcdnaClient()
        result = client.get_patients()
        assert len(result) == 3

    @patch("scripts.utils.ecdna_client.requests.get")
    def test_filter_by_cancer_type(self, mock_get, sample_patients):
        mock_get.return_value = _FakeResponse(sample_patients)
        client = EcdnaClient()
        result = client.get_patients(cancer_type="Neuroblastoma")
        assert len(result) == 2
        assert all(p["cancer_type"] == "Neuroblastoma" for p in result)

    @patch("scripts.utils.ecdna_client.requests.get")
    def test_filter_by_cancer_subclass(self, mock_get, sample_patients):
        mock_get.return_value = _FakeResponse(sample_patients)
        client = EcdnaClient()
        result = client.get_patients(cancer_subclass="SHH")
        assert len(result) == 1
        assert result[0]["patient_id"] == "P003"

    @patch("scripts.utils.ecdna_client.requests.get")
    def test_filter_by_both(self, mock_get, sample_patients):
        mock_get.return_value = _FakeResponse(sample_patients)
        client = EcdnaClient()
        result = client.get_patients(cancer_type="Neuroblastoma", cancer_subclass="MYCN-amplified")
        assert len(result) == 1
        assert result[0]["patient_id"] == "P001"

    @patch("scripts.utils.ecdna_client.requests.get")
    def test_filter_case_insensitive(self, mock_get, sample_patients):
        mock_get.return_value = _FakeResponse(sample_patients)
        client = EcdnaClient()
        result = client.get_patients(cancer_type="neuroblastoma")
        assert len(result) == 2

    @patch("scripts.utils.ecdna_client.requests.get")
    def test_no_matches_returns_empty(self, mock_get, sample_patients):
        mock_get.return_value = _FakeResponse(sample_patients)
        client = EcdnaClient()
        result = client.get_patients(cancer_type="Osteosarcoma")
        assert result == []

    @patch("scripts.utils.ecdna_client.requests.get")
    def test_to_dataframe(self, mock_get, sample_patients):
        mock_get.return_value = _FakeResponse(sample_patients)
        client = EcdnaClient()
        df = client.get_patients_df(cancer_type="Neuroblastoma")
        assert len(df) == 2
        assert "patient_id" in df.columns
        assert "cancer_type" in df.columns


class TestGetBiosamples:
    """Tests for EcdnaClient.get_biosamples."""

    @patch("scripts.utils.ecdna_client.requests.get")
    def test_filter_by_cancer_type(self, mock_get):
        biosamples = [
            {
                "biosample_id": "BS001",
                "patient_id": "P001",
                "cancer_type": "Neuroblastoma",
                "cancer_subclass": "MYCN-amplified",
                "amplicon_class": "ecDNA",
                "ecDNA_sequences_detected": 3,
            },
            {
                "biosample_id": "BS002",
                "patient_id": "P003",
                "cancer_type": "Medulloblastoma",
                "cancer_subclass": "SHH",
                "amplicon_class": "ecDNA",
                "ecDNA_sequences_detected": 1,
            },
        ]
        mock_get.return_value = _FakeResponse(biosamples)
        client = EcdnaClient()
        result = client.get_biosamples(cancer_type="Neuroblastoma")
        assert len(result) == 1
        assert result[0]["biosample_id"] == "BS001"
