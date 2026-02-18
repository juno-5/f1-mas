"""MAS Persona Index — in-memory index of 158 personas with lazy character loading."""

import os
import re
import threading
import time
from dataclasses import dataclass, field

from . import mas_config as cfg

_REGISTRY_SECTION_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)
_TABLE_ROW_RE = re.compile(r"^\|(.+)\|$", re.MULTILINE)

# Priority table from selection-rules.md — hardcoded for O(1) lookup
FUNCTION_PRIORITY = {
    "system_architecture": ["F1-02", "FC-01", "F1-07"],
    "security_audit": ["F1-01", "F1-06", "FC-06"],
    "performance": ["F1-03", "FC-08"],
    "algorithm": ["F1-04"],
    "debugging": ["F1-05"],
    "ml_training": ["F1-08", "FC-03"],
    "ai_compiler": ["F1-09"],
    "data_pipeline": ["F1-10", "FC-07"],
    "sre_monitoring": ["F1-11", "FC-05"],
    "nlp_llm": ["F1-12", "F1-08"],
    "vision_multimodal": ["F1-13", "F1-20"],
    "database_storage": ["F1-14", "FC-02"],
    "networking": ["F1-15"],
    "cloud_container": ["F1-16", "FC-05"],
    "formal_verification": ["F1-17"],
    "product_ux": ["F1-18", "FC-09", "FC-04"],
    "quantum": ["F1-19"],
    "image_gen": ["F1-20", "F1-13"],
    "video_gen": ["F1-21", "04"],
    "audio_gen": ["F1-22", "03"],
    "frontend_ui": ["FC-04", "F1-02"],
    "engineering_mgmt": ["FC-10", "FC-01"],
    # Marketing functions (KR first, then US)
    "commerce_strategy": ["COM-KR-01", "COM-KR-02", "COM-US-01", "COM-US-02"],
    "growth_hacking": ["GRO-KR-01", "GRO-KR-05", "GRO-US-01", "GRO-US-05"],
    "amazon_ops": ["AMZ-KR-01", "AMZ-KR-02", "AMZ-US-01", "AMZ-US-02"],
    "tiktok_shortform": ["TIK-KR-01", "TIK-KR-02", "TIK-US-01", "TIK-US-02"],
    "brand_strategy": ["BRD-KR-01", "BRD-KR-02", "BRD-US-01", "BRD-US-02"],
    "visual_design": ["DES-KR-01", "DES-KR-02", "DES-US-01", "DES-US-02"],
    # Creative functions
    "lighting_photography": ["01", "F1-20"],
    "color_palette": ["02", "DES-KR-01"],
    "sound_music": ["03", "F1-22"],
    "motion_video": ["04", "F1-21"],
    "scent_sensory": ["05"],
}

# Domain → category mapping keywords
DOMAIN_KEYWORDS = {
    "developers": [
        r"코드|code|아키텍처|architecture|버그|bug|리팩토링|refactor|debug|디버그",
        r"구현|implement|설계|design|테스트|test|보안|security|배포|deploy",
        r"인프라|infra|api|backend|frontend|데이터베이스|database|알고리즘|algorithm",
        r"성능|performance|최적화|optimize|ML|머신러닝|machine.?learn",
        r"시스템|system|서버|server|네트워크|network|컨테이너|container|클라우드|cloud",
        r"AI|인공지능|모델학습|training|파이프라인|pipeline|데이터|data",
    ],
    "marketers": [
        r"마케팅|marketing|캠페인|campaign|광고|advertising|퍼포먼스|performance.?marketing",
        r"브랜딩|branding|브랜드|brand|카피|copy|전략|strategy",
        r"그로스|growth|성장|UA|유저.?획득|acquisition|리텐션|retention",
        r"아마존|amazon|tiktok|틱톡|커머스|commerce|이커머스|e.?commerce",
        r"SNS|소셜|social|인플루언서|influencer|콘텐츠|content.?marketing",
        r"CRO|전환율|conversion|AB테스트|디자인|design",
    ],
    "models": [
        r"모델|model(?!.*router)|화보|lookbook|촬영|shooting|캐스팅|casting",
        r"패션|fashion|뷰티|beauty|스타일링|styling|런웨이|runway",
        r"화장품|cosmetic|헤어|hair|메이크업|makeup|룩북",
    ],
    "creatives": [
        r"조명|lighting|라이팅|컬러|color|팔레트|palette|사운드|sound",
        r"음악|music|음향|audio|모션|motion|영상|video|시네마|cinema",
        r"향|scent|감각|sensory|오감|five.?sense|아트디렉션|art.?direction",
    ],
}

