
def get_engine_status():
    return {
        "image": {
            "name": "Image Studio",
            "status": "planned",
            "connected": False
        },
        "video": {
            "name": "Video Studio",
            "status": "planned",
            "connected": False
        },
        "voice": {
            "name": "Voice Studio",
            "status": "adapter_available",
            "connected": False
        },
        "voicebox": {
            "name": "Voicebox",
            "status": "configuration_required",
            "connected": False
        },
        "openmontage": {
            "name": "OpenMontage",
            "status": "planned",
            "connected": False
        }
    }
    
