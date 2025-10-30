import os

# значения по умолчанию
SCENE_INTRO_TIME = os.getenv("SCENE_INTRO_TIME", "08:30")

try:
    SCENE_INTRO_DURATION = int(os.getenv("SCENE_INTRO_DURATION", "180"))
except ValueError:
    SCENE_INTRO_DURATION = 180

SCENE_INTRO_REPLY = os.getenv("SCENE_INTRO_REPLY", "default")
