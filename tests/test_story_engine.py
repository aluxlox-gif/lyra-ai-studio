import asyncio

from app.engines.adapters.story_engine import StoryEngineAdapter
from app.engines.registry import get_engine_status


def test_registry_lists_story_engine_as_planned():
    story = get_engine_status()["story"]
    assert story["name"] == "Story Engine"
    assert story["status"] == "planned"
    assert story["connected"] is False


def test_adapter_info_and_capabilities():
    adapter = StoryEngineAdapter()
    info = adapter.get_info()
    assert info["engine_id"] == "story"
    assert info["engine_name"] == "Story Engine"
    assert info["capabilities"] == [
        "story_development",
        "storyboard",
        "illustration",
        "narration",
        "assembly",
    ]


def test_pipeline_stages_map_to_existing_engines():
    stages = StoryEngineAdapter().get_pipeline()
    assert [stage["id"] for stage in stages] == [
        "story_development",
        "storyboard",
        "illustration",
        "narration",
        "assembly",
    ]
    assert {stage["engine"] for stage in stages} <= {
        "hermes",
        "image",
        "voicebox",
        "video",
    }
    assert all(stage["status"] == "pending" for stage in stages)


def test_health_check_reports_planned_not_connected():
    result = asyncio.run(StoryEngineAdapter().health_check())
    assert result["connected"] is False
    assert result["status"] == "planned"
    assert len(result["stages"]) == 5
