"""Transparent, deterministic story-structure checks (not an LLM judge)."""

from app.story.schemas import (
    StoryDimensionScore,
    StoryReviewRequest,
    StoryReviewResponse,
)


def _bounded_score(value: float) -> int:
    return max(0, min(100, round(value)))


def review_story(payload: StoryReviewRequest, target_duration_seconds: int) -> StoryReviewResponse:
    scenes = sorted(payload.scenes, key=lambda item: item.scene_number)
    first_scene = scenes[0]
    last_scene = scenes[-1]
    issues: list[str] = []
    suggestions: list[str] = []

    hook_present = bool(first_scene.dramatic_question.strip()) or first_scene.beat_type == "hook"
    hook_score = 100 if hook_present else 25
    if not hook_present:
        issues.append("Adegan pembuka belum memiliki pertanyaan dramatik atau penanda hook yang eksplisit.")
        suggestions.append("Mulai dengan anomali, pilihan sulit, ancaman, atau hasil yang memancing pertanyaan penonton.")

    goal_length = len(payload.protagonist_goal.strip())
    goal_score = _bounded_score(35 + min(goal_length, 100) * 0.65)
    if goal_length < 30:
        issues.append("Tujuan protagonis masih terlalu umum untuk menjadi penggerak adegan.")
        suggestions.append("Nyatakan apa yang ingin dicapai protagonis, batas waktunya, dan hambatan langsungnya.")

    stakes_length = len(payload.stakes.strip())
    stakes_score = _bounded_score(30 + min(stakes_length, 110) * 0.64)
    if stakes_length < 30:
        issues.append("Konsekuensi kegagalan belum cukup konkret.")
        suggestions.append("Tunjukkan apa yang hilang, berubah, atau memburuk jika protagonis gagal.")

    conflict_length = len(payload.central_conflict.strip())
    conflict_score = _bounded_score(30 + min(conflict_length, 120) * 0.58)
    if conflict_length < 35:
        issues.append("Konflik utama belum terdefinisi dengan tajam.")
        suggestions.append("Perjelas pihak atau kekuatan yang menghalangi tujuan protagonis dan mengapa konflik sulit diselesaikan.")

    turning_points = sum(1 for scene in scenes if scene.turning_point)
    escalation_score = _bounded_score(25 + min(len(scenes), 8) * 6 + min(turning_points, 4) * 8)
    if len(scenes) >= 4 and turning_points < 2:
        issues.append("Eskalasi belum memiliki cukup titik balik yang dapat dikenali.")
        suggestions.append("Tambahkan perubahan situasi yang menaikkan risiko; jangan hanya mengulang hambatan yang sama.")

    payoff_present = bool(last_scene.payoff.strip()) or last_scene.beat_type in {"payoff", "climax", "cliffhanger"}
    payoff_score = 100 if payoff_present else 30
    if not payoff_present:
        issues.append("Akhir cerita belum menunjukkan payoff atau cliffhanger yang disengaja.")
        suggestions.append("Bayar janji cerita utama atau akhiri dengan pertanyaan baru yang spesifik dan relevan.")

    estimated_duration = sum(scene.estimated_duration_seconds for scene in scenes)
    duration_target = max(1, target_duration_seconds)
    duration_deviation = abs(estimated_duration - duration_target) / duration_target
    pacing_score = _bounded_score(100 - min(duration_deviation * 125, 100))
    if duration_deviation > 0.25:
        issues.append("Estimasi durasi adegan menyimpang lebih dari 25% dari target proyek.")
        suggestions.append("Sesuaikan jumlah adegan atau durasi tiap adegan dengan target runtime; hindari memperpanjang adegan tanpa fungsi dramatik.")

    numbers = [scene.scene_number for scene in scenes]
    if len(numbers) != len(set(numbers)):
        issues.append("Nomor adegan duplikat ditemukan.")
        suggestions.append("Gunakan nomor adegan unik dan berurutan agar storyboard dapat dirakit secara deterministik.")

    dimensions = {
        "opening_hook": StoryDimensionScore(
            score=hook_score,
            rationale="Memeriksa pertanyaan dramatik atau beat hook eksplisit pada adegan pertama.",
        ),
        "protagonist_goal": StoryDimensionScore(
            score=goal_score,
            rationale="Mengukur kelengkapan deskripsi tujuan protagonis; bukan penilaian semantik AI.",
        ),
        "stakes": StoryDimensionScore(
            score=stakes_score,
            rationale="Mengukur kelengkapan deskripsi konsekuensi; bukan penilaian semantik AI.",
        ),
        "central_conflict": StoryDimensionScore(
            score=conflict_score,
            rationale="Mengukur kelengkapan deskripsi konflik utama; bukan penilaian semantik AI.",
        ),
        "escalation": StoryDimensionScore(
            score=escalation_score,
            rationale="Menggunakan jumlah adegan dan titik balik yang ditandai secara eksplisit.",
        ),
        "payoff": StoryDimensionScore(
            score=payoff_score,
            rationale="Memeriksa payoff atau cliffhanger eksplisit pada adegan terakhir.",
        ),
        "pacing": StoryDimensionScore(
            score=pacing_score,
            rationale="Membandingkan total estimasi durasi adegan dengan target runtime proyek.",
        ),
    }

    weights = {
        "opening_hook": 0.20,
        "protagonist_goal": 0.10,
        "stakes": 0.15,
        "central_conflict": 0.15,
        "escalation": 0.15,
        "payoff": 0.15,
        "pacing": 0.10,
    }
    overall = _bounded_score(sum(dimensions[name].score * weight for name, weight in weights.items()))
    rating = (
        "strong" if overall >= 85 else
        "promising" if overall >= 70 else
        "developing" if overall >= 50 else
        "weak"
    )

    return StoryReviewResponse(
        overall_score=overall,
        rating=rating,
        dimensions=dimensions,
        issues=issues,
        suggestions=suggestions,
        scene_count=len(scenes),
        estimated_duration_seconds=estimated_duration,
    )
