"""MAS Persona Index — in-memory index of 184 personas with lazy character loading."""

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
    "platform_engineering": ["F1-11", "FC-05", "F1-02", "FC-01"],
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
    "frontend_ui": ["FC-04", "F1-03", "F1-18", "UX-05"],
    "engineering_mgmt": ["FC-10", "FC-01"],
    # Marketing functions (KR first, then US)
    "commerce_strategy": ["COM-KR-01", "COM-KR-02", "COM-US-01", "COM-US-02"],
    "growth_hacking": ["GRO-KR-01", "GRO-KR-05", "GRO-US-01", "GRO-US-05"],
    "amazon_ops": ["AMZ-KR-01", "AMZ-KR-02", "AMZ-US-01", "AMZ-US-02"],
    "tiktok_shortform": ["TIK-KR-01", "TIK-KR-02", "TIK-US-01", "TIK-US-02"],
    "brand_strategy": ["BRD-KR-01", "BRD-KR-02", "BRD-US-01", "BRD-US-02"],
    "visual_design": ["DES-KR-01", "DES-KR-02", "DES-US-01", "DES-US-02"],
    # Commerce team functions
    "ecommerce_platform": ["CMM-03", "CMM-01"],
    "conversion_optimization": ["CMM-02", "CMM-01"],
    "marketplace_strategy": ["CMM-04", "CMM-01"],
    "loyalty_retention": ["CMM-05", "CMM-01"],
    # Sales team functions
    "enterprise_sales": ["SLS-01", "SLS-05"],
    "sales_methodology": ["SLS-02", "SLS-01"],
    "plg_sales": ["SLS-03", "SLS-01"],
    "account_management": ["SLS-04", "SLS-01"],
    "sales_engineering": ["SLS-05", "SLS-01"],
    # UIUX team functions
    "design_strategy": ["UX-01", "UX-02"],
    "interaction_design": ["UX-02", "UX-01"],
    "user_research": ["UX-03", "UX-01"],
    "design_system": ["UX-04", "UX-01"],
    "ux_engineering": ["UX-05", "UX-04"],
    # CX team functions
    "cx_strategy": ["CX-01", "CX-02"],
    "customer_success": ["CX-02", "CX-01"],
    "cx_analytics": ["CX-03", "CX-01"],
    "omnichannel_cx": ["CX-04", "CX-01"],
    "cx_operations": ["CX-05", "CX-01"],
    # Creative functions — Five Senses
    "lighting_photography": ["01", "F1-20"],
    "color_palette": ["02", "DES-KR-01"],
    "sound_music": ["03", "F1-22"],
    "motion_video": ["04", "F1-21"],
    "scent_sensory": ["05"],
    # Creative functions — Art Master Squad
    "ai_art_direction": ["AM-01", "AM-06"],
    "ai_video_gen": ["AM-02", "AM-03", "AM-05"],
    "ai_image_gen": ["AM-04", "AM-01"],
    "ai_motion": ["AM-03", "AM-02"],
    "ai_shortform": ["AM-05", "AM-03"],
    "prompt_architecture": ["AM-06", "AM-01"],
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
    tribe: str = ""      # tribe_id (e.g. "product", "growth")
    squad: str = ""      # squad_id (e.g. "engineering", "growth_kr")


@dataclass
class SquadInfo:
    squad_id: str          # "engineering", "growth_kr"
    squad_name: str        # "Engineering Squad"
    tribe_id: str          # "product"
    member_ids: list[str] = field(default_factory=list)  # ordered, first = lead
    lead_id: str = ""


@dataclass
class TribeInfo:
    tribe_id: str          # "product"
    tribe_name: str        # "Product Tribe"
    squad_ids: list[str] = field(default_factory=list)
    description: str = ""


