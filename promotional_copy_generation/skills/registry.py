"""Skill registry - supports retrieval by stage."""

from dataclasses import dataclass
from typing import Protocol

STAGES = (
    "context_enhance",
    "copy_write",
    "image_prompt",
)


@dataclass
class Skill:
    """Skill protocol: all Skills must implement."""

    id: str
    name: str
    stage: str
    description: str
    content: str

    def __post_init__(self):
        if self.stage not in STAGES:
            raise ValueError(f"stage must be one of {STAGES}, got {self.stage}")


_registry: dict[str, Skill] = {}
_stage_index: dict[str, list[Skill]] = {s: [] for s in STAGES}


def register_skill(skill: Skill) -> None:
    """Register a Skill."""
    _registry[skill.id] = skill
    if skill.stage not in _stage_index:
        _stage_index[skill.stage] = []
    if skill not in _stage_index[skill.stage]:
        _stage_index[skill.stage].append(skill)


def get_skills_for_stage(stage: str) -> list[Skill]:
    """Get all Skills for a stage."""
    return _stage_index.get(stage, []).copy()


def get_skill_by_id(skill_id: str) -> Skill | None:
    """Get Skill by ID."""
    return _registry.get(skill_id)


def clear_registry() -> None:
    """Clear registry (for testing)."""
    _registry.clear()
    for s in _stage_index:
        _stage_index[s].clear()
