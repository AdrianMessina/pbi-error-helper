"""Knowledge base loader, search engine, and diagnostic matcher.

Loads markdown files with YAML frontmatter from `errors/` and builds an
in-memory index plus a Whoosh full-text index for search. The `diagnose`
function does fuzzy matching against pasted error text and returns
ranked results with confidence scores.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable

import frontmatter
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import ID, KEYWORD, NUMERIC, TEXT, Schema
from whoosh.filedb.filestore import RamStorage
from whoosh.qparser import MultifieldParser, OrGroup

try:
    ROOT = Path(__file__).parent
except NameError:
    ROOT = Path.cwd()
ERRORS_DIR = ROOT / "errors"
MEDIA_DIR = ROOT / "media"

CANONICAL_SECTIONS = ["Síntoma", "Causa", "Solución paso a paso", "Cómo prevenirlo", "Fuentes"]


@dataclass
class ErrorEntry:
    id: str
    title: str
    category: str
    severity: str
    tools: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    videos: list[str] = field(default_factory=list)
    body: str = ""
    path: Path | None = None

    @property
    def image_paths(self) -> list[Path]:
        return [MEDIA_DIR / "images" / img for img in self.images]

    @property
    def video_paths(self) -> list[Path]:
        return [MEDIA_DIR / "videos" / vid for vid in self.videos]

    @property
    def sections(self) -> dict[str, str]:
        return _split_sections(self.body)

    @property
    def snippet(self) -> str:
        sections = self.sections
        for key in ("Síntoma", "Causa"):
            if key in sections and sections[key].strip():
                text = sections[key].strip().split("\n\n")[0]
                text = re.sub(r"[#*`>_\-]+", "", text).strip()
                return text[:180] + ("…" if len(text) > 180 else "")
        return ""

    @property
    def searchable_text(self) -> str:
        parts = [self.title, self.id, " ".join(str(t) for t in self.tags), " ".join(str(t) for t in self.tools)]
        sections = self.sections
        if "Síntoma" in sections:
            parts.append(sections["Síntoma"])
        if "Causa" in sections:
            parts.append(sections["Causa"])
        return " ".join(parts).lower()


@dataclass
class DiagnosticMatch:
    entry: ErrorEntry
    score: float  # 0.0 - 1.0
    matched_keywords: list[str] = field(default_factory=list)

    @property
    def confidence_pct(self) -> int:
        return min(99, max(5, int(self.score * 100)))


def _split_sections(body: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_title: str | None = None
    current_lines: list[str] = []
    for line in body.splitlines():
        match = re.match(r"^##\s+(.+)$", line)
        if match:
            if current_title is not None:
                sections[current_title] = "\n".join(current_lines).strip()
            current_title = match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_title is not None:
        sections[current_title] = "\n".join(current_lines).strip()
    return sections


def _parse_file(path: Path) -> ErrorEntry | None:
    try:
        post = frontmatter.load(path)
    except Exception as exc:
        print(f"[kb] skip {path.name}: {exc}")
        return None

    meta = post.metadata or {}
    media = meta.get("media") or {}

    return ErrorEntry(
        id=str(meta.get("id", path.stem)),
        title=str(meta.get("title", path.stem)),
        category=str(meta.get("category", path.parent.name)),
        severity=str(meta.get("severity", "media")),
        tools=list(meta.get("tools", []) or []),
        tags=list(meta.get("tags", []) or []),
        related=list(meta.get("related", []) or []),
        images=list(media.get("images", []) or []),
        videos=list(media.get("videos", []) or []),
        body=post.content,
        path=path,
    )


def load_entries() -> list[ErrorEntry]:
    if not ERRORS_DIR.exists():
        return []
    entries: list[ErrorEntry] = []
    for md_path in sorted(ERRORS_DIR.rglob("*.md")):
        entry = _parse_file(md_path)
        if entry is not None:
            entries.append(entry)
    return entries


def build_index(entries: Iterable[ErrorEntry]):
    schema = Schema(
        id=ID(stored=True, unique=True),
        title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
        category=KEYWORD(stored=True, lowercase=True, scorable=True),
        severity=KEYWORD(stored=True, lowercase=True),
        tools=KEYWORD(stored=True, lowercase=True, commas=True),
        tags=KEYWORD(stored=True, lowercase=True, commas=True),
        body=TEXT(analyzer=StemmingAnalyzer()),
    )
    storage = RamStorage()
    ix = storage.create_index(schema)
    writer = ix.writer()
    for e in entries:
        writer.add_document(
            id=e.id,
            title=e.title,
            category=e.category,
            severity=e.severity,
            tools=",".join(str(t) for t in e.tools),
            tags=",".join(str(t) for t in e.tags),
            body=e.body,
        )
    writer.commit()
    return ix


def search(ix, query_str: str, limit: int = 20) -> list[str]:
    """Return matching error ids ordered by relevance."""
    if not query_str.strip():
        return []
    with ix.searcher() as searcher:
        parser = MultifieldParser(["title", "body", "tags"], schema=ix.schema, group=OrGroup)
        query = parser.parse(query_str)
        results = searcher.search(query, limit=limit)
        return [hit["id"] for hit in results]


# ============ DIAGNOSTIC ENGINE ============

_NOISE = re.compile(
    r"\b(the|a|an|is|are|was|were|be|been|being|have|has|had|do|does|did|"
    r"will|would|shall|should|may|might|can|could|must|need|to|of|in|for|"
    r"on|with|at|by|from|as|into|through|during|before|after|above|below|"
    r"between|out|off|over|under|again|further|then|once|here|there|when|"
    r"where|why|how|all|both|each|few|more|most|other|some|such|no|nor|not|"
    r"only|own|same|so|than|too|very|just|because|but|and|or|if|while|que|"
    r"el|la|los|las|un|una|de|del|en|por|para|con|sin|es|son|al|se|su|"
    r"lo|le|les|nos|ya|pero|como|no|si|más|este|esta|estos|estas|"
    r"error|power|bi|powerbi)\b",
    re.IGNORECASE,
)


def _normalize(text: str) -> str:
    text = re.sub(r"[^\w\s]", " ", text.lower())
    text = _NOISE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_keywords(text: str) -> list[str]:
    return [w for w in _normalize(text).split() if len(w) > 2]


def _keyword_overlap(input_kw: list[str], entry_text: str) -> tuple[float, list[str]]:
    if not input_kw:
        return 0.0, []
    matched = [kw for kw in input_kw if kw in entry_text]
    score = len(matched) / len(input_kw) if input_kw else 0.0
    return score, matched


def _fuzzy_title_match(input_text: str, title: str) -> float:
    return SequenceMatcher(None, _normalize(input_text), _normalize(title)).ratio()


def diagnose(
    entries: list[ErrorEntry],
    error_text: str,
    limit: int = 5,
) -> list[DiagnosticMatch]:
    """Match pasted error text against all KB entries. Returns ranked matches."""
    if not error_text.strip():
        return []

    input_lower = error_text.lower()
    input_keywords = _extract_keywords(error_text)
    input_norm = _normalize(error_text)

    scored: list[DiagnosticMatch] = []

    for entry in entries:
        entry_searchable = entry.searchable_text

        # Keyword overlap (0-1)
        kw_score, kw_matched = _keyword_overlap(input_keywords, entry_searchable)

        # Fuzzy title match (0-1)
        title_score = _fuzzy_title_match(error_text, entry.title)

        # Exact substring bonus: if the pasted text contains the entry title verbatim
        exact_bonus = 0.25 if _normalize(entry.title) in input_norm else 0.0

        # Tag direct hit bonus
        tag_hits = sum(1 for t in entry.tags if str(t).lower() in input_lower)
        tag_score = min(0.20, tag_hits * 0.07)

        # Combine with weights
        combined = (
            kw_score * 0.40
            + title_score * 0.25
            + exact_bonus
            + tag_score
            + 0.10  # base so nothing is exactly 0
        )

        if combined > 0.15:
            scored.append(DiagnosticMatch(
                entry=entry,
                score=min(1.0, combined),
                matched_keywords=kw_matched,
            ))

    scored.sort(key=lambda m: m.score, reverse=True)
    return scored[:limit]


# ============ QUERIES ============

def categories(entries: Iterable[ErrorEntry]) -> list[str]:
    return sorted({e.category for e in entries})


def category_counts(entries: Iterable[ErrorEntry]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for e in entries:
        counts[e.category] = counts.get(e.category, 0) + 1
    return counts


def by_id(entries: Iterable[ErrorEntry], error_id: str) -> ErrorEntry | None:
    for e in entries:
        if e.id == error_id:
            return e
    return None


def by_category(entries: Iterable[ErrorEntry], category: str) -> list[ErrorEntry]:
    return [e for e in entries if e.category == category]
