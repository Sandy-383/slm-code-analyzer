import re
from dataclasses import dataclass, field
from enum import Enum


class Language(str, Enum):
    PYTHON     = "python"
    JAVASCRIPT = "javascript"
    CPP        = "cpp"
    JAVA       = "java"
    GO         = "go"
    RUST       = "rust"
    UNKNOWN    = "unknown"


@dataclass
class CodePayload:
    code: str
    language: Language
    loc: int
    char_count: int
    analyses: list[str] = field(default_factory=lambda: ["summary", "complexity", "workflow", "optimization"])


LANG_PATTERNS = {
    Language.PYTHON:     [r"def ", r"import ", r"print\(", r":\s*$"],
    Language.JAVASCRIPT: [r"function ", r"const ", r"let ", r"=>"],
    Language.CPP:        [r"#include", r"std::", r"cout"],
    Language.JAVA:       [r"public class", r"System\.out", r"void main"],
    Language.GO:         [r"^package ", r'^import "'],
    Language.RUST:       [r"fn ", r"let mut", r"use std"],
}


def detect_language(code: str) -> Language:
    for lang, patterns in LANG_PATTERNS.items():
        if any(re.search(p, code, re.MULTILINE) for p in patterns):
            return lang
    return Language.UNKNOWN


def normalize_code(raw: str) -> str:
    """Strip trailing whitespace, normalize line endings, remove BOM."""
    code = raw.replace("\r\n", "\n").replace("\r", "\n")
    code = code.lstrip("\ufeff")
    lines = [line.rstrip() for line in code.split("\n")]
    return "\n".join(lines).strip()


def build_payload(
    code: str,
    language: str = "auto",
    analyses: list[str] = None,
) -> CodePayload:
    if analyses is None:
        analyses = ["summary", "complexity", "workflow", "optimization"]

    code = normalize_code(code)

    if not code:
        raise ValueError("Code input is empty after normalization.")
    if len(code.splitlines()) > 500:
        raise ValueError("Input exceeds 500 line limit.")

    lang = (
        detect_language(code)
        if language == "auto"
        else Language(language)
    )

    return CodePayload(
        code=code,
        language=lang,
        loc=len(code.splitlines()),
        char_count=len(code),
        analyses=analyses,
    )
