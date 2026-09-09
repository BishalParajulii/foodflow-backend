"""API docs grouping: every /api/v1/* operation belongs to an app tag."""

import pytest
from drf_spectacular.generators import SchemaGenerator

EXPECTED_TAGS = {
    "/api/v1/auth/": "Auth",
    "/api/v1/restaurants/": "Restaurants",
    "/api/v1/menu/": "Menu",
}


def _operations_by_path():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    assert schema is not None
    return schema["paths"]


@pytest.mark.django_db
def test_v1_endpoints_grouped_by_app_tag():
    paths = _operations_by_path()
    v1_paths = [p for p in paths if p.startswith("/api/v1/") and p != "/api/v1/"]
    assert v1_paths, "expected versioned endpoints in the schema"

    for path, operations in paths.items():
        if not path.startswith("/api/v1/") or path == "/api/v1/":
            continue
        prefix = next(pre for pre in EXPECTED_TAGS if path.startswith(pre))
        for method, operation in operations.items():
            assert operation.get("tags") == [EXPECTED_TAGS[prefix]], (
                f"{method.upper()} {path} tags={operation.get('tags')}"
            )


def test_tag_metadata_present():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    assert {t["name"] for t in schema.get("tags", [])} == {
        "Auth",
        "Restaurants",
        "Menu",
    }