_domain_compiled = {
    cat: [re.compile(p, re.IGNORECASE) for p in patterns]
    for cat, patterns in DOMAIN_KEYWORDS.items()
}


@dataclass
class PersonaEntry:
    id: str
    name: str
    callsign: str
    role: str
    category: str       # developers/marketers/models/creatives
    locale: str          # korea/usa/japan/europe/global
    tags: list[str] = field(default_factory=list)
    file_path: str = ""  # relative path within characters/
    specialty: str = ""  # models only


class PersonaIndex:
    """In-memory persona index with O(1) lookups and lazy character loading."""

    def __init__(self):
        self._by_id: dict[str, PersonaEntry] = {}
        self._by_category: dict[str, list[str]] = {}
        self._by_locale: dict[str, list[str]] = {}
        self._by_tag: dict[str, list[str]] = {}
        self._char_cache: dict[str, str] = {}
        self._char_cache_ts: dict[str, float] = {}
        self._lock = threading.Lock()
        self._registry_mtime = 0.0
        self._loaded = False

    def load(self):
        """Parse persona-registry.md and build indices."""
        registry_path = cfg.get("persona_registry_path", "")
        if not registry_path or not os.path.isfile(registry_path):
            return

        try:
            mtime = os.path.getmtime(registry_path)
            if mtime == self._registry_mtime and self._loaded:
                return
            self._registry_mtime = mtime
        except OSError:
            return

        with open(registry_path, "r", encoding="utf-8") as f:
            content = f.read()

        entries = []
        entries.extend(self._parse_developers(content))
        entries.extend(self._parse_marketers(content))
        entries.extend(self._parse_models(content))
        entries.extend(self._parse_creatives(content))

        with self._lock:
            self._by_id.clear()
            self._by_category.clear()
            self._by_locale.clear()
            self._by_tag.clear()

            for e in entries:
                self._by_id[e.id] = e
                self._by_category.setdefault(e.category, []).append(e.id)
                self._by_locale.setdefault(e.locale, []).append(e.id)
                for tag in e.tags:
                    self._by_tag.setdefault(tag, []).append(e.id)

            self._loaded = True

    def _parse_table_rows(self, section_text):
        """Extract table rows from a markdown section (skip headers + separators).

        Handles multiple tables within a section by resetting state on blank lines.
        """
        rows = []
        sep_seen = False
        for line in section_text.split("\n"):
            stripped = line.strip()
            if not stripped.startswith("|"):
                # Reset for next table in same section
                sep_seen = False
                continue
            if "---" in stripped:
                sep_seen = True
                continue
            if not sep_seen:
                # This is a header row, skip
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            rows.append(cells)
        return rows

    def _extract_section(self, content, start_header, stop_headers=None):
        """Extract text from a section heading to the next same-level heading."""
        lines = content.split("\n")
        collecting = False
        result = []
        level = 0
        for line in lines:
            if start_header in line and line.strip().startswith("#"):
                collecting = True
                level = len(line) - len(line.lstrip("#"))
                continue
            if collecting:
                if line.strip().startswith("#"):
                    cur_level = len(line.strip()) - len(line.strip().lstrip("#"))
                    if cur_level <= level:
                        break
                    if stop_headers and any(h in line for h in stop_headers):
                        break
                result.append(line)
        return "\n".join(result)

    def _parse_developers(self, content):
        """Parse developer sections from registry."""
        entries = []
        dev_section = self._extract_section(content, "Developers")

        # F1 Korea has 3 sub-sections: Core, Extended, Generative
        for sub_h in ["Core", "Extended", "Generative"]:
            sub_text = self._extract_section(dev_section, sub_h)
            if sub_text:
                for row in self._parse_table_rows(sub_text):
                    if len(row) >= 5:
                        pid, name, callsign, role, fpath = row[0], row[1], row[2], row[3], row[4]
                        tags_str = row[5] if len(row) > 5 else ""
                        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                        entries.append(PersonaEntry(
                            id=pid.strip(), name=name.strip(),
                            callsign=callsign.strip().replace("—", "").strip(),
                            role=role.strip(), category="developers",
                            locale="korea",
                            tags=tags,
                            file_path=fpath.strip().strip("`"),
                        ))

        # Falcon Global (has Location column)
        falcon_text = self._extract_section(dev_section, "Falcon Global")
        if falcon_text:
            for row in self._parse_table_rows(falcon_text):
                if len(row) >= 6:
                    pid, name, callsign, role = row[0], row[1], row[2], row[3]
                    # location = row[4]
                    fpath = row[5]
                    tags_str = row[6] if len(row) > 6 else ""
                    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                    entries.append(PersonaEntry(
                        id=pid.strip(), name=name.strip(),
                        callsign=callsign.strip().replace("—", "").strip(),
                        role=role.strip(), category="developers", locale="global",
                        tags=tags, file_path=fpath.strip().strip("`"),
                    ))

        return entries

    def _parse_marketers(self, content):
        """Parse marketer personas."""
        entries = []
        mkt_section = self._extract_section(content, "Marketers")

        for region, locale in [("Korea (30)", "korea"), ("USA (30)", "usa")]:
            region_text = self._extract_section(mkt_section, region)
            if not region_text:
                # Try simpler headers
                region_text = self._extract_section(mkt_section, region.split(" ")[0])
            if not region_text:
                continue

            for row in self._parse_table_rows(region_text):
                if len(row) >= 4:
                    pid = row[0].strip()
                    name = row[1].strip()
                    # Korean has English name column; USA doesn't
                    if locale == "korea" and len(row) >= 6:
                        eng_name = row[2].strip()
                        role = row[3].strip()
                        fpath = row[4].strip().strip("`")
                        tags_str = row[5] if len(row) > 5 else ""
                    else:
                        eng_name = ""
                        role = row[2].strip()
                        fpath = row[3].strip().strip("`")
                        tags_str = row[4] if len(row) > 4 else ""

                    tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                    callsign = eng_name if eng_name else name
                    entries.append(PersonaEntry(
                        id=pid, name=name, callsign=callsign,
                        role=role, category="marketers", locale=locale,
                        tags=tags, file_path=fpath,
                    ))

        return entries

    def _parse_models(self, content):
        """Parse model personas."""
        entries = []
        models_section = self._extract_section(content, "Models")

        for region, locale in [
            ("Korea (20)", "korea"), ("Japan (10)", "japan"),
            ("USA (20)", "usa"), ("Europe (10)", "europe"),
        ]:
            region_text = self._extract_section(models_section, region)
            if not region_text:
                region_text = self._extract_section(models_section, region.split(" ")[0])
            if not region_text:
                continue

            for row in self._parse_table_rows(region_text):
                if len(row) >= 3:
                    pid = row[0].strip()
                    name = row[1].strip()
                    fpath = row[2].strip().strip("`")
                    specialty = row[3].strip() if len(row) > 3 else ""
                    # Europe has Nationality column
                    if locale == "europe" and len(row) >= 5:
                        fpath = row[2].strip().strip("`")
                        specialty = row[4].strip() if len(row) > 4 else ""

                    entries.append(PersonaEntry(
                        id=pid, name=name, callsign=name,
                        role="Model", category="models", locale=locale,
                        tags=[], file_path=fpath, specialty=specialty,
                    ))

        return entries

    def _parse_creatives(self, content):
        """Parse creative personas."""
        entries = []
        creative_section = self._extract_section(content, "Creatives")

        for row in self._parse_table_rows(creative_section):
            if len(row) >= 5:
                pid = row[0].strip()
                callsign = row[1].strip()
                sense = row[2].strip()
                role = row[3].strip()
                fpath = row[4].strip().strip("`")
                tags_str = row[6] if len(row) > 6 else ""
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]

                entries.append(PersonaEntry(
                    id=pid, name=callsign, callsign=callsign,
                    role=role, category="creatives", locale="global",
                    tags=tags, file_path=fpath, specialty=sense,
                ))

        return entries

    # ── Public API ──

    def get(self, persona_id: str) -> PersonaEntry | None:
        with self._lock:
            return self._by_id.get(persona_id)

    def by_category(self, category: str) -> list[PersonaEntry]:
        with self._lock:
            ids = self._by_category.get(category, [])
            return [self._by_id[i] for i in ids if i in self._by_id]

    def by_locale(self, locale: str) -> list[PersonaEntry]:
        with self._lock:
            ids = self._by_locale.get(locale, [])
            return [self._by_id[i] for i in ids if i in self._by_id]

    def by_tag(self, tag: str) -> list[PersonaEntry]:
        with self._lock:
            ids = self._by_tag.get(tag, [])
            return [self._by_id[i] for i in ids if i in self._by_id]

    def by_function(self, function_key: str) -> list[PersonaEntry]:
        """Get personas by function priority key."""
        ids = FUNCTION_PRIORITY.get(function_key, [])
        with self._lock:
            return [self._by_id[i] for i in ids if i in self._by_id]

    def all_entries(self) -> list[PersonaEntry]:
        with self._lock:
            return list(self._by_id.values())

    def count(self) -> int:
        with self._lock:
            return len(self._by_id)

    def search(self, query: str) -> list[PersonaEntry]:
        """Simple text search across name, callsign, role, tags."""
        q = query.lower()
        results = []
        with self._lock:
            for e in self._by_id.values():
                if (q in e.name.lower() or q in e.callsign.lower()
                        or q in e.role.lower() or q in e.id.lower()
                        or any(q in t for t in e.tags)):
                    results.append(e)
        return results

    def detect_domain(self, text: str) -> list[str]:
        """Detect domain categories from user text using regex."""
        matches = {}
        for cat, patterns in _domain_compiled.items():
            score = sum(1 for p in patterns if p.search(text))
            if score > 0:
                matches[cat] = score
        if not matches:
            return ["developers"]  # default
        return sorted(matches, key=matches.get, reverse=True)

    def detect_locale(self, text: str) -> str:
        """Detect locale from text patterns."""
        # Korean characters present
        if re.search(r"[가-힣]", text):
            return "korea"
        # Japanese characters
        if re.search(r"[\u3040-\u309F\u30A0-\u30FF]", text):
            return "japan"
        # Explicit locale mentions
        locale_kw = {
            "korea": r"한국|korea|korean|KR",
            "japan": r"일본|japan|japanese|JP",
            "usa": r"미국|america|US|USA",
            "europe": r"유럽|europe|european|EU",
            "global": r"글로벌|global|worldwide|international",
        }
        for loc, pat in locale_kw.items():
            if re.search(pat, text, re.IGNORECASE):
                return loc
        return "korea"  # default for ambiguous

    def load_character(self, persona_id: str) -> str:
        """Lazy load a character file, cached with TTL."""
        entry = self.get(persona_id)
        if not entry or not entry.file_path:
            return ""

        ttl = cfg.get("persona_cache_ttl", 300)
        now = time.time()

        with self._lock:
            if persona_id in self._char_cache:
                if now - self._char_cache_ts.get(persona_id, 0) < ttl:
                    return self._char_cache[persona_id]

        base_dir = cfg.get("characters_base_dir", "")
        full_path = os.path.join(base_dir, entry.file_path)
        if not os.path.isfile(full_path):
            return ""

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            return ""

        with self._lock:
            self._char_cache[persona_id] = content
            self._char_cache_ts[persona_id] = now

        return content

    def extract_character_sections(self, persona_id: str) -> str:
        """Load character file and extract only key sections (~200 lines)."""
        full_content = self.load_character(persona_id)
        if not full_content:
            return ""

        sections_to_keep = cfg.get("character_extract_sections", [])
        if not sections_to_keep:
            return full_content

        lines = full_content.split("\n")
        result = []
        # Always include first heading block (identity)
        collecting = True
        first_section_done = False

        for i, line in enumerate(lines):
            if line.startswith("## ") and first_section_done:
                # Check if this section should be kept
                heading = line.lstrip("#").strip()
                # Remove emoji from heading for matching
                heading_clean = re.sub(r"[^\w\s]", "", heading).strip()
                collecting = any(
                    s.lower() in heading_clean.lower() or heading_clean.lower() in s.lower()
                    for s in sections_to_keep
                )
            elif line.startswith("## "):
                first_section_done = True

            if collecting:
                result.append(line)

        extracted = "\n".join(result)
        # Trim to ~200 lines if still too long
        result_lines = extracted.split("\n")
        if len(result_lines) > 250:
            result_lines = result_lines[:250]
            result_lines.append("\n[... truncated for token efficiency ...]")
        return "\n".join(result_lines)

    def to_summary_list(self) -> list[dict]:
        """Return all personas as dicts for API response."""
        with self._lock:
            return [
                {
                    "id": e.id,
                    "name": e.name,
                    "callsign": e.callsign,
                    "role": e.role,
                    "category": e.category,
                    "locale": e.locale,
                    "tags": e.tags,
                }
                for e in self._by_id.values()
            ]


def _reload_loop(index: PersonaIndex):
    """Background thread: reload index if registry changed."""
    while True:
        time.sleep(cfg.get("hot_reload_interval", 30))
        try:
            index.load()
        except Exception:
            pass


# Module-level singleton
_index = PersonaIndex()


def get_index() -> PersonaIndex:
    if not _index._loaded:
        _index.load()
    return _index


def start_hot_reload():
    t = threading.Thread(target=_reload_loop, args=(_index,), daemon=True)
    t.start()
