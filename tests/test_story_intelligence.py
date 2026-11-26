from app.story.intelligence import review_story
from app.story.schemas import StoryReviewRequest


def _story_payload():
    return StoryReviewRequest(
        logline="A courier discovers a secret that can change her city.",
        premise="A young courier must deliver a sealed message before sunrise while rival groups search for it.",
        protagonist_goal="Deliver the sealed message to the archive before sunrise and learn why it was entrusted to her.",
        stakes="If she fails, the archive will be destroyed and the evidence will disappear permanently.",
        central_conflict="A rival courier intercepts her route and forces her to choose between safety and revealing the truth.",
        scenes=[
            {
                "scene_number": 1,
                "beat_type": "hook",
                "title": "The wrong address",
                "visual_action": "The courier finds her own name on the sealed envelope.",
                "dramatic_question": "Why is her name inside a message she has not opened?",
                "estimated_duration_seconds": 10,
            },
            {
                "scene_number": 2,
                "beat_type": "escalation",
                "title": "The blocked route",
                "visual_action": "A rival blocks the only bridge.",
                "turning_point": True,
                "estimated_duration_seconds": 10,
            },
            {
                "scene_number": 3,
                "beat_type": "reversal",
                "title": "The hidden map",
                "visual_action": "The message reveals a second route and a larger secret.",
                "turning_point": True,
                "estimated_duration_seconds": 10,
            },
            {
                "scene_number": 4,
                "beat_type": "climax",
                "title": "The archive door",
                "visual_action": "She reaches the archive as the doors begin to close.",
                "turning_point": True,
                "estimated_duration_seconds": 10,
            },
            {
                "scene_number": 5,
                "beat_type": "payoff",
                "title": "The sender",
                "visual_action": "The archivist reveals who sent the message.",
                "payoff": "The message was sent by the courier's missing mentor.",
                "estimated_duration_seconds": 20,
            },
        ],
    )


def test_story_review_returns_transparent_weighted_scores():
    result = review_story(_story_payload(), target_duration_seconds=60)

    assert result.evaluation_mode == "deterministic_heuristic"
    assert result.overall_score >= 70
    assert result.dimensions["opening_hook"].score == 100
    assert result.dimensions["payoff"].score == 100
    assert result.estimated_duration_seconds == 60


def test_story_review_flags_missing_hook_and_payoff():
    payload = _story_payload()
    payload.scenes[0].beat_type = "setup"
    payload.scenes[0].dramatic_question = ""
    payload.scenes[-1].beat_type = "other"
    payload.scenes[-1].payoff = ""

    result = review_story(payload, target_duration_seconds=60)

    assert result.dimensions["opening_hook"].score == 25
    assert result.dimensions["payoff"].score == 30
    assert any("pembuka" in issue for issue in result.issues)
    assert any("payoff" in issue for issue in result.issues)
