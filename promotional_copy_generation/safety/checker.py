"""Input/output safety check - rule-based + LLM dual verification."""

import json
import re
from pathlib import Path

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from ..config import settings


def _load_forbidden_words() -> set[str]:
    """Load forbidden words list."""
    path = settings.forbidden_words_file
    if not path:
        return set()
    p = Path(path)
    if not p.exists():
        return set()
    words = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            words.add(line)
    return words


def _check_text_forbidden(text: str, forbidden: set[str]) -> tuple[bool, str]:
    """Rule-based check: whether text contains forbidden words."""
    if not text:
        return True, ""
    for w in forbidden:
        if w in text:
            return False, f"Contains forbidden word: {w}"
    return True, ""


def _check_text_llm(text: str, check_type: str = "input") -> tuple[bool, str]:
    """LLM check: determine whether text is compliant."""
    if not text or not settings.safety_use_llm:
        return True, ""

    prompt_path = settings.config_path / "prompts" / "safety_check.txt"
    if prompt_path.exists():
        template = prompt_path.read_text(encoding="utf-8")
    else:
        template = (
            "You are a content compliance reviewer. Determine whether the following text is compliant "
            "(illegal content, forbidden words, advertising law violations, false advertising, etc.).\n"
            "Text:\n---\n{content}\n---\n"
            "Output strictly in JSON format: {{\"passed\": true/false, \"reason\": \"explanation\"}}\n"
        )

    prompt = template.format(content=text[:2000])  # Limit length

    llm = ChatOpenAI(
        base_url=settings.main_model_url,
        api_key=settings.main_model_api_key,
        model=settings.safety_llm_model or settings.main_model,
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content if hasattr(response, "content") else str(response)
        # Parse JSON
        for match in re.finditer(r"\{[^{}]*\"passed\"[^{}]*\}", content):
            try:
                data = json.loads(match.group())
                if "passed" in data:
                    passed = data.get("passed", True)
                    reason = data.get("reason", "")
                    return passed, reason
            except json.JSONDecodeError:
                continue
    except Exception:
        pass
    # Default to pass when LLM call fails to avoid blocking
    return True, ""


def _check_text(text: str, forbidden: set[str], use_llm: bool = True) -> tuple[bool, str]:
    """Combined check: rule-based first, then LLM."""
    ok, msg = _check_text_forbidden(text, forbidden)
    if not ok:
        return False, msg
    if use_llm and text.strip():
        ok, msg = _check_text_llm(text)
        if not ok:
            return False, msg
    return True, ""


def check_input(
    requirements: str,
    description: str | None = None,
    images: list[bytes] | None = None,
) -> tuple[bool, str]:
    """Input safety check (rule-based + LLM)."""
    forbidden = _load_forbidden_words()
    use_llm = settings.safety_use_llm

    ok, msg = _check_text(requirements, forbidden, use_llm)
    if not ok:
        return False, msg
    if description:
        ok, msg = _check_text(description, forbidden, use_llm)
        if not ok:
            return False, msg
    # Image check: placeholder only, can be extended to call multimodal model
    return True, ""


def check_output(
    copy: str,
    image_prompts: list[str] | None = None,
    generated_images: list[bytes] | None = None,
) -> tuple[bool, str]:
    """Output safety check (rule-based + LLM)."""
    forbidden = _load_forbidden_words()
    use_llm = settings.safety_use_llm

    ok, msg = _check_text(copy, forbidden, use_llm)
    if not ok:
        return False, msg
    if image_prompts:
        for p in image_prompts:
            ok, msg = _check_text(p, forbidden, use_llm)
            if not ok:
                return False, msg
    return True, ""
