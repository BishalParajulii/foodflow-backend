"""Placeholder API tests — only the project-level namespace exists."""

import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_api_v1_placeholder() -> None:
    client = APIClient()
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.data["version"] == "v1"


def test_project_root_placeholder() -> None:
    client = APIClient()
    response = client.get(reverse("project-root"))
    assert response.status_code == 200
