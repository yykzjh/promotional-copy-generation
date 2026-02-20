"""Skill loader - auto-discover from files/directories."""

import re
from pathlib import Path

from .registry import Skill, register_skill

FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
)


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter, return (meta, body)."""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content

    import yaml
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except Exception:
        meta = {}
    body = content[match.end() :].strip()
    return meta, body


def load_skill_from_file(path: Path) -> Skill | None:
    """Load Skill from a single file."""
    if not path.exists() or not path.is_file():
        return None

    content = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(content)

    skill_id = meta.get("id") or path.stem
    name = meta.get("name") or skill_id
    stage = meta.get("stage", "copy_write")
    description = meta.get("description", "")

    return Skill(
        id=skill_id,
        name=name,
        stage=stage,
        description=description,
        content=body or content,
    )


def load_skills_from_dir(dir_path: Path) -> list[Skill]:
    """Load all Skills from directory (recursive *.md)."""
    skills: list[Skill] = []
    for f in dir_path.rglob("*.md"):
        skill = load_skill_from_file(f)
        if skill:
            skills.append(skill)
    return skills


def load_skills_from_dirs(dirs: list[Path]) -> list[Skill]:
    """Load Skills from multiple directories and register them."""
    all_skills: list[Skill] = []
    for d in dirs:
        if not d.exists():
            continue
        if d.is_file():
            s = load_skill_from_file(d)
            if s:
                all_skills.append(s)
        else:
            all_skills.extend(load_skills_from_dir(d))

    for s in all_skills:
        register_skill(s)
    return all_skills
