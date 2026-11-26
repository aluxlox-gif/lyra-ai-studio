from app.production.schemas import ProjectCreate
from app.production.store import ProductionStore


def test_project_round_trip_persists_all_core_fields(tmp_path):
    store = ProductionStore(tmp_path / "production.sqlite3")
    payload = ProjectCreate(
        title="Pilot Episode",
        description="A short cinematic story",
        language="id",
        aspect_ratio="9:16",
        visual_style="cinematic illustration",
        target_duration_seconds=90,
        metadata={"genre": "mystery", "tags": ["pilot", "short"]},
    )

    created = store.create_project(payload)
    loaded = store.get_project(created.id)

    assert loaded is not None
    assert loaded.id == created.id
    assert loaded.title == "Pilot Episode"
    assert loaded.aspect_ratio == "9:16"
    assert loaded.target_duration_seconds == 90
    assert loaded.metadata == {"genre": "mystery", "tags": ["pilot", "short"]}
    assert loaded.created_at == created.created_at


def test_unknown_project_returns_none(tmp_path):
    store = ProductionStore(tmp_path / "production.sqlite3")

    assert store.get_project("missing-project") is None
