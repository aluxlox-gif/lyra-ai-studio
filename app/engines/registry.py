"""
LYRA AI STUDIO — Engine Registry

Pusat registrasi mesin AI.
Mesin yang terdaftar belum tentu sudah terhubung atau aktif.
"""

from copy import deepcopy


ENGINE_REGISTRY = {
    "image": {
        "id": "image",
        "name": "Image Engine",
        "status": "planned",
        "provider": None,
        "capabilities": [
            "text_to_image",
            "image_editing",
            "character_sheets",
            "storyboards",
            "reference_images",
        ],
        "description": (
            "Pembuatan dan pengeditan gambar, "
            "character sheet, serta storyboard."
        ),
    },
    "voice": {
        "id": "voice",
        "name": "Voice Engine",
        "status": "planned",
        "provider": "voicebox",
        "capabilities": [
            "text_to_speech",
            "speech_to_text",
            "voice_conversion",
            "audio_processing",
        ],
        "description": (
            "Pusat fitur suara dan pemrosesan audio. "
            "Ketersediaan setiap kemampuan bergantung "
            "pada mesin yang nantinya dihubungkan."
        ),
    },
    "video": {
        "id": "video",
        "name": "Video Engine",
        "status": "planned",
        "provider": "openmontage",
        "capabilities": [
            "scene_planning",
            "storyboard_workflow",
            "asset_continuity",
            "video_composition",
        ],
        "description": (
            "Perencanaan adegan, kontinuitas aset, "
            "dan alur produksi video."
        ),
    },
}


def list_engines():
    """Mengembalikan daftar seluruh mesin yang terdaftar."""
    return deepcopy(list(ENGINE_REGISTRY.values()))


def get_engine(engine_id: str):
    """Mengambil informasi satu mesin berdasarkan ID."""
    engine = ENGINE_REGISTRY.get(engine_id)

    if engine is None:
        return None

    return deepcopy(engine)


def get_engine_status():
    """Ringkasan status seluruh mesin."""
    engines = list_engines()

    return {
        "total": len(engines),
        "connected": sum(
            engine["status"] == "connected"
            for engine in engines
        ),
        "available": sum(
            engine["status"] == "available"
            for engine in engines
        ),
        "planned": sum(
            engine["status"] == "planned"
            for engine in engines
        ),
    }
