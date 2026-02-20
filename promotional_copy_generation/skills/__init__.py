"""Skills module - stage-based registration and loading."""

from .registry import Skill, get_skills_for_stage, register_skill
from .loader import load_skills_from_dirs

__all__ = ["Skill", "get_skills_for_stage", "register_skill", "load_skills_from_dirs"]