class PersonaIndex:
    """In-memory persona index with O(1) lookups and lazy character loading."""

    def __init__(self):
        self._by_id: dict[str, PersonaEntry] = {}
        self._by_category: dict[str, list[str]] = {}
        self._by_locale: dict[str, list[str]] = {}
        self._by_tag: dict[str, list[str]] = {}
        self._char_cache: dict[str, str] = {}
        self._char_cache_ts: dict[str, float] = {}
        self._extract_cache: dict[str, str] = {}  # cached extract_character_sections results
        self._extract_cache_ts: dict[str, float] = {}
        self._lock = threading.Lock()
        self._registry_mtime = 0.0
        self._tribe_registry_mtime = 0.0
        self._loaded = False
        # Tribe/Squad indices
        self._tribes: dict[str, TribeInfo] = {}
        self._squads: dict[str, SquadInfo] = {}
        self._by_tribe: dict[str, list[str]] = {}   # tribe_id → [persona_ids]
        self._by_squad: dict[str, list[str]] = {}   # squad_id → [persona_ids]
        self._squad_patterns: dict[str, re.Pattern] | None = None  # lazy from org/squads.yaml
        self._squad_meta: dict[str, dict] | None = None  # raw yaml metadata
        self._squads_yaml_mtime: float = 0.0
        self._tribe_patterns: dict[str, re.Pattern] | None = None  # lazy from org/tribes.yaml
        self._tribe_meta: dict[str, dict] | None = None  # raw yaml metadata
        self._tribes_yaml_mtime: float = 0.0
        self._domain_compiled: dict[str, list[re.Pattern]] | None = None  # lazy from org/domains.yaml
        self._domains_yaml_mtime: float = 0.0
        self._function_compiled: dict[str, re.Pattern] | None = None
        self._function_priority: dict[str, list[str]] | None = None
        self._function_defaults: dict[str, str] | None = None
        self._functions_yaml_mtime: float = 0.0

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
        # New teams (same table format: ID|Name|Callsign|Role|Location|File|Tags)
        for section, category in [
            ("Commerce", "commerce"), ("Sales", "sales"),
            ("UIUX", "uiux"), ("CX", "cx"),
        ]:
            entries.extend(self._parse_generic_team(content, section, category))

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

        # Load tribe/squad overlay
        self.load_tribes()

    def load_tribes(self):
        """Parse tribe-registry.md and patch PersonaEntry tribe/squad fields."""
        tribe_path = cfg.get("tribe_registry_path", "")
        if not tribe_path or not os.path.isfile(tribe_path):
            return

        try:
            mtime = os.path.getmtime(tribe_path)
            if mtime == self._tribe_registry_mtime and self._tribes:
                return
            self._tribe_registry_mtime = mtime
        except OSError:
            return

        with open(tribe_path, "r", encoding="utf-8") as f:
            content = f.read()

        tribes: dict[str, TribeInfo] = {}
        squads: dict[str, SquadInfo] = {}
        by_tribe: dict[str, list[str]] = {}
        by_squad: dict[str, list[str]] = {}

        current_tribe_id = ""
        current_tribe_name = ""
        current_tribe_desc = ""
        current_squad_id = ""
        current_squad_name = ""
        in_table = False
        sep_seen = False

        for line in content.split("\n"):
            stripped = line.strip()

            # ## Tribe heading
            if stripped.startswith("## ") and not stripped.startswith("### "):
                # Save previous tribe if any
                # Parse new tribe
                current_tribe_name = stripped[3:].strip()
                current_tribe_id = self._normalize_id(current_tribe_name, "Tribe")
                current_tribe_desc = ""
                tribes[current_tribe_id] = TribeInfo(
                    tribe_id=current_tribe_id,
                    tribe_name=current_tribe_name,
                )
                by_tribe[current_tribe_id] = []
                current_squad_id = ""
                in_table = False
                sep_seen = False
                continue

            # > description line after tribe heading
            if stripped.startswith(">") and current_tribe_id and not current_squad_id:
                current_tribe_desc = stripped[1:].strip()
                tribes[current_tribe_id].description = current_tribe_desc
                continue

            # ### Squad heading
            if stripped.startswith("### "):
                current_squad_name = stripped[4:].strip()
                current_squad_id = self._normalize_squad_id(
                    current_squad_name, current_tribe_id
                )
                squads[current_squad_id] = SquadInfo(
                    squad_id=current_squad_id,
                    squad_name=current_squad_name,
                    tribe_id=current_tribe_id,
                )
                by_squad[current_squad_id] = []
                tribes[current_tribe_id].squad_ids.append(current_squad_id)
                in_table = False
                sep_seen = False
                continue

            # Table rows
            if not current_squad_id:
                continue

            if not stripped.startswith("|"):
                in_table = False
                sep_seen = False
                continue

            if "---" in stripped:
                sep_seen = True
                in_table = True
                continue

            if not sep_seen:
                continue  # header row

            # Data row: | ID | Role in Squad |
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) >= 1:
                pid = cells[0].strip()
                if not pid or pid.lower() == "id":
                    continue

                role_in_squad = cells[1].strip() if len(cells) > 1 else ""
                is_lead = "Lead" in role_in_squad and by_squad[current_squad_id] == []

                by_squad[current_squad_id].append(pid)
                by_tribe[current_tribe_id].append(pid)

                if is_lead or not squads[current_squad_id].member_ids:
                    squads[current_squad_id].lead_id = pid if is_lead else squads[current_squad_id].lead_id
                squads[current_squad_id].member_ids.append(pid)

                # Set lead_id to first member if not explicitly set
                if not squads[current_squad_id].lead_id:
                    squads[current_squad_id].lead_id = squads[current_squad_id].member_ids[0]

        # Patch PersonaEntry with tribe/squad
        with self._lock:
            self._tribes = tribes
            self._squads = squads
            self._by_tribe = by_tribe
            self._by_squad = by_squad

            for squad_id, member_ids in by_squad.items():
                sq = squads[squad_id]
                for pid in member_ids:
                    entry = self._by_id.get(pid)
                    if entry:
                        entry.tribe = sq.tribe_id
                        entry.squad = squad_id

    @staticmethod
    def _normalize_id(name: str, strip_suffix: str = "") -> str:
        """Normalize a heading into an ID: 'Product Tribe' → 'product'."""
        name = name.strip()
        if strip_suffix and name.endswith(strip_suffix):
            name = name[: -len(strip_suffix)].strip()
        return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")

    @staticmethod
    def _normalize_squad_id(squad_name: str, tribe_id: str) -> str:
        """Normalize squad heading into unique ID.

        'Growth KR Squad' → 'growth_kr'
        'Engineering Squad' → 'engineering'
        'Korea Squad' (under model tribe) → 'model_korea'
        """
        name = squad_name.strip()
        if name.endswith("Squad"):
            name = name[:-5].strip()

        raw = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")

        # For generic names like 'Korea', 'Japan', 'USA', 'Europe' under model tribe,
        # prefix with tribe to avoid collision
        generic = {"korea", "japan", "usa", "europe"}
        if raw in generic:
            return f"{tribe_id}_{raw}"
        return raw

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
        """Parse creative personas (Five Senses + Art Master Squad)."""
        entries = []
        creative_section = self._extract_section(content, "Creatives")

        for row in self._parse_table_rows(creative_section):
            pid = row[0].strip() if row else ""
            if not pid:
                continue

            # Art Master Squad: ID|Name|Callsign|Role|File|Tags
            if pid.startswith("AM-") and len(row) >= 5:
                name = row[1].strip()
                callsign = row[2].strip()
                role = row[3].strip()
                fpath = row[4].strip().strip("`")
                tags_str = row[5] if len(row) > 5 else ""
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                entries.append(PersonaEntry(
                    id=pid, name=name, callsign=callsign,
                    role=role, category="creatives", locale="global",
                    tags=tags, file_path=fpath, specialty="ai-art",
                ))
            # Five Senses: ID|Callsign|Sense|Role|Short|Full|Tags
            elif len(row) >= 5:
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

    def _parse_generic_team(self, content, section_header, category):
        """Parse a team section with format: ID|Name|Callsign|Role|Location|File|Tags."""
        entries = []
        section = self._extract_section(content, section_header)
        if not section:
            return entries

        locale_map = {
            "korea": "korea", "japan": "japan", "usa": "usa",
            "global": "global", "germany": "europe", "france": "europe",
        }

        for row in self._parse_table_rows(section):
            if len(row) >= 6:
                pid = row[0].strip()
                name = row[1].strip()
                callsign = row[2].strip()
                role = row[3].strip()
                location = row[4].strip().lower()
                fpath = row[5].strip().strip("`")
                tags_str = row[6] if len(row) > 6 else ""
                tags = [t.strip() for t in tags_str.split(",") if t.strip()]
                locale = locale_map.get(location, "global")

                entries.append(PersonaEntry(
                    id=pid, name=name, callsign=callsign,
                    role=role, category=category, locale=locale,
                    tags=tags, file_path=fpath,
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
        """Get personas by function priority key (from org/functions.yaml)."""
        self._load_functions_yaml()
        prio = self._function_priority or FUNCTION_PRIORITY
        ids = prio.get(function_key, [])
        with self._lock:
            return [self._by_id[i] for i in ids if i in self._by_id]

    def by_tribe(self, tribe_id: str) -> list[PersonaEntry]:
        """Get all personas in a tribe."""
        with self._lock:
            ids = self._by_tribe.get(tribe_id, [])
            return [self._by_id[i] for i in ids if i in self._by_id]

    def by_squad(self, squad_id: str) -> list[PersonaEntry]:
        """Get all personas in a squad."""
        with self._lock:
            ids = self._by_squad.get(squad_id, [])
            return [self._by_id[i] for i in ids if i in self._by_id]

    def squad_lead(self, squad_id: str) -> PersonaEntry | None:
        """Get the squad lead persona."""
        with self._lock:
            sq = self._squads.get(squad_id)
            if sq and sq.lead_id:
                return self._by_id.get(sq.lead_id)
            return None

    def get_tribe(self, tribe_id: str) -> TribeInfo | None:
        with self._lock:
            return self._tribes.get(tribe_id)

    def get_squad(self, squad_id: str) -> SquadInfo | None:
        with self._lock:
            return self._squads.get(squad_id)

    def all_tribes(self) -> list[TribeInfo]:
        with self._lock:
            return list(self._tribes.values())

    def all_squads(self, tribe_id: str = None) -> list[SquadInfo]:
        with self._lock:
            if tribe_id:
                tribe = self._tribes.get(tribe_id)
                if not tribe:
                    return []
                return [self._squads[sid] for sid in tribe.squad_ids
                        if sid in self._squads]
            return list(self._squads.values())

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
        compiled = self._get_domain_compiled()
        matches = {}
        for cat, patterns in compiled.items():
            score = sum(1 for p in patterns if p.search(text))
            if score > 0:
                matches[cat] = score
        if not matches:
            return ["developers"]  # default
        return sorted(matches, key=matches.get, reverse=True)

    def _get_domain_compiled(self) -> dict[str, list[re.Pattern]]:
        """Load and cache domain keyword patterns from org/domains.yaml."""
        yaml_path = self._find_org_yaml("domains.yaml")
        if yaml_path and os.path.isfile(yaml_path):
            try:
                mtime = os.path.getmtime(yaml_path)
                if mtime != self._domains_yaml_mtime:
                    self._domain_compiled = None
                    self._domains_yaml_mtime = mtime
            except OSError:
                pass
        if self._domain_compiled is not None:
            return self._domain_compiled

        compiled: dict[str, list[re.Pattern]] = {}
        if yaml_path and os.path.isfile(yaml_path):
            try:
                import yaml
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                for cat, meta in data.items():
                    pats = meta.get("patterns", [])
                    if pats:
                        compiled[cat] = [re.compile(p, re.IGNORECASE) for p in pats]
            except Exception:
                pass

        # Fallback: minimal domain set (org/domains.yaml should always exist)
        if not compiled:
            compiled = {
                "developers": [re.compile(r"코드|code|아키텍처|architecture|설계|design|배포|deploy|인프라|infra", re.IGNORECASE)],
                "marketers": [re.compile(r"마케팅|marketing|브랜드|brand|그로스|growth", re.IGNORECASE)],
                "models": [re.compile(r"모델|model(?!.*router)|패션|fashion|촬영|shooting", re.IGNORECASE)],
                "creatives": [re.compile(r"조명|lighting|컬러|color|사운드|sound|모션|motion", re.IGNORECASE)],
            }

        self._domain_compiled = compiled
        return compiled

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
        # Pure Latin/ASCII text (no CJK) → global; otherwise → korea
        if not re.search(r"[\u3000-\u9FFF\uAC00-\uD7AF]", text):
            return "global"
        return "korea"

    def detect_tribe(self, text: str) -> str | None:
        """Detect tribe from text using keyword scoring (most matches wins)."""
        patterns = self._get_tribe_patterns()
        scores = {}
        for tribe_id, pat in patterns.items():
            hits = len(pat.findall(text))
            if hits > 0:
                scores[tribe_id] = hits
        if not scores:
            return None
        return max(scores, key=scores.get)

    def _get_tribe_patterns(self) -> dict[str, re.Pattern]:
        """Load and cache tribe keyword patterns from org/tribes.yaml."""
        yaml_path = self._find_org_yaml("tribes.yaml")
        if yaml_path and os.path.isfile(yaml_path):
            try:
                mtime = os.path.getmtime(yaml_path)
                if mtime != self._tribes_yaml_mtime:
                    self._tribe_patterns = None
                    self._tribe_meta = None
                    self._tribes_yaml_mtime = mtime
            except OSError:
                pass
        if self._tribe_patterns is not None:
            return self._tribe_patterns

        patterns = {}
        meta_store: dict[str, dict] = {}
        if yaml_path and os.path.isfile(yaml_path):
            try:
                import yaml
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                for tribe_id, meta in data.items():
                    meta_store[tribe_id] = meta
                    parts = []
                    for kw in meta.get("keywords", []):
                        parts.append(re.escape(kw))
                    for pat in meta.get("patterns", []):
                        parts.append(pat)
                    if parts:
                        patterns[tribe_id] = re.compile(
                            "|".join(parts), re.IGNORECASE,
                        )
            except Exception:
                pass

        # Fallback: minimal hardcoded set
        if not patterns:
            _fallback = {
                "product": r"엔지니어링|engineering|코드|code|\bAI\b",
                "growth": r"그로스|growth|틱톡|tiktok|아마존|amazon",
                "revenue": r"커머스|commerce|세일즈|sales|\bCX\b",
                "brand": r"브랜드|brand|디자인|design|크리에이티브|creative",
                "model": r"패션|fashion|모델|model(?!.*router)",
            }
            patterns = {k: re.compile(v, re.IGNORECASE) for k, v in _fallback.items()}

        self._tribe_patterns = patterns
        self._tribe_meta = meta_store
        return patterns

    def detect_squad(self, text: str) -> str | None:
        """Detect squad from text using keywords from org/squads.yaml."""
        patterns = self._get_squad_patterns()
        for squad_id, pat in patterns.items():
            if pat.search(text):
                return squad_id
        return None

    def _get_squad_patterns(self) -> dict[str, re.Pattern]:
        """Load and cache squad keyword patterns from org/squads.yaml."""
        yaml_path = self._find_org_yaml("squads.yaml")
        # Check mtime for hot-reload invalidation
        if yaml_path and os.path.isfile(yaml_path):
            try:
                mtime = os.path.getmtime(yaml_path)
                if mtime != self._squads_yaml_mtime:
                    self._squad_patterns = None
                    self._squad_meta = None
                    self._squads_yaml_mtime = mtime
            except OSError:
                pass
        if self._squad_patterns is not None:
            return self._squad_patterns

        patterns = {}
        meta_store: dict[str, dict] = {}
        if yaml_path and os.path.isfile(yaml_path):
            try:
                import yaml
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                for squad_id, meta in data.items():
                    meta_store[squad_id] = meta
                    kws = meta.get("keywords", [])
                    if kws:
                        escaped = [re.escape(k) for k in kws]
                        patterns[squad_id] = re.compile(
                            "|".join(escaped), re.IGNORECASE,
                        )
            except Exception:
                pass

        # Fallback: if no YAML or empty, use minimal hardcoded set
        if not patterns:
            _fallback = {
                "engineering": r"\bengineering\b|엔지니어링\s*스쿼드",
                "growth_kr": r"그로스.*KR|growth.*kr|한국.*그로스",
                "growth_us": r"그로스.*US|growth.*us|미국.*그로스",
                "commerce": r"\bcommerce\s*squad|커머스\s*스쿼드",
                "sales": r"\bsales\s*squad|세일즈\s*스쿼드",
                "cx": r"\bCX\s*squad|CX\s*스쿼드",
            }
            patterns = {k: re.compile(v, re.IGNORECASE) for k, v in _fallback.items()}

        self._squad_patterns = patterns
        self._squad_meta = meta_store
        return patterns

    def _find_org_yaml(self, filename: str) -> str:
        """Find org/<filename> relative to config paths."""
        reg_path = cfg.get("persona_registry_path", "")
        if reg_path:
            base = os.path.dirname(os.path.dirname(reg_path))
            candidate = os.path.join(base, "org", filename)
            if os.path.isfile(candidate):
                return candidate
        for base in [
            os.path.expanduser("~/projects/mayacrew-f1crew/f1-mas"),
            os.path.expanduser("~/F1/f1-mas"),
        ]:
            candidate = os.path.join(base, "org", filename)
            if os.path.isfile(candidate):
                return candidate
        return ""

    def get_tribe_meta(self, tribe_id: str) -> dict | None:
        """Return tribe metadata (description, keywords) from org/tribes.yaml."""
        self._get_tribe_patterns()  # ensure loaded
        if self._tribe_meta and tribe_id in self._tribe_meta:
            return self._tribe_meta[tribe_id]
        return None

    def get_squad_meta(self, squad_id: str) -> dict | None:
        """Return squad metadata (expertise, tools) from org/squads.yaml."""
        self._get_squad_patterns()  # ensure loaded
        if self._squad_meta and squad_id in self._squad_meta:
            return self._squad_meta[squad_id]
        return None

    def all_squad_meta(self) -> dict[str, dict]:
        """Return all squad metadata keyed by squad_id."""
        self._get_squad_patterns()  # ensure loaded
        return dict(self._squad_meta) if self._squad_meta else {}

    # ── Function YAML loading (org/functions.yaml) ──

    def _load_functions_yaml(self):
        """Load function patterns/priority/defaults from org/functions.yaml (mtime-cached)."""
        yaml_path = self._find_org_yaml("functions.yaml")
        if yaml_path and os.path.isfile(yaml_path):
            try:
                mtime = os.path.getmtime(yaml_path)
                if mtime != self._functions_yaml_mtime:
                    self._function_compiled = None
                    self._function_priority = None
                    self._function_defaults = None
                    self._functions_yaml_mtime = mtime
            except OSError:
                pass
        if self._function_compiled is not None:
            return

        compiled = {}
        priority = {}
        defaults = {}
        if yaml_path and os.path.isfile(yaml_path):
            try:
                import yaml
                with open(yaml_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                defaults_raw = data.pop("defaults", {})
                for func_key, meta in data.items():
                    pats = meta.get("patterns", [])
                    if pats:
                        compiled[func_key] = re.compile(
                            "|".join(pats), re.IGNORECASE,
                        )
                    prio = meta.get("priority", [])
                    if prio:
                        priority[func_key] = prio
                for domain, func in defaults_raw.items():
                    defaults[domain] = func
            except Exception:
                pass

        if not priority:
            priority = dict(FUNCTION_PRIORITY)
        if not defaults:
            defaults = {
                "developers": "system_architecture",
                "marketers": "brand_strategy",
                "models": "lighting_photography",
                "creatives": "color_palette",
                "commerce": "ecommerce_platform",
                "sales": "enterprise_sales",
                "uiux": "design_strategy",
                "cx": "cx_strategy",
            }

        self._function_compiled = compiled  # {} if YAML unavailable
        self._function_priority = priority
        self._function_defaults = defaults

    def detect_function(self, text: str) -> list[str]:
        """Detect function keys from user text using regex from org/functions.yaml."""
        self._load_functions_yaml()
        if not self._function_compiled:
            return []
        return [k for k, pat in self._function_compiled.items() if pat.search(text)]

    def default_function(self, domain: str) -> str:
        """Get default function for a domain from org/functions.yaml."""
        self._load_functions_yaml()
        if self._function_defaults:
            return self._function_defaults.get(domain, "system_architecture")
        return "system_architecture"

    def load_character(self, persona_id: str) -> str:
        """Lazy load a character file, cached with TTL.

        Supports anchor notation (e.g. ``commerce.md#1``) for combined files
        where multiple personas share one markdown file separated by
        ``## N.`` headings.
        """
        entry = self.get(persona_id)
        if not entry or not entry.file_path:
            return ""

        ttl = cfg.get("persona_cache_ttl", 300)
        now = time.time()

        with self._lock:
            if persona_id in self._char_cache:
                if now - self._char_cache_ts.get(persona_id, 0) < ttl:
                    return self._char_cache[persona_id]

        # Handle #N anchor notation (combined character files)
        file_path = entry.file_path
        anchor = None
        if "#" in file_path:
            file_path, anchor_str = file_path.rsplit("#", 1)
            try:
                anchor = int(anchor_str)
            except ValueError:
                pass

        base_dir = cfg.get("characters_base_dir", "")
        full_path = os.path.join(base_dir, file_path)
        if not os.path.isfile(full_path):
            return ""

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError:
            return ""

        # Extract specific persona section from combined file
        if anchor is not None:
            content = self._extract_anchor_section(content, anchor)

        with self._lock:
            self._char_cache[persona_id] = content
            self._char_cache_ts[persona_id] = now

        return content

    @staticmethod
    def _extract_anchor_section(content: str, n: int) -> str:
        """Extract persona section N from a combined character file.

        Combined files use ``## N. Name`` headings to separate personas.
        """
        lines = content.split("\n")
        result = []
        collecting = False
        prefix = f"## {n}."
        for line in lines:
            if line.startswith(prefix):
                collecting = True
                result.append(line)
            elif collecting and line.startswith("## ") and not line.startswith(prefix):
                break
            elif collecting:
                result.append(line)
        return "\n".join(result)

    def extract_character_sections(self, persona_id: str) -> str:
        """Load character file and extract only key sections (~200 lines).

        Results are cached in memory (same TTL as raw character files)
        to avoid repeated regex processing on every agent invocation.
        """
        ttl = cfg.get("persona_cache_ttl", 300)
        now = time.time()

        with self._lock:
            if persona_id in self._extract_cache:
                if now - self._extract_cache_ts.get(persona_id, 0) < ttl:
                    return self._extract_cache[persona_id]

        full_content = self.load_character(persona_id)
        if not full_content:
            return ""

        sections_to_keep = cfg.get("character_extract_sections", [])
        # Skip extraction for small files (< 10KB) or when no sections configured
        if not sections_to_keep or len(full_content) < 10_000:
            with self._lock:
                self._extract_cache[persona_id] = full_content
                self._extract_cache_ts[persona_id] = now
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
            extracted = "\n".join(result_lines)
        # Enforce character limit (Korean text = ~5.65 tokens/char)
        max_chars = cfg.get("character_extract_max_chars", 0)
        if max_chars > 0 and len(extracted) > max_chars:
            truncated = extracted[:max_chars]
            last_section = truncated.rfind("\n## ")
            if last_section > len(extracted) // 4:
                truncated = truncated[:last_section]
            extracted = truncated.rstrip() + "\n\n[... truncated for token efficiency ...]"

        with self._lock:
            self._extract_cache[persona_id] = extracted
            self._extract_cache_ts[persona_id] = now

        return extracted

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
                    "tribe": e.tribe,
                    "squad": e.squad,
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
