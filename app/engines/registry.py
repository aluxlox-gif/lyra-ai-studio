def get_engine_status(voicebox_configured: bool = False):
    voicebox_status = "configuration_required"
    if voicebox_configured:
        voicebox_status = "configured_not_checked"

    return {
        "image": {
            "name": "Image Studio",
            "status": "planned",
            "connected": False,
        },
        "video": {
            "name": "Video Studio",
            "status": "planned",
            "connected": False,
        },
        "voice": {
            "name": "Voice Studio",
            "status": "adapter_available",
            "connected": False,
        },
        "voicebox": {
            "name": "LYRA VOICEBOX CLOUD",
            "status": voicebox_status,
            "configured": voicebox_configured,
            "connected": False,
        },
        "openmontage": {
            "name": "OpenMontage",
            "status": "planned",
            "connected": False,
        },
    }
